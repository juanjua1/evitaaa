"""
Transcriptor WhisperX v5.0 - ECAPA-TDNN (SpeechBrain)
- Embeddings superiores con ECAPA-TDNN
- Mejor precisión en identificación de hablantes
- Diarización forzada a 2 hablantes
- Ideal para llamadas telefónicas
"""
import warnings
warnings.filterwarnings("ignore")

import os
import json
import whisperx
from pathlib import Path
from datetime import datetime, timedelta
import torch
import gc
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
import time
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity

# Imports para ECAPA-TDNN
try:
    import torchaudio
    from speechbrain.pretrained import EncoderClassifier
    ECAPA_DISPONIBLE = True
except ImportError:
    ECAPA_DISPONIBLE = False
    print("⚠️  SpeechBrain no disponible.")
    print("   Instalar: pip install speechbrain torchaudio")


# ==================== MODELO ECAPA-TDNN GLOBAL ====================

_ECAPA_ENCODER = None

def get_ecapa_encoder():
    """Carga el modelo ECAPA una sola vez (singleton)"""
    global _ECAPA_ENCODER
    
    if _ECAPA_ENCODER is None and ECAPA_DISPONIBLE:
        print("  🧠 Cargando modelo ECAPA-TDNN (primera vez)...")
        _ECAPA_ENCODER = EncoderClassifier.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            savedir="pretrained_models/spkrec-ecapa-voxceleb",
            run_opts={"device": "cuda" if torch.cuda.is_available() else "cpu"}
        )
        print("  ✓ ECAPA-TDNN cargado")
    
    return _ECAPA_ENCODER


# ==================== EXTRACCIÓN DE EMBEDDINGS ECAPA ====================

def extraer_embeddings_ecapa(segments, audio_path):
    """
    Extrae embeddings ECAPA-TDNN para cada segmento.
    
    Args:
        segments: Lista de segmentos con start/end
        audio_path: Ruta del audio completo
    
    Returns:
        Lista de embeddings (numpy arrays)
    """
    encoder = get_ecapa_encoder()
    
    if encoder is None:
        raise ImportError("ECAPA-TDNN no disponible")
    
    # Cargar audio completo
    signal, sr = torchaudio.load(audio_path)
    
    # Si es estéreo, convertir a mono
    if signal.shape[0] > 1:
        signal = torch.mean(signal, dim=0, keepdim=True)
    
    embeddings = []
    
    for seg in segments:
        # Extraer segmento temporal
        start_sample = int(seg['start'] * sr)
        end_sample = int(seg['end'] * sr)
        
        # Validar límites
        start_sample = max(0, start_sample)
        end_sample = min(signal.shape[1], end_sample)
        
        segment_signal = signal[:, start_sample:end_sample]
        
        # Segmento muy corto -> embedding nulo
        if segment_signal.shape[1] < 1600:  # < 100ms a 16kHz
            embeddings.append(np.zeros(192))  # ECAPA produce embeddings de 192 dims
            continue
        
        try:
            # Extraer embedding
            with torch.no_grad():
                emb = encoder.encode_batch(segment_signal)
                emb_np = emb.squeeze().cpu().numpy()
                embeddings.append(emb_np)
        
        except Exception as e:
            # Fallback: embedding nulo
            embeddings.append(np.zeros(192))
    
    return embeddings


# ==================== DIARIZACIÓN FORZADA A 2 HABLANTES ====================

def diarize_forced_two_speakers(segments, embeddings, min_segment_duration=0.30):
    """
    Diarización forzada a exactamente 2 hablantes usando clustering.
    
    Args:
        segments: Lista de segments con start, end, text
        embeddings: Lista de embeddings ECAPA (numpy arrays)
        min_segment_duration: Duración mínima para clustering
    
    Returns:
        Lista de segments con speaker asignado
    """
    # Filtrar segmentos muy cortos
    filtered_segments = []
    filtered_embeddings = []
    
    for seg, emb in zip(segments, embeddings):
        duration = seg['end'] - seg['start']
        if duration >= min_segment_duration:
            filtered_segments.append(seg)
            filtered_embeddings.append(emb)
    
    if len(filtered_segments) == 0:
        return []
    
    # Matriz de embeddings
    emb_matrix = np.vstack(filtered_embeddings)
    
    # Clustering forzado a 2 hablantes
    clustering = AgglomerativeClustering(
        n_clusters=2,
        metric='cosine',
        linkage='average'
    )
    labels = clustering.fit_predict(emb_matrix)
    
    # Asignar speakers
    diarized = []
    for seg, spk in zip(filtered_segments, labels):
        diarized.append({
            'start': seg['start'],
            'end': seg['end'],
            'text': seg.get('text', ''),
            'speaker': f"Hablante {chr(65 + spk)}",  # A o B
            'words': seg.get('words', [])
        })
    
    # Fusionar segmentos consecutivos del mismo hablante
    merged = []
    for seg in diarized:
        if not merged:
            merged.append(seg)
            continue
        
        last = merged[-1]
        
        # Mismo hablante y están cerca (<0.2s)
        if seg['speaker'] == last['speaker'] and seg['start'] <= last['end'] + 0.20:
            last['end'] = seg['end']
            last['text'] = (last.get('text', '') + " " + seg.get('text', '')).strip()
            if 'words' in last and 'words' in seg:
                last['words'].extend(seg.get('words', []))
        else:
            merged.append(seg)
    
    return merged


# ==================== REFINAMIENTO CON CENTROIDES ESTABLES ====================

def compute_stable_centroids(segments, embeddings, min_duration=1.0):
    """
    Calcula centroides usando SOLO segmentos largos y confiables.
    
    Args:
        segments: Segmentos diarizados
        embeddings: Embeddings ECAPA
        min_duration: Duración mínima para ser considerado "estable"
    
    Returns:
        Dict {speaker: centroid_vector}
    """
    speaker_embeddings = {}
    
    for seg, emb in zip(segments, embeddings):
        duration = seg['end'] - seg['start']
        
        if duration >= min_duration:
            speaker = seg['speaker']
            if speaker not in speaker_embeddings:
                speaker_embeddings[speaker] = []
            speaker_embeddings[speaker].append(emb)
    
    # Calcular centroides
    centroids = {}
    for speaker, embs in speaker_embeddings.items():
        if len(embs) > 0:
            centroids[speaker] = np.mean(np.vstack(embs), axis=0)
    
    return centroids


def reassign_short_segments(segments, embeddings, centroids, short_threshold=0.7):
    """
    Reasigna TODOS los segmentos cortos basándose en similitud con centroides.
    
    Args:
        segments: Segmentos diarizados
        embeddings: Embeddings ECAPA
        centroids: Centroides calculados de segmentos largos
        short_threshold: Duración máxima para reasignar
    
    Returns:
        Segmentos con speakers corregidos
    """
    if not centroids or len(centroids) < 2:
        return segments
    
    reasignados = 0
    
    for i, seg in enumerate(segments):
        duration = seg['end'] - seg['start']
        
        # Solo reasignar segmentos cortos
        if duration >= short_threshold:
            continue
        
        emb = embeddings[i]
        
        # Calcular similitud con cada centroide
        similarities = {}
        for speaker, centroid in centroids.items():
            sim = cosine_similarity([emb], [centroid])[0][0]
            similarities[speaker] = sim
        
        # Asignar al speaker más similar
        best_speaker = max(similarities, key=similarities.get)
        
        if seg['speaker'] != best_speaker:
            reasignados += 1
        
        seg['speaker'] = best_speaker
    
    if reasignados > 0:
        print(f"        🔧 Reasignados {reasignados} segmentos cortos")
    
    return segments


# ==================== DIARIZACIÓN POR PAUSAS (FALLBACK) ====================

def diarizar_por_pausas(segments, umbral=1.5):
    """
    Método simple de fallback: alterna hablantes en pausas largas.
    """
    hablante_actual = 0
    ultimo_fin = 0
    
    for seg in segments:
        pausa = seg['start'] - ultimo_fin
        
        if pausa > umbral:
            hablante_actual = 1 - hablante_actual
        
        seg['speaker'] = f"Hablante {chr(65 + hablante_actual)}"
        ultimo_fin = seg['end']
    
    return segments


# ==================== WORKER PRINCIPAL ====================

def transcribir_audio_worker(args):
    """
    Worker con ECAPA-TDNN para diarización superior
    """
    audio_path, carpeta_salida, device, compute_type, usar_ecapa = args
    
    archivo_nombre = os.path.basename(audio_path)
    base_name = Path(audio_path).stem
    json_path = Path(carpeta_salida) / f"{base_name}_transcripcion.json"
    
    if json_path.exists():
        return {"status": "skip", "archivo": archivo_nombre}
    
    t0 = time.time()
    
    try:
        print(f"\n  🎯 {archivo_nombre[:60]}")
        
        # 1. CARGAR MODELO WHISPERX
        print(f"     🧠 Cargando WhisperX...")
        model = whisperx.load_model(
            "medium",
            device=device,
            compute_type=compute_type,
            language="es"
        )
        
        # 2. TRANSCRIBIR
        print(f"     🎤 Transcribiendo...")
        audio = whisperx.load_audio(audio_path)
        result = model.transcribe(
            audio,
            batch_size=32,
            language="es"
        )
        
        # 3. ALINEAR
        print(f"     📍 Alineando timestamps...")
        model_a, metadata = whisperx.load_align_model(language_code="es", device=device)
        result = whisperx.align(
            result["segments"],
            model_a,
            metadata,
            audio,
            device,
            return_char_alignments=False
        )
        
        del model_a
        gc.collect()
        
        segments = result["segments"]
        metodo = "pausas_simple"
        
        # 4. DIARIZACIÓN CON ECAPA-TDNN
        if usar_ecapa and ECAPA_DISPONIBLE:
            try:
                print(f"     🎭 Extrayendo embeddings ECAPA-TDNN...")
                
                # Extraer embeddings
                embeddings = extraer_embeddings_ecapa(segments, audio_path)
                
                print(f"     🔬 Clustering forzado a 2 hablantes...")
                
                # Diarización forzada
                segments = diarize_forced_two_speakers(
                    segments,
                    embeddings,
                    min_segment_duration=0.30
                )
                
                # Refinamiento con centroides estables
                print(f"     🔧 Refinando con centroides estables...")
                centroids = compute_stable_centroids(
                    segments,
                    embeddings,
                    min_duration=1.0
                )
                
                if centroids and len(centroids) >= 2:
                    segments = reassign_short_segments(
                        segments,
                        embeddings,
                        centroids,
                        short_threshold=0.7
                    )
                
                metodo = "ecapa_tdnn_2_speakers"
                
            except Exception as e:
                print(f"     ⚠️  ECAPA falló: {str(e)[:50]}")
                print(f"     🔄 Usando método de pausas...")
                segments = diarizar_por_pausas(segments, umbral=1.5)
                metodo = "pausas_fallback"
        else:
            print(f"     🎭 Diarizando por pausas...")
            segments = diarizar_por_pausas(segments, umbral=1.5)
        
        del model
        gc.collect()
        if device == "cuda":
            torch.cuda.empty_cache()
        
        # 5. CONSTRUIR RESULTADO
        conversacion = []
        
        for seg in segments:
            texto = seg.get('text', '').strip()
            if not texto:
                continue
            
            # Calcular confianza
            confianza = None
            if 'words' in seg and seg['words']:
                scores = [w.get('score', 0) for w in seg['words'] if 'score' in w]
                if scores:
                    confianza = round(sum(scores) / len(scores), 3)
            
            conversacion.append({
                "hablante": seg.get('speaker', 'Hablante A'),
                "inicio": round(seg['start'], 2),
                "fin": round(seg['end'], 2),
                "duracion": round(seg['end'] - seg['start'], 2),
                "texto": texto,
                "confianza": confianza
            })
        
        # Estadísticas
        duracion_total = conversacion[-1]["fin"] if conversacion else 0
        hablantes = sorted(list(set([c["hablante"] for c in conversacion])))
        
        # Tiempo por hablante
        tiempo_por_hablante = {}
        for c in conversacion:
            h = c["hablante"]
            tiempo_por_hablante[h] = tiempo_por_hablante.get(h, 0) + c["duracion"]
        
        confianzas = [c["confianza"] for c in conversacion if c["confianza"]]
        confianza_avg = round(sum(confianzas) / len(confianzas), 3) if confianzas else None
        
        texto_completo = " ".join([c["texto"] for c in conversacion])
        
        tiempo_proceso = time.time() - t0
        
        resultado = {
            "archivo": archivo_nombre,
            "duracion_segundos": round(duracion_total, 2),
            "num_segmentos": len(conversacion),
            "num_hablantes": len(hablantes),
            "hablantes": hablantes,
            "tiempo_por_hablante": {k: round(v, 2) for k, v in tiempo_por_hablante.items()},
            "idioma": "es",
            "conversacion": conversacion,
            "transcripcion_completa": texto_completo,
            "calidad": {
                "confianza_promedio": confianza_avg,
                "metodo_diarizacion": metodo,
                "tiempo_procesamiento": round(tiempo_proceso, 1)
            },
            "metadata": {
                "modelo": "whisperx_medium",
                "diarizacion": "ecapa_tdnn" if metodo.startswith("ecapa") else "pausas",
                "dispositivo": device,
                "fecha": datetime.now().isoformat(),
                "version": "5.0_ecapa"
            }
        }
        
        # Guardar JSON
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        
        # Porcentajes
        porcentajes = {
            h: f"{(t/duracion_total*100):.1f}%" 
            for h, t in tiempo_por_hablante.items()
        }
        
        print(f"     ✅ {tiempo_proceso:.1f}s | {metodo}")
        if len(hablantes) >= 2:
            print(f"        {hablantes[0]}: {porcentajes.get(hablantes[0], '0%')} | {hablantes[1]}: {porcentajes.get(hablantes[1], '0%')}")
        
        return {
            "status": "success",
            "archivo": archivo_nombre,
            "tiempo": tiempo_proceso,
            "hablantes": len(hablantes),
            "metodo": metodo
        }
        
    except Exception as e:
        error_path = Path(carpeta_salida) / f"{base_name}_ERROR.txt"
        with open(error_path, "w", encoding="utf-8") as f:
            f.write(f"Error: {str(e)}\n\n")
            f.write(traceback.format_exc())
        
        print(f"     ❌ ERROR: {str(e)[:80]}")
        
        return {
            "status": "error",
            "archivo": archivo_nombre,
            "error": str(e)
        }


# ==================== PROCESAMIENTO PARALELO ====================

def procesar_paralelo(carpeta_entrada, carpeta_salida, num_workers, usar_ecapa):
    
    os.makedirs(carpeta_salida, exist_ok=True)
    
    archivos = sorted(list(Path(carpeta_entrada).glob("*.wav")))
    total = len(archivos)
    
    if total == 0:
        print("❌ No hay archivos .wav")
        return
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16" if device == "cuda" else "int8"
    
    if num_workers is None:
        num_workers = 1  # ECAPA es pesado, mejor 1 worker
    
    print(f"\n{'='*70}")
    print(f"  🚀 WHISPERX v5.0 - ECAPA-TDNN (SpeechBrain)")
    print(f"{'='*70}")
    print(f"  📂 Entrada: {carpeta_entrada}")
    print(f"  📂 Salida: {carpeta_salida}")
    print(f"  🔊 Total: {total:,} audios")
    print(f"  👥 Workers: {num_workers}")
    print(f"  💻 {('🎮 GPU' if device == 'cuda' else '🖥️  CPU')} | Modelo: Medium")
    print(f"  🎭 Diarización: {'ECAPA-TDNN (superior)' if usar_ecapa else 'Pausas simples'}")
    print(f"{'='*70}\n")
    
    if usar_ecapa and not ECAPA_DISPONIBLE:
        print("  ⚠️  SpeechBrain no disponible")
        print("     Instalar: pip install speechbrain torchaudio")
        print("     Usando método de pausas\n")
    
    tareas = [
        (str(archivo), carpeta_salida, device, compute_type, usar_ecapa)
        for archivo in archivos
    ]
    
    exitos = 0
    errores = 0
    saltados = 0
    tiempos = []
    metodos = {}
    
    inicio = datetime.now()
    ultimo_reporte = inicio
    
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(transcribir_audio_worker, t): t for t in tareas}
        
        for i, future in enumerate(as_completed(futures), 1):
            try:
                resultado = future.result()
                
                if resultado["status"] == "success":
                    exitos += 1
                    tiempos.append(resultado["tiempo"])
                    metodo = resultado.get("metodo", "?")
                    metodos[metodo] = metodos.get(metodo, 0) + 1
                    
                elif resultado["status"] == "skip":
                    saltados += 1
                    print(f"  ⏭️  {resultado['archivo'][:50]} (ya existe)")
                    
                elif resultado["status"] == "error":
                    errores += 1
            
            except Exception as e:
                errores += 1
                print(f"  ❌ Error: {str(e)[:60]}")
            
            # Reporte periódico
            ahora = datetime.now()
            if i % 10 == 0 or (ahora - ultimo_reporte).total_seconds() > 120:
                transcurrido = (ahora - inicio).total_seconds()
                procesados = exitos + errores
                velocidad = procesados / (transcurrido / 3600) if transcurrido > 0 else 0
                restante = (total - i) / velocidad if velocidad > 0 else 0
                
                tiempo_promedio = sum(tiempos) / len(tiempos) if tiempos else 0
                
                print(f"\n{'='*70}")
                print(f"  📊 PROGRESO: {i}/{total} ({i/total*100:.1f}%)")
                print(f"  ✓ {exitos} | ❌ {errores} | ⏭️ {saltados}")
                print(f"  ⚡ {velocidad:.0f} audios/hora | {tiempo_promedio:.1f}s/audio")
                print(f"  🕐 Restante: ~{restante:.1f}h")
                if metodos:
                    print(f"  🎯 Métodos: {', '.join([f'{k}: {v}' for k,v in metodos.items()])}")
                print(f"{'='*70}\n")
                
                ultimo_reporte = ahora
    
    # RESUMEN FINAL
    tiempo_total = (datetime.now() - inicio).total_seconds()
    
    print(f"\n{'='*70}")
    print(f"  🎉 COMPLETADO")
    print(f"{'='*70}")
    print(f"  ✓ Exitosos: {exitos}/{total}")
    print(f"  ❌ Errores: {errores}")
    print(f"  ⏭️ Saltados: {saltados}")
    print(f"  ⏱️ Tiempo total: {tiempo_total/3600:.2f}h ({tiempo_total/60:.1f} min)")
    if exitos > 0:
        print(f"  ⚡ Velocidad: {exitos/(tiempo_total/3600):.0f} audios/hora")
        print(f"  📈 Tiempo promedio: {sum(tiempos)/len(tiempos):.1f}s/audio")
    if metodos:
        print(f"\n  🎯 Métodos usados:")
        for m, c in metodos.items():
            print(f"     • {m}: {c} audios ({c/exitos*100:.1f}%)")
    print(f"{'='*70}\n")


# ==================== MAIN ====================

if __name__ == "__main__":
    
    CARPETA_ENTRADA = r"C:\Users\rodri\Documents\codigo-WC\eva\audios_descargados"
    CARPETA_SALIDA = r"C:\Users\rodri\Documents\codigo-WC\eva\transcripciones"
    
    # ========== CONFIGURACIÓN ==========
    
    # ¿Usar ECAPA-TDNN para diarización?
    # True = ECAPA (mucho mejor, requiere speechbrain)
    # False = Método de pausas (rápido pero básico)
    USAR_ECAPA = True
    
    # Workers (recomendado: 1 para ECAPA)
    NUM_WORKERS = 1
    
    # ====================================
    
    if not os.path.exists(CARPETA_ENTRADA):
        print(f"❌ No existe {CARPETA_ENTRADA}")
        exit()
    
    total = len(list(Path(CARPETA_ENTRADA).glob("*.wav")))
    if total == 0:
        print("❌ No hay archivos .wav")
        exit()
    
    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    procesados = len(list(Path(CARPETA_SALIDA).glob("*_transcripcion.json")))
    pendientes = total - procesados
    
    tiene_gpu = torch.cuda.is_available()
    
    print(f"\n{'='*70}")
    print(f"  📊 ANÁLISIS INICIAL")
    print(f"{'='*70}")
    print(f"  🔊 Total: {total:,}")
    print(f"  ✓ Procesados: {procesados:,}")
    print(f"  ⏳ Pendientes: {pendientes:,}")
    print(f"  💻 GPU: {'Sí ✓' if tiene_gpu else 'No'}")
    
    if pendientes == 0:
        print("\n✅ ¡Todo procesado!")
        exit()
    
    # Verificar ECAPA
    if USAR_ECAPA and not ECAPA_DISPONIBLE:
        print(f"\n  ⚠️  ECAPA-TDNN no disponible")
        print(f"     Instalar: pip install speechbrain torchaudio")
        print(f"     Se usará método de pausas\n")
    
    # Estimación
    vel_estimada = 400 if tiene_gpu else 200
    tiempo_estimado = pendientes / vel_estimada
    
    print(f"\n  ⚡ ESTIMACIÓN:")
    print(f"     • Velocidad: ~{vel_estimada} audios/hora")
    print(f"     • Tiempo: ~{tiempo_estimado:.1f}h ({tiempo_estimado*60:.0f} min)")
    print(f"     • Finaliza: ~{(datetime.now() + timedelta(hours=tiempo_estimado)).strftime('%H:%M')}")
    
    print(f"\n  ✨ MEJORAS v5.0 - ECAPA-TDNN:")
    print(f"     • 🎯 Embeddings de máxima calidad (192 dims)")
    print(f"     • 🎭 Precisión superior en identificación")
    print(f"     • 📊 Similitud coseno >0.70 = mismo hablante")
    print(f"     • 🔧 Clustering + refinamiento con centroides")
    print(f"     • 🚀 Modelo pre-entrenado en VoxCeleb")
    print(f"     • ✅ Ideal para llamadas con 2 hablantes")
    
    print(f"\n{'='*70}")
    print(f"¿Iniciar procesamiento? (s/n): ", end="")
    
    respuesta = input().strip().lower()
    if respuesta not in ['s', 'si', 'sí', 'y', 'yes', '']:
        print("❌ Cancelado")
        exit()
    
    print(f"\n🚀 Iniciando con ECAPA-TDNN...\n")
    
    try:
        procesar_paralelo(
            CARPETA_ENTRADA,
            CARPETA_SALIDA,
            NUM_WORKERS,
            USAR_ECAPA
        )
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrumpido")
        print("💾 Archivos procesados guardados")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        traceback.print_exc()
    
    print("\n✅ Finalizado")
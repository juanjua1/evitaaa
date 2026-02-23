"""
Mejora de Transcripciones con Gemini - VERSIÓN PARALELA
========================================================
Procesa múltiples transcripciones simultáneamente con ThreadPoolExecutor.
Reanuda automáticamente (salta archivos ya procesados).
"""

import json
import os
import time
import re
import threading
import google.generativeai as genai
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

BASE_DIR = Path(r"C:\Users\rodri\Documents\codigo-WC\eva")
INPUT_DIR = BASE_DIR / "transcripciones"
OUTPUT_DIR = BASE_DIR / "transcripciones_mejoradas"
REPORTE_DIR = BASE_DIR / "reportes" / "mejora_gemini"

from config import api_key
API_KEY = api_key

MODEL_NAME = "gemini-2.0-flash-lite"
MAX_WORKERS = 5          # Hilos concurrentes
DELAY_BETWEEN_CALLS = 0.3  # Delay por worker (total ~15 req/s con 5 workers)
MAX_RETRIES = 3

# Lock para prints y estadísticas
print_lock = threading.Lock()
stats_lock = threading.Lock()
stats = defaultdict(int)
procesados_count = 0

# ============================================================================
# PROMPT
# ============================================================================

PROMPT_MEJORA = """Eres un experto en corrección y mejora de transcripciones automáticas de un call center de ventas de Movistar Argentina (Mendoza).

## TRANSCRIPCIÓN ORIGINAL (generada por WhisperX, puede tener errores):
{transcripcion}

## TAREA
Analiza y mejora esta transcripción. Debes:

1. **CORREGIR ERRORES DE WHISPER**: Whisper suele transcribir mal:
   - "gigas" → aparece como "llenas", "llegas", "libras", "sigas", "chicas", etc.
   - Nombres propios mal escritos
   - Palabras cortadas o sin sentido
   - "fibra" → puede aparecer como "libra", "fila", etc.
   - Números y planes (ej: "plan de 15", "plan de 20 gigas")

2. **IDENTIFICAR ROLES**: Determina quién es el AGENTE (vendedor Movistar) y quién es el CLIENTE.
   - AGENTE: Se presenta ("Habla con X de Movistar"), ofrece productos, valida datos
   - CLIENTE: Responde, pregunta precios, acepta/rechaza

3. **CLASIFICAR LA LLAMADA**:
   - Tipo: VENTA | SEGUIMIENTO | RECLAMO | SIN_CONTACTO | NO_ATENDIDA
   - Resultado: VENTA_EXITOSA | RECHAZO | PENDIENTE | SIN_DECISION | CORTE

4. **PRODUCTOS MENCIONADOS**: Lista los planes/productos ofrecidos (ej: "plan 15gb", "fibra 100mb", "combo fibra+móvil")

RESPONDE SOLO con este JSON (sin texto adicional, sin markdown):
{{
  "conversacion_mejorada": [
    {{
      "hablante": "AGENTE" o "CLIENTE",
      "inicio": <número>,
      "fin": <número>,
      "texto": "<texto corregido y mejorado>"
    }}
  ],
  "analisis": {{
    "agente_detectado": "Hablante A" o "Hablante B",
    "confianza_roles": "ALTA" | "MEDIA" | "BAJA",
    "tipo_llamada": "VENTA" | "SEGUIMIENTO" | "RECLAMO" | "SIN_CONTACTO" | "NO_ATENDIDA",
    "resultado": "VENTA_EXITOSA" | "RECHAZO" | "PENDIENTE" | "SIN_DECISION" | "CORTE",
    "productos_mencionados": [],
    "plan_vendido": null,
    "incluye_fibra": false,
    "calidad_transcripcion_original": "BUENA" | "REGULAR" | "MALA",
    "correcciones_realizadas": "<breve descripción de qué se corrigió>"
  }}
}}
"""

# ============================================================================
# FUNCIONES
# ============================================================================

def crear_modelo():
    """Crea una instancia del modelo Gemini."""
    return genai.GenerativeModel(MODEL_NAME)


def formatear_transcripcion(conversacion):
    lineas = []
    for seg in conversacion:
        hablante = seg.get('hablante', 'Desconocido')
        texto = seg.get('texto', '')
        inicio = seg.get('inicio', 0)
        fin = seg.get('fin', 0)
        lineas.append(f"[{inicio:.1f}s-{fin:.1f}s] {hablante}: {texto}")
    return '\n'.join(lineas)


def limpiar_json_response(texto):
    texto = texto.strip()
    if texto.startswith('```json'):
        texto = texto[7:]
    if texto.startswith('```'):
        texto = texto[3:]
    if texto.endswith('```'):
        texto = texto[:-3]
    return texto.strip()


def procesar_con_gemini(model, transcripcion_text):
    prompt = PROMPT_MEJORA.format(transcripcion=transcripcion_text)
    
    for intento in range(MAX_RETRIES):
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=8192,
                )
            )
            
            texto_resp = limpiar_json_response(response.text)
            
            try:
                return json.loads(texto_resp)
            except json.JSONDecodeError:
                ultimo = texto_resp.rfind('}')
                if ultimo > 0:
                    depth = 0
                    for i, c in enumerate(texto_resp):
                        if c == '{':
                            depth += 1
                        elif c == '}':
                            depth -= 1
                            if depth == 0:
                                return json.loads(texto_resp[:i+1])
                raise
                    
        except json.JSONDecodeError as e:
            with print_lock:
                print(f"      ⚠️ JSON inválido (intento {intento+1}): {str(e)[:50]}")
            if intento < MAX_RETRIES - 1:
                time.sleep(2)
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower() or "resource" in error_msg.lower():
                wait = 30 * (intento + 1)
                with print_lock:
                    print(f"      ⚠️ Rate limit, esperando {wait}s...")
                time.sleep(wait)
            else:
                with print_lock:
                    print(f"      ❌ Error Gemini (intento {intento+1}): {str(e)[:60]}")
                if intento < MAX_RETRIES - 1:
                    time.sleep(3)
    
    return None


def procesar_archivo(json_path, total, worker_id):
    """Procesa un archivo de transcripción (thread-safe)."""
    global procesados_count
    
    # Usar modelo compartido (genai ya configurado en main)
    model = crear_modelo()
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        conversacion = data.get('conversacion', [])
        if not conversacion or len(conversacion) < 2:
            with stats_lock:
                stats['skip'] += 1
                procesados_count += 1
                num = procesados_count
            with print_lock:
                print(f"  [{num}/{total}] {json_path.stem[:45]}... ⏭️ Sin conversación suficiente")
            return
        
        textos_reales = [s for s in conversacion if len(s.get('texto', '').strip()) > 3]
        if len(textos_reales) < 3:
            with stats_lock:
                stats['skip'] += 1
                procesados_count += 1
                num = procesados_count
            with print_lock:
                print(f"  [{num}/{total}] {json_path.stem[:45]}... ⏭️ Muy corta")
            return
        
        texto_transcripcion = formatear_transcripcion(conversacion)
        
        # Pequeño delay escalonado por worker para no bombardear la API
        time.sleep(DELAY_BETWEEN_CALLS * worker_id)
        
        resultado_gemini = procesar_con_gemini(model, texto_transcripcion)
        
        if not resultado_gemini:
            with stats_lock:
                stats['error'] += 1
                procesados_count += 1
                num = procesados_count
            with print_lock:
                print(f"  [{num}/{total}] {json_path.stem[:45]}... ❌ Sin respuesta")
            return
        
        # Construir archivo mejorado
        data_mejorada = data.copy()
        analisis = resultado_gemini.get('analisis', {})
        data_mejorada['mejora_gemini'] = {
            'analisis': analisis,
            'fecha_mejora': datetime.now().isoformat(),
            'modelo': MODEL_NAME
        }
        
        conv_mejorada = resultado_gemini.get('conversacion_mejorada', [])
        if conv_mejorada and len(conv_mejorada) > 0:
            data_mejorada['conversacion_original'] = data.get('conversacion', [])
            data_mejorada['conversacion'] = conv_mejorada
            data_mejorada['transcripcion_completa'] = ' '.join(
                seg.get('texto', '') for seg in conv_mejorada
            )
        
        output_name = json_path.name.replace('_transcripcion.json', '_mejorado.json')
        output_path = OUTPUT_DIR / output_name
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data_mejorada, f, ensure_ascii=False, indent=2)
        
        tipo = analisis.get('tipo_llamada', '?')
        resultado = analisis.get('resultado', '?')
        calidad = analisis.get('calidad_transcripcion_original', '?')
        
        with stats_lock:
            stats['ok'] += 1
            procesados_count += 1
            num = procesados_count
        with print_lock:
            print(f"  [{num}/{total}] {json_path.stem[:45]}... ✅ {tipo} | {resultado} | {calidad}")
        
    except Exception as e:
        with stats_lock:
            stats['error'] += 1
            procesados_count += 1
            num = procesados_count
        with print_lock:
            print(f"  [{num}/{total}] {json_path.stem[:45]}... ❌ {str(e)[:50]}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 70)
    print("  🤖 MEJORA DE TRANSCRIPCIONES CON GEMINI (PARALELO)")
    print("=" * 70)
    print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  📂 Input:  {INPUT_DIR}")
    print(f"  📂 Output: {OUTPUT_DIR}")
    print(f"  🧠 Modelo: {MODEL_NAME}")
    print(f"  ⚡ Workers: {MAX_WORKERS}")
    print("=" * 70)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORTE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Listar transcripciones
    todos = sorted(INPUT_DIR.glob("*_transcripcion.json"))
    print(f"\n  📊 Transcripciones disponibles: {len(todos)}")
    
    # Saltar ya procesadas
    ya_mejorados = set()
    if OUTPUT_DIR.exists():
        for f in OUTPUT_DIR.iterdir():
            if f.name.endswith('_mejorado.json'):
                nombre_orig = f.name.replace('_mejorado.json', '_transcripcion.json')
                ya_mejorados.add(nombre_orig)
    
    pendientes = [f for f in todos if f.name not in ya_mejorados]
    print(f"  ✅ Ya mejoradas: {len(ya_mejorados)}")
    print(f"  ⏳ Pendientes: {len(pendientes)}")
    
    if not pendientes:
        print("\n  ✅ ¡Todas las transcripciones ya están mejoradas!")
        return
    
    total = len(pendientes)
    print(f"\n  🚀 Iniciando mejora de {total} con {MAX_WORKERS} workers...\n")
    
    # Configurar Gemini UNA sola vez
    genai.configure(api_key=API_KEY)
    
    inicio = datetime.now()
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for idx, json_path in enumerate(pendientes):
            worker_id = idx % MAX_WORKERS
            future = executor.submit(procesar_archivo, json_path, total, worker_id)
            futures.append(future)
            # Pequeño delay entre submits para escalonar
            time.sleep(0.1)
        
        # Esperar todos
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                with print_lock:
                    print(f"  ❌ Error inesperado: {e}")
    
    elapsed = (datetime.now() - inicio).total_seconds()
    
    print(f"\n{'='*70}")
    print(f"  🎉 PROCESO COMPLETADO")
    print(f"{'='*70}")
    print(f"  ✅ Mejoradas: {stats['ok']}")
    print(f"  ⏭️ Saltadas:  {stats['skip']}")
    print(f"  ❌ Errores:   {stats['error']}")
    print(f"  ⏱️ Tiempo:    {elapsed/60:.1f} minutos")
    print(f"  ⚡ Velocidad: {stats['ok']/(elapsed/60):.0f} archivos/min" if elapsed > 0 else "")
    print(f"  📂 Salida:    {OUTPUT_DIR}")
    print(f"{'='*70}")
    
    # Guardar reporte
    reporte = {
        "fecha": datetime.now().isoformat(),
        "modelo": MODEL_NAME,
        "workers": MAX_WORKERS,
        "total_procesados": sum(stats.values()),
        "estadisticas": dict(stats),
        "tiempo_minutos": round(elapsed / 60, 1)
    }
    reporte_path = REPORTE_DIR / f"reporte_mejora_parallel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(reporte_path, 'w', encoding='utf-8') as f:
        json.dump(reporte, f, ensure_ascii=False, indent=2)
    print(f"  📄 Reporte: {reporte_path}")


if __name__ == "__main__":
    main()

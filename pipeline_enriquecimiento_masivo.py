"""
Pipeline de Enriquecimiento Masivo para Transcripciones EVA
============================================================

Este script procesa más de 5000 transcripciones:
1. JOIN con CSV de interacciones (Origen Corte, TalkingTime, Hold, ACW, etc.)
2. Corrección de errores de Whisper (gigas→llenas, etc.)
3. Pre-clasificación con patrones regex (productos, objeciones, etc.)
4. Prepara archivos para el prompt de mejora de Gemini

Fecha: Febrero 2026
"""

import json
import os
import re
import csv
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import concurrent.futures
from typing import Dict, List, Tuple, Optional

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

BASE_DIR = Path(r"C:\Users\rodri\Documents\codigo-WC\eva")
INPUT_DIR = BASE_DIR / "transcripts" / "transcripts"
OUTPUT_DIR = BASE_DIR / "transcripts" / "enriquecidos"
CSV_PATH = BASE_DIR / "interacciones-semana3.csv"
REPORTE_DIR = BASE_DIR / "reportes" / "enriquecimiento_masivo"

# ============================================================================
# ERRORES DE TRANSCRIPCIÓN DE WHISPER
# ============================================================================

ERRORES_GIGAS = r'llenas|llegas|libras|digas|dinas|sigas|siglas|sidas|chicas|rigas|yidas|gigas?|giga|gb|g'

# Correcciones de texto para mejorar transcripciones
CORRECCIONES_TEXTO = {
    # Errores comunes de Whisper
    r'\bllenas\b': 'gigas',
    r'\bllegas\b': 'gigas',
    r'\blibras\b': 'gigas',
    r'\bdigas\b': 'gigas',
    r'\bdinas\b': 'gigas',
    r'\bsigas\b': 'gigas',
    r'\bsiglas\b': 'gigas',
    r'\bsidas\b': 'gigas',
    r'\bchicas\b': 'gigas',
    r'\brigas\b': 'gigas',
    r'\byidas\b': 'gigas',
    # Movistar variations
    r'\bmovi\s*star\b': 'Movistar',
    r'\bmobis?tar\b': 'Movistar',
    # Números comunes
    r'\b(\d+)\s*(?:llenas|llegas|libras)\b': r'\1 gigas',
}

# ============================================================================
# PATRONES DE CLASIFICACIÓN
# ============================================================================

PATRONES_CLASIFICACION = {
    "productos": {
        "fibra": [
            r'\bfibra\b', r'\bfibra\s*[oó]ptica\b',
            r'\binternet\s+(?:de\s+)?(?:hogar|casa|fijo)\b',
            r'\bwifi\s+(?:de\s+)?(?:hogar|casa)\b',
            r'\bmegas?\s+(?:de\s+)?(?:internet|hogar)\b',
        ],
        "portabilidad": [
            r'\bportabilidad\b', r'\bporta\b', r'\bportab\b',
            r'\btraer\s+(?:tu|su|el)\s+(?:número|numero|linea|línea)\b',
            r'\bmantener\s+(?:tu|su|el)\s+(?:número|numero)\b',
            r'\bpasar(?:te|se)?\s+(?:a\s+)?movistar\b',
        ],
    },
    "planes": {
        "30gb": [rf'\b30\s*(?:{ERRORES_GIGAS})\b', rf'\btreinta\s*(?:{ERRORES_GIGAS})\b'],
        "20gb": [rf'\b20\s*(?:{ERRORES_GIGAS})\b', rf'\bveinte\s*(?:{ERRORES_GIGAS})\b'],
        "16gb": [rf'\b16\s*(?:{ERRORES_GIGAS})\b', rf'\bdiecis[eé]is\s*(?:{ERRORES_GIGAS})\b'],
        "15gb": [rf'\b15\s*(?:{ERRORES_GIGAS})\b', rf'\bquince\s*(?:{ERRORES_GIGAS})\b'],
        "12gb": [rf'\b12\s*(?:{ERRORES_GIGAS})\b', rf'\bdoce\s*(?:{ERRORES_GIGAS})\b'],
        "10gb": [rf'\b10\s*(?:{ERRORES_GIGAS})\b', rf'\bdiez\s*(?:{ERRORES_GIGAS})\b'],
        "8gb": [rf'\b8\s*(?:{ERRORES_GIGAS})\b', rf'\bocho\s*(?:{ERRORES_GIGAS})\b'],
        "6gb": [rf'\b6\s*(?:{ERRORES_GIGAS})\b', rf'\bseis\s*(?:{ERRORES_GIGAS})\b'],
        "4gb": [rf'\b4\s*(?:{ERRORES_GIGAS})\b', rf'\bcuatro\s*(?:{ERRORES_GIGAS})\b'],
    },
    "objeciones": {
        "precio": [r'\bcaro\b', r'\bmucho\s+dinero\b', r'\bno\s+tengo\s+plata\b', r'\bcostoso\b'],
        "competencia": [r'\bclaro\b', r'\bpersonal\b', r'\btuenti\b', r'\botro\s+servicio\b'],
        "tiempo": [r'\bno\s+tengo\s+tiempo\b', r'\bestoy\s+ocupad[oa]\b', r'\bahora\s+no\b'],
        "desinteres": [r'\bno\s+me\s+interesa\b', r'\bno\s+gracias\b', r'\bno\s+quiero\b'],
    },
    "sentimiento": {
        "positivo": [r'\bperfecto\b', r'\bexcelente\b', r'\bgenial\b', r'\bbuenísimo\b', r'\bme\s+encanta\b'],
        "negativo": [r'\bmal\b', r'\bpésimo\b', r'\bhorrible\b', r'\bno\s+funciona\b', r'\bproblema\b'],
        "neutral": [r'\bok\b', r'\bbueno\b', r'\bdejame\s+pensar\b'],
    },
    "resultado": {
        "venta": [r'\bacepto\b', r'\bquiero\s+el\s+plan\b', r'\bhacelo\b', r'\bactivalo\b', r'\bsi\s+dale\b'],
        "rechazo": [r'\bno\s+quiero\b', r'\bno\s+me\s+interesa\b', r'\bno\s+gracias\b', r'\bchau\b'],
        "seguimiento": [r'\bllamame\s+después\b', r'\bla\s+próxima\b', r'\bvuelvan\s+a\s+llamar\b'],
    }
}

# ============================================================================
# FUNCIONES DE CARGA
# ============================================================================

def cargar_csv_interacciones() -> Dict[str, dict]:
    """
    Carga el CSV de interacciones y crea un diccionario por idInteraccion.
    """
    print(f"\n📂 Cargando CSV: {CSV_PATH}")
    csv_data = {}
    
    try:
        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                id_interaccion = row.get('idInteraccion', '')
                if id_interaccion:
                    csv_data[id_interaccion] = row
    except Exception as e:
        print(f"   ❌ Error leyendo CSV: {e}")
        return {}
    
    print(f"   ✅ {len(csv_data):,} registros cargados del CSV")
    return csv_data


def extraer_id_interaccion(filename: str) -> Optional[str]:
    """
    Extrae el idInteraccion del nombre de archivo.
    Ejemplo: amza55_1_260128122925297_ACD_52047_transcripcion.json
             → 260128122925297_ACD_52047
    """
    # Quitar extensión y sufijo _transcripcion
    base = filename.replace('_transcripcion.json', '').replace('.json', '')
    
    # El patrón es: prefijo_X_IDINTERACCION
    # donde IDINTERACCION tiene formato: YYMMDDHHMMSS_XXX_NNNNN
    match = re.search(r'(\d{15}_(?:ACD|MIT)_\d{5})', base)
    if match:
        return match.group(1)
    
    return None


# ============================================================================
# FUNCIONES DE PROCESAMIENTO
# ============================================================================

def corregir_texto(texto: str) -> str:
    """
    Aplica correcciones de errores de Whisper al texto.
    """
    texto_corregido = texto
    for patron, reemplazo in CORRECCIONES_TEXTO.items():
        texto_corregido = re.sub(patron, reemplazo, texto_corregido, flags=re.IGNORECASE)
    return texto_corregido


def clasificar_transcripcion(texto: str) -> dict:
    """
    Clasifica la transcripción usando patrones regex.
    """
    texto_lower = texto.lower()
    clasificacion = {}
    
    for categoria, subcategorias in PATRONES_CLASIFICACION.items():
        clasificacion[categoria] = {}
        for subcategoria, patrones in subcategorias.items():
            encontrado = False
            matches = []
            for patron in patrones:
                if re.search(patron, texto_lower, re.IGNORECASE):
                    encontrado = True
                    matches.append(patron)
            if encontrado:
                clasificacion[categoria][subcategoria] = True
    
    return clasificacion


def obtener_texto_completo(data: dict) -> str:
    """
    Extrae el texto completo de la transcripción.
    """
    textos = []
    
    if 'conversacion' in data:
        for segmento in data['conversacion']:
            if 'texto' in segmento:
                textos.append(segmento['texto'])
    
    return ' '.join(textos)


def crear_metadatos_enriquecidos(csv_row: dict, clasificacion: dict) -> dict:
    """
    Crea los metadatos enriquecidos a partir del CSV y clasificación.
    """
    
    # Parsear fecha
    fecha_str = csv_row.get('Inicio', '')
    try:
        fecha_dt = datetime.strptime(fecha_str, '%d/%m/%Y %H:%M:%S')
        fecha_iso = fecha_dt.isoformat()
        dia_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'][fecha_dt.weekday()]
    except:
        fecha_iso = fecha_str
        dia_semana = ''
    
    # Determinar tipo de llamada
    campana = csv_row.get('Campaña', '')
    sentido = csv_row.get('Sentido', '')
    if 'OUT' in campana or sentido == 'Saliente':
        tipo_llamada = 'SALIENTE_MANUAL'
    elif 'Discador' in sentido:
        tipo_llamada = 'SALIENTE_PREDICTIVO'
    else:
        tipo_llamada = 'ENTRANTE' if sentido == 'Entrante' else 'DESCONOCIDO'
    
    # Calcular eficiencia de tiempo
    duracion = int(csv_row.get('Duración', 0) or 0)
    talking = int(csv_row.get('TalkingTime', 0) or 0)
    hold = int(csv_row.get('Hold', 0) or 0)
    eficiencia_tiempo = round(talking / duracion * 100, 1) if duracion > 0 else 0
    
    return {
        "id_interaccion": csv_row.get('idInteraccion', ''),
        "fecha": {
            "original": fecha_str,
            "iso": fecha_iso,
            "dia_semana": dia_semana
        },
        "cliente": {
            "telefono": csv_row.get('Cliente', '').replace('"', ''),
            "id": csv_row.get('idCliente', ''),
            "nombre": csv_row.get('Nombre Cliente', '')
        },
        "agente": {
            "nombre": csv_row.get('Nombre Agente', ''),
            "login_id": csv_row.get('LoginId', ''),
            "equipo": csv_row.get('Equipo', ''),
            "sitio": csv_row.get('Sitio', '')
        },
        "tiempos": {
            "duracion_total_seg": duracion,
            "talking_time_seg": talking,
            "hold_seg": hold,
            "acw_seg": int(csv_row.get('ACW', 0) or 0),
            "en_cola_seg": int(csv_row.get('EnCola', 0) or 0),
            "eficiencia_pct": eficiencia_tiempo
        },
        "llamada": {
            "tipo": tipo_llamada,
            "campana": campana,
            "lote": csv_row.get('Lote', ''),
            "sentido": sentido,
            "origen_corte": csv_row.get('Origen Corte', ''),  # Agente / Cliente
            "causa_terminacion": csv_row.get('Causa Terminación', '')
        },
        "clasificacion_previa": clasificacion,
        "procesado_en": datetime.now().isoformat()
    }


def procesar_archivo(args: Tuple[str, dict]) -> dict:
    """
    Procesa un archivo de transcripción individual.
    """
    json_file, csv_data = args
    json_path = INPUT_DIR / json_file
    
    resultado = {
        "archivo": json_file,
        "status": "error",
        "mensaje": "",
        "id_interaccion": None,
        "match_csv": False
    }
    
    try:
        # 1. Extraer ID de interacción
        id_interaccion = extraer_id_interaccion(json_file)
        resultado["id_interaccion"] = id_interaccion
        
        if not id_interaccion:
            resultado["mensaje"] = "No se pudo extraer ID de interacción"
            return resultado
        
        # 2. Leer JSON original
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 3. Extraer texto completo
        texto_completo = obtener_texto_completo(data)
        
        # 4. Corregir errores de Whisper
        texto_corregido = corregir_texto(texto_completo)
        
        # 5. Clasificar transcripción
        clasificacion = clasificar_transcripcion(texto_corregido)
        
        # 6. Buscar match en CSV
        csv_row = csv_data.get(id_interaccion, {})
        resultado["match_csv"] = bool(csv_row)
        
        # 7. Crear metadatos enriquecidos
        if csv_row:
            metadatos = crear_metadatos_enriquecidos(csv_row, clasificacion)
        else:
            # Metadatos básicos sin CSV
            metadatos = {
                "id_interaccion": id_interaccion,
                "fecha": {"original": "", "iso": "", "dia_semana": ""},
                "cliente": {"telefono": "", "id": "", "nombre": ""},
                "agente": {
                    "nombre": "",
                    "login_id": "",
                    "equipo": "",
                    "sitio": ""
                },
                "tiempos": {
                    "duracion_total_seg": data.get('duracion_segundos', 0),
                    "talking_time_seg": 0,
                    "hold_seg": 0,
                    "acw_seg": 0,
                    "en_cola_seg": 0,
                    "eficiencia_pct": 0
                },
                "llamada": {
                    "tipo": "DESCONOCIDO",
                    "campana": "",
                    "lote": "",
                    "sentido": "",
                    "origen_corte": "",
                    "causa_terminacion": ""
                },
                "clasificacion_previa": clasificacion,
                "procesado_en": datetime.now().isoformat()
            }
        
        # 8. Crear JSON enriquecido
        json_enriquecido = {
            "info_llamada": metadatos,
            "archivo_original": data.get('archivo', json_file),
            "duracion_segundos": data.get('duracion_segundos', 0),
            "num_segmentos": data.get('num_segmentos', 0),
            "num_hablantes": data.get('num_hablantes', 2),
            "hablantes": data.get('hablantes', ['Hablante A', 'Hablante B']),
            "tiempo_por_hablante": data.get('tiempo_por_hablante', {}),
            "idioma": data.get('idioma', 'es'),
            "texto_corregido": texto_corregido,
            "conversacion": data.get('conversacion', [])
        }
        
        # 9. Guardar JSON enriquecido
        output_path = OUTPUT_DIR / json_file.replace('_transcripcion.json', '_enriquecido.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_enriquecido, f, ensure_ascii=False, indent=2)
        
        resultado["status"] = "ok"
        resultado["mensaje"] = "Procesado correctamente"
        
    except Exception as e:
        resultado["mensaje"] = str(e)
    
    return resultado


# ============================================================================
# PIPELINE PRINCIPAL
# ============================================================================

def ejecutar_pipeline():
    """
    Ejecuta el pipeline completo de enriquecimiento masivo.
    """
    print("=" * 80)
    print("PIPELINE DE ENRIQUECIMIENTO MASIVO - EVA 360")
    print("=" * 80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Input: {INPUT_DIR}")
    print(f"Output: {OUTPUT_DIR}")
    print("=" * 80)
    
    # Crear carpetas de salida
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORTE_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Cargar CSV de interacciones
    csv_data = cargar_csv_interacciones()
    
    # 2. Listar archivos a procesar
    json_files = [f for f in os.listdir(INPUT_DIR) 
                  if f.endswith('_transcripcion.json')]
    
    print(f"\n📁 Archivos a procesar: {len(json_files):,}")
    
    # 3. Procesar en paralelo
    print(f"\n🔄 Procesando transcripciones...")
    
    resultados = []
    procesados = 0
    errores = 0
    sin_match = 0
    
    # Procesar en lotes para mostrar progreso
    batch_size = 100
    total_batches = (len(json_files) + batch_size - 1) // batch_size
    
    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(json_files))
        batch_files = json_files[start_idx:end_idx]
        
        # Procesar batch
        for json_file in batch_files:
            resultado = procesar_archivo((json_file, csv_data))
            resultados.append(resultado)
            
            if resultado["status"] == "ok":
                procesados += 1
                if not resultado["match_csv"]:
                    sin_match += 1
            else:
                errores += 1
        
        # Mostrar progreso
        pct = (end_idx / len(json_files)) * 100
        print(f"   [{batch_num + 1}/{total_batches}] {end_idx:,}/{len(json_files):,} ({pct:.1f}%)")
    
    # 4. Generar reporte
    print(f"\n📊 Generando reporte...")
    
    reporte = {
        "fecha_proceso": datetime.now().isoformat(),
        "total_archivos": len(json_files),
        "procesados_ok": procesados,
        "errores": errores,
        "sin_match_csv": sin_match,
        "con_match_csv": procesados - sin_match,
        "tasa_match": round((procesados - sin_match) / procesados * 100, 1) if procesados > 0 else 0,
        "detalles_errores": [r for r in resultados if r["status"] == "error"][:50]  # Primeros 50 errores
    }
    
    # Estadísticas de clasificación
    clasificaciones = defaultdict(lambda: defaultdict(int))
    for r in resultados:
        if r["status"] == "ok" and r["match_csv"]:
            # Leer JSON enriquecido para estadísticas
            try:
                output_file = r["archivo"].replace('_transcripcion.json', '_enriquecido.json')
                output_path = OUTPUT_DIR / output_file
                if output_path.exists():
                    with open(output_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    clasif = data.get("info_llamada", {}).get("clasificacion_previa", {})
                    for cat, subcats in clasif.items():
                        for subcat in subcats.keys():
                            clasificaciones[cat][subcat] += 1
            except:
                pass
    
    reporte["clasificaciones"] = dict(clasificaciones)
    
    # Guardar reporte
    reporte_path = REPORTE_DIR / f"reporte_enriquecimiento_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(reporte_path, 'w', encoding='utf-8') as f:
        json.dump(reporte, f, ensure_ascii=False, indent=2)
    
    # 5. Mostrar resumen
    print("\n" + "=" * 80)
    print("RESUMEN DEL PROCESO")
    print("=" * 80)
    print(f"✅ Procesados correctamente: {procesados:,}")
    print(f"   - Con match CSV: {procesados - sin_match:,} ({reporte['tasa_match']:.1f}%)")
    print(f"   - Sin match CSV: {sin_match:,}")
    print(f"❌ Errores: {errores:,}")
    print(f"\n📁 Archivos enriquecidos en: {OUTPUT_DIR}")
    print(f"📊 Reporte guardado en: {reporte_path}")
    print("=" * 80)
    
    return reporte


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    ejecutar_pipeline()

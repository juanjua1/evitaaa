"""
Script de Limpieza y Mejora de Transcripciones con Gemini
==========================================================

Este script usa Gemini para:
1. Identificar correctamente quién es el agente y quién es el cliente
2. Corregir errores de diarización (hablantes mal asignados)
3. Mejorar la coherencia del texto
4. Preparar la transcripción para la evaluación final

Fecha: Febrero 2026
"""

import json
import os
import time
import google.generativeai as genai
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import concurrent.futures
from collections import defaultdict

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

BASE_DIR = Path(r"C:\Users\rodri\Documents\codigo-WC\eva")
INPUT_DIR = BASE_DIR / "transcripts" / "enriquecidos"
OUTPUT_DIR = BASE_DIR / "transcripts" / "mejorados_gemini"
REPORTE_DIR = BASE_DIR / "reportes" / "mejora_gemini"

# API Key de Gemini - importar desde config
try:
    from config import api_key
    API_KEY = api_key
except ImportError:
    API_KEY = os.environ.get('GEMINI_API_KEY', '')

# Modelo a usar (flash-lite es el más económico)
MODEL_NAME = "gemini-2.0-flash-lite"

# Configuración de procesamiento
BATCH_SIZE = 20  # Procesar de a 20 archivos
DELAY_BETWEEN_CALLS = 1.0  # Segundos entre llamadas para evitar rate limit
MAX_RETRIES = 3
MAX_OUTPUT_TOKENS = 2048  # Reducir para evitar JSONs muy largos

# ============================================================================
# PROMPT DE MEJORA DE TRANSCRIPCIÓN
# ============================================================================

PROMPT_MEJORA = """Eres un experto en análisis de transcripciones de call center de ventas de Movistar Argentina.

## TRANSCRIPCIÓN
{transcripcion}

## TAREA
Identifica quién es el AGENTE (vendedor de Movistar) y quién es el CLIENTE.

PISTAS AGENTE:
- Se presenta: "Habla con [nombre], te llamo de Movistar..."
- Ofrece productos: "El plan incluye X gigas...", "El precio es..."
- Valida: "¿Hablo con...?", "¿Me confirmas...?"

PISTAS CLIENTE:
- Responde: "Sí", "No", "¿Quién habla?"
- Pregunta: "¿Cuánto cuesta?", "¿Qué incluye?"
- Objeta: "No me interesa", "Está caro"

RESPONDE SOLO con este JSON (sin texto adicional):
{{
  "analisis": {{
    "agente_detectado": "Hablante A" | "Hablante B",
    "confianza": "ALTA" | "MEDIA" | "BAJA",
    "tipo_llamada": "VENTA" | "SEGUIMIENTO" | "RECLAMO" | "SIN_CONTACTO",
    "resultado": "VENTA" | "RECHAZO" | "PENDIENTE" | "SIN_DECISION" | "CORTE",
    "productos_mencionados": ["plan 15gb", "fibra", etc],
    "calidad_transcripcion": "BUENA" | "REGULAR" | "MALA"
  }}
}}
"""

# ============================================================================
# FUNCIONES DE PROCESAMIENTO
# ============================================================================

def configurar_gemini():
    """Configura la API de Gemini."""
    genai.configure(api_key=API_KEY)
    return genai.GenerativeModel(MODEL_NAME)


def formatear_transcripcion(conversacion: List[dict]) -> str:
    """Formatea la conversación para el prompt."""
    lineas = []
    for i, seg in enumerate(conversacion):
        hablante = seg.get('hablante', f'Hablante {i % 2}')
        texto = seg.get('texto', '')
        inicio = seg.get('inicio', 0)
        fin = seg.get('fin', 0)
        lineas.append(f"[{inicio:.1f}s - {fin:.1f}s] {hablante}: {texto}")
    return '\n'.join(lineas)


def formatear_contexto(info_llamada: dict) -> str:
    """Formatea el contexto de la llamada para el prompt."""
    agente = info_llamada.get('agente', {})
    cliente = info_llamada.get('cliente', {})
    llamada = info_llamada.get('llamada', {})
    tiempos = info_llamada.get('tiempos', {})
    
    contexto_lines = [
        f"- Agente: {agente.get('nombre', 'Desconocido')} ({agente.get('equipo', '')})",
        f"- Tipo de llamada: {llamada.get('tipo', 'DESCONOCIDO')}",
        f"- Campaña: {llamada.get('campana', '')}",
        f"- Duración total: {tiempos.get('duracion_total_seg', 0)} segundos",
        f"- Tiempo de conversación: {tiempos.get('talking_time_seg', 0)} segundos",
        f"- Origen del corte: {llamada.get('origen_corte', 'No especificado')}",
    ]
    
    return '\n'.join(contexto_lines)


def procesar_con_gemini(model, data: dict) -> Optional[dict]:
    """Procesa una transcripción con Gemini."""
    
    # Extraer datos
    info_llamada = data.get('info_llamada', {})
    conversacion = data.get('conversacion', [])
    
    if not conversacion:
        return None
    
    # Formatear prompt
    contexto = formatear_contexto(info_llamada)
    transcripcion = formatear_transcripcion(conversacion)
    
    prompt_completo = PROMPT_MEJORA.format(
        contexto=contexto,
        transcripcion=transcripcion
    )
    
    # Llamar a Gemini con reintentos
    for intento in range(MAX_RETRIES):
        try:
            response = model.generate_content(
                prompt_completo,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=MAX_OUTPUT_TOKENS,
                )
            )
            
            # Extraer JSON de la respuesta
            texto_respuesta = response.text.strip()
            
            # Limpiar el texto si viene con markdown
            if texto_respuesta.startswith('```json'):
                texto_respuesta = texto_respuesta[7:]
            if texto_respuesta.startswith('```'):
                texto_respuesta = texto_respuesta[3:]
            if texto_respuesta.endswith('```'):
                texto_respuesta = texto_respuesta[:-3]
            
            texto_respuesta = texto_respuesta.strip()
            
            # Intentar parsear directamente
            try:
                resultado = json.loads(texto_respuesta)
                return resultado
            except json.JSONDecodeError as parse_error:
                # Si falla, intentar limpiar caracteres problemáticos
                # Buscar el último } válido para truncar JSON incompleto
                ultimo_brace = texto_respuesta.rfind('}')
                if ultimo_brace > 0:
                    texto_respuesta = texto_respuesta[:ultimo_brace + 1]
                    resultado = json.loads(texto_respuesta)
                    return resultado
                else:
                    raise parse_error
            
        except json.JSONDecodeError as e:
            print(f"      ⚠️ Error parseando JSON (intento {intento + 1}): {e}")
            if intento == MAX_RETRIES - 1:
                return None
            time.sleep(1)
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                print(f"      ⚠️ Rate limit alcanzado, esperando 60s...")
                time.sleep(60)
            else:
                print(f"      ❌ Error en Gemini (intento {intento + 1}): {e}")
                if intento == MAX_RETRIES - 1:
                    return None
                time.sleep(2)
    
    return None


def procesar_archivo(model, json_path: Path) -> dict:
    """Procesa un archivo individual."""
    resultado = {
        "archivo": json_path.name,
        "status": "error",
        "mensaje": "",
        "diarizacion_corregida": False,
        "calidad": ""
    }
    
    try:
        # Leer archivo enriquecido
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Procesar con Gemini
        respuesta_gemini = procesar_con_gemini(model, data)
        
        if not respuesta_gemini:
            resultado["mensaje"] = "No se obtuvo respuesta de Gemini"
            return resultado
        
        # Aplicar el análisis a la transcripción
        analisis = respuesta_gemini.get('analisis', {})
        agente_detectado = analisis.get('agente_detectado', 'Hablante A')
        
        # Actualizar roles en la conversación original
        conversacion_mejorada = []
        for seg in data.get('conversacion', []):
            seg_mejorado = seg.copy()
            hablante_actual = seg.get('hablante', 'Hablante A')
            
            # Asignar rol basado en el análisis
            if hablante_actual == agente_detectado:
                seg_mejorado['rol'] = 'AGENTE'
            else:
                seg_mejorado['rol'] = 'CLIENTE'
            
            conversacion_mejorada.append(seg_mejorado)
        
        # Agregar el análisis y la conversación mejorada
        data["mejora_gemini"] = {
            "analisis": analisis,
            "conversacion_con_roles": conversacion_mejorada
        }
        data["procesado_mejora"] = datetime.now().isoformat()
        
        # Guardar archivo mejorado
        output_path = OUTPUT_DIR / json_path.name.replace('_enriquecido.json', '_mejorado.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Actualizar resultado
        resultado["status"] = "ok"
        resultado["mensaje"] = "Procesado correctamente"
        resultado["calidad"] = analisis.get('calidad_transcripcion', 'DESCONOCIDA')
        resultado["tipo_llamada"] = analisis.get('tipo_llamada', '')
        resultado["resultado_probable"] = analisis.get('resultado', '')
        
    except Exception as e:
        resultado["mensaje"] = str(e)
    
    return resultado


# ============================================================================
# PIPELINE PRINCIPAL
# ============================================================================

def obtener_procesados() -> set:
    """Obtiene lista de archivos ya procesados."""
    procesados = set()
    if OUTPUT_DIR.exists():
        for f in OUTPUT_DIR.iterdir():
            if f.suffix == '.json':
                # El nombre original sería sin _mejorado
                nombre_original = f.name.replace('_mejorado.json', '_enriquecido.json')
                procesados.add(nombre_original)
    return procesados

def ejecutar_pipeline_mejora(limite: int = None):
    """
    Ejecuta el pipeline de mejora con Gemini.
    
    Args:
        limite: Número máximo de archivos a procesar (None = todos)
    """
    print("=" * 80)
    print("PIPELINE DE MEJORA DE TRANSCRIPCIONES CON GEMINI")
    print("=" * 80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Modelo: {MODEL_NAME}")
    print(f"Input: {INPUT_DIR}")
    print(f"Output: {OUTPUT_DIR}")
    print("=" * 80)
    
    # Crear carpetas
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORTE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Obtener archivos ya procesados
    procesados = obtener_procesados()
    print(f"\n[INFO] Ya procesados anteriormente: {len(procesados):,}")
    
    # Configurar Gemini
    print("\n[CONFIG] Configurando Gemini...")
    model = configurar_gemini()
    
    # Listar archivos pendientes (excluyendo ya procesados)
    todos_archivos = [f for f in INPUT_DIR.iterdir() if f.suffix == '.json']
    archivos = [f for f in todos_archivos if f.name not in procesados]
    
    if limite:
        archivos = archivos[:limite]
    
    print(f"\n[INFO] Archivos pendientes: {len(archivos):,} de {len(todos_archivos):,} totales")
    
    if not archivos:
        print("\n[OK] No hay archivos pendientes por procesar!")
        return
    
    # Procesar
    resultados = []
    estadisticas = defaultdict(int)
    errores_consecutivos = 0
    
    for i, json_path in enumerate(archivos):
        print(f"\n[{i+1}/{len(archivos)}] {json_path.name[:55]}...")
        
        try:
            resultado = procesar_archivo(model, json_path)
            resultados.append(resultado)
            
            # Actualizar estadísticas
            estadisticas[resultado["status"]] += 1
            if resultado.get("diarizacion_corregida"):
                estadisticas["diarizacion_corregida"] += 1
            if resultado.get("calidad"):
                estadisticas[f"calidad_{resultado['calidad']}"] += 1
            if resultado.get("resultado_probable"):
                estadisticas[f"resultado_{resultado['resultado_probable']}"] += 1
            
            if resultado["status"] == "ok":
                print(f"   [OK] Calidad: {resultado.get('calidad', 'N/A')} - Resultado: {resultado.get('resultado_probable', 'N/A')}")
                errores_consecutivos = 0
            else:
                print(f"   [ERROR] {resultado['mensaje'][:60]}...")
                errores_consecutivos += 1
                
            # Si hay muchos errores consecutivos, pausar
            if errores_consecutivos >= 5:
                print(f"\n[PAUSA] Demasiados errores consecutivos. Esperando 30s...")
                time.sleep(30)
                errores_consecutivos = 0
                
        except KeyboardInterrupt:
            print("\n\n[INTERRUMPIDO] Guardando progreso...")
            break
        except Exception as e:
            print(f"   [ERROR CRITICO] {str(e)[:60]}")
            errores_consecutivos += 1
            if errores_consecutivos >= 10:
                print("\n[ABORT] Demasiados errores. Abortando...")
                break
        
        # Delay para evitar rate limit
        time.sleep(DELAY_BETWEEN_CALLS)
        
        # Mostrar progreso cada 100 archivos
        if (i + 1) % 100 == 0:
            print(f"\n--- PROGRESO: {i+1}/{len(archivos)} ({(i+1)*100/len(archivos):.1f}%) - OK: {estadisticas.get('ok', 0)} ---\n")
    
    # Generar reporte
    print(f"\n[INFO] Generando reporte...")
    
    reporte = {
        "fecha_proceso": datetime.now().isoformat(),
        "modelo": MODEL_NAME,
        "total_archivos": len(archivos),
        "procesados_ok": estadisticas.get('ok', 0),
        "estadisticas": dict(estadisticas),
        "detalles_errores": [r for r in resultados if r["status"] == "error"]
    }
    
    reporte_path = REPORTE_DIR / f"reporte_mejora_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(reporte_path, 'w', encoding='utf-8') as f:
        json.dump(reporte, f, ensure_ascii=False, indent=2)
    
    # Contar total procesados
    total_procesados = len(obtener_procesados())
    
    # Resumen final
    print("\n" + "=" * 80)
    print("RESUMEN DEL PROCESO")
    print("=" * 80)
    print(f"[OK] Procesados en esta sesion: {estadisticas.get('ok', 0):,}")
    print(f"[OK] Total procesados acumulado: {total_procesados:,}")
    print(f"[ERROR] Errores: {estadisticas.get('error', 0):,}")
    print(f"[INFO] Diarizacion corregida: {estadisticas.get('diarizacion_corregida', 0):,}")
    print(f"\n[INFO] Calidad de transcripciones:")
    print(f"   - Buena: {estadisticas.get('calidad_BUENA', 0):,}")
    print(f"   - Regular: {estadisticas.get('calidad_REGULAR', 0):,}")
    print(f"   - Mala: {estadisticas.get('calidad_MALA', 0):,}")
    print(f"\n[INFO] Resultados de llamadas:")
    print(f"   - Venta exitosa: {estadisticas.get('resultado_VENTA_EXITOSA', 0):,}")
    print(f"   - Rechazo: {estadisticas.get('resultado_RECHAZO', 0):,}")
    print(f"   - Pendiente: {estadisticas.get('resultado_PENDIENTE', 0):,}")
    print(f"   - Sin decision: {estadisticas.get('resultado_SIN_DECISION', 0):,}")
    print(f"   - Corte cliente: {estadisticas.get('resultado_CORTE_CLIENTE', 0):,}")
    print(f"\n[OUTPUT] Archivos mejorados en: {OUTPUT_DIR}")
    print(f"[REPORT] Reporte guardado en: {reporte_path}")
    print("=" * 80)
    
    return reporte


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Mejora de transcripciones con Gemini')
    parser.add_argument('--limite', type=int, default=None, 
                        help='Número máximo de archivos a procesar (default: todos)')
    parser.add_argument('--test', action='store_true',
                        help='Modo test: procesar solo 5 archivos')
    
    args = parser.parse_args()
    
    limite = 5 if args.test else args.limite
    
    ejecutar_pipeline_mejora(limite=limite)

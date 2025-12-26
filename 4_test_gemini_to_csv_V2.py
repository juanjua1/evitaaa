"""
Sistema de Evaluación de Transcripciones con Gemini AI
======================================================
Este script procesa transcripciones de llamadas y las evalúa según reglas 
predefinidas usando Google Gemini AI. Guarda los resultados de forma incremental
para evitar pérdida de datos en caso de interrupción.

Autor: Sistema de Evaluación EVA
Versión: 2.1 (manejo de cuota Gemini)
"""

import os
import json
import pandas as pd
import google.generativeai as genai
import re
from datetime import datetime
from typing import Dict, List, Optional, Set
import config

# =============================================================================
# CONFIGURACIÓN INICIAL
# =============================================================================

# Configurar API de Gemini
genai.configure(api_key=config.api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

# Rutas de archivos y carpetas
CARPETA_TRANSCRIPCIONES = r"J:\EVA\total_transcripciones"
CARPETA_REGLAS = r"J:\EVA\reglas"
CSV_SALIDA = r"J:\EVA\evaluaciones_modelo_gemini.csv"
ARCHIVO_PROCESADOS = r"J:\EVA\procesados.json"
LOG_ERRORES = r"J:\EVA\errores_procesamiento.log"

# =============================================================================
# TIPOS DE ERROR PERSONALIZADOS
# =============================================================================

class CuotaGeminiAgotada(Exception):
    """
    Excepción específica para indicar que se alcanzó el límite de cuota/tokens
    de la API de Gemini y que se debe detener el procesamiento.
    """
    pass


def es_error_cuota(error: Exception) -> bool:
    """
    Heurística simple para detectar si un error de la API está relacionado
    con límites de cuota o rate limits.

    Args:
        error: Excepción capturada

    Returns:
        True si el mensaje parece indicar problema de cuota, False en caso contrario.
    """
    msg = str(error).lower()
    patrones = [
        "rate limit",
        "quota",
        "quota exceeded",
        "resource exhausted",
        "resourceexhausted",
        "429"
    ]
    return any(p in msg for p in patrones)


# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

def log_mensaje(mensaje: str, tipo: str = "INFO") -> None:
    """
    Registra un mensaje con timestamp en consola y opcionalmente en archivo.
    
    Args:
        mensaje: Texto del mensaje a registrar
        tipo: Tipo de mensaje (INFO, ERROR, WARNING, SUCCESS)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    simbolos = {
        "INFO": "ℹ️",
        "ERROR": "❌",
        "WARNING": "⚠️",
        "SUCCESS": "✅",
        "PROCESSING": "🔄"
    }
    simbolo = simbolos.get(tipo, "•")
    mensaje_completo = f"[{timestamp}] {simbolo} {mensaje}"
    print(mensaje_completo)
    
    # Registrar errores en archivo de log
    if tipo == "ERROR":
        with open(LOG_ERRORES, "a", encoding="utf-8") as log:
            log.write(mensaje_completo + "\n")


def cargar_procesados() -> Set[str]:
    """
    Carga el conjunto de archivos ya procesados desde el archivo JSON.
    
    Returns:
        Set con los nombres de archivos procesados previamente
    """
    if os.path.exists(ARCHIVO_PROCESADOS):
        try:
            with open(ARCHIVO_PROCESADOS, "r", encoding="utf-8") as f:
                procesados = set(json.load(f))
            log_mensaje(f"Cargados {len(procesados)} archivos procesados anteriormente", "INFO")
            return procesados
        except Exception as e:
            log_mensaje(f"Error al cargar procesados: {e}", "WARNING")
            return set()
    else:
        log_mensaje("No se encontró archivo de procesados, iniciando desde cero", "INFO")
        return set()


def guardar_procesado(archivo: str, procesados: Set[str]) -> None:
    """
    Guarda un archivo como procesado en el registro JSON.
    
    Args:
        archivo: Nombre del archivo procesado
        procesados: Set de archivos procesados (se modifica in-place)
    """
    procesados.add(archivo)
    try:
        with open(ARCHIVO_PROCESADOS, "w", encoding="utf-8") as f:
            json.dump(list(procesados), f, ensure_ascii=False, indent=2)
        log_mensaje(f"Archivo {archivo} registrado como procesado", "SUCCESS")
    except Exception as e:
        log_mensaje(f"Error al guardar registro de procesados: {e}", "ERROR")


def cargar_reglas_desde_carpeta(carpeta: str) -> List[Dict]:
    """
    Carga todas las reglas de evaluación desde archivos JSON en una carpeta.
    
    Args:
        carpeta: Ruta de la carpeta conteniendo archivos de reglas
        
    Returns:
        Lista de diccionarios con las reglas cargadas
    """
    log_mensaje(f"Cargando reglas desde: {carpeta}", "PROCESSING")
    reglas = []
    
    if not os.path.exists(carpeta):
        log_mensaje(f"La carpeta de reglas no existe: {carpeta}", "ERROR")
        return reglas
    
    archivos_reglas = [f for f in os.listdir(carpeta) if f.endswith(".json")]
    
    for archivo in archivos_reglas:
        try:
            ruta_completa = os.path.join(carpeta, archivo)
            with open(ruta_completa, "r", encoding="utf-8") as file:
                regla = json.load(file)
                reglas.append(regla)
                log_mensaje(f"  ✓ Cargada regla: {regla.get('step_name', archivo)}", "INFO")
        except Exception as e:
            log_mensaje(f"Error al cargar regla {archivo}: {e}", "ERROR")
    
    log_mensaje(f"Total de reglas cargadas: {len(reglas)}", "SUCCESS")
    return reglas


def construir_dialogo(data: Dict) -> str:
    """
    Construye una representación textual del diálogo desde los datos de transcripción.
    
    Args:
        data: Diccionario con los datos de la transcripción
        
    Returns:
        String con el diálogo formateado (Hablante: texto)
    """
    dialogo = []
    conversacion = data.get("conversacion", [])
    
    for seg in conversacion:
        hablante = seg.get("hablante", "Desconocido")
        texto = seg.get("texto", "").strip()
        if texto:
            dialogo.append(f"{hablante}: {texto}")
    
    total_lineas = len(dialogo)
    log_mensaje(f"Diálogo construido: {total_lineas} intervenciones", "INFO")
    return "\n".join(dialogo)


def analizar_llamada_con_reglas(dialogo: str, metadata: Dict, reglas: Dict) -> str:
    """
    Envía el diálogo y reglas a Gemini AI para su análisis y evaluación.
    
    Args:
        dialogo: Texto completo del diálogo
        metadata: Metadatos de la transcripción (archivo, etc.)
        reglas: Diccionario con las reglas de evaluación
        
    Returns:
        Respuesta en texto de Gemini con el análisis en formato JSON
        
    Raises:
        CuotaGeminiAgotada: Si se detecta que se alcanzó el límite de cuota
        Exception: Para otros errores de la API
    """
    step_name = reglas.get('step_name', 'Sin nombre')
    log_mensaje(f"Enviando análisis a Gemini para etapa: {step_name}", "PROCESSING")
    
    prompt = f"""
Analizá la siguiente transcripción usando EXCLUSIVAMENTE las reglas provistas.

Devolveme SOLO un JSON con el siguiente formato:

{{
  "step_id": "{reglas.get('step_id')}",
  "step_name": "{reglas.get('step_name')}",
  "overall_score": number,
  "max_score": number,
  "compliance_percent": number,
  "results": [
      {{
        "id": "string",
        "complies": "yes | no | partial",
        "score_given": number,
        "justification": "string"
      }}
  ]
}}


METADATOS:
archivo: {metadata.get('archivo')}

REGLAS:
{json.dumps(reglas, ensure_ascii=False, indent=2)}

DIÁLOGO:
{dialogo}
"""
    
    try:
        response = model.generate_content(prompt)
        log_mensaje(f"✓ Respuesta recibida de Gemini para {step_name}", "SUCCESS")
        return response.text
    except Exception as e:
        log_mensaje(f"ERROR con la API de Gemini: {str(e)}", "ERROR")
        
        # <<< NUEVO: detección de error de cuota / rate limit
        if es_error_cuota(e):
            log_mensaje(
                "Detectado posible error de cuota/límite de Gemini. "
                "Se detendrá el procesamiento para evitar más llamadas fallidas.",
                "WARNING"
            )
            # Lanzamos una excepción específica para que el nivel superior pueda cortar el bucle
            raise CuotaGeminiAgotada(str(e))
        # <<< FIN NUEVO

        # Otros errores (no de cuota)
        log_mensaje(
            "Error de la API de Gemini no identificado como límite de cuota. "
            "El proceso continuará con el siguiente archivo.",
            "WARNING"
        )
        raise


def extraer_porcentaje(resultado_texto: str) -> Optional[float]:
    """
    Extrae el porcentaje de cumplimiento del resultado JSON de Gemini.
    
    Args:
        resultado_texto: Texto de respuesta de Gemini (debe contener JSON)
        
    Returns:
        Float con el porcentaje o None si no se encuentra
    """
    match = re.search(r'"compliance_percent"\s*:\s*([\d.]+)', resultado_texto)
    if match:
        porcentaje = float(match.group(1))
        return porcentaje
    else:
        log_mensaje("No se pudo extraer compliance_percent del resultado", "WARNING")
        return None


def calcular_puntaje_general(porcentajes: List[Optional[float]]) -> Optional[float]:
    """
    Calcula el promedio de porcentajes disponibles.
    
    Args:
        porcentajes: Lista de porcentajes (puede contener None)
        
    Returns:
        Promedio de porcentajes válidos o None si no hay datos
    """
    presentes = [p for p in porcentajes if p is not None]
    if presentes:
        promedio = sum(presentes) / len(presentes)
        return round(promedio, 2)
    return None


def guardar_resultado_csv(fila: Dict, es_primera_vez: bool) -> None:
    """
    Guarda un resultado individual en el CSV de forma incremental.
    
    Args:
        fila: Diccionario con los datos de una evaluación
        es_primera_vez: Si es True, escribe el encabezado
    """
    try:
        df_fila = pd.DataFrame([fila])
        df_fila.to_csv(
            CSV_SALIDA,
            mode="a",
            index=False,
            header=es_primera_vez,
            encoding="utf-8"
        )
        log_mensaje(f"✓ Resultado guardado en CSV: {fila['Agente']}", "SUCCESS")
    except Exception as e:
        log_mensaje(f"ERROR al guardar en CSV: {e}", "ERROR")
        raise


# =============================================================================
# FUNCIÓN PRINCIPAL DE PROCESAMIENTO
# =============================================================================

def procesar_transcripciones() -> None:
    """
    Función principal que orquesta todo el proceso de evaluación.
    Lee transcripciones, las evalúa con Gemini y guarda resultados incrementalmente.
    """
    # Banner inicial
    print("\n" + "="*70)
    print("  SISTEMA DE EVALUACIÓN DE TRANSCRIPCIONES - GEMINI AI")
    print("="*70 + "\n")
    
    log_mensaje("Iniciando proceso de evaluación", "INFO")
    
    # Cargar datos persistentes
    procesados = cargar_procesados()
    reglas_list = cargar_reglas_desde_carpeta(CARPETA_REGLAS)
    
    if not reglas_list:
        log_mensaje("No se cargaron reglas. Proceso abortado.", "ERROR")
        return
    
    # Obtener lista de archivos a procesar
    if not os.path.exists(CARPETA_TRANSCRIPCIONES):
        log_mensaje(f"La carpeta de transcripciones no existe: {CARPETA_TRANSCRIPCIONES}", "ERROR")
        return
    
    todos_los_archivos = [
        f for f in os.listdir(CARPETA_TRANSCRIPCIONES) 
        if f.endswith(".json")
    ]
    
    archivos_pendientes = [f for f in todos_los_archivos if f not in procesados]
    
    log_mensaje(f"Total de archivos encontrados: {len(todos_los_archivos)}", "INFO")
    log_mensaje(f"Archivos ya procesados: {len(procesados)}", "INFO")
    log_mensaje(f"Archivos pendientes: {len(archivos_pendientes)}", "INFO")
    
    if not archivos_pendientes:
        log_mensaje("No hay archivos pendientes de procesar", "SUCCESS")
        return
    
    # Determinar si el CSV ya existe (para el encabezado)
    csv_existe = os.path.exists(CSV_SALIDA)
    
    # Procesar cada archivo pendiente
    print("\n" + "-"*70)
    
    for idx, archivo in enumerate(archivos_pendientes, 1):
        print("\n" + "="*70)
        log_mensaje(f"Procesando archivo {idx}/{len(archivos_pendientes)}: {archivo}", "PROCESSING")
        print("="*70)
        
        try:
            # Cargar transcripción
            ruta_archivo = os.path.join(CARPETA_TRANSCRIPCIONES, archivo)
            with open(ruta_archivo, "r", encoding="utf-8") as file:
                data = json.load(file)
            data["archivo"] = archivo
            
            log_mensaje(f"✓ Archivo cargado correctamente", "SUCCESS")
            
            # Construir diálogo
            dialogo = construir_dialogo(data)
            
            if not dialogo:
                log_mensaje("ADVERTENCIA: Diálogo vacío, saltando archivo", "WARNING")
                continue
            
            # Evaluar cada etapa
            puntajes_etapas = []
            
            for idx_regla, reglas in enumerate(reglas_list, 1):
                step_name = reglas.get('step_name', f'Etapa {idx_regla}')
                print(f"\n  └─ Evaluando {step_name} ({idx_regla}/{len(reglas_list)})")
                
                # Aquí puede lanzarse CuotaGeminiAgotada y cortar todo el proceso
                resultado = analizar_llamada_con_reglas(dialogo, data, reglas)
                porcentaje = extraer_porcentaje(resultado)
                puntajes_etapas.append(porcentaje)
                
                if porcentaje is not None:
                    log_mensaje(f"    ✓ Cumplimiento: {porcentaje}%", "SUCCESS")
                else:
                    log_mensaje(f"    ⚠ No se pudo extraer porcentaje", "WARNING")
            
            # Construir fila de resultados
            fila = {
                "Agente": archivo,
                "Etapa_1_Porcentaje": puntajes_etapas[0] if len(puntajes_etapas) > 0 else None,
                "Etapa_2_Porcentaje": puntajes_etapas[1] if len(puntajes_etapas) > 1 else None,
                "Etapa_3_Porcentaje": puntajes_etapas[2] if len(puntajes_etapas) > 2 else None,
                "Etapa_4_Porcentaje": puntajes_etapas[3] if len(puntajes_etapas) > 3 else None,
                "Etapa_5_Porcentaje": puntajes_etapas[4] if len(puntajes_etapas) > 4 else None,
            }
            
            # Calcular puntaje general
            fila["Puntaje_General"] = calcular_puntaje_general(
                list(fila.values())[1:6]
            )
            
            log_mensaje(f"Puntaje General: {fila['Puntaje_General']}%", "INFO")
            
            # GUARDADO INCREMENTAL: Escribir inmediatamente al CSV
            guardar_resultado_csv(fila, es_primera_vez=(not csv_existe))
            csv_existe = True  # Después de la primera escritura, el archivo ya existe
            
            # Registrar como procesado
            guardar_procesado(archivo, procesados)
            
            log_mensaje(f"✅ Archivo {archivo} procesado completamente", "SUCCESS")
        
        except CuotaGeminiAgotada as e:
            # <<< NUEVO: caso específico de límite de cuota
            log_mensaje(
                "⚠️ Se alcanzó el límite de cuota/tokens de Gemini. "
                "El procesamiento se detendrá en este punto.",
                "ERROR"
            )
            log_mensaje(
                "Los archivos procesados hasta ahora quedaron guardados en el CSV "
                "y en el registro de procesados.",
                "INFO"
            )
            break
        
        except KeyboardInterrupt:
            log_mensaje("\n⚠️ Proceso interrumpido por el usuario", "WARNING")
            log_mensaje("Los datos procesados hasta ahora están guardados", "INFO")
            break
            
        except Exception as e:
            log_mensaje(f"ERROR al procesar {archivo}: {str(e)}", "ERROR")
            log_mensaje("Continuando con el siguiente archivo...", "INFO")
            continue
    
    # Resumen final
    print("\n" + "="*70)
    log_mensaje("PROCESO FINALIZADO", "SUCCESS")
    log_mensaje(f"Archivos procesados en esta sesión: {idx}", "INFO")
    log_mensaje(f"Total acumulado de archivos procesados: {len(procesados)}", "INFO")
    log_mensaje(f"Resultados guardados en: {CSV_SALIDA}", "SUCCESS")
    print("="*70 + "\n")


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================

if __name__ == "__main__":
    try:
        procesar_transcripciones()
    except Exception as e:
        log_mensaje(f"ERROR CRÍTICO: {str(e)}", "ERROR")
        print("\n⛔ El proceso se detuvo debido a un error crítico.")
        print("📋 Revisa el archivo de log para más detalles:", LOG_ERRORES)

"""
Sistema de Evaluación de Transcripciones con Gemini AI
======================================================
Este script procesa transcripciones de llamadas y las evalúa según reglas 
predefinidas usando Google Gemini AI. Aprovecha los datos ya clasificados
por los scripts de análisis previos.

Autor: Sistema de Evaluación EVA
Versión: 3.0 (Integrado con clasificaciones previas)
"""

import os
import json
import pandas as pd
import google.generativeai as genai
import re
import time
from datetime import datetime
from typing import Dict, List, Optional, Set
from pathlib import Path

# =============================================================================
# CONFIGURACIÓN INICIAL
# =============================================================================

# Intentar cargar config, si no existe usar variable de entorno
try:
    import config
    API_KEY = config.api_key
except:
    API_KEY = os.environ.get('GEMINI_API_KEY', '')

if not API_KEY:
    print("⚠️ No se encontró API key de Gemini. Configura config.py o variable GEMINI_API_KEY")

# Configurar API de Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-lite")

# Rutas de archivos y carpetas - RUTAS LOCALES
BASE_DIR = Path(__file__).parent
CARPETA_TRANSCRIPCIONES = BASE_DIR / "total_transcripciones" / "procesados"
CARPETA_REGLAS = BASE_DIR / "reglas"
CSV_CLASIFICACION = BASE_DIR / "reportes" / "clasificacion_completa" / "clasificacion_completa.csv"
CSV_CONSOLIDADO = BASE_DIR / "reportes" / "para_gemini" / "datos_consolidados_para_gemini.csv"
CSV_SALIDA = BASE_DIR / "reportes" / "evaluaciones_gemini.csv"
ARCHIVO_PROCESADOS = BASE_DIR / "reportes" / "gemini_procesados.json"
LOG_ERRORES = BASE_DIR / "reportes" / "errores_gemini.log"

# Configuración de rate limiting
DELAY_ENTRE_LLAMADAS = 2  # segundos entre llamadas a Gemini
MAX_REINTENTOS = 3

# =============================================================================
# TIPOS DE ERROR PERSONALIZADOS
# =============================================================================

class CuotaGeminiAgotada(Exception):
    """Excepción para límite de cuota de Gemini."""
    pass


def es_error_cuota(error: Exception) -> bool:
    """Detecta si un error está relacionado con límites de cuota."""
    msg = str(error).lower()
    patrones = ["rate limit", "quota", "resource exhausted", "429", "too many"]
    return any(p in msg for p in patrones)


# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

def log_mensaje(mensaje: str, tipo: str = "INFO") -> None:
    """Registra un mensaje con timestamp."""
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
    
    if tipo == "ERROR":
        with open(LOG_ERRORES, "a", encoding="utf-8") as log:
            log.write(mensaje_completo + "\n")


def cargar_procesados() -> Set[str]:
    """Carga el conjunto de archivos ya procesados."""
    if ARCHIVO_PROCESADOS.exists():
        try:
            with open(ARCHIVO_PROCESADOS, "r", encoding="utf-8") as f:
                procesados = set(json.load(f))
            log_mensaje(f"Cargados {len(procesados)} archivos procesados anteriormente", "INFO")
            return procesados
        except Exception as e:
            log_mensaje(f"Error al cargar procesados: {e}", "WARNING")
            return set()
    return set()


def guardar_procesado(archivo: str, procesados: Set[str]) -> None:
    """Guarda un archivo como procesado."""
    procesados.add(archivo)
    try:
        ARCHIVO_PROCESADOS.parent.mkdir(parents=True, exist_ok=True)
        with open(ARCHIVO_PROCESADOS, "w", encoding="utf-8") as f:
            json.dump(list(procesados), f, ensure_ascii=False, indent=2)
    except Exception as e:
        log_mensaje(f"Error al guardar procesados: {e}", "ERROR")


def cargar_clasificacion_previa() -> Optional[pd.DataFrame]:
    """Carga los datos de clasificación previa."""
    if CSV_CLASIFICACION.exists():
        try:
            df = pd.read_csv(CSV_CLASIFICACION)
            log_mensaje(f"Cargada clasificación previa: {len(df)} registros", "SUCCESS")
            return df
        except Exception as e:
            log_mensaje(f"Error al cargar clasificación: {e}", "WARNING")
    return None


def construir_dialogo(data: Dict) -> str:
    """Construye representación textual del diálogo."""
    dialogo = []
    conversacion = data.get("conversacion", [])
    
    for seg in conversacion:
        # Usar 'rol' si está disponible (archivos nuevos), sino usar 'hablante'
        hablante = seg.get("rol", seg.get("hablante", "Desconocido"))
        # Normalizar nombres
        if hablante.upper() in ['AGENTE', 'VENDEDOR']:
            hablante = "Agente"
        elif hablante.upper() in ['CLIENTE', 'USUARIO']:
            hablante = "Cliente"
        texto = seg.get("texto", "").strip()
        if texto:
            dialogo.append(f"{hablante}: {texto}")
    
    return "\n".join(dialogo)


def obtener_contexto_clasificacion(archivo: str, df_clasificacion: pd.DataFrame) -> Dict:
    """Obtiene el contexto de clasificación previa para un archivo."""
    if df_clasificacion is None:
        return {}
    
    fila = df_clasificacion[df_clasificacion['archivo'] == archivo]
    if len(fila) == 0:
        return {}
    
    fila = fila.iloc[0]
    return {
        'motivo': fila.get('motivo_principal', ''),
        'tiene_saludo': fila.get('tiene_saludo', False),
        'tiene_cierre': fila.get('tiene_cierre_correcto', False),
        'score_calidad': fila.get('score_calidad', 0),
        'planes_ofrecidos': fila.get('planes_ofrecidos', ''),
        'ofrece_fibra': fila.get('ofrece_fibra', False),
        'menciona_promo': fila.get('menciona_promo', False),
        'objeciones': fila.get('objeciones', ''),
        'sentimiento': fila.get('sentimiento', ''),
        'tiene_queja': fila.get('tiene_queja', False),
        'queja_resuelta': fila.get('queja_resuelta', False),
        'resultado': fila.get('resultado', ''),
        'duracion_min': fila.get('duracion_min', 0),
    }


def evaluar_con_gemini(dialogo: str, metadata: Dict, contexto: Dict) -> Dict:
    """
    Envía el diálogo a Gemini para evaluación completa.
    Usa el contexto de clasificación previa para enriquecer el análisis.
    """
    archivo = metadata.get('archivo', 'desconocido')
    agente = metadata.get('agente', 'desconocido')
    
    # Construir contexto previo
    contexto_str = ""
    if contexto:
        contexto_str = f"""
CONTEXTO PRE-CLASIFICADO:
- Motivo detectado: {contexto.get('motivo', 'no identificado')}
- Score calidad previo: {contexto.get('score_calidad', 0)}/100
- Planes ofrecidos: {contexto.get('planes_ofrecidos', 'ninguno')}
- Ofrece fibra: {'Sí' if contexto.get('ofrece_fibra') else 'No'}
- Menciona promo: {'Sí' if contexto.get('menciona_promo') else 'No'}
- Objeciones detectadas: {contexto.get('objeciones', 'ninguna')}
- Sentimiento cliente: {contexto.get('sentimiento', 'neutro')}
- Tiene queja: {'Sí' if contexto.get('tiene_queja') else 'No'}
- Queja resuelta: {'Sí' if contexto.get('queja_resuelta') else 'No'}
- Resultado: {contexto.get('resultado', 'sin cierre claro')}
- Duración: {contexto.get('duracion_min', 0)} minutos
"""
    
    prompt = f"""Sos un evaluador experto de calidad de llamadas de un call center de ventas de Movistar Argentina.

Analizá la siguiente transcripción y devolvé ÚNICAMENTE un JSON válido con la evaluación.

ARCHIVO: {archivo}
AGENTE: {agente}
{contexto_str}

## REGLAS DEL NEGOCIO MOVISTAR (OBLIGATORIAS para evaluar):

### PROMOCIÓN VIGENTE (MUY IMPORTANTE):
- Durante enero 2026 hay PROMOCIÓN del 80% de descuento
- Los agentes DEBEN mencionar esta promo: "80% de descuento", "ochenta por ciento"
- Si no menciona el descuento del 80%, penalizar en PROACTIVIDAD y OFERTA_PRODUCTOS

### FRASES PROHIBIDAS (restar puntos si las usa):
- "¿Te parece bien si...?" → NO se pregunta, se procede directamente
- "¿Le gustaría que...?" → Frase prohibida de cierre
- "¿Te interesaría conocer...?" → NO se pregunta, se comenta directamente
- "Podría interesarle" → Debe decir "LE VA a interesar"
- "Período de prueba gratuito" → NO EXISTE

### CRITERIOS DE EVALUACIÓN (puntuá cada uno de 0 a 100):

1. SALUDO_PRESENTACION: ¿Se presentó correctamente? (nombre, empresa, motivo)
   - CORRECTO: "Tengo una oferta que le VA a interesar"
   - INCORRECTO: "Tengo algo que PODRÍA interesarle"

2. IDENTIFICACION_CLIENTE: ¿Verificó que habla con la persona correcta?
   - CORRECTO: "Hola, ¿me comunico con [Nombre]?" para verificar identidad
   - IMPORTANTE: Es válido y necesario verificar que es la persona correcta

3. DETECCION_NECESIDADES: ¿Hizo las preguntas correctas para detectar necesidades?
   - CORRECTO: "¿Qué es lo que más usás del celular?" / "¿Cuántos GB tenés?"
   - INCORRECTO: "¿Qué es lo más importante para ti en un plan?"

4. OFERTA_PRODUCTOS: ¿Ofreció productos de forma directa y adecuada?
   - Evaluar si ofreció planes, fibra, equipos
   - IMPORTANTE: ¿Mencionó el 80% de descuento de la promo?
   - CORRECTO: Comentar directamente sobre fibra
   - INCORRECTO: Preguntar "¿Te interesaría conocer...?"

5. MANEJO_OBJECIONES: ¿Manejó las objeciones de forma personalizada?
   - CORRECTO: Rebatir la objeción específica del cliente
   - INCORRECTO: Respuestas genéricas iguales para todos

6. CIERRE: ¿Hizo cierre DIRECTO sin preguntar?
   - CORRECTO: Asignar sucursal directamente o buscar domicilio
   - INCORRECTO: Preguntar "¿Te parece bien si procedemos?"
   - REGLA: Nunca preguntar si quiere seguir, PROCEDER directamente

7. DESPEDIDA: ¿Se despidió correctamente?
   - CORRECTO: Ofrecer acompañamiento durante la portabilidad
   - INCORRECTO: "Estaré encantado de ayudarte en el futuro"

8. PROACTIVIDAD: ¿Ofreció fibra, la PROMO del 80% y productos adicionales?
   - CORRECTO: Mencionar el 80% de descuento, comentar sobre fibra
   - INCORRECTO: No mencionar la promo, preguntar si le interesa

9. EMPATIA: ¿Mostró empatía con el cliente?

10. RESOLUCION_PROBLEMAS: Si hubo quejas, ¿las resolvió o gestionó?

DIÁLOGO:
{dialogo[:8000]}

Devolvé SOLO este JSON (sin texto adicional, sin markdown):
{{
  "archivo": "{archivo}",
  "agente": "{agente}",
  "evaluacion": {{
    "saludo_presentacion": {{"puntaje": 0, "comentario": ""}},
    "identificacion_cliente": {{"puntaje": 0, "comentario": ""}},
    "deteccion_necesidades": {{"puntaje": 0, "comentario": ""}},
    "oferta_productos": {{"puntaje": 0, "comentario": ""}},
    "manejo_objeciones": {{"puntaje": 0, "comentario": ""}},
    "cierre": {{"puntaje": 0, "comentario": ""}},
    "despedida": {{"puntaje": 0, "comentario": ""}},
    "proactividad": {{"puntaje": 0, "comentario": ""}},
    "empatia": {{"puntaje": 0, "comentario": ""}},
    "resolucion_problemas": {{"puntaje": 0, "comentario": ""}}
  }},
  "puntaje_total": 0,
  "resumen": "",
  "areas_mejora": [],
  "fortalezas": []
}}
"""
    
    for intento in range(MAX_REINTENTOS):
        try:
            response = model.generate_content(prompt)
            texto = response.text
            
            # Limpiar respuesta
            texto = texto.strip()
            if texto.startswith("```json"):
                texto = texto[7:]
            if texto.startswith("```"):
                texto = texto[3:]
            if texto.endswith("```"):
                texto = texto[:-3]
            texto = texto.strip()
            
            # Parsear JSON
            resultado = json.loads(texto)
            return resultado
            
        except json.JSONDecodeError as e:
            log_mensaje(f"Error parseando JSON (intento {intento+1}): {e}", "WARNING")
            if intento < MAX_REINTENTOS - 1:
                time.sleep(DELAY_ENTRE_LLAMADAS)
                continue
            return None
            
        except Exception as e:
            if es_error_cuota(e):
                raise CuotaGeminiAgotada(str(e))
            
            log_mensaje(f"Error Gemini (intento {intento+1}): {e}", "WARNING")
            if intento < MAX_REINTENTOS - 1:
                time.sleep(DELAY_ENTRE_LLAMADAS * 2)
                continue
            return None
    
    return None


def guardar_resultado_csv(resultado: Dict, es_primera_vez: bool) -> None:
    """Guarda un resultado en el CSV."""
    try:
        # Aplanar la estructura
        evaluacion = resultado.get('evaluacion', {})
        
        fila = {
            'archivo': resultado.get('archivo', ''),
            'agente': resultado.get('agente', ''),
            'saludo_presentacion': evaluacion.get('saludo_presentacion', {}).get('puntaje', 0),
            'identificacion_cliente': evaluacion.get('identificacion_cliente', {}).get('puntaje', 0),
            'deteccion_necesidades': evaluacion.get('deteccion_necesidades', {}).get('puntaje', 0),
            'oferta_productos': evaluacion.get('oferta_productos', {}).get('puntaje', 0),
            'manejo_objeciones': evaluacion.get('manejo_objeciones', {}).get('puntaje', 0),
            'cierre': evaluacion.get('cierre', {}).get('puntaje', 0),
            'despedida': evaluacion.get('despedida', {}).get('puntaje', 0),
            'proactividad': evaluacion.get('proactividad', {}).get('puntaje', 0),
            'empatia': evaluacion.get('empatia', {}).get('puntaje', 0),
            'resolucion_problemas': evaluacion.get('resolucion_problemas', {}).get('puntaje', 0),
            'puntaje_total': resultado.get('puntaje_total', 0),
            'resumen': resultado.get('resumen', ''),
            'areas_mejora': ', '.join(resultado.get('areas_mejora', [])),
            'fortalezas': ', '.join(resultado.get('fortalezas', [])),
            'fecha_evaluacion': datetime.now().isoformat(),
        }
        
        df_fila = pd.DataFrame([fila])
        CSV_SALIDA.parent.mkdir(parents=True, exist_ok=True)
        df_fila.to_csv(
            CSV_SALIDA,
            mode="a",
            index=False,
            header=es_primera_vez,
            encoding="utf-8"
        )
        log_mensaje(f"✓ Resultado guardado: {fila['archivo']}", "SUCCESS")
    except Exception as e:
        log_mensaje(f"Error al guardar CSV: {e}", "ERROR")


def guardar_resultado_json(resultado: Dict, archivo: str) -> None:
    """Guarda el resultado completo en JSON."""
    try:
        carpeta_json = BASE_DIR / "reportes" / "evaluaciones_detalle"
        carpeta_json.mkdir(parents=True, exist_ok=True)
        
        nombre_json = archivo.replace('.json', '_evaluacion.json')
        ruta_json = carpeta_json / nombre_json
        
        with open(ruta_json, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log_mensaje(f"Error al guardar JSON detalle: {e}", "WARNING")


# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================

def procesar_transcripciones(limite: int = None) -> None:
    """
    Función principal que procesa las transcripciones con Gemini.
    
    Args:
        limite: Número máximo de archivos a procesar (None = todos)
    """
    print("\n" + "="*70)
    print("  🤖 EVALUACIÓN DE TRANSCRIPCIONES CON GEMINI AI")
    print("="*70 + "\n")
    
    log_mensaje("Iniciando proceso de evaluación", "INFO")
    
    # Cargar datos previos
    procesados = cargar_procesados()
    df_clasificacion = cargar_clasificacion_previa()
    
    # Verificar carpeta de transcripciones
    if not CARPETA_TRANSCRIPCIONES.exists():
        log_mensaje(f"No existe la carpeta: {CARPETA_TRANSCRIPCIONES}", "ERROR")
        return
    
    # Obtener archivos pendientes
    todos_archivos = list(CARPETA_TRANSCRIPCIONES.glob("*.json"))
    archivos_pendientes = [f for f in todos_archivos if f.name not in procesados]
    
    if limite:
        archivos_pendientes = archivos_pendientes[:limite]
    
    log_mensaje(f"Total archivos: {len(todos_archivos)}", "INFO")
    log_mensaje(f"Ya procesados: {len(procesados)}", "INFO")
    log_mensaje(f"Pendientes a procesar: {len(archivos_pendientes)}", "INFO")
    
    if not archivos_pendientes:
        log_mensaje("No hay archivos pendientes", "SUCCESS")
        return
    
    # Procesar
    csv_existe = CSV_SALIDA.exists()
    procesados_sesion = 0
    errores_sesion = 0
    
    print("\n" + "-"*70)
    
    for idx, archivo_path in enumerate(archivos_pendientes, 1):
        archivo = archivo_path.name
        
        print(f"\n[{idx}/{len(archivos_pendientes)}] Procesando: {archivo}")
        
        try:
            # Cargar transcripción
            with open(archivo_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Obtener metadata
            metadata = data.get('metadata_llamada', {})
            info = data.get('info_llamada', {})
            
            metadata_eval = {
                'archivo': archivo,
                'agente': metadata.get('agente_nombre', '') or info.get('agente', {}).get('nombre', 'desconocido'),
            }
            
            # Construir diálogo
            dialogo = construir_dialogo(data)
            
            if not dialogo or len(dialogo) < 50:
                log_mensaje("Diálogo muy corto, saltando", "WARNING")
                continue
            
            # Obtener contexto de clasificación previa
            contexto = obtener_contexto_clasificacion(archivo, df_clasificacion)
            
            # Evaluar con Gemini
            log_mensaje("Enviando a Gemini...", "PROCESSING")
            resultado = evaluar_con_gemini(dialogo, metadata_eval, contexto)
            
            if resultado:
                # Guardar resultados
                guardar_resultado_csv(resultado, es_primera_vez=(not csv_existe))
                csv_existe = True
                guardar_resultado_json(resultado, archivo)
                guardar_procesado(archivo, procesados)
                
                puntaje = resultado.get('puntaje_total', 0)
                log_mensaje(f"✅ Puntaje total: {puntaje}/100", "SUCCESS")
                procesados_sesion += 1
            else:
                log_mensaje("No se obtuvo resultado válido", "WARNING")
                errores_sesion += 1
            
            # Rate limiting
            time.sleep(DELAY_ENTRE_LLAMADAS)
            
        except CuotaGeminiAgotada:
            log_mensaje("⚠️ Límite de cuota alcanzado. Deteniendo...", "WARNING")
            break
            
        except KeyboardInterrupt:
            log_mensaje("\n⚠️ Interrumpido por usuario", "WARNING")
            break
            
        except Exception as e:
            log_mensaje(f"Error procesando {archivo}: {e}", "ERROR")
            errores_sesion += 1
            continue
    
    # Resumen final
    print("\n" + "="*70)
    log_mensaje("PROCESO FINALIZADO", "SUCCESS")
    log_mensaje(f"Procesados en esta sesión: {procesados_sesion}", "INFO")
    log_mensaje(f"Errores en esta sesión: {errores_sesion}", "INFO")
    log_mensaje(f"Total acumulado: {len(procesados)}", "INFO")
    log_mensaje(f"Resultados en: {CSV_SALIDA}", "SUCCESS")
    print("="*70 + "\n")


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================

if __name__ == "__main__":
    import sys
    
    # Permitir pasar límite como argumento
    limite = None
    if len(sys.argv) > 1:
        try:
            limite = int(sys.argv[1])
            print(f"Procesando máximo {limite} archivos")
        except:
            pass
    
    try:
        procesar_transcripciones(limite=limite)
    except Exception as e:
        log_mensaje(f"ERROR CRÍTICO: {e}", "ERROR")
        print(f"\n⛔ Error crítico: {e}")

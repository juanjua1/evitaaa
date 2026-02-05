"""
Script de Coaching IA para Vendedores
Genera análisis exhaustivos y planes de acción personalizados usando Gemini Pro
Actúa como un Jefe de Ventas experimentado
"""

import os
import json
import pandas as pd
from datetime import datetime
import time
import sys

# Suprimir warnings
import warnings
warnings.filterwarnings("ignore")

import google.generativeai as genai
import numpy as np
from config import api_key

# Configurar API
genai.configure(api_key=api_key)

def convertir_tipos_nativos(obj):
    """Convierte tipos numpy/pandas a tipos nativos de Python para JSON."""
    if isinstance(obj, dict):
        return {k: convertir_tipos_nativos(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convertir_tipos_nativos(v) for v in obj]
    elif isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32, np.float16)):
        return float(obj) if not np.isnan(obj) else 0.0
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif pd.isna(obj):
        return None
    else:
        return obj

# Usar modelo efectivo para análisis
MODEL_NAME = "gemini-2.0-flash"  # Modelo efectivo y económico para coaching

# Directorios
DIR_REPORTES = "reportes"
DIR_COACHING = os.path.join(DIR_REPORTES, "coaching_vendedores")
os.makedirs(DIR_COACHING, exist_ok=True)

# Fechas para separar períodos
FECHA_CORTE = "2026-01-19"  # Fecha que separa período anterior del nuevo

def log(mensaje, tipo="info"):
    """Logger con timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    emoji = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}.get(tipo, "")
    print(f"[{timestamp}] {emoji} {mensaje}")


def extraer_fecha_de_archivo(nombre_archivo):
    """Extrae la fecha del nombre del archivo (formato 260105XXXXXX -> fecha)"""
    import re
    # El nombre tiene formato como 260105102252090_ACD_69849 donde 2601 = 26 enero, 05 = 2025/2026
    match = re.search(r'(\d{2})(\d{2})(\d{2})', nombre_archivo)
    if match:
        dia = int(match.group(1))
        mes = int(match.group(2))
        # Año 05 = 2025, 06 = 2026
        anio_corto = int(match.group(3))
        anio = 2020 + anio_corto
        try:
            from datetime import date
            return date(anio, mes, dia)
        except:
            return None
    return None


def cargar_coaching_previo(agente):
    """Carga el coaching anterior de un agente si existe"""
    archivo_individual = os.path.join(DIR_COACHING, f"coaching_{agente.replace(' ', '_')}.json")
    if os.path.exists(archivo_individual):
        with open(archivo_individual, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def cargar_datos_completos():
    """Carga todos los datos disponibles para el análisis"""
    datos = {}
    
    # Cargar evaluaciones de Gemini
    ruta_eval = os.path.join(DIR_REPORTES, "evaluaciones_gemini.csv")
    if os.path.exists(ruta_eval):
        datos['evaluaciones'] = pd.read_csv(ruta_eval)
        log(f"Cargadas {len(datos['evaluaciones'])} evaluaciones de IA")
    
    # Cargar clasificación completa
    ruta_clasif = os.path.join(DIR_REPORTES, "clasificacion_completa", "clasificacion_completa.csv")
    if os.path.exists(ruta_clasif):
        datos['clasificacion'] = pd.read_csv(ruta_clasif)
        log(f"Cargadas {len(datos['clasificacion'])} clasificaciones")
    
    # Cargar análisis integral
    ruta_integral = os.path.join(DIR_REPORTES, "analisis_integral", "analisis_integral.csv")
    if os.path.exists(ruta_integral):
        datos['integral'] = pd.read_csv(ruta_integral)
        log(f"Cargados {len(datos['integral'])} registros integrales")
    
    # Cargar cierres comerciales
    ruta_cierres = os.path.join(DIR_REPORTES, "cierres_comerciales", "cierres_comerciales.csv")
    if os.path.exists(ruta_cierres):
        datos['cierres'] = pd.read_csv(ruta_cierres, sep=';')
        log(f"Cargados {len(datos['cierres'])} cierres comerciales")
    
    # Cargar datos de calidad
    ruta_calidad = os.path.join("datos_calidad", "datos_calidad_procesados.json")
    if os.path.exists(ruta_calidad):
        with open(ruta_calidad, 'r', encoding='utf-8') as f:
            datos['calidad'] = json.load(f)
        log(f"Cargados datos de calidad (llamadas, tiempos, ventas)")
    
    return datos


def obtener_metricas_agente(agente, datos):
    """Recopila todas las métricas disponibles de un agente, separando por período"""
    from datetime import date
    fecha_corte = date(2026, 1, 19)
    
    metricas = {
        'agente': agente,
        'evaluaciones': {},
        'evaluaciones_semana_anterior': {},  # 12-16 enero
        'evaluaciones_semana_actual': {},     # 19-24 enero
        'clasificacion': {},
        'integral': {},
        'cierres': {},
        'calidad_llamadas': {},
        'calidad_ventas': {}
    }
    
    # Métricas de evaluaciones IA
    if 'evaluaciones' in datos:
        df_ag = datos['evaluaciones'][datos['evaluaciones']['agente'] == agente].copy()
        if len(df_ag) > 0:
            # Extraer fecha de cada archivo
            df_ag['fecha'] = df_ag['archivo'].apply(extraer_fecha_de_archivo)
            
            # Separar por período
            df_anterior = df_ag[df_ag['fecha'] < fecha_corte] if 'fecha' in df_ag.columns else pd.DataFrame()
            df_actual = df_ag[df_ag['fecha'] >= fecha_corte] if 'fecha' in df_ag.columns else pd.DataFrame()
            
            # Métricas generales (todo el historial)
            metricas['evaluaciones'] = {
                'total_evaluadas': len(df_ag),
                'puntaje_promedio': round(df_ag['puntaje_total'].mean(), 1),
                'puntaje_min': df_ag['puntaje_total'].min(),
                'puntaje_max': df_ag['puntaje_total'].max(),
                'desviacion_std': round(df_ag['puntaje_total'].std(), 1),
                'llamadas_excelentes': len(df_ag[df_ag['puntaje_total'] >= 80]),
                'llamadas_criticas': len(df_ag[df_ag['puntaje_total'] <= 20]),
                'criterios': {}
            }
            
            # Puntajes por criterio
            criterios = ['saludo_presentacion', 'identificacion_cliente', 'deteccion_necesidades',
                        'oferta_productos', 'manejo_objeciones', 'cierre', 'despedida',
                        'proactividad', 'empatia', 'resolucion_problemas']
            
            for c in criterios:
                if c in df_ag.columns:
                    metricas['evaluaciones']['criterios'][c] = round(df_ag[c].mean(), 1)
            
            # Áreas de mejora frecuentes
            areas_mejora = []
            for areas in df_ag['areas_mejora'].dropna():
                if isinstance(areas, str):
                    for area in areas.split(','):
                        area = area.strip().strip('"').strip("'").strip('[').strip(']')
                        if area:
                            areas_mejora.append(area)
            
            if areas_mejora:
                from collections import Counter
                metricas['evaluaciones']['areas_mejora_frecuentes'] = dict(Counter(areas_mejora).most_common(5))
            
            # Fortalezas
            fortalezas = []
            for fort in df_ag['fortalezas'].dropna():
                if isinstance(fort, str):
                    for f in fort.split(','):
                        f = f.strip().strip('"').strip("'").strip('[').strip(']')
                        if f:
                            fortalezas.append(f)
            
            if fortalezas:
                from collections import Counter
                metricas['evaluaciones']['fortalezas_frecuentes'] = dict(Counter(fortalezas).most_common(5))
            
            # Ejemplos de resúmenes (las 3 mejores y 3 peores)
            mejores = df_ag.nlargest(3, 'puntaje_total')[['puntaje_total', 'resumen']].to_dict('records')
            peores = df_ag.nsmallest(3, 'puntaje_total')[['puntaje_total', 'resumen']].to_dict('records')
            metricas['evaluaciones']['ejemplos_mejores'] = mejores
            metricas['evaluaciones']['ejemplos_peores'] = peores
            
            # === MÉTRICAS POR PERÍODO ===
            # Semana anterior (12-16 enero)
            if len(df_anterior) > 0:
                metricas['evaluaciones_semana_anterior'] = {
                    'periodo': '12-16 Enero 2026',
                    'total_evaluadas': len(df_anterior),
                    'puntaje_promedio': round(df_anterior['puntaje_total'].mean(), 1),
                    'llamadas_excelentes': len(df_anterior[df_anterior['puntaje_total'] >= 80]),
                    'llamadas_criticas': len(df_anterior[df_anterior['puntaje_total'] <= 20]),
                    'criterios': {c: round(df_anterior[c].mean(), 1) for c in criterios if c in df_anterior.columns}
                }
            
            # Semana actual (19-24 enero)
            if len(df_actual) > 0:
                metricas['evaluaciones_semana_actual'] = {
                    'periodo': '19-24 Enero 2026',
                    'total_evaluadas': len(df_actual),
                    'puntaje_promedio': round(df_actual['puntaje_total'].mean(), 1),
                    'llamadas_excelentes': len(df_actual[df_actual['puntaje_total'] >= 80]),
                    'llamadas_criticas': len(df_actual[df_actual['puntaje_total'] <= 20]),
                    'criterios': {c: round(df_actual[c].mean(), 1) for c in criterios if c in df_actual.columns}
                }
                
                # Calcular evolución si hay datos de ambos períodos
                if len(df_anterior) > 0:
                    metricas['evolucion'] = {
                        'cambio_puntaje': round(df_actual['puntaje_total'].mean() - df_anterior['puntaje_total'].mean(), 1),
                        'mejoro': df_actual['puntaje_total'].mean() > df_anterior['puntaje_total'].mean(),
                        'criterios_mejoraron': [],
                        'criterios_empeoraron': [],
                        'criterios_igual': []
                    }
                    for c in criterios:
                        if c in df_anterior.columns and c in df_actual.columns:
                            diff = df_actual[c].mean() - df_anterior[c].mean()
                            if diff > 0.5:
                                metricas['evolucion']['criterios_mejoraron'].append(f"{c} (+{round(diff, 1)})")
                            elif diff < -0.5:
                                metricas['evolucion']['criterios_empeoraron'].append(f"{c} ({round(diff, 1)})")
                            else:
                                metricas['evolucion']['criterios_igual'].append(c)
    
    # Métricas de clasificación
    if 'clasificacion' in datos:
        df_ag = datos['clasificacion'][datos['clasificacion']['agente'] == agente]
        if len(df_ag) > 0:
            metricas['clasificacion'] = {
                'total_llamadas': len(df_ag),
                'con_saludo': len(df_ag[df_ag.get('tiene_saludo', False) == True]) if 'tiene_saludo' in df_ag.columns else 0,
                'con_cierre': len(df_ag[df_ag.get('tiene_cierre', False) == True]) if 'tiene_cierre' in df_ag.columns else 0,
                'con_identificacion': len(df_ag[df_ag.get('tiene_identificacion', False) == True]) if 'tiene_identificacion' in df_ag.columns else 0,
                'ofrece_plan': len(df_ag[df_ag.get('ofrece_plan', False) == True]) if 'ofrece_plan' in df_ag.columns else 0,
                'ofrece_fibra': len(df_ag[df_ag.get('ofrece_fibra', False) == True]) if 'ofrece_fibra' in df_ag.columns else 0,
                'ventas': len(df_ag[df_ag.get('es_venta', False) == True]) if 'es_venta' in df_ag.columns else 0,
                'score_calidad_prom': round(df_ag['score_calidad'].mean(), 1) if 'score_calidad' in df_ag.columns else 0,
            }
            
            # Calcular porcentajes
            total = metricas['clasificacion']['total_llamadas']
            if total > 0:
                metricas['clasificacion']['pct_saludo'] = round(metricas['clasificacion']['con_saludo'] / total * 100, 1)
                metricas['clasificacion']['pct_cierre'] = round(metricas['clasificacion']['con_cierre'] / total * 100, 1)
                metricas['clasificacion']['pct_plan'] = round(metricas['clasificacion']['ofrece_plan'] / total * 100, 1)
                metricas['clasificacion']['pct_fibra'] = round(metricas['clasificacion']['ofrece_fibra'] / total * 100, 1)
                metricas['clasificacion']['tasa_conversion'] = round(metricas['clasificacion']['ventas'] / total * 100, 1)
    
    # Métricas integrales (duración, etc.)
    if 'integral' in datos:
        df_ag = datos['integral'][datos['integral']['agente'] == agente]
        if len(df_ag) > 0:
            metricas['integral'] = {
                'duracion_promedio_seg': round(df_ag['duracion_seg'].mean(), 0) if 'duracion_seg' in df_ag.columns else 0,
                'duracion_promedio_min': round(df_ag['duracion_seg'].mean() / 60, 1) if 'duracion_seg' in df_ag.columns else 0,
            }
            
            # Distribución por rango de duración
            if 'rango_duracion' in df_ag.columns:
                rangos = df_ag['rango_duracion'].value_counts().to_dict()
                metricas['integral']['distribucion_duracion'] = rangos
    
    # Métricas de cierres
    if 'cierres' in datos:
        df_ag = datos['cierres'][datos['cierres']['agente'] == agente]
        if len(df_ag) > 0:
            metricas['cierres'] = {
                'total_ventas': len(df_ag),
                'porcentaje_cierre_prom': round(df_ag['porcentaje'].mean(), 1) if 'porcentaje' in df_ag.columns else 0,
            }
    
    # Métricas de calidad - Llamadas
    if 'calidad' in datos and 'llamadas' in datos['calidad']:
        llamadas_calidad = datos['calidad']['llamadas']
        # Buscar el agente en la lista de llamadas (buscar por código de agente)
        agente_lower = agente.lower()
        for item in llamadas_calidad:
            if isinstance(item, dict):
                agente_calidad = item.get('agente', '').lower()
                vendedor_calidad = item.get('vendedor', '').lower()
                if agente_lower in agente_calidad or agente_lower in vendedor_calidad or agente_calidad in agente_lower:
                    metricas['calidad_llamadas'] = {
                        'total_llamadas': item.get('total_llamadas', 0),
                        'tmo_seg': item.get('tmo_seg', 0),
                        'tmo_formato': item.get('tmo_fmt', ''),
                        'supera_1min': item.get('supera_1min', 0),
                        'pct_supera_1min': item.get('pct_supera_1min', 0),
                        'supera_5min': item.get('supera_5min', 0),
                        'pct_supera_5min': item.get('pct_supera_5min', 0),
                        'menos_30seg': item.get('menos_30seg', 0),
                        'capta_atencion': item.get('capta_atencion', 0),
                        'pct_capta_atencion': item.get('pct_capta_atencion', 0),
                        'corte_cliente': item.get('corte_cliente', 0),
                        'corte_agente': item.get('corte_agente', 0),
                        'estado_calidad': item.get('estado', ''),
                        'equipo': item.get('equipo', '')
                    }
                    break
    
    # Métricas de calidad - Ventas
    if 'calidad' in datos and 'ventas' in datos['calidad']:
        ventas_calidad = datos['calidad']['ventas']
        if 'por_vendedor' in ventas_calidad:
            agente_lower = agente.lower()
            for item in ventas_calidad['por_vendedor']:
                if isinstance(item, dict):
                    vendedor_calidad = item.get('vendedor', '').lower()
                    if agente_lower in vendedor_calidad or vendedor_calidad in agente_lower:
                        metricas['calidad_ventas'] = {
                            'total_ventas': item.get('total_ventas', 0),
                            'aprobadas': item.get('aprobadas', 0),
                            'canceladas': item.get('canceladas', 0),
                            'preventa': item.get('preventa', 0),
                            'tasa_aprobacion': item.get('tasa_aprobacion', 0),
                            'dif_vs_promedio': item.get('dif_vs_promedio', 0),
                            'estado_ventas': item.get('estado', '')
                        }
                        break
    
    return metricas


def calcular_comparativa_general(agente, datos):
    """Calcula cómo se compara el agente con el promedio general"""
    comparativa = {}
    
    if 'evaluaciones' in datos:
        df = datos['evaluaciones']
        df_ag = df[df['agente'] == agente]
        
        if len(df_ag) > 0:
            prom_general = df['puntaje_total'].mean()
            prom_agente = df_ag['puntaje_total'].mean()
            
            comparativa['puntaje_ia'] = {
                'agente': round(prom_agente, 1),
                'general': round(prom_general, 1),
                'diferencia': round(prom_agente - prom_general, 1),
                'percentil': round((df['puntaje_total'] < prom_agente).mean() * 100, 1)
            }
            
            # Por criterio
            criterios = ['saludo_presentacion', 'identificacion_cliente', 'deteccion_necesidades',
                        'oferta_productos', 'manejo_objeciones', 'cierre', 'despedida',
                        'proactividad', 'empatia', 'resolucion_problemas']
            
            comparativa['criterios'] = {}
            for c in criterios:
                if c in df.columns and c in df_ag.columns:
                    prom_gen = df[c].mean()
                    prom_ag = df_ag[c].mean()
                    comparativa['criterios'][c] = {
                        'agente': round(prom_ag, 1),
                        'general': round(prom_gen, 1),
                        'diferencia': round(prom_ag - prom_gen, 1)
                    }
    
    if 'clasificacion' in datos:
        df = datos['clasificacion']
        df_ag = df[df['agente'] == agente]
        
        if len(df_ag) > 0 and 'es_venta' in df.columns:
            tasa_general = df['es_venta'].mean() * 100
            tasa_agente = df_ag['es_venta'].mean() * 100
            
            comparativa['conversion'] = {
                'agente': round(tasa_agente, 1),
                'general': round(tasa_general, 1),
                'diferencia': round(tasa_agente - tasa_general, 1)
            }
    
    return comparativa


def generar_prompt_coaching(agente, metricas, comparativa, metricas_generales, coaching_previo=None):
    """Genera el prompt para el análisis de coaching con historial"""
    
    # Convertir todos los tipos numpy/pandas a tipos nativos de Python
    metricas = convertir_tipos_nativos(metricas)
    comparativa = convertir_tipos_nativos(comparativa)
    metricas_generales = convertir_tipos_nativos(metricas_generales)
    
    # Sección de historial si existe coaching previo
    seccion_historial = ""
    if coaching_previo:
        coaching_previo = convertir_tipos_nativos(coaching_previo)
        metricas_prev = coaching_previo.get('metricas', {}).get('evaluaciones', {})
        fecha_prev = coaching_previo.get('fecha_generacion', 'Fecha desconocida')[:10]
        seccion_historial = f"""
## 📜 HISTORIAL DEL VENDEDOR (Coaching anterior del {fecha_prev}):

### Métricas del período anterior:
- Puntaje IA promedio: {metricas_prev.get('puntaje_promedio', 'N/A')}
- Llamadas evaluadas: {metricas_prev.get('total_evaluadas', 'N/A')}
- Llamadas excelentes (≥80): {metricas_prev.get('llamadas_excelentes', 'N/A')}
- Llamadas críticas (≤20): {metricas_prev.get('llamadas_criticas', 'N/A')}

### Áreas de mejora identificadas anteriormente:
{json.dumps(metricas_prev.get('areas_mejora_frecuentes', {}), indent=2, ensure_ascii=False)}

### Fortalezas identificadas anteriormente:
{json.dumps(metricas_prev.get('fortalezas_frecuentes', {}), indent=2, ensure_ascii=False)}

⚠️ IMPORTANTE: Compara el desempeño actual con este historial para identificar EVOLUCIÓN.
"""
    
    # Sección de evolución si hay datos comparativos
    seccion_evolucion = ""
    if 'evolucion' in metricas:
        evol = metricas['evolucion']
        tendencia = "📈 MEJORÓ" if evol.get('mejoro') else "📉 EMPEORÓ"
        seccion_evolucion = f"""
## 🔄 EVOLUCIÓN ENTRE PERÍODOS:

### Tendencia General: {tendencia} ({evol.get('cambio_puntaje', 0):+.1f} puntos)

### Semana Anterior (12-16 Enero):
{json.dumps(metricas.get('evaluaciones_semana_anterior', {}), indent=2, ensure_ascii=False)}

### Semana Actual (19-24 Enero):
{json.dumps(metricas.get('evaluaciones_semana_actual', {}), indent=2, ensure_ascii=False)}

### Criterios que MEJORARON:
{', '.join(evol.get('criterios_mejoraron', ['Ninguno'])) or 'Ninguno'}

### Criterios que EMPEORARON:
{', '.join(evol.get('criterios_empeoraron', ['Ninguno'])) or 'Ninguno'}

### Criterios ESTABLES:
{', '.join(evol.get('criterios_igual', ['Ninguno'])) or 'Ninguno'}
"""
    
    prompt = f"""
Eres un JEFE DE VENTAS experimentado y mentor de alto rendimiento en telecomunicaciones (Movistar Argentina). 
Tu misión es analizar exhaustivamente el desempeño del vendedor y crear un plan de acción 
personalizado para ayudarlo a alcanzar su MÁXIMO POTENCIAL.

⚠️ ESTE ANÁLISIS CONSIDERA EL HISTORIAL DEL VENDEDOR Y SU EVOLUCIÓN RECIENTE.
El plan de acción debe enfocarse en la ÚLTIMA SEMANA (19-24 Enero), destacando:
- Qué MEJORÓ respecto al período anterior
- Qué EMPEORÓ y necesita atención urgente
- Qué SIGUE PENDIENTE de trabajar
{seccion_historial}
{seccion_evolucion}

## ⚠️ REGLAS CRÍTICAS DEL NEGOCIO (OBLIGATORIAS):

### FRASES PROHIBIDAS - NUNCA SUGERIR:
- "¿Te parece bien si...?" → NO se pregunta, se procede directamente
- "¿Le gustaría que...?" → Frase prohibida de cierre
- "¿Te interesaría conocer...?" → NO se pregunta, se comenta directamente
- "Podría interesarle" → Debe decir "LE VA a interesar"
- "Período de prueba gratuito" → NO EXISTE
- "Estaré encantado de ayudarte en el futuro" → Solo acompañamiento durante portabilidad
- "Vi que visitó nuestra página web" → NO tienen acceso a esa info
- "Investigar necesidades antes de la llamada" → NO se puede hacer

### ACCIONES CORRECTAS POR CRITERIO:

1. **IDENTIFICACIÓN DEL CLIENTE**: 
   - CORRECTO: "Hola, ¿me comunico con [Nombre]?" para verificar que es la persona correcta
   - Es IMPORTANTE verificar identidad para asegurar contacto correcto

2. **DETECCIÓN DE NECESIDADES**:
   - INCORRECTO: "¿Qué es lo más importante para ti en un plan?"
   - CORRECTO: "¿Qué es lo que más usás del celular?" / "¿Cuántos GB tenés en tu plan?"

3. **CIERRE DE VENTAS**:
   - EVALUAR: Que el cierre se complete (aunque haya interrupciones está bien)
   - CORRECTO: Asignar sucursal o buscar domicilio del cliente para completar la venta
   - NO PENALIZAR: Si el cierre no fue fluido o tuvo pausas, lo importante es que se haya completado

4. **DESPEDIDA**:
   - EVALUAR: Que se despida de forma cordial y profesional
   - OPCIONAL: Ofrecer acompañamiento durante la portabilidad (no penalizar si no lo hace)
   - INCORRECTO: "Estaré encantado de ayudarte en el futuro"

5. **OFERTA DE FIBRA (Proactividad)**:
   - INCORRECTO: "¿Te interesaría conocer nuestros servicios de fibra?"
   - CORRECTO: Comentar DIRECTAMENTE sobre fibra sin preguntar
   - REGLA: TODOS deben ofrecer fibra de forma directa, sin preguntar

6. **MANEJO DE OBJECIONES**:
   - INCORRECTO: Respuestas genéricas iguales para todos
   - CORRECTO: Rebatir la objeción PUNTUAL de CADA cliente
   - Sincronizar/personalizar la respuesta según el cliente específico

7. **SALUDO Y PRESENTACIÓN**:
   - INCORRECTO: "Tengo una oferta que podría interesarle"
   - CORRECTO: "Tengo una oferta que le VA a interesar"
   - NO personalizar con info de visitas web (no tienen acceso)

8. **MANEJO DE PRECIO**:
   - INCORRECTO: Textos muy formales/corporativos
   - CORRECTO: "Es lógico que mires el precio. A varios clientes les pasó eso al comienzo, y cuando empezaron a usar la conexión y vieron la diferencia en el servicio, entendieron que el valor estaba ahí."

## VENDEDOR A ANALIZAR: {agente}

## DATOS DEL VENDEDOR:

### 📊 MÉTRICAS DE EVALUACIÓN IA:
{json.dumps(metricas.get('evaluaciones', {}), indent=2, ensure_ascii=False)}

### 📋 MÉTRICAS DE CLASIFICACIÓN:
{json.dumps(metricas.get('clasificacion', {}), indent=2, ensure_ascii=False)}

### ⏱️ MÉTRICAS DE DURACIÓN:
{json.dumps(metricas.get('integral', {}), indent=2, ensure_ascii=False)}

### 💰 MÉTRICAS DE CIERRES:
{json.dumps(metricas.get('cierres', {}), indent=2, ensure_ascii=False)}

### 📞 MÉTRICAS DE CALIDAD - LLAMADAS:
{json.dumps(metricas.get('calidad_llamadas', {}), indent=2, ensure_ascii=False)}
⚠️ INTERPRETACIÓN MÉTRICAS DE LLAMADAS:
- TMO (Tiempo Medio Operativo): Duración promedio de llamadas. Óptimo entre 2-4 minutos.
- Capta Atención (%): Llamadas >1 minuto. MAYOR % es MEJOR (indica engagement del cliente).
- Supera 5 min (%): Llamadas muy largas. Puede indicar dificultad para cerrar o conversaciones productivas.
- Menos 30 seg: Llamadas muy cortas. MENOR cantidad es MEJOR (indica que no cuelgan rápido).
- Corte Cliente vs Corte Agente: Quién finaliza la llamada. Alto corte cliente puede indicar falta de enganche.
- Estados: 🟢 Excelente (>50% capta atención), 🟡 Bueno (40-50%), 🟠 Regular (30-40%), 🔴 Bajo (<30%).

### 💵 MÉTRICAS DE CALIDAD - VENTAS:
{json.dumps(metricas.get('calidad_ventas', {}), indent=2, ensure_ascii=False)}
⚠️ INTERPRETACIÓN MÉTRICAS DE VENTAS:
- Tasa Aprobación: % de ventas que fueron aprobadas vs total. MAYOR es MEJOR.
- Dif vs Promedio: Diferencia con el promedio del equipo. Positivo = mejor que promedio.
- Canceladas: Ventas rechazadas o canceladas. MENOR es MEJOR.

## COMPARATIVA CON EL EQUIPO:
{json.dumps(comparativa, indent=2, ensure_ascii=False)}

## PROMEDIOS GENERALES DEL EQUIPO:
- Puntaje IA promedio del equipo: {metricas_generales.get('puntaje_prom_equipo', 'N/A')}
- Tasa de conversión del equipo: {metricas_generales.get('tasa_conversion_equipo', 'N/A')}%
- Total de agentes: {metricas_generales.get('total_agentes', 'N/A')}
- TMO promedio del equipo: {metricas_generales.get('tmo_promedio_equipo', 'N/A')} seg
- % Capta Atención promedio: {metricas_generales.get('capta_atencion_promedio', 'N/A')}%

---

## TU ANÁLISIS DEBE INCLUIR:

### 1. DIAGNÓSTICO GENERAL Y EVOLUCIÓN (2-3 párrafos)
- ¿Cómo está este vendedor comparado con el equipo?
- ¿Cuál es su nivel actual? (Crítico / Necesita Mejora / Promedio / Bueno / Excelente)
- **EVOLUCIÓN**: Si hay historial, ¿mejoró o empeoró respecto al período anterior?
- ¿Cuál es su potencial de mejora?

### 2. ANÁLISIS DE EVOLUCIÓN SEMANAL (FUNDAMENTAL)
⚠️ ESTA SECCIÓN ES OBLIGATORIA SI HAY DATOS DE AMBOS PERÍODOS:
- **QUÉ MEJORÓ**: Criterios donde el vendedor subió su puntaje. Felicitar y reforzar.
- **QUÉ EMPEORÓ**: Criterios donde bajó el puntaje. Analizar causas y dar prioridad.
- **QUÉ SIGUE PENDIENTE**: Áreas que ya se identificaron antes y no han mejorado.
- **TENDENCIA GENERAL**: ¿Va por buen camino o necesita intervención urgente?

### 3. FORTALEZAS IDENTIFICADAS (mínimo 3)
- Aspectos positivos que debe mantener y potenciar
- Ejemplos concretos de lo que hace bien
- Destacar si alguna fortaleza es NUEVA (mejoró esta semana)

### 4. ÁREAS CRÍTICAS DE MEJORA (mínimo 3)
- Debilidades que impactan directamente en sus resultados
- Indicar si son NUEVAS o PERSISTENTES (ya estaban en el período anterior)
- Por qué cada área es importante mejorar

### 5. ANÁLISIS DE MÉTRICAS DE CALIDAD (FUNDAMENTAL)
Analiza las métricas de llamadas y ventas del agente:
- **TMO (Tiempo Medio)**: ¿Está en el rango óptimo (2-4 min)? Si es muy bajo, no está generando engagement. Si es muy alto, puede tener dificultades para cerrar.
- **% Capta Atención**: Este KPI es CRÍTICO. Mide llamadas >1 min. Si es bajo (<30%), el agente no logra enganchar al cliente.
- **Cortes de llamada**: Si hay más cortes del cliente que del agente, puede indicar problemas en el pitch inicial.
- **Llamadas <30 seg**: Demasiadas llamadas cortas indican problemas en el saludo/enganche inicial.
- **Tasa de aprobación de ventas**: Si es baja, puede haber problemas de calidad en las ventas (datos incorrectos, mal procesamiento).

### 6. ANÁLISIS DETALLADO POR COMPETENCIA
Para cada criterio evaluado, indica:
- Nivel actual (Crítico/Bajo/Regular/Bueno/Excelente)
- Qué está haciendo mal o bien
- Cómo mejorar específicamente (RESPETANDO LAS REGLAS DEL NEGOCIO)

### 7. PLAN DE ACCIÓN SEMANAL (4 semanas)
**Semana 1:** [Foco principal y acciones específicas]
**Semana 2:** [Siguiente prioridad]
**Semana 3:** [Consolidación]
**Semana 4:** [Optimización]

### 7. TÉCNICAS Y SCRIPTS RECOMENDADOS
⚠️ IMPORTANTE: Todas las frases y scripts deben respetar las REGLAS DEL NEGOCIO listadas arriba.
- Frases específicas para verificar identidad del cliente
- Preguntas correctas para detectar necesidades ("¿Qué es lo que más usás del celular?")
- Cómo ofrecer fibra de forma directa (sin preguntar si le interesa)
- Técnicas de cierre DIRECTO (asignar sucursal, buscar domicilio)
- Manejo de objeciones personalizado según tipo de cliente

### 9. METAS CUANTIFICABLES
- Meta de puntaje IA a alcanzar en 30 días
- Meta de tasa de conversión
- Meta de ofrecimiento de productos
- Meta de % Capta Atención (llamadas >1 min)
- Meta de TMO a alcanzar
- KPIs específicos a mejorar

### 10. MENSAJE MOTIVACIONAL PERSONALIZADO
Un mensaje directo y motivador para este vendedor, reconociendo su esfuerzo
y visualizando su potencial de crecimiento.
Si MEJORÓ respecto al período anterior, felicitarlo específicamente.
Si EMPEORÓ, motivarlo a retomar el buen camino.

---

IMPORTANTE: 
- Sé específico y práctico, no genérico
- Usa los datos proporcionados para personalizar cada recomendación
- El tono debe ser de mentor que cree en el potencial del vendedor
- Las acciones deben ser ejecutables y medibles
- INCLUYE SIEMPRE el análisis de métricas de calidad (llamadas y ventas) si están disponibles
- ⚠️ SI HAY HISTORIAL: El análisis DEBE mencionar la evolución del vendedor
- ⚠️ ENFOCATE EN LA ÚLTIMA SEMANA (19-24 Enero) pero considerando el historial
- NO incluyas frases introductorias como "¡Aquí tienes!", "¡Absolutamente!", "¡Claro!" o similares
- Empieza DIRECTAMENTE con el título "## ANÁLISIS DEL VENDEDOR: {agente}"
- NO repitas el nombre del vendedor en frases introductorias innecesarias
"""
    
    return prompt


def generar_coaching_agente(agente, datos, model, metricas_generales):
    """Genera el análisis de coaching para un agente, incluyendo historial"""
    
    # Cargar coaching previo si existe
    coaching_previo = cargar_coaching_previo(agente)
    if coaching_previo:
        log(f"Encontrado coaching previo del {coaching_previo.get('fecha_generacion', 'fecha desconocida')[:10]}")
    
    # Obtener métricas del agente
    metricas = obtener_metricas_agente(agente, datos)
    comparativa = calcular_comparativa_general(agente, datos)
    
    # Verificar que hay suficientes datos (mínimo 10 evaluaciones)
    if metricas['evaluaciones'].get('total_evaluadas', 0) < 10:
        return None, "Insuficientes evaluaciones (mínimo 10)"
    
    # Generar prompt con historial
    prompt = generar_prompt_coaching(agente, metricas, comparativa, metricas_generales, coaching_previo)
    
    try:
        log("Enviando a Gemini...")
        response = model.generate_content(prompt)
        analisis = response.text
        
        # Estructurar resultado (convertir tipos numpy)
        resultado = convertir_tipos_nativos({
            'agente': agente,
            'fecha_generacion': datetime.now().isoformat(),
            'metricas': metricas,
            'comparativa': comparativa,
            'analisis_coaching': analisis,
            'modelo_usado': MODEL_NAME,
            'tiene_historial': coaching_previo is not None,
            'fecha_coaching_anterior': coaching_previo.get('fecha_generacion', None) if coaching_previo else None,
            'evolucion': metricas.get('evolucion', None)
        })
        
        return resultado, None
        
    except Exception as e:
        return None, str(e)


def main():
    print("\n" + "="*70)
    print("  🎯 GENERADOR DE COACHING PERSONALIZADO CON IA")
    print("  📊 Análisis con historial y evolución semanal")
    print("="*70 + "\n")
    
    # Cargar datos
    log("Cargando todos los datos disponibles...")
    datos = cargar_datos_completos()
    
    if 'evaluaciones' not in datos:
        log("No se encontraron evaluaciones de IA. Ejecuta primero 4_evaluacion_gemini.py", "error")
        return
    
    # Inicializar modelo
    log(f"Inicializando modelo {MODEL_NAME}...")
    model = genai.GenerativeModel(MODEL_NAME)
    
    # Obtener lista de agentes con suficientes datos (mínimo 10 evaluaciones)
    df_eval = datos['evaluaciones']
    agentes_counts = df_eval['agente'].value_counts()
    agentes_validos = agentes_counts[agentes_counts >= 10].index.tolist()
    
    log(f"Agentes con suficientes datos (>=10 evaluaciones): {len(agentes_validos)}")
    
    # Calcular métricas generales
    metricas_generales = {
        'puntaje_prom_equipo': round(df_eval['puntaje_total'].mean(), 1),
        'tasa_conversion_equipo': round(datos['clasificacion']['es_venta'].mean() * 100, 1) if 'clasificacion' in datos and 'es_venta' in datos['clasificacion'].columns else 'N/A',
        'total_agentes': len(agentes_validos)
    }
    
    # Agregar métricas de calidad generales
    if 'calidad' in datos and 'llamadas' in datos['calidad']:
        totales = datos['calidad']['llamadas'].get('totales', {})
        if isinstance(totales, dict):
            metricas_generales['tmo_promedio_equipo'] = totales.get('tmo_global_seg', 'N/A')
            metricas_generales['capta_atencion_promedio'] = totales.get('pct_capta_atencion', 'N/A')
        else:
            # Buscar totales en la lista
            for item in datos['calidad']['llamadas']:
                if isinstance(item, dict) and item.get('agente') == 'totales':
                    metricas_generales['tmo_promedio_equipo'] = item.get('tmo_global_seg', 'N/A')
                    metricas_generales['capta_atencion_promedio'] = item.get('pct_capta_atencion', 'N/A')
                    break
    
    # Cargar coaching existente
    archivo_coaching = os.path.join(DIR_COACHING, "coaching_completo.json")
    if os.path.exists(archivo_coaching):
        with open(archivo_coaching, 'r', encoding='utf-8') as f:
            coaching_existente = json.load(f)
        agentes_procesados = [c['agente'] for c in coaching_existente]
        log(f"Coaching existente: {len(agentes_procesados)} agentes")
    else:
        coaching_existente = []
        agentes_procesados = []
    
    # Parsear argumentos
    forzar_actualizar = '--actualizar' in sys.argv or '-u' in sys.argv
    
    # Filtrar agentes pendientes
    args_numericos = [arg for arg in sys.argv[1:] if arg.isdigit()]
    if args_numericos:
        max_agentes = int(args_numericos[0])
        log(f"Procesando máximo {max_agentes} agentes")
    else:
        max_agentes = len(agentes_validos)
    
    if forzar_actualizar:
        log("⚠️ MODO ACTUALIZACIÓN: Reprocesando agentes con historial")
        # En modo actualizar, procesar todos pero guardando el historial
        agentes_pendientes = agentes_validos[:max_agentes]
    else:
        agentes_pendientes = [a for a in agentes_validos if a not in agentes_procesados][:max_agentes]
    
    if not agentes_pendientes:
        log("Todos los agentes ya tienen coaching generado", "success")
        log("Usa --actualizar o -u para reprocesar con el historial")
        return
    
    log(f"Pendientes a procesar: {len(agentes_pendientes)}")
    print("-" * 70)
    
    # Procesar cada agente
    if forzar_actualizar:
        # En modo actualizar, empezar con lista vacía para regenerar todo
        resultados = []
    else:
        resultados = coaching_existente.copy()
    errores = 0
    
    for i, agente in enumerate(agentes_pendientes, 1):
        print(f"\n[{i}/{len(agentes_pendientes)}] Generando coaching para: {agente}")
        log("Recopilando datos del agente...")
        
        resultado, error = generar_coaching_agente(agente, datos, model, metricas_generales)
        
        if error:
            log(f"Error: {error}", "error")
            errores += 1
            continue
        
        resultados.append(resultado)
        log(f"Coaching generado exitosamente", "success")
        
        # Guardar individual
        archivo_individual = os.path.join(DIR_COACHING, f"coaching_{agente.replace(' ', '_')}.json")
        with open(archivo_individual, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        
        # Guardar consolidado
        with open(archivo_coaching, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)
        
        # Rate limiting (3 segundos para modelo más potente)
        if i < len(agentes_pendientes):
            log("Esperando 3 segundos (rate limiting)...")
            time.sleep(3)
    
    # Generar CSV resumen
    log("\nGenerando resumen CSV...")
    
    resumen_data = []
    for r in resultados:
        metricas = r.get('metricas', {})
        eval_data = metricas.get('evaluaciones', {})
        clasif_data = metricas.get('clasificacion', {})
        
        resumen_data.append({
            'agente': r['agente'],
            'fecha_coaching': r['fecha_generacion'],
            'puntaje_ia': eval_data.get('puntaje_promedio', 0),
            'llamadas_evaluadas': eval_data.get('total_evaluadas', 0),
            'llamadas_excelentes': eval_data.get('llamadas_excelentes', 0),
            'llamadas_criticas': eval_data.get('llamadas_criticas', 0),
            'tasa_conversion': clasif_data.get('tasa_conversion', 0),
            'pct_saludo': clasif_data.get('pct_saludo', 0),
            'pct_cierre': clasif_data.get('pct_cierre', 0),
            'tiene_coaching': True
        })
    
    df_resumen = pd.DataFrame(resumen_data)
    df_resumen.to_csv(os.path.join(DIR_COACHING, "resumen_coaching.csv"), index=False)
    
    # Resumen final
    print("\n" + "="*70)
    log("PROCESO FINALIZADO", "success")
    log(f"Coaching generado: {len(resultados)} agentes")
    log(f"Errores: {errores}")
    log(f"Archivos en: {DIR_COACHING}")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

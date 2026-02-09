"""
Script Unificado: Resumen + Plan de Acción por Vendedor y por Equipo
====================================================================
Genera análisis exhaustivos y planes de acción personalizados usando Gemini.
Procesa TODOS los vendedores y TODOS los equipos.
NO borra datos existentes - solo agrega o actualiza.

Uso:
    python generar_resumen_vendedores_equipos.py                 # Procesa pendientes
    python generar_resumen_vendedores_equipos.py --actualizar    # Reprocesa todos
    python generar_resumen_vendedores_equipos.py --solo-equipos  # Solo equipos
    python generar_resumen_vendedores_equipos.py --solo-vendedores # Solo vendedores
    python generar_resumen_vendedores_equipos.py --min 5         # Mínimo 5 evaluaciones
"""

import os
import json
import sys
import re
import time
import warnings
from datetime import datetime, date
from collections import Counter

warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import google.generativeai as genai
from config import api_key

# ============================================================
# CONFIGURACIÓN
# ============================================================
genai.configure(api_key=api_key)
MODEL_NAME = "gemini-2.0-flash"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DIR_REPORTES = os.path.join(BASE_DIR, "reportes")
DIR_COACHING_VENDEDORES = os.path.join(DIR_REPORTES, "coaching_vendedores")
DIR_COACHING_EQUIPOS = os.path.join(DIR_REPORTES, "coaching_equipos")
os.makedirs(DIR_COACHING_VENDEDORES, exist_ok=True)
os.makedirs(DIR_COACHING_EQUIPOS, exist_ok=True)

MIN_EVALUACIONES_DEFAULT = 5  # Mínimo de evaluaciones por vendedor
RATE_LIMIT_SEG = 3  # Segundos entre llamadas a Gemini


# ============================================================
# UTILIDADES
# ============================================================
def log(mensaje, tipo="info"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    emoji = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}.get(tipo, "")
    try:
        print(f"[{timestamp}] {emoji} {mensaje}")
    except UnicodeEncodeError:
        print(f"[{timestamp}] [{tipo.upper()}] {mensaje}")


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
    elif isinstance(obj, (pd.Timestamp,)):
        return str(obj)
    elif isinstance(obj, (date, datetime)):
        return str(obj)
    elif pd.isna(obj) if not isinstance(obj, (list, dict, str, int, float, bool)) else False:
        return None
    else:
        return obj


def normalizar_codigo_agente(agente):
    """Normaliza codigo de agente (MZA 1 -> mza1, amza46 -> mza46)"""
    if pd.isna(agente) or agente is None:
        return ''
    codigo = str(agente).lower().replace(' ', '').replace('_', '').replace('\t', '')
    if codigo.startswith('amza'):
        codigo = codigo[1:]
    return codigo


def obtener_nombre_agente(agente, codigo_a_nombre):
    """Devuelve el nombre mapeado cuando exista; si no, conserva el valor original."""
    if not agente:
        return agente
    codigo_norm = normalizar_codigo_agente(agente)
    return codigo_a_nombre.get(codigo_norm, agente)


def extraer_fecha_de_archivo(nombre_archivo):
    """Extrae la fecha del nombre del archivo."""
    match = re.search(r'(\d{2})(\d{2})(\d{2})', str(nombre_archivo))
    if match:
        dia = int(match.group(1))
        mes = int(match.group(2))
        anio_corto = int(match.group(3))
        anio = 2020 + anio_corto
        try:
            return date(anio, mes, dia)
        except:
            return None
    return None


# ============================================================
# CARGA DE DATOS
# ============================================================
def cargar_listado_vendedores():
    """Carga el listado de vendedores con sus equipos."""
    listado = {}  # usuario -> nombre
    equipos = {}  # equipo -> [nombres]
    codigo_a_equipo = {}  # codigo_norm -> equipo
    codigo_a_nombre = {}  # codigo_norm -> nombre

    try:
        ruta = os.path.join(BASE_DIR, 'LISTADO-DE-VENDEDORES.csv')
        df = pd.read_csv(ruta, header=None, skiprows=1)
        for _, row in df.iterrows():
            usuario = str(row.iloc[0]).strip().lower().replace('\t', '').replace(' ', '') if pd.notna(row.iloc[0]) else ""
            nombre = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
            equipo = str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else "Sin Equipo"

            if usuario and usuario != 'usuario' and nombre:
                listado[usuario] = nombre.title()
                usuario_norm = normalizar_codigo_agente(usuario)
                if usuario_norm:
                    codigo_a_nombre[usuario_norm] = nombre.title()
                    if equipo and equipo not in ['Sin Equipo', '', 'nan']:
                        codigo_a_equipo[usuario_norm] = equipo
                        if equipo not in equipos:
                            equipos[equipo] = []
                        equipos[equipo].append(nombre.title())

        log(f"Cargados {len(listado)} vendedores en {len(equipos)} equipos")
    except Exception as e:
        log(f"Error cargando listado: {e}", "error")

    return listado, equipos, codigo_a_equipo, codigo_a_nombre


def cargar_datos_completos():
    """Carga todos los datos disponibles."""
    datos = {}

    # Evaluaciones Gemini
    ruta = os.path.join(DIR_REPORTES, "evaluaciones_gemini.csv")
    if os.path.exists(ruta):
        datos['evaluaciones'] = pd.read_csv(ruta)
        log(f"Evaluaciones: {len(datos['evaluaciones'])} registros")

    # Análisis integral
    ruta = os.path.join(DIR_REPORTES, "analisis_integral", "analisis_integral.csv")
    if os.path.exists(ruta):
        datos['integral'] = pd.read_csv(ruta)
        log(f"Integral: {len(datos['integral'])} registros")

    # Planes
    ruta = os.path.join(DIR_REPORTES, "planes", "analisis_planes_detallado.csv")
    if os.path.exists(ruta):
        datos['planes'] = pd.read_csv(ruta)
        log(f"Planes: {len(datos['planes'])} registros")

    # Quejas
    ruta = os.path.join(DIR_REPORTES, "quejas", "quejas_no_resueltas.csv")
    if os.path.exists(ruta):
        datos['quejas'] = pd.read_csv(ruta)
        log(f"Quejas: {len(datos['quejas'])} registros")

    # Cierres comerciales
    ruta = os.path.join(DIR_REPORTES, "cierres_comerciales", "cierres_comerciales.csv")
    if os.path.exists(ruta):
        datos['cierres'] = pd.read_csv(ruta, sep=';')
        log(f"Cierres: {len(datos['cierres'])} registros")

    # Clasificación completa
    ruta = os.path.join(DIR_REPORTES, "clasificacion_completa", "clasificacion_completa.csv")
    if os.path.exists(ruta):
        datos['clasificacion'] = pd.read_csv(ruta)
        log(f"Clasificacion: {len(datos['clasificacion'])} registros")

    # Datos de calidad
    ruta = os.path.join(BASE_DIR, "datos_calidad", "datos_calidad_procesados.json")
    if os.path.exists(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            datos['calidad'] = json.load(f)
        log(f"Calidad: datos cargados")

    # Coaching individual previo
    ruta = os.path.join(DIR_COACHING_VENDEDORES, "coaching_completo.json")
    if os.path.exists(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            datos['coaching_individual'] = json.load(f)
        log(f"Coaching previo: {len(datos['coaching_individual'])} vendedores")

    return datos


# ============================================================
# MÉTRICAS POR VENDEDOR
# ============================================================
def obtener_metricas_vendedor(agente, datos, codigo_a_equipo, codigo_a_nombre):
    """Recopila todas las metricas de un vendedor."""
    nombre_agente = obtener_nombre_agente(agente, codigo_a_nombre)
    metricas = {
        'agente': nombre_agente,
        'agente_codigo': agente,
        'equipo': codigo_a_equipo.get(normalizar_codigo_agente(agente), 'Sin Equipo'),
        'evaluaciones': {},
        'clasificacion': {},
        'integral': {},
        'cierres': {},
        'planes': {},
        'calidad_llamadas': {},
        'calidad_ventas': {}
    }

    # === EVALUACIONES DEL MODELO ===
    if 'evaluaciones' in datos:
        df_ag = datos['evaluaciones'][datos['evaluaciones']['agente'] == agente].copy()
        if len(df_ag) > 0:
            criterios = ['saludo_presentacion', 'identificacion_cliente', 'deteccion_necesidades',
                         'oferta_productos', 'manejo_objeciones', 'cierre', 'despedida',
                         'proactividad', 'empatia', 'resolucion_problemas']

            metricas['evaluaciones'] = {
                'total_evaluadas': len(df_ag),
                'puntaje_promedio': round(df_ag['puntaje_total'].mean(), 1),
                'puntaje_min': int(df_ag['puntaje_total'].min()),
                'puntaje_max': int(df_ag['puntaje_total'].max()),
                'desviacion_std': round(df_ag['puntaje_total'].std(), 1) if len(df_ag) > 1 else 0,
                'llamadas_excelentes': int(len(df_ag[df_ag['puntaje_total'] >= 80])),
                'llamadas_buenas': int(len(df_ag[(df_ag['puntaje_total'] >= 60) & (df_ag['puntaje_total'] < 80)])),
                'llamadas_regulares': int(len(df_ag[(df_ag['puntaje_total'] >= 40) & (df_ag['puntaje_total'] < 60)])),
                'llamadas_criticas': int(len(df_ag[df_ag['puntaje_total'] < 40])),
                'criterios': {}
            }

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
                metricas['evaluaciones']['fortalezas_frecuentes'] = dict(Counter(fortalezas).most_common(5))

            # Ejemplos mejores y peores
            mejores = df_ag.nlargest(3, 'puntaje_total')[['puntaje_total', 'resumen']].to_dict('records')
            peores = df_ag.nsmallest(3, 'puntaje_total')[['puntaje_total', 'resumen']].to_dict('records')
            metricas['evaluaciones']['ejemplos_mejores'] = mejores
            metricas['evaluaciones']['ejemplos_peores'] = peores

            # Ofrecimiento de fibra
            if 'se_ofrecio_fibra' in df_ag.columns:
                total_fibra = df_ag['se_ofrecio_fibra'].sum() if df_ag['se_ofrecio_fibra'].dtype == bool else len(df_ag[df_ag['se_ofrecio_fibra'] == True])
                metricas['evaluaciones']['pct_ofrece_fibra'] = round(total_fibra / len(df_ag) * 100, 1)

    # === CLASIFICACIÓN ===
    if 'clasificacion' in datos:
        df_ag = datos['clasificacion'][datos['clasificacion']['agente'] == agente]
        if len(df_ag) > 0:
            total = len(df_ag)
            metricas['clasificacion'] = {
                'total_llamadas': total,
                'ventas': int(len(df_ag[df_ag.get('es_venta', False) == True])) if 'es_venta' in df_ag.columns else 0,
                'tasa_conversion': round(len(df_ag[df_ag['es_venta'] == True]) / total * 100, 1) if 'es_venta' in df_ag.columns and total > 0 else 0,
            }

    # === INTEGRAL (duración) ===
    if 'integral' in datos:
        df_ag = datos['integral'][datos['integral']['agente'] == agente]
        if len(df_ag) > 0:
            metricas['integral'] = {
                'duracion_promedio_min': round(df_ag['duracion_seg'].mean() / 60, 1) if 'duracion_seg' in df_ag.columns else 0,
            }

    # === CIERRES ===
    if 'cierres' in datos:
        df_ag = datos['cierres'][datos['cierres']['agente'] == agente]
        if len(df_ag) > 0:
            metricas['cierres'] = {
                'total_ventas': len(df_ag),
                'porcentaje_cierre_prom': round(df_ag['porcentaje'].mean(), 1) if 'porcentaje' in df_ag.columns else 0,
            }

    # === PLANES ===
    if 'planes' in datos:
        df_ag = datos['planes'][datos['planes']['agente'] == agente]
        if len(df_ag) > 0:
            total = len(df_ag)
            metricas['planes'] = {
                'total_llamadas': total,
                'con_plan': int(len(df_ag[df_ag['cantidad_planes'] > 0])) if 'cantidad_planes' in df_ag.columns else 0,
                'ofrece_fibra': int(len(df_ag[df_ag['ofrece_fibra'] == True])) if 'ofrece_fibra' in df_ag.columns else 0,
            }
            if total > 0:
                metricas['planes']['pct_plan'] = round(metricas['planes']['con_plan'] / total * 100, 1)
                metricas['planes']['pct_fibra'] = round(metricas['planes']['ofrece_fibra'] / total * 100, 1)

    # === CALIDAD - LLAMADAS ===
    if 'calidad' in datos and 'llamadas' in datos['calidad']:
        llamadas = datos['calidad']['llamadas']
        por_vendedor = llamadas.get('por_vendedor', llamadas if isinstance(llamadas, list) else [])
        agente_lower = agente.lower().replace(' ', '')
        for item in por_vendedor:
            if isinstance(item, dict):
                ag_cal = str(item.get('agente', '')).lower().replace(' ', '')
                if agente_lower == ag_cal or normalizar_codigo_agente(agente) == normalizar_codigo_agente(ag_cal):
                    metricas['calidad_llamadas'] = {
                        'total_llamadas': item.get('total_llamadas', 0),
                        'tmo_seg': item.get('tmo_seg', item.get('tmo_global_seg', 0)),
                        'pct_capta_atencion': item.get('pct_capta_atencion', 0),
                        'menos_30seg': item.get('menos_30seg', 0),
                        'corte_cliente': item.get('corte_cliente', 0),
                        'corte_agente': item.get('corte_agente', 0),
                    }
                    break

    # === CALIDAD - VENTAS ===
    if 'calidad' in datos and 'ventas' in datos['calidad']:
        ventas = datos['calidad']['ventas']
        por_vendedor = ventas.get('por_vendedor', [])
        agente_lower = agente.lower().replace(' ', '')
        for item in por_vendedor:
            if isinstance(item, dict):
                v_cal = str(item.get('vendedor', '')).lower().replace(' ', '')
                if agente_lower in v_cal or v_cal in agente_lower:
                    metricas['calidad_ventas'] = {
                        'total_ventas': item.get('total_ventas', item.get('cantidad_ventas', 0)),
                        'aprobadas': item.get('aprobadas', 0),
                        'canceladas': item.get('canceladas', 0),
                        'tasa_aprobacion': item.get('tasa_aprobacion', 0),
                    }
                    break

    return metricas


def calcular_comparativa_vendedor(agente, datos):
    """Compara un vendedor con el promedio general."""
    comp = {}
    if 'evaluaciones' in datos:
        df = datos['evaluaciones']
        df_ag = df[df['agente'] == agente]
        if len(df_ag) > 0:
            prom_gen = df['puntaje_total'].mean()
            prom_ag = df_ag['puntaje_total'].mean()
            comp['puntaje_modelo'] = {
                'agente': round(prom_ag, 1),
                'general': round(prom_gen, 1),
                'diferencia': round(prom_ag - prom_gen, 1),
                'percentil': round((df['puntaje_total'] < prom_ag).mean() * 100, 1)
            }
            criterios = ['saludo_presentacion', 'identificacion_cliente', 'deteccion_necesidades',
                         'oferta_productos', 'manejo_objeciones', 'cierre', 'despedida',
                         'proactividad', 'empatia', 'resolucion_problemas']
            comp['criterios'] = {}
            for c in criterios:
                if c in df.columns:
                    comp['criterios'][c] = {
                        'agente': round(df_ag[c].mean(), 1),
                        'general': round(df[c].mean(), 1),
                        'diferencia': round(df_ag[c].mean() - df[c].mean(), 1)
                    }
    return comp


# ============================================================
# PROMPT DE COACHING - VENDEDOR
# ============================================================
def generar_prompt_vendedor(nombre_agente, metricas, comparativa, metricas_generales, coaching_previo=None):
    metricas = convertir_tipos_nativos(metricas)
    comparativa = convertir_tipos_nativos(comparativa)
    metricas_generales = convertir_tipos_nativos(metricas_generales)

    seccion_historial = ""
    if coaching_previo:
        coaching_previo = convertir_tipos_nativos(coaching_previo)
        metricas_prev = coaching_previo.get('metricas', {}).get('evaluaciones', {})
        fecha_prev = str(coaching_previo.get('fecha_generacion', ''))[:10]
        seccion_historial = f"""
## HISTORIAL DEL VENDEDOR (Coaching anterior del {fecha_prev}):
- Puntaje promedio anterior: {metricas_prev.get('puntaje_promedio', 'N/A')}
- Llamadas evaluadas anteriores: {metricas_prev.get('total_evaluadas', 'N/A')}
- Areas de mejora anteriores: {json.dumps(metricas_prev.get('areas_mejora_frecuentes', {}), ensure_ascii=False)}
- Fortalezas anteriores: {json.dumps(metricas_prev.get('fortalezas_frecuentes', {}), ensure_ascii=False)}

IMPORTANTE: Compara el desempeño actual con este historial para identificar EVOLUCION.
"""

    prompt = f"""
Eres un JEFE DE VENTAS experimentado y mentor de alto rendimiento en telecomunicaciones (Movistar Argentina).
Tu misión es analizar exhaustivamente el desempeño del vendedor y crear un plan de acción
personalizado para ayudarlo a alcanzar su MÁXIMO POTENCIAL.

## REGLAS CRITICAS DEL NEGOCIO:

### FRASES PROHIBIDAS - NUNCA SUGERIR:
- "¿Te parece bien si...?" -> NO se pregunta, se procede directamente
- "¿Le gustaría que...?" -> Frase prohibida de cierre
- "¿Te interesaría conocer...?" -> NO se pregunta, se comenta directamente
- "Podría interesarle" -> Debe decir "LE VA a interesar"
- "Período de prueba gratuito" -> NO EXISTE
- "Estaré encantado de ayudarte en el futuro" -> Solo acompañamiento durante portabilidad

### ACCIONES CORRECTAS:
1. IDENTIFICACION: "Hola, ¿me comunico con [Nombre]?" para verificar persona correcta
2. DETECCION NECESIDADES: "¿Qué es lo que más usás del celular?" / "¿Cuántos GB tenés?"
3. CIERRE: Asignar sucursal o buscar domicilio directamente
4. OFERTA FIBRA: Comentar DIRECTAMENTE sin preguntar si le interesa
5. OBJECIONES: Rebatir la objeción PUNTUAL de CADA cliente, no respuestas genéricas
6. SALUDO: "Tengo una oferta que le VA a interesar" (no "podría interesarle")
7. PRECIO: "Es lógico que mires el precio. A varios clientes les pasó eso..."

{seccion_historial}

## VENDEDOR: {nombre_agente}
## EQUIPO: {metricas.get('equipo', 'Sin Equipo')}

### METRICAS DE EVALUACION DEL MODELO:
{json.dumps(metricas.get('evaluaciones', {}), indent=2, ensure_ascii=False)}

### METRICAS DE CLASIFICACION:
{json.dumps(metricas.get('clasificacion', {}), indent=2, ensure_ascii=False)}

### DURACION DE LLAMADAS:
{json.dumps(metricas.get('integral', {}), indent=2, ensure_ascii=False)}

### CIERRES COMERCIALES:
{json.dumps(metricas.get('cierres', {}), indent=2, ensure_ascii=False)}

### PLANES OFRECIDOS:
{json.dumps(metricas.get('planes', {}), indent=2, ensure_ascii=False)}

### CALIDAD - LLAMADAS:
{json.dumps(metricas.get('calidad_llamadas', {}), indent=2, ensure_ascii=False)}
(TMO optimo: 2-4 min. Capta Atencion >1min: mayor es mejor. <30seg: menos es mejor.)

### CALIDAD - VENTAS:
{json.dumps(metricas.get('calidad_ventas', {}), indent=2, ensure_ascii=False)}

### COMPARATIVA CON EL EQUIPO:
{json.dumps(comparativa, indent=2, ensure_ascii=False)}

### PROMEDIOS GENERALES:
- Puntaje promedio del modelo: {metricas_generales.get('puntaje_prom_general', 'N/A')}
- Total agentes: {metricas_generales.get('total_agentes', 'N/A')}

---

## GENERA TU ANALISIS CON ESTA ESTRUCTURA:

### 1. DIAGNOSTICO GENERAL (2-3 parrafos)
- Nivel actual: Critico / Necesita Mejora / Promedio / Bueno / Excelente
- Como se compara con el equipo
- Potencial de mejora
- Si hay historial: evolución vs periodo anterior

### 2. FORTALEZAS (minimo 3)
- Aspectos positivos a mantener y potenciar

### 3. AREAS CRITICAS DE MEJORA (minimo 3)
- Debilidades con impacto en resultados

### 4. ANALISIS POR COMPETENCIA
Para cada criterio: nivel actual, que hace mal/bien, como mejorar (respetando reglas del negocio)

### 5. PLAN DE ACCION SEMANAL (4 semanas)
**Semana 1:** [Foco principal y acciones]
**Semana 2:** [Siguiente prioridad]
**Semana 3:** [Consolidación]
**Semana 4:** [Optimización]

### 6. TECNICAS Y SPEACH RECOMENDADOS
- Frases para verificar identidad
- Preguntas para detectar necesidades
- Como ofrecer fibra directamente
- Técnicas de cierre directo
- Manejo de objeciones personalizado

### 7. METAS CUANTIFICABLES
- Meta de puntaje del modelo a 30 dias
- Meta de calidad de llamadas
- KPIs (indicadores clave de desempeño) específicos a mejorar

### 8. MENSAJE MOTIVACIONAL PERSONALIZADO

---
IMPORTANTE:
- Se especifico y practico, NO genérico
- Usa los datos para personalizar cada recomendacion
- Las acciones deben ser ejecutables y medibles
- Cuando menciones puntajes, aclara siempre "de 100" (ejemplo: "Despedida: 68.6 de 100")
- No incluyas la linea "Recursos Necesarios: N/A"
- NO incluyas frases introductorias como "Aqui tienes!", "Absolutamente!"
- Empieza DIRECTAMENTE con "## ANALISIS DEL VENDEDOR: {nombre_agente}"
"""
    return prompt


# ============================================================
# MÉTRICAS POR EQUIPO
# ============================================================
def obtener_metricas_equipo(equipo, vendedores, datos, codigo_a_equipo):
    """Recopila métricas de un equipo completo."""
    metricas = {
        'equipo': equipo,
        'vendedores': vendedores,
        'total_vendedores': len(vendedores),
        'evaluaciones': {},
        'clasificacion': {},
        'planes': {},
        'quejas': {},
        'calidad': {}
    }

    # === EVALUACIONES DEL MODELO ===
    if 'evaluaciones' in datos:
        df = datos['evaluaciones'].copy()
        df['agente_norm'] = df['agente'].apply(normalizar_codigo_agente)
        df['equipo_calc'] = df['agente_norm'].map(codigo_a_equipo)
        df_eq = df[df['equipo_calc'] == equipo]

        if len(df_eq) > 0:
            criterios = ['saludo_presentacion', 'identificacion_cliente', 'deteccion_necesidades',
                         'oferta_productos', 'manejo_objeciones', 'cierre', 'despedida',
                         'proactividad', 'empatia', 'resolucion_problemas']

            metricas['evaluaciones'] = {
                'total_evaluadas': len(df_eq),
                'puntaje_promedio': round(df_eq['puntaje_total'].mean(), 1),
                'puntaje_min': int(df_eq['puntaje_total'].min()),
                'puntaje_max': int(df_eq['puntaje_total'].max()),
                'llamadas_excelentes': int(len(df_eq[df_eq['puntaje_total'] >= 80])),
                'llamadas_buenas': int(len(df_eq[(df_eq['puntaje_total'] >= 60) & (df_eq['puntaje_total'] < 80)])),
                'llamadas_regulares': int(len(df_eq[(df_eq['puntaje_total'] >= 40) & (df_eq['puntaje_total'] < 60)])),
                'llamadas_criticas': int(len(df_eq[df_eq['puntaje_total'] < 40])),
                'criterios': {}
            }

            for c in criterios:
                if c in df_eq.columns:
                    metricas['evaluaciones']['criterios'][c] = round(df_eq[c].mean(), 1)

            # Areas de mejora frecuentes del equipo
            areas_mejora = []
            for areas in df_eq['areas_mejora'].dropna():
                if isinstance(areas, str):
                    for area in areas.split(','):
                        area = area.strip().strip('"').strip("'").strip('[').strip(']')
                        if area:
                            areas_mejora.append(area)
            if areas_mejora:
                metricas['evaluaciones']['areas_mejora'] = dict(Counter(areas_mejora).most_common(10))

            # Fortalezas del equipo
            fortalezas = []
            for fort in df_eq['fortalezas'].dropna():
                if isinstance(fort, str):
                    for f in fort.split(','):
                        f = f.strip().strip('"').strip("'").strip('[').strip(']')
                        if f:
                            fortalezas.append(f)
            if fortalezas:
                metricas['evaluaciones']['fortalezas'] = dict(Counter(fortalezas).most_common(10))

            # Rendimiento por vendedor dentro del equipo
            rendimiento = []
            for ag in df_eq['agente'].unique():
                df_v = df_eq[df_eq['agente'] == ag]
                rendimiento.append({
                    'vendedor': ag,
                    'puntaje_promedio': round(df_v['puntaje_total'].mean(), 1),
                    'evaluaciones': len(df_v),
                    'excelentes': int(len(df_v[df_v['puntaje_total'] >= 80])),
                    'criticas': int(len(df_v[df_v['puntaje_total'] < 40]))
                })
            metricas['evaluaciones']['rendimiento_vendedores'] = sorted(
                rendimiento, key=lambda x: x['puntaje_promedio'], reverse=True
            )

    # === PLANES ===
    if 'planes' in datos:
        df = datos['planes'].copy()
        df['agente_norm'] = df['agente'].apply(normalizar_codigo_agente)
        df['equipo_calc'] = df['agente_norm'].map(codigo_a_equipo)
        df_eq = df[df['equipo_calc'] == equipo]
        if len(df_eq) > 0:
            total = len(df_eq)
            metricas['planes'] = {
                'total_llamadas': total,
                'con_plan': int(len(df_eq[df_eq['cantidad_planes'] > 0])) if 'cantidad_planes' in df_eq.columns else 0,
                'ofrece_fibra': int(len(df_eq[df_eq['ofrece_fibra'] == True])) if 'ofrece_fibra' in df_eq.columns else 0,
            }
            if total > 0:
                metricas['planes']['pct_plan'] = round(metricas['planes']['con_plan'] / total * 100, 1)
                metricas['planes']['pct_fibra'] = round(metricas['planes']['ofrece_fibra'] / total * 100, 1)

    # === QUEJAS ===
    if 'quejas' in datos:
        df = datos['quejas'].copy()
        df['agente_norm'] = df['agente'].apply(normalizar_codigo_agente)
        df['equipo_calc'] = df['agente_norm'].map(codigo_a_equipo)
        df_eq = df[df['equipo_calc'] == equipo]
        if len(df_eq) > 0:
            total = len(df_eq)
            no_resueltas = int(df_eq['quejas_no_resueltas'].sum()) if 'quejas_no_resueltas' in df_eq.columns else 0
            metricas['quejas'] = {
                'total_quejas': total,
                'no_resueltas': no_resueltas,
                'resueltas': total - no_resueltas,
                'pct_resolucion': round((total - no_resueltas) / total * 100, 1) if total > 0 else 0
            }

    # === CALIDAD ===
    if 'calidad' in datos:
        calidad = datos['calidad']
        # Llamadas
        if 'llamadas' in calidad:
            por_vendedor = calidad['llamadas'].get('por_vendedor', calidad['llamadas'] if isinstance(calidad['llamadas'], list) else [])
            llamadas_eq = [v for v in por_vendedor if isinstance(v, dict) and v.get('equipo', '') == equipo]
            if llamadas_eq:
                metricas['calidad']['llamadas'] = {
                    'vendedores_con_datos': len(llamadas_eq),
                    'total_llamadas': sum(v.get('total_llamadas', 0) for v in llamadas_eq),
                    'tmo_promedio': round(sum(v.get('tmo_seg', v.get('tmo_global_seg', 0)) for v in llamadas_eq) / len(llamadas_eq)),
                    'pct_capta_atencion_prom': round(sum(v.get('pct_capta_atencion', 0) for v in llamadas_eq) / len(llamadas_eq), 1),
                }
        # Ventas
        if 'ventas' in calidad and 'por_vendedor' in calidad['ventas']:
            ventas_eq = [v for v in calidad['ventas']['por_vendedor'] if isinstance(v, dict) and v.get('equipo', '') == equipo]
            if ventas_eq:
                metricas['calidad']['ventas'] = {
                    'vendedores_con_datos': len(ventas_eq),
                    'total_ventas': sum(v.get('total_ventas', v.get('cantidad_ventas', 0)) for v in ventas_eq),
                }

    return metricas


def calcular_comparativa_equipos(equipo_actual, todos_metricas):
    """Compara un equipo con el resto."""
    comp = {}
    puntajes = []
    for eq, met in todos_metricas.items():
        p = met.get('evaluaciones', {}).get('puntaje_promedio')
        if p:
            puntajes.append((eq, p))

    if puntajes:
        puntajes_sorted = sorted(puntajes, key=lambda x: x[1], reverse=True)
        prom_general = sum(p for _, p in puntajes) / len(puntajes)
        puntaje_equipo = next((p for eq, p in puntajes if eq == equipo_actual), 0)
        ranking = next((i + 1 for i, (eq, _) in enumerate(puntajes_sorted) if eq == equipo_actual), len(puntajes))
        comp['puntaje_modelo'] = {
            'equipo': round(puntaje_equipo, 1),
            'general': round(prom_general, 1),
            'diferencia': round(puntaje_equipo - prom_general, 1),
            'ranking': f"{ranking} de {len(puntajes)}"
        }
        comp['ranking_completo'] = [{'equipo': eq, 'puntaje': round(p, 1)} for eq, p in puntajes_sorted]

    return comp


# ============================================================
# PROMPT DE COACHING - EQUIPO
# ============================================================
def generar_prompt_equipo(equipo, metricas, comparativa, metricas_generales):
    metricas = convertir_tipos_nativos(metricas)
    comparativa = convertir_tipos_nativos(comparativa)
    metricas_generales = convertir_tipos_nativos(metricas_generales)

    prompt = f"""
Eres un DIRECTOR DE OPERACIONES y estratega de ventas en telecomunicaciones (Movistar Argentina).
Tu misión es analizar exhaustivamente el desempeño del EQUIPO COMPLETO y crear un plan de acción
estratégico para mejorar el rendimiento grupal.

## CONTEXTO:
- Empresa: Movistar Argentina (Telefonía móvil)
- Productos: Planes móviles (4GB, 8GB, 15GB, 30GB), Fibra Óptica, Promociones
- Objetivo: Portabilidad - traer clientes de otras compañías

## EQUIPO: {equipo}

### COMPOSICION:
- Total vendedores: {metricas.get('total_vendedores', 0)}
- Vendedores: {', '.join(metricas.get('vendedores', [])[:15])}{'...' if len(metricas.get('vendedores', [])) > 15 else ''}

### EVALUACIONES DEL MODELO DEL EQUIPO:
{json.dumps(metricas.get('evaluaciones', {}), indent=2, ensure_ascii=False)}

### PLANES OFRECIDOS:
{json.dumps(metricas.get('planes', {}), indent=2, ensure_ascii=False)}

### GESTION DE QUEJAS:
{json.dumps(metricas.get('quejas', {}), indent=2, ensure_ascii=False)}

### CALIDAD (TIEMPOS Y PRODUCTIVIDAD):
{json.dumps(metricas.get('calidad', {}), indent=2, ensure_ascii=False)}

### COMPARATIVA CON OTROS EQUIPOS:
{json.dumps(comparativa, indent=2, ensure_ascii=False)}

### METRICAS GENERALES:
- Puntaje general del modelo: {metricas_generales.get('puntaje_general', 0):.1f}
- Total equipos: {metricas_generales.get('total_equipos', 0)}

## GENERA UN ANALISIS EXHAUSTIVO EN JSON CON ESTA ESTRUCTURA:

{{
    "resumen_ejecutivo": "Parrafo de 3-4 oraciones resumiendo el estado actual del equipo",
    
    "diagnostico": {{
        "nivel_rendimiento": "EXCELENTE/BUENO/EN DESARROLLO/CRITICO",
        "puntaje_equipo": 0-100,
        "posicion_ranking": "X de Y equipos",
        "tendencia": "MEJORANDO/ESTABLE/DECAYENDO"
    }},
    
    "fortalezas_equipo": [
        {{
            "area": "Nombre del area fuerte",
            "evidencia": "Datos que lo demuestran",
            "impacto": "Como beneficia al equipo"
        }}
    ],
    
    "areas_mejora_prioritarias": [
        {{
            "area": "Nombre del area a mejorar",
            "situacion_actual": "Descripcion con datos",
            "meta": "Objetivo especifico y medible",
            "impacto_potencial": "Beneficio esperado al mejorar"
        }}
    ],
    
    "analisis_vendedores": {{
        "top_performers": ["Vendedores destacados con sus fortalezas"],
        "necesitan_apoyo": ["Vendedores que requieren atencion especial"],
        "potencial_alto": ["Vendedores con potencial de crecimiento"]
    }},
    
    "plan_accion_equipo": [
        {{
            "prioridad": 1,
            "accion": "Descripcion de la accion especifica",
            "responsable": "Lider del equipo / Todos",
            "plazo": "Inmediato/Corto plazo/Mediano plazo",
            "indicador_exito": "Metrica para medir el exito"
        }}
    ],
    
    "capacitaciones_recomendadas": [
        {{
            "tema": "Nombre del tema",
            "objetivo": "Que se busca lograr",
            "modalidad": "Grupal/Individual/Mixta",
            "duracion_sugerida": "X horas/sesiones",
            "vendedores_prioritarios": ["Lista de vendedores"]
        }}
    ],
    
    "metas_equipo": {{
        "corto_plazo_30_dias": [
            {{
                "meta": "Descripcion de la meta",
                "valor_actual": "X",
                "valor_objetivo": "Y",
                "estrategia": "Como lograrlo"
            }}
        ],
        "mediano_plazo_90_dias": [
            {{
                "meta": "Descripcion",
                "valor_actual": "X",
                "valor_objetivo": "Y",
                "estrategia": "Como lograrlo"
            }}
        ]
    }},
    
    "mensaje_motivacional_equipo": "Mensaje motivador para todo el equipo"
}}

IMPORTANTE:
1. Se ESPECIFICO con los datos - usa numeros concretos
2. Las recomendaciones deben ser ACCIONABLES y realistas
3. Identifica patrones grupales
4. El plan debe ser implementable por un supervisor/lider
5. Prioriza acciones por impacto

Responde SOLO con el JSON, sin explicaciones adicionales.
"""
    return prompt


# ============================================================
# GENERACIÓN CON GEMINI
# ============================================================
def generar_coaching_vendedor(agente, datos, model, metricas_generales, codigo_a_equipo, codigo_a_nombre):
    """Genera coaching para un vendedor."""
    # Buscar coaching previo
    coaching_previo = None
    archivo_prev = os.path.join(DIR_COACHING_VENDEDORES, f"coaching_{agente.replace(' ', '_')}.json")
    if os.path.exists(archivo_prev):
        try:
            with open(archivo_prev, 'r', encoding='utf-8') as f:
                coaching_previo = json.load(f)
        except:
            pass

    nombre_agente = obtener_nombre_agente(agente, codigo_a_nombre)
    metricas = obtener_metricas_vendedor(agente, datos, codigo_a_equipo, codigo_a_nombre)
    comparativa = calcular_comparativa_vendedor(agente, datos)

    if metricas['evaluaciones'].get('total_evaluadas', 0) == 0:
        return None, "Sin evaluaciones"

    prompt = generar_prompt_vendedor(nombre_agente, metricas, comparativa, metricas_generales, coaching_previo)

    try:
        response = model.generate_content(prompt)
        analisis = response.text

        resultado = convertir_tipos_nativos({
            'agente': nombre_agente,
            'agente_codigo': agente,
            'equipo': metricas.get('equipo', 'Sin Equipo'),
            'fecha_generacion': datetime.now().isoformat(),
            'metricas': metricas,
            'comparativa': comparativa,
            'analisis_coaching': analisis,
            'modelo_usado': MODEL_NAME,
            'tiene_historial': coaching_previo is not None,
        })

        return resultado, None
    except Exception as e:
        return None, str(e)


def generar_coaching_equipo(equipo, metricas, comparativa, model, metricas_generales):
    """Genera coaching para un equipo."""
    try:
        prompt = generar_prompt_equipo(equipo, metricas, comparativa, metricas_generales)
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=8000
            )
        )

        texto = response.text.strip()
        if texto.startswith("```json"):
            texto = texto[7:]
        if texto.startswith("```"):
            texto = texto[3:]
        if texto.endswith("```"):
            texto = texto[:-3]

        coaching_modelo = json.loads(texto)

        resultado = convertir_tipos_nativos({
            'equipo': equipo,
            'fecha_generacion': datetime.now().isoformat(),
            'metricas': metricas,
            'comparativa': comparativa,
            'coaching_modelo': coaching_modelo
        })

        return resultado, None
    except json.JSONDecodeError as e:
        return None, f"Error parseando JSON: {e}"
    except Exception as e:
        return None, f"Error: {e}"


# ============================================================
# MAIN
# ============================================================
def main():
    print("\n" + "=" * 70)
    print("  GENERADOR DE RESUMEN + PLAN DE ACCION")
    print("  Vendedores y Equipos - Movistar Argentina")
    print("=" * 70 + "\n")

    # Parsear argumentos
    solo_equipos = '--solo-equipos' in sys.argv
    solo_vendedores = '--solo-vendedores' in sys.argv
    forzar_actualizar = '--actualizar' in sys.argv or '-u' in sys.argv
    
    # Mínimo de evaluaciones
    min_eval = MIN_EVALUACIONES_DEFAULT
    if '--min' in sys.argv:
        idx = sys.argv.index('--min')
        if idx + 1 < len(sys.argv):
            min_eval = int(sys.argv[idx + 1])
    
    log(f"Minimo evaluaciones por vendedor: {min_eval}")

    # Cargar datos
    log("Cargando listado de vendedores...")
    listado, equipos_dict, codigo_a_equipo, codigo_a_nombre = cargar_listado_vendedores()

    log("Cargando datos completos...")
    datos = cargar_datos_completos()

    if 'evaluaciones' not in datos:
        log("No se encontraron evaluaciones. Ejecuta primero 4_evaluacion_gemini.py", "error")
        return

    # Inicializar modelo
    log(f"Inicializando modelo {MODEL_NAME}...")
    model = genai.GenerativeModel(MODEL_NAME)

    df_eval = datos['evaluaciones']

    # ============================================================
    # PARTE 1: COACHING POR VENDEDOR
    # ============================================================
    if not solo_equipos:
        print("\n" + "=" * 70)
        print("  PARTE 1: RESUMEN POR VENDEDOR")
        print("=" * 70)

        # Agentes con suficientes evaluaciones
        agentes_counts = df_eval['agente'].value_counts()
        agentes_validos = agentes_counts[agentes_counts >= min_eval].index.tolist()
        log(f"Vendedores con >= {min_eval} evaluaciones: {len(agentes_validos)}")

        metricas_generales_v = {
            'puntaje_prom_general': round(df_eval['puntaje_total'].mean(), 1),
            'total_agentes': len(agentes_validos)
        }

        # Cargar coaching existente (NO borrar)
        archivo_coaching_v = os.path.join(DIR_COACHING_VENDEDORES, "coaching_completo.json")
        coaching_existente_v = []
        agentes_ya_procesados = set()
        if os.path.exists(archivo_coaching_v):
            try:
                with open(archivo_coaching_v, 'r', encoding='utf-8') as f:
                    coaching_existente_v = json.load(f)
                agentes_ya_procesados = {c['agente'] for c in coaching_existente_v}
                log(f"Coaching previo cargado: {len(coaching_existente_v)} vendedores (NO se borran)")
            except:
                coaching_existente_v = []

        if forzar_actualizar:
            # Mantener los existentes como historial pero regenerar
            agentes_pendientes = agentes_validos
            log("MODO ACTUALIZACION: regenerando todos, el historial se preserva en archivos individuales")
        else:
            agentes_pendientes = [a for a in agentes_validos if a not in agentes_ya_procesados]

        log(f"Vendedores a procesar: {len(agentes_pendientes)}")

        if forzar_actualizar:
            resultados_v = []  # Nuevo consolidado (los individuales se mantienen como historial)
        else:
            resultados_v = coaching_existente_v.copy()  # Preservar existentes

        errores_v = 0
        for i, agente in enumerate(agentes_pendientes, 1):
            nombre_agente = obtener_nombre_agente(agente, codigo_a_nombre)
            print(f"\n  [{i}/{len(agentes_pendientes)}] Procesando: {nombre_agente}")

            resultado, error = generar_coaching_vendedor(agente, datos, model, metricas_generales_v, codigo_a_equipo, codigo_a_nombre)

            if error:
                log(f"  Error con {nombre_agente}: {error}", "error")
                errores_v += 1
                continue

            # Si es actualización, reemplazar; si no, agregar
            if forzar_actualizar:
                resultados_v.append(resultado)
            else:
                resultados_v.append(resultado)

            log(f"  Coaching generado para {nombre_agente}", "success")

            # Guardar individual
            archivo_ind = os.path.join(DIR_COACHING_VENDEDORES, f"coaching_{agente.replace(' ', '_')}.json")
            with open(archivo_ind, 'w', encoding='utf-8') as f:
                json.dump(resultado, f, ensure_ascii=False, indent=2)

            # Guardar consolidado incremental
            with open(archivo_coaching_v, 'w', encoding='utf-8') as f:
                json.dump(resultados_v, f, ensure_ascii=False, indent=2)

            if i < len(agentes_pendientes):
                time.sleep(RATE_LIMIT_SEG)

        # CSV resumen vendedores
        log("Generando CSV resumen de vendedores...")
        resumen_v = []
        for r in resultados_v:
            met = r.get('metricas', {})
            ev = met.get('evaluaciones', {})
            resumen_v.append({
                'agente': r.get('agente', ''),
                'agente_codigo': r.get('agente_codigo', ''),
                'equipo': r.get('equipo', met.get('equipo', 'Sin Equipo')),
                'fecha_coaching': r['fecha_generacion'],
                'puntaje_modelo': ev.get('puntaje_promedio', 0),
                'llamadas_evaluadas': ev.get('total_evaluadas', 0),
                'llamadas_excelentes': ev.get('llamadas_excelentes', 0),
                'llamadas_criticas': ev.get('llamadas_criticas', 0),
                'tiene_coaching': True
            })

        df_resumen_v = pd.DataFrame(resumen_v)
        df_resumen_v.to_csv(os.path.join(DIR_COACHING_VENDEDORES, "resumen_coaching.csv"), index=False)
        log(f"VENDEDORES COMPLETADO: {len(resultados_v)} procesados, {errores_v} errores", "success")

    # ============================================================
    # PARTE 2: COACHING POR EQUIPO
    # ============================================================
    if not solo_vendedores:
        print("\n" + "=" * 70)
        print("  PARTE 2: RESUMEN POR EQUIPO")
        print("=" * 70)

        equipos_validos = {k: v for k, v in equipos_dict.items()
                          if k and k != "Sin Equipo" and k != "nan" and len(v) >= 2}

        log(f"Equipos a analizar: {len(equipos_validos)}")
        for eq, vendedores in equipos_validos.items():
            print(f"   - {eq}: {len(vendedores)} vendedores")

        metricas_generales_eq = {
            'total_equipos': len(equipos_validos),
            'puntaje_general': float(df_eval['puntaje_total'].mean()),
        }

        # Recopilar métricas de todos los equipos primero
        log("Recopilando metricas de todos los equipos...")
        todos_equipos_metricas = {}
        for equipo, vendedores in equipos_validos.items():
            met = obtener_metricas_equipo(equipo, vendedores, datos, codigo_a_equipo)
            todos_equipos_metricas[equipo] = met
            log(f"  {equipo}: {met.get('evaluaciones', {}).get('total_evaluadas', 0)} evaluaciones")

        # Cargar coaching existente de equipos (NO borrar)
        archivo_coaching_eq = os.path.join(DIR_COACHING_EQUIPOS, "coaching_equipos_completo.json")
        coaching_existente_eq = []
        equipos_ya_procesados = set()
        if os.path.exists(archivo_coaching_eq) and not forzar_actualizar:
            try:
                with open(archivo_coaching_eq, 'r', encoding='utf-8') as f:
                    coaching_existente_eq = json.load(f)
                equipos_ya_procesados = {c['equipo'] for c in coaching_existente_eq}
                log(f"Coaching previo de equipos: {len(coaching_existente_eq)} (NO se borran)")
            except:
                coaching_existente_eq = []

        if forzar_actualizar:
            equipos_pendientes = list(equipos_validos.keys())
            resultados_eq = []
        else:
            equipos_pendientes = [e for e in equipos_validos.keys() if e not in equipos_ya_procesados]
            resultados_eq = coaching_existente_eq.copy()

        log(f"Equipos a procesar: {len(equipos_pendientes)}")

        errores_eq = 0
        for i, equipo in enumerate(equipos_pendientes, 1):
            print(f"\n  [{i}/{len(equipos_pendientes)}] Procesando equipo: {equipo}")

            metricas = todos_equipos_metricas[equipo]
            comparativa = calcular_comparativa_equipos(equipo, todos_equipos_metricas)

            resultado, error = generar_coaching_equipo(equipo, metricas, comparativa, model, metricas_generales_eq)

            if error:
                log(f"  Error con equipo {equipo}: {error}", "error")
                errores_eq += 1
                continue

            resultados_eq.append(resultado)
            log(f"  Coaching generado para equipo {equipo}", "success")

            # Guardar individual
            archivo_ind = os.path.join(DIR_COACHING_EQUIPOS, f"coaching_{equipo.replace(' ', '_')}.json")
            with open(archivo_ind, 'w', encoding='utf-8') as f:
                json.dump(resultado, f, ensure_ascii=False, indent=2)

            # Guardar consolidado incremental
            with open(archivo_coaching_eq, 'w', encoding='utf-8') as f:
                json.dump(resultados_eq, f, ensure_ascii=False, indent=2)

            if i < len(equipos_pendientes):
                time.sleep(RATE_LIMIT_SEG + 2)  # Un poco más de espera para equipos

        # CSV resumen equipos
        log("Generando CSV resumen de equipos...")
        resumen_eq = []
        for r in resultados_eq:
            met = r.get('metricas', {})
            ev = met.get('evaluaciones', {})
            coaching_modelo = r.get('coaching_modelo', {})
            diag = coaching_modelo.get('diagnostico', {})
            resumen_eq.append({
                'equipo': r['equipo'],
                'fecha_coaching': r['fecha_generacion'],
                'total_vendedores': met.get('total_vendedores', 0),
                'puntaje_modelo_equipo': ev.get('puntaje_promedio', 0),
                'evaluaciones_totales': ev.get('total_evaluadas', 0),
                'nivel_rendimiento': diag.get('nivel_rendimiento', 'N/A'),
                'puntaje_equipo': diag.get('puntaje_equipo', 0),
            })

        df_resumen_eq = pd.DataFrame(resumen_eq)
        df_resumen_eq.to_csv(os.path.join(DIR_COACHING_EQUIPOS, "resumen_coaching_equipos.csv"), index=False)
        log(f"EQUIPOS COMPLETADO: {len(resultados_eq)} procesados, {errores_eq} errores", "success")

    # ============================================================
    # RESUMEN FINAL
    # ============================================================
    print("\n" + "=" * 70)
    print("  PROCESO FINALIZADO")
    print("=" * 70)
    if not solo_equipos:
        log(f"Coaching vendedores: {DIR_COACHING_VENDEDORES}")
    if not solo_vendedores:
        log(f"Coaching equipos: {DIR_COACHING_EQUIPOS}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()

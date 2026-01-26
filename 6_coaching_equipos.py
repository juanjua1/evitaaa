"""
Script de Coaching IA para EQUIPOS
Genera análisis exhaustivos y planes de acción para equipos completos usando Gemini Pro
Integra datos de calidad, evaluaciones individuales y métricas de vendedores
PASO 3 del pipeline de análisis

Requiere haber ejecutado previamente:
- 4_evaluacion_gemini.py (evaluaciones individuales)
- 5_coaching_vendedores.py (coaching individual)
"""

import os
import json
import pandas as pd
from datetime import datetime
import time
import sys
from collections import Counter

# Suprimir warnings
import warnings
warnings.filterwarnings("ignore")

import google.generativeai as genai
from config import api_key

# Configurar API
genai.configure(api_key=api_key)

# Usar modelo más potente para análisis exhaustivo de equipos
MODEL_NAME = "gemini-2.0-flash"

# Directorios
DIR_REPORTES = "reportes"
DIR_COACHING = os.path.join(DIR_REPORTES, "coaching_vendedores")
DIR_COACHING_EQUIPOS = os.path.join(DIR_REPORTES, "coaching_equipos")
DIR_CALIDAD = "datos_calidad"
os.makedirs(DIR_COACHING_EQUIPOS, exist_ok=True)

def log(mensaje, tipo="info"):
    """Logger con timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    emoji = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}.get(tipo, "")
    print(f"[{timestamp}] {emoji} {mensaje}")


def cargar_listado_vendedores():
    """Carga el listado de vendedores con sus equipos"""
    listado_vendedores = {}
    equipos_vendedores = {}
    try:
        ruta_listado = os.path.join(os.path.dirname(__file__), 'LISTADO-DE-VENDEDORES.csv')
        df_listado = pd.read_csv(ruta_listado, header=0)
        for _, row in df_listado.iterrows():
            usuario = str(row.iloc[0]).strip().lower().replace('\t', '').replace(' ', '')
            nombre = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
            equipo = str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else "Sin Equipo"
            if usuario and nombre and usuario != 'usuario':
                listado_vendedores[usuario] = nombre.title()
                if equipo not in equipos_vendedores:
                    equipos_vendedores[equipo] = []
                equipos_vendedores[equipo].append(nombre.title())
        log(f"Cargados {len(listado_vendedores)} vendedores en {len(equipos_vendedores)} equipos")
    except Exception as e:
        log(f"Error cargando listado: {e}", "error")
    return listado_vendedores, equipos_vendedores


def cargar_datos_completos():
    """Carga todos los datos disponibles para el análisis de equipos"""
    datos = {}
    
    # Cargar evaluaciones de Gemini
    ruta_eval = os.path.join(DIR_REPORTES, "evaluaciones_gemini.csv")
    if os.path.exists(ruta_eval):
        datos['evaluaciones'] = pd.read_csv(ruta_eval)
        log(f"Cargadas {len(datos['evaluaciones'])} evaluaciones de IA")
    
    # Cargar coaching individual de vendedores
    ruta_coaching = os.path.join(DIR_COACHING, "coaching_completo.json")
    if os.path.exists(ruta_coaching):
        with open(ruta_coaching, 'r', encoding='utf-8') as f:
            datos['coaching_individual'] = json.load(f)
        log(f"Cargados {len(datos['coaching_individual'])} coaching individuales")
    
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
    
    # Cargar análisis de planes
    ruta_planes = os.path.join(DIR_REPORTES, "planes", "analisis_planes_detallado.csv")
    if os.path.exists(ruta_planes):
        datos['planes'] = pd.read_csv(ruta_planes)
        log(f"Cargados {len(datos['planes'])} registros de planes")
    
    # Cargar quejas
    ruta_quejas = os.path.join(DIR_REPORTES, "quejas", "quejas_no_resueltas.csv")
    if os.path.exists(ruta_quejas):
        datos['quejas'] = pd.read_csv(ruta_quejas)
        log(f"Cargadas {len(datos['quejas'])} quejas")
    
    # Cargar cierres comerciales
    ruta_cierres = os.path.join(DIR_REPORTES, "cierres_comerciales", "cierres_comerciales.csv")
    if os.path.exists(ruta_cierres):
        datos['cierres'] = pd.read_csv(ruta_cierres, sep=';')
        log(f"Cargados {len(datos['cierres'])} cierres comerciales")
    
    # Cargar datos de calidad (tiempos, ventas, llamadas)
    ruta_calidad = os.path.join(DIR_CALIDAD, "datos_calidad_procesados.json")
    if os.path.exists(ruta_calidad):
        with open(ruta_calidad, 'r', encoding='utf-8') as f:
            datos['calidad'] = json.load(f)
        log(f"Cargados datos de calidad")
    
    return datos


def obtener_nombre_agente(agente_id, listado_vendedores):
    """Convierte ID de agente a nombre real"""
    if pd.isna(agente_id) or agente_id is None:
        return "Desconocido"
    agente_normalizado = str(agente_id).lower().replace(' ', '').replace('_', '').replace('\t', '')
    return listado_vendedores.get(agente_normalizado, str(agente_id))


def crear_mapeo_codigo_a_equipo(datos):
    """Crea mapeo de código de agente normalizado a equipo desde datos de calidad"""
    codigo_a_equipo = {}
    codigo_a_nombre = {}
    
    if 'calidad' in datos and 'llamadas' in datos['calidad']:
        for v in datos['calidad']['llamadas'].get('por_vendedor', []):
            agente = str(v.get('agente', '')).lower().replace(' ', '')
            equipo = v.get('equipo', 'Sin Equipo')
            nombre = v.get('vendedor', agente)
            codigo_a_equipo[agente] = equipo
            codigo_a_nombre[agente] = nombre
    
    return codigo_a_equipo, codigo_a_nombre


def normalizar_codigo_agente(agente):
    """Normaliza código de agente para comparación (MZA 1 -> mza1)"""
    if pd.isna(agente) or agente is None:
        return ''
    return str(agente).lower().replace(' ', '').replace('_', '').replace('\t', '')


def recopilar_metricas_equipo(equipo, vendedores_equipo, datos, listado_vendedores, codigo_a_equipo=None):
    """Recopila todas las métricas de un equipo completo"""
    metricas = {
        'equipo': equipo,
        'vendedores': vendedores_equipo,
        'total_vendedores': len(vendedores_equipo),
        'evaluaciones': {},
        'coaching_resumen': [],
        'clasificacion': {},
        'planes': {},
        'quejas': {},
        'calidad': {},
        'cierres': {}
    }
    
    # Crear mapeo de nombres para búsqueda por nombre (fallback)
    nombres_lower = [v.lower().strip() for v in vendedores_equipo]
    
    # ========================================
    # MÉTRICAS DE EVALUACIONES IA
    # ========================================
    if 'evaluaciones' in datos:
        df = datos['evaluaciones'].copy()
        
        # Usar mapeo de código a equipo si está disponible
        if codigo_a_equipo:
            df['agente_norm'] = df['agente'].apply(normalizar_codigo_agente)
            df['equipo_calc'] = df['agente_norm'].map(codigo_a_equipo)
            df_equipo = df[df['equipo_calc'] == equipo]
        else:
            # Fallback: buscar por nombre (método anterior)
            mask = df['agente'].apply(lambda x: any(n in str(x).lower() for n in nombres_lower) if pd.notna(x) else False)
            df_equipo = df[mask]
        
        if len(df_equipo) > 0:
            metricas['evaluaciones'] = {
                'total_evaluadas': len(df_equipo),
                'puntaje_promedio': round(df_equipo['puntaje_total'].mean(), 1),
                'puntaje_min': df_equipo['puntaje_total'].min(),
                'puntaje_max': df_equipo['puntaje_total'].max(),
                'desviacion_std': round(df_equipo['puntaje_total'].std(), 1),
                'llamadas_excelentes': len(df_equipo[df_equipo['puntaje_total'] >= 80]),
                'llamadas_buenas': len(df_equipo[(df_equipo['puntaje_total'] >= 60) & (df_equipo['puntaje_total'] < 80)]),
                'llamadas_regulares': len(df_equipo[(df_equipo['puntaje_total'] >= 40) & (df_equipo['puntaje_total'] < 60)]),
                'llamadas_criticas': len(df_equipo[df_equipo['puntaje_total'] <= 40]),
                'criterios': {},
                'areas_mejora': [],
                'fortalezas': []
            }
            
            # Puntajes por criterio
            criterios = ['saludo_presentacion', 'identificacion_cliente', 'deteccion_necesidades',
                        'oferta_productos', 'manejo_objeciones', 'cierre', 'despedida',
                        'proactividad', 'empatia', 'resolucion_problemas']
            
            for c in criterios:
                if c in df_equipo.columns:
                    metricas['evaluaciones']['criterios'][c] = round(df_equipo[c].mean(), 1)
            
            # Áreas de mejora frecuentes
            areas_mejora = []
            for areas in df_equipo['areas_mejora'].dropna():
                if isinstance(areas, str):
                    for area in areas.split(','):
                        area = area.strip().strip('"').strip("'").strip('[').strip(']')
                        if area:
                            areas_mejora.append(area)
            if areas_mejora:
                metricas['evaluaciones']['areas_mejora'] = dict(Counter(areas_mejora).most_common(10))
            
            # Fortalezas
            fortalezas = []
            for fort in df_equipo['fortalezas'].dropna():
                if isinstance(fort, str):
                    for f in fort.split(','):
                        f = f.strip().strip('"').strip("'").strip('[').strip(']')
                        if f:
                            fortalezas.append(f)
            if fortalezas:
                metricas['evaluaciones']['fortalezas'] = dict(Counter(fortalezas).most_common(10))
            
            # Rendimiento por vendedor
            rendimiento_vendedores = []
            for vendedor in vendedores_equipo:
                mask_v = df_equipo['agente'].apply(lambda x: vendedor.lower() in str(x).lower() if pd.notna(x) else False)
                df_v = df_equipo[mask_v]
                if len(df_v) > 0:
                    rendimiento_vendedores.append({
                        'vendedor': vendedor,
                        'puntaje_promedio': round(df_v['puntaje_total'].mean(), 1),
                        'evaluaciones': len(df_v),
                        'excelentes': len(df_v[df_v['puntaje_total'] >= 80]),
                        'criticas': len(df_v[df_v['puntaje_total'] <= 40])
                    })
            metricas['evaluaciones']['rendimiento_vendedores'] = sorted(
                rendimiento_vendedores, key=lambda x: x['puntaje_promedio'], reverse=True
            )
    
    # ========================================
    # RESUMEN DE COACHING INDIVIDUAL
    # ========================================
    if 'coaching_individual' in datos:
        for coaching in datos['coaching_individual']:
            agente = coaching.get('agente', '')
            if any(n in agente.lower() for n in nombres_lower):
                comparativa = coaching.get('comparativa', {})
                metricas['coaching_resumen'].append({
                    'vendedor': agente,
                    'puntaje_ia': comparativa.get('puntaje_ia', {}).get('agente', 0),
                    'conversion': comparativa.get('conversion', {}).get('agente', 0),
                    'percentil': comparativa.get('puntaje_ia', {}).get('percentil', 0)
                })
    
    # ========================================
    # MÉTRICAS DE CLASIFICACIÓN
    # ========================================
    if 'clasificacion' in datos:
        df = datos['clasificacion'].copy()
        
        if codigo_a_equipo:
            df['agente_norm'] = df['agente'].apply(normalizar_codigo_agente)
            df['equipo_calc'] = df['agente_norm'].map(codigo_a_equipo)
            df_equipo = df[df['equipo_calc'] == equipo]
        else:
            mask = df['agente'].apply(lambda x: any(n in str(x).lower() for n in nombres_lower) if pd.notna(x) else False)
            df_equipo = df[mask]
        
        if len(df_equipo) > 0:
            total = len(df_equipo)
            metricas['clasificacion'] = {
                'total_llamadas': total,
                'con_saludo': len(df_equipo[df_equipo.get('tiene_saludo', False) == True]) if 'tiene_saludo' in df_equipo.columns else 0,
                'con_cierre': len(df_equipo[df_equipo.get('tiene_cierre', False) == True]) if 'tiene_cierre' in df_equipo.columns else 0,
                'ofrece_plan': len(df_equipo[df_equipo.get('ofrece_plan', False) == True]) if 'ofrece_plan' in df_equipo.columns else 0,
                'ofrece_fibra': len(df_equipo[df_equipo.get('ofrece_fibra', False) == True]) if 'ofrece_fibra' in df_equipo.columns else 0,
                'ventas': len(df_equipo[df_equipo.get('es_venta', False) == True]) if 'es_venta' in df_equipo.columns else 0,
            }
            
            if total > 0:
                metricas['clasificacion']['pct_saludo'] = round(metricas['clasificacion']['con_saludo'] / total * 100, 1)
                metricas['clasificacion']['pct_cierre'] = round(metricas['clasificacion']['con_cierre'] / total * 100, 1)
                metricas['clasificacion']['pct_plan'] = round(metricas['clasificacion']['ofrece_plan'] / total * 100, 1)
                metricas['clasificacion']['pct_fibra'] = round(metricas['clasificacion']['ofrece_fibra'] / total * 100, 1)
                metricas['clasificacion']['tasa_conversion'] = round(metricas['clasificacion']['ventas'] / total * 100, 1)
    
    # ========================================
    # MÉTRICAS DE PLANES Y FIBRA
    # ========================================
    if 'planes' in datos:
        df = datos['planes'].copy()
        
        if codigo_a_equipo:
            df['agente_norm'] = df['agente'].apply(normalizar_codigo_agente)
            df['equipo_calc'] = df['agente_norm'].map(codigo_a_equipo)
            df_equipo = df[df['equipo_calc'] == equipo]
        else:
            mask = df['agente'].apply(lambda x: any(n in str(x).lower() for n in nombres_lower) if pd.notna(x) else False)
            df_equipo = df[mask]
        
        if len(df_equipo) > 0:
            total = len(df_equipo)
            con_plan = len(df_equipo[df_equipo['cantidad_planes'] > 0])
            ofrece_fibra = len(df_equipo[df_equipo['ofrece_fibra'] == True])
            df_promo = df_equipo[df_equipo['es_dia_promo'] == True]
            menciona_promo = len(df_promo[df_promo['menciona_promo'] == True])
            
            metricas['planes'] = {
                'total_llamadas': total,
                'con_plan': con_plan,
                'pct_plan': round(con_plan / total * 100, 1) if total > 0 else 0,
                'ofrece_fibra': ofrece_fibra,
                'pct_fibra': round(ofrece_fibra / total * 100, 1) if total > 0 else 0,
                'dias_promo': len(df_promo),
                'menciona_promo': menciona_promo,
                'pct_promo': round(menciona_promo / len(df_promo) * 100, 1) if len(df_promo) > 0 else 0
            }
    
    # ========================================
    # MÉTRICAS DE QUEJAS
    # ========================================
    if 'quejas' in datos:
        df = datos['quejas'].copy()
        
        if codigo_a_equipo:
            df['agente_norm'] = df['agente'].apply(normalizar_codigo_agente)
            df['equipo_calc'] = df['agente_norm'].map(codigo_a_equipo)
            df_equipo = df[df['equipo_calc'] == equipo]
        else:
            mask = df['agente'].apply(lambda x: any(n in str(x).lower() for n in nombres_lower) if pd.notna(x) else False)
            df_equipo = df[mask]
        
        if len(df_equipo) > 0:
            total = len(df_equipo)
            no_resueltas = int(df_equipo['quejas_no_resueltas'].sum())
            
            metricas['quejas'] = {
                'total_quejas': total,
                'no_resueltas': no_resueltas,
                'resueltas': total - no_resueltas,
                'pct_resolucion': round((total - no_resueltas) / total * 100, 1) if total > 0 else 0
            }
    
    # ========================================
    # MÉTRICAS DE CALIDAD (TIEMPOS, VENTAS)
    # ========================================
    if 'calidad' in datos:
        calidad = datos['calidad']
        
        # Tiempos
        if 'tiempos' in calidad and 'por_vendedor' in calidad['tiempos']:
            tiempos_equipo = []
            for vendedor_data in calidad['tiempos']['por_vendedor']:
                if vendedor_data.get('equipo', '') == equipo:
                    tiempos_equipo.append(vendedor_data)
            
            if tiempos_equipo:
                metricas['calidad']['tiempos'] = {
                    'vendedores_con_datos': len(tiempos_equipo),
                    'break_promedio_seg': round(sum(v.get('break_seg', 0) for v in tiempos_equipo) / len(tiempos_equipo)),
                    'coaching_promedio_seg': round(sum(v.get('coaching_seg', 0) for v in tiempos_equipo) / len(tiempos_equipo)),
                    'disponible_promedio_seg': round(sum(v.get('disponible_seg', 0) for v in tiempos_equipo) / len(tiempos_equipo)),
                    'no_disponible_promedio_seg': round(sum(v.get('no_disponible_seg', 0) for v in tiempos_equipo) / len(tiempos_equipo)),
                }
        
        # Ventas
        if 'ventas' in calidad and 'por_vendedor' in calidad['ventas']:
            ventas_equipo = []
            for vendedor_data in calidad['ventas']['por_vendedor']:
                if vendedor_data.get('equipo', '') == equipo:
                    ventas_equipo.append(vendedor_data)
            
            if ventas_equipo:
                metricas['calidad']['ventas'] = {
                    'vendedores_con_datos': len(ventas_equipo),
                    'total_ventas': sum(v.get('cantidad_ventas', 0) for v in ventas_equipo),
                    'ventas_promedio': round(sum(v.get('cantidad_ventas', 0) for v in ventas_equipo) / len(ventas_equipo), 1)
                }
        
        # Llamadas
        if 'llamadas' in calidad and 'por_vendedor' in calidad['llamadas']:
            llamadas_equipo = []
            for vendedor_data in calidad['llamadas']['por_vendedor']:
                if vendedor_data.get('equipo', '') == equipo:
                    llamadas_equipo.append(vendedor_data)
            
            if llamadas_equipo:
                metricas['calidad']['llamadas'] = {
                    'vendedores_con_datos': len(llamadas_equipo),
                    'total_llamadas': sum(v.get('total_llamadas', 0) for v in llamadas_equipo),
                    'llamadas_promedio': round(sum(v.get('total_llamadas', 0) for v in llamadas_equipo) / len(llamadas_equipo), 1),
                    'atendidas_promedio': round(sum(v.get('atendidas', 0) for v in llamadas_equipo) / len(llamadas_equipo), 1)
                }
    
    return metricas


def calcular_comparativa_equipos(equipo_actual, todos_equipos_metricas):
    """Compara un equipo con el promedio de todos los equipos"""
    comparativa = {}
    
    # Recopilar métricas de todos los equipos
    puntajes_todos = []
    conversiones_todos = []
    fibra_todos = []
    planes_todos = []
    quejas_todos = []
    
    for eq, met in todos_equipos_metricas.items():
        if met.get('evaluaciones', {}).get('puntaje_promedio'):
            puntajes_todos.append(met['evaluaciones']['puntaje_promedio'])
        if met.get('clasificacion', {}).get('tasa_conversion'):
            conversiones_todos.append(met['clasificacion']['tasa_conversion'])
        if met.get('planes', {}).get('pct_fibra'):
            fibra_todos.append(met['planes']['pct_fibra'])
        if met.get('planes', {}).get('pct_plan'):
            planes_todos.append(met['planes']['pct_plan'])
        if met.get('quejas', {}).get('pct_resolucion'):
            quejas_todos.append(met['quejas']['pct_resolucion'])
    
    # Métricas del equipo actual
    met_actual = todos_equipos_metricas.get(equipo_actual, {})
    
    if puntajes_todos and met_actual.get('evaluaciones', {}).get('puntaje_promedio'):
        prom_general = sum(puntajes_todos) / len(puntajes_todos)
        prom_equipo = met_actual['evaluaciones']['puntaje_promedio']
        comparativa['puntaje_ia'] = {
            'equipo': round(prom_equipo, 1),
            'general': round(prom_general, 1),
            'diferencia': round(prom_equipo - prom_general, 1),
            'ranking': sorted(puntajes_todos, reverse=True).index(prom_equipo) + 1 if prom_equipo in puntajes_todos else len(puntajes_todos)
        }
    
    if conversiones_todos and met_actual.get('clasificacion', {}).get('tasa_conversion'):
        prom_general = sum(conversiones_todos) / len(conversiones_todos)
        prom_equipo = met_actual['clasificacion']['tasa_conversion']
        comparativa['conversion'] = {
            'equipo': round(prom_equipo, 1),
            'general': round(prom_general, 1),
            'diferencia': round(prom_equipo - prom_general, 1)
        }
    
    if fibra_todos and met_actual.get('planes', {}).get('pct_fibra'):
        prom_general = sum(fibra_todos) / len(fibra_todos)
        prom_equipo = met_actual['planes']['pct_fibra']
        comparativa['fibra'] = {
            'equipo': round(prom_equipo, 1),
            'general': round(prom_general, 1),
            'diferencia': round(prom_equipo - prom_general, 1)
        }
    
    return comparativa


def generar_prompt_coaching_equipo(equipo, metricas, comparativa, metricas_generales):
    """Genera el prompt para el análisis de coaching del equipo"""
    
    prompt = f"""
Eres un DIRECTOR DE OPERACIONES y estratega de ventas experimentado en telecomunicaciones (Movistar Argentina).
Tu misión es analizar exhaustivamente el desempeño del EQUIPO COMPLETO y crear un plan de acción 
estratégico para mejorar el rendimiento grupal.

## ⚠️ CONTEXTO DEL NEGOCIO:
- Empresa: Movistar Argentina (Telefonía móvil)
- Productos: Planes móviles (4GB, 8GB, 15GB, 30GB), Fibra Óptica, Promociones
- Objetivo: Portabilidad - traer clientes de otras compañías

## 📊 EQUIPO A ANALIZAR: {equipo}

### COMPOSICIÓN DEL EQUIPO:
- Total de vendedores: {metricas.get('total_vendedores', 0)}
- Vendedores: {', '.join(metricas.get('vendedores', [])[:10])}{'...' if len(metricas.get('vendedores', [])) > 10 else ''}

### MÉTRICAS DE EVALUACIÓN IA DEL EQUIPO:
{json.dumps(metricas.get('evaluaciones', {}), indent=2, ensure_ascii=False)}

### RENDIMIENTO POR VENDEDOR:
{json.dumps(metricas.get('evaluaciones', {}).get('rendimiento_vendedores', []), indent=2, ensure_ascii=False)}

### COACHING INDIVIDUAL - RESUMEN:
{json.dumps(metricas.get('coaching_resumen', []), indent=2, ensure_ascii=False)}

### MÉTRICAS DE CLASIFICACIÓN:
{json.dumps(metricas.get('clasificacion', {}), indent=2, ensure_ascii=False)}

### OFERTAS DE PRODUCTOS (PLANES Y FIBRA):
{json.dumps(metricas.get('planes', {}), indent=2, ensure_ascii=False)}

### GESTIÓN DE QUEJAS:
{json.dumps(metricas.get('quejas', {}), indent=2, ensure_ascii=False)}

### MÉTRICAS DE CALIDAD (TIEMPOS Y PRODUCTIVIDAD):
{json.dumps(metricas.get('calidad', {}), indent=2, ensure_ascii=False)}

### COMPARATIVA CON OTROS EQUIPOS:
{json.dumps(comparativa, indent=2, ensure_ascii=False)}

### MÉTRICAS GENERALES DE LA OPERACIÓN:
- Puntaje IA promedio general: {metricas_generales.get('puntaje_general', 0):.1f}
- Tasa conversión general: {metricas_generales.get('conversion_general', 0):.1f}%
- Total equipos: {metricas_generales.get('total_equipos', 0)}

## 🎯 TU TAREA:

Genera un análisis EXHAUSTIVO del equipo con la siguiente estructura JSON:

{{
    "resumen_ejecutivo": "Párrafo de 3-4 oraciones resumiendo el estado actual del equipo",
    
    "diagnostico": {{
        "nivel_rendimiento": "EXCELENTE/BUENO/EN DESARROLLO/CRÍTICO",
        "puntaje_equipo": 0-100,
        "posicion_ranking": "X de Y equipos",
        "tendencia": "MEJORANDO/ESTABLE/DECAYENDO"
    }},
    
    "fortalezas_equipo": [
        {{
            "area": "Nombre del área fuerte",
            "evidencia": "Datos que lo demuestran",
            "impacto": "Cómo beneficia al equipo"
        }}
    ],
    
    "areas_mejora_prioritarias": [
        {{
            "area": "Nombre del área a mejorar",
            "situacion_actual": "Descripción con datos",
            "meta": "Objetivo específico y medible",
            "impacto_potencial": "Beneficio esperado al mejorar"
        }}
    ],
    
    "analisis_vendedores": {{
        "top_performers": ["Lista de los mejores vendedores con sus fortalezas"],
        "necesitan_apoyo": ["Vendedores que requieren atención especial"],
        "potencial_alto": ["Vendedores con potencial de crecimiento"]
    }},
    
    "plan_accion_equipo": [
        {{
            "prioridad": 1,
            "accion": "Descripción de la acción específica",
            "responsable": "Líder del equipo / Todos",
            "plazo": "Inmediato/Corto plazo/Mediano plazo",
            "indicador_exito": "Métrica para medir el éxito",
            "recursos_necesarios": "Qué se necesita para implementar"
        }}
    ],
    
    "capacitaciones_recomendadas": [
        {{
            "tema": "Nombre del tema",
            "objetivo": "Qué se busca lograr",
            "modalidad": "Grupal/Individual/Mixta",
            "duracion_sugerida": "X horas/sesiones",
            "vendedores_prioritarios": ["Lista de vendedores que más lo necesitan"]
        }}
    ],
    
    "dinamicas_equipo": [
        {{
            "nombre": "Nombre de la dinámica",
            "objetivo": "Qué se busca mejorar",
            "frecuencia": "Diaria/Semanal/Mensual",
            "descripcion": "Cómo implementarla"
        }}
    ],
    
    "metas_equipo": {{
        "corto_plazo_30_dias": [
            {{
                "meta": "Descripción de la meta",
                "valor_actual": "X",
                "valor_objetivo": "Y",
                "estrategia": "Cómo lograrlo"
            }}
        ],
        "mediano_plazo_90_dias": [
            {{
                "meta": "Descripción de la meta",
                "valor_actual": "X",
                "valor_objetivo": "Y",
                "estrategia": "Cómo lograrlo"
            }}
        ]
    }},
    
    "seguimiento": {{
        "reuniones_sugeridas": "Frecuencia y formato de reuniones de equipo",
        "metricas_monitorear": ["Lista de KPIs a seguir semanalmente"],
        "alertas": ["Situaciones que requieren intervención inmediata"]
    }}
}}

IMPORTANTE:
1. Sé ESPECÍFICO con los datos - usa números concretos del análisis
2. Las recomendaciones deben ser ACCIONABLES y realistas
3. Identifica patrones grupales, no solo individuales
4. Considera la dinámica de equipo y cómo los vendedores pueden apoyarse entre sí
5. El plan debe ser implementable por un supervisor/líder de equipo
6. Prioriza las acciones por impacto y facilidad de implementación

Responde SOLO con el JSON, sin explicaciones adicionales.
"""
    
    return prompt


def generar_coaching_equipo(equipo, metricas, comparativa, model, metricas_generales):
    """Genera el coaching para un equipo específico"""
    try:
        prompt = generar_prompt_coaching_equipo(equipo, metricas, comparativa, metricas_generales)
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=8000
            )
        )
        
        # Extraer JSON de la respuesta
        texto = response.text.strip()
        if texto.startswith("```json"):
            texto = texto[7:]
        if texto.startswith("```"):
            texto = texto[3:]
        if texto.endswith("```"):
            texto = texto[:-3]
        
        coaching_ia = json.loads(texto)
        
        resultado = {
            'equipo': equipo,
            'fecha_generacion': datetime.now().isoformat(),
            'metricas': metricas,
            'comparativa': comparativa,
            'coaching_ia': coaching_ia
        }
        
        return resultado, None
        
    except json.JSONDecodeError as e:
        return None, f"Error parseando JSON: {e}"
    except Exception as e:
        return None, f"Error generando coaching: {e}"


def main():
    print("\n" + "="*70)
    print("🏢 COACHING IA PARA EQUIPOS - PASO 3")
    print("="*70 + "\n")
    
    # Cargar modelo
    log("Inicializando modelo Gemini...")
    model = genai.GenerativeModel(MODEL_NAME)
    log(f"Modelo: {MODEL_NAME}", "success")
    
    # Cargar listado de vendedores y equipos
    log("Cargando listado de vendedores...")
    listado_vendedores, equipos_vendedores = cargar_listado_vendedores()
    
    # Filtrar equipos válidos
    equipos_validos = {k: v for k, v in equipos_vendedores.items() 
                       if k and k != "Sin Equipo" and k != "nan" and len(v) >= 2}
    
    if not equipos_validos:
        log("No se encontraron equipos válidos para analizar", "error")
        return
    
    log(f"Equipos a analizar: {len(equipos_validos)}")
    for eq, vendedores in equipos_validos.items():
        print(f"   - {eq}: {len(vendedores)} vendedores")
    
    # Cargar datos
    log("\nCargando datos completos...")
    datos = cargar_datos_completos()
    
    # Calcular métricas generales
    metricas_generales = {
        'total_equipos': len(equipos_validos),
        'puntaje_general': 0,
        'conversion_general': 0
    }
    
    if 'evaluaciones' in datos:
        metricas_generales['puntaje_general'] = datos['evaluaciones']['puntaje_total'].mean()
    
    if 'clasificacion' in datos and 'es_venta' in datos['clasificacion'].columns:
        metricas_generales['conversion_general'] = datos['clasificacion']['es_venta'].mean() * 100
    
    # Recopilar métricas de todos los equipos
    log("\nCreando mapeo de códigos de agente a equipos...")
    codigo_a_equipo, codigo_a_nombre = crear_mapeo_codigo_a_equipo(datos)
    log(f"Mapeo creado: {len(codigo_a_equipo)} agentes")
    
    log("\nRecopilando métricas de todos los equipos...")
    todos_equipos_metricas = {}
    for equipo, vendedores in equipos_validos.items():
        metricas = recopilar_metricas_equipo(equipo, vendedores, datos, listado_vendedores, codigo_a_equipo)
        todos_equipos_metricas[equipo] = metricas
        log(f"  {equipo}: {metricas.get('evaluaciones', {}).get('total_evaluadas', 0)} evaluaciones")
    
    # Verificar coaching existente
    archivo_coaching = os.path.join(DIR_COACHING_EQUIPOS, "coaching_equipos_completo.json")
    # Siempre regenerar para tener métricas actualizadas
    coaching_existente = []
    equipos_procesados = []
    
    # Filtrar equipos pendientes
    if len(sys.argv) > 1:
        max_equipos = int(sys.argv[1])
        log(f"Procesando máximo {max_equipos} equipos")
    else:
        max_equipos = len(equipos_validos)
    
    equipos_pendientes = [e for e in equipos_validos.keys() if e not in equipos_procesados][:max_equipos]
    
    if not equipos_pendientes:
        log("Todos los equipos ya tienen coaching generado", "success")
        return
    
    log(f"Pendientes a procesar: {len(equipos_pendientes)}")
    print("-" * 70)
    
    # Procesar cada equipo
    resultados = coaching_existente.copy()
    errores = 0
    
    for i, equipo in enumerate(equipos_pendientes, 1):
        print(f"\n[{i}/{len(equipos_pendientes)}] Generando coaching para equipo: {equipo}")
        log("Calculando comparativas...")
        
        metricas = todos_equipos_metricas[equipo]
        comparativa = calcular_comparativa_equipos(equipo, todos_equipos_metricas)
        
        resultado, error = generar_coaching_equipo(equipo, metricas, comparativa, model, metricas_generales)
        
        if error:
            log(f"Error: {error}", "error")
            errores += 1
            continue
        
        resultados.append(resultado)
        log(f"Coaching generado exitosamente", "success")
        
        # Guardar individual
        archivo_individual = os.path.join(DIR_COACHING_EQUIPOS, f"coaching_{equipo.replace(' ', '_')}.json")
        with open(archivo_individual, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        
        # Guardar consolidado
        with open(archivo_coaching, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)
        
        # Rate limiting
        if i < len(equipos_pendientes):
            log("Esperando 5 segundos (rate limiting)...")
            time.sleep(5)
    
    # Generar CSV resumen
    log("\nGenerando resumen CSV...")
    
    resumen_data = []
    for r in resultados:
        metricas = r.get('metricas', {})
        eval_data = metricas.get('evaluaciones', {})
        clasif_data = metricas.get('clasificacion', {})
        planes_data = metricas.get('planes', {})
        coaching_ia = r.get('coaching_ia', {})
        diagnostico = coaching_ia.get('diagnostico', {})
        
        resumen_data.append({
            'equipo': r['equipo'],
            'fecha_coaching': r['fecha_generacion'],
            'total_vendedores': metricas.get('total_vendedores', 0),
            'puntaje_ia_equipo': eval_data.get('puntaje_promedio', 0),
            'evaluaciones_totales': eval_data.get('total_evaluadas', 0),
            'tasa_conversion': clasif_data.get('tasa_conversion', 0),
            'pct_fibra': planes_data.get('pct_fibra', 0),
            'pct_plan': planes_data.get('pct_plan', 0),
            'nivel_rendimiento': diagnostico.get('nivel_rendimiento', 'N/A'),
            'puntaje_equipo': diagnostico.get('puntaje_equipo', 0)
        })
    
    df_resumen = pd.DataFrame(resumen_data)
    df_resumen.to_csv(os.path.join(DIR_COACHING_EQUIPOS, "resumen_coaching_equipos.csv"), index=False)
    
    # Resumen final
    print("\n" + "="*70)
    log("PROCESO FINALIZADO", "success")
    log(f"Coaching generado: {len(resultados)} equipos")
    log(f"Errores: {errores}")
    log(f"Archivos en: {DIR_COACHING_EQUIPOS}")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

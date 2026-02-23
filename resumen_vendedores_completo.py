"""
Resumen Integral de Vendedores - Métricas Operacionales + Calidad
=================================================================
Cruza datos de:
1. Detalle de Interacciones (CSV Mitrol) → métricas operacionales
2. Evaluaciones Gemini (CSV) → puntajes de calidad por llamada

Genera un reporte completo por vendedor con:
- Total de llamadas, duración promedio, talking time
- Minutos hablados por hora
- Tipificaciones (ventas, rechazos, contacto efectivo)
- Puntajes de calidad promedio por criterio
- Ranking general
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta

# =============================================================================
# CONFIGURACIÓN
# =============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_INTERACCIONES = os.path.join(BASE_DIR, "Detalle Interacciones (Campaña - Lote).csv")
CSV_EVALUACIONES = os.path.join(BASE_DIR, "reportes", "evaluaciones_gemini.csv")
SALIDA_CSV = os.path.join(BASE_DIR, "reportes", "resumen_vendedores_integral.csv")
SALIDA_JSON = os.path.join(BASE_DIR, "reportes", "resumen_vendedores_integral.json")

NOMBRES_AGENTES = {
    'mza1': 'MZA 1', 'mza2': 'MZA 2', 'mza3': 'MZA 3',
    'mza4': 'MZA 4', 'mza5': 'MZA 5', 'mza6': 'MZA 6',
    'mza7': 'MZA 7', 'mza8': 'MZA 8', 'mza9': 'MZA 9',
    'mza10': 'MZA 10', 'mza12': 'MZA 12'
}

# =============================================================================
# CARGAR DATOS
# =============================================================================
def cargar_interacciones():
    """Carga y preprocesa el CSV de interacciones de Mitrol."""
    df = pd.read_csv(CSV_INTERACCIONES, sep=';', encoding='utf-8')
    
    # Convertir columnas numéricas (vienen como string con comillas)
    cols_numericas = ['Duración', 'Tiempo Tarifado', 'TalkingTime', 'Hold', 'ACW', 'EnCola', 'Preview', 'Dialing', 'Ringing']
    for col in cols_numericas:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace('"', ''), errors='coerce').fillna(0).astype(int)
    
    # Parsear fecha
    df['Fecha_dt'] = pd.to_datetime(df['Inicio'], format='%d/%m/%Y %H:%M:%S', dayfirst=True, errors='coerce')
    df['Fecha'] = df['Fecha_dt'].dt.date
    df['Hora'] = df['Fecha_dt'].dt.hour
    
    print(f"  ✅ Interacciones cargadas: {len(df)} registros")
    print(f"     Agentes: {sorted(df['LoginId'].unique())}")
    print(f"     Fechas: {df['Fecha'].min()} a {df['Fecha'].max()}")
    return df


def cargar_evaluaciones():
    """Carga las evaluaciones de calidad de Gemini."""
    if not os.path.exists(CSV_EVALUACIONES):
        print("  ⚠️ No se encontró evaluaciones_gemini.csv")
        return None
    
    df = pd.read_csv(CSV_EVALUACIONES, encoding='utf-8')
    
    # Extraer agente del nombre de archivo (amza10_... -> mza10)
    df['agente_norm'] = df['archivo'].apply(lambda x: x.split('_')[0].replace('a', '', 1) if x.startswith('a') else x.split('_')[0])
    
    # Extraer ID de interacción del nombre de archivo para matchear
    # Formato: amza10_1_260209105133829_ACD_95297_mejorado.json
    def extraer_id_interaccion(archivo):
        partes = archivo.split('_')
        if len(partes) >= 5:
            # Reconstruir: 260209105133829_ACD_95297
            return f"{partes[2]}_{partes[3]}_{partes[4]}"
        return ''
    
    df['id_interaccion'] = df['archivo'].apply(extraer_id_interaccion)
    
    cols_puntaje = ['saludo_presentacion', 'identificacion_cliente', 'deteccion_necesidades',
                    'oferta_productos', 'manejo_objeciones', 'cierre', 'despedida',
                    'proactividad', 'empatia', 'resolucion_problemas', 'puntaje_total']
    for col in cols_puntaje:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    print(f"  ✅ Evaluaciones cargadas: {len(df)} registros")
    return df


# =============================================================================
# MÉTRICAS OPERACIONALES POR VENDEDOR
# =============================================================================
def calcular_metricas_operacionales(df):
    """Calcula métricas operacionales por vendedor."""
    resultados = {}
    
    for agente in sorted(df['LoginId'].unique()):
        df_ag = df[df['LoginId'] == agente]
        
        # --- Métricas generales ---
        total_llamadas = len(df_ag)
        
        # Duración en segundos
        duracion_total_seg = df_ag['Duración'].sum()
        duracion_promedio_seg = df_ag['Duración'].mean()
        talking_total_seg = df_ag['TalkingTime'].sum()
        talking_promedio_seg = df_ag['TalkingTime'].mean()
        hold_total_seg = df_ag['Hold'].sum()
        acw_total_seg = df_ag['ACW'].sum()
        
        # Convertir a minutos
        duracion_total_min = duracion_total_seg / 60
        talking_total_min = talking_total_seg / 60
        
        # --- Llamadas por resultado ---
        exitosas = len(df_ag[df_ag['Tipos Tipificación'] == 'Exitoso'])
        no_exitosas = len(df_ag[df_ag['Tipos Tipificación'] == 'No Exitoso'])
        tasa_contacto_efectivo = (exitosas / total_llamadas * 100) if total_llamadas > 0 else 0
        
        # --- Tipificaciones detalladas ---
        ventas = len(df_ag[df_ag['Tipificación'] == 'Venta'])
        agendados = len(df_ag[df_ag['Tipificación'] == 'Agendado por el Vdor'])
        no_quiere = len(df_ag[df_ag['Tipificación'] == 'No quiere volver a ser contactado'])
        conforme = len(df_ag[df_ag['Tipificación'] == 'Conforme con plan-prestador actual'])
        cortes = len(df_ag[df_ag['Tipificación'] == 'Se corta durante la conversacion'])
        mudas = len(df_ag[df_ag['Tipificación'] == 'Cae Muda o Cortada'])
        contestador = len(df_ag[df_ag['Tipificación'] == 'Contestador'])
        nro_equivocado = len(df_ag[df_ag['Tipificación'] == 'Número equivocado'])
        
        # --- Distribución por hora ---
        llamadas_por_hora = df_ag.groupby('Hora').size().to_dict()
        talking_por_hora = df_ag.groupby('Hora')['TalkingTime'].sum().to_dict()
        # Minutos hablados por hora (talking time / 60)
        min_hablados_por_hora = {h: round(s / 60, 1) for h, s in talking_por_hora.items()}
        
        # Promedio de minutos hablados por hora trabajada
        horas_trabajadas = len(llamadas_por_hora)
        promedio_min_por_hora = round(talking_total_min / horas_trabajadas, 1) if horas_trabajadas > 0 else 0
        
        # --- Distribución por día ---
        llamadas_por_dia = df_ag.groupby('Fecha').size().to_dict()
        dias_trabajados = len(llamadas_por_dia)
        llamadas_por_dia_promedio = round(total_llamadas / dias_trabajados, 1) if dias_trabajados > 0 else 0
        
        # --- Llamadas largas (>1 min talking) vs cortas ---
        llamadas_largas = len(df_ag[df_ag['TalkingTime'] > 60])
        llamadas_cortas = len(df_ag[df_ag['TalkingTime'] <= 60])
        
        # --- Llamadas con conversación real (>30s talking) ---
        con_conversacion = len(df_ag[df_ag['TalkingTime'] > 30])
        tasa_conversacion = round(con_conversacion / total_llamadas * 100, 1) if total_llamadas > 0 else 0
        
        # --- Origen del corte ---
        corte_cliente = len(df_ag[df_ag['Origen Corte'] == 'Cliente'])
        corte_agente = len(df_ag[df_ag['Origen Corte'] == 'Agente'])
        
        resultados[agente] = {
            'nombre': NOMBRES_AGENTES.get(agente, agente.upper()),
            'total_llamadas': total_llamadas,
            'dias_trabajados': dias_trabajados,
            'llamadas_por_dia_promedio': llamadas_por_dia_promedio,
            'duracion_total_min': round(duracion_total_min, 1),
            'duracion_promedio_seg': round(duracion_promedio_seg, 1),
            'talking_total_min': round(talking_total_min, 1),
            'talking_promedio_seg': round(talking_promedio_seg, 1),
            'hold_total_min': round(hold_total_seg / 60, 1),
            'acw_total_min': round(acw_total_seg / 60, 1),
            'horas_trabajadas': horas_trabajadas,
            'promedio_min_hablados_por_hora': promedio_min_por_hora,
            'exitosas': exitosas,
            'no_exitosas': no_exitosas,
            'tasa_contacto_efectivo': round(tasa_contacto_efectivo, 1),
            'ventas': ventas,
            'agendados': agendados,
            'no_quiere_contacto': no_quiere,
            'conforme_actual': conforme,
            'cortes_conversacion': cortes,
            'mudas_cortadas': mudas,
            'contestador': contestador,
            'nro_equivocado': nro_equivocado,
            'llamadas_largas_1min': llamadas_largas,
            'llamadas_cortas_1min': llamadas_cortas,
            'con_conversacion_real_30s': con_conversacion,
            'tasa_conversacion_real': tasa_conversacion,
            'corte_cliente': corte_cliente,
            'corte_agente': corte_agente,
            'llamadas_por_hora': llamadas_por_hora,
            'min_hablados_por_hora': min_hablados_por_hora,
            'llamadas_por_dia': {str(k): v for k, v in llamadas_por_dia.items()},
        }
    
    return resultados


# =============================================================================
# MÉTRICAS DE CALIDAD POR VENDEDOR
# =============================================================================
def calcular_metricas_calidad(df_eval):
    """Calcula promedios de calidad por vendedor desde evaluaciones Gemini."""
    if df_eval is None:
        return {}
    
    resultados = {}
    
    criterios = ['saludo_presentacion', 'identificacion_cliente', 'deteccion_necesidades',
                 'oferta_productos', 'manejo_objeciones', 'cierre', 'despedida',
                 'proactividad', 'empatia', 'resolucion_problemas', 'puntaje_total']
    
    for agente in sorted(df_eval['agente_norm'].unique()):
        df_ag = df_eval[df_eval['agente_norm'] == agente]
        
        promedios = {}
        for criterio in criterios:
            promedios[f'avg_{criterio}'] = round(df_ag[criterio].mean(), 1)
        
        # Distribución de puntajes
        total_eval = len(df_ag)
        excelentes = len(df_ag[df_ag['puntaje_total'] >= 70])
        buenos = len(df_ag[(df_ag['puntaje_total'] >= 40) & (df_ag['puntaje_total'] < 70)])
        regulares = len(df_ag[(df_ag['puntaje_total'] >= 20) & (df_ag['puntaje_total'] < 40)])
        malos = len(df_ag[df_ag['puntaje_total'] < 20])
        
        # Fibra ofrecida
        ofrecio_fibra = len(df_ag[df_ag['se_ofrecio_fibra'] == True])
        tasa_fibra = round(ofrecio_fibra / total_eval * 100, 1) if total_eval > 0 else 0
        
        # Fortalezas y áreas de mejora más comunes
        todas_fortalezas = []
        todas_mejoras = []
        for _, row in df_ag.iterrows():
            if pd.notna(row.get('fortalezas', '')):
                todas_fortalezas.extend([f.strip() for f in str(row['fortalezas']).split(',') if f.strip()])
            if pd.notna(row.get('areas_mejora', '')):
                todas_mejoras.extend([m.strip() for m in str(row['areas_mejora']).split(',') if m.strip()])
        
        # Top 3 fortalezas y mejoras
        from collections import Counter
        top_fortalezas = [item for item, _ in Counter(todas_fortalezas).most_common(3)]
        top_mejoras = [item for item, _ in Counter(todas_mejoras).most_common(3)]
        
        resultados[agente] = {
            'total_evaluaciones': total_eval,
            **promedios,
            'llamadas_excelentes_70plus': excelentes,
            'llamadas_buenas_40_70': buenos,
            'llamadas_regulares_20_40': regulares,
            'llamadas_malas_sub20': malos,
            'pct_excelentes': round(excelentes / total_eval * 100, 1) if total_eval > 0 else 0,
            'ofrecio_fibra': ofrecio_fibra,
            'tasa_ofrecimiento_fibra': tasa_fibra,
            'top_fortalezas': top_fortalezas,
            'top_areas_mejora': top_mejoras,
        }
    
    return resultados


# =============================================================================
# COMBINAR Y GENERAR RESUMEN
# =============================================================================
def generar_resumen_integral(metricas_op, metricas_cal):
    """Combina métricas operacionales y de calidad en un resumen integral."""
    
    todos_agentes = set(list(metricas_op.keys()) + list(metricas_cal.keys()))
    resumen = {}
    
    for agente in sorted(todos_agentes):
        op = metricas_op.get(agente, {})
        cal = metricas_cal.get(agente, {})
        
        # Score compuesto: 50% operacional + 50% calidad
        # Operacional: normalizado sobre talking time, tasa contacto, llamadas/día
        score_operacional = 0
        if op:
            # Normalizar talking promedio (máx razonable: 120 seg = 100 puntos)
            s_talking = min(op.get('talking_promedio_seg', 0) / 120 * 100, 100)
            # Tasa de contacto efectivo
            s_contacto = op.get('tasa_contacto_efectivo', 0)
            # Tasa de conversación real
            s_conversacion = op.get('tasa_conversacion_real', 0)
            # Minutos hablados por hora (máx razonable: 40 min = 100 puntos)
            s_productividad = min(op.get('promedio_min_hablados_por_hora', 0) / 40 * 100, 100)
            
            score_operacional = round((s_talking * 0.3 + s_contacto * 0.2 + s_conversacion * 0.2 + s_productividad * 0.3), 1)
        
        score_calidad = cal.get('avg_puntaje_total', 0)
        
        score_integral = round(score_operacional * 0.4 + score_calidad * 0.6, 1)
        
        resumen[agente] = {
            'nombre': op.get('nombre', NOMBRES_AGENTES.get(agente, agente.upper())),
            'score_integral': score_integral,
            'score_operacional': score_operacional,
            'score_calidad': score_calidad,
            **{k: v for k, v in op.items() if k not in ['nombre', 'llamadas_por_hora', 'min_hablados_por_hora', 'llamadas_por_dia']},
            **{k: v for k, v in cal.items() if k not in ['top_fortalezas', 'top_areas_mejora']},
            'top_fortalezas': cal.get('top_fortalezas', []),
            'top_areas_mejora': cal.get('top_areas_mejora', []),
            'detalle_por_hora': op.get('min_hablados_por_hora', {}),
            'detalle_por_dia': op.get('llamadas_por_dia', {}),
        }
    
    return resumen


def imprimir_resumen(resumen):
    """Imprime el resumen en consola de forma legible."""
    
    print("\n" + "=" * 90)
    print("  📊 RESUMEN INTEGRAL DE VENDEDORES - EQUIPO MEL")
    print("=" * 90)
    
    # Ordenar por score integral descendente
    ranking = sorted(resumen.items(), key=lambda x: x[1].get('score_integral', 0), reverse=True)
    
    print(f"\n{'#':<3} {'Agente':<10} {'Score':<8} {'Op.':<7} {'Cal.':<7} {'Llam':<6} {'Talk(m)':<9} {'Min/h':<7} {'% Conv':<7} {'Ventas':<7} {'Agenda':<7}")
    print("-" * 90)
    
    for i, (agente, datos) in enumerate(ranking, 1):
        print(f"{i:<3} {datos['nombre']:<10} {datos['score_integral']:<8} "
              f"{datos['score_operacional']:<7} {datos['score_calidad']:<7} "
              f"{datos.get('total_llamadas', 0):<6} "
              f"{datos.get('talking_total_min', 0):<9} "
              f"{datos.get('promedio_min_hablados_por_hora', 0):<7} "
              f"{datos.get('tasa_conversacion_real', 0):<7} "
              f"{datos.get('ventas', 0):<7} "
              f"{datos.get('agendados', 0):<7}")
    
    print("\n" + "-" * 90)
    print("\n📋 DETALLE POR VENDEDOR:\n")
    
    for i, (agente, d) in enumerate(ranking, 1):
        print(f"\n{'─' * 70}")
        print(f"  #{i} {d['nombre']} ({agente})")
        print(f"{'─' * 70}")
        
        print(f"  📊 SCORES: Integral={d['score_integral']} | Operacional={d['score_operacional']} | Calidad={d['score_calidad']}")
        
        print(f"\n  📞 MÉTRICAS OPERACIONALES:")
        print(f"     Total llamadas: {d.get('total_llamadas', 0)} | Días trabajados: {d.get('dias_trabajados', 0)}")
        print(f"     Llamadas/día promedio: {d.get('llamadas_por_dia_promedio', 0)}")
        print(f"     Duración promedio: {d.get('duracion_promedio_seg', 0)}s | Talking promedio: {d.get('talking_promedio_seg', 0)}s")
        print(f"     Talking total: {d.get('talking_total_min', 0)} min | Hold total: {d.get('hold_total_min', 0)} min")
        print(f"     ACW total: {d.get('acw_total_min', 0)} min")
        print(f"     Minutos hablados/hora: {d.get('promedio_min_hablados_por_hora', 0)}")
        print(f"     Horas activas: {d.get('horas_trabajadas', 0)}")
        
        print(f"\n  📈 RESULTADOS:")
        print(f"     Exitosas: {d.get('exitosas', 0)} ({d.get('tasa_contacto_efectivo', 0)}%) | No exitosas: {d.get('no_exitosas', 0)}")
        print(f"     Ventas: {d.get('ventas', 0)} | Agendados: {d.get('agendados', 0)}")
        print(f"     No quiere contacto: {d.get('no_quiere_contacto', 0)} | Conforme actual: {d.get('conforme_actual', 0)}")
        print(f"     Cortes: {d.get('cortes_conversacion', 0)} | Mudas: {d.get('mudas_cortadas', 0)}")
        print(f"     Corte cliente: {d.get('corte_cliente', 0)} | Corte agente: {d.get('corte_agente', 0)}")
        
        print(f"\n  🎯 ENGAGEMENT:")
        print(f"     Conversación real (>30s): {d.get('con_conversacion_real_30s', 0)} ({d.get('tasa_conversacion_real', 0)}%)")
        print(f"     Llamadas largas (>1min): {d.get('llamadas_largas_1min', 0)} | Cortas (<1min): {d.get('llamadas_cortas_1min', 0)}")
        
        if d.get('total_evaluaciones', 0) > 0:
            print(f"\n  🤖 CALIDAD (Gemini - {d['total_evaluaciones']} evaluaciones):")
            print(f"     Puntaje total promedio: {d.get('avg_puntaje_total', 0)}/100")
            print(f"     Saludo: {d.get('avg_saludo_presentacion', 0)} | Identificación: {d.get('avg_identificacion_cliente', 0)}")
            print(f"     Necesidades: {d.get('avg_deteccion_necesidades', 0)} | Oferta: {d.get('avg_oferta_productos', 0)}")
            print(f"     Objeciones: {d.get('avg_manejo_objeciones', 0)} | Cierre: {d.get('avg_cierre', 0)}")
            print(f"     Despedida: {d.get('avg_despedida', 0)} | Proactividad: {d.get('avg_proactividad', 0)}")
            print(f"     Empatía: {d.get('avg_empatia', 0)} | Resolución: {d.get('avg_resolucion_problemas', 0)}")
            print(f"     Fibra ofrecida: {d.get('ofrecio_fibra', 0)} ({d.get('tasa_ofrecimiento_fibra', 0)}%)")
            print(f"     Excelentes(≥70): {d.get('llamadas_excelentes_70plus', 0)} | Buenas(40-70): {d.get('llamadas_buenas_40_70', 0)}")
            print(f"     Regulares(20-40): {d.get('llamadas_regulares_20_40', 0)} | Malas(<20): {d.get('llamadas_malas_sub20', 0)}")
            
            if d.get('top_fortalezas'):
                print(f"     💪 Fortalezas: {', '.join(d['top_fortalezas'])}")
            if d.get('top_areas_mejora'):
                print(f"     ⚠️  Mejorar: {', '.join(d['top_areas_mejora'])}")


def guardar_resultados(resumen):
    """Guarda los resultados en CSV y JSON."""
    os.makedirs(os.path.dirname(SALIDA_CSV), exist_ok=True)
    
    # CSV plano
    filas = []
    for agente, datos in sorted(resumen.items()):
        fila = {k: v for k, v in datos.items() 
                if k not in ['top_fortalezas', 'top_areas_mejora', 'detalle_por_hora', 'detalle_por_dia']}
        fila['top_fortalezas'] = ', '.join(datos.get('top_fortalezas', []))
        fila['top_areas_mejora'] = ', '.join(datos.get('top_areas_mejora', []))
        fila['agente_id'] = agente
        filas.append(fila)
    
    df = pd.DataFrame(filas)
    df.to_csv(SALIDA_CSV, index=False, encoding='utf-8-sig')
    print(f"\n  ✅ CSV guardado: {SALIDA_CSV}")
    
    # JSON completo
    resumen_serializable = {}
    for agente, datos in resumen.items():
        resumen_serializable[agente] = datos
    
    with open(SALIDA_JSON, 'w', encoding='utf-8') as f:
        json.dump({
            'fecha_generacion': datetime.now().isoformat(),
            'total_agentes': len(resumen),
            'vendedores': resumen_serializable
        }, f, ensure_ascii=False, indent=2, default=str)
    print(f"  ✅ JSON guardado: {SALIDA_JSON}")


# =============================================================================
# MAIN
# =============================================================================
def main():
    print("\n" + "=" * 70)
    print("  📊 GENERANDO RESUMEN INTEGRAL DE VENDEDORES")
    print("=" * 70 + "\n")
    
    print("  1️⃣  Cargando datos de interacciones...")
    df_inter = cargar_interacciones()
    
    print("\n  2️⃣  Cargando evaluaciones de calidad...")
    df_eval = cargar_evaluaciones()
    
    print("\n  3️⃣  Calculando métricas operacionales...")
    metricas_op = calcular_metricas_operacionales(df_inter)
    
    print("  4️⃣  Calculando métricas de calidad...")
    metricas_cal = calcular_metricas_calidad(df_eval)
    
    print("  5️⃣  Generando resumen integral...")
    resumen = generar_resumen_integral(metricas_op, metricas_cal)
    
    imprimir_resumen(resumen)
    
    print("\n  6️⃣  Guardando resultados...")
    guardar_resultados(resumen)
    
    print("\n" + "=" * 70)
    print("  ✅ PROCESO COMPLETADO")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()

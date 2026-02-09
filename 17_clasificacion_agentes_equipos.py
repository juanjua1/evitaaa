#!/usr/bin/env python3
"""
Sistema de Clasificación por Agente y Equipo
=============================================
Analiza las evaluaciones de Gemini y genera clasificaciones detalladas
por agente individual y por equipo completo.
"""

import pandas as pd
import json
import os
import numpy as np
from datetime import datetime
from collections import defaultdict

# ==================== CONFIGURACIÓN ====================

CSV_EVALUACIONES = r"C:\Users\rodri\Documents\codigo-WC\eva\reportes\evaluaciones_gemini.csv"
CARPETA_SALIDA = r"C:\Users\rodri\Documents\codigo-WC\eva\reportes\clasificacion_agentes_equipos"

# Criterios de evaluación
CRITERIOS = [
    'saludo_presentacion',
    'identificacion_cliente', 
    'deteccion_necesidades',
    'oferta_productos',
    'manejo_objeciones',
    'cierre',
    'despedida',
    'proactividad',
    'empatia',
    'resolucion_problemas'
]

# Umbrales de clasificación
UMBRAL_EXCELENTE = 80
UMBRAL_BUENO = 60
UMBRAL_REGULAR = 40
UMBRAL_CRITICO = 20


def extraer_equipo(nombre_agente):
    """Extrae el nombre del equipo del nombre del agente."""
    if not nombre_agente or pd.isna(nombre_agente):
        return "SIN_EQUIPO"
    
    # Formato esperado: "MZA 100", "BYL VENTAS", "DIANA", etc.
    partes = str(nombre_agente).strip().split()
    
    if len(partes) >= 2:
        # Si el segundo valor es un número, el equipo es la primera parte
        try:
            int(partes[1])
            return partes[0]  # "MZA", "AMZA", etc.
        except ValueError:
            # Si no es número, todo es el equipo
            return nombre_agente
    
    return nombre_agente


def clasificar_nivel(puntaje):
    """Clasifica un puntaje en un nivel de desempeño."""
    if puntaje >= UMBRAL_EXCELENTE:
        return "EXCELENTE"
    elif puntaje >= UMBRAL_BUENO:
        return "BUENO"
    elif puntaje >= UMBRAL_REGULAR:
        return "REGULAR"
    elif puntaje >= UMBRAL_CRITICO:
        return "DEFICIENTE"
    else:
        return "CRÍTICO"


def convertir_a_tipos_nativos(obj):
    """Convierte tipos numpy/pandas a tipos nativos de Python para serialización JSON."""
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convertir_a_tipos_nativos(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convertir_a_tipos_nativos(item) for item in obj]
    elif pd.isna(obj):
        return None
    return obj


def analizar_por_agente(df):
    """Analiza las métricas agrupadas por agente."""
    print("\n" + "="*70)
    print("📊 ANÁLISIS POR AGENTE")
    print("="*70)
    
    # Agrupar por agente
    agentes_stats = []
    
    for agente in df['agente'].unique():
        if pd.isna(agente):
            continue
            
        df_agente = df[df['agente'] == agente]
        
        stats = {
            'agente': agente,
            'equipo': extraer_equipo(agente),
            'total_llamadas': len(df_agente),
            'total_ventas': len(df_agente[df_agente['puntaje_total'] >= 60]),
            'total_rechazos': len(df_agente[df_agente['puntaje_total'] < 20]),
            'puntaje_promedio': df_agente['puntaje_total'].mean()
        }
        
        # Promedios por criterio
        for criterio in CRITERIOS:
            stats[f'promedio_{criterio}'] = df_agente[criterio].mean()
        
        # Ofertas de fibra
        stats['total_fibra_ofrecida'] = df_agente['se_ofrecio_fibra'].sum()
        stats['porcentaje_fibra'] = (stats['total_fibra_ofrecida'] / stats['total_llamadas'] * 100) if stats['total_llamadas'] > 0 else 0
        
        # Clasificación general
        stats['nivel_desempeno'] = clasificar_nivel(stats['puntaje_promedio'])
        
        # Identificar fortalezas (criterios con mejor puntaje)
        criterios_puntajes = [(c, stats[f'promedio_{c}']) for c in CRITERIOS]
        criterios_puntajes.sort(key=lambda x: x[1], reverse=True)
        stats['fortaleza_1'] = criterios_puntajes[0][0]
        stats['fortaleza_1_puntaje'] = criterios_puntajes[0][1]
        stats['fortaleza_2'] = criterios_puntajes[1][0]
        stats['fortaleza_2_puntaje'] = criterios_puntajes[1][1]
        
        # Identificar debilidades (criterios con peor puntaje)
        stats['debilidad_1'] = criterios_puntajes[-1][0]
        stats['debilidad_1_puntaje'] = criterios_puntajes[-1][1]
        stats['debilidad_2'] = criterios_puntajes[-2][0]
        stats['debilidad_2_puntaje'] = criterios_puntajes[-2][1]
        
        agentes_stats.append(stats)
    
    # Crear DataFrame y ordenar por puntaje
    df_agentes = pd.DataFrame(agentes_stats)
    df_agentes = df_agentes.sort_values('puntaje_promedio', ascending=False)
    
    # Agregar ranking
    df_agentes['ranking'] = range(1, len(df_agentes) + 1)
    
    print(f"\n✅ Total de agentes analizados: {len(df_agentes)}")
    print(f"\n🏆 TOP 5 AGENTES:")
    print(df_agentes[['ranking', 'agente', 'puntaje_promedio', 'total_llamadas', 'nivel_desempeno']].head())
    print(f"\n⚠️ BOTTOM 5 AGENTES:")
    print(df_agentes[['ranking', 'agente', 'puntaje_promedio', 'total_llamadas', 'nivel_desempeno']].tail())
    
    return df_agentes


def analizar_por_equipo(df_agentes):
    """Analiza las métricas agrupadas por equipo."""
    print("\n" + "="*70)
    print("🏢 ANÁLISIS POR EQUIPO")
    print("="*70)
    
    # Agrupar por equipo
    equipos_stats = []
    
    for equipo in df_agentes['equipo'].unique():
        if pd.isna(equipo):
            continue
            
        df_equipo = df_agentes[df_agentes['equipo'] == equipo]
        
        stats = {
            'equipo': equipo,
            'total_agentes': len(df_equipo),
            'total_llamadas': df_equipo['total_llamadas'].sum(),
            'total_ventas': df_equipo['total_ventas'].sum(),
            'total_rechazos': df_equipo['total_rechazos'].sum(),
            'puntaje_promedio_equipo': df_equipo['puntaje_promedio'].mean(),
            'puntaje_mejor_agente': df_equipo['puntaje_promedio'].max(),
            'puntaje_peor_agente': df_equipo['puntaje_promedio'].min(),
            'mejor_agente': df_equipo.loc[df_equipo['puntaje_promedio'].idxmax(), 'agente'],
            'peor_agente': df_equipo.loc[df_equipo['puntaje_promedio'].idxmin(), 'agente']
        }
        
        # Promedios por criterio del equipo
        for criterio in CRITERIOS:
            stats[f'promedio_{criterio}'] = df_equipo[f'promedio_{criterio}'].mean()
        
        # Tasa de conversión estimada
        stats['tasa_conversion'] = (stats['total_ventas'] / stats['total_llamadas'] * 100) if stats['total_llamadas'] > 0 else 0
        
        # Promedio de fibra ofrecida
        stats['promedio_fibra_ofrecida'] = df_equipo['porcentaje_fibra'].mean()
        
        # Clasificación general del equipo
        stats['nivel_desempeno'] = clasificar_nivel(stats['puntaje_promedio_equipo'])
        
        # Identificar fortalezas del equipo
        criterios_puntajes = [(c, stats[f'promedio_{c}']) for c in CRITERIOS]
        criterios_puntajes.sort(key=lambda x: x[1], reverse=True)
        stats['fortaleza_equipo_1'] = criterios_puntajes[0][0]
        stats['fortaleza_equipo_1_puntaje'] = criterios_puntajes[0][1]
        
        # Identificar debilidades del equipo
        stats['debilidad_equipo_1'] = criterios_puntajes[-1][0]
        stats['debilidad_equipo_1_puntaje'] = criterios_puntajes[-1][1]
        
        equipos_stats.append(stats)
    
    # Crear DataFrame y ordenar por puntaje
    df_equipos = pd.DataFrame(equipos_stats)
    df_equipos = df_equipos.sort_values('puntaje_promedio_equipo', ascending=False)
    
    # Agregar ranking
    df_equipos['ranking_equipo'] = range(1, len(df_equipos) + 1)
    
    print(f"\n✅ Total de equipos analizados: {len(df_equipos)}")
    print(f"\n🏆 RANKING DE EQUIPOS:")
    print(df_equipos[['ranking_equipo', 'equipo', 'puntaje_promedio_equipo', 'total_agentes', 'total_llamadas', 'nivel_desempeno']])
    
    return df_equipos


def generar_reporte_detallado_agente(df_agentes, df_evaluaciones):
    """Genera un reporte JSON detallado por agente."""
    print("\n" + "="*70)
    print("📝 GENERANDO REPORTES DETALLADOS POR AGENTE")
    print("="*70)
    
    reportes = {}
    
    for _, row in df_agentes.iterrows():
        agente = row['agente']
        df_llamadas = df_evaluaciones[df_evaluaciones['agente'] == agente]
        
        reporte = {
            'agente': agente,
            'equipo': row['equipo'],
            'ranking': int(row['ranking']),
            'resumen': {
                'total_llamadas': int(row['total_llamadas']),
                'puntaje_promedio': round(float(row['puntaje_promedio']), 2),
                'nivel_desempeno': row['nivel_desempeno'],
                'total_ventas_estimadas': int(row['total_ventas']),
                'total_rechazos_estimados': int(row['total_rechazos'])
            },
            'fortalezas': [
                {
                    'criterio': row['fortaleza_1'],
                    'puntaje': round(float(row['fortaleza_1_puntaje']), 2)
                },
                {
                    'criterio': row['fortaleza_2'],
                    'puntaje': round(float(row['fortaleza_2_puntaje']), 2)
                }
            ],
            'debilidades': [
                {
                    'criterio': row['debilidad_1'],
                    'puntaje': round(float(row['debilidad_1_puntaje']), 2)
                },
                {
                    'criterio': row['debilidad_2'],
                    'puntaje': round(float(row['debilidad_2_puntaje']), 2)
                }
            ],
            'metricas_detalladas': {}
        }
        
        # Agregar métricas por criterio
        for criterio in CRITERIOS:
            reporte['metricas_detalladas'][criterio] = {
                'promedio': round(float(row[f'promedio_{criterio}']), 2),
                'nivel': clasificar_nivel(row[f'promedio_{criterio}'])
            }
        
        # Agregar info de fibra
        reporte['proactividad_fibra'] = {
            'total_ofrecidas': int(row['total_fibra_ofrecida']),
            'porcentaje': round(float(row['porcentaje_fibra']), 2)
        }
        
        # Ejemplos de mejores y peores llamadas
        df_llamadas_ordenadas = df_llamadas.sort_values('puntaje_total', ascending=False)
        
        if len(df_llamadas_ordenadas) > 0:
            mejores = df_llamadas_ordenadas.head(3)[['archivo', 'puntaje_total', 'resumen']].to_dict('records')
            reporte['mejores_llamadas'] = [
                {
                    'archivo': m['archivo'],
                    'puntaje': int(m['puntaje_total']),
                    'resumen': m['resumen']
                }
                for m in mejores
            ]
            
            peores = df_llamadas_ordenadas.tail(3)[['archivo', 'puntaje_total', 'areas_mejora']].to_dict('records')
            reporte['peores_llamadas'] = [
                {
                    'archivo': p['archivo'],
                    'puntaje': int(p['puntaje_total']),
                    'areas_mejora': p['areas_mejora']
                }
                for p in peores
            ]
        
        reportes[agente] = reporte
    
    print(f"✅ Reportes detallados generados para {len(reportes)} agentes")
    return reportes


def generar_reporte_detallado_equipo(df_equipos, df_agentes):
    """Genera un reporte JSON detallado por equipo."""
    print("\n" + "="*70)
    print("📝 GENERANDO REPORTES DETALLADOS POR EQUIPO")
    print("="*70)
    
    reportes = {}
    
    for _, row in df_equipos.iterrows():
        equipo = row['equipo']
        df_agentes_equipo = df_agentes[df_agentes['equipo'] == equipo]
        
        reporte = {
            'equipo': equipo,
            'ranking': int(row['ranking_equipo']),
            'resumen': {
                'total_agentes': int(row['total_agentes']),
                'total_llamadas': int(row['total_llamadas']),
                'puntaje_promedio': round(float(row['puntaje_promedio_equipo']), 2),
                'nivel_desempeno': row['nivel_desempeno'],
                'tasa_conversion_estimada': round(float(row['tasa_conversion']), 2)
            },
            'mejor_agente': {
                'nombre': row['mejor_agente'],
                'puntaje': round(float(row['puntaje_mejor_agente']), 2)
            },
            'peor_agente': {
                'nombre': row['peor_agente'],
                'puntaje': round(float(row['puntaje_peor_agente']), 2)
            },
            'fortalezas_equipo': [
                {
                    'criterio': row['fortaleza_equipo_1'],
                    'puntaje': round(float(row['fortaleza_equipo_1_puntaje']), 2)
                }
            ],
            'debilidades_equipo': [
                {
                    'criterio': row['debilidad_equipo_1'],
                    'puntaje': round(float(row['debilidad_equipo_1_puntaje']), 2)
                }
            ],
            'metricas_detalladas': {},
            'distribucion_agentes': []
        }
        
        # Agregar métricas por criterio del equipo
        for criterio in CRITERIOS:
            reporte['metricas_detalladas'][criterio] = {
                'promedio': round(float(row[f'promedio_{criterio}']), 2),
                'nivel': clasificar_nivel(row[f'promedio_{criterio}'])
            }
        
        # Distribución de agentes por nivel
        for nivel in ['EXCELENTE', 'BUENO', 'REGULAR', 'DEFICIENTE', 'CRÍTICO']:
            count = len(df_agentes_equipo[df_agentes_equipo['nivel_desempeno'] == nivel])
            if count > 0:
                reporte['distribucion_agentes'].append({
                    'nivel': nivel,
                    'cantidad': count,
                    'porcentaje': round(count / len(df_agentes_equipo) * 100, 2)
                })
        
        # Lista de todos los agentes del equipo
        agentes_lista = df_agentes_equipo.sort_values('puntaje_promedio', ascending=False)[
            ['agente', 'puntaje_promedio', 'total_llamadas', 'nivel_desempeno']
        ].to_dict('records')
        
        # Convertir valores numpy/pandas a tipos nativos de Python
        for agente_info in agentes_lista:
            agente_info['puntaje_promedio'] = float(agente_info['puntaje_promedio'])
            agente_info['total_llamadas'] = int(agente_info['total_llamadas'])
        
        reporte['agentes'] = agentes_lista
        
        reportes[equipo] = reporte
    
    print(f"✅ Reportes detallados generados para {len(reportes)} equipos")
    return reportes


def guardar_reportes(df_agentes, df_equipos, reportes_agentes, reportes_equipos):
    """Guarda todos los reportes en archivos."""
    print("\n" + "="*70)
    print("💾 GUARDANDO REPORTES")
    print("="*70)
    
    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. CSV de agentes
    archivo_csv_agentes = os.path.join(CARPETA_SALIDA, f"clasificacion_agentes_{timestamp}.csv")
    df_agentes.to_csv(archivo_csv_agentes, index=False, encoding='utf-8-sig')
    print(f"✅ CSV Agentes: {archivo_csv_agentes}")
    
    # 2. CSV de equipos
    archivo_csv_equipos = os.path.join(CARPETA_SALIDA, f"clasificacion_equipos_{timestamp}.csv")
    df_equipos.to_csv(archivo_csv_equipos, index=False, encoding='utf-8-sig')
    print(f"✅ CSV Equipos: {archivo_csv_equipos}")
    
    # 3. JSON detallado de agentes
    archivo_json_agentes = os.path.join(CARPETA_SALIDA, f"reportes_agentes_{timestamp}.json")
    with open(archivo_json_agentes, 'w', encoding='utf-8') as f:
        json.dump(reportes_agentes, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON Agentes: {archivo_json_agentes}")
    
    # 4. JSON detallado de equipos
    archivo_json_equipos = os.path.join(CARPETA_SALIDA, f"reportes_equipos_{timestamp}.json")
    with open(archivo_json_equipos, 'w', encoding='utf-8') as f:
        json.dump(reportes_equipos, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON Equipos: {archivo_json_equipos}")
    
    # 5. Reporte consolidado
    reporte_consolidado = {
        'fecha_generacion': datetime.now().isoformat(),
        'total_agentes': len(df_agentes),
        'total_equipos': len(df_equipos),
        'total_evaluaciones': df_agentes['total_llamadas'].sum(),
        'puntaje_promedio_global': round(df_agentes['puntaje_promedio'].mean(), 2),
        'mejor_equipo': {
            'nombre': df_equipos.iloc[0]['equipo'],
            'puntaje': round(df_equipos.iloc[0]['puntaje_promedio_equipo'], 2)
        },
        'mejor_agente': {
            'nombre': df_agentes.iloc[0]['agente'],
            'equipo': df_agentes.iloc[0]['equipo'],
            'puntaje': round(df_agentes.iloc[0]['puntaje_promedio'], 2)
        },
        'equipos': reportes_equipos,
        'agentes': reportes_agentes
    }
    
    # Convertir todo a tipos nativos de Python
    reporte_consolidado = convertir_a_tipos_nativos(reporte_consolidado)
    
    archivo_consolidado = os.path.join(CARPETA_SALIDA, f"reporte_consolidado_{timestamp}.json")
    with open(archivo_consolidado, 'w', encoding='utf-8') as f:
        json.dump(reporte_consolidado, f, ensure_ascii=False, indent=2)
    print(f"✅ Reporte Consolidado: {archivo_consolidado}")
    
    return archivo_consolidado


def main():
    """Función principal."""
    print("\n" + "="*70)
    print("🎯 SISTEMA DE CLASIFICACIÓN POR AGENTE Y EQUIPO")
    print("="*70)
    
    # 1. Cargar evaluaciones
    print(f"\n📂 Cargando evaluaciones desde: {CSV_EVALUACIONES}")
    df = pd.read_csv(CSV_EVALUACIONES)
    print(f"✅ Total de evaluaciones cargadas: {len(df)}")
    print(f"   Agentes únicos: {df['agente'].nunique()}")
    
    # 2. Analizar por agente
    df_agentes = analizar_por_agente(df)
    
    # 3. Analizar por equipo
    df_equipos = analizar_por_equipo(df_agentes)
    
    # 4. Generar reportes detallados
    reportes_agentes = generar_reporte_detallado_agente(df_agentes, df)
    reportes_equipos = generar_reporte_detallado_equipo(df_equipos, df_agentes)
    
    # 5. Guardar todo
    archivo_final = guardar_reportes(df_agentes, df_equipos, reportes_agentes, reportes_equipos)
    
    print("\n" + "="*70)
    print("✅ PROCESO COMPLETADO EXITOSAMENTE")
    print("="*70)
    print(f"\n📊 Resumen Final:")
    print(f"   - Total de agentes analizados: {len(df_agentes)}")
    print(f"   - Total de equipos analizados: {len(df_equipos)}")
    print(f"   - Total de evaluaciones procesadas: {len(df)}")
    print(f"   - Puntaje promedio global: {df_agentes['puntaje_promedio'].mean():.2f}")
    print(f"\n🏆 Mejor equipo: {df_equipos.iloc[0]['equipo']} ({df_equipos.iloc[0]['puntaje_promedio_equipo']:.2f})")
    print(f"🏆 Mejor agente: {df_agentes.iloc[0]['agente']} ({df_agentes.iloc[0]['puntaje_promedio']:.2f})")
    print(f"\n📁 Reporte consolidado guardado en:")
    print(f"   {archivo_final}")


if __name__ == "__main__":
    main()

"""
Dashboard EVA - Análisis de Calidad de Llamadas
Interfaz gráfica para presentaciones corporativas
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime
from collections import defaultdict

# Configuración de la página
st.set_page_config(
    page_title="EVA - Dashboard de Calidad",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado - LEGIBLE Y CONTRASTANTE
st.markdown("""
<style>
    /* Fondo general */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* Header principal */
    .main-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #FFFFFF;
        text-align: center;
        padding: 1.2rem;
        background: linear-gradient(135deg, #1E3A5F 0%, #3B82F6 100%);
        border-radius: 10px;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 15px rgba(30, 58, 95, 0.3);
    }
    
    /* Títulos de sección */
    .section-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1E3A5F;
        border-left: 5px solid #3B82F6;
        padding: 0.6rem 1rem;
        margin: 1.2rem 0 1rem 0;
        background-color: #FFFFFF;
        border-radius: 0 8px 8px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Sidebar - fondo oscuro con texto claro */
    [data-testid="stSidebar"] {
        background-color: #1E293B !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #F1F5F9 !important;
    }
    
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #60A5FA !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stSidebar"] p {
        font-size: 0.95rem !important;
    }
    
    /* Métricas */
    [data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 5px solid #3B82F6;
    }
    
    [data-testid="stMetric"] label {
        color: #1E3A5F !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #0F172A !important;
        font-weight: 700 !important;
        font-size: 1.6rem !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #FFFFFF;
        padding: 8px;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.08);
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #F1F5F9;
        border-radius: 6px;
        padding: 8px 16px;
        color: #1E293B;
        font-weight: 600;
        font-size: 0.9rem;
        border: 1px solid #CBD5E1;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #DBEAFE;
        border-color: #3B82F6;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3B82F6 !important;
        color: #FFFFFF !important;
        font-weight: 700;
        border: none !important;
    }
    
    /* DataFrames */
    .stDataFrame {
        border: 1px solid #CBD5E1 !important;
        border-radius: 6px;
    }
    
    /* Selectbox y inputs */
    .stSelectbox > div > div {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        border: 2px solid #CBD5E1 !important;
        font-size: 0.95rem;
    }
    
    .stMultiSelect > div > div {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        border: 2px solid #CBD5E1 !important;
    }
    
    /* Textos generales más legibles */
    .stMarkdown p, .stText {
        color: #1E293B;
        font-size: 0.95rem;
    }
    
    /* MEJORAS DE LEGIBILIDAD PARA MARKDOWN */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5 {
        color: #1E3A5F !important;
        font-weight: 700 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.75rem !important;
    }
    
    .stMarkdown h2 {
        font-size: 1.4rem !important;
        border-bottom: 2px solid #3B82F6;
        padding-bottom: 0.5rem;
    }
    
    .stMarkdown h3 {
        font-size: 1.15rem !important;
        color: #2563EB !important;
    }
    
    .stMarkdown ul, .stMarkdown ol {
        color: #334155 !important;
        line-height: 1.8 !important;
    }
    
    .stMarkdown li {
        margin-bottom: 0.5rem !important;
    }
    
    .stMarkdown strong {
        color: #0F172A !important;
        font-weight: 700 !important;
    }
    
    /* Tablas en Markdown */
    .stMarkdown table {
        width: 100% !important;
        border-collapse: collapse !important;
        margin: 1rem 0 !important;
        font-size: 0.9rem !important;
    }
    
    .stMarkdown table th {
        background-color: #1E3A5F !important;
        color: #FFFFFF !important;
        padding: 12px !important;
        text-align: left !important;
        font-weight: 600 !important;
        border: 1px solid #334155 !important;
    }
    
    .stMarkdown table td {
        padding: 10px 12px !important;
        border: 1px solid #CBD5E1 !important;
        color: #1E293B !important;
        background-color: #FFFFFF !important;
    }
    
    .stMarkdown table tr:nth-child(even) td {
        background-color: #F8FAFC !important;
    }
    
    .stMarkdown table tr:hover td {
        background-color: #EFF6FF !important;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background-color: #F1F5F9 !important;
        color: #1E293B !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }
    
    .streamlit-expanderContent {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 0 0 8px 8px !important;
        padding: 1rem !important;
    }
    
    /* Radio buttons sidebar */
    .stRadio > label {
        color: #F1F5F9 !important;
        font-weight: 600;
        font-size: 0.95rem !important;
    }
    
    /* Logo EVA en sidebar */
    .eva-logo-container {
        text-align: center;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }
    
    .eva-logo-container img {
        max-width: 80px;
    }
    
    .eva-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #60A5FA !important;
        text-align: center;
        margin-top: 0.5rem;
    }
    
    .eva-subtitle {
        font-size: 0.85rem;
        color: #94A3B8 !important;
        text-align: center;
        margin-top: -0.3rem;
    }
    
    /* Plotly charts container */
    .stPlotlyChart {
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        border: 1px solid #E2E8F0;
    }
    
    /* Botones */
    .stButton > button {
        font-size: 0.85rem;
        padding: 0.4rem 0.8rem;
        font-weight: 600;
        background-color: #3B82F6 !important;
        color: #FFFFFF !important;
        border: none !important;
    }
    
    .stButton > button:hover {
        background-color: #2563EB !important;
    }
    
    /* Info boxes y warnings más legibles */
    .stAlert {
        border-radius: 8px !important;
    }
    
    /* Cards personalizadas */
    .coach-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border: 1px solid #E2E8F0;
        margin-bottom: 1rem;
    }
    
    .coach-card h3 {
        color: #1E3A5F !important;
        margin-bottom: 1rem;
    }
    
    /* Badges/Pills */
    .badge-success {
        background-color: #10B981;
        color: #FFFFFF;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .badge-warning {
        background-color: #F59E0B;
        color: #FFFFFF;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .badge-danger {
        background-color: #EF4444;
        color: #FFFFFF;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Paleta de colores - ALTO CONTRASTE Y MODERNA
COLORS = {
    'primary': '#3B82F6',
    'secondary': '#60A5FA',
    'success': '#10B981',
    'warning': '#F59E0B',
    'danger': '#EF4444',
    'info': '#06B6D4',
    'light': '#F8FAFC',
    'dark': '#1E293B',
    'text': '#1E293B',
    'card_bg': '#FFFFFF',
    'border': '#CBD5E1',
    'gradient': ['#1E3A5F', '#3B82F6', '#60A5FA', '#93C5FD', '#DBEAFE']
}

# Colores para calificaciones - MUY distinguibles
CALIFICACION_COLORS = {
    'Excelente': '#059669',    # Verde esmeralda
    'Bueno': '#10B981',        # Verde medio
    'Regular': '#F59E0B',      # Ámbar
    'Deficiente': '#F97316',   # Naranja
    'Sin cierre': '#EF4444'    # Rojo
}


def agrupar_valores_pequenos(values, names, umbral=4):
    """
    Agrupa valores menores al umbral% en 'Otros' y retorna info del hover
    """
    total = sum(values)
    if total == 0:
        return values, names, {}
    
    nuevos_values = []
    nuevos_names = []
    otros_values = []
    otros_names = []
    otros_desglose = {}
    
    for v, n in zip(values, names):
        porcentaje = (v / total) * 100
        if porcentaje < umbral:
            otros_values.append(v)
            otros_names.append(n)
            otros_desglose[n] = {'cantidad': v, 'porcentaje': round(porcentaje, 1)}
        else:
            nuevos_values.append(v)
            nuevos_names.append(n)
    
    # Si hay valores pequeños, agruparlos en "Otros"
    if otros_values:
        nuevos_values.append(sum(otros_values))
        nuevos_names.append('Otros')
    
    return nuevos_values, nuevos_names, otros_desglose


def crear_pie_chart_expandible(values, names, titulo, colors, key_id, height_normal=320):
    """
    Crea un gráfico de pie limpio con leyenda lateral y opción de popup
    """
    # Agrupar valores pequeños
    values_agrupados, names_agrupados, otros_info = agrupar_valores_pequenos(list(values), list(names))
    total = sum(values_agrupados)
    
    # Crear texto de hover personalizado
    def crear_hover_text(names_list, values_list, otros_desglose):
        hover_texts = []
        for n, v in zip(names_list, values_list):
            pct = (v / total) * 100 if total > 0 else 0
            if n == 'Otros' and otros_desglose:
                desglose = "<br>".join([f"• {k}: {d['cantidad']} ({d['porcentaje']}%)" 
                                       for k, d in otros_desglose.items()])
                hover_texts.append(f"<b>Otros</b><br>Total: {v} ({pct:.1f}%)<br><b>Desglose:</b><br>{desglose}")
            else:
                hover_texts.append(f"<b>{n}</b><br>Cantidad: {v}<br>Porcentaje: {pct:.1f}%")
        return hover_texts
    
    hover_text = crear_hover_text(names_agrupados, values_agrupados, otros_info)
    
    # Ajustar colores
    cols = list(colors)
    if 'Otros' in names_agrupados:
        cols = cols[:len(names_agrupados)-1] + ['#7F8C8D']
    
    # Gráfico limpio - sin texto externo, solo leyenda
    fig = go.Figure(data=[go.Pie(
        values=values_agrupados,
        labels=names_agrupados,
        hole=0.4,
        marker=dict(
            colors=cols[:len(names_agrupados)],
            line=dict(color='#FFFFFF', width=2)
        ),
        textposition='inside',
        textinfo='percent',
        textfont=dict(size=12, color='#FFFFFF'),
        hovertemplate='%{customdata}<extra></extra>',
        customdata=hover_text
    )])
    
    fig.update_layout(
        height=height_normal,
        margin=dict(t=10, b=10, l=10, r=120),
        paper_bgcolor='#FFFFFF',
        font=dict(color='#2C3E50', size=12),
        legend=dict(
            font=dict(size=11, color='#2C3E50'),
            bgcolor='rgba(255,255,255,0.95)',
            bordercolor='#BDC3C7',
            borderwidth=1,
            orientation='v',
            yanchor='middle',
            y=0.5,
            xanchor='left',
            x=1.02,
            itemwidth=30
        ),
        hoverlabel=dict(
            bgcolor='#FFFFFF',
            bordercolor='#1A5276',
            font=dict(size=12, color='#2C3E50')
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Botón para popup
    if st.button(f"🔍 Ver detalle", key=f"btn_{key_id}"):
        mostrar_popup_grafico(titulo, values, names, colors, otros_info, key_id)


@st.dialog("📊 Vista Detallada", width="large")
def mostrar_popup_grafico(titulo, values, names, colors, otros_info, key_id):
    """Muestra el gráfico en un popup modal con detalles"""
    st.markdown(f"### {titulo}")
    
    # Agrupar valores pequeños
    values_agrupados, names_agrupados, otros_desglose = agrupar_valores_pequenos(list(values), list(names))
    total = sum(values_agrupados)
    
    # Crear hover text
    hover_texts = []
    for n, v in zip(names_agrupados, values_agrupados):
        pct = (v / total) * 100 if total > 0 else 0
        if n == 'Otros' and otros_desglose:
            desglose = "<br>".join([f"• {k}: {d['cantidad']} ({d['porcentaje']}%)" 
                                   for k, d in otros_desglose.items()])
            hover_texts.append(f"<b>Otros</b><br>Total: {v} ({pct:.1f}%)<br><b>Desglose:</b><br>{desglose}")
        else:
            hover_texts.append(f"<b>{n}</b><br>Cantidad: {v}<br>Porcentaje: {pct:.1f}%")
    
    # Colores
    cols = list(colors)
    if 'Otros' in names_agrupados:
        cols = cols[:len(names_agrupados)-1] + ['#7F8C8D']
    
    # Layout en dos columnas: gráfico y tabla
    col_grafico, col_tabla = st.columns([3, 2])
    
    with col_grafico:
        fig = go.Figure(data=[go.Pie(
            values=values_agrupados,
            labels=names_agrupados,
            hole=0.4,
            marker=dict(
                colors=cols[:len(names_agrupados)],
                line=dict(color='#FFFFFF', width=2)
            ),
            textposition='inside',
            textinfo='percent',
            textfont=dict(size=13, color='#FFFFFF'),
            hovertemplate='%{customdata}<extra></extra>',
            customdata=hover_texts
        )])
        
        fig.update_layout(
            height=380,
            margin=dict(t=15, b=15, l=15, r=15),
            paper_bgcolor='#FFFFFF',
            font=dict(color='#2C3E50', size=12),
            legend=dict(
                font=dict(size=12, color='#2C3E50'),
                bgcolor='#FFFFFF',
                bordercolor='#BDC3C7',
                borderwidth=1
            ),
            hoverlabel=dict(
                bgcolor='#FFFFFF',
                bordercolor='#1A5276',
                font=dict(size=12, color='#2C3E50')
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col_tabla:
        st.markdown("**📋 Detalle de datos:**")
        
        df_datos = pd.DataFrame({
            'Categoría': list(names),
            'Cantidad': list(values),
            '%': [f"{(v/sum(values))*100:.1f}%" for v in values]
        }).sort_values('Cantidad', ascending=False)
        
        st.dataframe(df_datos, use_container_width=True, hide_index=True, height=280)
        
        # Si hay "Otros", mostrar desglose
        if otros_desglose:
            st.markdown("**📌 Desglose 'Otros':**")
            df_otros = pd.DataFrame([
                {'Categoría': k, 'Cant.': v['cantidad'], '%': f"{v['porcentaje']}%"}
                for k, v in otros_desglose.items()
            ])
            st.dataframe(df_otros, use_container_width=True, hide_index=True)


# Directorio base del script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_data(ttl=300)  # Cache por 5 minutos
def cargar_datos():
    """Carga todos los datos necesarios para el dashboard"""
    datos = {}
    
    # Cargar transcripciones procesadas
    carpeta = os.path.join(BASE_DIR, "total_transcripciones/procesados")
    if os.path.exists(carpeta):
        transcripciones = []
        for archivo in os.listdir(carpeta):
            if archivo.endswith('.json'):
                with open(os.path.join(carpeta, archivo), 'r', encoding='utf-8') as f:
                    transcripciones.append(json.load(f))
        datos['transcripciones'] = transcripciones
    
    # Cargar resumen de cierres
    ruta_cierres = os.path.join(BASE_DIR, 'reportes/cierres_comerciales/resumen_cierres.json')
    if os.path.exists(ruta_cierres):
        with open(ruta_cierres, 'r', encoding='utf-8') as f:
            datos['cierres'] = json.load(f)
    
    # Cargar CSV de cierres
    ruta = os.path.join(BASE_DIR, 'reportes/cierres_comerciales/cierres_comerciales.csv')
    if os.path.exists(ruta):
        datos['cierres_df'] = pd.read_csv(ruta, sep=';')
    
    # Cargar resumen de planes
    ruta = os.path.join(BASE_DIR, 'reportes/planes/resumen_planes.json')
    if os.path.exists(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            datos['planes'] = json.load(f)
    
    # Cargar resumen de quejas
    ruta = os.path.join(BASE_DIR, 'reportes/quejas/resumen_quejas.json')
    if os.path.exists(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            datos['quejas'] = json.load(f)
    
    # Cargar CSV de quejas
    ruta = os.path.join(BASE_DIR, 'reportes/quejas/quejas_no_resueltas.csv')
    if os.path.exists(ruta):
        datos['quejas_df'] = pd.read_csv(ruta)
    
    # Cargar análisis integral
    ruta = os.path.join(BASE_DIR, 'reportes/analisis_integral/resumen_integral.json')
    if os.path.exists(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            datos['integral'] = json.load(f)
    
    # Cargar CSV integral
    ruta = os.path.join(BASE_DIR, 'reportes/analisis_integral/analisis_integral.csv')
    if os.path.exists(ruta):
        datos['integral_df'] = pd.read_csv(ruta)
    
    # Cargar métricas por agente integral
    ruta = os.path.join(BASE_DIR, 'reportes/analisis_integral/metricas_por_agente.csv')
    if os.path.exists(ruta):
        datos['metricas_agentes_df'] = pd.read_csv(ruta)
    
    # Cargar clasificación completa
    ruta = os.path.join(BASE_DIR, 'reportes/clasificacion_completa/resumen_clasificacion.json')
    if os.path.exists(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            datos['clasificacion'] = json.load(f)
    
    # Cargar CSV clasificación completa
    ruta = os.path.join(BASE_DIR, 'reportes/clasificacion_completa/clasificacion_completa.csv')
    if os.path.exists(ruta):
        datos['clasificacion_df'] = pd.read_csv(ruta)
    
    # Cargar clasificación por agente
    ruta = os.path.join(BASE_DIR, 'reportes/clasificacion_completa/clasificacion_por_agente.csv')
    if os.path.exists(ruta):
        datos['clasificacion_agentes_df'] = pd.read_csv(ruta)
    
    # Cargar evaluaciones Gemini
    ruta = os.path.join(BASE_DIR, 'reportes/evaluaciones_gemini.csv')
    if os.path.exists(ruta):
        datos['evaluaciones_gemini_df'] = pd.read_csv(ruta)
    
    # Cargar coaching de vendedores
    # Cargar coaching de vendedores
    ruta = os.path.join(BASE_DIR, 'reportes/coaching_vendedores/coaching_completo.json')
    if os.path.exists(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            coaching_list = json.load(f)
            # Convertir lista a diccionario por agente
            datos['coaching'] = {item['agente']: item for item in coaching_list}
    
    return datos


def crear_df_llamadas(transcripciones):
    """Crea un DataFrame con la información de las llamadas"""
    filas = []
    for t in transcripciones:
        info = t.get('info_llamada', {})
        calidad = t.get('analisis_calidad', {})
        productos = t.get('productos_ofrecidos', {})
        
        fila = {
            'id': info.get('id_interaccion', ''),
            'fecha': info.get('fecha_llamada', ''),
            'agente': info.get('agente', {}).get('nombre', 'desconocido'),
            'duracion': info.get('tiempos', {}).get('talking_time', 0),
            'tipificacion': info.get('resultado', {}).get('tipificacion', ''),
            'tipo': info.get('resultado', {}).get('tipos_tipificacion', ''),
            'score_calidad': calidad.get('score_calidad', 0),
            'tiene_saludo': calidad.get('tiene_saludo_correcto', False),
            'tiene_cierre': calidad.get('tiene_cierre_correcto', False),
            'planes': ', '.join(productos.get('planes_ofrecidos', [])),
            'primer_plan': productos.get('primer_plan', ''),
        }
        filas.append(fila)
    
    df = pd.DataFrame(filas)
    if 'fecha' in df.columns and len(df) > 0:
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
        df['dia'] = df['fecha'].dt.date
        df['hora'] = df['fecha'].dt.hour
    return df


def pagina_resumen_ejecutivo(datos, df):
    """Página de resumen ejecutivo"""
    st.markdown('<div class="main-header">📊 Dashboard EVA - Resumen Ejecutivo</div>', unsafe_allow_html=True)
    
    # Fecha del análisis
    st.markdown(f"**Última actualización:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    # Métricas principales
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_llamadas = len(df)
    ventas = len(df[df['tipificacion'] == 'Venta'])
    tasa_conversion = (ventas / total_llamadas * 100) if total_llamadas > 0 else 0
    promedio_calidad = df['score_calidad'].mean() if len(df) > 0 else 0
    promedio_duracion = df['duracion'].mean() / 60 if len(df) > 0 else 0
    
    with col1:
        st.metric("📞 Total Llamadas", f"{total_llamadas:,}")
    with col2:
        st.metric("✅ Ventas", f"{ventas:,}")
    with col3:
        st.metric("📈 Tasa Conversión", f"{tasa_conversion:.1f}%")
    with col4:
        st.metric("⭐ Calidad Promedio", f"{promedio_calidad:.1f}/100")
    with col5:
        st.metric("⏱️ Duración Promedio", f"{promedio_duracion:.1f} min")
    
    st.markdown("---")
    
    # Gráficos principales
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<p class="section-header">📊 Distribución por Tipificación</p>', unsafe_allow_html=True)
        tipificacion_counts = df['tipificacion'].value_counts()
        crear_pie_chart_expandible(
            values=list(tipificacion_counts.values),
            names=list(tipificacion_counts.index),
            titulo="Distribución por Tipificación",
            colors=['#1A5276', '#145A32', '#B7950B', '#922B21', '#6C3483', '#0E6655'],
            key_id="tipificacion"
        )
    
    with col2:
        st.markdown('<p class="section-header">📈 Llamadas por Día</p>', unsafe_allow_html=True)
        if 'dia' in df.columns:
            llamadas_dia = df.groupby('dia').size().reset_index(name='llamadas')
            fig = px.bar(
                llamadas_dia, x='dia', y='llamadas',
                color_discrete_sequence=['#3B82F6']
            )
            fig.update_layout(
                height=300, 
                xaxis_title="Fecha",
                yaxis_title="Llamadas",
                margin=dict(t=20, b=40, l=50, r=20),
                paper_bgcolor='#FFFFFF',
                plot_bgcolor='#FAFBFC',
                font=dict(color='#2C3E50', size=12)
            )
            fig.update_xaxes(
                gridcolor='#E5E8E8', 
                tickfont=dict(size=9, color='#2C3E50'),
                title_font=dict(size=13, color='#2C3E50')
            )
            fig.update_yaxes(
                gridcolor='#E5E8E8', 
                tickfont=dict(size=9, color='#2C3E50'),
                title_font=dict(size=13, color='#2C3E50')
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Resultados de las llamadas
    st.markdown('<p class="section-header">🎯 Resultados de las Llamadas</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    exitosas = len(df[df['tipo'] == 'Exitoso'])
    no_exitosas = len(df[df['tipo'] == 'No Exitoso'])
    sin_tipo = total_llamadas - exitosas - no_exitosas
    
    with col1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=exitosas,
            title={'text': "Exitosas", 'font': {'color': '#2C3E50', 'size': 13}},
            number={'font': {'color': '#27AE60', 'size': 24}},
            gauge={
                'axis': {'range': [0, total_llamadas], 'tickcolor': '#BDC3C7', 'tickfont': {'size': 9, 'color': '#7F8C8D'}},
                'bar': {'color': '#27AE60', 'thickness': 0.7},
                'bgcolor': '#EAFAF1',
                'bordercolor': '#D5D8DC',
                'borderwidth': 1,
                'steps': [
                    {'range': [0, total_llamadas], 'color': '#E8F6F3'}
                ],
            }
        ))
        fig.update_layout(height=180, margin=dict(t=50, b=10), paper_bgcolor='#FFFFFF')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=no_exitosas,
            title={'text': "No Exitosas", 'font': {'color': '#2C3E50', 'size': 13}},
            number={'font': {'color': '#E74C3C', 'size': 24}},
            gauge={
                'axis': {'range': [0, total_llamadas], 'tickcolor': '#BDC3C7', 'tickfont': {'size': 9, 'color': '#7F8C8D'}},
                'bar': {'color': '#E74C3C', 'thickness': 0.7},
                'bgcolor': '#FDEDEC',
                'bordercolor': '#D5D8DC',
                'borderwidth': 1,
                'steps': [
                    {'range': [0, total_llamadas], 'color': '#FADBD8'}
                ],
            }
        ))
        fig.update_layout(height=180, margin=dict(t=50, b=10), paper_bgcolor='#FFFFFF')
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=sin_tipo,
            title={'text': "Sin Clasificar", 'font': {'color': '#2C3E50', 'size': 13}},
            number={'font': {'color': '#F39C12', 'size': 24}},
            gauge={
                'axis': {'range': [0, total_llamadas], 'tickcolor': '#BDC3C7', 'tickfont': {'size': 9, 'color': '#7F8C8D'}},
                'bar': {'color': '#F39C12', 'thickness': 0.7},
                'bgcolor': '#FEF9E7',
                'bordercolor': '#D5D8DC',
                'borderwidth': 1,
                'steps': [
                    {'range': [0, total_llamadas], 'color': '#FCF3CF'}
                ],
            }
        ))
        fig.update_layout(height=180, margin=dict(t=50, b=10), paper_bgcolor='#FFFFFF')
        st.plotly_chart(fig, use_container_width=True)


def mostrar_proximamente(titulo, icono="🚧"):
    """Muestra un cartel elegante de Próximamente"""
    st.markdown(f'<div class="main-header">{titulo}</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 80px 40px;
        margin: 40px auto;
        max-width: 600px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    ">
        <div style="font-size: 80px; margin-bottom: 20px;">🚀</div>
        <h1 style="
            color: white;
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0 0 15px 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        ">Próximamente</h1>
        <p style="
            color: rgba(255,255,255,0.9);
            font-size: 1.1rem;
            text-align: center;
            margin: 0;
            max-width: 400px;
            line-height: 1.6;
        ">Estamos trabajando en esta funcionalidad.<br>¡Pronto estará disponible!</p>
        <div style="
            margin-top: 30px;
            padding: 12px 30px;
            background: rgba(255,255,255,0.2);
            border-radius: 30px;
            color: white;
            font-weight: 500;
            backdrop-filter: blur(10px);
        ">⏳ En desarrollo</div>
    </div>
    """, unsafe_allow_html=True)


def pagina_cierres_comerciales(datos):
    """Página de análisis de cierres comerciales"""
    mostrar_proximamente("📋 Análisis de Cierres Comerciales")


def pagina_planes_ofrecidos(datos, df):
    """Página de análisis de planes ofrecidos, fibra y promociones"""
    st.markdown('<div class="main-header">📱 Análisis de Planes, Fibra y Promociones</div>', unsafe_allow_html=True)
    
    if 'planes' not in datos:
        st.warning("⚠️ No hay datos de planes disponibles.")
        return
    
    # Cargar nombres de vendedores
    listado_vendedores = {}
    try:
        df_listado = pd.read_csv('LISTADO-DE-VENDEDORES.csv', header=0)
        for _, row in df_listado.iterrows():
            usuario = str(row.iloc[0]).strip().lower().replace('\t', '').replace(' ', '')
            nombre = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
            if usuario and nombre and usuario != 'usuario':
                listado_vendedores[usuario] = nombre.title()
    except:
        pass
    
    def obtener_nombre_agente(agente_id):
        agente_normalizado = agente_id.lower().replace(' ', '').replace('_', '')
        return listado_vendedores.get(agente_normalizado, agente_id)
    
    planes = datos['planes']
    stats = planes.get('estadisticas', {})
    total_llamadas = planes.get('total_llamadas', 0)
    
    # =========================================================================
    # SECCIÓN 1: PLANES DE PORTA
    # =========================================================================
    st.markdown('<p class="section-header">📱 Planes de Porta (4GB, 8GB, 15GB, 30GB)</p>', unsafe_allow_html=True)
    
    planes_stats = stats.get('planes', {})
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📞 Total Llamadas", f"{total_llamadas:,}")
    with col2:
        con_plan = planes_stats.get('con_plan', 0)
        pct = planes_stats.get('porcentaje_con_plan', 0)
        st.metric("✅ Con Plan Ofrecido", f"{con_plan:,}", f"{pct:.1f}%")
    with col3:
        sin_plan = planes_stats.get('sin_plan', 0)
        pct_sin = 100 - pct if pct else 0
        st.metric("❌ Sin Plan Ofrecido", f"{sin_plan:,}", f"{pct_sin:.1f}%", delta_color="inverse")
    with col4:
        # Plan más usado como primer ofrecimiento
        primer_plan_conteo = stats.get('primer_plan_conteo', {})
        if primer_plan_conteo:
            top_plan = max(primer_plan_conteo, key=primer_plan_conteo.get)
            st.metric("🥇 Primer Plan Más Usado", top_plan.upper(), f"{primer_plan_conteo[top_plan]} veces")
    
    # Gráficos de planes
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Planes Más Ofrecidos**")
        
        planes_conteo = stats.get('planes_conteo', {})
        if planes_conteo:
            orden = ['4gb', '8gb', '15gb', '30gb']
            planes_ord = {k.upper(): planes_conteo.get(k, 0) for k in orden if k in planes_conteo}
            
            fig = px.bar(
                x=list(planes_ord.keys()),
                y=list(planes_ord.values()),
                color=list(planes_ord.values()),
                color_continuous_scale=[[0, '#93C5FD'], [0.5, '#3B82F6'], [1, '#1E3A5F']],
                labels={'x': 'Plan', 'y': 'Veces Ofrecido'},
                text=list(planes_ord.values())
            )
            fig.update_traces(textposition='outside', textfont=dict(size=11, color='#2C3E50'))
            fig.update_layout(
                height=280,
                showlegend=False,
                margin=dict(t=20, b=40, l=50, r=20),
                paper_bgcolor='#FFFFFF',
                plot_bgcolor='#FAFBFC',
                font=dict(color='#2C3E50', size=12)
            )
            fig.update_xaxes(gridcolor='#E5E8E8', tickfont=dict(size=11, color='#2C3E50'))
            fig.update_yaxes(gridcolor='#E5E8E8', tickfont=dict(size=10, color='#2C3E50'))
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**🥇 Primer Plan Ofrecido (Estrategia Inicial)**")
        
        primer_plan = stats.get('primer_plan_conteo', {})
        if primer_plan:
            # Ordenar
            orden = ['4gb', '8gb', '15gb', '30gb']
            primer_ord = {k.upper(): primer_plan.get(k, 0) for k in orden if k in primer_plan}
            
            fig = px.pie(
                values=list(primer_ord.values()),
                names=list(primer_ord.keys()),
                color_discrete_sequence=['#1E3A5F', '#10B981', '#F59E0B', '#EF4444']
            )
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                textfont=dict(size=12, color='#FFFFFF')
            )
            fig.update_layout(
                height=280,
                showlegend=True,
                legend=dict(font=dict(size=11, color='#2C3E50')),
                margin=dict(t=20, b=20, l=20, r=120),
                paper_bgcolor='#FFFFFF'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # =========================================================================
    # SECCIÓN 2: FIBRA (INTERNET HOGAR)
    # =========================================================================
    st.markdown('<p class="section-header">🏠 Fibra (Internet Hogar)</p>', unsafe_allow_html=True)
    
    fibra_stats = stats.get('fibra', {})
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ofrece = fibra_stats.get('ofrece', 0)
        pct_ofrece = fibra_stats.get('porcentaje_ofrece', 0)
        st.metric("✅ Ofrece Fibra", f"{ofrece:,}", f"{pct_ofrece:.1f}%")
    with col2:
        no_ofrece = fibra_stats.get('no_ofrece', 0)
        pct_no = 100 - pct_ofrece if pct_ofrece else 0
        st.metric("❌ NO Ofrece Fibra", f"{no_ofrece:,}", f"-{pct_no:.1f}%", delta_color="inverse")
    with col3:
        # Indicador visual
        if pct_ofrece < 30:
            st.error(f"⚠️ Solo {pct_ofrece:.1f}% ofrece Fibra - Área de mejora crítica")
        elif pct_ofrece < 50:
            st.warning(f"⚠️ {pct_ofrece:.1f}% ofrece Fibra - Necesita mejorar")
        else:
            st.success(f"✅ {pct_ofrece:.1f}% ofrece Fibra - Buen desempeño")
    
    # Gráfico de Fibra
    col1, col2 = st.columns(2)
    
    with col1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=pct_ofrece,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "% Ofrece Fibra", 'font': {'size': 14, 'color': '#2C3E50'}},
            delta={'reference': 50, 'increasing': {'color': "#27AE60"}, 'decreasing': {'color': "#E74C3C"}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#2C3E50"},
                'bar': {'color': "#3B82F6"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "#E5E8E8",
                'steps': [
                    {'range': [0, 30], 'color': '#FADBD8'},
                    {'range': [30, 50], 'color': '#FCF3CF'},
                    {'range': [50, 100], 'color': '#D5F5E3'}
                ],
                'threshold': {
                    'line': {'color': "#E74C3C", 'width': 4},
                    'thickness': 0.75,
                    'value': 50
                }
            }
        ))
        fig.update_layout(
            height=220,
            margin=dict(t=40, b=20, l=30, r=30),
            paper_bgcolor='#FFFFFF'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top agentes que NO ofrecen fibra
        fibra_por_agente = planes.get('fibra_por_agente', {})
        if fibra_por_agente:
            agentes_sin_fibra = []
            for agente, data in fibra_por_agente.items():
                total = data.get('ofrece', 0) + data.get('no_ofrece', 0)
                if total >= 5:  # Solo agentes con al menos 5 llamadas
                    pct = data.get('no_ofrece', 0) / total * 100 if total > 0 else 0
                    nombre_real = obtener_nombre_agente(agente)
                    agentes_sin_fibra.append({'Agente': nombre_real, 'Sin Fibra %': round(pct, 1), 'Total': total})
            
            if agentes_sin_fibra:
                df_sin_fibra = pd.DataFrame(agentes_sin_fibra)
                df_sin_fibra = df_sin_fibra.sort_values('Sin Fibra %', ascending=False).head(10)
                st.markdown("**🚨 Agentes que menos ofrecen Fibra:**")
                st.dataframe(df_sin_fibra, use_container_width=True, hide_index=True, height=180)
    
    st.markdown("---")
    
    # =========================================================================
    # SECCIÓN 3: PROMOCIONES
    # =========================================================================
    st.markdown('<p class="section-header">🎁 Promociones (80% días 13-16/01)</p>', unsafe_allow_html=True)
    
    promo_stats = stats.get('promociones', {})
    col1, col2, col3, col4 = st.columns(4)
    
    dias_promo_total = promo_stats.get('dias_promo_total', 0)
    menciona = promo_stats.get('dias_promo_menciona', 0)
    no_menciona = promo_stats.get('dias_promo_no_menciona', 0)
    
    with col1:
        st.metric("📅 Llamadas en Días Promo", f"{dias_promo_total:,}")
    with col2:
        pct_menciona = menciona / dias_promo_total * 100 if dias_promo_total > 0 else 0
        st.metric("✅ Menciona Promo", f"{menciona:,}", f"{pct_menciona:.1f}%")
    with col3:
        pct_no = 100 - pct_menciona if pct_menciona else 0
        st.metric("❌ NO Menciona Promo", f"{no_menciona:,}", f"-{pct_no:.1f}%", delta_color="inverse")
    with col4:
        menciona_total = promo_stats.get('menciona_promo', 0)
        pct_total = menciona_total / total_llamadas * 100 if total_llamadas > 0 else 0
        st.metric("📣 Menciona Promo (Total)", f"{menciona_total:,}", f"{pct_total:.1f}%")
    
    # Gráfico de promociones
    col1, col2 = st.columns(2)
    
    with col1:
        if dias_promo_total > 0:
            fig = go.Figure(data=[
                go.Bar(name='Menciona Promo', x=['Días de Promo'], y=[menciona], marker_color='#27AE60', 
                       text=[f'{menciona} ({pct_menciona:.1f}%)'], textposition='inside', textfont=dict(color='#FFFFFF', size=12)),
                go.Bar(name='NO Menciona', x=['Días de Promo'], y=[no_menciona], marker_color='#E74C3C',
                       text=[f'{no_menciona} ({pct_no:.1f}%)'], textposition='inside', textfont=dict(color='#FFFFFF', size=12))
            ])
            fig.update_layout(
                barmode='stack',
                height=250,
                title={'text': 'Cumplimiento en Días de Promoción', 'font': {'size': 13, 'color': '#2C3E50'}},
                margin=dict(t=50, b=30, l=40, r=20),
                paper_bgcolor='#FFFFFF',
                plot_bgcolor='#FAFBFC',
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5, font=dict(size=10))
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Indicador visual con mejor legibilidad
        if pct_menciona < 50:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #DC2626 0%, #B91C1C 100%); 
                        padding: 20px; border-radius: 12px; color: white; 
                        box-shadow: 0 4px 15px rgba(220, 38, 38, 0.3);">
                <h3 style="margin: 0 0 10px 0; color: white;">🚨 Alerta Crítica</h3>
                <p style="margin: 0; font-size: 1.1rem; color: white;">
                    Solo <strong>{pct_menciona:.1f}%</strong> de las llamadas en días de promoción mencionan el descuento del 80%.
                </p>
                <p style="margin: 10px 0 0 0; color: rgba(255,255,255,0.9);">
                    <strong>{no_menciona}</strong> llamadas perdieron la oportunidad de ofrecer la promo.
                </p>
            </div>
            """, unsafe_allow_html=True)
        elif pct_menciona < 70:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); 
                        padding: 20px; border-radius: 12px; color: #1E293B; 
                        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);">
                <h3 style="margin: 0 0 10px 0; color: #1E293B;">⚠️ Área de Mejora</h3>
                <p style="margin: 0; font-size: 1.1rem; color: #1E293B;">
                    <strong>{pct_menciona:.1f}%</strong> de las llamadas en días de promoción mencionan el descuento.
                </p>
                <p style="margin: 10px 0 0 0; color: #374151;">
                    Todavía hay <strong>{no_menciona}</strong> llamadas que no ofrecieron la promo.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%); 
                        padding: 20px; border-radius: 12px; color: white; 
                        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);">
                <h3 style="margin: 0 0 10px 0; color: white;">✅ Buen Desempeño</h3>
                <p style="margin: 0; font-size: 1.1rem; color: white;">
                    <strong>{pct_menciona:.1f}%</strong> de las llamadas en días de promoción mencionan el descuento del 80%.
                </p>
            </div>
            """, unsafe_allow_html=True)


def pagina_coaching_vendedores(datos):
    """Página de Coaching IA personalizado para cada vendedor"""
    st.markdown('<div class="main-header">🎯 Coaching IA para Vendedores</div>', unsafe_allow_html=True)
    
    # Cargar listado de vendedores desde CSV
    listado_vendedores = {}
    equipos_vendedores = {}
    try:
        df_listado = pd.read_csv('LISTADO-DE-VENDEDORES.csv', header=0)
        # La estructura es: Usuario, Nombre, Equipo
        for _, row in df_listado.iterrows():
            usuario = str(row.iloc[0]).strip().lower().replace('\t', '')  # Normalizar ID
            nombre = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
            equipo = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else "Sin Equipo"
            
            if usuario and nombre and usuario != 'usuario':
                listado_vendedores[usuario] = nombre.title()  # Capitalizar nombre
                if equipo not in equipos_vendedores:
                    equipos_vendedores[equipo] = []
                equipos_vendedores[equipo].append(usuario)
    except Exception as e:
        st.warning(f"No se pudo cargar el listado de vendedores: {e}")
    
    def obtener_nombre_vendedor(agente_id):
        """Convierte ID de agente a nombre real"""
        agente_normalizado = agente_id.lower().replace(' ', '').replace('_', '')
        return listado_vendedores.get(agente_normalizado, agente_id)
    
    def obtener_equipo_vendedor(agente_id):
        """Obtiene el equipo del vendedor"""
        agente_normalizado = agente_id.lower().replace(' ', '').replace('_', '')
        for equipo, vendedores in equipos_vendedores.items():
            if agente_normalizado in vendedores:
                return equipo
        return "Sin Equipo"
    
    # Verificar si hay datos de coaching
    if 'coaching' not in datos or not datos['coaching']:
        st.warning("⚠️ No hay datos de coaching disponibles actualmente.")
        st.info("💡 Los datos de coaching se generarán próximamente.")
        return
    
    coaching_data = datos['coaching']
    
    # Obtener lista de agentes con coaching
    agentes_coaching = list(coaching_data.keys())
    
    if not agentes_coaching:
        st.warning("No hay agentes con coaching generado.")
        return
    
    # Información general del coaching
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1E3A5F 0%, #3B82F6 100%); 
                padding: 20px; border-radius: 15px; margin-bottom: 25px; color: white;
                box-shadow: 0 4px 15px rgba(30, 58, 95, 0.3);'>
        <h3 style='margin:0; color: #FFFFFF; font-weight: 700;'>🤖 Coaching Personalizado con Inteligencia Artificial</h3>
        <p style='margin: 10px 0 0 0; color: #E0E7FF;'>
            Análisis exhaustivo generado por IA actuando como <strong style='color: #FFFFFF;'>Jefe de Ventas</strong>. 
            Cada vendedor tiene un plan de acción personalizado diseñado para maximizar su potencial.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Métricas generales del coaching
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Agentes con Coaching", len(agentes_coaching))
    
    # Calcular estadísticas generales
    puntajes = []
    conversiones = []
    for agente, data in coaching_data.items():
        if 'comparativa' in data and 'puntaje_ia' in data['comparativa']:
            puntajes.append(data['comparativa']['puntaje_ia'].get('agente', 0))
        if 'comparativa' in data and 'conversion' in data['comparativa']:
            conversiones.append(data['comparativa']['conversion'].get('agente', 0))
    
    with col2:
        if puntajes:
            st.metric("📊 Puntaje IA Promedio", f"{np.mean(puntajes):.1f}")
    
    with col3:
        if conversiones:
            st.metric("💰 Conversión Promedio", f"{np.mean(conversiones):.1f}%")
    
    with col4:
        # Total de evaluaciones
        total_eval = sum(data.get('metricas', {}).get('evaluaciones', {}).get('total_evaluadas', 0) for data in coaching_data.values())
        st.metric("📝 Total Evaluaciones", total_eval)
    
    st.markdown("---")
    
    # Tabs principales
    tab1, tab2, tab3 = st.tabs(["📋 Coaching Individual", "📊 Comparativa del Equipo", "📈 Ranking de Mejora"])
    
    with tab1:
        # Selector de agente con filtro por equipo
        st.markdown("### Selecciona un Vendedor")
        
        # Crear diccionario de agentes por equipo
        agentes_por_equipo = {}
        for agente in agentes_coaching:
            equipo = obtener_equipo_vendedor(agente)
            if equipo not in agentes_por_equipo:
                agentes_por_equipo[equipo] = []
            agentes_por_equipo[equipo].append(agente)
        
        # Filtro por equipo
        col_equipo, col_vendedor = st.columns([1, 2])
        
        with col_equipo:
            equipos_disponibles = ["Todos los Equipos"] + sorted([e for e in agentes_por_equipo.keys() if e != "Sin Equipo"]) + (["Sin Equipo"] if "Sin Equipo" in agentes_por_equipo else [])
            equipo_seleccionado = st.selectbox(
                "🏢 Filtrar por Equipo",
                equipos_disponibles,
                help="Filtra los vendedores por equipo/supervisor"
            )
        
        # Filtrar agentes según equipo seleccionado
        if equipo_seleccionado == "Todos los Equipos":
            agentes_filtrados = agentes_coaching
        else:
            agentes_filtrados = agentes_por_equipo.get(equipo_seleccionado, [])
        
        # Crear opciones con nombre real y puntaje
        opciones_agentes = []
        mapeo_display_id = {}  # Para mapear la opción mostrada al ID real
        for agente in sorted(agentes_filtrados, key=lambda x: obtener_nombre_vendedor(x)):
            data = coaching_data[agente]
            puntaje = data.get('comparativa', {}).get('puntaje_ia', {}).get('agente', 0)
            nombre_real = obtener_nombre_vendedor(agente)
            display = f"{nombre_real} (Puntaje: {puntaje:.1f})"
            opciones_agentes.append(display)
            mapeo_display_id[display] = agente
        
        with col_vendedor:
            if opciones_agentes:
                agente_seleccionado_display = st.selectbox(
                    "👤 Vendedor",
                    opciones_agentes,
                    help="Selecciona un vendedor para ver su coaching personalizado"
                )
                # Obtener ID real del agente
                agente_id = mapeo_display_id.get(agente_seleccionado_display, "")
                agente_seleccionado = obtener_nombre_vendedor(agente_id)
            else:
                st.warning("No hay vendedores en este equipo")
                return
        
        if agente_id in coaching_data:
            data = coaching_data[agente_id]
            
            # Métricas del agente
            equipo_actual = obtener_equipo_vendedor(agente_id)
            st.markdown(f"### 📊 Métricas de {agente_seleccionado}")
            st.caption(f"📍 Equipo: **{equipo_actual}**")
            
            comparativa = data.get('comparativa', {})
            metricas = data.get('metricas', {})
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                puntaje = comparativa.get('puntaje_ia', {}).get('agente', 0)
                diferencia = comparativa.get('puntaje_ia', {}).get('diferencia', 0)
                st.metric(
                    "Puntaje IA",
                    f"{puntaje:.1f}",
                    f"{diferencia:+.1f} vs equipo",
                    delta_color="normal"
                )
            
            with col2:
                conversion = comparativa.get('conversion', {}).get('agente', 0)
                dif_conv = comparativa.get('conversion', {}).get('diferencia', 0)
                st.metric(
                    "Conversión",
                    f"{conversion:.1f}%",
                    f"{dif_conv:+.1f}%",
                    delta_color="normal"
                )
            
            with col3:
                total_eval = metricas.get('evaluaciones', {}).get('total_evaluadas', 0)
                st.metric("Evaluaciones", total_eval)
            
            with col4:
                excelentes = metricas.get('evaluaciones', {}).get('llamadas_excelentes', 0)
                st.metric("Excelentes", excelentes, help="Puntaje >= 80")
            
            with col5:
                criticas = metricas.get('evaluaciones', {}).get('llamadas_criticas', 0)
                st.metric("Críticas", criticas, delta_color="inverse", help="Puntaje < 30")
            
            # Gráfico radar de criterios
            st.markdown("### 📈 Comparativa por Criterio")
            
            criterios_comp = comparativa.get('criterios', {})
            if criterios_comp:
                criterios_nombres = {
                    'saludo_presentacion': 'Saludo',
                    'identificacion_cliente': 'Identificación',
                    'deteccion_necesidades': 'Necesidades',
                    'oferta_productos': 'Oferta',
                    'manejo_objeciones': 'Objeciones',
                    'cierre': 'Cierre',
                    'despedida': 'Despedida',
                    'proactividad': 'Proactividad',
                    'empatia': 'Empatía',
                    'resolucion_problemas': 'Resolución'
                }
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Gráfico de barras comparativo
                    criterios_list = []
                    valores_agente = []
                    valores_equipo = []
                    
                    for crit, nombre in criterios_nombres.items():
                        if crit in criterios_comp:
                            criterios_list.append(nombre)
                            valores_agente.append(criterios_comp[crit].get('agente', 0))
                            valores_equipo.append(criterios_comp[crit].get('general', 0))
                    
                    df_comparativo = pd.DataFrame({
                        'Criterio': criterios_list + criterios_list,
                        'Valor': valores_agente + valores_equipo,
                        'Tipo': [agente_seleccionado] * len(criterios_list) + ['Promedio Equipo'] * len(criterios_list)
                    })
                    
                    fig = px.bar(
                        df_comparativo,
                        x='Criterio',
                        y='Valor',
                        color='Tipo',
                        barmode='group',
                        title=f'Desempeño de {agente_seleccionado} vs Equipo',
                        color_discrete_sequence=['#3B82F6', '#CBD5E1']
                    )
                    fig.update_layout(height=400, xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Tabla de diferencias
                    st.markdown("#### Diferencias con el equipo")
                    
                    diferencias_data = []
                    for crit, nombre in criterios_nombres.items():
                        if crit in criterios_comp:
                            dif = criterios_comp[crit].get('diferencia', 0)
                            emoji = "🟢" if dif >= 0 else "🔴"
                            diferencias_data.append({
                                'Criterio': nombre,
                                'Dif': f"{emoji} {dif:+.1f}"
                            })
                    
                    df_dif = pd.DataFrame(diferencias_data)
                    st.dataframe(df_dif, hide_index=True, use_container_width=True)
            
            # Análisis de Coaching
            st.markdown("---")
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #3B82F6 0%, #1E40AF 100%);
                padding: 1.5rem 2rem;
                border-radius: 12px;
                margin: 1rem 0 1.5rem 0;
                box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
            ">
                <h2 style="
                    color: white;
                    margin: 0;
                    font-size: 1.5rem;
                    font-weight: 700;
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                ">
                    <span style="font-size: 1.8rem;">🎯</span>
                    Análisis de Coaching Personalizado
                </h2>
                <p style="
                    color: rgba(255,255,255,0.9);
                    margin: 0.5rem 0 0 0;
                    font-size: 1.1rem;
                    font-weight: 500;
                ">
                    Vendedor: <span style="color: #FCD34D; font-weight: 700;">{agente_seleccionado}</span>
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            analisis = data.get('analisis_coaching', '')
            
            if analisis:
                # Limpiar introducciones genéricas de la IA
                import re
                # Patrones a eliminar al inicio del texto
                patrones_intro = [
                    r'^¡?[A-Za-záéíóúüñÁÉÍÓÚÜÑ]+!?\s*[Aa]quí\s+tienes[^:]*:\s*',
                    r'^¡?[Aa]bsolutamente!?\s*',
                    r'^¡?[Cc]laro!?\s*',
                    r'^¡?[Pp]or\s+supuesto!?\s*',
                    r'^¡?[Ee]xcelente!?\s*',
                ]
                for patron in patrones_intro:
                    analisis = re.sub(patron, '', analisis, flags=re.MULTILINE)
                analisis = analisis.strip()
                
                # Mostrar el análisis limpio
                st.markdown(analisis)
            else:
                st.info("No hay análisis de coaching disponible para este vendedor.")
            
            # Información adicional
            st.markdown("---")
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #10B981 0%, #059669 100%);
                padding: 1rem 1.5rem;
                border-radius: 12px;
                margin-bottom: 1rem;
                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
            ">
                <span style="
                    color: white;
                    font-size: 1.2rem;
                    font-weight: 700;
                ">📋 Datos Adicionales del Vendedor</span>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div style="
                    background: white;
                    padding: 1rem 1.25rem;
                    border-radius: 10px;
                    border-left: 4px solid #10B981;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                ">
                    <h4 style="color: #059669; margin: 0 0 0.75rem 0; font-size: 1rem;">💪 Fortalezas frecuentes</h4>
                </div>
                """, unsafe_allow_html=True)
                fortalezas = metricas.get('evaluaciones', {}).get('fortalezas_frecuentes', {})
                if fortalezas:
                    for fort, count in fortalezas.items():
                        st.markdown(f"- **{fort}**: {count} menciones")
                else:
                    st.write("No hay datos")
            
            with col2:
                st.markdown("""
                <div style="
                    background: white;
                    padding: 1rem 1.25rem;
                    border-radius: 10px;
                    border-left: 4px solid #F59E0B;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                ">
                    <h4 style="color: #D97706; margin: 0 0 0.75rem 0; font-size: 1rem;">📈 Áreas de mejora frecuentes</h4>
                </div>
                """, unsafe_allow_html=True)
                areas = metricas.get('evaluaciones', {}).get('areas_mejora_frecuentes', {})
                if areas:
                    for area, count in areas.items():
                        st.markdown(f"- **{area}**: {count} menciones")
                else:
                    st.write("No hay datos")
    
    with tab2:
        st.markdown("### 📊 Comparativa General del Equipo")
        
        # Filtro por equipo en comparativa
        equipos_disponibles_tab2 = ["Todos los Equipos"] + sorted([e for e in equipos_vendedores.keys() if e != "Sin Equipo"]) + (["Sin Equipo"] if "Sin Equipo" in equipos_vendedores else [])
        equipo_filtro_tab2 = st.selectbox(
            "🏢 Filtrar por Equipo",
            equipos_disponibles_tab2,
            key="equipo_tab2"
        )
        
        # Crear DataFrame con métricas de todos los agentes
        metricas_equipo = []
        
        for agente, data in coaching_data.items():
            # Filtrar por equipo si está seleccionado
            equipo_agente = obtener_equipo_vendedor(agente)
            if equipo_filtro_tab2 != "Todos los Equipos" and equipo_agente != equipo_filtro_tab2:
                continue
                
            comp = data.get('comparativa', {})
            met = data.get('metricas', {})
            
            row = {
                'Agente': obtener_nombre_vendedor(agente),
                'Equipo': equipo_agente,
                'Puntaje IA': comp.get('puntaje_ia', {}).get('agente', 0),
                'vs Equipo': comp.get('puntaje_ia', {}).get('diferencia', 0),
                'Percentil': comp.get('puntaje_ia', {}).get('percentil', 0),
                'Conversión': comp.get('conversion', {}).get('agente', 0),
                'Evaluaciones': met.get('evaluaciones', {}).get('total_evaluadas', 0),
                'Excelentes': met.get('evaluaciones', {}).get('llamadas_excelentes', 0),
                'Críticas': met.get('evaluaciones', {}).get('llamadas_criticas', 0)
            }
            
            # Agregar criterios principales
            criterios = comp.get('criterios', {})
            row['Saludo'] = criterios.get('saludo_presentacion', {}).get('agente', 0)
            row['Cierre'] = criterios.get('cierre', {}).get('agente', 0)
            row['Empatía'] = criterios.get('empatia', {}).get('agente', 0)
            
            metricas_equipo.append(row)
        
        df_equipo = pd.DataFrame(metricas_equipo)
        df_equipo = df_equipo.sort_values('Puntaje IA', ascending=False)
        
        # Gráfico de ranking
        fig = px.bar(
            df_equipo,
            x='Agente',
            y='Puntaje IA',
            color='vs Equipo',
            color_continuous_scale=['#EF4444', '#F59E0B', '#10B981'],
            title='Ranking de Puntaje IA por Agente'
        )
        fig.add_hline(
            y=df_equipo['Puntaje IA'].mean(),
            line_dash="dash",
            line_color="gray",
            annotation_text="Promedio"
        )
        fig.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabla detallada
        st.markdown("#### Tabla Detallada")
        
        # Formatear la tabla
        def color_diferencia(val):
            if isinstance(val, (int, float)):
                if val > 0:
                    return 'background-color: #d4edda'
                elif val < 0:
                    return 'background-color: #f8d7da'
            return ''
        
        styled_df = df_equipo.style.applymap(
            color_diferencia,
            subset=['vs Equipo']
        ).format({
            'Puntaje IA': '{:.1f}',
            'vs Equipo': '{:+.1f}',
            'Percentil': '{:.1f}',
            'Conversión': '{:.1f}%',
            'Saludo': '{:.1f}',
            'Cierre': '{:.1f}',
            'Empatía': '{:.1f}'
        })
        
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        # Scatter plot: Puntaje vs Conversión
        st.markdown("#### Relación Puntaje IA vs Conversión")
        fig2 = px.scatter(
            df_equipo,
            x='Puntaje IA',
            y='Conversión',
            text='Agente',
            size='Evaluaciones',
            color='vs Equipo',
            color_continuous_scale=['#EF4444', '#F59E0B', '#10B981'],
            title='Puntaje IA vs Tasa de Conversión'
        )
        fig2.update_traces(textposition='top center')
        fig2.update_layout(height=500)
        st.plotly_chart(fig2, use_container_width=True)
    
    with tab3:
        st.markdown("### 📈 Ranking y Prioridades de Mejora")
        
        # Calcular potencial de mejora
        df_mejora = df_equipo.copy()
        
        # Calcular índice de potencial de mejora
        # Mayor puntaje para quienes tienen más margen de mejora pero buena base
        df_mejora['Potencial'] = (100 - df_mejora['Puntaje IA']) * (df_mejora['Evaluaciones'] / df_mejora['Evaluaciones'].max())
        df_mejora['Tasa_Criticas'] = df_mejora['Críticas'] / df_mejora['Evaluaciones'] * 100
        
        df_mejora = df_mejora.sort_values('Potencial', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔴 Prioridad Alta (Mayor potencial de mejora)")
            
            top_mejora = df_mejora.head(10)
            
            for i, (_, row) in enumerate(top_mejora.iterrows(), 1):
                color = "#EF4444" if row['vs Equipo'] < -10 else "#F59E0B" if row['vs Equipo'] < 0 else "#10B981"
                st.markdown(f"""
                <div style='background: #FFFFFF; padding: 12px; border-radius: 8px; margin: 5px 0;
                            border-left: 4px solid {color}; box-shadow: 0 2px 6px rgba(0,0,0,0.08);'>
                    <strong style='color: #1E293B;'>{i}. {row['Agente']}</strong><br>
                    <small style='color: #475569;'>Puntaje: {row['Puntaje IA']:.1f} | Críticas: {row['Tasa_Criticas']:.1f}% | Eval: {row['Evaluaciones']}</small>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### 🟢 Top Performers")
            
            top_performers = df_equipo.head(10)
            
            for i, (_, row) in enumerate(top_performers.iterrows(), 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                st.markdown(f"""
                <div style='background: #FFFFFF; padding: 12px; border-radius: 8px; margin: 5px 0;
                            border-left: 4px solid #10B981; box-shadow: 0 2px 6px rgba(0,0,0,0.08);'>
                    <strong style='color: #1E293B;'>{medal} {row['Agente']}</strong><br>
                    <small style='color: #475569;'>Puntaje: {row['Puntaje IA']:.1f} | Conv: {row['Conversión']:.1f}% | Excelentes: {row['Excelentes']}</small>
                </div>
                """, unsafe_allow_html=True)
        
        # Distribución de puntajes
        st.markdown("---")
        st.markdown("#### 📊 Distribución de Puntajes del Equipo")
        
        fig3 = px.histogram(
            df_equipo,
            x='Puntaje IA',
            nbins=15,
            title='Distribución de Puntajes IA del Equipo',
            color_discrete_sequence=['#3B82F6']
        )
        fig3.add_vline(x=df_equipo['Puntaje IA'].mean(), line_dash="dash", line_color="#EF4444", annotation_text="Promedio")
        fig3.update_layout(height=350)
        st.plotly_chart(fig3, use_container_width=True)
        
        # Recomendaciones generales
        st.markdown("---")
        st.markdown("### 💡 Recomendaciones para el Equipo")
        
        prom_puntaje = df_equipo['Puntaje IA'].mean()
        prom_conv = df_equipo['Conversión'].mean()
        agentes_bajo_prom = len(df_equipo[df_equipo['Puntaje IA'] < prom_puntaje])
        agentes_criticos = len(df_equipo[df_equipo['vs Equipo'] < -15])
        
        st.markdown(f"""
        📌 **Situación actual del equipo:**
        - Puntaje IA promedio: **{prom_puntaje:.1f}/100**
        - Conversión promedio: **{prom_conv:.1f}%**
        - Agentes bajo el promedio: **{agentes_bajo_prom}**
        - Agentes en situación crítica: **{agentes_criticos}**
        
        🎯 **Acciones recomendadas:**
        1. **Coaching intensivo** para los {min(5, agentes_criticos)} agentes con mayor necesidad de mejora
        2. **Mentoring entre pares**: emparejar top performers con agentes en desarrollo
        3. **Capacitación grupal** en las áreas más débiles del equipo
        4. **Seguimiento semanal** del progreso con metas específicas
        """)


def pagina_performance_agentes(df, datos):
    """Página de performance por agente"""
    mostrar_proximamente("👥 Performance de Agentes")
    
    st.markdown("---")
    
    # Gráfico de dispersión: Calidad vs Conversión
    st.markdown('<p class="section-header">📊 Análisis de Performance</p>', unsafe_allow_html=True)
    
    fig = px.scatter(
        agentes_stats,
        x='Score Calidad',
        y='Tasa Conversión',
        size='Total Llamadas',
        hover_name='Agente',
        color='Ventas',
        color_continuous_scale='Blues',
        labels={
            'Score Calidad': 'Score de Calidad',
            'Tasa Conversión': 'Tasa de Conversión (%)',
            'Ventas': 'Ventas Totales'
        }
    )
    fig.update_layout(
        height=350,
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FAFBFC',
        font=dict(color='#2C3E50', size=12),
        margin=dict(t=20, b=40, l=50, r=20)
    )
    fig.update_xaxes(
        gridcolor='#E5E8E8', 
        tickfont=dict(size=9, color='#2C3E50'),
        title_font=dict(size=12, color='#2C3E50')
    )
    fig.update_yaxes(
        gridcolor='#E5E8E8', 
        tickfont=dict(size=9, color='#2C3E50'),
        title_font=dict(size=12, color='#2C3E50')
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabla completa
    st.markdown('<p class="section-header">📋 Tabla Completa de Agentes</p>', unsafe_allow_html=True)
    
    ordenar = st.selectbox(
        "Ordenar por:",
        ['Tasa Conversión', 'Score Calidad', 'Total Llamadas', 'Ventas'],
        key='orden_agentes'
    )
    
    agentes_ordenados = agentes_stats.sort_values(ordenar, ascending=False)
    st.dataframe(agentes_ordenados, use_container_width=True, hide_index=True)
    
    # Si hay datos de cierres, agregar info
    if 'cierres_df' in datos:
        st.markdown('<p class="section-header">📋 Cierres Comerciales por Agente</p>', unsafe_allow_html=True)
        
        df_cierres = datos['cierres_df']
        if 'agente' in df_cierres.columns and 'porcentaje' in df_cierres.columns:
            cierres_agente = df_cierres.groupby('agente').agg({
                'porcentaje': ['mean', 'count'],
            }).reset_index()
            cierres_agente.columns = ['Agente', 'Promedio Cierre', 'Total Ventas']
            cierres_agente['Promedio Cierre'] = cierres_agente['Promedio Cierre'].round(1)
            cierres_agente = cierres_agente.sort_values('Promedio Cierre', ascending=False)
            
            fig = px.bar(
                cierres_agente.head(15),
                x='Agente',
                y='Promedio Cierre',
                color='Promedio Cierre',
                color_continuous_scale='Greens',
                text='Promedio Cierre'
            )
            fig.update_traces(
                texttemplate='%{text:.1f}%', 
                textposition='outside',
                textfont=dict(size=9, color='#2C3E50')
            )
            fig.update_layout(
                height=320, 
                xaxis_tickangle=-45,
                paper_bgcolor='#FFFFFF',
                plot_bgcolor='#FAFBFC',
                font=dict(color='#2C3E50', size=12),
                margin=dict(t=30, b=70, l=50, r=20)
            )
            fig.update_xaxes(
                gridcolor='#E5E8E8', 
                tickfont=dict(size=8, color='#2C3E50'),
                title_font=dict(size=12, color='#2C3E50')
            )
            fig.update_yaxes(
                gridcolor='#E5E8E8', 
                tickfont=dict(size=9, color='#2C3E50'),
                title_font=dict(size=12, color='#2C3E50')
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # =============================================================================
    # ANÁLISIS DETALLADO DE UN AGENTE ESPECÍFICO
    # =============================================================================
    st.markdown("---")
    st.markdown('<p class="section-header">🔍 Análisis Detallado por Agente</p>', unsafe_allow_html=True)
    
    agentes_lista = sorted(df['agente'].dropna().unique().tolist())
    agente_sel = st.selectbox("Selecciona un agente para ver su análisis detallado:", agentes_lista, key='agente_perf_detail')
    
    df_agente = df[df['agente'] == agente_sel].copy()
    
    if len(df_agente) > 0:
        # Métricas del agente
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_ag = len(df_agente)
            st.metric("📞 Total Llamadas", f"{total_ag:,}")
        with col2:
            ventas_ag = len(df_agente[df_agente['tipificacion'] == 'Venta'])
            tasa_ag = ventas_ag / total_ag * 100 if total_ag > 0 else 0
            st.metric("💰 Tasa Conversión", f"{tasa_ag:.1f}%")
        with col3:
            score_ag = df_agente['score_calidad'].mean()
            st.metric("⭐ Score Calidad", f"{score_ag:.1f}")
        with col4:
            dur_ag = df_agente['duracion'].mean() / 60
            st.metric("⏱️ Duración Prom", f"{dur_ag:.1f} min")
        
        # Gráficos del agente
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribución de tipificaciones
            st.markdown("**📊 Distribución de Resultados:**")
            if 'tipificacion' in df_agente.columns:
                tip_counts = df_agente['tipificacion'].value_counts()
                fig = px.pie(
                    values=tip_counts.values,
                    names=tip_counts.index,
                    color_discrete_sequence=px.colors.qualitative.Set2
                )
                fig.update_layout(height=300, paper_bgcolor='#FFFFFF')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Evolución temporal si hay fechas
            st.markdown("**📈 Llamadas por Día:**")
            if 'dia' in df_agente.columns and df_agente['dia'].notna().any():
                llamadas_dia = df_agente.groupby('dia').size().reset_index(name='Llamadas')
                fig = px.line(
                    llamadas_dia,
                    x='dia',
                    y='Llamadas',
                    markers=True,
                    color_discrete_sequence=['#3B82F6']
                )
                fig.update_layout(height=300, paper_bgcolor='#FFFFFF')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sin datos temporales disponibles")
        
        # Tabla de llamadas del agente
        st.markdown("---")
        st.markdown("**📋 Últimas Llamadas del Agente:**")
        
        columnas_tabla = ['id', 'fecha', 'tipificacion', 'duracion', 'score_calidad', 'planes']
        cols_disponibles = [c for c in columnas_tabla if c in df_agente.columns]
        
        df_mostrar = df_agente[cols_disponibles].copy()
        if 'duracion' in df_mostrar.columns:
            df_mostrar['duracion'] = (df_mostrar['duracion'] / 60).round(1).astype(str) + ' min'
        
        st.dataframe(df_mostrar.head(30), use_container_width=True, hide_index=True, height=300)


def pagina_analisis_temporal(df):
    """Página de análisis temporal"""
    mostrar_proximamente("📅 Análisis Temporal")
    return
    
    # === CÓDIGO COMENTADO PARA FUTURO ===
    if 'dia' not in df.columns or 'hora' not in df.columns:
        st.warning("No hay datos temporales disponibles")
        return
    
    # Llamadas por día
    st.markdown('<p class="section-header">📈 Evolución Diaria</p>', unsafe_allow_html=True)
    
    df_dia = df.groupby('dia').agg({
        'id': 'count',
        'tipificacion': lambda x: (x == 'Venta').sum(),
        'score_calidad': 'mean'
    }).reset_index()
    df_dia.columns = ['Fecha', 'Llamadas', 'Ventas', 'Calidad Promedio']
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(name='Llamadas', x=df_dia['Fecha'], y=df_dia['Llamadas'], marker_color='#5DADE2'),
        secondary_y=False
    )
    fig.add_trace(
        go.Scatter(name='Ventas', x=df_dia['Fecha'], y=df_dia['Ventas'], mode='lines+markers', 
                   line=dict(color='#27AE60', width=2), marker=dict(size=6)),
        secondary_y=False
    )
    fig.update_layout(
        height=300, 
        hovermode='x unified',
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FAFBFC',
        font=dict(color='#2C3E50', size=12),
        margin=dict(t=20, b=40, l=50, r=20),
        legend=dict(bgcolor='rgba(255,255,255,0.9)', bordercolor='#E5E8E8', borderwidth=1, font=dict(color='#2C3E50', size=9))
    )
    fig.update_xaxes(
        gridcolor='#E5E8E8', 
        tickfont=dict(size=9, color='#2C3E50'),
        title_font=dict(size=12, color='#2C3E50')
    )
    fig.update_yaxes(
        title_text="Cantidad", 
        secondary_y=False, 
        gridcolor='#E5E8E8', 
        tickfont=dict(size=9, color='#2C3E50'),
        title_font=dict(size=12, color='#2C3E50')
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Heatmap por hora y día
    st.markdown('<p class="section-header">🕐 Distribución por Hora del Día</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        llamadas_hora = df.groupby('hora').size().reset_index(name='llamadas')
        fig = px.bar(
            llamadas_hora, x='hora', y='llamadas',
            color='llamadas', color_continuous_scale='Blues',
            labels={'hora': 'Hora', 'llamadas': 'Llamadas'}
        )
        fig.update_layout(
            height=280, 
            title=dict(text='Volumen por Hora', font=dict(size=11, color='#2C3E50')),
            paper_bgcolor='#FFFFFF',
            plot_bgcolor='#FAFBFC',
            font=dict(color='#2C3E50', size=12),
            margin=dict(t=35, b=40, l=50, r=20),
            showlegend=False
        )
        fig.update_xaxes(
            gridcolor='#E5E8E8', 
            tickfont=dict(size=9, color='#2C3E50'),
            title_font=dict(size=12, color='#2C3E50')
        )
        fig.update_yaxes(
            gridcolor='#E5E8E8', 
            tickfont=dict(size=9, color='#2C3E50'),
            title_font=dict(size=12, color='#2C3E50')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        ventas_hora = df[df['tipificacion'] == 'Venta'].groupby('hora').size().reset_index(name='ventas')
        fig = px.bar(
            ventas_hora, x='hora', y='ventas',
            color='ventas', color_continuous_scale='Greens',
            labels={'hora': 'Hora', 'ventas': 'Ventas'}
        )
        fig.update_layout(
            height=280, 
            title=dict(text='Ventas por Hora', font=dict(size=11, color='#2C3E50')),
            paper_bgcolor='#FFFFFF',
            plot_bgcolor='#FAFBFC',
            font=dict(color='#2C3E50', size=12),
            margin=dict(t=35, b=40, l=50, r=20),
            showlegend=False
        )
        fig.update_xaxes(
            gridcolor='#E5E8E8', 
            tickfont=dict(size=9, color='#2C3E50'),
            title_font=dict(size=12, color='#2C3E50')
        )
        fig.update_yaxes(
            gridcolor='#E5E8E8', 
            tickfont=dict(size=9, color='#2C3E50'),
            title_font=dict(size=12, color='#2C3E50')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Tasa de conversión por hora
    st.markdown('<p class="section-header">📊 Tasa de Conversión por Hora</p>', unsafe_allow_html=True)
    
    conversion_hora = df.groupby('hora').apply(
        lambda x: (x['tipificacion'] == 'Venta').sum() / len(x) * 100 if len(x) > 0 else 0
    ).reset_index(name='tasa_conversion')
    
    fig = px.line(
        conversion_hora, x='hora', y='tasa_conversion',
        markers=True,
        labels={'hora': 'Hora', 'tasa_conversion': 'Tasa de Conversión (%)'}
    )
    fig.update_traces(line=dict(color='#2980B9', width=2), marker=dict(size=6, color='#1A5276'))
    fig.update_layout(
        height=280,
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FAFBFC',
        font=dict(color='#2C3E50', size=12),
        margin=dict(t=20, b=40, l=50, r=20)
    )
    fig.update_xaxes(
        gridcolor='#E5E8E8', 
        tickfont=dict(size=9, color='#2C3E50'),
        title_font=dict(size=12, color='#2C3E50')
    )
    fig.update_yaxes(
        gridcolor='#E5E8E8', 
        tickfont=dict(size=9, color='#2C3E50'),
        title_font=dict(size=12, color='#2C3E50')
    )
    st.plotly_chart(fig, use_container_width=True)


def pagina_detalle_llamadas(df, datos):
    """Página de detalle de llamadas"""
    mostrar_proximamente("🔍 Explorador de Llamadas")
    return
    
    # === CÓDIGO COMENTADO PARA FUTURO ===
    # Filtros en la página principal
    st.markdown('<p class="section-header">🔧 Filtros de Búsqueda</p>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        agentes = ['Todos'] + sorted(df['agente'].unique().tolist())
        filtro_agente = st.selectbox("Agente:", agentes, key='exp_agente')
    
    with col2:
        tipificaciones = ['Todas'] + sorted(df['tipificacion'].dropna().unique().tolist())
        filtro_tipificacion = st.selectbox("Tipificación:", tipificaciones, key='exp_tip')
    
    with col3:
        tipos = ['Todos'] + sorted(df['tipo'].dropna().unique().tolist())
        filtro_tipo = st.selectbox("Resultado:", tipos, key='exp_tipo')
    
    with col4:
        min_calidad, max_calidad = st.slider(
            "Score de Calidad:",
            0, 100, (0, 100), key='exp_calidad'
        )
    
    # Aplicar filtros
    df_filtrado = df.copy()
    if filtro_agente != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['agente'] == filtro_agente]
    if filtro_tipificacion != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['tipificacion'] == filtro_tipificacion]
    if filtro_tipo != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['tipo'] == filtro_tipo]
    df_filtrado = df_filtrado[
        (df_filtrado['score_calidad'] >= min_calidad) & 
        (df_filtrado['score_calidad'] <= max_calidad)
    ]
    
    # Métricas del filtro
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Llamadas Encontradas", f"{len(df_filtrado):,}")
    with col2:
        ventas_filt = len(df_filtrado[df_filtrado['tipificacion'] == 'Venta'])
        st.metric("💰 Ventas", f"{ventas_filt:,}")
    with col3:
        score_filt = df_filtrado['score_calidad'].mean() if len(df_filtrado) > 0 else 0
        st.metric("⭐ Score Promedio", f"{score_filt:.1f}")
    with col4:
        dur_filt = df_filtrado['duracion'].mean() / 60 if len(df_filtrado) > 0 else 0
        st.metric("⏱️ Duración Prom", f"{dur_filt:.1f} min")
    
    # Gráficos resumen del filtro
    if len(df_filtrado) > 0 and len(df_filtrado) < len(df):
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📊 Distribución de Resultados (Filtrado):**")
            tip_counts = df_filtrado['tipificacion'].value_counts()
            fig = px.pie(
                values=tip_counts.values,
                names=tip_counts.index,
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig.update_layout(height=280, paper_bgcolor='#FFFFFF')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**📈 Score de Calidad (Filtrado):**")
            fig = px.histogram(
                df_filtrado,
                x='score_calidad',
                nbins=20,
                color_discrete_sequence=['#3B82F6']
            )
            fig.update_layout(height=280, paper_bgcolor='#FFFFFF')
            st.plotly_chart(fig, use_container_width=True)
    
    # Tabla interactiva
    st.markdown("---")
    st.markdown('<p class="section-header">📋 Listado de Llamadas</p>', unsafe_allow_html=True)
    
    columnas_mostrar = ['id', 'fecha', 'agente', 'duracion', 'tipificacion', 'tipo', 'score_calidad', 'planes']
    columnas_disponibles = [c for c in columnas_mostrar if c in df_filtrado.columns]
    
    df_tabla = df_filtrado[columnas_disponibles].copy()
    if 'duracion' in df_tabla.columns:
        df_tabla['duracion'] = (df_tabla['duracion'] / 60).round(1).astype(str) + ' min'
    
    st.dataframe(
        df_tabla.sort_values('fecha', ascending=False).head(100),
        use_container_width=True,
        height=400,
        hide_index=True
    )
    
    # Detalle de una llamada específica
    st.markdown("---")
    st.markdown('<p class="section-header">🔎 Ver Detalle de Llamada</p>', unsafe_allow_html=True)
    
    if len(df_filtrado) > 0:
        ids_disponibles = df_filtrado['id'].tolist()[:50]
        id_seleccionado = st.selectbox("Selecciona ID de llamada:", ids_disponibles, key='id_detalle')
        
        llamada = df_filtrado[df_filtrado['id'] == id_seleccionado].iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📞 Información de la Llamada:**")
            st.markdown(f"- **ID:** {llamada['id']}")
            st.markdown(f"- **Fecha:** {llamada.get('fecha', 'N/A')}")
            st.markdown(f"- **Agente:** {llamada.get('agente', 'N/A')}")
            dur_min = llamada.get('duracion', 0) / 60
            st.markdown(f"- **Duración:** {dur_min:.1f} min")
        
        with col2:
            st.markdown("**📊 Resultados:**")
            st.markdown(f"- **Tipificación:** {llamada.get('tipificacion', 'N/A')}")
            st.markdown(f"- **Tipo:** {llamada.get('tipo', 'N/A')}")
            st.markdown(f"- **Score Calidad:** {llamada.get('score_calidad', 0)}")
            st.markdown(f"- **Planes Ofrecidos:** {llamada.get('planes', 'Ninguno')}")
        
        # Si hay evaluación de Gemini
        if 'evaluaciones_gemini_df' in datos:
            df_gemini = datos['evaluaciones_gemini_df']
            # Buscar por coincidencia parcial del ID
            eval_match = df_gemini[df_gemini['archivo'].str.contains(str(id_seleccionado), na=False)]
            
            if len(eval_match) > 0:
                st.markdown("---")
                st.markdown("**🤖 Evaluación IA:**")
                eval_data = eval_match.iloc[0]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Puntaje IA", f"{eval_data.get('puntaje_total', 0)}/100")
                with col2:
                    st.markdown(f"**Resumen:** {eval_data.get('resumen', 'N/A')}")
    
    # Exportar datos
    st.markdown("---")
    col1, col2, col3 = st.columns([1,1,2])
    
    with col1:
        csv = df_filtrado.to_csv(index=False, sep=';').encode('utf-8')
        st.download_button(
            label="📥 Descargar CSV",
            data=csv,
            file_name=f"llamadas_filtradas_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime='text/csv'
        )
    
    with col2:
        st.markdown(f"**Total registros:** {len(df_filtrado):,}")


def pagina_quejas_no_resueltas(datos):
    """Página de análisis de quejas no resueltas"""
    st.markdown('<div class="main-header">😤 Quejas No Resueltas</div>', unsafe_allow_html=True)
    
    if 'quejas' not in datos:
        st.warning("⚠️ No hay datos de quejas disponibles.")
        return
    
    # Cargar nombres de vendedores
    listado_vendedores = {}
    try:
        df_listado = pd.read_csv('LISTADO-DE-VENDEDORES.csv', header=0)
        for _, row in df_listado.iterrows():
            usuario = str(row.iloc[0]).strip().lower().replace('\t', '').replace(' ', '')
            nombre = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
            if usuario and nombre and usuario != 'usuario':
                listado_vendedores[usuario] = nombre.title()
    except:
        pass
    
    def obtener_nombre_agente(agente_id):
        agente_normalizado = str(agente_id).lower().replace(' ', '').replace('_', '')
        return listado_vendedores.get(agente_normalizado, agente_id)
    
    quejas = datos['quejas']
    stats = quejas.get('estadisticas', {})
    
    # Nota explicativa
    st.info("""
    **📌 Este análisis excluye:**
    - Llamadas con cierre comercial (venta realizada)
    - Llamadas que continúan después (por WhatsApp u otra llamada)
    
    Solo analiza llamadas donde hubo una queja y NO se gestionó la venta o continuación.
    """)
    
    # =========================================================================
    # MÉTRICAS PRINCIPALES
    # =========================================================================
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📞 Total Llamadas", f"{stats.get('total_llamadas', 0):,}")
    with col2:
        analizadas = stats.get('analizadas', 0)
        excluidas = stats.get('excluidas_venta', 0) + stats.get('excluidas_continuacion', 0)
        st.metric("🔍 Analizadas", f"{analizadas:,}", f"-{excluidas} excluidas")
    with col3:
        con_queja = stats.get('con_queja', 0)
        pct = stats.get('porcentaje_con_queja', 0)
        st.metric("😤 Con Queja", f"{con_queja:,}", f"{pct:.1f}%")
    with col4:
        resueltas = stats.get('queja_resuelta', 0)
        pct_res = resueltas / con_queja * 100 if con_queja > 0 else 0
        st.metric("✅ Resueltas", f"{resueltas:,}", f"{pct_res:.1f}%")
    with col5:
        no_resueltas = stats.get('queja_no_resuelta', 0)
        pct_no = stats.get('porcentaje_no_resuelta', 0)
        st.metric("❌ NO Resueltas", f"{no_resueltas:,}", f"-{pct_no:.1f}%", delta_color="inverse")
    
    st.markdown("---")
    
    # =========================================================================
    # GRÁFICOS
    # =========================================================================
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<p class="section-header">📊 Estado de Quejas</p>', unsafe_allow_html=True)
        
        resueltas = stats.get('queja_resuelta', 0)
        no_resueltas = stats.get('queja_no_resuelta', 0)
        
        if resueltas + no_resueltas > 0:
            fig = go.Figure(data=[go.Pie(
                labels=['Resueltas', 'No Resueltas'],
                values=[resueltas, no_resueltas],
                marker_colors=['#27AE60', '#E74C3C'],
                textinfo='percent+value',
                textfont=dict(size=14, color='#FFFFFF'),
                hole=0.4
            )])
            fig.update_layout(
                height=280,
                margin=dict(t=20, b=20, l=20, r=120),
                paper_bgcolor='#FFFFFF',
                legend=dict(font=dict(size=12, color='#2C3E50'))
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown('<p class="section-header">📋 Tipos de Quejas No Resueltas</p>', unsafe_allow_html=True)
        
        tipos = quejas.get('tipos_queja', {})
        if tipos:
            fig = px.bar(
                x=list(tipos.values()),
                y=list(tipos.keys()),
                orientation='h',
                color=list(tipos.values()),
                color_continuous_scale='Reds',
                text=list(tipos.values())
            )
            fig.update_traces(textposition='outside', textfont=dict(size=11, color='#2C3E50'))
            fig.update_layout(
                height=280,
                showlegend=False,
                margin=dict(t=20, b=30, l=20, r=40),
                paper_bgcolor='#FFFFFF',
                plot_bgcolor='#FAFBFC',
                xaxis_title="Cantidad",
                yaxis_title=""
            )
            fig.update_xaxes(gridcolor='#E5E8E8', tickfont=dict(size=10, color='#2C3E50'))
            fig.update_yaxes(tickfont=dict(size=11, color='#2C3E50'))
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # =========================================================================
    # ALERTA DE GRAVEDAD
    # =========================================================================
    pct_no_resuelta = stats.get('porcentaje_no_resuelta', 0)
    
    if pct_no_resuelta > 80:
        st.error(f"""
        ### 🚨 Alerta Crítica
        **{pct_no_resuelta:.1f}%** de las quejas NO se resuelven.
        
        Esto indica un problema grave en la gestión de reclamos. Los agentes no están:
        - Ofreciendo soluciones concretas
        - Generando tickets/reclamos
        - Explicando los procesos de resolución
        """)
    elif pct_no_resuelta > 50:
        st.warning(f"""
        ### ⚠️ Área de Mejora
        **{pct_no_resuelta:.1f}%** de las quejas no se resuelven.
        
        Capacitar a los agentes en manejo de objeciones y resolución de problemas.
        """)
    else:
        st.success(f"""
        ### ✅ Buen Desempeño
        Solo **{pct_no_resuelta:.1f}%** de las quejas no se resuelven.
        """)
    
    st.markdown("---")
    
    # =========================================================================
    # TOP AGENTES CON MÁS QUEJAS NO RESUELTAS
    # =========================================================================
    st.markdown('<p class="section-header">🚨 Agentes con Más Quejas No Resueltas</p>', unsafe_allow_html=True)
    
    quejas_por_agente = quejas.get('quejas_por_agente', {})
    if quejas_por_agente:
        agentes_data = []
        for agente, data in quejas_por_agente.items():
            total = data.get('total', 0)
            no_res = data.get('no_resueltas', 0)
            if total >= 3:  # Solo agentes con al menos 3 quejas
                pct = no_res / total * 100 if total > 0 else 0
                nombre_real = obtener_nombre_agente(agente)
                agentes_data.append({
                    'Agente': nombre_real,
                    'Total Quejas': total,
                    'Resueltas': data.get('resueltas', 0),
                    'No Resueltas': no_res,
                    '% No Resueltas': round(pct, 1)
                })
        
        if agentes_data:
            df_agentes = pd.DataFrame(agentes_data)
            df_agentes = df_agentes.sort_values('No Resueltas', ascending=False).head(15)
            
            # Gráfico de barras
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Resueltas',
                x=df_agentes['Agente'],
                y=df_agentes['Resueltas'],
                marker_color='#27AE60',
                text=df_agentes['Resueltas'],
                textposition='inside'
            ))
            fig.add_trace(go.Bar(
                name='No Resueltas',
                x=df_agentes['Agente'],
                y=df_agentes['No Resueltas'],
                marker_color='#E74C3C',
                text=df_agentes['No Resueltas'],
                textposition='inside'
            ))
            fig.update_layout(
                barmode='stack',
                height=350,
                margin=dict(t=30, b=80, l=50, r=20),
                paper_bgcolor='#FFFFFF',
                plot_bgcolor='#FAFBFC',
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5, font=dict(size=11)),
                xaxis_tickangle=-45
            )
            fig.update_xaxes(tickfont=dict(size=9, color='#2C3E50'))
            fig.update_yaxes(gridcolor='#E5E8E8', tickfont=dict(size=10, color='#2C3E50'))
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabla
            st.dataframe(df_agentes, use_container_width=True, hide_index=True, height=300)
    
    # =========================================================================
    # DETALLE DE QUEJAS NO RESUELTAS
    # =========================================================================
    if 'quejas_df' in datos:
        st.markdown("---")
        st.markdown('<p class="section-header">📝 Detalle de Quejas No Resueltas</p>', unsafe_allow_html=True)
        
        df_quejas = datos['quejas_df']
        
        # Filtro por agente (manejar NaN)
        agentes_unicos = df_quejas['agente'].dropna().astype(str).unique().tolist()
        agentes = ['Todos'] + sorted([a for a in agentes_unicos if a and a != 'nan'])
        filtro = st.selectbox("Filtrar por Agente:", agentes)
        
        if filtro != 'Todos':
            df_quejas = df_quejas[df_quejas['agente'] == filtro]
        
        st.dataframe(
            df_quejas[['archivo', 'agente', 'duracion_seg', 'cantidad_quejas', 'primera_queja']].head(50),
            use_container_width=True,
            height=300
        )


def pagina_analisis_duracion(datos):
    """Página de análisis integral por duración de llamadas"""
    mostrar_proximamente("⏱️ Análisis de Duración de Llamadas")
    return
    
    # === CÓDIGO COMENTADO PARA FUTURO ===
    if 'integral' not in datos or 'integral_df' not in datos:
        st.warning("⚠️ No se encontraron datos del análisis integral.")
        return
    
    resumen = datos['integral']
    df = datos['integral_df'].copy()
    
    # =============================================================================
    # MÉTRICAS PRINCIPALES
    # =============================================================================
    st.markdown('<p class="section-header">📊 Métricas Generales</p>', unsafe_allow_html=True)
    
    total = resumen.get('total_llamadas', 0)
    dur_prom = resumen.get('duracion_promedio_seg', 0)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📞 Total Llamadas", f"{total:,}")
    with col2:
        st.metric("⏱️ Duración Promedio", f"{dur_prom/60:.1f} min")
    with col3:
        menos_1min = resumen.get('por_duracion', {}).get('< 1 min', {}).get('total', 0)
        st.metric("⚡ < 1 min (Cortas)", f"{menos_1min:,}")
    with col4:
        mas_8min = resumen.get('por_duracion', {}).get('> 8 min', {}).get('total', 0)
        st.metric("⏰ > 8 min (Largas)", f"{mas_8min:,}")
    with col5:
        problematicas = df['es_problematica'].sum() if 'es_problematica' in df.columns else 0
        st.metric("🚨 Problemáticas", f"{problematicas:,}")
    
    st.markdown("---")
    
    # =============================================================================
    # DISTRIBUCIÓN POR DURACIÓN
    # =============================================================================
    st.markdown('<p class="section-header">📈 Distribución por Rango de Duración</p>', unsafe_allow_html=True)
    
    rangos_orden = ['< 1 min', '1-3 min', '3-5 min', '5-8 min', '> 8 min']
    por_duracion = resumen.get('por_duracion', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de barras
        datos_barras = []
        for rango in rangos_orden:
            if rango in por_duracion:
                datos_barras.append({
                    'Rango': rango,
                    'Llamadas': por_duracion[rango].get('total', 0)
                })
        
        if datos_barras:
            df_barras = pd.DataFrame(datos_barras)
            fig = px.bar(
                df_barras, x='Rango', y='Llamadas',
                color='Llamadas',
                color_continuous_scale=['#3B82F6', '#10B981', '#F59E0B', '#F97316', '#EF4444']
            )
            fig.update_layout(
                height=350,
                margin=dict(t=30, b=50, l=50, r=20),
                paper_bgcolor='#FFFFFF',
                plot_bgcolor='#FAFBFC',
                showlegend=False
            )
            fig.update_xaxes(tickfont=dict(size=11, color='#2C3E50'))
            fig.update_yaxes(gridcolor='#E5E8E8', tickfont=dict(size=10, color='#2C3E50'))
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Tabla resumen
        tabla_duracion = []
        for rango in rangos_orden:
            if rango in por_duracion:
                d = por_duracion[rango]
                total_rango = d.get('total', 0)
                tabla_duracion.append({
                    'Rango': rango,
                    'Total': total_rango,
                    'Con Plan': d.get('con_plan', 0),
                    '% Plan': f"{d.get('con_plan', 0)/total_rango*100:.1f}%" if total_rango > 0 else "0%",
                    'Fibra': d.get('ofrece_fibra', 0),
                    'Queja NR': d.get('queja_no_resuelta', 0),
                    'Cierre+': d.get('cierre_positivo', 0),
                })
        
        df_tabla = pd.DataFrame(tabla_duracion)
        st.dataframe(df_tabla, use_container_width=True, hide_index=True, height=280)
    
    # =============================================================================
    # ANÁLISIS DE EFECTIVIDAD POR DURACIÓN
    # =============================================================================
    st.markdown("---")
    st.markdown('<p class="section-header">🎯 Efectividad por Rango de Duración</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Tasa de oferta de plan por duración
        datos_plan = []
        for rango in rangos_orden:
            if rango in por_duracion:
                d = por_duracion[rango]
                total_rango = d.get('total', 0)
                con_plan = d.get('con_plan', 0)
                pct = con_plan/total_rango*100 if total_rango > 0 else 0
                datos_plan.append({'Rango': rango, '% Ofrecen Plan': pct})
        
        if datos_plan:
            df_plan = pd.DataFrame(datos_plan)
            fig = px.bar(df_plan, x='Rango', y='% Ofrecen Plan', 
                        color='% Ofrecen Plan',
                        color_continuous_scale=['#E74C3C', '#F1C40F', '#2ECC71'])
            fig.update_layout(
                title='% que Ofrece Plan por Duración',
                height=300,
                margin=dict(t=50, b=50, l=50, r=20),
                paper_bgcolor='#FFFFFF',
                plot_bgcolor='#FAFBFC'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Tasa de cierre por duración
        datos_cierre = []
        for rango in rangos_orden:
            if rango in por_duracion:
                d = por_duracion[rango]
                total_rango = d.get('total', 0)
                cierres = d.get('cierre_positivo', 0)
                pct = cierres/total_rango*100 if total_rango > 0 else 0
                datos_cierre.append({'Rango': rango, '% Cierre Positivo': pct})
        
        if datos_cierre:
            df_cierre = pd.DataFrame(datos_cierre)
            fig = px.bar(df_cierre, x='Rango', y='% Cierre Positivo',
                        color='% Cierre Positivo',
                        color_continuous_scale=['#E74C3C', '#F1C40F', '#2ECC71'])
            fig.update_layout(
                title='% Cierre Positivo por Duración',
                height=300,
                margin=dict(t=50, b=50, l=50, r=20),
                paper_bgcolor='#FFFFFF',
                plot_bgcolor='#FAFBFC'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # =============================================================================
    # ANÁLISIS POR AGENTE
    # =============================================================================
    if 'metricas_agentes_df' in datos:
        st.markdown("---")
        st.markdown('<p class="section-header">👥 Performance de Agentes por Duración</p>', unsafe_allow_html=True)
        
        df_agentes = datos['metricas_agentes_df'].copy()
        
        # Filtro de agentes
        min_llamadas = st.slider("Mínimo de llamadas para mostrar:", 5, 50, 10)
        df_agentes = df_agentes[df_agentes['total_llamadas'] >= min_llamadas]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🚨 Top Agentes más Problemáticos**")
            df_prob = df_agentes.nlargest(10, 'pct_problema')[['agente', 'total_llamadas', 'llamadas_problema', 'pct_problema']]
            df_prob.columns = ['Agente', 'Total', 'Problemáticas', '% Problema']
            st.dataframe(df_prob, use_container_width=True, hide_index=True, height=300)
        
        with col2:
            st.markdown("**⭐ Top Agentes con Mejor Cierre**")
            df_cierre = df_agentes.nlargest(10, 'pct_cierre')[['agente', 'total_llamadas', 'cierre_positivo', 'pct_cierre']]
            df_cierre.columns = ['Agente', 'Total', 'Cierres', '% Cierre']
            st.dataframe(df_cierre, use_container_width=True, hide_index=True, height=300)
        
        st.markdown("---")
        
        # Distribución de duración por agente seleccionado
        st.markdown('<p class="section-header">📊 Distribución de Duración por Agente</p>', unsafe_allow_html=True)
        
        agentes_lista = ['Todos'] + sorted(df_agentes['agente'].dropna().astype(str).unique().tolist())
        agente_sel = st.selectbox("Seleccionar Agente:", agentes_lista)
        
        if agente_sel != 'Todos':
            agente_data = df_agentes[df_agentes['agente'] == agente_sel].iloc[0] if len(df_agentes[df_agentes['agente'] == agente_sel]) > 0 else None
            
            if agente_data is not None:
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric("📞 Total", int(agente_data['total_llamadas']))
                with col2:
                    st.metric("✅ Cierres", f"{agente_data['cierre_positivo']} ({agente_data['pct_cierre']:.1f}%)")
                with col3:
                    st.metric("📱 Ofrece Plan", f"{agente_data['con_plan']} ({agente_data['pct_con_plan']:.1f}%)")
                with col4:
                    st.metric("🌐 Ofrece Fibra", f"{agente_data['ofrece_fibra']} ({agente_data['pct_fibra']:.1f}%)")
                with col5:
                    st.metric("🚨 Problemáticas", f"{agente_data['llamadas_problema']} ({agente_data['pct_problema']:.1f}%)")
                
                # Gráfico de distribución
                duraciones = {
                    '< 1 min': int(agente_data['menos_1min']),
                    '1-3 min': int(agente_data['1_3min']),
                    '3-5 min': int(agente_data['3_5min']),
                    '5-8 min': int(agente_data['5_8min']),
                    '> 8 min': int(agente_data['mas_8min']),
                }
                
                df_dur = pd.DataFrame([{'Rango': k, 'Llamadas': v} for k, v in duraciones.items()])
                fig = px.bar(df_dur, x='Rango', y='Llamadas', color='Rango',
                            color_discrete_sequence=['#3B82F6', '#10B981', '#F59E0B', '#F97316', '#EF4444'])
                fig.update_layout(
                    height=300,
                    margin=dict(t=30, b=50, l=50, r=20),
                    paper_bgcolor='#FFFFFF',
                    plot_bgcolor='#FAFBFC',
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # =============================================================================
    # LLAMADAS PROBLEMÁTICAS DETALLE
    # =============================================================================
    st.markdown("---")
    st.markdown('<p class="section-header">🔴 Detalle de Llamadas Problemáticas</p>', unsafe_allow_html=True)
    
    st.markdown("""
    **Criterios de llamada problemática:**
    - Tiene queja del cliente y NO fue resuelta
    - Duración >= 3 min SIN ofrecer plan y SIN cierre positivo
    - Es día de promo (13-16 enero) y NO mencionó la promoción
    """)
    
    df_problematicas = df[df['es_problematica'] == True].copy() if 'es_problematica' in df.columns else pd.DataFrame()
    
    if len(df_problematicas) > 0:
        col1, col2 = st.columns([1, 3])
        
        with col1:
            tipo_filtro = st.radio("Filtrar por tipo:", 
                ['Todas', 'Con queja no resuelta', 'Sin oferta de plan', 'Sin mención promo'])
        
        with col2:
            if tipo_filtro == 'Con queja no resuelta':
                df_show = df_problematicas[(df_problematicas['tiene_queja'] == True) & (df_problematicas['queja_resuelta'] == False)]
            elif tipo_filtro == 'Sin oferta de plan':
                df_show = df_problematicas[(df_problematicas['cantidad_planes'] == 0) & (df_problematicas['duracion_seg'] >= 180)]
            elif tipo_filtro == 'Sin mención promo':
                df_show = df_problematicas[(df_problematicas['es_dia_promo'] == True) & (df_problematicas['menciona_promo'] == False)]
            else:
                df_show = df_problematicas
            
            st.metric("Llamadas encontradas", len(df_show))
        
        # Mostrar tabla
        cols_mostrar = ['archivo', 'agente', 'duracion_min', 'rango_duracion', 'resultado', 
                       'tiene_queja', 'queja_resuelta', 'planes', 'ofrece_fibra', 'menciona_promo']
        cols_existentes = [c for c in cols_mostrar if c in df_show.columns]
        
        st.dataframe(
            df_show[cols_existentes].head(100),
            use_container_width=True,
            height=400
        )
    else:
        st.info("No hay llamadas problemáticas identificadas")
    
    # =============================================================================
    # ANÁLISIS DE RESULTADO
    # =============================================================================
    st.markdown("---")
    st.markdown('<p class="section-header">📊 Distribución por Resultado</p>', unsafe_allow_html=True)
    
    if 'resultado' in df.columns:
        resultado_counts = df['resultado'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                values=resultado_counts.values,
                names=resultado_counts.index,
                color_discrete_sequence=['#10B981', '#3B82F6', '#EF4444', '#F59E0B', '#8B5CF6']
            )
            fig.update_layout(
                height=350,
                margin=dict(t=30, b=30, l=30, r=30),
                paper_bgcolor='#FFFFFF'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            df_resultado = resultado_counts.reset_index()
            df_resultado.columns = ['Resultado', 'Cantidad']
            df_resultado['%'] = (df_resultado['Cantidad'] / df_resultado['Cantidad'].sum() * 100).round(1)
            st.dataframe(df_resultado, use_container_width=True, hide_index=True, height=300)


def pagina_clasificacion_integral(datos):
    """Página de clasificación integral de llamadas"""
    mostrar_proximamente("📊 Clasificación Integral de Llamadas")
    return
    
    # === CÓDIGO COMENTADO PARA FUTURO ===
    if 'clasificacion' not in datos:
        st.warning("⚠️ No se encontraron datos de clasificación.")
        return
    
    resumen = datos['clasificacion']
    total = resumen.get('total_llamadas', 0)
    
    # =============================================================================
    # MÉTRICAS PRINCIPALES
    # =============================================================================
    st.markdown('<p class="section-header">📊 Métricas Generales</p>', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📞 Total Llamadas", f"{total:,}")
    with col2:
        ventas = resumen.get('resultados', {}).get('venta', 0)
        st.metric("✅ Ventas", f"{ventas:,} ({ventas/total*100:.1f}%)")
    with col3:
        calidad = resumen.get('calidad', {})
        score = calidad.get('score_promedio', 0)
        st.metric("⭐ Score Calidad", f"{score:.0f}/100")
    with col4:
        con_plan = resumen.get('productos', {}).get('con_plan', 0)
        st.metric("📱 Ofrecen Plan", f"{con_plan/total*100:.1f}%")
    with col5:
        quejas = resumen.get('quejas', {}).get('total', 0)
        st.metric("😤 Con Queja", f"{quejas:,}")
    
    st.markdown("---")
    
    # =============================================================================
    # TABS DE ANÁLISIS
    # =============================================================================
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Calidad", "📱 Productos", "🛑 Objeciones", "😊 Sentimiento", "🎯 Resultados"])
    
    # TAB 1: CALIDAD
    with tab1:
        st.markdown('<p class="section-header">⭐ Calidad de Atención</p>', unsafe_allow_html=True)
        
        calidad = resumen.get('calidad', {})
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            v = calidad.get('con_saludo', 0)
            st.metric("👋 Con Saludo", f"{v:,} ({v/total*100:.1f}%)")
        with col2:
            v = calidad.get('con_identificacion', 0)
            st.metric("🔍 Identificación", f"{v:,} ({v/total*100:.1f}%)")
        with col3:
            v = calidad.get('con_cierre_correcto', 0)
            st.metric("👋 Cierre Correcto", f"{v:,} ({v/total*100:.1f}%)")
        with col4:
            v = calidad.get('despedida_abrupta', 0)
            st.metric("⚠️ Despedida Abrupta", f"{v:,} ({v/total*100:.1f}%)")
        
        # Gráfico de calidad
        col1, col2 = st.columns(2)
        
        with col1:
            datos_calidad = [
                {'Indicador': 'Saludo Correcto', 'Cumple': calidad.get('con_saludo', 0), 'No Cumple': total - calidad.get('con_saludo', 0)},
                {'Indicador': 'Identificación Cliente', 'Cumple': calidad.get('con_identificacion', 0), 'No Cumple': total - calidad.get('con_identificacion', 0)},
                {'Indicador': 'Cierre Correcto', 'Cumple': calidad.get('con_cierre_correcto', 0), 'No Cumple': total - calidad.get('con_cierre_correcto', 0)},
            ]
            df_calidad = pd.DataFrame(datos_calidad)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Cumple', x=df_calidad['Indicador'], y=df_calidad['Cumple'], marker_color='#27AE60'))
            fig.add_trace(go.Bar(name='No Cumple', x=df_calidad['Indicador'], y=df_calidad['No Cumple'], marker_color='#E74C3C'))
            fig.update_layout(barmode='stack', height=300, paper_bgcolor='#FFFFFF', plot_bgcolor='#FAFBFC')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**🔴 Áreas Críticas:**")
            st.markdown(f"""
            - Solo **{calidad.get('con_identificacion', 0)/total*100:.1f}%** verifica datos del cliente
            - Solo **{calidad.get('con_cierre_correcto', 0)/total*100:.1f}%** realiza cierre correcto
            - **{calidad.get('despedida_abrupta', 0)}** llamadas con despedida abrupta
            """)
    
    # TAB 2: PRODUCTOS
    with tab2:
        st.markdown('<p class="section-header">📱 Productos Ofrecidos</p>', unsafe_allow_html=True)
        
        productos = resumen.get('productos', {})
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            v = productos.get('con_plan', 0)
            st.metric("📱 Ofrecen Plan", f"{v:,} ({v/total*100:.1f}%)")
        with col2:
            v = productos.get('con_fibra', 0)
            st.metric("🌐 Ofrecen Fibra", f"{v:,} ({v/total*100:.1f}%)")
        with col3:
            v = productos.get('con_equipo', 0)
            st.metric("📱 Ofrecen Equipo", f"{v:,} ({v/total*100:.1f}%)")
        with col4:
            v = productos.get('con_promo', 0)
            st.metric("🎁 Mencionan Promo", f"{v:,} ({v/total*100:.1f}%)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribución de planes
            por_plan = productos.get('por_plan', {})
            if por_plan:
                fig = px.pie(
                    values=list(por_plan.values()),
                    names=list(por_plan.keys()),
                    title='Distribución de Planes Ofrecidos',
                    color_discrete_sequence=['#3B82F6', '#10B981', '#F59E0B', '#EF4444']
                )
                fig.update_layout(height=300, paper_bgcolor='#FFFFFF')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**📊 Detalle por Plan:**")
            for plan, count in sorted(por_plan.items(), key=lambda x: -x[1]):
                st.markdown(f"- **{plan.upper()}**: {count:,} llamadas")
            
            # Cross-selling
            cross_sell = resumen.get('cross_sell', {})
            st.markdown("---")
            st.markdown(f"**💼 Cross-Selling:** {cross_sell.get('total', 0)} llamadas ({cross_sell.get('total', 0)/total*100:.1f}%)")
            for tipo, count in cross_sell.get('por_tipo', {}).items():
                st.markdown(f"   - {tipo}: {count}")
    
    # TAB 3: OBJECIONES
    with tab3:
        st.markdown('<p class="section-header">🛑 Objeciones del Cliente</p>', unsafe_allow_html=True)
        
        objeciones = resumen.get('objeciones', {})
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.metric("Total con Objeciones", f"{objeciones.get('total_con_objeciones', 0):,}")
            st.metric("% del Total", f"{objeciones.get('total_con_objeciones', 0)/total*100:.1f}%")
            st.metric("Agentes que Manejan", f"{objeciones.get('con_manejo', 0):,}")
        
        with col2:
            por_tipo = objeciones.get('por_tipo', {})
            if por_tipo:
                df_obj = pd.DataFrame([{'Tipo': k, 'Cantidad': v} for k, v in por_tipo.items()])
                df_obj = df_obj.sort_values('Cantidad', ascending=True)
                
                fig = px.bar(df_obj, y='Tipo', x='Cantidad', orientation='h',
                            color='Cantidad', color_continuous_scale=['#3B82F6', '#EF4444'])
                fig.update_layout(height=300, paper_bgcolor='#FFFFFF', plot_bgcolor='#FAFBFC', showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        
        # Competencia mencionada
        st.markdown("---")
        st.markdown('<p class="section-header">🏢 Competencia Mencionada</p>', unsafe_allow_html=True)
        
        competencia = resumen.get('competencia', {})
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Menciones", f"{competencia.get('total_menciones', 0):,}")
        
        with col2:
            por_empresa = competencia.get('por_empresa', {})
            for empresa, count in sorted(por_empresa.items(), key=lambda x: -x[1]):
                st.markdown(f"- **{empresa.capitalize()}**: {count:,}")
    
    # TAB 4: SENTIMIENTO
    with tab4:
        st.markdown('<p class="section-header">😊 Sentimiento del Cliente</p>', unsafe_allow_html=True)
        
        sentimiento = resumen.get('sentimiento', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            if sentimiento:
                fig = px.pie(
                    values=list(sentimiento.values()),
                    names=list(sentimiento.keys()),
                    color=list(sentimiento.keys()),
                    color_discrete_map={
                        'positivo': '#27AE60',
                        'negativo': '#E74C3C',
                        'mixto': '#F39C12',
                        'neutro': '#95A5A6'
                    }
                )
                fig.update_layout(height=350, paper_bgcolor='#FFFFFF')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**Distribución de Sentimiento:**")
            for sent, count in sorted(sentimiento.items(), key=lambda x: -x[1]):
                emoji = {'positivo': '😊', 'negativo': '😤', 'mixto': '😐', 'neutro': '😶'}.get(sent, '•')
                pct = count/total*100
                st.markdown(f"{emoji} **{sent.capitalize()}**: {count:,} ({pct:.1f}%)")
        
        # Quejas
        st.markdown("---")
        st.markdown('<p class="section-header">😤 Quejas</p>', unsafe_allow_html=True)
        
        quejas = resumen.get('quejas', {})
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total con Queja", f"{quejas.get('total', 0):,}")
        with col2:
            st.metric("Resueltas", f"{quejas.get('resueltas', 0):,}")
        with col3:
            no_res = quejas.get('no_resueltas', 0)
            total_q = quejas.get('total', 0)
            pct = no_res/total_q*100 if total_q > 0 else 0
            st.metric("No Resueltas", f"{no_res:,} ({pct:.1f}%)", delta=f"-{pct:.0f}%", delta_color="inverse")
    
    # TAB 5: RESULTADOS
    with tab5:
        st.markdown('<p class="section-header">🎯 Resultados de Llamadas</p>', unsafe_allow_html=True)
        
        resultados = resumen.get('resultados', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            if resultados:
                fig = px.pie(
                    values=list(resultados.values()),
                    names=list(resultados.keys()),
                    color_discrete_sequence=['#10B981', '#3B82F6', '#EF4444', '#F59E0B', '#8B5CF6', '#14B8A6']
                )
                fig.update_layout(height=350, paper_bgcolor='#FFFFFF')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**Distribución por Resultado:**")
            for res, count in sorted(resultados.items(), key=lambda x: -x[1]):
                pct = count/total*100
                st.markdown(f"- **{res}**: {count:,} ({pct:.1f}%)")
        
        # Problemas
        st.markdown("---")
        st.markdown('<p class="section-header">⚠️ Indicadores de Problemas</p>', unsafe_allow_html=True)
        
        problemas = resumen.get('problemas', {})
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🔄 Transferencias", f"{problemas.get('transferencias', 0):,}")
        with col2:
            st.metric("📈 Escalaciones", f"{problemas.get('escalaciones', 0):,}")
        with col3:
            st.metric("🔁 Retención", f"{resumen.get('retencion', 0):,}")
    
    # =============================================================================
    # ANÁLISIS POR AGENTE
    # =============================================================================
    if 'clasificacion_agentes_df' in datos:
        st.markdown("---")
        st.markdown('<p class="section-header">👥 Ranking de Agentes</p>', unsafe_allow_html=True)
        
        df_agentes = datos['clasificacion_agentes_df'].copy()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**⭐ Top 10 por Tasa de Venta:**")
            top_ventas = df_agentes.nlargest(10, 'pct_ventas')[['agente', 'total', 'ventas', 'pct_ventas']]
            top_ventas.columns = ['Agente', 'Total', 'Ventas', '% Ventas']
            st.dataframe(top_ventas, use_container_width=True, hide_index=True, height=300)
        
        with col2:
            st.markdown("**⭐ Top 10 por Score Calidad:**")
            top_calidad = df_agentes.nlargest(10, 'score_calidad_prom')[['agente', 'total', 'score_calidad_prom']]
            top_calidad.columns = ['Agente', 'Total', 'Score Calidad']
            st.dataframe(top_calidad, use_container_width=True, hide_index=True, height=300)


def pagina_evaluaciones_gemini(datos):
    """Página de evaluaciones realizadas con Inteligencia Artificial"""
    st.markdown('<div class="main-header">🤖 Evaluaciones con Inteligencia Artificial</div>', unsafe_allow_html=True)
    
    # Verificar datos
    if 'evaluaciones_gemini_df' not in datos:
        st.warning("⚠️ No se encontraron evaluaciones de IA disponibles.")
        st.info("💡 Los datos de evaluación no están disponibles actualmente.")
        
        # Mostrar progreso si existe el archivo parcial
        import os
        if os.path.exists('reportes/evaluaciones_gemini.csv'):
            try:
                df_parcial = pd.read_csv('reportes/evaluaciones_gemini.csv')
                st.success(f"📊 Progreso actual: {len(df_parcial):,} evaluaciones completadas")
            except:
                pass
        return
    
    df = datos['evaluaciones_gemini_df'].copy()
    
    # Cargar nombres de vendedores
    listado_vendedores = {}
    try:
        df_listado = pd.read_csv('LISTADO-DE-VENDEDORES.csv', header=0)
        for _, row in df_listado.iterrows():
            usuario = str(row.iloc[0]).strip().lower().replace('\t', '').replace(' ', '')
            nombre = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
            if usuario and nombre and usuario != 'usuario':
                listado_vendedores[usuario] = nombre.title()
    except:
        pass
    
    def obtener_nombre_agente(agente_id):
        """Convierte ID de agente a nombre real"""
        agente_normalizado = str(agente_id).lower().replace(' ', '').replace('_', '')
        return listado_vendedores.get(agente_normalizado, agente_id)
    
    # Aplicar mapeo de nombres a todo el dataframe
    if 'agente' in df.columns:
        df['agente'] = df['agente'].apply(obtener_nombre_agente)
    
    # Definir criterios y nombres
    criterios = ['saludo_presentacion', 'identificacion_cliente', 'deteccion_necesidades',
                 'oferta_productos', 'manejo_objeciones', 'cierre', 'despedida',
                 'proactividad', 'empatia', 'resolucion_problemas']
    
    criterios_nombres = {
        'saludo_presentacion': 'Saludo y Presentación',
        'identificacion_cliente': 'Identificación Cliente',
        'deteccion_necesidades': 'Detección Necesidades',
        'oferta_productos': 'Oferta de Productos',
        'manejo_objeciones': 'Manejo de Objeciones',
        'cierre': 'Cierre de Venta',
        'despedida': 'Despedida',
        'proactividad': 'Proactividad',
        'empatia': 'Empatía',
        'resolucion_problemas': 'Resolución Problemas'
    }
    
    # =============================================================================
    # TABS PRINCIPALES
    # =============================================================================
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Vista General", "👤 Análisis por Agente", "🎯 Criterios Detallados", "🔍 Explorador"])
    
    with tab1:
        # =============================================================================
        # MÉTRICAS PRINCIPALES
        # =============================================================================
        st.markdown('<p class="section-header">📈 Métricas Generales de Evaluación IA</p>', unsafe_allow_html=True)
        
        total = len(df)
        puntaje_promedio = df['puntaje_total'].mean()
        
        # Clasificar por rangos de puntaje
        df['rango_puntaje'] = pd.cut(df['puntaje_total'], 
                                      bins=[-1, 20, 40, 60, 80, 100],
                                      labels=['Crítico (0-20)', 'Bajo (21-40)', 'Regular (41-60)', 'Bueno (61-80)', 'Excelente (81-100)'])
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("📊 Total Evaluadas", f"{total:,}")
        with col2:
            color = "🔴" if puntaje_promedio < 40 else "🟡" if puntaje_promedio < 60 else "🟢"
            st.metric(f"{color} Puntaje Promedio", f"{puntaje_promedio:.1f}/100")
        with col3:
            excelentes = len(df[df['puntaje_total'] >= 80])
            st.metric("🌟 Excelentes (80+)", f"{excelentes:,} ({excelentes/total*100:.1f}%)")
        with col4:
            criticos = len(df[df['puntaje_total'] <= 20])
            st.metric("🔴 Críticos (≤20)", f"{criticos:,} ({criticos/total*100:.1f}%)")
        with col5:
            cero = len(df[df['puntaje_total'] == 0])
            st.metric("⚠️ Puntaje 0", f"{cero:,} ({cero/total*100:.1f}%)")
        
        # Distribución de puntajes
        st.markdown("---")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.histogram(
                df, 
                x='puntaje_total',
                nbins=20,
                title="Distribución de Puntajes Totales",
                labels={'puntaje_total': 'Puntaje', 'count': 'Cantidad'},
                color_discrete_sequence=['#3B82F6']
            )
            fig.add_vline(x=puntaje_promedio, line_dash="dash", line_color="#EF4444", 
                          annotation_text=f"Promedio: {puntaje_promedio:.1f}")
            fig.update_layout(
                height=400, 
                paper_bgcolor='#FFFFFF',
                plot_bgcolor='#FAFBFC',
                font=dict(color='#1E293B', size=12),
                title_font=dict(color='#1E3A5F', size=14, family='Arial Black')
            )
            fig.update_xaxes(tickfont=dict(color='#1E293B', size=11), title_font=dict(color='#1E3A5F'))
            fig.update_yaxes(tickfont=dict(color='#1E293B', size=11), title_font=dict(color='#1E3A5F'))
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            rango_counts = df['rango_puntaje'].value_counts()
            fig = px.pie(
                values=rango_counts.values,
                names=rango_counts.index,
                title="Distribución por Rango",
                color_discrete_sequence=['#E74C3C', '#F39C12', '#F1C40F', '#27AE60', '#2ECC71']
            )
            fig.update_layout(
                height=400, 
                paper_bgcolor='#FFFFFF',
                font=dict(color='#1E293B', size=12),
                title_font=dict(color='#1E3A5F', size=14, family='Arial Black')
            )
            fig.update_traces(textfont=dict(color='#1E293B', size=11))
            st.plotly_chart(fig, use_container_width=True)
        
        # Ranking de agentes resumen
        st.markdown("---")
        st.markdown('<p class="section-header">👥 Ranking Rápido de Agentes</p>', unsafe_allow_html=True)
        
        if 'agente' in df.columns:
            df_agentes_resumen = df.groupby('agente').agg({
                'puntaje_total': ['mean', 'count']
            }).round(1)
            df_agentes_resumen.columns = ['Puntaje_Prom', 'Evaluaciones']
            df_agentes_resumen = df_agentes_resumen.reset_index()
            df_agentes_resumen = df_agentes_resumen[df_agentes_resumen['Evaluaciones'] >= 5]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🏆 Top 10 Mejores:**")
                top_10 = df_agentes_resumen.nlargest(10, 'Puntaje_Prom')
                fig = px.bar(
                    top_10,
                    x='Puntaje_Prom',
                    y='agente',
                    orientation='h',
                    color='Puntaje_Prom',
                    color_continuous_scale='Greens',
                    text='Puntaje_Prom'
                )
                fig.update_traces(texttemplate='%{text:.1f}', textposition='outside', textfont=dict(color='#1E293B', size=11))
                fig.update_layout(
                    height=350, 
                    paper_bgcolor='#FFFFFF', 
                    plot_bgcolor='#FAFBFC',
                    showlegend=False,
                    yaxis={'categoryorder': 'total ascending'},
                    font=dict(color='#1E293B', size=11)
                )
                fig.update_xaxes(tickfont=dict(color='#1E293B', size=10))
                fig.update_yaxes(tickfont=dict(color='#1E293B', size=10))
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("**⚠️ 10 Necesitan Mejora:**")
                bottom_10 = df_agentes_resumen.nsmallest(10, 'Puntaje_Prom')
                fig = px.bar(
                    bottom_10,
                    x='Puntaje_Prom',
                    y='agente',
                    orientation='h',
                    color='Puntaje_Prom',
                    color_continuous_scale='Reds_r',
                    text='Puntaje_Prom'
                )
                fig.update_traces(texttemplate='%{text:.1f}', textposition='outside', textfont=dict(color='#1E293B', size=11))
                fig.update_layout(
                    height=350, 
                    paper_bgcolor='#FFFFFF', 
                    plot_bgcolor='#FAFBFC',
                    showlegend=False,
                    yaxis={'categoryorder': 'total descending'},
                    font=dict(color='#1E293B', size=11)
                )
                fig.update_xaxes(tickfont=dict(color='#1E293B', size=10))
                fig.update_yaxes(tickfont=dict(color='#1E293B', size=10))
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # =============================================================================
        # ANÁLISIS DETALLADO POR AGENTE
        # =============================================================================
        st.markdown('<p class="section-header">👤 Selecciona un Agente para Ver su Análisis Detallado</p>', unsafe_allow_html=True)
        
        if 'agente' in df.columns:
            agentes_list = sorted(df['agente'].dropna().unique().tolist())
            agente_seleccionado = st.selectbox("Selecciona un agente:", agentes_list, key='agente_gemini')
            
            # Filtrar datos del agente
            df_agente = df[df['agente'] == agente_seleccionado].copy()
            total_agente = len(df_agente)
            
            if total_agente > 0:
                puntaje_agente = df_agente['puntaje_total'].mean()
                
                # Métricas del agente
                st.markdown("---")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📊 Llamadas Evaluadas", f"{total_agente:,}")
                with col2:
                    diff_vs_prom = puntaje_agente - puntaje_promedio
                    st.metric("🎯 Puntaje Promedio", f"{puntaje_agente:.1f}/100", 
                              delta=f"{diff_vs_prom:+.1f} vs general")
                with col3:
                    excelentes_ag = len(df_agente[df_agente['puntaje_total'] >= 80])
                    st.metric("🌟 Llamadas Excelentes", f"{excelentes_ag} ({excelentes_ag/total_agente*100:.1f}%)")
                with col4:
                    criticos_ag = len(df_agente[df_agente['puntaje_total'] <= 20])
                    st.metric("🔴 Llamadas Críticas", f"{criticos_ag} ({criticos_ag/total_agente*100:.1f}%)")
                
                # Gráficos del agente
                st.markdown("---")
                col1, col2 = st.columns(2)
                
                with col1:
                    # Radar de criterios del agente
                    st.markdown("**📊 Perfil de Competencias:**")
                    
                    criterios_agente = {}
                    for c in criterios:
                        if c in df_agente.columns:
                            criterios_agente[criterios_nombres.get(c, c)] = df_agente[c].mean()
                    
                    if criterios_agente:
                        categories = list(criterios_agente.keys())
                        values_agente = list(criterios_agente.values())
                        
                        # Calcular valores generales para comparación
                        values_general = [df[c].mean() if c in df.columns else 0 for c in criterios]
                        
                        fig = go.Figure()
                        
                        # Agente seleccionado
                        fig.add_trace(go.Scatterpolar(
                            r=values_agente + [values_agente[0]],
                            theta=categories + [categories[0]],
                            fill='toself',
                            name=agente_seleccionado,
                            line_color='#3B82F6',
                            line_width=3,
                            fillcolor='rgba(59, 130, 246, 0.5)'
                        ))
                        
                        # Promedio general
                        fig.add_trace(go.Scatterpolar(
                            r=values_general + [values_general[0]],
                            theta=categories + [categories[0]],
                            fill='toself',
                            name='Promedio General',
                            line_color='#EF4444',
                            line_width=2,
                            fillcolor='rgba(239, 68, 68, 0.25)'
                        ))
                        
                        fig.update_layout(
                            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                            showlegend=True,
                            height=400,
                            paper_bgcolor='#FFFFFF'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Distribución de puntajes del agente
                    st.markdown("**📈 Distribución de Puntajes:**")
                    
                    fig = px.histogram(
                        df_agente,
                        x='puntaje_total',
                        nbins=10,
                        color_discrete_sequence=['#27AE60']
                    )
                    fig.add_vline(x=puntaje_agente, line_dash="dash", line_color="blue",
                                  annotation_text=f"Promedio: {puntaje_agente:.1f}")
                    fig.add_vline(x=puntaje_promedio, line_dash="dot", line_color="red",
                                  annotation_text=f"General: {puntaje_promedio:.1f}")
                    fig.update_layout(height=400, paper_bgcolor='#FFFFFF',
                                      xaxis_title="Puntaje", yaxis_title="Cantidad")
                    st.plotly_chart(fig, use_container_width=True)
                
                # Barras comparativas por criterio
                st.markdown("---")
                st.markdown("**📊 Comparación por Criterio vs Promedio General:**")
                
                comparacion_data = []
                for c in criterios:
                    if c in df_agente.columns and c in df.columns:
                        comparacion_data.append({
                            'Criterio': criterios_nombres.get(c, c),
                            'Agente': df_agente[c].mean(),
                            'General': df[c].mean()
                        })
                
                if comparacion_data:
                    df_comp = pd.DataFrame(comparacion_data)
                    df_comp_melted = df_comp.melt(id_vars=['Criterio'], var_name='Tipo', value_name='Puntaje')
                    
                    fig = px.bar(
                        df_comp_melted,
                        x='Criterio',
                        y='Puntaje',
                        color='Tipo',
                        barmode='group',
                        color_discrete_map={'Agente': '#3B82F6', 'General': '#EF4444'}
                    )
                    fig.update_layout(height=400, paper_bgcolor='#FFFFFF', xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Tabla de evaluaciones del agente
                st.markdown("---")
                st.markdown("**📋 Últimas Evaluaciones del Agente:**")
                
                columnas_tabla = ['archivo', 'puntaje_total', 'resumen', 'areas_mejora', 'fortalezas']
                columnas_disponibles = [c for c in columnas_tabla if c in df_agente.columns]
                
                df_mostrar = df_agente[columnas_disponibles].sort_values('puntaje_total', ascending=False)
                st.dataframe(df_mostrar.head(20), use_container_width=True, hide_index=True, height=400)
                
                # Áreas de mejora específicas del agente
                if 'areas_mejora' in df_agente.columns:
                    st.markdown("---")
                    st.markdown("**🎯 Áreas de Mejora Recurrentes de Este Agente:**")
                    
                    from collections import Counter
                    areas_agente = []
                    for areas in df_agente['areas_mejora'].dropna():
                        if isinstance(areas, str):
                            for area in areas.split(','):
                                area = area.strip().strip('"').strip("'").strip('[').strip(']')
                                if area:
                                    areas_agente.append(area)
                    
                    if areas_agente:
                        area_counts = Counter(areas_agente)
                        top_areas_agente = area_counts.most_common(10)
                        
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            df_areas = pd.DataFrame(top_areas_agente, columns=['Área', 'Frecuencia'])
                            fig = px.bar(
                                df_areas,
                                x='Frecuencia',
                                y='Área',
                                orientation='h',
                                color='Frecuencia',
                                color_continuous_scale='Oranges'
                            )
                            fig.update_layout(height=350, paper_bgcolor='#FFFFFF', 
                                              yaxis={'categoryorder': 'total ascending'})
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            st.markdown("**📝 Plan de Capacitación Sugerido:**")
                            for i, (area, freq) in enumerate(top_areas_agente[:5], 1):
                                st.markdown(f"{i}. **{area}** ({freq} veces)")
    
    with tab3:
        # =============================================================================
        # ANÁLISIS DETALLADO POR CRITERIO
        # =============================================================================
        st.markdown('<p class="section-header">🎯 Análisis Detallado por Criterio de Evaluación</p>', unsafe_allow_html=True)
        
        # Calcular promedios por criterio
        promedios = {}
        for c in criterios:
            if c in df.columns:
                promedios[criterios_nombres.get(c, c)] = df[c].mean()
        
        if promedios:
            # Gráfico de barras horizontal
            df_criterios = pd.DataFrame({
                'Criterio': list(promedios.keys()),
                'Puntaje': list(promedios.values())
            }).sort_values('Puntaje', ascending=True)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = px.bar(
                    df_criterios,
                    y='Criterio',
                    x='Puntaje',
                    orientation='h',
                    title="Puntaje Promedio por Criterio",
                    color='Puntaje',
                    color_continuous_scale=['#E74C3C', '#F39C12', '#27AE60']
                )
                fig.update_layout(height=450, paper_bgcolor='#FFFFFF', showlegend=False)
                fig.add_vline(x=50, line_dash="dash", line_color="gray", annotation_text="Meta: 50")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("**📋 Detalle por Criterio:**")
                for criterio, puntaje in sorted(promedios.items(), key=lambda x: -x[1]):
                    emoji = "🟢" if puntaje >= 50 else "🟡" if puntaje >= 30 else "🔴"
                    st.markdown(f"{emoji} **{criterio}**: {puntaje:.1f}/100")
        
        # Box plot por criterio
        st.markdown("---")
        st.markdown("**📊 Distribución de Puntajes por Criterio:**")
        
        criterios_disponibles = [c for c in criterios if c in df.columns]
        if criterios_disponibles:
            df_box = df[criterios_disponibles].melt(var_name='Criterio', value_name='Puntaje')
            df_box['Criterio'] = df_box['Criterio'].map(criterios_nombres)
            
            fig = px.box(
                df_box,
                x='Criterio',
                y='Puntaje',
                color='Criterio',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(height=450, paper_bgcolor='#FFFFFF', showlegend=False, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Áreas de mejora más frecuentes
        st.markdown("---")
        st.markdown('<p class="section-header">📝 Áreas de Mejora Identificadas por IA</p>', unsafe_allow_html=True)
        
        if 'areas_mejora' in df.columns:
            from collections import Counter
            all_areas = []
            for areas in df['areas_mejora'].dropna():
                if isinstance(areas, str):
                    for area in areas.split(','):
                        area = area.strip().strip('"').strip("'").strip('[').strip(']')
                        if area:
                            all_areas.append(area)
            
            if all_areas:
                area_counts = Counter(all_areas)
                top_areas = area_counts.most_common(15)
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    df_areas = pd.DataFrame(top_areas, columns=['Área', 'Frecuencia'])
                    fig = px.bar(
                        df_areas,
                        x='Frecuencia',
                        y='Área',
                        orientation='h',
                        title="Top 15 Áreas de Mejora Identificadas",
                        color='Frecuencia',
                        color_continuous_scale='Reds'
                    )
                    fig.update_layout(height=450, paper_bgcolor='#FFFFFF', yaxis={'categoryorder': 'total ascending'})
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.markdown("**🎯 Prioridades de Capacitación:**")
                    for i, (area, freq) in enumerate(top_areas[:10], 1):
                        pct = freq / total * 100
                        st.markdown(f"{i}. **{area}**: {freq:,} ({pct:.1f}%)")
    
    with tab4:
        # =============================================================================
        # EXPLORADOR DE EVALUACIONES
        # =============================================================================
        st.markdown('<p class="section-header">🔍 Explorador de Evaluaciones</p>', unsafe_allow_html=True)
        
        # Asegurar que rango_puntaje existe
        if 'rango_puntaje' not in df.columns:
            df['rango_puntaje'] = pd.cut(df['puntaje_total'], 
                                          bins=[-1, 20, 40, 60, 80, 100],
                                          labels=['Crítico (0-20)', 'Bajo (21-40)', 'Regular (41-60)', 'Bueno (61-80)', 'Excelente (81-100)'])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            rangos_lista = ['Todos'] + [r for r in df['rango_puntaje'].dropna().unique().tolist() if pd.notna(r)]
            filtro_rango = st.selectbox("Filtrar por rango:", rangos_lista, key='filtro_rango_exp')
        with col2:
            if 'agente' in df.columns:
                agentes_list = ['Todos'] + sorted(df['agente'].dropna().unique().tolist())
                filtro_agente = st.selectbox("Filtrar por agente:", agentes_list, key='filtro_agente_exp')
            else:
                filtro_agente = 'Todos'
        with col3:
            orden = st.selectbox("Ordenar por:", ['Puntaje (menor a mayor)', 'Puntaje (mayor a menor)'], key='orden_exp')
        
        df_filtrado = df.copy()
        if filtro_rango != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['rango_puntaje'] == filtro_rango]
        if filtro_agente != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['agente'] == filtro_agente]
        
        ascending = 'menor' in orden
        df_filtrado = df_filtrado.sort_values('puntaje_total', ascending=ascending)
        
        st.markdown(f"**Mostrando {len(df_filtrado):,} evaluaciones:**")
        
        # Tabla expandida
        columnas_mostrar = ['archivo', 'agente', 'puntaje_total', 'saludo_presentacion', 
                           'cierre', 'oferta_productos', 'resumen']
        columnas_disponibles = [c for c in columnas_mostrar if c in df_filtrado.columns]
        
        st.dataframe(
            df_filtrado[columnas_disponibles].head(100),
            use_container_width=True,
            hide_index=True,
            height=500
        )
        
        # Detalle de una evaluación específica
        st.markdown("---")
        st.markdown("**📄 Ver Detalle de Evaluación Específica:**")
        
        if len(df_filtrado) > 0:
            archivos_lista = df_filtrado['archivo'].tolist()[:50]
            archivo_sel = st.selectbox("Selecciona un archivo:", archivos_lista, key='archivo_detalle')
            
            eval_sel = df_filtrado[df_filtrado['archivo'] == archivo_sel].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Archivo:** {eval_sel['archivo']}")
                st.markdown(f"**Agente:** {eval_sel.get('agente', 'N/A')}")
                st.markdown(f"**Puntaje Total:** {eval_sel['puntaje_total']}/100")
                st.markdown(f"**Resumen:** {eval_sel.get('resumen', 'N/A')}")
            
            with col2:
                st.markdown("**Puntajes por Criterio:**")
                for c in criterios:
                    if c in eval_sel.index:
                        valor = eval_sel[c]
                        emoji = "🟢" if valor >= 50 else "🟡" if valor >= 30 else "🔴"
                        st.markdown(f"{emoji} {criterios_nombres.get(c, c)}: **{valor}**")


def main():
    """Función principal del dashboard"""
    
    # Cargar datos
    with st.spinner('Cargando datos...'):
        datos = cargar_datos()
    
    if 'transcripciones' not in datos or not datos['transcripciones']:
        st.error("No se encontraron transcripciones procesadas. Asegúrate de tener archivos en 'total_transcripciones/procesados/'")
        return
    
    # Crear DataFrame de llamadas
    df = crear_df_llamadas(datos['transcripciones'])
    
    # Sidebar - Logo EVA
    st.sidebar.markdown("""
    <div class="eva-logo-container">
        <div class="eva-title">🦉 EVA</div>
        <div class="eva-subtitle">Evaluador Virtual de Auditoría</div>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📊 Navegación")
    
    paginas = {
        "🏠 Resumen Ejecutivo": "resumen",
        "📋 Cierres Comerciales": "cierres",
        "📱 Planes y Fibra": "planes",
        "😤 Quejas No Resueltas": "quejas",
        "⏱️ Análisis Duración": "duracion",
        "🔮 Clasificación Integral": "clasificacion",
        "🤖 Evaluaciones IA": "gemini",
        "🎯 Coaching IA": "coaching",
        "👥 Performance Agentes": "agentes",
        "📅 Análisis Temporal": "temporal",
        "🔍 Explorador de Llamadas": "detalle"
    }
    
    seleccion = st.sidebar.radio("Selecciona una sección:", list(paginas.keys()))
    
    # Info adicional en sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Resumen Rápido")
    st.sidebar.markdown(f"**Total llamadas:** {len(df):,}")
    if 'dia' in df.columns and df['dia'].notna().any():
        fecha_min = df['dia'].dropna().min()
        fecha_max = df['dia'].dropna().max()
        st.sidebar.markdown(f"**Período:** {fecha_min} a {fecha_max}")
    st.sidebar.markdown(f"**Agentes:** {df['agente'].nunique()}")
    
    # Renderizar página seleccionada
    if paginas[seleccion] == "resumen":
        pagina_resumen_ejecutivo(datos, df)
    elif paginas[seleccion] == "cierres":
        pagina_cierres_comerciales(datos)
    elif paginas[seleccion] == "planes":
        pagina_planes_ofrecidos(datos, df)
    elif paginas[seleccion] == "quejas":
        pagina_quejas_no_resueltas(datos)
    elif paginas[seleccion] == "duracion":
        pagina_analisis_duracion(datos)
    elif paginas[seleccion] == "clasificacion":
        pagina_clasificacion_integral(datos)
    elif paginas[seleccion] == "gemini":
        pagina_evaluaciones_gemini(datos)
    elif paginas[seleccion] == "coaching":
        pagina_coaching_vendedores(datos)
    elif paginas[seleccion] == "agentes":
        pagina_performance_agentes(df, datos)
    elif paginas[seleccion] == "temporal":
        pagina_analisis_temporal(df)
    elif paginas[seleccion] == "detalle":
        pagina_detalle_llamadas(df, datos)
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"<small>EVA Dashboard v1.0<br>Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M')}</small>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()

"""
COMMAND - Sistema de Rendimiento Comercial

Dashboard ejecutivo para auditoría de equipos de venta.
Interfaz profesional para presentaciones corporativas.
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
    page_title="COMMAND - Sistema de Rendimiento Comercial",
    page_icon="📈",
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
    
    /* Radio buttons en contenido principal - ALTO CONTRASTE */
    [data-testid="stHorizontalBlock"] .stRadio > label {
        color: #1E293B !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
    }
    
    [data-testid="stHorizontalBlock"] .stRadio [role="radiogroup"] label {
        background-color: #FFFFFF !important;
        border: 2px solid #CBD5E1 !important;
        border-radius: 8px !important;
        padding: 10px 16px !important;
        margin: 4px 8px 4px 0 !important;
        transition: all 0.2s ease !important;
    }
    
    [data-testid="stHorizontalBlock"] .stRadio [role="radiogroup"] label:hover {
        background-color: #EFF6FF !important;
        border-color: #3B82F6 !important;
    }
    
    [data-testid="stHorizontalBlock"] .stRadio [role="radiogroup"] label div p {
        color: #1E293B !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    
    [data-testid="stHorizontalBlock"] .stRadio [role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {
        background-color: #3B82F6 !important;
        border-color: #3B82F6 !important;
    }
    
    [data-testid="stHorizontalBlock"] .stRadio [role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) div p {
        color: #FFFFFF !important;
    }
    
    /* Logo COMMAND en sidebar */
    .command-logo-container {
        text-align: center;
        padding: 1rem;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #0F172A 0%, #1E3A5F 100%);
        border-radius: 12px;
        margin: 0.5rem;
    }

    .command-logo-container img {
        max-width: 80px;
    }
    
    .command-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #60A5FA !important;
        text-align: center;
        margin-top: 0.5rem;
        letter-spacing: 3px;
    }
    
    .command-subtitle {
        font-size: 0.75rem;
        color: #94A3B8 !important;
        text-align: center;
        margin-top: -0.1rem;
        letter-spacing: 1px;
        text-transform: uppercase;
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


# Directorio base de la aplicación
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Variables y helpers para precarga de datos en background
_DATOS_PRELOAD = None
_DATOS_LOADING = False

def cargar_datos_io():
    """Versión pura de IO de carga de datos sin usar Streamlit ni decoradores.
    Usa la misma lógica que carga_datos() pero sin interacciones con Streamlit.
    """
    datos = {}

    # Cargar evaluaciones primero para saber qué archivos cargar
    ruta_eval = os.path.join(BASE_DIR, 'reportes/evaluaciones_gemini.csv')
    archivos_evaluados = set()
    if os.path.exists(ruta_eval):
        try:
            df_eval = pd.read_csv(ruta_eval)
            archivos_evaluados = set(df_eval['archivo'].tolist())
        except Exception:
            pass

    # Cargar transcripciones mejoradas (solo las que tienen evaluación)
    carpeta = os.path.join(BASE_DIR, "transcripts/mejorados_gemini")
    if os.path.exists(carpeta):
        transcripciones = []
        for archivo in os.listdir(carpeta):
            if archivo.endswith('.json') and archivo in archivos_evaluados:
                try:
                    with open(os.path.join(carpeta, archivo), 'r', encoding='utf-8') as f:
                        transcripciones.append(json.load(f))
                except Exception:
                    continue
        datos['transcripciones'] = transcripciones

    # Cargar resumen de cierres
    ruta_cierres = os.path.join(BASE_DIR, 'reportes/cierres_comerciales/resumen_cierres.json')
    if os.path.exists(ruta_cierres):
        try:
            with open(ruta_cierres, 'r', encoding='utf-8') as f:
                datos['cierres'] = json.load(f)
        except Exception:
            datos['cierres'] = None

    # Cargar CSV de cierres
    ruta = os.path.join(BASE_DIR, 'reportes/cierres_comerciales/cierres_comerciales.csv')
    if os.path.exists(ruta):
        try:
            datos['cierres_df'] = pd.read_csv(ruta, sep=';')
        except Exception:
            datos['cierres_df'] = None

    # Cargar resumen de planes
    ruta = os.path.join(BASE_DIR, 'reportes/planes/resumen_planes.json')
    if os.path.exists(ruta):
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                datos['planes_resumen'] = json.load(f)
        except Exception:
            datos['planes_resumen'] = None

    # Cargar para_gemini CSV
    ruta = os.path.join(BASE_DIR, 'reportes/para_gemini/datos_consolidados_para_gemini.csv')
    if os.path.exists(ruta):
        try:
            datos['para_gemini'] = pd.read_csv(ruta)
        except Exception:
            datos['para_gemini'] = None

    # Cargar evaluaciones
    ruta = os.path.join(BASE_DIR, 'reportes/evaluaciones_gemini.csv')
    if os.path.exists(ruta):
        try:
            df_eval = pd.read_csv(ruta)
            datos['evaluaciones'] = df_eval
            datos['evaluaciones_gemini_df'] = df_eval
        except Exception:
            datos['evaluaciones'] = None
            datos['evaluaciones_gemini_df'] = None

    return datos


def iniciar_preload_datos():
    """Inicia la carga de datos en un thread de fondo para no bloquear la UI.
    Guarda el resultado en la variable global _DATOS_PRELOAD.
    Usa la versión IO para evitar que Streamlit muestre mensajes internos como "Running cargar_datos()".
    """
    global _DATOS_PRELOAD, _DATOS_LOADING
    import threading
    if _DATOS_LOADING or _DATOS_PRELOAD is not None:
        return
    def _bg():
        global _DATOS_PRELOAD, _DATOS_LOADING
        _DATOS_LOADING = True
        try:
            _DATOS_PRELOAD = cargar_datos_io()
        finally:
            _DATOS_LOADING = False

    th = threading.Thread(target=_bg, daemon=True)
    th.start()

# Mapeo de nombres de criterios para gráficos
CRITERIOS_NOMBRES = {
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

# =============================================================================
# SISTEMA DE AUTENTICACIÓN Y ROLES
# =============================================================================
import hashlib

def hash_password(password):
    """Genera hash SHA-256 de la contraseña"""
    return hashlib.sha256(password.encode()).hexdigest()

# Definición de usuarios y roles
# Roles: admin (acceso total), supervisor (acceso equipo), vendedor (solo sus datos)
USUARIOS = {
    'matias': {
        'password_hash': hash_password('mercurio'),
        'nombre': 'Matias',
        'rol': 'admin',
        'equipo': None,  # Admin tiene acceso a todo
        'permisos': ['dashboard', 'coaching', 'evaluaciones', 'reportes', 'config', 'todos_agentes']
    },
    # ========================================
    # SUPERVISORES
    # ========================================
    'byl': {
        'password_hash': hash_password('Kp7mNx2w'),
        'nombre': 'Byl',
        'rol': 'supervisor',
        'equipo': 'BYL',
        'permisos': ['dashboard', 'coaching', 'evaluaciones', 'reportes']
    },
    'diana': {
        'password_hash': hash_password('Qr9sVt4y'),
        'nombre': 'Diana',
        'rol': 'supervisor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'coaching', 'evaluaciones', 'reportes']
    },
    'marina': {
        'password_hash': hash_password('Hj6bLm3c'),
        'nombre': 'Marina',
        'rol': 'supervisor',
        'equipo': 'MARINA MARTINEZ',
        'permisos': ['dashboard', 'coaching', 'evaluaciones', 'reportes']
    },
    'calidad': {
        'password_hash': hash_password('Wd8fPn5z'),
        'nombre': 'Calidad',
        'rol': 'supervisor',
        'equipo': None,
        'permisos': ['dashboard', 'coaching', 'evaluaciones', 'reportes', 'calidad']
    },
    'melani': {
        'password_hash': hash_password('Yx3gRk7v'),
        'nombre': 'Melani',
        'rol': 'supervisor',
        'equipo': 'MELANIE CARMONA',
        'permisos': ['dashboard', 'coaching', 'evaluaciones', 'reportes']
    },
    'josefina': {
        'password_hash': hash_password('Nt5cWq8m'),
        'nombre': 'Josefina',
        'rol': 'supervisor',
        'equipo': 'JOSEFINA ZEBALLOS',
        'permisos': ['dashboard', 'coaching', 'evaluaciones', 'reportes']
    },
    'yasmin': {
        'password_hash': hash_password('Bv2jHs6p'),
        'nombre': 'Yasmin',
        'rol': 'supervisor',
        'equipo': 'ARENAS YASMIN',
        'permisos': ['dashboard', 'coaching', 'evaluaciones', 'reportes']
    },
    'nati': {
        'password_hash': hash_password('Zf4dKt9r'),
        'nombre': 'Nati',
        'rol': 'supervisor',
        'equipo': 'NATALI SANCHE',
        'permisos': ['dashboard', 'coaching', 'evaluaciones', 'reportes']
    },
    'capacitacion': {
        'password_hash': hash_password('Mc7xJn2b'),
        'nombre': 'Capacitación',
        'rol': 'supervisor',
        'equipo': None,
        'permisos': ['dashboard', 'coaching', 'evaluaciones', 'reportes']
    },
    # ========================================
    # VENDEDORES EQUIPO DIANA
    # ========================================
    'mza46': {
        'password_hash': hash_password('Vk3pRw7n'),
        'nombre': 'MZA 46',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza47': {
        'password_hash': hash_password('Ht9cBm2x'),
        'nombre': 'MZA 47',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza48': {
        'password_hash': hash_password('Qf5jNs8d'),
        'nombre': 'MZA 48',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza49': {
        'password_hash': hash_password('Lw6gKp4v'),
        'nombre': 'MZA 49',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza50': {
        'password_hash': hash_password('Zy2mXt9c'),
        'nombre': 'MZA 50',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza51': {
        'password_hash': hash_password('Rn8bPq3f'),
        'nombre': 'MZA 51',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mzasup5': {
        'password_hash': hash_password('Ds4hWk7j'),
        'nombre': 'MZA Sup5',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza52': {
        'password_hash': hash_password('Gx7rLn2s'),
        'nombre': 'MZA 52',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza53': {
        'password_hash': hash_password('Jm3vCt8p'),
        'nombre': 'MZA 53',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza54': {
        'password_hash': hash_password('Pw9dFk4y'),
        'nombre': 'MZA 54',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza55': {
        'password_hash': hash_password('Tb6nHq2w'),
        'nombre': 'MZA 55',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza56': {
        'password_hash': hash_password('Xc2sJm7r'),
        'nombre': 'MZA 56',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza57': {
        'password_hash': hash_password('Kf8pBx3g'),
        'nombre': 'MZA 57',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza58': {
        'password_hash': hash_password('Nq4wRt9h'),
        'nombre': 'MZA 58',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza59': {
        'password_hash': hash_password('Ys7kMn2c'),
        'nombre': 'MZA 59',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza60': {
        'password_hash': hash_password('Bd3fVp8x'),
        'nombre': 'MZA 60',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza61': {
        'password_hash': hash_password('Wt9jLs4n'),
        'nombre': 'MZA 61',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza62': {
        'password_hash': hash_password('Hk6cQw2v'),
        'nombre': 'MZA 62',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza63': {
        'password_hash': hash_password('Rm2xGt7b'),
        'nombre': 'MZA 63',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza64': {
        'password_hash': hash_password('Fp8nYk3d'),
        'nombre': 'MZA 64',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza65': {
        'password_hash': hash_password('Cs4rDm9j'),
        'nombre': 'MZA 65',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza66': {
        'password_hash': hash_password('Vn7hPw2f'),
        'nombre': 'MZA 66',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza67': {
        'password_hash': hash_password('Zq3kXt8s'),
        'nombre': 'MZA 67',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza68': {
        'password_hash': hash_password('Jw9bNc4p'),
        'nombre': 'MZA 68',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza69': {
        'password_hash': hash_password('Mx6gRs2y'),
        'nombre': 'MZA 69',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza70': {
        'password_hash': hash_password('Lf2vKq7w'),
        'nombre': 'MZA 70',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza71': {
        'password_hash': hash_password('Tp8cHm3x'),
        'nombre': 'MZA 71',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza84': {
        'password_hash': hash_password('Qk4jBn9d'),
        'nombre': 'MZA 84',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza85': {
        'password_hash': hash_password('Wr7pFs2g'),
        'nombre': 'MZA 85',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza86': {
        'password_hash': hash_password('Yn3sDt8h'),
        'nombre': 'MZA 86',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza87': {
        'password_hash': hash_password('Gc9wLk4r'),
        'nombre': 'MZA 87',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza88': {
        'password_hash': hash_password('Bx5nPv7m'),
        'nombre': 'MZA 88',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza89': {
        'password_hash': hash_password('Df2cQw9j'),
        'nombre': 'MZA 89',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza90': {
        'password_hash': hash_password('Kh8rXm3s'),
        'nombre': 'MZA 90',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza91': {
        'password_hash': hash_password('Nt4bYp7f'),
        'nombre': 'MZA 91',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza92': {
        'password_hash': hash_password('Sq9kJc2n'),
        'nombre': 'MZA 92',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza93': {
        'password_hash': hash_password('Vw6hGt8d'),
        'nombre': 'MZA 93',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza323': {
        'password_hash': hash_password('Xp3mRs4y'),
        'nombre': 'MZA 323',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza324': {
        'password_hash': hash_password('Zr7nKw9b'),
        'nombre': 'MZA 324',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza325': {
        'password_hash': hash_password('Ct2vLq5x'),
        'nombre': 'MZA 325',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza326': {
        'password_hash': hash_password('Hf8jPm3c'),
        'nombre': 'MZA 326',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza327': {
        'password_hash': hash_password('Mk4dBn7g'),
        'nombre': 'MZA 327',
        'rol': 'vendedor',
        'equipo': 'DIANA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    # ========================================
    # VENDEDORES EQUIPO BYL
    # ========================================
    'mza307': {
        'password_hash': hash_password('Rw9sFt2p'),
        'nombre': 'MZA 307',
        'rol': 'vendedor',
        'equipo': 'BYL',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza308': {
        'password_hash': hash_password('Yn5cXk8j'),
        'nombre': 'MZA 308',
        'rol': 'vendedor',
        'equipo': 'BYL',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza309': {
        'password_hash': hash_password('Gq3hNm7r'),
        'nombre': 'MZA 309',
        'rol': 'vendedor',
        'equipo': 'BYL',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza310': {
        'password_hash': hash_password('Bv8pRt4w'),
        'nombre': 'MZA 310',
        'rol': 'vendedor',
        'equipo': 'BYL',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza311': {
        'password_hash': hash_password('Df6kLs9n'),
        'nombre': 'MZA 311',
        'rol': 'vendedor',
        'equipo': 'BYL',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza312': {
        'password_hash': hash_password('Jx2wQc5m'),
        'nombre': 'MZA 312',
        'rol': 'vendedor',
        'equipo': 'BYL',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza315': {
        'password_hash': hash_password('Ks7bYp3f'),
        'nombre': 'MZA 315',
        'rol': 'vendedor',
        'equipo': 'BYL',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza99': {
        'password_hash': hash_password('Pw4nHt8d'),
        'nombre': 'MZA 99',
        'rol': 'vendedor',
        'equipo': 'BYL',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza100': {
        'password_hash': hash_password('Tc9rMk2v'),
        'nombre': 'MZA 100',
        'rol': 'vendedor',
        'equipo': 'BYL',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza301': {
        'password_hash': hash_password('Xh5jGw7s'),
        'nombre': 'MZA 301',
        'rol': 'vendedor',
        'equipo': 'BYL',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza302': {
        'password_hash': hash_password('Zn3cFq9x'),
        'nombre': 'MZA 302',
        'rol': 'vendedor',
        'equipo': 'BYL',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza303': {
        'password_hash': hash_password('Lm8vDt4p'),
        'nombre': 'MZA 303',
        'rol': 'vendedor',
        'equipo': 'BYL',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza304': {
        'password_hash': hash_password('Qr6kBn2y'),
        'nombre': 'MZA 304',
        'rol': 'vendedor',
        'equipo': 'BYL',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza305': {
        'password_hash': hash_password('Ws4pJm7c'),
        'nombre': 'MZA 305',
        'rol': 'vendedor',
        'equipo': 'BYL',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    # ========================================
    # VENDEDORES EQUIPO MELANIE CARMONA
    # ========================================
    'mza1': {
        'password_hash': hash_password('Rf4nBk9t'),
        'nombre': 'MZA 1',
        'rol': 'vendedor',
        'equipo': 'MELANIE CARMONA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza2': {
        'password_hash': hash_password('Yc7mHw3p'),
        'nombre': 'MZA 2',
        'rol': 'vendedor',
        'equipo': 'MELANIE CARMONA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza3': {
        'password_hash': hash_password('Ks2vPq8j'),
        'nombre': 'MZA 3',
        'rol': 'vendedor',
        'equipo': 'MELANIE CARMONA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza4': {
        'password_hash': hash_password('Bn6xRt4f'),
        'nombre': 'MZA 4',
        'rol': 'vendedor',
        'equipo': 'MELANIE CARMONA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza5': {
        'password_hash': hash_password('Dw9cLm2s'),
        'nombre': 'MZA 5',
        'rol': 'vendedor',
        'equipo': 'MELANIE CARMONA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza6': {
        'password_hash': hash_password('Hj3kNp7v'),
        'nombre': 'MZA 6',
        'rol': 'vendedor',
        'equipo': 'MELANIE CARMONA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza7': {
        'password_hash': hash_password('Tq8bGs4y'),
        'nombre': 'MZA 7',
        'rol': 'vendedor',
        'equipo': 'MELANIE CARMONA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza8': {
        'password_hash': hash_password('Xn5rWk9c'),
        'nombre': 'MZA 8',
        'rol': 'vendedor',
        'equipo': 'MELANIE CARMONA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza9': {
        'password_hash': hash_password('Fm2jVt6h'),
        'nombre': 'MZA 9',
        'rol': 'vendedor',
        'equipo': 'MELANIE CARMONA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza10': {
        'password_hash': hash_password('Pc7sDq3n'),
        'nombre': 'MZA 10',
        'rol': 'vendedor',
        'equipo': 'MELANIE CARMONA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza12': {
        'password_hash': hash_password('Zk4wMr8b'),
        'nombre': 'MZA 12',
        'rol': 'vendedor',
        'equipo': 'MELANIE CARMONA',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    # ========================================
    # VENDEDORES EQUIPO ARENAS YASMIN
    # ========================================
    'mza13': {
        'password_hash': hash_password('Gt9hXn2f'),
        'nombre': 'MZA 13',
        'rol': 'vendedor',
        'equipo': 'ARENAS YASMIN',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza14': {
        'password_hash': hash_password('Lv6cBp4k'),
        'nombre': 'MZA 14',
        'rol': 'vendedor',
        'equipo': 'ARENAS YASMIN',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza15': {
        'password_hash': hash_password('Qw3rKs7m'),
        'nombre': 'MZA 15',
        'rol': 'vendedor',
        'equipo': 'ARENAS YASMIN',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza16': {
        'password_hash': hash_password('Jn8fTq2x'),
        'nombre': 'MZA 16',
        'rol': 'vendedor',
        'equipo': 'ARENAS YASMIN',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza18': {
        'password_hash': hash_password('Yb5mPv9d'),
        'nombre': 'MZA 18',
        'rol': 'vendedor',
        'equipo': 'ARENAS YASMIN',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza19': {
        'password_hash': hash_password('Ck2wRn6j'),
        'nombre': 'MZA 19',
        'rol': 'vendedor',
        'equipo': 'ARENAS YASMIN',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza20': {
        'password_hash': hash_password('Hs7kDt3p'),
        'nombre': 'MZA 20',
        'rol': 'vendedor',
        'equipo': 'ARENAS YASMIN',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza21': {
        'password_hash': hash_password('Nr4cGm8v'),
        'nombre': 'MZA 21',
        'rol': 'vendedor',
        'equipo': 'ARENAS YASMIN',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza22': {
        'password_hash': hash_password('Wf9jLs5b'),
        'nombre': 'MZA 22',
        'rol': 'vendedor',
        'equipo': 'ARENAS YASMIN',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza23': {
        'password_hash': hash_password('Xq2nYk7r'),
        'nombre': 'MZA 23',
        'rol': 'vendedor',
        'equipo': 'ARENAS YASMIN',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza24': {
        'password_hash': hash_password('Bm6hPt3w'),
        'nombre': 'MZA 24',
        'rol': 'vendedor',
        'equipo': 'ARENAS YASMIN',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    # ========================================
    # VENDEDORES EQUIPO JOSEFINA ZEBALLOS
    # ========================================
    'mza25': {
        'password_hash': hash_password('Vk8rFn4c'),
        'nombre': 'MZA 25',
        'rol': 'vendedor',
        'equipo': 'JOSEFINA ZEBALLOS',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza26': {
        'password_hash': hash_password('Tn3wSq9j'),
        'nombre': 'MZA 26',
        'rol': 'vendedor',
        'equipo': 'JOSEFINA ZEBALLOS',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza27': {
        'password_hash': hash_password('Md7cXk2p'),
        'nombre': 'MZA 27',
        'rol': 'vendedor',
        'equipo': 'JOSEFINA ZEBALLOS',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza28': {
        'password_hash': hash_password('Rj5nBv8f'),
        'nombre': 'MZA 28',
        'rol': 'vendedor',
        'equipo': 'JOSEFINA ZEBALLOS',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza29': {
        'password_hash': hash_password('Yh2kLm6s'),
        'nombre': 'MZA 29',
        'rol': 'vendedor',
        'equipo': 'JOSEFINA ZEBALLOS',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza30': {
        'password_hash': hash_password('Gw9pRt4n'),
        'nombre': 'MZA 30',
        'rol': 'vendedor',
        'equipo': 'JOSEFINA ZEBALLOS',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza31': {
        'password_hash': hash_password('Kb4fDq7x'),
        'nombre': 'MZA 31',
        'rol': 'vendedor',
        'equipo': 'JOSEFINA ZEBALLOS',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza32': {
        'password_hash': hash_password('Zn8cHs3v'),
        'nombre': 'MZA 32',
        'rol': 'vendedor',
        'equipo': 'JOSEFINA ZEBALLOS',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza33': {
        'password_hash': hash_password('Pt6jWm9k'),
        'nombre': 'MZA 33',
        'rol': 'vendedor',
        'equipo': 'JOSEFINA ZEBALLOS',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    # ========================================
    # VENDEDORES EQUIPO NATALI SANCHE
    # ========================================
    'mza34': {
        'password_hash': hash_password('Fc2rNb7h'),
        'nombre': 'MZA 34',
        'rol': 'vendedor',
        'equipo': 'NATALI SANCHE',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza35': {
        'password_hash': hash_password('Xk5wPq3d'),
        'nombre': 'MZA 35',
        'rol': 'vendedor',
        'equipo': 'NATALI SANCHE',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza36': {
        'password_hash': hash_password('Lm9cVt4j'),
        'nombre': 'MZA 36',
        'rol': 'vendedor',
        'equipo': 'NATALI SANCHE',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza37': {
        'password_hash': hash_password('Qs7hKn2f'),
        'nombre': 'MZA 37',
        'rol': 'vendedor',
        'equipo': 'NATALI SANCHE',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza38': {
        'password_hash': hash_password('Br4jGs8p'),
        'nombre': 'MZA 38',
        'rol': 'vendedor',
        'equipo': 'NATALI SANCHE',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza39': {
        'password_hash': hash_password('Wn6dYm3c'),
        'nombre': 'MZA 39',
        'rol': 'vendedor',
        'equipo': 'NATALI SANCHE',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza40': {
        'password_hash': hash_password('Hv8kRq5x'),
        'nombre': 'MZA 40',
        'rol': 'vendedor',
        'equipo': 'NATALI SANCHE',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza41': {
        'password_hash': hash_password('Tc2pLs9n'),
        'nombre': 'MZA 41',
        'rol': 'vendedor',
        'equipo': 'NATALI SANCHE',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza42': {
        'password_hash': hash_password('Jf7bXw4k'),
        'nombre': 'MZA 42',
        'rol': 'vendedor',
        'equipo': 'NATALI SANCHE',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza43': {
        'password_hash': hash_password('Yk3nDt6v'),
        'nombre': 'MZA 43',
        'rol': 'vendedor',
        'equipo': 'NATALI SANCHE',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    # ========================================
    # VENDEDORES EQUIPO MARINA MARTINEZ
    # ========================================
    'mza44': {
        'password_hash': hash_password('Np8rFm2j'),
        'nombre': 'MZA 44',
        'rol': 'vendedor',
        'equipo': 'MARINA MARTINEZ',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza45': {
        'password_hash': hash_password('Gk5cBq7s'),
        'nombre': 'MZA 45',
        'rol': 'vendedor',
        'equipo': 'MARINA MARTINEZ',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza72': {
        'password_hash': hash_password('Rw3hPn9d'),
        'nombre': 'MZA 72',
        'rol': 'vendedor',
        'equipo': 'MARINA MARTINEZ',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza73': {
        'password_hash': hash_password('Vb6jKt4x'),
        'nombre': 'MZA 73',
        'rol': 'vendedor',
        'equipo': 'MARINA MARTINEZ',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza74': {
        'password_hash': hash_password('Sm2wYq8f'),
        'nombre': 'MZA 74',
        'rol': 'vendedor',
        'equipo': 'MARINA MARTINEZ',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza313': {
        'password_hash': hash_password('Dn7kRs3p'),
        'nombre': 'MZA 313',
        'rol': 'vendedor',
        'equipo': 'MARINA MARTINEZ',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
    'mza314': {
        'password_hash': hash_password('Xt4cLv9m'),
        'nombre': 'MZA 314',
        'rol': 'vendedor',
        'equipo': 'MARINA MARTINEZ',
        'permisos': ['dashboard', 'mi_rendimiento']
    },
}

def verificar_credenciales(usuario, password):
    """Verifica las credenciales del usuario"""
    usuario = usuario.lower().strip()
    if usuario in USUARIOS:
        if USUARIOS[usuario]['password_hash'] == hash_password(password):
            return True, USUARIOS[usuario]
    return False, None


def obtener_permisos_usuario():
    """
    Obtiene los permisos y restricciones del usuario actual.
    Retorna un diccionario con:
    - rol: admin/supervisor/vendedor
    - equipo: equipo asignado (None para admin)
    - nombre_usuario: nombre del vendedor para filtrar
    - puede_ver_todos: si puede ver todos los equipos/vendedores
    - puede_comparar: si puede ver comparativas entre equipos
    - equipos_permitidos: lista de equipos que puede ver
    - vendedores_permitidos: lista de vendedores que puede ver (vacía si puede ver todos)
    """
    datos_usuario = st.session_state.get('datos_usuario', {})
    usuario_key = st.session_state.get('usuario', '').lower()
    
    rol = datos_usuario.get('rol', 'vendedor')
    equipo = datos_usuario.get('equipo', None)
    nombre = datos_usuario.get('nombre', '')
    
    permisos = {
        'rol': rol,
        'equipo': equipo,
        'nombre_usuario': nombre,
        'puede_ver_todos': False,
        'puede_comparar': False,
        'equipos_permitidos': [],
        'vendedores_permitidos': [],
        'es_admin': False
    }
    
    if rol == 'admin':
        # Admin puede ver todo
        permisos['puede_ver_todos'] = True
        permisos['puede_comparar'] = True
        permisos['es_admin'] = True
    elif rol == 'supervisor':
        # Supervisor solo puede ver su equipo
        permisos['puede_ver_todos'] = False
        permisos['puede_comparar'] = False
        if equipo:
            permisos['equipos_permitidos'] = [equipo]
        else:
            # Supervisor sin equipo (calidad, capacitación) - pueden ver todos
            permisos['puede_ver_todos'] = True
            permisos['puede_comparar'] = True
    elif rol == 'vendedor':
        # Vendedor solo puede ver sus propios datos
        permisos['puede_ver_todos'] = False
        permisos['puede_comparar'] = False
        if equipo:
            permisos['equipos_permitidos'] = [equipo]
        permisos['vendedores_permitidos'] = [nombre]
    
    return permisos


def filtrar_datos_por_permisos(df, permisos, columna_agente='agente', columna_equipo='equipo'):
    """
    Filtra un DataFrame según los permisos del usuario.
    Si el usuario no puede ver todos, filtra por equipo y/o vendedor.
    """
    if permisos['puede_ver_todos']:
        return df
    
    df_filtrado = df.copy()
    
    # Filtrar por vendedores específicos primero (para vendedores)
    if permisos['vendedores_permitidos']:
        nombre_usuario = permisos['vendedores_permitidos'][0].lower()
        if columna_agente in df_filtrado.columns:
            mask = df_filtrado[columna_agente].apply(
                lambda x: nombre_usuario in str(x).lower() if pd.notna(x) else False
            )
            df_filtrado = df_filtrado[mask]
        return df_filtrado
    
    # Filtrar por equipo (para supervisores)
    if permisos['equipos_permitidos'] and columna_equipo in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado[columna_equipo].isin(permisos['equipos_permitidos'])]
    
    return df_filtrado


def mostrar_login():
    """Muestra la pantalla de login profesional - Formato corporativo"""
    
    # CSS personalizado para el login - FONDO CLARO, TEXTO OSCURO
    st.markdown("""
    <style>
        /* Fondo claro corporativo */
        .stApp {
            background: linear-gradient(180deg, #F8FAFC 0%, #E2E8F0 100%) !important;
        }
        
        /* Ocultar elementos de Streamlit */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Contenedor del logo */
        .login-logo-box {
            text-align: center;
            padding: 30px 0;
        }
        
        .login-logo-icon {
            font-size: 4.5rem;
            display: block;
            margin-bottom: 10px;
        }
        
        .login-brand {
            font-size: 2.5rem;
            font-weight: 800;
            color: #1E3A5F;
            letter-spacing: 4px;
            margin: 0;
        }
        
        .login-tagline {
            font-size: 1rem;
            color: #64748B;
            margin-top: 5px;
            font-weight: 500;
        }
        
        /* Card del formulario - BLANCO con sombra suave */
        .login-form-card {
            background: #FFFFFF;
            border-radius: 16px;
            padding: 35px 40px;
            box-shadow: 0 10px 40px rgba(30, 58, 95, 0.12);
            border: 1px solid #E2E8F0;
            max-width: 400px;
            margin: 0 auto;
        }
        
        .login-form-title {
            font-size: 1.4rem;
            font-weight: 700;
            color: #1E293B;
            text-align: center;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 2px solid #E2E8F0;
        }
        
        /* Labels de inputs */
        .stTextInput > label {
            font-weight: 600 !important;
            color: #334155 !important;
            font-size: 0.95rem !important;
            margin-bottom: 6px !important;
        }
        
        /* Inputs - fondo gris muy claro */
        .stTextInput > div > div > input {
            border-radius: 10px !important;
            border: 2px solid #CBD5E1 !important;
            padding: 12px 16px !important;
            font-size: 1rem !important;
            background: #F8FAFC !important;
            color: #1E293B !important;
            transition: all 0.2s ease !important;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #3B82F6 !important;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
            background: #FFFFFF !important;
        }
        
        .stTextInput > div > div > input::placeholder {
            color: #94A3B8 !important;
        }
        
        /* Botón de login - Azul corporativo */
        .stFormSubmitButton > button {
            width: 100%;
            border-radius: 10px !important;
            padding: 12px 24px !important;
            font-size: 1rem !important;
            font-weight: 600 !important;
            background: #1E3A5F !important;
            border: none !important;
            color: #FFFFFF !important;
            transition: all 0.2s ease !important;
            margin-top: 15px !important;
        }
        
        .stFormSubmitButton > button:hover {
            background: #2563EB !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
        }
        
        /* Alertas con mejor visibilidad */
        .stAlert {
            border-radius: 10px !important;
            margin-top: 15px !important;
        }
        
        /* Footer */
        .login-footer-text {
            text-align: center;
            margin-top: 30px;
            color: #64748B;
            font-size: 0.85rem;
        }
        
        /* Características/Features */
        .login-features-row {
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 35px;
            padding-top: 20px;
        }
        
        .login-feature-item {
            text-align: center;
        }
        
        .login-feature-item span {
            font-size: 2rem;
            display: block;
            margin-bottom: 8px;
        }
        
        .login-feature-item p {
            color: #475569;
            font-size: 0.85rem;
            font-weight: 500;
            margin: 0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Espaciado superior
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    
    # Estructura centrada
    col1, col2, col3 = st.columns([1, 1.8, 1])
    
    with col2:
        # Logo y marca
        st.markdown("""
        <div class="login-logo-box">
            <span class="login-logo-icon">📈</span>
            <h1 class="login-brand">COMMAND</h1>
            <p class="login-tagline">Sistema de Rendimiento Comercial</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Título del formulario
        st.markdown('<p class="login-form-title">Iniciar Sesión</p>', unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            usuario = st.text_input(
                "Usuario",
                placeholder="Ingrese su usuario",
                key="login_usuario"
            )
            
            password = st.text_input(
                "Contraseña",
                type="password",
                placeholder="Ingrese su contraseña",
                key="login_password"
            )
            
            submitted = st.form_submit_button("Ingresar", use_container_width=True)
            
            if submitted:
                if usuario and password:
                    valido, datos_usuario = verificar_credenciales(usuario, password)
                    if valido:
                        # Iniciar carga de datos en background para evitar que la UI muestre "Running cargar_datos()" inmediatamente
                        try:
                            iniciar_preload_datos()
                            st.session_state['datos_preload_started'] = True
                        except Exception:
                            # En caso de algún error, no impedir el login
                            pass

                        st.session_state['autenticado'] = True
                        st.session_state['usuario'] = usuario.lower()
                        st.session_state['datos_usuario'] = datos_usuario
                        st.rerun()
                    else:
                        st.error("Usuario o contraseña incorrectos")
                else:
                    st.warning("Por favor complete todos los campos")
        
        # Features
        st.markdown("""
        <div class="login-features-row">
            <div class="login-feature-item">
                <span>📊</span>
                <p>Reportes Ejecutivos</p>
            </div>
            <div class="login-feature-item">
                <span>👥</span>
                <p>Auditoría de Equipos</p>
            </div>
            <div class="login-feature-item">
                <span>🎯</span>
                <p>Métricas de Rendimiento</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Footer
        st.markdown("""
        <p class="login-footer-text">
            © 2026 COMMAND · Sistema de Rendimiento Comercial
        </p>
        """, unsafe_allow_html=True)

def cerrar_sesion():
    """Cierra la sesión del usuario"""
    for key in ['autenticado', 'usuario', 'datos_usuario']:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

def verificar_permiso(permiso):
    """Verifica si el usuario actual tiene un permiso específico"""
    if 'datos_usuario' not in st.session_state:
        return False
    permisos_usuario = st.session_state['datos_usuario'].get('permisos', [])
    return permiso in permisos_usuario or 'admin' == st.session_state['datos_usuario'].get('rol')

def obtener_agentes_permitidos(df):
    """Filtra los agentes según el rol del usuario"""
    if 'datos_usuario' not in st.session_state:
        return df
    
    datos = st.session_state['datos_usuario']
    rol = datos.get('rol', 'vendedor')
    
    if rol == 'admin':
        # Admin ve todo
        return df
    elif rol == 'supervisor':
        # Supervisor ve solo su equipo
        equipo = datos.get('equipo')
        if equipo and 'agente' in df.columns:
            _, equipos_vendedores = cargar_listado_vendedores()
            agentes_equipo = equipos_vendedores.get(equipo, [])
            return df[df['agente'].isin(agentes_equipo)]
        return df
    else:
        # Vendedor solo ve sus propios datos
        nombre_usuario = datos.get('nombre', '')
        if 'agente' in df.columns and nombre_usuario:
            return df[df['agente'] == nombre_usuario]
        return df

# =============================================================================
# MAPEO GLOBAL DE NOMBRES DE VENDEDORES
# =============================================================================
@st.cache_data(ttl=3600)  # Cache por 1 hora
def cargar_listado_vendedores():
    """Carga el listado de vendedores y retorna un diccionario de mapeo usuario -> nombre"""
    listado_vendedores = {}
    equipos_vendedores = {}
    try:
        ruta_listado = os.path.join(BASE_DIR, 'LISTADO-DE-VENDEDORES.csv')
        df_listado = pd.read_csv(ruta_listado, header=0)
        for _, row in df_listado.iterrows():
            usuario = str(row.iloc[0]).strip().lower().replace('\t', '').replace(' ', '')
            nombre = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
            equipo = str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else "Sin Equipo"
            if usuario and nombre and usuario != 'usuario':
                listado_vendedores[usuario] = nombre.title()
                # Solo agregar a equipos_vendedores si no es "Sin Equipo"
                if equipo != "Sin Equipo":
                    if equipo not in equipos_vendedores:
                        equipos_vendedores[equipo] = []
                    equipos_vendedores[equipo].append(nombre.title())
    except:
        pass
    return listado_vendedores, equipos_vendedores

def obtener_nombre_vendedor_global(agente_id):
    """Convierte ID de agente a nombre real usando el listado global"""
    listado, _ = cargar_listado_vendedores()
    if pd.isna(agente_id) or agente_id is None:
        return "Desconocido"
    agente_normalizado = str(agente_id).lower().replace(' ', '').replace('_', '').replace('\t', '')
    return listado.get(agente_normalizado, str(agente_id))

def aplicar_mapeo_nombres_df(df, columna='agente'):
    """Aplica el mapeo de nombres a una columna de un DataFrame"""
    if columna in df.columns:
        df[columna] = df[columna].apply(obtener_nombre_vendedor_global)
    return df

# Alias para compatibilidad con código existente
obtener_nombre_agente = obtener_nombre_vendedor_global


def extraer_fecha_de_archivo(nombre_archivo):
    """
    Extrae la fecha de la llamada del nombre del archivo.
    El patrón es: YYMMDD en posiciones como 260112 (2026-01-12)
    Ejemplo: amza10_1_260112105813064_ACD_11829_transcripcion.json -> 2026-01-12
    """
    import re
    if pd.isna(nombre_archivo) or not isinstance(nombre_archivo, str):
        return None
    
    # Buscar patrón de 6 dígitos que comience con 26 (2026)
    match = re.search(r'26(01\d{2})\d+', nombre_archivo)
    if match:
        # Extraer MMDD del match
        fecha_str = match.group(0)[:6]  # Primeros 6 dígitos: YYMMDD
        try:
            year = 2000 + int(fecha_str[:2])  # 26 -> 2026
            month = int(fecha_str[2:4])
            day = int(fecha_str[4:6])
            return datetime(year, month, day).date()
        except:
            return None
    return None


def obtener_rango_fechas_disponibles(df, columna_fecha='fecha_llamada'):
    """Obtiene el rango de fechas disponibles en el DataFrame"""
    if columna_fecha not in df.columns:
        return None, None
    fechas_validas = df[columna_fecha].dropna()
    if len(fechas_validas) == 0:
        return None, None
    return fechas_validas.min(), fechas_validas.max()


def obtener_semanas_disponibles(df, columna_fecha='fecha_llamada'):
    """Agrupa las fechas disponibles en semanas para facilitar la comparación"""
    if columna_fecha not in df.columns:
        return {}
    
    fechas_validas = df[columna_fecha].dropna().unique()
    semanas = {}
    
    for fecha in sorted(fechas_validas):
        # Obtener inicio de semana (lunes)
        if isinstance(fecha, datetime):
            fecha = fecha.date()
        inicio_semana = fecha - pd.Timedelta(days=fecha.weekday())
        fin_semana = inicio_semana + pd.Timedelta(days=6)
        clave = f"{inicio_semana.strftime('%d/%m')} - {fin_semana.strftime('%d/%m/%Y')}"
        if clave not in semanas:
            semanas[clave] = {'inicio': inicio_semana, 'fin': fin_semana}
    
    return semanas


@st.cache_data(ttl=300)  # Cache por 5 minutos
def cargar_datos():
    """Carga todos los datos necesarios para el dashboard"""
    datos = {}
    
    # Cargar evaluaciones primero para saber qué archivos cargar
    ruta_eval = os.path.join(BASE_DIR, 'reportes/evaluaciones_gemini.csv')
    archivos_evaluados = set()
    if os.path.exists(ruta_eval):
        df_eval = pd.read_csv(ruta_eval)
        archivos_evaluados = set(df_eval['archivo'].tolist())
    
    # Cargar transcripciones mejoradas (solo las que tienen evaluación)
    carpeta = os.path.join(BASE_DIR, "transcripts/mejorados_gemini")
    if os.path.exists(carpeta):
        transcripciones = []
        for archivo in os.listdir(carpeta):
            if archivo.endswith('.json') and archivo in archivos_evaluados:
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
    
    # Cargar CSV de planes detallado
    ruta = os.path.join(BASE_DIR, 'reportes/planes/analisis_planes_detallado.csv')
    if os.path.exists(ruta):
        datos['planes_df'] = pd.read_csv(ruta)
    
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
            # Convertir lista a diccionario por agente (aplicando mapeo de nombres)
            datos['coaching'] = {}
            for item in coaching_list:
                comparativa = item.get('comparativa', {}) or {}
                if 'puntaje_ia' not in comparativa and 'puntaje_modelo' in comparativa:
                    comparativa['puntaje_ia'] = comparativa['puntaje_modelo']
                if 'puntaje_ia' not in comparativa:
                    puntaje_prom = item.get('metricas', {}).get('evaluaciones', {}).get('puntaje_promedio', 0)
                    comparativa['puntaje_ia'] = {
                        'agente': puntaje_prom,
                        'general': 0,
                        'diferencia': 0,
                        'percentil': 0
                    }
                item['comparativa'] = comparativa
                nombre_real = obtener_nombre_vendedor_global(item['agente'])
                item['agente'] = nombre_real
                datos['coaching'][nombre_real] = item
    
    # Cargar listado de vendedores y equipos
    listado, equipos = cargar_listado_vendedores()
    datos['listado_vendedores'] = listado
    datos['equipos_vendedores'] = equipos
    
    # Aplicar mapeo de nombres a todos los DataFrames con columna 'agente'
    dataframes_con_agente = ['integral_df', 'metricas_agentes_df', 'clasificacion_df', 
                             'clasificacion_agentes_df', 'evaluaciones_gemini_df', 
                             'cierres_df', 'quejas_df']
    for df_name in dataframes_con_agente:
        if df_name in datos and datos[df_name] is not None:
            datos[df_name] = aplicar_mapeo_nombres_df(datos[df_name], 'agente')
    
    # =========================================================================
    # AGREGAR COLUMNA DE FECHA A LOS DATAFRAMES QUE TIENEN NOMBRE DE ARCHIVO
    # =========================================================================
    dataframes_con_archivo = ['evaluaciones_gemini_df', 'clasificacion_df', 'integral_df']
    for df_name in dataframes_con_archivo:
        if df_name in datos and datos[df_name] is not None:
            df = datos[df_name]
            if 'archivo' in df.columns:
                # Extraer fecha del nombre del archivo
                df['fecha_llamada'] = df['archivo'].apply(extraer_fecha_de_archivo)
                # Convertir a datetime para facilitar filtrado
                df['fecha_llamada'] = pd.to_datetime(df['fecha_llamada'], errors='coerce')
                # Crear columna de semana para agrupaciones
                df['semana'] = df['fecha_llamada'].dt.isocalendar().week
                df['dia_semana'] = df['fecha_llamada'].dt.day_name()
                datos[df_name] = df
    
    return datos


def crear_df_llamadas(transcripciones):
    """Crea un DataFrame con la información de las llamadas"""
    filas = []
    for t in transcripciones:
        info = t.get('info_llamada', {})
        calidad = t.get('analisis_calidad', {})
        productos = t.get('productos_ofrecidos', {})
        
        # Obtener nombre del agente y aplicar mapeo
        agente_raw = info.get('agente', {}).get('nombre', 'desconocido')
        agente_nombre = obtener_nombre_vendedor_global(agente_raw)
        
        fila = {
            'id': info.get('id_interaccion', ''),
            'fecha': info.get('fecha_llamada', ''),
            'agente': agente_nombre,
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


def crear_df_llamadas_desde_evaluaciones(df_eval):
    """Crea un DataFrame de llamadas usando solo evaluaciones."""
    if df_eval is None or df_eval.empty:
        return pd.DataFrame()

    base = df_eval.copy()
    idx = base.index

    if 'fecha_evaluacion' in base.columns:
        fecha_eval = pd.to_datetime(base['fecha_evaluacion'], errors='coerce')
    else:
        fecha_eval = pd.Series([pd.NaT] * len(base), index=idx)

    if 'archivo' in base.columns:
        fecha_archivo = pd.to_datetime(base['archivo'].apply(extraer_fecha_de_archivo), errors='coerce')
    else:
        fecha_archivo = pd.Series([pd.NaT] * len(base), index=idx)

    fecha_final = fecha_eval.fillna(fecha_archivo)

    if 'archivo' in base.columns:
        ids = base['archivo']
    else:
        ids = base.index.astype(str)

    if 'agente' in base.columns:
        agentes = base['agente']
    else:
        agentes = pd.Series(['Desconocido'] * len(base), index=idx)

    if 'puntaje_total' in base.columns:
        score_calidad = pd.to_numeric(base['puntaje_total'], errors='coerce').fillna(0)
    else:
        score_calidad = pd.Series([0] * len(base), index=idx)

    if 'saludo_presentacion' in base.columns:
        tiene_saludo = pd.to_numeric(base['saludo_presentacion'], errors='coerce').fillna(0) > 0
    else:
        tiene_saludo = pd.Series([False] * len(base), index=idx)

    if 'cierre' in base.columns:
        tiene_cierre = pd.to_numeric(base['cierre'], errors='coerce').fillna(0) > 0
    else:
        tiene_cierre = pd.Series([False] * len(base), index=idx)

    if 'planes_mencionados' in base.columns:
        planes = base['planes_mencionados'].fillna('')
    else:
        planes = pd.Series([''] * len(base), index=idx)

    if 'primer_plan_ofrecido' in base.columns:
        primer_plan = base['primer_plan_ofrecido'].fillna('')
    else:
        primer_plan = pd.Series([''] * len(base), index=idx)

    df = pd.DataFrame({
        'id': ids,
        'fecha': fecha_final,
        'agente': agentes,
        'duracion': 0,
        'tipificacion': 'Sin datos',
        'tipo': 'Sin datos',
        'score_calidad': score_calidad,
        'tiene_saludo': tiene_saludo,
        'tiene_cierre': tiene_cierre,
        'planes': planes,
        'primer_plan': primer_plan,
    })

    df['agente'] = df['agente'].apply(obtener_nombre_vendedor_global)
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    if 'fecha' in df.columns and len(df) > 0:
        df['dia'] = df['fecha'].dt.date
        df['hora'] = df['fecha'].dt.hour
    return df


def cargar_coaching_equipo(ruta_coaching):
    """Carga y normaliza el coaching de un equipo desde JSON."""
    if not os.path.exists(ruta_coaching):
        return None
    try:
        with open(ruta_coaching, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        return None

    comparativa = data.get('comparativa', {}) or {}
    if 'puntaje_ia' not in comparativa and 'puntaje_modelo' in comparativa:
        comparativa['puntaje_ia'] = comparativa['puntaje_modelo']
    data['comparativa'] = comparativa

    coaching_modelo = data.get('coaching_modelo', {}) or {}
    coaching_ia = data.get('coaching_ia') or coaching_modelo or {}

    if 'plan_accion_equipo' not in coaching_ia:
        if 'plan_accion_equipo' in coaching_modelo:
            coaching_ia['plan_accion_equipo'] = coaching_modelo.get('plan_accion_equipo', [])

    if not coaching_ia.get('plan_accion_equipo'):
        areas = coaching_ia.get('areas_mejora_prioritarias', []) or []
        plan = []
        for idx, area in enumerate(areas[:4], 1):
            nombre_area = area.get('area', 'Area clave')
            meta = area.get('meta', 'Mejorar el puntaje del equipo')
            plan.append({
                'prioridad': idx,
                'accion': f"Mejorar {nombre_area} con practicas semanales del equipo.",
                'responsable': 'Lider del equipo',
                'plazo': 'Corto plazo',
                'indicador_exito': meta
            })
        if plan:
            coaching_ia['plan_accion_equipo'] = plan

    data['coaching_ia'] = coaching_ia
    return data


def pagina_resumen_ejecutivo(datos, df):
    """Página de resumen ejecutivo"""
    st.markdown('<div class="main-header">📈 COMMAND · Panel Ejecutivo de Rendimiento Comercial</div>', unsafe_allow_html=True)
    
    # Subtítulo con contexto corporativo
    fecha_reporte = datetime.now().strftime('%d/%m/%Y %H:%M')
    st.markdown(f"""
    <div style='background: #F8FAFC; padding: 12px 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #3B82F6;'>
        <p style='margin: 0; color: #334155; font-size: 0.95rem;'>
            <strong>Informe de Gestión Comercial</strong> · Consolidado de métricas de rendimiento del equipo de ventas
        </p>
        <p style='margin: 5px 0 0 0; color: #64748B; font-size: 0.85rem;'>
            Fecha del reporte: <strong>{fecha_reporte}</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Métricas principales
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_llamadas = len(df)
    ventas = len(df[df['tipificacion'] == 'Venta'])
    tasa_conversion = (ventas / total_llamadas * 100) if total_llamadas > 0 else 0
    promedio_calidad = df['score_calidad'].mean() if len(df) > 0 else 0
    promedio_duracion = df['duracion'].mean() / 60 if len(df) > 0 else 0
    
    with col1:
        st.metric("📞 Total Operaciones", f"{total_llamadas:,}")
    with col2:
        st.metric("✅ Ventas Cerradas", f"{ventas:,}")
    with col3:
        st.metric("📈 Tasa de Conversión", f"{tasa_conversion:.1f}%")
    with col4:
        st.metric("⭐ Índice de Calidad", f"{promedio_calidad:.1f}/100")
    with col5:
        st.metric("⏱️ Tiempo Promedio", f"{promedio_duracion:.1f} min")
    
    st.markdown("---")
    
    # Gráficos principales
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<p class="section-header">📊 Distribución por Resultado de Gestión</p>', unsafe_allow_html=True)
        tipificacion_counts = df['tipificacion'].value_counts()
        crear_pie_chart_expandible(
            values=list(tipificacion_counts.values),
            names=list(tipificacion_counts.index),
            titulo="Distribución por Tipificación",
            colors=['#1A5276', '#145A32', '#B7950B', '#922B21', '#6C3483', '#0E6655'],
            key_id="tipificacion"
        )
    
    with col2:
        st.markdown('<p class="section-header">📈 Volumen de Operaciones Diarias</p>', unsafe_allow_html=True)
        if 'dia' in df.columns:
            llamadas_dia = df.groupby('dia').size().reset_index(name='llamadas')
            fig = px.bar(
                llamadas_dia, x='dia', y='llamadas',
                color_discrete_sequence=['#3B82F6']
            )
            fig.update_layout(
                height=300, 
                xaxis_title="Fecha",
                yaxis_title="Operaciones",
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
    st.markdown('<p class="section-header">🎯 Indicadores de Efectividad Comercial</p>', unsafe_allow_html=True)
    
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
    mostrar_proximamente("📋 COMMAND · Gestión de Cierres Comerciales")


def pagina_planes_ofrecidos(datos, df):
    """Página de análisis de planes ofrecidos, fibra y promociones"""
    st.markdown('<div class="main-header">📱 COMMAND · Análisis de Portafolio de Productos</div>', unsafe_allow_html=True)
    
    # Obtener permisos del usuario actual
    permisos = obtener_permisos_usuario()
    
    if 'planes' not in datos:
        st.warning("⚠️ No hay datos de planes disponibles.")
        return
    
    planes = datos['planes']
    stats = planes.get('estadisticas', {})
    
    # Cargar datos de filtrado
    listado_vendedores, equipos_vendedores = cargar_listado_vendedores()
    
    # Crear mapeo inverso: nombre -> equipo
    nombre_a_equipo = {}
    for equipo, vendedores in equipos_vendedores.items():
        for vendedor in vendedores:
            nombre_a_equipo[vendedor.lower().strip()] = equipo
    
    def obtener_equipo_por_nombre(nombre):
        """Obtiene el equipo del vendedor por su nombre"""
        if pd.isna(nombre) or nombre is None:
            return "Sin Equipo"
        nombre_lower = str(nombre).lower().strip()
        # Buscar coincidencia exacta primero
        if nombre_lower in nombre_a_equipo:
            return nombre_a_equipo[nombre_lower]
        # Buscar coincidencia parcial
        for nom, eq in nombre_a_equipo.items():
            if nombre_lower in nom or nom in nombre_lower:
                return eq
        return "Sin Equipo"
    
    # Cargar CSV de planes para filtrado
    planes_df = datos.get('planes_df', pd.DataFrame())
    
    if not planes_df.empty and 'agente' in planes_df.columns:
        # Aplicar nombres reales
        planes_df['agente_display'] = planes_df['agente'].apply(obtener_nombre_agente)
        planes_df['equipo'] = planes_df['agente_display'].apply(obtener_equipo_por_nombre)
        
        # Filtrar vendedores sin equipo
        planes_df = planes_df[planes_df['equipo'] != "Sin Equipo"]
        
        # =========================================================================
        # APLICAR RESTRICCIONES SEGÚN ROL DEL USUARIO
        # =========================================================================
        if permisos['rol'] == 'vendedor':
            # Vendedor: Filtrar solo sus datos, sin mostrar selectores
            nombre_vendedor = permisos['nombre_usuario'].lower()
            planes_df = planes_df[planes_df['agente_display'].apply(
                lambda x: nombre_vendedor in str(x).lower() if pd.notna(x) else False
            )]
            equipo_seleccionado = permisos['equipo'] if permisos['equipo'] else "Sin Equipo"
            agente_seleccionado = permisos['nombre_usuario']
            
            st.info(f"👤 Mostrando datos de: **{permisos['nombre_usuario']}** | Equipo: **{equipo_seleccionado}**")
            
        elif permisos['rol'] == 'supervisor' and permisos['equipos_permitidos']:
            # Supervisor con equipo: Filtrar solo su equipo
            equipo_supervisor = permisos['equipos_permitidos'][0]
            planes_df = planes_df[planes_df['equipo'] == equipo_supervisor]
            equipo_seleccionado = equipo_supervisor
            
            st.info(f"🏢 Mostrando datos del equipo: **{equipo_supervisor}**")
            
            # Mostrar selector de vendedor dentro del equipo
            st.markdown('<p class="section-header">🔍 Filtro de Vendedor</p>', unsafe_allow_html=True)
            agentes_equipo = planes_df['agente_display'].unique().tolist()
            agentes_opciones = ["Todos"] + sorted([a for a in agentes_equipo if a])
            agente_seleccionado = st.selectbox(
                "👤 Vendedor",
                agentes_opciones,
                key="filtro_agente_planes"
            )
        else:
            # Admin o supervisor sin restricciones: Mostrar todos los filtros
            st.markdown('<p class="section-header">🔍 Filtros</p>', unsafe_allow_html=True)
            
            # Obtener listas de equipos únicos (excluyendo Sin Equipo)
            equipos_unicos = planes_df['equipo'].unique().tolist()
            equipos_ordenados = sorted([e for e in equipos_unicos if e != "Sin Equipo"])
            equipos_disponibles = ["Todos los Equipos"] + equipos_ordenados
            
            col_filtro1, col_filtro2 = st.columns(2)
            
            with col_filtro1:
                equipo_seleccionado = st.selectbox(
                    "🏢 Equipo",
                    equipos_disponibles,
                    key="filtro_equipo_planes"
                )
            
            # Filtrar agentes según equipo
            if equipo_seleccionado != "Todos los Equipos":
                agentes_filtrados_list = planes_df[planes_df['equipo'] == equipo_seleccionado]['agente_display'].unique().tolist()
            else:
                agentes_filtrados_list = planes_df['agente_display'].unique().tolist()
            
            with col_filtro2:
                agentes_opciones = ["Todos"] + sorted([a for a in agentes_filtrados_list if a])
                agente_seleccionado = st.selectbox(
                    "👤 Vendedor",
                    agentes_opciones,
                    key="filtro_agente_planes"
                )
        
        # Aplicar filtros al DataFrame
        df_filtrado = planes_df.copy()
        if permisos['puede_ver_todos'] and equipo_seleccionado != "Todos los Equipos":
            df_filtrado = df_filtrado[df_filtrado['equipo'] == equipo_seleccionado]
        if agente_seleccionado != "Todos":
            df_filtrado = df_filtrado[df_filtrado['agente_display'] == agente_seleccionado]
        
        # Recalcular estadísticas basadas en el filtro
        total_llamadas = len(df_filtrado)
        
        # Estadísticas de planes filtradas
        con_plan = len(df_filtrado[df_filtrado['cantidad_planes'] > 0])
        sin_plan = len(df_filtrado[df_filtrado['cantidad_planes'] == 0])
        pct_con_plan = con_plan / total_llamadas * 100 if total_llamadas > 0 else 0
        
        # Estadísticas de fibra filtradas
        ofrece_fibra = len(df_filtrado[df_filtrado['ofrece_fibra'] == True])
        no_ofrece_fibra = len(df_filtrado[df_filtrado['ofrece_fibra'] == False])
        pct_fibra = ofrece_fibra / total_llamadas * 100 if total_llamadas > 0 else 0
        
        # Estadísticas de promociones filtradas
        df_promo = df_filtrado[df_filtrado['es_dia_promo'] == True]
        dias_promo_total = len(df_promo)
        menciona_promo = len(df_promo[df_promo['menciona_promo'] == True])
        no_menciona_promo = len(df_promo[df_promo['menciona_promo'] == False])
        
        # Mostrar indicador de filtro activo (solo para admin)
        if permisos['puede_ver_todos'] and (equipo_seleccionado != "Todos los Equipos" or agente_seleccionado != "Todos"):
            filtro_texto = []
            if equipo_seleccionado != "Todos los Equipos":
                filtro_texto.append(f"Equipo: {equipo_seleccionado}")
            if agente_seleccionado != "Todos":
                filtro_texto.append(f"Vendedor: {agente_seleccionado}")
            st.info(f"🔍 Filtro activo: {' | '.join(filtro_texto)} - Mostrando {total_llamadas:,} llamadas")
    else:
        total_llamadas = planes.get('total_llamadas', 0)
        con_plan = stats.get('planes', {}).get('con_plan', 0)
        sin_plan = stats.get('planes', {}).get('sin_plan', 0)
        pct_con_plan = stats.get('planes', {}).get('porcentaje_con_plan', 0)
        ofrece_fibra = stats.get('fibra', {}).get('ofrece', 0)
        no_ofrece_fibra = stats.get('fibra', {}).get('no_ofrece', 0)
        pct_fibra = stats.get('fibra', {}).get('porcentaje_ofrece', 0)
        dias_promo_total = stats.get('promociones', {}).get('dias_promo_total', 0)
        menciona_promo = stats.get('promociones', {}).get('dias_promo_menciona', 0)
        no_menciona_promo = stats.get('promociones', {}).get('dias_promo_no_menciona', 0)
        df_filtrado = pd.DataFrame()
    
    st.markdown("---")
    
    # =========================================================================
    # SECCIÓN 1: PLANES DE PORTA
    # =========================================================================
    st.markdown('<p class="section-header">📱 Análisis de Ofertas de Planes Móviles</p>', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📞 Total Operaciones", f"{total_llamadas:,}")
    with col2:
        st.metric("✅ Oferta Realizada", f"{con_plan:,}", f"{pct_con_plan:.1f}%")
    with col3:
        pct_sin = 100 - pct_con_plan if pct_con_plan else 0
        st.metric("❌ Sin Oferta", f"{sin_plan:,}", f"{pct_sin:.1f}%", delta_color="inverse")
    with col4:
        # Calcular si se ofreció fibra desde el CSV de evaluaciones
        if 'evaluaciones_gemini_df' in datos and datos['evaluaciones_gemini_df'] is not None:
            df_eval = datos['evaluaciones_gemini_df'].copy()
            # Si hay filtros aplicados por equipo/agente, aplicarlos también aquí
            if not df_filtrado.empty and 'agente_display' in df_filtrado.columns:
                # Usar los mismos agentes que en df_filtrado
                agentes_filtrados = df_filtrado['agente_display'].unique()
                df_eval = df_eval[df_eval['agente'].isin(agentes_filtrados)]
            
            if not df_eval.empty and 'se_ofrecio_fibra' in df_eval.columns:
                total_con_fibra = df_eval['se_ofrecio_fibra'].sum()
                pct_fibra_eval = (total_con_fibra / len(df_eval) * 100) if len(df_eval) > 0 else 0
                st.metric("🌐 Ofreció Fibra", f"{int(total_con_fibra):,}", f"{pct_fibra_eval:.1f}%")
            else:
                st.metric("🌐 Ofreció Fibra", "N/D")
        else:
            st.metric("🌐 Ofreció Fibra", "N/D")
    with col5:
        # Plan más usado como primer ofrecimiento
        if not df_filtrado.empty and 'primer_plan' in df_filtrado.columns:
            primer_plan_conteo = df_filtrado['primer_plan'].dropna().value_counts().to_dict()
        elif 'evaluaciones_gemini_df' in datos and datos['evaluaciones_gemini_df'] is not None:
            df_eval = datos['evaluaciones_gemini_df'].copy()
            # Si hay filtros aplicados, aplicarlos también aquí
            if not df_filtrado.empty and 'agente_display' in df_filtrado.columns:
                agentes_filtrados = df_filtrado['agente_display'].unique()
                df_eval = df_eval[df_eval['agente'].isin(agentes_filtrados)]
            
            if 'primer_plan_ofrecido' in df_eval.columns:
                primer_plan_conteo = df_eval['primer_plan_ofrecido'].dropna().value_counts().to_dict()
            else:
                primer_plan_conteo = stats.get('primer_plan_conteo', {})
        else:
            primer_plan_conteo = stats.get('primer_plan_conteo', {})
        if primer_plan_conteo:
            top_plan = max(primer_plan_conteo, key=primer_plan_conteo.get)
            st.metric("🥇 Plan Principal", str(top_plan).upper(), f"{primer_plan_conteo[top_plan]} veces")
    
    # Gráficos de planes
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Planes Más Ofrecidos**")
        
        # Calcular conteo de planes desde el DF filtrado si está disponible
        if not df_filtrado.empty and 'planes_ofrecidos' in df_filtrado.columns:
            # Contar planes desde los datos filtrados
            all_planes = []
            for planes_str in df_filtrado['planes_ofrecidos'].dropna():
                if isinstance(planes_str, str) and planes_str:
                    all_planes.extend([p.strip().lower() for p in planes_str.split(',')])
            from collections import Counter
            planes_conteo = dict(Counter(all_planes))
        else:
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
        
        # Usar datos filtrados si están disponibles
        if not df_filtrado.empty and 'primer_plan' in df_filtrado.columns:
            primer_plan_series = df_filtrado['primer_plan'].dropna().str.lower().value_counts()
            primer_plan = primer_plan_series.to_dict()
        else:
            primer_plan = stats.get('primer_plan_conteo', {})
        
        if primer_plan:
            # Ordenar
            orden = ['4gb', '8gb', '15gb', '30gb']
            primer_ord = {k.upper(): primer_plan.get(k, 0) for k in orden if k in primer_plan}
            
            if sum(primer_ord.values()) > 0:
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
    st.markdown('<p class="section-header">🏠 Análisis de Ofertas de Fibra Óptica</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        pct_no_fibra = 100 - pct_fibra if pct_fibra else 0
        st.metric("✅ Oferta Realizada", f"{ofrece_fibra:,}", f"{pct_fibra:.1f}%")
    with col2:
        st.metric("❌ Sin Oferta de Fibra", f"{no_ofrece_fibra:,}", f"-{pct_no_fibra:.1f}%", delta_color="inverse")
    with col3:
        # Indicador visual
        if pct_fibra < 30:
            st.error(f"⚠️ Solo {pct_fibra:.1f}% ofrece Fibra - Requiere acción inmediata")
        elif pct_fibra < 50:
            st.warning(f"⚠️ {pct_fibra:.1f}% ofrece Fibra - Área de mejora")
        else:
            st.success(f"✅ {pct_fibra:.1f}% ofrece Fibra - Cumplimiento adecuado")
    
    # Gráfico de Fibra
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de torta para Fibra
        fig = go.Figure(data=[go.Pie(
            labels=['Ofrece Fibra', 'No Ofrece Fibra'],
            values=[ofrece_fibra, no_ofrece_fibra],
            hole=0.4,
            marker_colors=['#10B981', '#EF4444'],
            textinfo='label+percent',
            textposition='outside',
            textfont=dict(size=11, color='#2C3E50'),
            pull=[0.02, 0]
        )])
        fig.update_layout(
            title={'text': "Distribución de Ofertas de Fibra", 'font': {'size': 14, 'color': '#2C3E50'}, 'x': 0.5},
            height=220,
            margin=dict(t=50, b=20, l=30, r=30),
            paper_bgcolor='#FFFFFF',
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top agentes que NO ofrecen fibra - usar datos filtrados si hay
        if not df_filtrado.empty and 'ofrece_fibra' in df_filtrado.columns:
            fibra_agente_df = df_filtrado.groupby('agente_display').agg({
                'ofrece_fibra': ['sum', 'count']
            }).reset_index()
            fibra_agente_df.columns = ['Agente', 'Ofrece', 'Total']
            fibra_agente_df['No_Ofrece'] = fibra_agente_df['Total'] - fibra_agente_df['Ofrece']
            fibra_agente_df = fibra_agente_df[fibra_agente_df['Total'] >= 5]
            fibra_agente_df['Sin Fibra %'] = (fibra_agente_df['No_Ofrece'] / fibra_agente_df['Total'] * 100).round(1)
            df_sin_fibra = fibra_agente_df[['Agente', 'Sin Fibra %', 'Total']].sort_values('Sin Fibra %', ascending=False).head(10)
            
            if not df_sin_fibra.empty:
                st.markdown("**🚨 Vendedores con Menor Oferta de Fibra:**")
                st.dataframe(df_sin_fibra, use_container_width=True, hide_index=True, height=180)
        else:
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
                    st.markdown("**🚨 Vendedores con Menor Oferta de Fibra:**")
                    st.dataframe(df_sin_fibra, use_container_width=True, hide_index=True, height=180)
    
    st.markdown("---")
    
    # =========================================================================
    # SECCIÓN 3: PROMOCIONES
    # =========================================================================
    #st.markdown('<p class="section-header">🎁 Análisis de Cumplimiento de Promociones</p>', unsafe_allow_html=True)
    
    #col1, col2, col3, col4 = st.columns(4)
    
    #with col1:
    #    st.metric("📅 Llamadas en Días Promo", f"{dias_promo_total:,}")
    #with col2:
    #    pct_menciona = menciona_promo / dias_promo_total * 100 if dias_promo_total > 0 else 0
    #    st.metric("✅ Menciona Promo", f"{menciona_promo:,}", f"{pct_menciona:.1f}%")
    #with col3:
    #    pct_no = 100 - pct_menciona if pct_menciona else 0
    #    st.metric("❌ NO Menciona Promo", f"{no_menciona_promo:,}", f"-{pct_no:.1f}%", delta_color="inverse")
    #with col4:
        # Menciona promo en total (incluyendo días no promo)
    #    if not df_filtrado.empty and 'menciona_promo' in df_filtrado.columns:
    #        menciona_total = len(df_filtrado[df_filtrado['menciona_promo'] == True])
    #    else:
    #        menciona_total = stats.get('promociones', {}).get('menciona_promo', 0)
    #    pct_total = menciona_total / total_llamadas * 100 if total_llamadas > 0 else 0
    #    st.metric("📣 Menciona Promo (Total)", f"{menciona_total:,}", f"{pct_total:.1f}%")
    
    # Gráfico de promociones
    #col1, col2 = st.columns(2)
    
    #with col1:
    #    if dias_promo_total > 0:
    #        fig = go.Figure(data=[
    #            go.Bar(name='Menciona Promo', x=['Días de Promo'], y=[menciona_promo], marker_color='#27AE60', 
    #                   text=[f'{menciona_promo} ({pct_menciona:.1f}%)'], textposition='inside', textfont=dict(color='#FFFFFF', size=12)),
    #            go.Bar(name='NO Menciona', x=['Días de Promo'], y=[no_menciona_promo], marker_color='#E74C3C',
    #                   text=[f'{no_menciona_promo} ({pct_no:.1f}%)'], textposition='inside', textfont=dict(color='#FFFFFF', size=12))
    #        ])
    #        fig.update_layout(
    #            barmode='stack',
    #            height=250,
    #            title={'text': 'Cumplimiento en Días de Promoción', 'font': {'size': 13, 'color': '#2C3E50'}},
    #            margin=dict(t=50, b=30, l=40, r=20),
    #            paper_bgcolor='#FFFFFF',
    #            plot_bgcolor='#FAFBFC',
    #            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5, font=dict(size=10))
    #        )
    #        st.plotly_chart(fig, use_container_width=True)


def pagina_coaching_vendedores(datos):
    """Página de Coaching personalizado para cada vendedor"""
    st.markdown('<div class="main-header">🎯 COMMAND · Planes de Mejora y Desarrollo de Vendedores</div>', unsafe_allow_html=True)
    
    # Subtítulo corporativo
    st.markdown("""
    <div style='background: #F8FAFC; padding: 12px 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #10B981;'>
        <p style='margin: 0; color: #334155; font-size: 0.95rem;'>
            <strong>Planes de Acción Individualizados</strong> · Recomendaciones basadas en análisis de rendimiento para cada vendedor
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Obtener permisos del usuario actual
    permisos = obtener_permisos_usuario()
    
    # Usar funciones globales de mapeo
    listado_vendedores, equipos_vendedores = cargar_listado_vendedores()
    
    def obtener_equipo_vendedor(agente_id):
        """Obtiene el equipo del vendedor"""
        agente_normalizado = str(agente_id).lower().replace(' ', '').replace('_', '')
        for equipo, vendedores in equipos_vendedores.items():
            # Normalizar nombres de vendedores para comparación
            for vendedor in vendedores:
                if agente_normalizado in vendedor.lower().replace(' ', ''):
                    return equipo
        return "Sin Equipo"
    
    # Verificar si hay datos de coaching
    if 'coaching' not in datos or not datos['coaching']:
        st.warning("⚠️ No hay datos de coaching disponibles actualmente.")
        st.info("💡 Los datos de coaching se generarán próximamente.")
        return
    
    coaching_data = datos['coaching']
    
    # =========================================================================
    # APLICAR FILTRO POR PERMISOS
    # =========================================================================
    if permisos['rol'] == 'vendedor':
        # Vendedor: Solo puede ver su propio coaching
        nombre_vendedor = permisos['nombre_usuario'].lower()
        coaching_filtrado = {}
        for agente, data in coaching_data.items():
            if nombre_vendedor in str(agente).lower():
                coaching_filtrado[agente] = data
        coaching_data = coaching_filtrado
        equipo_usuario = permisos['equipo'] if permisos['equipo'] else "Sin Equipo"
        st.info(f"👤 Mostrando coaching de: **{permisos['nombre_usuario']}** | Equipo: **{equipo_usuario}**")
        
    elif permisos['rol'] == 'supervisor' and permisos['equipos_permitidos']:
        # Supervisor: Solo puede ver coaching de su equipo
        equipo_supervisor = permisos['equipos_permitidos'][0]
        coaching_filtrado = {}
        for agente, data in coaching_data.items():
            equipo_agente = obtener_equipo_vendedor(agente)
            if equipo_agente == equipo_supervisor:
                coaching_filtrado[agente] = data
        coaching_data = coaching_filtrado
        st.info(f"🏢 Mostrando coaching del equipo: **{equipo_supervisor}**")
    
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
        <h3 style='margin:0; color: #FFFFFF; font-weight: 700;'>📋 Sistema de Desarrollo Profesional</h3>
        <p style='margin: 10px 0 0 0; color: #E0E7FF;'>
            Análisis exhaustivo del rendimiento individual de cada vendedor. 
            Cada colaborador cuenta con un <strong style='color: #FFFFFF;'>plan de acción personalizado</strong> diseñado para maximizar su potencial comercial.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Métricas generales del coaching
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Vendedores Evaluados", len(agentes_coaching))
    
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
            st.metric("📊 Puntaje Promedio", f"{np.mean(puntajes):.1f}")
    
    with col3:
        if conversiones:
            st.metric("💰 Conversión Promedio", f"{np.mean(conversiones):.1f}%")
    
    with col4:
        # Total de evaluaciones
        total_eval = sum(data.get('metricas', {}).get('evaluaciones', {}).get('total_evaluadas', 0) for data in coaching_data.values())
        st.metric("📝 Total Evaluaciones", total_eval)
    
    st.markdown("---")
    
    # Tabs principales - Ajustados según rol
    if permisos['rol'] == 'vendedor':
        # Vendedor solo ve su coaching individual
        tab1 = st.tabs(["📋 Mi Plan de Coaching"])[0]
        with tab1:
            # Mostrar coaching directo sin selector
            if len(agentes_coaching) > 0:
                agente_seleccionado = agentes_coaching[0]  # Solo hay uno para el vendedor
                data = coaching_data[agente_seleccionado]
                
                # Métricas del agente
                equipo_actual = obtener_equipo_vendedor(agente_seleccionado)
                st.markdown(f"### 📊 Mis Métricas")
                st.caption(f"📍 Equipo: **{equipo_actual}**")
                
                comparativa = data.get('comparativa', {})
                metricas = data.get('metricas', {})
                
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    puntaje = comparativa.get('puntaje_ia', {}).get('agente', 0)
                    diferencia = comparativa.get('puntaje_ia', {}).get('diferencia', 0)
                    st.metric(
                        "Puntaje",
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
                    total_ev = metricas.get('evaluaciones', {}).get('total_evaluadas', 0)
                    st.metric("Evaluaciones", total_ev)
                
                with col4:
                    prom_ev = metricas.get('evaluaciones', {}).get('puntaje_promedio', 0)
                    st.metric("Promedio Evaluaciones", f"{prom_ev:.1f}")
                
                with col5:
                    excelentes = metricas.get('evaluaciones', {}).get('excelentes', 0)
                    st.metric("Gestiones Excelentes", excelentes)
                
                # Plan de acción
                if 'plan_accion' in data and data['plan_accion']:
                    st.markdown("---")
                    st.markdown("### 📋 Mi Plan de Acción")
                    plan = data['plan_accion']
                    
                    for i, item in enumerate(plan[:10], 1):
                        prioridad = item.get('prioridad', 'Media')
                        # Determinar colores por prioridad (acepta 1/2/3 o etiquetas)
                        try:
                            pnum = int(prioridad)
                        except Exception:
                            pnum = 2 if str(prioridad).lower() in ['media','medium'] else 1 if str(prioridad).lower() in ['alta','high','1'] else 3
                        color_prioridad = '#E74C3C' if pnum == 1 else '#F39C12' if pnum == 2 else '#3B82F6'
                        bg_prioridad = '#FFF1F0' if pnum == 1 else '#FFFBEB' if pnum == 2 else '#EFF6FF'

                        descripcion = item.get('descripcion', 'Sin descripción')
                        recursos = item.get('recursos', '')

                        html = f"""
                        <details style='border-radius:8px; overflow:hidden; margin: 8px 0; border: 1px solid rgba(0,0,0,0.04);'>
                          <summary style='list-style:none; display:flex; align-items:center; gap:12px; padding:10px 12px; cursor:pointer; background: {bg_prioridad}; border-left:4px solid {color_prioridad};'>
                            <span style='width:10px; height:24px; display:inline-block; background:{color_prioridad}; border-radius:3px;'></span>
                            <strong style="color: #1E293B;">📌 {i}. {item.get('titulo', 'Acción')}</strong>
                            <span style='margin-left:auto; color:#64748B; font-size:0.9rem;'>Prioridad: {prioridad}</span>
                          </summary>
                          <div style='padding:12px; background:{bg_prioridad}; color:#475569;'>
                            <p style='margin:0 0 8px 0;'><strong>Descripción:</strong> {descripcion}</p>
                            <p style='margin:0 0 0 0;'><strong>Prioridad:</strong> {prioridad}</p>
                            {f"<p style='margin-top:8px;'><strong>Recursos sugeridos:</strong> {recursos}</p>" if recursos else ''}
                          </div>
                        </details>
                        """
                        st.markdown(html, unsafe_allow_html=True)
                
                # Fortalezas y debilidades
                if 'fortalezas' in data or 'debilidades' in data:
                    st.markdown("---")
                    col_f, col_d = st.columns(2)
                    
                    with col_f:
                        if 'fortalezas' in data and data['fortalezas']:
                            st.markdown("### 💪 Mis Fortalezas")
                            for f in data['fortalezas'][:5]:
                                st.success(f"✅ {f}")
                    
                    with col_d:
                        if 'debilidades' in data and data['debilidades']:
                            st.markdown("### 🎯 Áreas de Mejora")
                            for d in data['debilidades'][:5]:
                                st.warning(f"📌 {d}")
            else:
                st.info("No hay coaching disponible para tu perfil.")
        return  # Terminar aquí para vendedores
    
    # Para admin y supervisor, mostrar todos los tabs
    tab1, tab2, tab3 = st.tabs(["📋 Coaching Individual", "📊 Comparativa del Equipo", "📈 Ranking de Mejora"])
    
    with tab1:
        # Selector de agente con filtro por equipo
        st.markdown("### Selecciona un Vendedor")
        
        # Crear diccionario de agentes por equipo (excluyendo Sin Equipo)
        agentes_por_equipo = {}
        for agente in agentes_coaching:
            equipo = obtener_equipo_vendedor(agente)
            if equipo != "Sin Equipo":
                if equipo not in agentes_por_equipo:
                    agentes_por_equipo[equipo] = []
                agentes_por_equipo[equipo].append(agente)
        
        # Filtro por equipo - Ajustado según permisos
        col_equipo, col_vendedor = st.columns([1, 2])
        
        with col_equipo:
            if permisos['puede_ver_todos']:
                # Admin: puede ver todos los equipos (excluyendo Sin Equipo)
                equipos_disponibles = ["Todos los Equipos"] + sorted([e for e in agentes_por_equipo.keys() if e != "Sin Equipo"])
                equipo_seleccionado = st.selectbox(
                    "🏢 Filtrar por Equipo",
                    equipos_disponibles,
                    help="Filtra los vendedores por equipo/supervisor"
                )
            else:
                # Supervisor: solo ve su equipo (ya filtrado arriba)
                equipo_supervisor = permisos['equipos_permitidos'][0] if permisos['equipos_permitidos'] else "Sin Equipo"
                st.markdown(f"**🏢 Equipo:** {equipo_supervisor}")
                equipo_seleccionado = equipo_supervisor
        
        # Filtrar agentes según equipo seleccionado
        if equipo_seleccionado == "Todos los Equipos":
            agentes_filtrados = agentes_coaching
        else:
            agentes_filtrados = agentes_por_equipo.get(equipo_seleccionado, agentes_coaching)
        
        # Crear opciones con nombre real y puntaje
        opciones_agentes = []
        mapeo_display_id = {}  # Para mapear la opción mostrada al ID real
        for agente in sorted(agentes_filtrados, key=lambda x: x):
            data = coaching_data[agente]
            puntaje = data.get('comparativa', {}).get('puntaje_ia', {}).get('agente', 0)
            # El agente ya tiene el nombre real aplicado desde cargar_datos()
            display = f"{agente} (Puntaje: {puntaje:.1f})"
            opciones_agentes.append(display)
            mapeo_display_id[display] = agente
        
        with col_vendedor:
            if opciones_agentes:
                agente_seleccionado_display = st.selectbox(
                    "👤 Vendedor",
                    opciones_agentes,
                    help="Selecciona un vendedor para ver su coaching personalizado"
                )
                # Obtener nombre real del agente
                agente_seleccionado = mapeo_display_id.get(agente_seleccionado_display, "")
            else:
                st.warning("No hay vendedores en este equipo")
                return
        
        if agente_seleccionado in coaching_data:
            data = coaching_data[agente_seleccionado]
            
            # Métricas del agente
            equipo_actual = obtener_equipo_vendedor(agente_seleccionado)
            st.markdown(f"### 📊 Métricas de {agente_seleccionado}")
            st.caption(f"📍 Equipo: **{equipo_actual}**")
            
            # Sección explicativa sobre evaluaciones
            st.markdown("""
            <div style='background-color: #FFF4E6; padding: 15px; border-radius: 10px; margin-bottom: 15px; border-left: 5px solid #F59E0B;'>
                <h4 style='color: #92400E; margin-top: 0; font-size: 1rem;'>📋 ¿Cómo funciona la Evaluación?</h4>
                <p style='color: #78350F; margin-bottom: 8px; font-size: 0.9rem;'>
                    <strong>Evaluaciones = Llamadas Analizadas:</strong> Cada llamada es transcrita y evaluada automáticamente 
                    por IA según criterios de calidad establecidos.
                </p>
                <p style='color: #78350F; margin-bottom: 8px; font-size: 0.9rem;'>
                    <strong>Puntaje (0-100):</strong> Se calcula en base a 10 criterios: saludo, identificación, detección de necesidades, 
                    oferta de productos, manejo de objeciones, cierre, despedida, proactividad, empatía y resolución de problemas.
                </p>
                <p style='color: #78350F; margin-bottom: 8px; font-size: 0.9rem;'>
                    <strong>Clasificación Individual:</strong> 
                    • Excelentes (≥80) • Buenas (21-79) • Críticas (≤20)
                </p>
                <p style='color: #78350F; margin-bottom: 0; font-size: 0.9rem;'>
                    <strong>vs Equipo:</strong> Muestra la diferencia entre el puntaje del agente y el promedio de su equipo. 
                    Un valor positivo (+) indica que está por encima del equipo, negativo (-) indica que está por debajo.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            comparativa = data.get('comparativa', {})
            metricas = data.get('metricas', {})
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                puntaje = comparativa.get('puntaje_ia', {}).get('agente', 0)
                diferencia = comparativa.get('puntaje_ia', {}).get('diferencia', 0)
                st.metric(
                    "Puntaje",
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
                st.metric("Críticas", criticas, delta_color="inverse", help="Puntaje <= 20")
            
            # Mostrar información de percentil y ranking si está disponible
            percentil = comparativa.get('puntaje_ia', {}).get('percentil', 0)
            if percentil > 0:
                st.markdown(f"""
                <div style='background-color: #ECFDF5; padding: 10px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #10B981;'>
                    <p style='color: #065F46; margin: 0; font-size: 0.9rem;'>
                        🎯 <strong>Posicionamiento:</strong> Este agente se encuentra en el <strong>percentil {percentil:.0f}</strong> 
                        de su equipo, lo que significa que supera al {percentil:.0f}% de los agentes del equipo.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            # Gráfico radar de criterios
            st.markdown("### 📈 Comparativa por Criterio")
            
            # Sección explicativa sobre la comparativa
            equipo_del_agente = obtener_equipo_vendedor(agente_seleccionado)
            st.markdown(f"""
            <div style='background-color: #FEF3C7; padding: 12px; border-radius: 8px; margin-bottom: 15px; border-left: 5px solid #F59E0B;'>
                <p style='color: #78350F; margin: 0; font-size: 0.9rem;'>
                    <strong>📊 Promedio del Equipo:</strong> Se calcula como el promedio de puntajes de todos los agentes del equipo <strong>{equipo_del_agente}</strong>. 
                    Esta comparativa muestra si el agente está por encima o por debajo del rendimiento promedio de su equipo en cada criterio.
                    Un valor positivo (+) indica mejor desempeño que el equipo, negativo (-) indica área de mejora.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
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
                # Limpiar introducciones genéricas de Command
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
                        st.markdown(f"- **{fort}**")
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
                        st.markdown(f"- **{area}**")
                else:
                    st.write("No hay datos")
    
    with tab2:
        st.markdown("### 📊 Comparativa General del Equipo")
        
        # Filtro por equipo en comparativa - Ajustado según permisos
        if permisos['puede_ver_todos']:
            equipos_disponibles_tab2 = ["Todos los Equipos"] + sorted([e for e in equipos_vendedores.keys() if e != "Sin Equipo"])
            equipo_filtro_tab2 = st.selectbox(
                "🏢 Filtrar por Equipo",
                equipos_disponibles_tab2,
                key="equipo_tab2"
            )
        else:
            # Supervisor: solo su equipo
            equipo_filtro_tab2 = permisos['equipos_permitidos'][0] if permisos['equipos_permitidos'] else "Sin Equipo"
            st.markdown(f"**🏢 Equipo:** {equipo_filtro_tab2}")
        
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
                'Agente': agente,  # Ya tiene nombre real aplicado
                'Equipo': equipo_agente,
                'Puntaje': comp.get('puntaje_ia', {}).get('agente', 0),
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
        df_equipo = df_equipo.sort_values('Puntaje', ascending=False)
        
        # Gráfico de ranking
        fig = px.bar(
            df_equipo,
            x='Agente',
            y='Puntaje',
            color='vs Equipo',
            color_continuous_scale=['#EF4444', '#F59E0B', '#10B981'],
            range_color=[0, 100],
            title='Ranking de Puntaje por Agente'
        )
        fig.add_hline(
            y=df_equipo['Puntaje'].mean(),
            line_dash="dash",
            line_color="gray",
            annotation_text="Promedio"
        )
        fig.update_layout(height=400, xaxis_tickangle=-45)
        fig.update_yaxes(range=[0, 100])

        st.plotly_chart(fig, use_container_width=True)
        
        # Tabla detallada
        st.markdown("#### Tabla Detallada")
        
        # Formatear la tabla
        def color_diferencia(val):
            if isinstance(val, (int, float)):
                if val > 0:
                    return 'background-color: #144736'
                elif val < 0:
                    return 'background-color: #56131b'
            return ''
        
        styled_df = df_equipo.style.applymap(
            color_diferencia,
            subset=['vs Equipo']
        ).format({
            'Puntaje': '{:.1f}',
            'vs Equipo': '{:+.1f}',
            'Percentil': '{:.1f}',
            'Conversión': '{:.1f}%',
            'Saludo': '{:.1f}',
            'Cierre': '{:.1f}',
            'Empatía': '{:.1f}'
        })
        
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    with tab3:
        st.markdown("### 📈 Ranking y Prioridades de Mejora")
        
        # Filtro por equipo para el ranking - Ajustado según permisos
        _, equipos_vendedores_ranking = cargar_listado_vendedores()
        
        if permisos['puede_ver_todos']:
            # Admin: puede ver todos los equipos
            equipos_ranking = ["Todos los Equipos"] + sorted([e for e in equipos_vendedores_ranking.keys() if e and e != "Sin Equipo"])
            if "Sin Equipo" in equipos_vendedores_ranking:
                equipos_ranking.append("Sin Equipo")
            
            equipo_filtro_ranking = st.selectbox(
                "🏢 Filtrar por Equipo",
                equipos_ranking,
                key="equipo_filtro_ranking",
                help="Selecciona un equipo para ver su ranking específico"
            )
        else:
            # Supervisor: solo ve su equipo
            equipo_filtro_ranking = permisos['equipos_permitidos'][0] if permisos['equipos_permitidos'] else "Sin Equipo"
            st.markdown(f"**🏢 Equipo:** {equipo_filtro_ranking}")
        
        st.markdown("---")
        
        # Filtrar df_equipo según el equipo seleccionado
        if equipo_filtro_ranking == "Todos los Equipos":
            df_ranking = df_equipo.copy()
        else:
            # Obtener agentes del equipo seleccionado
            agentes_del_equipo = equipos_vendedores_ranking.get(equipo_filtro_ranking, [])
            df_ranking = df_equipo[df_equipo['Agente'].isin(agentes_del_equipo)].copy()
        
        if len(df_ranking) == 0:
            st.warning("⚠️ No hay agentes en el equipo seleccionado con datos de coaching.")
        else:
            # Calcular potencial de mejora
            df_mejora = df_ranking.copy()
            
            # Calcular índice de potencial de mejora
            # Mayor puntaje para quienes tienen más margen de mejora pero buena base
            df_mejora['Potencial'] = (100 - df_mejora['Puntaje']) * (df_mejora['Evaluaciones'] / df_mejora['Evaluaciones'].max())
            df_mejora['Tasa_Criticas'] = df_mejora['Críticas'] / df_mejora['Evaluaciones'] * 100
            
            df_mejora = df_mejora.sort_values('Potencial', ascending=False)
            
            # Mostrar info del equipo seleccionado
            if equipo_filtro_ranking != "Todos los Equipos":
                st.markdown(f"**Equipo:** {equipo_filtro_ranking} · **Agentes:** {len(df_ranking)}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🔴 Prioridad Alta (Mayor potencial de mejora)")
                
                top_mejora = df_mejora.head(10)
                
                for i, (_, row) in enumerate(top_mejora.iterrows(), 1):
                    color = "#EF4444" if row['vs Equipo'] < -10 else "#F59E0B" if row['vs Equipo'] < 0 else "#10B981"
                    st.markdown(f"""
                    <div style='background: #F8FAFC; padding: 12px; border-radius: 8px; margin: 5px 0;
                                border-left: 4px solid {color}; box-shadow: 0 2px 6px rgba(0,0,0,0.06);'>
                        <strong style='color: #1E293B;'>{i}. {row['Agente']}</strong><br>
                        <small style='color: #475569;'>Puntaje: {row['Puntaje']:.1f} | Críticas: {row['Tasa_Criticas']:.1f}% | Eval: {row['Evaluaciones']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### 🟢 Top Performers")
                
                top_performers = df_ranking.sort_values('Puntaje', ascending=False).head(10)
                
                for i, (_, row) in enumerate(top_performers.iterrows(), 1):
                    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                    st.markdown(f"""
                    <div style='background: #F8FAFC; padding: 12px; border-radius: 8px; margin: 5px 0;
                                border-left: 4px solid #10B981; box-shadow: 0 2px 6px rgba(0,0,0,0.06);'>
                        <strong style='color: #1E293B;'>{medal} {row['Agente']}</strong><br>
                        <small style='color: #475569;'>Puntaje: {row['Puntaje']:.1f} | Conv: {row['Conversión']:.1f}% | Excelentes: {row['Excelentes']}</small>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Distribución de puntajes - Gráfico profesional para juntas corporativas
        st.markdown("---")
        st.markdown("#### 📊 Distribución de Puntajes del Equipo")
        
        # Usar df_ranking filtrado para el gráfico
        df_grafico = df_ranking if 'df_ranking' in dir() and len(df_ranking) > 0 else df_equipo
        
        # Calcular estadísticas
        promedio = df_grafico['Puntaje'].mean()
        mediana = df_grafico['Puntaje'].median()
        
        # Definir colores por zona para las barras del histograma
        colores_zona = {
            'Crítico': '#DC2626',      # Rojo
            'En Desarrollo': '#F59E0B', # Amarillo/Naranja
            'Bueno': '#3B82F6',         # Azul
            'Excelente': '#10B981'      # Verde
        }
        
        # Crear datos para histograma coloreado por zona
        puntajes = df_grafico['Puntaje'].values
        
        # Separar datos por zona
        criticos_data = [p for p in puntajes if p < 30]
        desarrollo_data = [p for p in puntajes if 30 <= p < 60]
        buenos_data = [p for p in puntajes if 60 <= p < 80]
        excelentes_data = [p for p in puntajes if p >= 80]
        
        fig3 = go.Figure()
        
        # Agregar histograma por cada zona con su color correspondiente
        if criticos_data:
            fig3.add_trace(go.Histogram(
                x=criticos_data,
                name='Crítico (<30)',
                marker=dict(color=colores_zona['Crítico'], line=dict(color='#991B1B', width=1)),
                xbins=dict(start=0, end=30, size=10),
                hovertemplate='<b>Zona Crítica</b><br>Rango: %{x}<br>Agentes: %{y}<extra></extra>'
            ))
        
        if desarrollo_data:
            fig3.add_trace(go.Histogram(
                x=desarrollo_data,
                name='En Desarrollo (30-60)',
                marker=dict(color=colores_zona['En Desarrollo'], line=dict(color='#B45309', width=1)),
                xbins=dict(start=30, end=60, size=10),
                hovertemplate='<b>En Desarrollo</b><br>Rango: %{x}<br>Agentes: %{y}<extra></extra>'
            ))
        
        if buenos_data:
            fig3.add_trace(go.Histogram(
                x=buenos_data,
                name='Bueno (60-80)',
                marker=dict(color=colores_zona['Bueno'], line=dict(color='#1D4ED8', width=1)),
                xbins=dict(start=60, end=80, size=10),
                hovertemplate='<b>Bueno</b><br>Rango: %{x}<br>Agentes: %{y}<extra></extra>'
            ))
        
        if excelentes_data:
            fig3.add_trace(go.Histogram(
                x=excelentes_data,
                name='Excelente (≥80)',
                marker=dict(color=colores_zona['Excelente'], line=dict(color='#047857', width=1)),
                xbins=dict(start=80, end=100, size=10),
                hovertemplate='<b>Excelente</b><br>Rango: %{x}<br>Agentes: %{y}<extra></extra>'
            ))
        
        # Línea de promedio del equipo
        fig3.add_vline(
            x=promedio, 
            line_dash="dash", 
            line_color="#1E293B",
            line_width=3,
            annotation_text=f"Promedio: {promedio:.1f}",
            annotation_position="top",
            annotation_font=dict(size=14, color="#1E293B", family="Arial Black")
        )
        
        # Línea de meta (80 puntos = excelente)
        fig3.add_vline(
            x=80, 
            line_dash="dot", 
            line_color="#059669",
            line_width=2.5,
            annotation_text="Meta: 80",
            annotation_position="top right",
            annotation_font=dict(size=13, color="#059669", family="Arial Black")
        )
        
        fig3.update_layout(
            height=420,
            paper_bgcolor='#FFFFFF',
            plot_bgcolor='#FAFBFC',
            font=dict(family="Arial, sans-serif", size=12, color='#1E293B'),
            xaxis_title=dict(text="Puntaje", font=dict(size=14, color='#1E293B', family="Arial Black")),
            yaxis_title=dict(text="Cantidad de Agentes", font=dict(size=14, color='#1E293B', family="Arial Black")),
            xaxis=dict(
                gridcolor='#E2E8F0', 
                tickfont=dict(size=12, color='#1E293B'),
                range=[0, 100],
                dtick=10,
                showgrid=True,
                gridwidth=1
            ),
            yaxis=dict(
                gridcolor='#E2E8F0', 
                tickfont=dict(size=12, color='#1E293B'),
                showgrid=True,
                gridwidth=1
            ),
            margin=dict(t=50, b=60, l=60, r=40),
            barmode='stack',
            bargap=0.05,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                font=dict(size=12, color='#1E293B'),
                bgcolor='rgba(255,255,255,0.9)',
                bordercolor='#E2E8F0',
                borderwidth=1
            )
        )
        
        st.plotly_chart(fig3, use_container_width=True)
        
        # Resumen estadístico compacto debajo del gráfico (con colores que coinciden)
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        with col_stat1:
            criticos = len(df_ranking[df_ranking['Puntaje'] < 30])
            st.markdown(f"<div style='text-align:center; padding:10px; background:#FEE2E2; border-radius:8px; border-left: 4px solid #DC2626;'><span style='font-size:24px; font-weight:bold; color:#DC2626;'>{criticos}</span><br><small style='color:#991B1B; font-weight:600;'>Críticos (&lt;30)</small></div>", unsafe_allow_html=True)
        with col_stat2:
            bajos = len(df_ranking[(df_ranking['Puntaje'] >= 30) & (df_ranking['Puntaje'] < 60)])
            st.markdown(f"<div style='text-align:center; padding:10px; background:#FEF3C7; border-radius:8px; border-left: 4px solid #F59E0B;'><span style='font-size:24px; font-weight:bold; color:#B45309;'>{bajos}</span><br><small style='color:#78350F; font-weight:600;'>En Desarrollo (30-60)</small></div>", unsafe_allow_html=True)
        with col_stat3:
            buenos = len(df_ranking[(df_ranking['Puntaje'] >= 60) & (df_ranking['Puntaje'] < 80)])
            st.markdown(f"<div style='text-align:center; padding:10px; background:#DBEAFE; border-radius:8px; border-left: 4px solid #3B82F6;'><span style='font-size:24px; font-weight:bold; color:#1D4ED8;'>{buenos}</span><br><small style='color:#1E3A8A; font-weight:600;'>Buenos (60-80)</small></div>", unsafe_allow_html=True)
        with col_stat4:
            excelentes = len(df_ranking[df_ranking['Puntaje'] >= 80])
            st.markdown(f"<div style='text-align:center; padding:10px; background:#D1FAE5; border-radius:8px; border-left: 4px solid #10B981;'><span style='font-size:24px; font-weight:bold; color:#059669;'>{excelentes}</span><br><small style='color:#065F46; font-weight:600;'>Excelentes (≥80)</small></div>", unsafe_allow_html=True)
        
        # Recomendaciones generales
        st.markdown("---")
        st.markdown("### 💡 Recomendaciones para el Equipo")
        
        prom_puntaje = df_ranking['Puntaje'].mean()
        prom_conv = df_ranking['Conversión'].mean()
        agentes_bajo_prom = len(df_ranking[df_ranking['Puntaje'] < prom_puntaje])
        agentes_criticos = len(df_ranking[df_ranking['vs Equipo'] < -15])
        
        st.markdown(f"""
        📌 **Situación actual del equipo:**
        - Puntaje promedio: **{prom_puntaje:.1f}/100**
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
    """Página de performance por agente - Funcionalidad pendiente"""
    mostrar_proximamente("👥 COMMAND · Rendimiento Individual de Vendedores")


def pagina_analisis_temporal(df):
    """Página de análisis temporal"""
    mostrar_proximamente("📅 COMMAND · Análisis por Período de Tiempo")
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
    mostrar_proximamente("🔍 COMMAND · Detalle de Operaciones")
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
                st.markdown("**🤖 Evaluación:**")
                eval_data = eval_match.iloc[0]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Puntaje", f"{eval_data.get('puntaje_total', 0)}/100")
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


        #def pagina_quejas_no_resueltas(datos):
        #    """Página de análisis de quejas no resueltas"""
        #    st.markdown('<div class="main-header">⚠️ COMMAND · Gestión de Reclamos y Quejas Pendientes</div>', unsafe_allow_html=True)
        #    
            # Subtítulo corporativo
        #    st.markdown("""
        #    <div style='background: #FEF2F2; padding: 12px 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #EF4444;'>
        #        <p style='margin: 0; color: #7F1D1D; font-size: 0.95rem;'>
        #            <strong>Panel de Seguimiento de Reclamos</strong> · Casos que requieren atención y resolución
        #        </p>
        #    </div>
        #    """, unsafe_allow_html=True)
            
            # Obtener permisos del usuario actual
        #    permisos = obtener_permisos_usuario()
            
        #    if 'quejas' not in datos:
        #        st.warning("⚠️ No hay datos de quejas disponibles.")
        #        return
            
        #    quejas = datos['quejas']
        #    stats_original = quejas.get('estadisticas', {})
            
            # Cargar datos de filtrado
        #    listado_vendedores, equipos_vendedores = cargar_listado_vendedores()
            
            # Crear mapeo inverso: nombre -> equipo
        #    nombre_a_equipo = {}
        #    for equipo, vendedores in equipos_vendedores.items():
        #        for vendedor in vendedores:
        #            nombre_a_equipo[vendedor.lower().strip()] = equipo
    
    def obtener_equipo_por_nombre(nombre):
        """Obtiene el equipo del vendedor por su nombre"""
        if pd.isna(nombre) or nombre is None:
            return "Sin Equipo"
        nombre_lower = str(nombre).lower().strip()
        if nombre_lower in nombre_a_equipo:
            return nombre_a_equipo[nombre_lower]
        for nom, eq in nombre_a_equipo.items():
            if nombre_lower in nom or nom in nombre_lower:
                return eq
        return "Sin Equipo"
    
    # Cargar CSV de quejas para filtrado
    quejas_df = datos.get('quejas_df', pd.DataFrame())
    
    filtro_activo = False
    df_filtrado = pd.DataFrame()
    
    if not quejas_df.empty and 'agente' in quejas_df.columns:
        # Aplicar nombres reales
        quejas_df['agente_display'] = quejas_df['agente'].apply(obtener_nombre_agente)
        quejas_df['equipo'] = quejas_df['agente_display'].apply(obtener_equipo_por_nombre)
        
        # Filtrar vendedores sin equipo
        quejas_df = quejas_df[quejas_df['equipo'] != "Sin Equipo"]
        
        # =========================================================================
        # APLICAR RESTRICCIONES SEGÚN ROL DEL USUARIO
        # =========================================================================
        if permisos['rol'] == 'vendedor':
            # Vendedor: Filtrar solo sus datos
            nombre_vendedor = permisos['nombre_usuario'].lower()
            quejas_df = quejas_df[quejas_df['agente_display'].apply(
                lambda x: nombre_vendedor in str(x).lower() if pd.notna(x) else False
            )]
            equipo_seleccionado = permisos['equipo'] if permisos['equipo'] else "Sin Equipo"
            agente_seleccionado = permisos['nombre_usuario']
            filtro_activo = True
            
            st.info(f"👤 Mostrando datos de: **{permisos['nombre_usuario']}** | Equipo: **{equipo_seleccionado}**")
            df_filtrado = quejas_df.copy()
            
        elif permisos['rol'] == 'supervisor' and permisos['equipos_permitidos']:
            # Supervisor con equipo: Filtrar solo su equipo
            equipo_supervisor = permisos['equipos_permitidos'][0]
            quejas_df = quejas_df[quejas_df['equipo'] == equipo_supervisor]
            equipo_seleccionado = equipo_supervisor
            filtro_activo = True
            
            st.info(f"🏢 Mostrando datos del equipo: **{equipo_supervisor}**")
            
            # Mostrar selector de vendedor
            st.markdown('<p class="section-header">🔍 Filtro de Vendedor</p>', unsafe_allow_html=True)
            agentes_equipo = quejas_df['agente_display'].unique().tolist()
            agentes_opciones = ["Todos"] + sorted([a for a in agentes_equipo if a])
            agente_seleccionado = st.selectbox(
                "👤 Vendedor",
                agentes_opciones,
                key="filtro_agente_quejas"
            )
            
            df_filtrado = quejas_df.copy()
            if agente_seleccionado != "Todos":
                df_filtrado = df_filtrado[df_filtrado['agente_display'] == agente_seleccionado]
        else:
            # Admin o supervisor sin restricciones
            st.markdown('<p class="section-header">🔍 Filtros</p>', unsafe_allow_html=True)
            
            equipos_unicos = quejas_df['equipo'].unique().tolist()
            equipos_ordenados = sorted([e for e in equipos_unicos if e != "Sin Equipo"])
            equipos_disponibles = ["Todos los Equipos"] + equipos_ordenados
            
            col_filtro1, col_filtro2 = st.columns(2)
            
            with col_filtro1:
                equipo_seleccionado = st.selectbox(
                    "🏢 Equipo",
                    equipos_disponibles,
                    key="filtro_equipo_quejas"
                )
            
            if equipo_seleccionado != "Todos los Equipos":
                agentes_filtrados_list = quejas_df[quejas_df['equipo'] == equipo_seleccionado]['agente_display'].unique().tolist()
            else:
                agentes_filtrados_list = quejas_df['agente_display'].unique().tolist()
            
            with col_filtro2:
                agentes_opciones = ["Todos"] + sorted([a for a in agentes_filtrados_list if a])
                agente_seleccionado = st.selectbox(
                    "👤 Vendedor",
                    agentes_opciones,
                    key="filtro_agente_quejas"
                )
            
            df_filtrado = quejas_df.copy()
            if equipo_seleccionado != "Todos los Equipos":
                df_filtrado = df_filtrado[df_filtrado['equipo'] == equipo_seleccionado]
                filtro_activo = True
            if agente_seleccionado != "Todos":
                df_filtrado = df_filtrado[df_filtrado['agente_display'] == agente_seleccionado]
                filtro_activo = True
        
        # Recalcular estadísticas basadas en el filtro
        if filtro_activo or len(df_filtrado) > 0:
            total_llamadas = len(df_filtrado)
            con_queja = len(df_filtrado[df_filtrado['cantidad_quejas'] > 0]) if 'cantidad_quejas' in df_filtrado.columns else total_llamadas
            no_resueltas = int(df_filtrado['quejas_no_resueltas'].sum()) if 'quejas_no_resueltas' in df_filtrado.columns else 0
            resueltas = max(0, con_queja - no_resueltas)
            pct_con_queja = con_queja / total_llamadas * 100 if total_llamadas > 0 else 0
            pct_no_resuelta = no_resueltas / con_queja * 100 if con_queja > 0 else 0
            
            # Mostrar indicador solo para admin
            if permisos['puede_ver_todos'] and (equipo_seleccionado != "Todos los Equipos" or agente_seleccionado != "Todos"):
                filtro_texto = []
                if equipo_seleccionado != "Todos los Equipos":
                    filtro_texto.append(f"Equipo: {equipo_seleccionado}")
                if agente_seleccionado != "Todos":
                    filtro_texto.append(f"Vendedor: {agente_seleccionado}")
                st.info(f"🔍 Filtro activo: {' | '.join(filtro_texto)} - Mostrando {total_llamadas:,} registros con quejas")
        else:
            total_llamadas = stats_original.get('total_llamadas', 0)
            con_queja = stats_original.get('con_queja', 0)
            resueltas = stats_original.get('queja_resuelta', 0)
            no_resueltas = stats_original.get('queja_no_resuelta', 0)
            pct_con_queja = stats_original.get('porcentaje_con_queja', 0)
            pct_no_resuelta = stats_original.get('porcentaje_no_resuelta', 0)
    else:
        total_llamadas = stats_original.get('total_llamadas', 0)
        con_queja = stats_original.get('con_queja', 0)
        resueltas = stats_original.get('queja_resuelta', 0)
        no_resueltas = stats_original.get('queja_no_resuelta', 0)
        pct_con_queja = stats_original.get('porcentaje_con_queja', 0)
        pct_no_resuelta = stats_original.get('porcentaje_no_resuelta', 0)
    
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
        st.metric("📞 Total Llamadas", f"{total_llamadas:,}")
    with col2:
        if not filtro_activo:
            analizadas = stats_original.get('analizadas', 0)
            excluidas = stats_original.get('excluidas_venta', 0) + stats_original.get('excluidas_continuacion', 0)
            st.metric("🔍 Analizadas", f"{analizadas:,}", f"-{excluidas} excluidas")
        else:
            st.metric("🔍 Registros Filtrados", f"{len(df_filtrado):,}")
    with col3:
        st.metric("😤 Con Queja", f"{con_queja:,}", f"{pct_con_queja:.1f}%")
    with col4:
        pct_res = resueltas / con_queja * 100 if con_queja > 0 else 0
        st.metric("✅ Resueltas", f"{resueltas:,}", f"{pct_res:.1f}%")
    with col5:
        st.metric("❌ NO Resueltas", f"{no_resueltas:,}", f"-{pct_no_resuelta:.1f}%", delta_color="inverse")
    
    st.markdown("---")
    
    # =========================================================================
    # GRÁFICOS
    # =========================================================================
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<p class="section-header">📊 Estado de Quejas</p>', unsafe_allow_html=True)
        
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
    # TOP AGENTES CON MÁS QUEJAS NO RESUELTAS
    # =========================================================================
    st.markdown('<p class="section-header">🚨 Agentes con Más Quejas No Resueltas</p>', unsafe_allow_html=True)
    
    # Usar datos filtrados si hay filtro activo
    if filtro_activo and not df_filtrado.empty:
        # Calcular quejas por agente desde datos filtrados
        agentes_data = []
        for agente in df_filtrado['agente_display'].unique():
            df_agente = df_filtrado[df_filtrado['agente_display'] == agente]
            total = len(df_agente)
            no_res = df_agente['quejas_no_resueltas'].sum() if 'quejas_no_resueltas' in df_agente.columns else 0
            resueltas_ag = total - no_res
            if total >= 1:  # Mostrar todos cuando hay filtro
                pct = no_res / total * 100 if total > 0 else 0
                agentes_data.append({
                    'Agente': agente,
                    'Total Quejas': total,
                    'Resueltas': resueltas_ag,
                    'No Resueltas': no_res,
                    '% No Resueltas': round(pct, 1)
                })
    else:
        quejas_por_agente = quejas.get('quejas_por_agente', {})
        agentes_data = []
        if quejas_por_agente:
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
    st.markdown("---")
    st.markdown('<p class="section-header">📝 Detalle de Quejas No Resueltas</p>', unsafe_allow_html=True)
    
    # Usar datos filtrados si hay filtro activo
    if filtro_activo and not df_filtrado.empty:
        df_detalle = df_filtrado[['agente_display', 'id_interaccion', 'duracion_seg', 'cantidad_quejas', 'quejas_no_resueltas', 'primera_queja']].copy()
        df_detalle.columns = ['Agente', 'ID Interacción', 'Duración (seg)', 'Cant. Quejas', 'No Resueltas', 'Primera Queja']
        st.dataframe(df_detalle, use_container_width=True, hide_index=True, height=400)
    elif 'quejas_df' in datos:
        
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
    mostrar_proximamente("⏱️ COMMAND · Control de Tiempos de Atención")
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
    mostrar_proximamente("🔮 COMMAND · Clasificación de Interacciones")
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


def pagina_analisis_equipos(datos):
    """Página de análisis y planes de mejora para equipos"""
    st.markdown('<div class="main-header">👥 COMMAND · Análisis y Desarrollo de Equipos</div>', unsafe_allow_html=True)
    
    # Obtener permisos del usuario actual
    permisos = obtener_permisos_usuario()
    
    # Vendedores no tienen acceso a esta página
    if permisos['rol'] == 'vendedor':
        st.warning("⚠️ Esta sección está disponible solo para supervisores de equipo.")
        st.info("💡 Puedes ver tu información individual en la sección de Coaching de Vendedores.")
        return
    
    # Subtítulo corporativo
    st.markdown("""
    <div style='background: #F0F9FF; padding: 12px 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #0EA5E9;'>
        <p style='margin: 0; color: #0C4A6E; font-size: 0.95rem;'>
            <strong>Planes de Mejora por Equipo</strong> · Análisis de rendimiento grupal y estrategias de desarrollo
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Cargar datos necesarios
    listado_vendedores, equipos_vendedores = cargar_listado_vendedores()
    
    # Crear mapeo inverso: nombre -> equipo
    nombre_a_equipo = {}
    for equipo, vendedores in equipos_vendedores.items():
        for vendedor in vendedores:
            nombre_a_equipo[vendedor.lower().strip()] = equipo
    
    def obtener_equipo_por_nombre(nombre):
        """Obtiene el equipo del vendedor por su nombre"""
        if pd.isna(nombre) or nombre is None:
            return "Sin Equipo"
        nombre_lower = str(nombre).lower().strip()
        if nombre_lower in nombre_a_equipo:
            return nombre_a_equipo[nombre_lower]
        for nom, eq in nombre_a_equipo.items():
            if nombre_lower in nom or nom in nombre_lower:
                return eq
        return "Sin Equipo"
    
    # Verificar datos disponibles
    coaching_data = datos.get('coaching', {})
    planes_df = datos.get('planes_df', pd.DataFrame())
    quejas_df = datos.get('quejas_df', pd.DataFrame())
    
    if not coaching_data and planes_df.empty:
        st.warning("⚠️ No hay suficientes datos para el análisis de equipos.")
        return
    
    # Obtener lista de equipos disponibles (excluyendo vacíos y sin equipo)
    equipos_disponibles = [e for e in equipos_vendedores.keys() if e and e != "nan" and e != "Sin Equipo"]
    equipos_disponibles = sorted(equipos_disponibles)
    
    # =========================================================================
    # RESTRICCIÓN POR ROL: Supervisores solo ven su equipo
    # =========================================================================
    if permisos['rol'] == 'supervisor' and permisos['equipos_permitidos']:
        equipo_supervisor = permisos['equipos_permitidos'][0]
        # Verificar que el equipo del supervisor existe
        if equipo_supervisor in equipos_disponibles:
            equipos_disponibles = [equipo_supervisor]
            st.info(f"🏢 Mostrando análisis del equipo: **{equipo_supervisor}**")
        else:
            st.warning(f"⚠️ No se encontraron datos para el equipo: {equipo_supervisor}")
            return
    
    if not equipos_disponibles:
        st.warning("⚠️ No se encontraron equipos configurados.")
        return
    
    # Tabs principales - Ajustados según permisos
    if permisos['puede_comparar']:
        # Admin: puede ver comparativa de equipos
        tab1, tab2 = st.tabs(["📋 Análisis por Equipo", "📊 Comparativa de Equipos"])
    else:
        # Supervisor: solo análisis de su equipo, sin comparativa
        tab1 = st.tabs(["📋 Análisis de Mi Equipo"])[0]
        tab2 = None
    
    # =========================================================================
    # TAB 1: ANÁLISIS POR EQUIPO INDIVIDUAL
    # =========================================================================
    with tab1:
        if permisos['puede_ver_todos']:
            st.markdown("### 🏢 Selecciona un Equipo para Analizar")
            equipo_seleccionado = st.selectbox(
                "Equipo",
                equipos_disponibles,
                key="equipo_individual"
            )
        else:
            # Supervisor: no puede seleccionar, solo ve su equipo
            equipo_seleccionado = equipos_disponibles[0]
            st.markdown(f"### 🏢 Equipo: {equipo_seleccionado}")
        
        if equipo_seleccionado:
            # Obtener vendedores del equipo
            vendedores_equipo = equipos_vendedores.get(equipo_seleccionado, [])
            
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #1E3A5F 0%, #3B82F6 100%); 
                        padding: 20px; border-radius: 15px; margin: 20px 0; color: white;
                        box-shadow: 0 4px 15px rgba(30, 58, 95, 0.3);'>
                <h3 style='margin:0; color: #FFFFFF;'>📊 Equipo: {equipo_seleccionado}</h3>
                <p style='margin: 10px 0 0 0; color: #E0E7FF;'>
                    <strong>{len(vendedores_equipo)}</strong> vendedores en este equipo
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Recopilar métricas del equipo desde coaching
            metricas_equipo = {
                'puntajes_ia': [],
                'conversiones': [],
                'total_evaluaciones': 0,
                'vendedores_data': []
            }
            
            for vendedor in vendedores_equipo:
                # Buscar en coaching_data
                for agente_key, data in coaching_data.items():
                    if vendedor.lower() in agente_key.lower() or agente_key.lower() in vendedor.lower():
                        comparativa = data.get('comparativa', {})
                        puntaje = comparativa.get('puntaje_ia', {}).get('agente', 0)
                        conversion = comparativa.get('conversion', {}).get('agente', 0)
                        evaluaciones = data.get('metricas', {}).get('evaluaciones', {}).get('total_evaluadas', 0)
                        
                        metricas_equipo['puntajes_ia'].append(puntaje)
                        metricas_equipo['conversiones'].append(conversion)
                        metricas_equipo['total_evaluaciones'] += evaluaciones
                        metricas_equipo['vendedores_data'].append({
                            'Vendedor': agente_key,
                            'Puntaje': puntaje,
                            'Conversión %': conversion,
                            'Evaluaciones': evaluaciones
                        })
                        break
            
            # Métricas agregadas del equipo
            st.markdown("---")
            st.markdown('<p class="section-header">📈 Métricas del Equipo</p>', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("👥 Vendedores", len(vendedores_equipo))
            with col2:
                prom_puntaje = np.mean(metricas_equipo['puntajes_ia']) if metricas_equipo['puntajes_ia'] else 0
                st.metric("📊 Puntaje Promedio", f"{prom_puntaje:.1f}")
            with col3:
                prom_conversion = np.mean(metricas_equipo['conversiones']) if metricas_equipo['conversiones'] else 0
                st.metric("💰 Conversión Promedio", f"{prom_conversion:.1f}%")
            with col4:
                st.metric("📝 Total Evaluaciones", metricas_equipo['total_evaluaciones'])
            
            # Análisis de Fibra y Planes del equipo
            if not planes_df.empty and 'agente' in planes_df.columns:
                planes_df_temp = planes_df.copy()
                planes_df_temp['agente_display'] = planes_df_temp['agente'].apply(obtener_nombre_agente)
                planes_df_temp['equipo'] = planes_df_temp['agente_display'].apply(obtener_equipo_por_nombre)
                planes_df_temp = planes_df_temp[planes_df_temp['equipo'] != "Sin Equipo"]
                
                df_equipo_planes = planes_df_temp[planes_df_temp['equipo'] == equipo_seleccionado]
                
                if not df_equipo_planes.empty:
                    st.markdown("---")
                    st.markdown('<p class="section-header">📱 Rendimiento en Productos</p>', unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    total_llamadas = len(df_equipo_planes)
                    con_plan = len(df_equipo_planes[df_equipo_planes['cantidad_planes'] > 0])
                    pct_plan = con_plan / total_llamadas * 100 if total_llamadas > 0 else 0
                    
                    ofrece_fibra = len(df_equipo_planes[df_equipo_planes['ofrece_fibra'] == True])
                    pct_fibra = ofrece_fibra / total_llamadas * 100 if total_llamadas > 0 else 0
                    
                    df_promo = df_equipo_planes[df_equipo_planes['es_dia_promo'] == True]
                    menciona_promo = len(df_promo[df_promo['menciona_promo'] == True])
                    pct_promo = menciona_promo / len(df_promo) * 100 if len(df_promo) > 0 else 0
                    
                    with col1:
                        color_plan = "#27AE60" if pct_plan >= 70 else "#F39C12" if pct_plan >= 50 else "#E74C3C"
                        st.metric("📱 Ofrece Planes", f"{pct_plan:.1f}%", f"{con_plan}/{total_llamadas}")
                    with col2:
                        color_fibra = "#27AE60" if pct_fibra >= 50 else "#F39C12" if pct_fibra >= 30 else "#E74C3C"
                        st.metric("🏠 Ofrece Fibra", f"{pct_fibra:.1f}%", f"{ofrece_fibra}/{total_llamadas}")
                    with col3:
                        st.metric("🎁 Menciona Promo", f"{pct_promo:.1f}%", f"{menciona_promo}/{len(df_promo)} en días promo")
            
            # Análisis de Quejas del equipo
            #if not quejas_df.empty and 'agente' in quejas_df.columns:
            #    quejas_df_temp = quejas_df.copy()
            #    quejas_df_temp['agente_display'] = quejas_df_temp['agente'].apply(obtener_nombre_agente)
            #    quejas_df_temp['equipo'] = quejas_df_temp['agente_display'].apply(obtener_equipo_por_nombre)
                
            #    df_equipo_quejas = quejas_df_temp[quejas_df_temp['equipo'] == equipo_seleccionado]
                
            #    if not df_equipo_quejas.empty:
            #        st.markdown("---")
            #        st.markdown('<p class="section-header">⚠️ Gestión de Quejas</p>', unsafe_allow_html=True)
                    
            #        total_quejas = len(df_equipo_quejas)
            #        no_resueltas = int(df_equipo_quejas['quejas_no_resueltas'].sum())
            #        resueltas = total_quejas - no_resueltas
            #        pct_resolucion = resueltas / total_quejas * 100 if total_quejas > 0 else 0
                    
            #        col1, col2, col3 = st.columns(3)
            #        with col1:
            #            st.metric("📋 Total Quejas", total_quejas)
            #        with col2:
            #            st.metric("✅ Resueltas", resueltas, f"{pct_resolucion:.1f}%")
            #        with col3:
            #            st.metric("❌ No Resueltas", no_resueltas)
            
            # Tabla de vendedores del equipo
            st.markdown("---")
            st.markdown('<p class="section-header">👥 Detalle por Vendedor</p>', unsafe_allow_html=True)
            
            if metricas_equipo['vendedores_data']:
                df_vendedores = pd.DataFrame(metricas_equipo['vendedores_data'])
                df_vendedores = df_vendedores.sort_values('Puntaje', ascending=False)
                
                # Gráfico de barras de puntajes
                fig = px.bar(
                    df_vendedores,
                    x='Vendedor',
                    y='Puntaje',
                    color='Puntaje',
                    color_continuous_scale=['#E74C3C', '#F39C12', '#27AE60'],
                    range_color=[0, 100],
                    text='Puntaje'
                )
                fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                fig.update_layout(
                    height=350,
                    paper_bgcolor='#FFFFFF',
                    plot_bgcolor='#FAFBFC',
                    showlegend=False,
                    xaxis_tickangle=-45,
                    margin=dict(t=30, b=80),
                    font=dict(color="#000000")
                )
                fig.update_xaxes(
                    tickfont=dict(color="#000000"),
                    title=dict(font=dict(color="#000000"))
                )

                fig.update_yaxes(
                    range=[0, 100],
                    tickfont=dict(color="#000000"),
                    title=dict(font=dict(color="#000000"))
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.dataframe(df_vendedores, use_container_width=True, hide_index=True)
            else:
                st.info("No hay datos de evaluación para los vendedores de este equipo.")
            
            # Plan de mejora del equipo
            st.markdown("---")
            st.markdown('<p class="section-header">🎯 Plan de Mejora del Equipo</p>', unsafe_allow_html=True)
            
            # Sección explicativa sobre planes de mejora
            st.markdown("""
            <div style='background-color: #F0F9FF; padding: 15px; border-radius: 10px; margin-bottom: 15px; border-left: 5px solid #0EA5E9;'>
                <h4 style='color: #075985; margin-top: 0; font-size: 1rem;'>📊 ¿Cómo se evalúa el puntaje?</h4>
                <p style='color: #0C4A6E; margin-bottom: 8px; font-size: 0.9rem;'>
                    <strong>Evaluaciones = Llamadas del Equipo:</strong> Todas las llamadas grabadas y procesadas de los agentes del equipo.
                    El sistema transcribe cada llamada y la evalúa automáticamente con IA.
                </p>
                <p style='color: #0C4A6E; margin-bottom: 8px; font-size: 0.9rem;'>
                    <strong>Clasificación de Llamadas (Equipo):</strong><br>
                    • <span style='color: #10B981;'>✓ Excelentes</span> (Puntaje ≥ 80): Cumplen con estándares de excelencia<br>
                    • <span style='color: #F59E0B;'>⚠ Requieren Atención</span> (Puntaje 41-79): Necesitan mejoras en algunos criterios<br>
                    • <span style='color: #EF4444;'>⚠ Críticas</span> (Puntaje ≤ 40): No cumplen con los estándares mínimos de calidad
                </p>
                <p style='color: #0C4A6E; margin-bottom: 0; font-size: 0.9rem;'>
                    <strong>Base del Puntaje:</strong> Se evalúan 10 criterios por llamada (saludo, identificación, necesidades, 
                    oferta, objeciones, cierre, despedida, proactividad, empatía, resolución). El promedio de todos los criterios 
                    da el puntaje total de 0 a 100 por llamada.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Identificar áreas de mejora
            recomendaciones = []
            
            if metricas_equipo['puntajes_ia']:
                prom_puntaje = np.mean(metricas_equipo['puntajes_ia'])
                if prom_puntaje < 50:
                    recomendaciones.append({
                        'area': '📊 Puntaje',
                        'estado': 'Crítico',
                        'color': '#E74C3C',
                        'recomendacion': 'Implementar capacitaciones intensivas de técnicas de venta y manejo de objeciones.'
                    })
                elif prom_puntaje < 70:
                    recomendaciones.append({
                        'area': '📊 Puntaje',
                        'estado': 'En desarrollo',
                        'color': '#F39C12',
                        'recomendacion': 'Reforzar prácticas de cierre comercial y seguimiento de llamadas.'
                    })
            
            if 'pct_fibra' in dir() and pct_fibra < 30:
                recomendaciones.append({
                    'area': '🏠 Oferta de Fibra',
                    'estado': 'Crítico',
                    'color': '#E74C3C',
                    'recomendacion': 'Entrenar al equipo en identificación de oportunidades de venta cruzada de Fibra.'
                })
            elif 'pct_fibra' in dir() and pct_fibra < 50:
                recomendaciones.append({
                    'area': '🏠 Oferta de Fibra',
                    'estado': 'En desarrollo',
                    'color': '#F39C12',
                    'recomendacion': 'Incluir recordatorios de oferta de Fibra en el speech comercial.'
                })
            
            if 'pct_resolucion' in dir() and pct_resolucion < 70:
                recomendaciones.append({
                    'area': '⚠️ Resolución de Quejas',
                    'estado': 'Requiere atención',
                    'color': '#F39C12',
                    'recomendacion': 'Capacitar en técnicas de manejo de objeciones y resolución de conflictos.'
                })
            
            if recomendaciones:
                for rec in recomendaciones:
                    st.markdown(f"""
                    <div style='background: #F8FAFC; padding: 15px; border-radius: 10px; margin: 10px 0; 
                                border-left: 4px solid {rec['color']}; box-shadow: 0 2px 5px rgba(0,0,0,0.06);'>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <strong style='color: #1E293B;'>{rec['area']}</strong>
                            <span style='background: {rec['color']}; color: white; padding: 3px 10px; border-radius: 15px; font-size: 0.8rem;'>
                                {rec['estado']}
                            </span>
                        </div>
                        <p style='margin: 10px 0 0 0; color: #475569;'>{rec['recomendacion']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("✅ El equipo está cumpliendo los objetivos principales. Continuar con las buenas prácticas.")
            
            # =================================================================
            # COACHING COMMAND DEL EQUIPO - CARGAR DESDE ARCHIVO JSON
            # =================================================================
            st.markdown("---")
            st.markdown('<p class="section-header">🤖 Plan de Acción del Equipo</p>', unsafe_allow_html=True)
            
            # Intentar cargar el archivo de coaching del equipo
            import os
            import json
            
            # Normalizar nombre del equipo para el archivo
            nombre_archivo = equipo_seleccionado.replace(" ", "_").upper()
            ruta_coaching = f"reportes/coaching_equipos/coaching_{nombre_archivo}.json"
            
            if os.path.exists(ruta_coaching):
                try:
                    coaching_equipo_data = cargar_coaching_equipo(ruta_coaching)
                    coaching_ia = (coaching_equipo_data or {}).get('coaching_ia', {})
                    
                    if coaching_ia:
                        # Resumen Ejecutivo
                        resumen = coaching_ia.get('resumen_ejecutivo', '')
                        if resumen:
                            st.markdown(f"""
                            <div style='background: linear-gradient(135deg, #1E3A5F 0%, #3B82F6 100%); 
                                        padding: 20px; border-radius: 15px; margin: 15px 0; color: white;
                                        box-shadow: 0 4px 15px rgba(30, 58, 95, 0.3);'>
                                <h4 style='margin:0 0 10px 0; color: #93C5FD;'>📋 Resumen Ejecutivo</h4>
                                <p style='margin: 0; color: #E0E7FF; line-height: 1.6;'>{resumen}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Diagnóstico
                        diagnostico = coaching_ia.get('diagnostico', {})
                        if diagnostico:
                            nivel = diagnostico.get('nivel_rendimiento', 'N/A')
                            color_nivel = '#27AE60' if nivel == 'BUENO' else '#F39C12' if nivel in ['REGULAR', 'ESTABLE'] else '#E74C3C'
                            
                            col_d1, col_d2, col_d3, col_d4 = st.columns(4)
                            with col_d1:
                                st.metric("📊 Nivel", nivel)
                            with col_d2:
                                st.metric("⭐ Puntaje", f"{diagnostico.get('puntaje_equipo', 0):.1f}")
                            with col_d3:
                                st.metric("🏆 Ranking", diagnostico.get('posicion_ranking', 'N/A'))
                            with col_d4:
                                st.metric("📈 Tendencia", diagnostico.get('tendencia', 'N/A'))
                        
                        # Fortalezas y Áreas de Mejora en columnas
                        col_fm1, col_fm2 = st.columns(2)
                        fortalezas = coaching_ia.get('fortalezas_equipo', [])
                        mejoras = coaching_ia.get('areas_mejora_prioritarias', [])

                        # =========================
                        # Normalizar áreas de fortalezas (lower + strip)
                        # =========================
                        areas_fortalezas = {
                            f.get("area", "").strip().lower()
                            for f in fortalezas
                            if f.get("area")
                        }

                        # =========================
                        # Filtrar mejoras que NO estén en fortalezas
                        # =========================
                        mejoras_filtradas = [
                                m for m in mejoras
                                if m.get("area", "").strip().lower() not in areas_fortalezas]
                        with col_fm1:
                            st.markdown("#### 💪 Fortalezas del Equipo")
                            fortalezas = coaching_ia.get('fortalezas_equipo', [])
                            for fort in fortalezas:
                                st.markdown(f"""
                                <div style='background: #ECFDF5; padding: 12px; border-radius: 8px; margin: 8px 0; border-left: 4px solid #10B981;'>
                                    <strong style='color: #065F46;'>{fort.get('area', 'N/A')}</strong>
                                    <p style='margin: 5px 0; color: #047857; font-size: 0.9rem;'>{fort.get('evidencia', '')}</p>
                                    <p style='margin: 0; color: #064E3B; font-size: 0.85rem;'><em>Impacto: {fort.get('impacto', '')}</em></p>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        with col_fm2:
                            st.markdown("#### 🎯 Áreas de Mejora Prioritarias")
                            mejoras = coaching_ia.get('areas_mejora_prioritarias', [])
                            for mejora in mejoras:
                                st.markdown(f"""
                                <div style='background: #FEF3C7; padding: 12px; border-radius: 8px; margin: 8px 0; border-left: 4px solid #F59E0B;'>
                                    <strong style='color: #92400E;'>{mejora.get('area', 'N/A')}</strong>
                                    <p style='margin: 5px 0; color: #B45309; font-size: 0.9rem;'>{mejora.get('situacion_actual', '')}</p>
                                    <p style='margin: 0; color: #78350F; font-size: 0.85rem;'><strong>Meta:</strong> {mejora.get('meta', '')}</p>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        # Plan de Acción
                        st.markdown("---")
                        st.markdown("#### 📝 Plan de Acción del Equipo")
                        plan_accion = coaching_ia.get('plan_accion_equipo', [])
                        
                        for i, accion in enumerate(plan_accion, 1):
                            prioridad = accion.get('prioridad', 0)
                            color_prioridad = '#E74C3C' if prioridad == 1 else '#F39C12' if prioridad == 2 else '#3B82F6'
                            bg_prioridad = '#FFF1F0' if prioridad == 1 else '#FFFBEB' if prioridad == 2 else '#EFF6FF'
                            
                            # Usar HTML nativo <details> para un colapso claro y accesible
                            st.markdown(f"""<details style='background: {bg_prioridad}; padding: 0; border-radius: 10px; margin: 10px 0; border-left: 5px solid {color_prioridad}; box-shadow: 0 2px 8px rgba(0,0,0,0.06);'><summary style='list-style: none; cursor: pointer; padding: 12px 15px; display:flex; justify-content:space-between; align-items:center;'><div style='display:flex; gap:12px; align-items:center;'><span style='background:{color_prioridad}; color:white; padding:4px 10px; border-radius:12px; font-weight:700;'>Prioridad {prioridad}</span><strong style='color:#0F172A; font-size:0.95rem;'>{accion.get('accion', '')}</strong></div><span style='color:#64748B; font-size:0.85rem;'>📅 {accion.get('plazo', 'N/A')}</span></summary><div style='padding: 12px 15px 16px 15px; color: #475569; border-top: 1px solid rgba(0,0,0,0.03);'><p style='margin:0 0 6px 0;'><strong>Responsable:</strong> {accion.get('responsable', 'N/A')}</p><p style='margin:0 0 6px 0;'><strong>Indicador de Éxito:</strong> {accion.get('indicador_exito', 'N/A')}</p><p style='margin:0;'><strong>Recursos Necesarios:</strong> {accion.get('recursos_necesarios', 'N/A')}</p></div></details>""", unsafe_allow_html=True)
                        
                        # Capacitaciones Recomendadas
                        capacitaciones = coaching_ia.get('capacitaciones_recomendadas', [])
                        if capacitaciones:
                            st.markdown("---")
                            st.markdown("#### 📚 Capacitaciones Recomendadas")
                            
                            for cap in capacitaciones:
                                st.markdown(f"""
                                <div style='background: #EDE9FE; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #8B5CF6;'>
                                    <strong style='color: #5B21B6;'>📖 {cap.get('tema', 'N/A')}</strong>
                                    <p style='margin: 8px 0; color: #6D28D9;'><em>Objetivo: {cap.get('objetivo', '')}</em></p>
                                    <p style='margin: 0; color: #7C3AED; font-size: 0.9rem;'>
                                        <strong>Modalidad:</strong> {cap.get('modalidad', 'N/A')} | 
                                        <strong>Duración:</strong> {cap.get('duracion_sugerida', 'N/A')}
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        # Metas del Equipo
                        metas = coaching_ia.get('metas_equipo', {})
                        if metas:
                            st.markdown("---")
                            st.markdown("#### 🎯 Metas del Equipo")
                            
                            col_m1, col_m2 = st.columns(2)
                            
                            with col_m1:
                                st.markdown("**📅 Corto Plazo (30 días)**")
                                for meta in metas.get('corto_plazo_30_dias', []):
                                    st.markdown(f"""
                                    <div style='background: #DBEAFE; padding: 12px; border-radius: 8px; margin: 8px 0;'>
                                        <strong style='color: #1E40AF;'>{meta.get('meta', '')}</strong>
                                        <p style='margin: 5px 0 0 0; color: #1D4ED8; font-size: 0.9rem;'>
                                            Actual: {meta.get('valor_actual', 'N/A')} → Objetivo: {meta.get('valor_objetivo', 'N/A')}
                                        </p>
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            with col_m2:
                                st.markdown("**📆 Mediano Plazo (90 días)**")
                                for meta in metas.get('mediano_plazo_90_dias', []):
                                    st.markdown(f"""
                                    <div style='background: #FEE2E2; padding: 12px; border-radius: 8px; margin: 8px 0;'>
                                        <strong style='color: #991B1B;'>{meta.get('meta', '')}</strong>
                                        <p style='margin: 5px 0 0 0; color: #B91C1C; font-size: 0.9rem;'>
                                            Actual: {meta.get('valor_actual', 'N/A')} → Objetivo: {meta.get('valor_objetivo', 'N/A')}
                                        </p>
                                    </div>
                                    """, unsafe_allow_html=True)
                        
                        # Seguimiento
                        seguimiento = coaching_ia.get('seguimiento', {})
                        if seguimiento:
                            st.markdown("---")
                            st.markdown("#### 📊 Seguimiento")
                            
                            col_s1, col_s2 = st.columns(2)
                            with col_s1:
                                st.markdown(f"**🗓️ Reuniones:** {seguimiento.get('reuniones_sugeridas', 'N/A')}")
                                st.markdown("**📈 Métricas a Monitorear:**")
                                for metrica in seguimiento.get('metricas_monitorear', []):
                                    st.markdown(f"- {metrica}")
                            with col_s2:
                                st.markdown("<span style='color:#000000; font-weight:bold;'>⚠️ Alertas:</span>", unsafe_allow_html=True)
                                for alerta in seguimiento.get('alertas', []):
                                    st.markdown(f"<div style='background:#FEF3C7; color:#000000; padding:10px; border-radius:6px; margin-bottom:6px;'>⚠️ {alerta}</div>", unsafe_allow_html=True)
                    else:
                        st.info("ℹ️ No hay datos de coaching disponibles para este equipo.")
                        
                except Exception as e:
                    st.warning(f"⚠️ Error al cargar el coaching del equipo: {str(e)}")
            else:
                st.info(f"ℹ️ No se encontró el archivo de coaching para el equipo '{equipo_seleccionado}'. Ejecute el proceso de coaching de equipos primero.")
    
    # =========================================================================
    # TAB 2: COMPARATIVA DE EQUIPOS (Solo para admin)
    # =========================================================================
    if tab2 is not None:
        with tab2:
            st.markdown("### 📊 Comparativa entre Equipos")
            
            # Sección explicativa
            st.markdown("""
            <div style='background-color: #E8F4F8; padding: 20px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #3498DB;'>
                <h4 style='color: #2C3E50; margin-top: 0;'>📋 Información sobre Evaluaciones de Equipo</h4>
                <p style='color: #34495E; margin-bottom: 10px;'>
                    <strong>¿Qué representa el Total de Evaluaciones?</strong><br>
                    El total de evaluaciones incluye todas las llamadas procesadas de todos los agentes pertenecientes a cada equipo.
                </p>
                <p style='color: #34495E; margin-bottom: 10px;'>
                    <strong>¿Cómo se calcula el Índice de Calidad?</strong><br>
                    El índice de calidad se obtiene del promedio del puntaje de evaluación de todas las llamadas del equipo, 
                    basado en criterios como: saludo correcto, identificación, oferta de productos (fibra, planes), 
                    resolución de quejas, y cierre de llamada. El puntaje máximo es 100.
                </p>
                <p style='color: #34495E; margin-bottom: 10px;'>
                    <strong>Llamadas que Requieren Atención:</strong><br>
                    Son aquellas evaluaciones con puntaje menor a 70 (consideradas críticas) que requieren 
                    coaching o capacitación adicional para mejorar el desempeño.
                </p>
                <p style='color: #34495E; margin-bottom: 0;'>
                    <strong>Llamadas Sin Evaluación:</strong><br>
                    Representa el porcentaje de llamadas que aún no han sido procesadas o evaluadas por el sistema de IA.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Selector múltiple de equipos
            todos_equipos_comparar = [e for e in equipos_vendedores.keys() if e and e != "nan" and e != "Sin Equipo"]
            equipos_comparar = st.multiselect(
                "Selecciona los equipos a comparar:",
                sorted(todos_equipos_comparar),
                default=sorted(todos_equipos_comparar)[:min(3, len(todos_equipos_comparar))],
                key="equipos_comparativa"
            )
        
            if len(equipos_comparar) < 2:
                st.warning("⚠️ Selecciona al menos 2 equipos para comparar.")
            else:
                # Recopilar métricas de todos los equipos seleccionados
                comparativa_data = []
                
                for equipo in equipos_comparar:
                    vendedores_eq = equipos_vendedores.get(equipo, [])
                    
                    metricas_eq = {
                        'Equipo': equipo,
                        'Vendedores': len(vendedores_eq),
                        'Puntaje': 0,
                        'Conversión %': 0,
                        'Ofrece Fibra %': 0,
                        'Ofrece Plan %': 0,
                        'Quejas Resueltas %': 0
                    }
                    
                    # Métricas de coaching
                    puntajes = []
                    conversiones = []
                    for vendedor in vendedores_eq:
                        for agente_key, data in coaching_data.items():
                            if vendedor.lower() in agente_key.lower() or agente_key.lower() in vendedor.lower():
                                puntajes.append(data.get('comparativa', {}).get('puntaje_ia', {}).get('agente', 0))
                                conversiones.append(data.get('comparativa', {}).get('conversion', {}).get('agente', 0))
                                break
                    
                    metricas_eq['Puntaje'] = round(np.mean(puntajes), 1) if puntajes else 0
                    metricas_eq['Conversión %'] = round(np.mean(conversiones), 1) if conversiones else 0
                    
                    # Métricas de planes
                    if not planes_df.empty and 'agente' in planes_df.columns:
                        planes_df_temp = planes_df.copy()
                        planes_df_temp['agente_display'] = planes_df_temp['agente'].apply(obtener_nombre_agente)
                        planes_df_temp['equipo'] = planes_df_temp['agente_display'].apply(obtener_equipo_por_nombre)
                        planes_df_temp = planes_df_temp[planes_df_temp['equipo'] != "Sin Equipo"]
                        df_eq = planes_df_temp[planes_df_temp['equipo'] == equipo]
                        
                        if not df_eq.empty:
                            total = len(df_eq)
                            metricas_eq['Ofrece Fibra %'] = round(len(df_eq[df_eq['ofrece_fibra'] == True]) / total * 100, 1)
                            metricas_eq['Ofrece Plan %'] = round(len(df_eq[df_eq['cantidad_planes'] > 0]) / total * 100, 1)
                    
                    # Métricas de quejas
                    if not quejas_df.empty and 'agente' in quejas_df.columns:
                        quejas_df_temp = quejas_df.copy()
                        quejas_df_temp['agente_display'] = quejas_df_temp['agente'].apply(obtener_nombre_agente)
                        quejas_df_temp['equipo'] = quejas_df_temp['agente_display'].apply(obtener_equipo_por_nombre)
                        quejas_df_temp = quejas_df_temp[quejas_df_temp['equipo'] != "Sin Equipo"]
                        df_eq_q = quejas_df_temp[quejas_df_temp['equipo'] == equipo]
                        
                        if not df_eq_q.empty:
                            total_q = len(df_eq_q)
                            no_res = int(df_eq_q['quejas_no_resueltas'].sum())
                            metricas_eq['Quejas Resueltas %'] = round((total_q - no_res) / total_q * 100, 1) if total_q > 0 else 0
                    
                    comparativa_data.append(metricas_eq)
                
                df_comparativa = pd.DataFrame(comparativa_data)
                df_comparativa = df_comparativa.drop(columns=['Quejas Resueltas %'], errors='ignore')

                # Métricas principales
                st.markdown("---")
                st.markdown('<p class="section-header">📈 Resumen Comparativo</p>', unsafe_allow_html=True)
                
                # Mostrar tabla comparativa
                st.dataframe(
                    df_comparativa.style.background_gradient(subset=['Puntaje', 'Conversión %', 'Ofrece Fibra %', 'Ofrece Plan %'], cmap='RdYlGn'),
                    use_container_width=True,
                    hide_index=True
                )
                
                st.markdown("---")
                
                # Gráficos comparativos
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**📊 Puntaje por Equipo**")
                    fig = px.bar(
                        df_comparativa,
                        x='Equipo',
                        y='Puntaje',
                        color='Puntaje',
                        color_continuous_scale=['#E74C3C', '#F39C12', '#27AE60'],
                        text='Puntaje'
                    )
                    fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                    fig.update_layout(
                        height=300,
                        paper_bgcolor='#FFFFFF',
                        plot_bgcolor='#FAFBFC',
                        showlegend=False,
                        font=dict(color="#000000")
                    )
                    fig.update_xaxes(
                        tickfont=dict(color="#000000"),
                        title=dict(font=dict(color="#000000"))
                    )

                    fig.update_yaxes(
                        tickfont=dict(color="#000000"),
                        title=dict(font=dict(color="#000000"))
                    )
                    fig.update_yaxes(range=[0, df_comparativa['Puntaje'].max() + 10])
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.markdown("**💰 Conversión por Equipo**")
                    fig = px.bar(
                        df_comparativa,
                        x='Equipo',
                        y='Conversión %',
                        color='Conversión %',
                        color_continuous_scale=['#E74C3C', '#F39C12', '#27AE60'],
                        text='Conversión %'
                    )
                    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                    fig.update_layout(
                        height=300,
                        paper_bgcolor='#FFFFFF',
                        plot_bgcolor='#FAFBFC',
                        showlegend=False,
                        font=dict(color="#000000")
                    )
                    fig.update_xaxes(
                        tickfont=dict(color="#000000"),
                        title=dict(font=dict(color="#000000"))
                    )

                    fig.update_yaxes(
                        tickfont=dict(color="#000000"),
                        title=dict(font=dict(color="#000000"))
                    )
                    fig.update_yaxes(range=[0, df_comparativa['Conversión %'].max() + 5])

                    st.plotly_chart(fig, use_container_width=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**🏠 Oferta de Fibra por Equipo**")
                    fig = px.bar(
                        df_comparativa,
                        x='Equipo',
                        y='Ofrece Fibra %',
                        color='Ofrece Fibra %',
                        color_continuous_scale=['#E74C3C', '#F39C12', '#27AE60'],
                        text='Ofrece Fibra %'
                    )
                    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                    fig.update_layout(
                        height=300,
                        paper_bgcolor='#FFFFFF',
                        plot_bgcolor='#FAFBFC',
                        showlegend=False,
                        font=dict(color="#000000")
                    )
                    fig.update_xaxes(
                        tickfont=dict(color="#000000"),
                        title=dict(font=dict(color="#000000"))
                    )

                    fig.update_yaxes(
                        tickfont=dict(color="#000000"),
                        title=dict(font=dict(color="#000000"))
                    )
                    fig.update_yaxes(range=[0, df_comparativa['Ofrece Fibra %'].max() + 5])

                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.markdown("**📱 Oferta de Planes por Equipo**")
                    fig = px.bar(
                        df_comparativa,
                        x='Equipo',
                        y='Ofrece Plan %',
                        color='Ofrece Plan %',
                        color_continuous_scale=['#E74C3C', '#F39C12', '#27AE60'],
                        text='Ofrece Plan %'
                    )
                    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                    fig.update_layout(
                        height=300,
                        paper_bgcolor='#FFFFFF',
                        plot_bgcolor='#FAFBFC',
                        showlegend=False,
                        font=dict(color="#000000")
                    )
                    fig.update_xaxes(
                        tickfont=dict(color="#000000"),
                        title=dict(font=dict(color="#000000"))
                    )

                    fig.update_yaxes(
                        tickfont=dict(color="#000000"),
                        title=dict(font=dict(color="#000000"))
                    )
                    fig.update_yaxes(range=[0, df_comparativa['Ofrece Plan %'].max() + 5])

                    st.plotly_chart(fig, use_container_width=True)
            
            # Gráfico radar comparativo
            #st.markdown("---")
            #st.markdown('<p class="section-header">🎯 Radar de Rendimiento</p>', unsafe_allow_html=True)
            
            #categorias = ['Puntaje', 'Conversión %', 'Ofrece Fibra %', 'Ofrece Plan %', 'Quejas Resueltas %']
            
            #fig = go.Figure()
            
            #colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']
            
            #for i, equipo in enumerate(equipos_comparar):
            #    eq_data = df_comparativa[df_comparativa['Equipo'] == equipo].iloc[0]
            #    valores = [eq_data[cat] for cat in categorias]
            #    valores.append(valores[0])  # Cerrar el radar
                
            #    fig.add_trace(go.Scatterpolar(
            #        r=valores,
            #        theta=categorias + [categorias[0]],
            #        fill='toself',
            #        name=equipo,
            #        line_color=colors[i % len(colors)],
            #        opacity=0.7
            #    ))
            
            #fig.update_layout(
            #    polar=dict(
            #        radialaxis=dict(
            #            visible=True,
            #            range=[0, 100]
            #        )
            #    ),
            #    showlegend=True,
            #    height=450,
            #    paper_bgcolor='#FFFFFF',
            #    legend=dict(
            #        orientation='h',
            #        yanchor='bottom',
            #        y=-0.2,
            #        xanchor='center',
            #        x=0.5
            #    )
            #)
            #st.plotly_chart(fig, use_container_width=True)
            
            # Ranking final
            st.markdown("---")
            st.markdown('<p class="section-header">🏆 Ranking de Equipos</p>', unsafe_allow_html=True)
            
            # Calcular score general (promedio de todas las métricas)
            df_comparativa['Score General'] = (
                df_comparativa['Puntaje'] + 
                df_comparativa['Conversión %'] + 
                df_comparativa['Ofrece Fibra %'] + 
                df_comparativa['Ofrece Plan %']
            ) / 4
            
            df_ranking = df_comparativa[['Equipo', 'Score General']].sort_values('Score General', ascending=False)
            
            for idx, row in df_ranking.iterrows():
                posicion = df_ranking.index.tolist().index(idx) + 1
                medalla = "🥇" if posicion == 1 else "🥈" if posicion == 2 else "🥉" if posicion == 3 else f"#{posicion}"
                color = "#FFD700" if posicion == 1 else "#C0C0C0" if posicion == 2 else "#CD7F32" if posicion == 3 else "#000000"
                color_medalla = "#000000" if posicion > 3 else color

                st.markdown(f"""
                <div style='background: linear-gradient(90deg, {color}22, #FFFFFF); padding: 15px 20px; 
                            border-radius: 10px; margin: 8px 0; border-left: 4px solid {color};
                            display: flex; justify-content: space-between; align-items: center;'>
                    <span style='font-size: 1.5rem; color: {color_medalla};'>{medalla}</span>
                    <strong style='color: #1E293B; font-size: 1.1rem;'>{row['Equipo']}</strong>
                    <span style='background: {color}; color: {"#000" if posicion <= 2 else "#FFF"}; 
                                 padding: 5px 15px; border-radius: 20px; font-weight: bold;'>
                        {row['Score General']:.1f} pts
                    </span>
                </div>
                """, unsafe_allow_html=True)


def pagina_evaluaciones_gemini(datos):
    """Página de evaluaciones realizadas con Inteligencia Artificial"""
    st.markdown('<div class="main-header">🤖 COMMAND · Evaluación Automatizada de Calidad</div>', unsafe_allow_html=True)
    
    # Subtítulo corporativo
    st.markdown("""
    <div style='background: #F8FAFC; padding: 12px 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #8B5CF6;'>
        <p style='margin: 0; color: #334155; font-size: 0.95rem;'>
            <strong>Sistema de Evaluación con Inteligencia Artificial</strong> · Análisis automático de calidad de cada interacción
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Obtener permisos del usuario actual
    permisos = obtener_permisos_usuario()
    
    # Verificar datos
    if 'evaluaciones_gemini_df' not in datos:
        st.warning("⚠️ No se encontraron evaluaciones de disponibles.")
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
    
    # =========================================================================
    # APLICAR FILTRO DE FECHAS DESDE SIDEBAR
    # =========================================================================
    fecha_inicio_filtro = st.session_state.get('filtro_fecha_inicio')
    fecha_fin_filtro = st.session_state.get('filtro_fecha_fin')
    
    if 'fecha_llamada' in df.columns and fecha_inicio_filtro and fecha_fin_filtro:
        # Convertir fechas del filtro a datetime para comparación
        fecha_inicio_dt = pd.to_datetime(fecha_inicio_filtro)
        fecha_fin_dt = pd.to_datetime(fecha_fin_filtro)
        
        df_original_len = len(df)
        df = df[(df['fecha_llamada'] >= fecha_inicio_dt) & (df['fecha_llamada'] <= fecha_fin_dt)]
        
        # Mostrar info del filtro aplicado
        if len(df) < df_original_len:
            st.info(f"📅 Filtro de fecha aplicado: **{fecha_inicio_filtro.strftime('%d/%m/%Y')}** - **{fecha_fin_filtro.strftime('%d/%m/%Y')}** ({len(df):,} de {df_original_len:,} evaluaciones)")
    
    # Obtener mapeo de equipos para los filtros
    _, equipos_vendedores = cargar_listado_vendedores()
    
    # Aplicar mapeo de nombres a todo el dataframe (usando función global)
    if 'agente' in df.columns:
        df['agente'] = df['agente'].apply(obtener_nombre_agente)
    
    # Crear mapeo inverso: nombre -> equipo
    nombre_a_equipo = {}
    for equipo, vendedores in equipos_vendedores.items():
        for vendedor in vendedores:
            nombre_a_equipo[vendedor.lower().strip()] = equipo
    
    def obtener_equipo_por_nombre(nombre):
        if pd.isna(nombre) or nombre is None:
            return "Sin Equipo"
        nombre_lower = str(nombre).lower().strip()
        if nombre_lower in nombre_a_equipo:
            return nombre_a_equipo[nombre_lower]
        for nom, eq in nombre_a_equipo.items():
            if nombre_lower in nom or nom in nombre_lower:
                return eq
        return "Sin Equipo"
    
    # Agregar columna de equipo
    df['equipo'] = df['agente'].apply(obtener_equipo_por_nombre)
    
    # Filtrar vendedores sin equipo
    df = df[df['equipo'] != "Sin Equipo"]
    
    # =========================================================================
    # APLICAR RESTRICCIONES SEGÚN ROL DEL USUARIO
    # =========================================================================
    if permisos['rol'] == 'vendedor':
        # Vendedor: Filtrar solo sus datos
        nombre_vendedor = permisos['nombre_usuario'].lower()
        df = df[df['agente'].apply(lambda x: nombre_vendedor in str(x).lower() if pd.notna(x) else False)]
        equipo_usuario = permisos['equipo'] if permisos['equipo'] else "Sin Equipo"
        st.info(f"👤 Mostrando evaluaciones de: **{permisos['nombre_usuario']}** | Equipo: **{equipo_usuario}**")
        
    elif permisos['rol'] == 'supervisor' and permisos['equipos_permitidos']:
        # Supervisor con equipo: Filtrar solo su equipo
        equipo_supervisor = permisos['equipos_permitidos'][0]
        df = df[df['equipo'] == equipo_supervisor]
        st.info(f"🏢 Mostrando evaluaciones del equipo: **{equipo_supervisor}**")
    
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
    
    # Verificar si hay datos después del filtro
    if len(df) == 0:
        st.warning("⚠️ No hay evaluaciones disponibles para mostrar.")
        return
    
    # =============================================================================
    # TABS PRINCIPALES - Ajustados según rol
    # =============================================================================
    if permisos['rol'] == 'vendedor':
        # Vendedores solo ven sus evaluaciones individuales
        tab1, tab2 = st.tabs(["📊 Mi Rendimiento", "🔍 Detalle de Evaluaciones"])
    else:
        tab1, tab2, tab4 = st.tabs(["📊 Resumen Ejecutivo", "👤 Análisis por Vendedor", "🔍 Detalle de Evaluaciones"])
    
    with tab1:
        # =============================================================================
        # MÉTRICAS PRINCIPALES
        # =============================================================================
        st.markdown('<p class="section-header">📈 Indicadores de Evaluación</p>', unsafe_allow_html=True)
        
        total = len(df)
        puntaje_promedio = df['puntaje_total'].mean()
        
        # Clasificar por rangos de puntaje
        df['rango_puntaje'] = pd.cut(df['puntaje_total'], 
                                      bins=[-1, 20, 40, 60, 80, 100],
                                      labels=['Crítico (0-20)', 'Bajo (21-40)', 'Regular (41-60)', 'Bueno (61-80)', 'Excelente (81-100)'])
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("📊 Total Evaluaciones", f"{total:,}")
        with col2:
            color = "🔴" if puntaje_promedio < 40 else "🟡" if puntaje_promedio < 60 else "🟢"
            st.metric(f"{color} Índice de Calidad", f"{puntaje_promedio:.1f}/100")
        with col3:
            excelentes = (df['rango_puntaje'] == 'Excelente (81-100)').sum()
            st.metric("🌟 Rendimiento Excelente", f"{excelentes:,} ({excelentes/total*100:.1f}%)")
        with col4:
            criticos = len(df[df['puntaje_total'] <= 20])
            st.metric("🔴 Requieren Atención", f"{criticos:,} ({criticos/total*100:.1f}%)")
        with col5:
            cero = len(df[df['puntaje_total'] == 0])
            st.metric("⚠️ Sin Evaluación", f"{cero:,} ({cero/total*100:.1f}%)")
        
        # Gráfico de torta - Distribución por Rango
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            rango_counts = df['rango_puntaje'].value_counts()
            fig = px.pie(
                values=rango_counts.values,
                names=rango_counts.index,
                title="Distribución por Rango de Desempeño",
                color_discrete_sequence=['#E74C3C', '#F39C12', '#F1C40F', '#27AE60', '#2ECC71']
            )
            fig.update_layout(
                height=350, 
                paper_bgcolor='#FFFFFF',
                font=dict(color='#1E293B', size=13),
                title_font=dict(color='#1E3A5F', size=16, family='Arial Black'),
                legend=dict(font=dict(color='#1E293B', size=12))
            )
            fig.update_traces(textinfo="none")
            st.plotly_chart(fig, use_container_width=True)
        
        # Ranking de agentes resumen
        st.markdown("---")
        st.markdown('<p class="section-header">👥 Ranking de Rendimiento por Vendedor</p>', unsafe_allow_html=True)
        
        if 'agente' in df.columns:
            df_agentes_resumen = df.groupby('agente').agg({
                'puntaje_total': ['mean', 'count']
            }).round(1)
            df_agentes_resumen.columns = ['Puntaje_Prom', 'Evaluaciones']
            df_agentes_resumen = df_agentes_resumen.reset_index()
            df_agentes_resumen = df_agentes_resumen[df_agentes_resumen['Evaluaciones'] >= 5]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🏆 Top 10 - Mejor Rendimiento:**")
                top_10 = df_agentes_resumen.nlargest(10, 'Puntaje_Prom')
                fig = px.bar(
                    top_10,
                    x='Puntaje_Prom',
                    y='agente',
                    orientation='h',
                    text='Puntaje_Prom'
                )
                fig.update_traces(marker_color="#27AE60", texttemplate='%{text:.1f}', textposition='outside', textfont=dict(color='#1E293B', size=11))
                fig.update_layout(
                    height=350, 
                    paper_bgcolor='#FFFFFF', 
                    plot_bgcolor='#FAFBFC',
                    showlegend=False,
                    yaxis={'categoryorder': 'total ascending'},
                    font=dict(color='#1E293B', size=11)
                )
                fig.update_xaxes(range=[0, 100], tickfont=dict(color='#1E293B', size=10))
                fig.update_yaxes(tickfont=dict(color='#1E293B', size=10))
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("**⚠️ Requieren Plan de Mejora:**")
                bottom_10 = df_agentes_resumen.nsmallest(10, 'Puntaje_Prom')
                fig = px.bar(
                    bottom_10,
                    x='Puntaje_Prom',
                    y='agente',
                    orientation='h',
                    text='Puntaje_Prom'
                )
                fig.update_traces(marker_color="#E74C3C", texttemplate='%{text:.1f}', textposition='outside', textfont=dict(color='#1E293B', size=11))
                fig.update_layout(
                    height=350, 
                    paper_bgcolor='#FFFFFF', 
                    plot_bgcolor='#FAFBFC',
                    showlegend=False,
                    yaxis={'categoryorder': 'total descending'},
                    font=dict(color='#1E293B', size=11)
                )
                fig.update_xaxes(range=[0, 100], tickfont=dict(color='#1E293B', size=10))
                fig.update_yaxes(tickfont=dict(color='#1E293B', size=10))
                st.plotly_chart(fig, use_container_width=True)
            
            # =============================================================================
            # ANÁLISIS DETALLADO POR CRITERIO (RESERVADO)
            # =============================================================================

            # Calcular promedios por criterio
            promedios = {}
            for c in criterios:
                if c in df.columns:
                    promedios[criterios_nombres.get(c, c)] = pd.to_numeric(df[c], errors="coerce").mean()

            if promedios:
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
                        color_continuous_scale=['#E74C3C', '#F39C12', '#27AE60'],
                        range_color=[0, 100]
                    )
                    fig.update_layout(
                        height=450,
                        paper_bgcolor='#FFFFFF',
                        plot_bgcolor='#FFFFFF',
                        showlegend=False,
                        font=dict(color="#000000"),
                        title=dict(
                            text="Puntaje Promedio por Criterio",
                            font=dict(color="#000000", size=16)
                        )  
                    )
                    fig.update_xaxes(
                        tickfont=dict(color="#000000"),
                        title=dict(font=dict(color="#000000"))
                    )
                    fig.update_yaxes(
                        tickfont=dict(color="#000000"),
                        title=dict(font=dict(color="#000000"))
                    )

                    fig.add_vline(x=50, line_dash="dash", line_color="gray", annotation_text="Meta: 50")
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    st.markdown("**📋 Detalle por Criterio:**")
                    for criterio, puntaje in sorted(promedios.items(), key=lambda x: -x[1]):
                        emoji = "🟢" if puntaje >= 50 else "🟡" if puntaje >= 30 else "🔴"
                        st.markdown(f"{emoji} **{criterio}**: {puntaje:.1f}/100")

            # =============================================================================
            # ÁREAS DE MEJORA (RESERVADO)
            # =============================================================================

            if 'areas_mejora' in df.columns:
                from collections import Counter
                all_areas = []

                for areas in df['areas_mejora'].dropna():
                    if isinstance(areas, str):
                        areas_unicas = set()  # Usar set para evitar duplicados por fila
                        for area in areas.split(','):
                            area = area.strip().strip('"').strip("'").strip('[').strip(']').strip()
                            if area and area not in areas_unicas:
                                areas_unicas.add(area)
                                all_areas.append(area)

                if all_areas:
                    area_counts = Counter(all_areas)
                    top_areas = area_counts.most_common(15)

                    total = sum(area_counts.values())

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
                            color_continuous_scale='Reds',
                            range_color=[0, df_areas['Frecuencia'].max()]
                        )
                        fig.update_layout(
                            height=450,
                            paper_bgcolor='#FFFFFF',
                            plot_bgcolor='#FFFFFF',
                            yaxis={'categoryorder': 'total ascending'},
                            title=dict(
                              text="Top 15 Áreas de Mejora Identificadas",
                                font=dict(color="#000000", size=16)
                            )
                        )
                        
                        fig.update_xaxes(
                            tickfont=dict(color="#000000"),
                            title=dict(font=dict(color="#000000"))
                        )

                        fig.update_yaxes(
                            tickfont=dict(color="#000000"),
                            title=dict(font=dict(color="#000000"))
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        st.markdown("**🎯 Prioridades de Capacitación:**")
                        for i, (area, freq) in enumerate(top_areas[:10], 1):
                            pct = freq / total * 100
                            st.markdown(f"{i}. **{area}**: {freq:,} ({pct:.1f}%)")
    
    # El tab2 solo existe para admin y supervisor (vendedores tienen tabs diferentes)
    if permisos['rol'] != 'vendedor':
        with tab2:
            # =============================================================================
            # ANÁLISIS DETALLADO POR AGENTE
            # =============================================================================
            st.markdown('<p class="section-header">👤 Análisis Individual de Rendimiento</p>', unsafe_allow_html=True)
            
            if 'agente' in df.columns:
                agentes_list = sorted(df['agente'].dropna().unique().tolist())
                agente_seleccionado = st.selectbox("Seleccionar vendedor:", agentes_list, key='agente_gemini')
                
                # Filtrar datos del agente
                df_agente = df[df['agente'] == agente_seleccionado].copy()
                total_agente = len(df_agente)
                
                if total_agente > 0:
                    puntaje_agente = df_agente['puntaje_total'].mean()
                    
                    # Métricas del agente
                    st.markdown("---")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("📊 Operaciones Evaluadas", f"{total_agente:,}")
                    with col2:
                        diff_vs_prom = puntaje_agente - puntaje_promedio
                        st.metric("🎯 Índice de Rendimiento", f"{puntaje_agente:.1f}/100", 
                                  delta=f"{diff_vs_prom:+.1f} vs general")
                    with col3:
                        excelentes_ag = len(df_agente[df_agente['puntaje_total'] >= 80])
                        st.metric("🌟 Gestiones Destacadas", f"{excelentes_ag} ({excelentes_ag/total_agente*100:.1f}%)")
                    with col4:
                        criticos_ag = len(df_agente[df_agente['puntaje_total'] <= 20])
                        st.metric("🔴 Gestiones Críticas", f"{criticos_ag} ({criticos_ag/total_agente*100:.1f}%)")
                    
                    # Gráfico de Perfil de Competencias - Barras comparativas profesional
                    st.markdown("---")
                    st.markdown("### 📊 Perfil de Competencias por Criterio")
                    
                    # ========== SELECTORES DE COMPARACIÓN (SOLO ADMIN) ==========
                    if permisos['puede_comparar']:
                        st.markdown("""
                        <div style='background: linear-gradient(90deg, #EFF6FF 0%, #DBEAFE 100%); 
                                    padding: 15px 20px; border-radius: 10px; margin-bottom: 20px;
                                    border: 1px solid #BFDBFE;'>
                            <span style='color:#1E40AF; font-weight:600; font-size:15px;'>⚙️ Configurar Comparativa</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col_config1, col_config2 = st.columns(2)
                        
                        with col_config1:
                            tipo_comparacion = st.selectbox(
                                "🔄 Comparar contra:",
                                ["Promedio General (Todos)", "Un Equipo Específico", "Otro Vendedor"],
                                key="tipo_comp_gemini"
                            )
                        
                        # Variables para la comparación
                        nombre_comparacion = "Promedio General"
                        valores_comparacion = []
                        # Siempre rojo para la comparación
                        color_comparacion = "#DC2626"
                        
                        with col_config2:
                            if tipo_comparacion == "Un Equipo Específico":
                                # Obtener lista de equipos únicos
                                equipos_disponibles = [eq for eq in equipos_vendedores.keys() if eq and eq != "Sin Equipo"]
                                
                                if equipos_disponibles:
                                    equipo_seleccionado = st.selectbox(
                                        "📋 Seleccionar equipo:",
                                        sorted(equipos_disponibles),
                                        key="equipo_comp_gemini"
                                    )
                                    nombre_comparacion = equipo_seleccionado
                                else:
                                    st.info("No hay equipos disponibles en el archivo LISTADO-DE-VENDEDORES.csv")
                                    equipo_seleccionado = None
                            
                            elif tipo_comparacion == "Otro Vendedor":
                                otros_agentes = [a for a in sorted(df['agente'].dropna().unique().tolist()) if a != agente_seleccionado]
                                if otros_agentes:
                                    agente_comparar = st.selectbox(
                                        "👤 Seleccionar vendedor:",
                                        otros_agentes,
                                        key="agente_comp_gemini"
                                    )
                                    nombre_comparacion = agente_comparar
                                else:
                                    st.info("No hay otros vendedores disponibles")
                                    agente_comparar = None
                    else:
                        # Supervisor: Solo comparar dentro de su equipo
                        st.markdown("""
                        <div style='background: linear-gradient(90deg, #FEF3C7 0%, #FDE68A 100%); 
                                    padding: 15px 20px; border-radius: 10px; margin-bottom: 20px;
                                    border: 1px solid #FCD34D;'>
                            <span style='color:#92400E; font-weight:600; font-size:15px;'>📊 Comparación con promedio del equipo</span>
                        </div>
                        """, unsafe_allow_html=True)
                        tipo_comparacion = "Promedio del Equipo"
                        nombre_comparacion = f"Promedio {permisos['equipos_permitidos'][0] if permisos['equipos_permitidos'] else 'Equipo'}"
                        valores_comparacion = []
                        color_comparacion = "#DC2626"
                
                    # Calcular valores del agente seleccionado
                    criterios_agente = {}
                    for c in criterios:
                        if c in df_agente.columns:
                            criterios_agente[criterios_nombres.get(c, c)] = df_agente[c].mean()
                    
                    if criterios_agente:
                        categories = list(criterios_agente.keys())
                        values_agente = list(criterios_agente.values())
                        
                        # Calcular valores de comparación según la selección
                        if tipo_comparacion == "Promedio General (Todos)":
                            valores_comparacion = [df[c].mean() if c in df.columns else 0 for c in criterios]
                        elif tipo_comparacion == "Un Equipo Específico" and 'equipo_seleccionado' in dir() and equipo_seleccionado:
                            # Filtrar por equipo
                            agentes_equipo = equipos_vendedores.get(equipo_seleccionado, [])
                            if agentes_equipo:
                                df_equipo = df[df['agente'].isin(agentes_equipo)]
                                valores_comparacion = [df_equipo[c].mean() if c in df_equipo.columns and len(df_equipo) > 0 else 0 for c in criterios]
                            else:
                                valores_comparacion = [df[c].mean() if c in df.columns else 0 for c in criterios]
                        elif tipo_comparacion == "Otro Vendedor" and 'agente_comparar' in dir() and agente_comparar:
                            df_otro = df[df['agente'] == agente_comparar]
                            valores_comparacion = [df_otro[c].mean() if c in df_otro.columns and len(df_otro) > 0 else 0 for c in criterios]
                        elif tipo_comparacion == "Promedio del Equipo":
                            # Supervisor: Comparar con promedio de su propio equipo (ya filtrado en df)
                            valores_comparacion = [df[c].mean() if c in df.columns else 0 for c in criterios]
                        else:
                            valores_comparacion = [df[c].mean() if c in df.columns else 0 for c in criterios]
                    
                    # Crear DataFrame para el gráfico
                    df_comparativo = pd.DataFrame({
                        'Criterio': categories,
                        'Vendedor': values_agente,
                        'Comparacion': valores_comparacion
                    })
                    
                    # Ordenar por diferencia para destacar fortalezas/debilidades
                    df_comparativo['Diferencia'] = df_comparativo['Vendedor'] - df_comparativo['Comparacion']
                    df_comparativo = df_comparativo.sort_values('Vendedor', ascending=True)
                    
                    # Subtítulo dinámico - Siempre azul para seleccionado, rojo para comparación
                    st.markdown(f"""
                    <p style='color:#475569; font-size:16px; margin-bottom:10px;'>
                        <strong style='color:#3B82F6; font-size:18px;'>🔵 {agente_seleccionado}</strong> 
                        &nbsp;&nbsp;vs&nbsp;&nbsp;
                        <strong style='color:#DC2626; font-size:18px;'>🔴 {nombre_comparacion}</strong>
                    </p>
                    """, unsafe_allow_html=True)
                    
                    fig = go.Figure()
                    
                    # Barras de Comparación (siempre ROJAS)
                    fig.add_trace(go.Bar(
                        y=df_comparativo['Criterio'],
                        x=df_comparativo['Comparacion'],
                        name=nombre_comparacion,
                        orientation='h',
                        marker=dict(
                            color='#DC2626',
                            line=dict(color='#991B1B', width=1.5)
                        ),
                        text=[f"{v:.1f}" for v in df_comparativo['Comparacion']],
                        textposition='inside',
                        textfont=dict(color='white', size=14, family='Arial Black'),
                        hovertemplate='<b>%{y}</b><br>' + nombre_comparacion + ': %{x:.1f}<extra></extra>'
                    ))
                    
                    # Barras del Vendedor (azules, adelante)
                    fig.add_trace(go.Bar(
                        y=df_comparativo['Criterio'],
                        x=df_comparativo['Vendedor'],
                        name=agente_seleccionado,
                        orientation='h',
                        marker=dict(
                            color='#3B82F6',
                            line=dict(color='#1E40AF', width=1.5)
                        ),
                        text=[f"{v:.1f}" for v in df_comparativo['Vendedor']],
                        textposition='inside',
                        textfont=dict(color='white', size=14, family='Arial Black'),
                        hovertemplate='<b>%{y}</b><br>' + agente_seleccionado + ': %{x:.1f}<extra></extra>'
                    ))
                    
                    # Línea de meta (80 = excelente)
                    fig.add_vline(
                        x=80, 
                        line_dash="dot", 
                        line_color="#10B981",
                        line_width=3,
                        annotation_text="Meta: 80",
                        annotation_position="top",
                        annotation_font=dict(size=14, color="#10B981", family="Arial Black")
                    )
                    
                    # Línea de promedio
                    fig.add_vline(
                        x=50, 
                        line_dash="dash", 
                        line_color="#94A3B8",
                        line_width=1,
                        annotation_text="50",
                        annotation_position="bottom",
                        annotation_font=dict(size=10, color="#94A3B8")
                    )
                    
                    fig.update_layout(
                        barmode='group',
                        height=700,  # Mucho más grande
                        paper_bgcolor='#FFFFFF',
                        plot_bgcolor='#FAFBFC',
                        font=dict(family="Arial, sans-serif", size=14, color='#1E293B'),
                        xaxis=dict(
                            title=dict(text="Puntaje (0-100)", font=dict(size=16, color='#1E293B', family='Arial Black')),
                            gridcolor='#E2E8F0',
                            tickfont=dict(size=14, color='#475569'),
                            range=[0, 105],
                            dtick=10,
                            showgrid=True,
                            gridwidth=1
                        ),
                        yaxis=dict(
                            title=dict(text="", font=dict(size=14)),
                            tickfont=dict(size=15, color='#1E293B', family='Arial'),
                            showgrid=False
                        ),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="center",
                            x=0.5,
                            font=dict(size=15),
                            bgcolor='rgba(255,255,255,0.9)',
                            bordercolor='#E2E8F0',
                            borderwidth=1
                        ),
                        margin=dict(t=80, b=60, l=150, r=50),
                        bargap=0.3,
                        bargroupgap=0.15
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Resumen de fortalezas y áreas de mejora
                    col_f, col_m = st.columns(2)
                    
                    with col_f:
                        fortalezas = df_comparativo[df_comparativo['Diferencia'] > 5].sort_values('Diferencia', ascending=False)
                        if len(fortalezas) > 0:
                            st.markdown(f"#### 💪 Fortalezas vs {nombre_comparacion}")
                            for _, row in fortalezas.iterrows():
                                st.markdown(f"""
                                <div style='background:#D1FAE5; padding:10px 15px; border-radius:8px; margin:6px 0; border-left:5px solid #10B981;'>
                                    <strong style='color:#065F46; font-size:15px;'>{row['Criterio']}</strong>
                                    <span style='float:right; color:#059669; font-size:16px; font-weight:bold;'>+{row['Diferencia']:.1f} pts</span>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info(f"Sin fortalezas destacadas vs {nombre_comparacion}")
                    
                    with col_m:
                        mejoras = df_comparativo[df_comparativo['Diferencia'] < -5].sort_values('Diferencia', ascending=True)
                        if len(mejoras) > 0:
                            st.markdown(f"#### 🎯 Áreas de Mejora vs {nombre_comparacion}")
                            for _, row in mejoras.iterrows():
                                st.markdown(f"""
                                <div style='background:#FEE2E2; padding:10px 15px; border-radius:8px; margin:6px 0; border-left:5px solid #DC2626;'>
                                    <strong style='color:#7F1D1D; font-size:15px;'>{row['Criterio']}</strong>
                                    <span style='float:right; color:#DC2626; font-size:16px; font-weight:bold;'>{row['Diferencia']:.1f} pts</span>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.success(f"¡Sin áreas críticas vs {nombre_comparacion}!")
                
                # Tabla de evaluaciones del agente
                st.markdown("---")
                st.markdown("**📋 Últimas Evaluaciones del Agente:**")
                
                # Preparar datos para la tabla mejorada
                df_mostrar = df_agente.copy()
                
                # Extraer ID de referencia del archivo (sin transcripcion.json)
                if 'archivo' in df_mostrar.columns:
                    df_mostrar['Referencia'] = df_mostrar['archivo'].apply(
                        lambda x: x.replace('transcripcion.json', '').replace('_transcripcion.json', '').rstrip('_').rstrip('/').split('/')[-1] if isinstance(x, str) else x
                    )
                
                # Crear columna de zona según puntaje
                if 'puntaje_total' in df_mostrar.columns:
                    def clasificar_zona(p):
                        if p >= 80:
                            return "🟢 Excelente"
                        elif p >= 60:
                            return "🔵 Bueno"
                        elif p >= 30:
                            return "🟡 En Desarrollo"
                        else:
                            return "🔴 Crítico"
                    df_mostrar['Zona'] = df_mostrar['puntaje_total'].apply(clasificar_zona)
                
                # Seleccionar y renombrar columnas para mostrar
                columnas_mostrar = []
                renombres = {}
                
                if 'Referencia' in df_mostrar.columns:
                    columnas_mostrar.append('Referencia')
                    renombres['Referencia'] = '📁 ID Llamada'
                
                if 'puntaje_total' in df_mostrar.columns:
                    columnas_mostrar.append('puntaje_total')
                    renombres['puntaje_total'] = '⭐ Puntaje'
                
                if 'Zona' in df_mostrar.columns:
                    columnas_mostrar.append('Zona')
                    renombres['Zona'] = '📊 Zona'
                
                if 'resumen' in df_mostrar.columns:
                    # Mantener resumen completo - Streamlit permite expandir al hacer doble click
                    columnas_mostrar.append('resumen')
                    renombres['resumen'] = '📝 Resumen (doble click para expandir)'
                
                if columnas_mostrar:
                    df_tabla = df_mostrar[columnas_mostrar].rename(columns=renombres)
                    df_tabla = df_tabla.sort_values('⭐ Puntaje', ascending=False) if '⭐ Puntaje' in df_tabla.columns else df_tabla
                    
                    # Mostrar tabla con estilo
                    st.dataframe(
                        df_tabla.head(20), 
                        use_container_width=True, 
                        hide_index=True, 
                        height=400,
                        column_config={
                            '📁 ID Llamada': st.column_config.TextColumn(width='medium'),
                            '⭐ Puntaje': st.column_config.NumberColumn(format="%.0f /100", width='small'),
                            '📊 Zona': st.column_config.TextColumn(width='small'),
                            '📝 Resumen (doble click para expandir)': st.column_config.TextColumn(width='large'),
                        }
                    )
                    
                    st.caption("💡 **Tip:** Hacé doble click en cualquier celda de resumen para ver el texto completo")
                
                # Áreas de mejora específicas del agente
                if 'areas_mejora' in df_agente.columns:
                    st.markdown("---")
                    st.markdown("**🎯 Áreas de Mejora Recurrentes de Este Agente:**")
                    
                    from collections import Counter
                    areas_agente = []
                    for areas in df_agente['areas_mejora'].dropna():
                        if isinstance(areas, str):
                            areas_unicas = set()  # Deduplicar por fila
                            for area in areas.split(','):
                                area = area.strip().strip('"').strip("'").strip('[').strip(']').strip()
                                if area and area not in areas_unicas:
                                    areas_unicas.add(area)
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
                                orientation='h'
                            )
                            fig.update_traces(marker_color="#F39C12")
                            fig.update_layout(height=350, paper_bgcolor='#FFFFFF', 
                                              yaxis={'categoryorder': 'total ascending'})
                            
                            fig.update_xaxes(
                                tickfont=dict(color="#000000"),
                                title=dict(font=dict(color="#000000"))
                            )

                            fig.update_yaxes(
                                tickfont=dict(color="#000000"),
                                title=dict(font=dict(color="#000000"))
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)

                        with col2:
                            st.markdown("**📝 Plan de Capacitación Sugerido:**")
                            for i, (area, freq) in enumerate(top_areas_agente[:5], 1):
                                st.markdown(f"{i}. **{area}** ({freq} veces)")
    
    # Tab3 y Tab4 solo existen para admin y supervisor
    if permisos['rol'] != 'vendedor':   
        with tab4:
            # =============================================================================
            # EXPLORADOR DE EVALUACIONES (Admin/Supervisor)
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
                # Aumentar límite de archivos mostrados en el selector
                max_archivos = min(200, len(df_filtrado))
                archivos_lista = df_filtrado['archivo'].tolist()[:max_archivos]
                
                st.info(f"ℹ️ Mostrando {max_archivos} de {len(df_filtrado)} evaluaciones en el selector. Usa los filtros para reducir la lista.")
                
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
                            st.markdown(f"{criterios_nombres.get(c, c)}: **{valor}**")
    
    else:
        # ===========================================================================
        # TABS PARA VENDEDOR - Vista simplificada
        # ===========================================================================
        with tab2:
            # Explorador de evaluaciones simplificado para vendedor
            st.markdown('<p class="section-header">🔍 Detalle de Mis Evaluaciones</p>', unsafe_allow_html=True)
            
            # Asegurar que rango_puntaje existe
            if 'rango_puntaje' not in df.columns:
                df['rango_puntaje'] = pd.cut(df['puntaje_total'], 
                                              bins=[-1, 20, 40, 60, 80, 100],
                                              labels=['Crítico (0-20)', 'Bajo (21-40)', 'Regular (41-60)', 'Bueno (61-80)', 'Excelente (81-100)'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                rangos_lista = ['Todos'] + [r for r in df['rango_puntaje'].dropna().unique().tolist() if pd.notna(r)]
                filtro_rango = st.selectbox("Filtrar por rango:", rangos_lista, key='filtro_rango_vendedor')
            with col2:
                orden = st.selectbox("Ordenar por:", ['Puntaje (menor a mayor)', 'Puntaje (mayor a menor)'], key='orden_vendedor')
            
            df_filtrado = df.copy()
            if filtro_rango != 'Todos':
                df_filtrado = df_filtrado[df_filtrado['rango_puntaje'] == filtro_rango]
            
            ascending = 'menor' in orden
            df_filtrado = df_filtrado.sort_values('puntaje_total', ascending=ascending)
            
            st.markdown(f"**Mostrando las primeras 100 de {len(df_filtrado):,} evaluaciones:**")
            columnas_mostrar = ['archivo', 'puntaje_total', 'saludo_presentacion', 
                               'cierre', 'oferta_productos', 'resumen']
            columnas_disponibles = [c for c in columnas_mostrar if c in df_filtrado.columns]
            
            st.dataframe(
                df_filtrado[columnas_disponibles].head(100),
                use_container_width=True,
                hide_index=True,
                height=400
            )
            
            # Detalle de una evaluación
            if len(df_filtrado) > 0:
                st.markdown("---")
                st.markdown("**📄 Ver Detalle de Evaluación:**")
                
                # Aumentar límite de archivos mostrados en el selector
                max_archivos = min(200, len(df_filtrado))
                archivos_lista = df_filtrado['archivo'].tolist()[:max_archivos]
                
                st.info(f"ℹ️ Mostrando {max_archivos} de {len(df_filtrado)} evaluaciones en el selector. Usa los filtros para reducir la lista.")
                
                archivo_sel = st.selectbox("Selecciona un archivo:", archivos_lista, key='archivo_detalle_vendedor')
                
                eval_sel = df_filtrado[df_filtrado['archivo'] == archivo_sel].iloc[0]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Archivo:** {eval_sel['archivo']}")
                    st.markdown(f"**Puntaje Total:** {eval_sel['puntaje_total']}/100")
                    st.markdown(f"**Resumen:** {eval_sel.get('resumen', 'N/A')}")
                
                with col2:
                    st.markdown("**Puntajes por Criterio:**")
                    for c in criterios:
                        if c in eval_sel.index:
                            valor = eval_sel[c]
                            emoji = "🟢" if valor >= 50 else "🟡" if valor >= 30 else "🔴"
                            st.markdown(f"{criterios_nombres.get(c, c)}: **{valor}**")


# =============================================================================
# SECCIÓN DE CALIDAD - ANÁLISIS DE LLAMADAS CALL CENTER
# =============================================================================

def to_seconds_calidad(dur_str):
    """Convierte hh:mm:ss a segundos para módulo de calidad"""
    try:
        if pd.isna(dur_str) or dur_str == '':
            return 0
        parts = str(dur_str).split(':')
        if len(parts) == 3:
            h, m, s = map(int, parts)
            return h * 3600 + m * 60 + s
        elif len(parts) == 2:
            m, s = map(int, parts)
            return m * 60 + s
        else:
            return int(float(dur_str))
    except:
        return 0

def sec_to_mmss(s):
    """Convierte segundos a mm:ss"""
    if pd.isna(s) or s == 0:
        return "00:00"
    m = int(s // 60)
    s = int(s % 60)
    return f"{m:02d}:{s:02d}"

def sec_to_hhmmss(s):
    """Convierte segundos a hh:mm:ss"""
    if pd.isna(s) or s == 0:
        return "00:00:00"
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = int(s % 60)
    return f"{h:02d}:{m:02d}:{sec:02d}"

def determinar_turno(hora_inicio):
    """Determina el turno basado en la hora de inicio"""
    try:
        if pd.isna(hora_inicio):
            return "Sin Turno"
        if isinstance(hora_inicio, str):
            hora = int(hora_inicio.split(':')[0])
        else:
            hora = hora_inicio.hour
        
        if 6 <= hora < 14:
            return "TM"  # Turno Mañana
        elif 14 <= hora < 22:
            return "TT"  # Turno Tarde
        else:
            return "TN"  # Turno Noche
    except:
        return "Sin Turno"

def aplicar_semaforo_tiempo(valor_segundos, tipo_estado):
    """Aplica semáforo según tipo de estado y valor"""
    if tipo_estado == "NO DISPONIBLE":
        if valor_segundos >= 300:  # >= 5 min
            return "🔴", "#DC2626", "Crítico"
        elif valor_segundos >= 180:  # 3-5 min
            return "🟡", "#F59E0B", "Alerta"
        else:
            return "🟢", "#10B981", "OK"
    
    elif tipo_estado == "BREAK":
        if valor_segundos >= 1500:  # >= 25 min
            return "🔴", "#DC2626", "Excedido"
        elif valor_segundos >= 1380:  # 23-25 min
            return "🟡", "#F59E0B", "Límite"
        else:
            return "🟢", "#10B981", "OK"
    
    elif tipo_estado == "BAÑO":
        if valor_segundos > 600:  # > 10 min
            return "🔴", "#DC2626", "Excedido"
        else:
            return "🟢", "#10B981", "OK"
    
    elif tipo_estado == "TIEMPO_LOGUEO":
        if valor_segundos < 16800:  # < 4:40:00
            return "🔴", "#DC2626", "Bajo"
        elif valor_segundos < 17100:  # 4:40:00 - 4:45:00
            return "🟡", "#F59E0B", "Límite"
        else:
            return "🟢", "#10B981", "OK"
    
    return "⚪", "#6B7280", "N/A"

def aplicar_semaforo_cumplimiento(porcentaje):
    """Aplica semáforo de cumplimiento de ventas"""
    if porcentaje >= 90:
        return "🟢", "#10B981", "Cumplido"
    elif porcentaje >= 60:
        return "🟡", "#F59E0B", "En Proceso"
    else:
        return "🔴", "#DC2626", "Bajo"


# =============================================================================
# PÁGINA DE COMPARATIVA DE PERÍODOS
# =============================================================================
def pagina_comparativa_periodos(datos):
    """Página para comparar métricas entre dos períodos diferentes"""
    st.markdown('<div class="main-header">📅 COMMAND · Comparativa de Períodos</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div style='background: #F1F5F9; padding: 20px; border-radius: 12px; border-left: 5px solid #3B82F6;'>
            <h3 style='margin: 0; color: #1E293B;'>🛠️ En desarrollo</h3>
            <p style='margin: 8px 0 0 0; color: #475569;'>
                Este apartado estara disponible pronto con comparativas avanzadas entre periodos.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    return
    
    # Subtítulo corporativo
    st.markdown("""
    <div style='background: #F8FAFC; padding: 12px 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #8B5CF6;'>
        <p style='margin: 0; color: #334155; font-size: 0.95rem;'>
            <strong>Análisis Comparativo de Rendimiento</strong> · Compare métricas entre diferentes semanas o períodos
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Verificar datos
    if 'evaluaciones_gemini_df' not in datos or datos['evaluaciones_gemini_df'] is None:
        st.warning("⚠️ No hay datos de evaluaciones disponibles para comparar.")
        return
    
    df = datos['evaluaciones_gemini_df'].copy()
    
    # Verificar que existe la columna de fecha
    if 'fecha_llamada' not in df.columns:
        st.error("⚠️ No se encontró la columna de fecha en los datos.")
        st.info("💡 Asegúrese de que los archivos tengan el patrón de fecha en el nombre (ej: 260112 = 12/01/2026)")
        return
    
    # Obtener fechas únicas disponibles
    fechas_disponibles = df['fecha_llamada'].dropna().dt.date.unique()
    fechas_ordenadas = sorted(fechas_disponibles)
    
    if len(fechas_ordenadas) < 2:
        st.warning("⚠️ Se necesitan al menos 2 fechas diferentes para hacer una comparativa.")
        return
    
    # Definir períodos predefinidos
    periodo_semana1 = [d for d in fechas_ordenadas if d >= datetime(2026, 1, 12).date() and d <= datetime(2026, 1, 16).date()]
    periodo_semana2 = [d for d in fechas_ordenadas if d >= datetime(2026, 1, 19).date() and d <= datetime(2026, 1, 24).date()]
    
    st.markdown("### ⚙️ Configurar Comparativa")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%); 
                    padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 2px solid #3B82F6;'>
            <span style='color:#1E40AF; font-weight:bold; font-size:16px;'>🔵 PERÍODO 1</span>
        </div>
        """, unsafe_allow_html=True)
        
        periodo1_tipo = st.selectbox(
            "Seleccionar período:",
            ["Semana 12-16 Enero", "Semana 19-24 Enero", "Personalizado"],
            key="periodo1_tipo"
        )
        
        if periodo1_tipo == "Semana 12-16 Enero":
            fecha_ini_1 = datetime(2026, 1, 12).date()
            fecha_fin_1 = datetime(2026, 1, 16).date()
        elif periodo1_tipo == "Semana 19-24 Enero":
            fecha_ini_1 = datetime(2026, 1, 19).date()
            fecha_fin_1 = datetime(2026, 1, 24).date()
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                fecha_ini_1 = st.date_input("Desde:", value=fechas_ordenadas[0], key="p1_ini")
            with col_b:
                fecha_fin_1 = st.date_input("Hasta:", value=fechas_ordenadas[-1], key="p1_fin")
        
        st.info(f"📅 {fecha_ini_1.strftime('%d/%m/%Y')} - {fecha_fin_1.strftime('%d/%m/%Y')}")
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%); 
                    padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 2px solid #DC2626;'>
            <span style='color:#991B1B; font-weight:bold; font-size:16px;'>🔴 PERÍODO 2</span>
        </div>
        """, unsafe_allow_html=True)
        
        periodo2_tipo = st.selectbox(
            "Seleccionar período:",
            ["Semana 19-24 Enero", "Semana 12-16 Enero", "Personalizado"],
            key="periodo2_tipo"
        )
        
        if periodo2_tipo == "Semana 12-16 Enero":
            fecha_ini_2 = datetime(2026, 1, 12).date()
            fecha_fin_2 = datetime(2026, 1, 16).date()
        elif periodo2_tipo == "Semana 19-24 Enero":
            fecha_ini_2 = datetime(2026, 1, 19).date()
            fecha_fin_2 = datetime(2026, 1, 24).date()
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                fecha_ini_2 = st.date_input("Desde:", value=fechas_ordenadas[0], key="p2_ini")
            with col_b:
                fecha_fin_2 = st.date_input("Hasta:", value=fechas_ordenadas[-1], key="p2_fin")
        
        st.info(f"📅 {fecha_ini_2.strftime('%d/%m/%Y')} - {fecha_fin_2.strftime('%d/%m/%Y')}")
    
    # =============================================================================
    # FILTRO POR EQUIPOS
    # =============================================================================
    st.markdown("### 🏢 Filtrar por Equipos")
    
    # Cargar equipos disponibles
    listado_vendedores, equipos_vendedores = cargar_listado_vendedores()
    
    # Crear mapeo nombre -> equipo
    nombre_a_equipo_comp = {}
    for equipo, vendedores in equipos_vendedores.items():
        for vendedor in vendedores:
            nombre_a_equipo_comp[vendedor.lower().strip()] = equipo
    
    def obtener_equipo_comp(agente):
        """Obtiene el equipo del agente"""
        if pd.isna(agente) or agente is None:
            return "Sin Equipo"
        nombre = obtener_nombre_agente(str(agente)).lower().strip()
        if nombre in nombre_a_equipo_comp:
            return nombre_a_equipo_comp[nombre]
        for nom, eq in nombre_a_equipo_comp.items():
            if nombre in nom or nom in nombre:
                return eq
        return "Sin Equipo"
    
    # Obtener equipos únicos
    equipos_lista = [e for e in equipos_vendedores.keys() if e and e != "nan" and e != "Sin Equipo"]
    equipos_lista = sorted(equipos_lista)
    
    # Selector de equipos (multiselect)
    equipos_seleccionados = st.multiselect(
        "Seleccione los equipos a comparar (vacío = todos):",
        options=equipos_lista,
        default=[],
        key="comparativa_equipos_filter"
    )
    
    # Filtrar datos por períodos
    df['fecha_date'] = df['fecha_llamada'].dt.date
    df_periodo1 = df[(df['fecha_date'] >= fecha_ini_1) & (df['fecha_date'] <= fecha_fin_1)].copy()
    df_periodo2 = df[(df['fecha_date'] >= fecha_ini_2) & (df['fecha_date'] <= fecha_fin_2)].copy()
    
    # Aplicar filtro de equipos si se seleccionaron
    if equipos_seleccionados:
        # Agregar columna de equipo a cada período
        df_periodo1['equipo_calc'] = df_periodo1['agente'].apply(obtener_equipo_comp)
        df_periodo2['equipo_calc'] = df_periodo2['agente'].apply(obtener_equipo_comp)
        
        df_periodo1 = df_periodo1[df_periodo1['equipo_calc'].isin(equipos_seleccionados)]
        df_periodo2 = df_periodo2[df_periodo2['equipo_calc'].isin(equipos_seleccionados)]
        
        st.info(f"🏢 Mostrando datos de {len(equipos_seleccionados)} equipo(s): {', '.join(equipos_seleccionados)}")
    
    # Verificar que hay datos en ambos períodos
    if len(df_periodo1) == 0:
        st.warning(f"⚠️ No hay datos para el Período 1 ({fecha_ini_1} - {fecha_fin_1})")
        return
    if len(df_periodo2) == 0:
        st.warning(f"⚠️ No hay datos para el Período 2 ({fecha_ini_2} - {fecha_fin_2})")
        return
    
    st.markdown("---")
    
    # =============================================================================
    # MÉTRICAS COMPARATIVAS PRINCIPALES
    # =============================================================================
    st.markdown("### 📊 Comparativa de Métricas Principales")
    
    # Calcular métricas para cada período
    def calcular_metricas(df_periodo):
        return {
            'total': len(df_periodo),
            'puntaje_promedio': df_periodo['puntaje_total'].mean() if 'puntaje_total' in df_periodo.columns else 0,
            'excelentes': len(df_periodo[df_periodo['puntaje_total'] >= 80]) if 'puntaje_total' in df_periodo.columns else 0,
            'criticos': len(df_periodo[df_periodo['puntaje_total'] <= 20]) if 'puntaje_total' in df_periodo.columns else 0,
            'agentes_unicos': df_periodo['agente'].nunique() if 'agente' in df_periodo.columns else 0
        }
    
    m1 = calcular_metricas(df_periodo1)
    m2 = calcular_metricas(df_periodo2)
    
    # Mostrar métricas comparativas
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        diff_total = m2['total'] - m1['total']
        st.metric(
            "📊 Total Evaluaciones",
            f"P1: {m1['total']:,} | P2: {m2['total']:,}",
            delta=f"{diff_total:+,} diferencia"
        )
    
    with col2:
        diff_puntaje = m2['puntaje_promedio'] - m1['puntaje_promedio']
        color = "normal" if diff_puntaje >= 0 else "inverse"
        st.metric(
            "⭐ Puntaje Promedio",
            f"P1: {m1['puntaje_promedio']:.1f} | P2: {m2['puntaje_promedio']:.1f}",
            delta=f"{diff_puntaje:+.1f} pts",
            delta_color=color
        )
    
    with col3:
        pct_exc_1 = (m1['excelentes'] / m1['total'] * 100) if m1['total'] > 0 else 0
        pct_exc_2 = (m2['excelentes'] / m2['total'] * 100) if m2['total'] > 0 else 0
        diff_exc = pct_exc_2 - pct_exc_1
        st.metric(
            "🌟 % Excelentes (≥80)",
            f"P1: {pct_exc_1:.1f}% | P2: {pct_exc_2:.1f}%",
            delta=f"{diff_exc:+.1f}%"
        )
    
    with col4:
        pct_crit_1 = (m1['criticos'] / m1['total'] * 100) if m1['total'] > 0 else 0
        pct_crit_2 = (m2['criticos'] / m2['total'] * 100) if m2['total'] > 0 else 0
        diff_crit = pct_crit_2 - pct_crit_1
        # Menos críticos es mejor, así que invertimos el color
        color = "inverse" if diff_crit <= 0 else "normal"
        st.metric(
            "🔴 % Críticos (≤20)",
            f"P1: {pct_crit_1:.1f}% | P2: {pct_crit_2:.1f}%",
            delta=f"{diff_crit:+.1f}%",
            delta_color=color
        )
    
    with col5:
        st.metric(
            "👥 Agentes Evaluados",
            f"P1: {m1['agentes_unicos']} | P2: {m2['agentes_unicos']}",
            delta=f"{m2['agentes_unicos'] - m1['agentes_unicos']:+}"
        )
    
    st.markdown("---")
    
    # =============================================================================
    # GRÁFICOS COMPARATIVOS
    # =============================================================================
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Distribución por Rango",
        "📈 Comparativa por Criterio", 
        "👥 Evolución por Agente",
        "📋 Detalle Completo"
    ])
    with tab1:
        st.markdown("### 📊 Distribución por Rango de Puntaje")
        col1, col2 = st.columns(2)
        
        # Clasificar por rangos
        def clasificar_rango(df_p):
            df_p = df_p.copy()
            df_p['rango'] = pd.cut(
                df_p['puntaje_total'], 
                bins=[-1, 20, 40, 60, 80, 100],
                labels=['Crítico (0-20)', 'Bajo (21-40)', 'Regular (41-60)', 'Bueno (61-80)', 'Excelente (81-100)']
            )
            return df_p['rango'].value_counts()
        
        with col1:
            st.markdown(f"**🔵 Período 1:** {fecha_ini_1.strftime('%d/%m')} - {fecha_fin_1.strftime('%d/%m/%Y')}")
            rango1 = clasificar_rango(df_periodo1)
            fig1 = px.pie(
                values=rango1.values,
                names=rango1.index,
                color_discrete_sequence=['#E74C3C', '#F39C12', '#F1C40F', '#27AE60', '#2ECC71'])
            fig1.update_layout(height=350, paper_bgcolor='#FFFFFF', font=dict(color="#000000"),legend=dict(font=dict(color="#000000")))
            fig1.update_traces(textinfo='percent+label', textfont=dict(size=12))
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            st.markdown(f"**🔴 Período 2:** {fecha_ini_2.strftime('%d/%m')} - {fecha_fin_2.strftime('%d/%m/%Y')}")
            rango2 = clasificar_rango(df_periodo2)
            fig2 = px.pie(
                values=rango2.values,
                names=rango2.index,
                color_discrete_sequence=['#E74C3C', '#F39C12', '#F1C40F', '#27AE60', '#2ECC71'])
            fig2.update_layout(height=350, paper_bgcolor='#FFFFFF', font=dict(color="#000000"),legend=dict(font=dict(color="#000000")))
            fig2.update_traces(textinfo='percent+label', textfont=dict(size=12))
            st.plotly_chart(fig2, use_container_width=True)
    
    with tab2:
        st.markdown("### 📈 Comparativa por Criterio de Evaluación")
        
        # Definir criterios
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
        
        # Calcular promedios por criterio
        valores_p1 = []
        valores_p2 = []
        nombres_criterios = []
        
        for c in criterios:
            if c in df_periodo1.columns and c in df_periodo2.columns:
                nombres_criterios.append(criterios_nombres.get(c, c))
                valores_p1.append(df_periodo1[c].mean())
                valores_p2.append(df_periodo2[c].mean())
        
        # Crear gráfico de barras comparativo
        df_comparativo = pd.DataFrame({
            'Criterio': nombres_criterios,
            f'Período 1 ({fecha_ini_1.strftime("%d/%m")}-{fecha_fin_1.strftime("%d/%m")})': valores_p1,
            f'Período 2 ({fecha_ini_2.strftime("%d/%m")}-{fecha_fin_2.strftime("%d/%m")})': valores_p2
        })
        
        df_melted = df_comparativo.melt(id_vars=['Criterio'], var_name='Período', value_name='Puntaje')
        
        fig = px.bar(
            df_melted,
            x='Criterio',
            y='Puntaje',
            color='Período',
            barmode='group',
            color_discrete_map={
                f'Período 1 ({fecha_ini_1.strftime("%d/%m")}-{fecha_fin_1.strftime("%d/%m")})': '#3B82F6',
                f'Período 2 ({fecha_ini_2.strftime("%d/%m")}-{fecha_fin_2.strftime("%d/%m")})': '#DC2626'
            }
        )
        
        fig.update_layout(
            height=500,
            paper_bgcolor='#FFFFFF',
            plot_bgcolor='#FAFBFC',
            xaxis_tickangle=-45,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                font=dict(color="#000000")
            ),
            font=dict(color="#000000")
        )
        fig.update_xaxes(
            tickfont=dict(color="#000000"),
            title=dict(font=dict(color="#000000"))
        )

        fig.update_yaxes(
            tickfont=dict(color="#000000"),
            title=dict(font=dict(color="#000000"))
        )
        fig.add_hline(y=80, line_dash="dot", line_color="#10B981", annotation_text="Meta: 80", annotation_font_color="#000000")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabla de diferencias
        st.markdown("#### 📋 Diferencias por Criterio")
        df_diff = pd.DataFrame({
            'Criterio': nombres_criterios,
            'Período 1': [f"{v:.1f}" for v in valores_p1],
            'Período 2': [f"{v:.1f}" for v in valores_p2],
            'Diferencia': [f"{v2-v1:+.1f}" for v1, v2 in zip(valores_p1, valores_p2)],
            'Tendencia': ['🔼 Mejoró' if v2 > v1 else '🔽 Bajó' if v2 < v1 else '➡️ Igual' for v1, v2 in zip(valores_p1, valores_p2)]
        })
        st.dataframe(df_diff, use_container_width=True, hide_index=True)
    
    with tab3:
        st.markdown("### 👥 Evolución por Agente")
        
        # Calcular promedios por agente en cada período
        if 'agente' in df_periodo1.columns and 'agente' in df_periodo2.columns:
            prom_agente_p1 = df_periodo1.groupby('agente')['puntaje_total'].agg(['mean', 'count']).reset_index()
            prom_agente_p1.columns = ['agente', 'puntaje_p1', 'n_p1']
            
            prom_agente_p2 = df_periodo2.groupby('agente')['puntaje_total'].agg(['mean', 'count']).reset_index()
            prom_agente_p2.columns = ['agente', 'puntaje_p2', 'n_p2']
            
            # Merge
            df_agentes = prom_agente_p1.merge(prom_agente_p2, on='agente', how='outer').fillna(0)
            df_agentes['diferencia'] = df_agentes['puntaje_p2'] - df_agentes['puntaje_p1']
            df_agentes['tendencia'] = df_agentes['diferencia'].apply(
                lambda x: '🔼 Mejoró' if x > 2 else '🔽 Bajó' if x < -2 else '➡️ Estable'
            )
            
            # Solo agentes con datos en ambos períodos
            df_agentes_ambos = df_agentes[(df_agentes['n_p1'] > 0) & (df_agentes['n_p2'] > 0)]
            
            if len(df_agentes_ambos) > 0:
                # Top mejoras y caídas
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**🔼 Mayor Mejora:**")
                    top_mejoras = df_agentes_ambos.nlargest(10, 'diferencia')
                    fig = px.bar(
                        top_mejoras,
                        x='diferencia',
                        y='agente',
                        orientation='h',
                        color='diferencia',
                        color_continuous_scale='Greens',
                        text=[f"{d:+.1f}" for d in top_mejoras['diferencia']]
                    )
                    fig.update_traces(textposition='outside')
                    fig.update_layout(height=400, showlegend=False, yaxis={'categoryorder': 'total ascending'})
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.markdown("**🔽 Mayor Caída:**")
                    top_caidas = df_agentes_ambos.nsmallest(10, 'diferencia')
                    fig = px.bar(
                        top_caidas,
                        x='diferencia',
                        y='agente',
                        orientation='h',
                        color='diferencia',
                        color_continuous_scale='Reds_r',
                        text=[f"{d:+.1f}" for d in top_caidas['diferencia']]
                    )
                    fig.update_traces(textposition='outside')
                    fig.update_layout(height=400, showlegend=False, yaxis={'categoryorder': 'total descending'})
                    st.plotly_chart(fig, use_container_width=True)
                
                # Tabla completa
                st.markdown("#### 📋 Detalle por Agente")
                df_mostrar = df_agentes_ambos[['agente', 'puntaje_p1', 'n_p1', 'puntaje_p2', 'n_p2', 'diferencia', 'tendencia']].copy()
                df_mostrar.columns = ['Agente', 'Puntaje P1', 'N° Eval P1', 'Puntaje P2', 'N° Eval P2', 'Diferencia', 'Tendencia']
                df_mostrar = df_mostrar.sort_values('Diferencia', ascending=False)
                df_mostrar['Puntaje P1'] = df_mostrar['Puntaje P1'].round(1)
                df_mostrar['Puntaje P2'] = df_mostrar['Puntaje P2'].round(1)
                df_mostrar['Diferencia'] = df_mostrar['Diferencia'].round(1)
                st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
            else:
                st.info("No hay agentes con datos en ambos períodos para comparar.")
    
    with tab4:
        st.markdown("### 📋 Detalle Completo de Evaluaciones")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**🔵 Período 1:** {len(df_periodo1):,} evaluaciones")
            if len(df_periodo1) > 0:
                cols_mostrar = ['archivo', 'agente', 'puntaje_total', 'fecha_llamada']
                cols_disp = [c for c in cols_mostrar if c in df_periodo1.columns]
                st.dataframe(
                    df_periodo1[cols_disp].sort_values('puntaje_total', ascending=False).head(50),
                    use_container_width=True,
                    hide_index=True
                )
        
        with col2:
            st.markdown(f"**🔴 Período 2:** {len(df_periodo2):,} evaluaciones")
            if len(df_periodo2) > 0:
                cols_mostrar = ['archivo', 'agente', 'puntaje_total', 'fecha_llamada']
                cols_disp = [c for c in cols_mostrar if c in df_periodo2.columns]
                st.dataframe(
                    df_periodo2[cols_disp].sort_values('puntaje_total', ascending=False).head(50),
                    use_container_width=True,
                    hide_index=True
                )


def pagina_calidad():
    """Página de Calidad - Análisis de Llamadas Call Center"""
    
    st.markdown('<p class="main-header">📞 COMMAND · Indicadores de Calidad y Cumplimiento</p>', unsafe_allow_html=True)
    st.markdown(
        """
        <div style='background: #F1F5F9; padding: 20px; border-radius: 12px; border-left: 5px solid #0EA5E9;'>
            <h3 style='margin: 0; color: #1E293B;'>🛠️ En desarrollo</h3>
            <p style='margin: 8px 0 0 0; color: #475569;'>
                Este apartado estara disponible pronto con indicadores operativos y KPIs.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    return
    
    # Subtítulo corporativo
    st.markdown("""
    <div style='background: #F8FAFC; padding: 12px 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #06B6D4;'>
        <p style='margin: 0; color: #334155; font-size: 0.95rem;'>
            <strong>Control de Calidad Operativa</strong> · Métricas de tiempo, cumplimiento y KPIs de ventas
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs principales - AGREGADO TAB DE ANÁLISIS CRUZADO
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📤 Carga de Datos", 
        "📊 Métricas por Vendedor", 
        "🚦 Semáforos de Tiempo",
        "💰 KPIs de Cumplimiento",
        "🏆 Análisis Cruzado (IQC)"
    ])
    
    # =========================================================================
    # TAB 1: CARGA DE DATOS
    # =========================================================================
    with tab1:
        st.markdown("### 📤 Carga de Archivos")
        st.markdown("""
        <div style='background: #EFF6FF; padding: 15px; border-radius: 10px; border-left: 4px solid #3B82F6; margin-bottom: 20px;'>
            <strong>📋 Archivos necesarios:</strong><br>
            <ul style='margin: 10px 0;'>
                <li><strong>Acumuladores de Agentes (Mitrol)</strong> - Tiempos y métricas de llamadas</li>
                <li><strong>Solicitudes (Customer)</strong> - Datos de ventas</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📞 Archivo Mitrol (Acumuladores)")
            archivo_mitrol = st.file_uploader(
                "Subir Acumuladores de Agentes (CSV)", 
                type=['csv'], 
                key='calidad_mitrol'
            )
            
            if archivo_mitrol is not None:
                try:
                    df_mitrol = pd.read_csv(archivo_mitrol, encoding='latin-1', sep=';')
                    st.session_state['df_calidad_mitrol'] = df_mitrol
                    st.success(f"✅ Mitrol cargado: {len(df_mitrol):,} registros")
                    with st.expander("👁️ Vista previa Mitrol"):
                        st.dataframe(df_mitrol.head(5), use_container_width=True)
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        with col2:
            st.markdown("#### 💼 Archivo Solicitudes (Ventas)")
            archivo_solicitudes = st.file_uploader(
                "Subir Solicitudes/Customer (CSV)", 
                type=['csv'], 
                key='calidad_solicitudes'
            )
            
            if archivo_solicitudes is not None:
                try:
                    df_solicitudes = pd.read_csv(archivo_solicitudes, encoding='latin-1')
                    st.session_state['df_calidad_solicitudes'] = df_solicitudes
                    st.success(f"✅ Solicitudes cargadas: {len(df_solicitudes):,} registros")
                    with st.expander("👁️ Vista previa Solicitudes"):
                        st.dataframe(df_solicitudes.head(5), use_container_width=True)
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        # Cargar mapeo de vendedores
        st.markdown("---")
        st.markdown("#### 🗂️ Mapeo de Vendedores")
        
        # Intentar cargar el archivo de listado automáticamente
        ruta_listado = os.path.join(os.path.dirname(__file__), 'LISTADO-DE-VENDEDORES.csv')
        if os.path.exists(ruta_listado):
            try:
                df_listado = pd.read_csv(ruta_listado, encoding='latin-1')
                # Limpiar columnas y crear mapeo
                df_listado.columns = ['Usuario', 'Nombre', 'Equipo'] + [f'col_{i}' for i in range(len(df_listado.columns)-3)]
                df_listado = df_listado[['Usuario', 'Nombre', 'Equipo']].dropna(subset=['Usuario'])
                df_listado = df_listado[df_listado['Usuario'] != 'Usuario']  # Quitar header
                # Normalizar Usuario
                df_listado['Usuario_norm'] = df_listado['Usuario'].str.lower().str.strip().str.replace(' ', '').str.replace('\t', '')
                st.session_state['df_mapeo_vendedores'] = df_listado
                st.success(f"✅ Mapeo de vendedores cargado: {len(df_listado)} agentes")
                
                # Mostrar resumen por equipo
                equipos = df_listado['Equipo'].value_counts()
                cols_eq = st.columns(len(equipos))
                for i, (equipo, count) in enumerate(equipos.items()):
                    with cols_eq[i]:
                        st.metric(f"👥 {equipo}", count)
            except Exception as e:
                st.warning(f"⚠️ No se pudo cargar el mapeo automático: {str(e)}")
        else:
            st.info("ℹ️ Coloca el archivo LISTADO-DE-VENDEDORES.csv en la carpeta del proyecto")
        
        # Botón procesar
        st.markdown("---")
        if st.button("🚀 Procesar y Unificar Datos", type="primary", use_container_width=True):
            errores = []
            if 'df_calidad_mitrol' not in st.session_state:
                errores.append("Falta archivo Mitrol")
            if 'df_calidad_solicitudes' not in st.session_state:
                errores.append("Falta archivo Solicitudes")
            
            if errores:
                st.warning(f"⚠️ {', '.join(errores)}")
            else:
                with st.spinner("Procesando datos..."):
                    # Procesar Mitrol
                    df_mitrol = st.session_state['df_calidad_mitrol'].copy()
                    df_mapeo = st.session_state.get('df_mapeo_vendedores', pd.DataFrame())
                    
                    # Normalizar columna Agente de Mitrol
                    if 'Agente' in df_mitrol.columns:
                        df_mitrol['Agente_norm'] = df_mitrol['Agente'].str.lower().str.strip().str.replace(' ', '')
                    
                    # Unir con mapeo
                    if not df_mapeo.empty and 'Agente_norm' in df_mitrol.columns:
                        df_mitrol = df_mitrol.merge(
                            df_mapeo[['Usuario_norm', 'Nombre', 'Equipo']],
                            left_on='Agente_norm',
                            right_on='Usuario_norm',
                            how='left'
                        )
                        df_mitrol['Vendedor'] = df_mitrol['Nombre'].fillna(df_mitrol['Agente'])
                    else:
                        df_mitrol['Vendedor'] = df_mitrol.get('Agente', 'Desconocido')
                        df_mitrol['Equipo'] = 'Sin Equipo'
                    
                    st.session_state['df_calidad_procesado'] = df_mitrol
                    st.success("✅ Datos procesados correctamente")
                    
                    # Resumen
                    st.markdown("### 📊 Resumen de Datos")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📞 Registros Mitrol", f"{len(df_mitrol):,}")
                    with col2:
                        agentes = df_mitrol['Vendedor'].nunique() if 'Vendedor' in df_mitrol.columns else 0
                        st.metric("👥 Agentes", agentes)
                    with col3:
                        solicitudes = len(st.session_state['df_calidad_solicitudes'])
                        st.metric("💼 Solicitudes", f"{solicitudes:,}")
    
    # =========================================================================
    # TAB 2: MÉTRICAS POR AGENTE
    # =========================================================================
    with tab2:
        st.markdown("### 📊 Métricas por Agente")
        
        if 'df_calidad_procesado' not in st.session_state:
            st.info("ℹ️ Primero carga y procesa los datos en la pestaña 'Carga de Datos'")
        else:
            df = st.session_state['df_calidad_procesado']
            
            # Filtros
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                if 'Turno' in df.columns:
                    turnos_disponibles = ['Todos'] + df['Turno'].dropna().unique().tolist()
                    turno_filtro = st.selectbox("🌅 Filtrar por Turno", turnos_disponibles)
                else:
                    turno_filtro = 'Todos'
            
            with col_f2:
                if 'Campaña' in df.columns:
                    campanas_disponibles = ['Todas'] + df['Campaña'].dropna().unique().tolist()
                    campana_filtro = st.selectbox("📢 Filtrar por Campaña", campanas_disponibles)
                else:
                    campana_filtro = 'Todas'
            
            with col_f3:
                mostrar_solo_validos = st.checkbox("✅ Solo agentes válidos", value=False)
            
            # Aplicar filtros
            df_filtrado = df.copy()
            if turno_filtro != 'Todos' and 'Turno' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['Turno'] == turno_filtro]
            if campana_filtro != 'Todas' and 'Campaña' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['Campaña'] == campana_filtro]
            if mostrar_solo_validos and 'agente_valido' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['agente_valido'] == True]
            
            if len(df_filtrado) == 0:
                st.warning("⚠️ No hay datos con los filtros seleccionados")
            else:
                # Calcular métricas por agente
                if 'Nombre Agente' in df_filtrado.columns and 'TalkingTime_seg' in df_filtrado.columns:
                    
                    # Tipificaciones especiales a excluir
                    tipif_excluir = ['contestador', 'ya tiene mvs']
                    
                    metricas_agente = []
                    
                    for agente in df_filtrado['Nombre Agente'].unique():
                        df_agente = df_filtrado[df_filtrado['Nombre Agente'] == agente]
                        
                        # Métricas básicas
                        cantidad_llamadas = len(df_agente)
                        
                        # Llamada más larga
                        llamada_mas_larga = df_agente['TalkingTime_seg'].max()
                        
                        # Tiempo promedio hablado
                        tiempo_promedio = df_agente['TalkingTime_seg'].mean()
                        
                        # Llamadas cortadas (por agente, excluyendo tipificaciones especiales)
                        if 'Origen Corte_lower' in df_agente.columns and 'Tipificación_lower' in df_agente.columns:
                            llamadas_cortadas = len(df_agente[
                                (df_agente['Origen Corte_lower'] == 'agente') & 
                                (~df_agente['Tipificación_lower'].isin(tipif_excluir))
                            ])
                        else:
                            llamadas_cortadas = 0
                        
                        # Superan el minuto (> 60 seg)
                        superan_minuto = len(df_agente[df_agente['TalkingTime_seg'] > 60])
                        
                        # Superan 5 minutos (> 300 seg)
                        superan_5min = len(df_agente[df_agente['TalkingTime_seg'] > 300])
                        
                        # Capta la atención
                        capta_atencion = "SI" if tiempo_promedio >= 60 else "NO"
                        
                        # Porcentaje de llamadas cortadas
                        pct_cortadas = (llamadas_cortadas / cantidad_llamadas * 100) if cantidad_llamadas > 0 else 0
                        
                        metricas_agente.append({
                            'Agente': agente,
                            'Cantidad Llamadas': cantidad_llamadas,
                            'Llamada Más Larga': sec_to_mmss(llamada_mas_larga),
                            'Tiempo Prom. Hablado': sec_to_mmss(tiempo_promedio),
                            'Tiempo Prom. (seg)': round(tiempo_promedio, 1),
                            'Llamadas Cortadas': llamadas_cortadas,
                            '% Cortadas': round(pct_cortadas, 1),
                            'Superan 1 Min': superan_minuto,
                            'Superan 5 Min': superan_5min,
                            'Capta Atención': capta_atencion
                        })
                    
                    df_metricas = pd.DataFrame(metricas_agente)
                    df_metricas = df_metricas.sort_values('Cantidad Llamadas', ascending=False)
                    
                    # Métricas globales
                    st.markdown("---")
                    col1, col2, col3, col4, col5 = st.columns(5)
                    
                    with col1:
                        total_llamadas = df_metricas['Cantidad Llamadas'].sum()
                        st.metric("📞 Total Llamadas", f"{total_llamadas:,}")
                    
                    with col2:
                        total_cortadas = df_metricas['Llamadas Cortadas'].sum()
                        pct_cortadas_global = (total_cortadas / total_llamadas * 100) if total_llamadas > 0 else 0
                        st.metric("✂️ Llamadas Cortadas", f"{total_cortadas:,}", f"{pct_cortadas_global:.1f}%")
                    
                    with col3:
                        agentes_captan = len(df_metricas[df_metricas['Capta Atención'] == 'SI'])
                        st.metric("🎯 Captan Atención", f"{agentes_captan}/{len(df_metricas)}")
                    
                    with col4:
                        # Contar tipificaciones especiales
                        if 'Tipificación_lower' in df_filtrado.columns:
                            ya_tiene_mvs = len(df_filtrado[df_filtrado['Tipificación_lower'] == 'ya tiene mvs'])
                            st.metric("📱 Ya Tiene MVS", f"{ya_tiene_mvs:,}")
                    
                    with col5:
                        if 'Tipificación_lower' in df_filtrado.columns:
                            contestador = len(df_filtrado[df_filtrado['Tipificación_lower'] == 'contestador'])
                            st.metric("📞 Contestador", f"{contestador:,}")
                    
                    # Tabla de métricas
                    st.markdown("---")
                    st.markdown("#### 📋 Detalle por Agente")
                    
                    # Estilizar tabla
                    def color_capta_atencion(val):
                        if val == 'SI':
                            return 'background-color: #D1FAE5; color: #065F46; font-weight: bold;'
                        else:
                            return 'background-color: #FEE2E2; color: #991B1B; font-weight: bold;'
                    
                    def color_cortadas(val):
                        if val > 20:
                            return 'background-color: #FEE2E2; color: #991B1B;'
                        elif val > 10:
                            return 'background-color: #FEF3C7; color: #92400E;'
                        else:
                            return 'background-color: #D1FAE5; color: #065F46;'
                    
                    styled_df = df_metricas.style.applymap(
                        color_capta_atencion, subset=['Capta Atención']
                    ).applymap(
                        color_cortadas, subset=['% Cortadas']
                    )
                    
                    st.dataframe(styled_df, use_container_width=True, height=400)
                    
                    # Gráficos
                    st.markdown("---")
                    col_g1, col_g2 = st.columns(2)
                    
                    with col_g1:
                        st.markdown("#### 📊 Top 10 Agentes por Cantidad de Llamadas")
                        top_10 = df_metricas.head(10)
                        fig_bar = go.Figure(data=[
                            go.Bar(
                                x=top_10['Agente'],
                                y=top_10['Cantidad Llamadas'],
                                marker_color='#3B82F6',
                                text=top_10['Cantidad Llamadas'],
                                textposition='outside'
                            )
                        ])
                        fig_bar.update_layout(
                            height=350,
                            paper_bgcolor='#FFFFFF',
                            plot_bgcolor='#FAFBFC',
                            xaxis_tickangle=-45,
                            margin=dict(t=30, b=100)
                        )
                        st.plotly_chart(fig_bar, use_container_width=True)
                    
                    with col_g2:
                        st.markdown("#### ✂️ Agentes con Mayor % de Llamadas Cortadas")
                        top_cortadas = df_metricas.nlargest(10, '% Cortadas')
                        fig_cortadas = go.Figure(data=[
                            go.Bar(
                                x=top_cortadas['Agente'],
                                y=top_cortadas['% Cortadas'],
                                marker_color=['#DC2626' if v > 20 else '#F59E0B' if v > 10 else '#10B981' 
                                             for v in top_cortadas['% Cortadas']],
                                text=[f"{v:.1f}%" for v in top_cortadas['% Cortadas']],
                                textposition='outside'
                            )
                        ])
                        fig_cortadas.update_layout(
                            height=350,
                            paper_bgcolor='#FFFFFF',
                            plot_bgcolor='#FAFBFC',
                            xaxis_tickangle=-45,
                            margin=dict(t=30, b=100),
                            yaxis_title="% Cortadas"
                        )
                        st.plotly_chart(fig_cortadas, use_container_width=True)
                    
                    # Histograma de tiempo promedio
                    st.markdown("#### ⏱️ Distribución de Tiempo Promedio por Agente")
                    fig_hist = go.Figure()
                    fig_hist.add_trace(go.Histogram(
                        x=df_metricas['Tiempo Prom. (seg)'],
                        nbinsx=20,
                        marker_color='#3B82F6',
                        name='Agentes'
                    ))
                    fig_hist.add_vline(x=60, line_dash="dash", line_color="#10B981", 
                                       annotation_text="Meta: 60 seg", annotation_position="top")
                    fig_hist.update_layout(
                        height=300,
                        paper_bgcolor='#FFFFFF',
                        plot_bgcolor='#FAFBFC',
                        xaxis_title="Tiempo Promedio (segundos)",
                        yaxis_title="Cantidad de Agentes"
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)
                    
                    # Botón para descargar
                    st.markdown("---")
                    csv = df_metricas.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Descargar Métricas (CSV)",
                        data=csv,
                        file_name=f"metricas_agentes_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("⚠️ No se encontraron las columnas necesarias (Nombre Agente, TalkingTime)")
    
    # =========================================================================
    # TAB 3: SEMÁFOROS DE TIEMPO
    # =========================================================================
    with tab3:
        st.markdown("### 🚦 Semáforos de Tiempo de Logueo")
        
        st.markdown("""
        <div style='background: #FEF3C7; padding: 15px; border-radius: 10px; border-left: 4px solid #F59E0B; margin-bottom: 20px;'>
            <strong>⚠️ Configuración de Umbrales:</strong><br>
            Esta sección permite configurar y visualizar los semáforos de tiempo según las reglas de negocio.
        </div>
        """, unsafe_allow_html=True)
        
        # Tabla de referencia de umbrales
        st.markdown("#### 📋 Tabla de Umbrales")
        
        umbrales_data = {
            'Estado': ['NO DISPONIBLE', 'BREAK', 'BAÑO', 'TIEMPO DE LOGUEO', 'ADMINISTRATIVO'],
            '🔴 Rojo (Crítico)': ['≥ 05:00 min', '≥ 25:00 min', '> 10:00 min', '< 04:40:00 hrs', '≥ (cant×10)+6 min'],
            '🟡 Amarillo (Alerta)': ['03:00 a 05:00 min', '23:00 a 24:59 min', '-', '04:40:00 a 04:45:00 hrs', '(cant×10) a (cant×10)+5 min'],
            '🟢 Verde (OK)': ['< 03:00 min', '< 23:00 min', '≤ 10:00 min', '≥ 04:45:00 hrs', '< (cant×10) min']
        }
        
        df_umbrales = pd.DataFrame(umbrales_data)
        st.table(df_umbrales)
        
        # Simulador de semáforo
        st.markdown("---")
        st.markdown("#### 🧪 Simulador de Semáforo")
        
        col1, col2 = st.columns(2)
        
        with col1:
            tipo_estado = st.selectbox(
                "Tipo de Estado:",
                ['NO DISPONIBLE', 'BREAK', 'BAÑO', 'TIEMPO_LOGUEO']
            )
        
        with col2:
            if tipo_estado == 'TIEMPO_LOGUEO':
                tiempo_input = st.text_input("Tiempo (hh:mm:ss):", value="04:45:00")
                tiempo_seg = to_seconds_calidad(tiempo_input)
            else:
                tiempo_input = st.text_input("Tiempo (mm:ss):", value="03:00")
                # Convertir mm:ss a segundos
                try:
                    parts = tiempo_input.split(':')
                    if len(parts) == 2:
                        tiempo_seg = int(parts[0]) * 60 + int(parts[1])
                    else:
                        tiempo_seg = 0
                except:
                    tiempo_seg = 0
        
        emoji, color, estado = aplicar_semaforo_tiempo(tiempo_seg, tipo_estado)
        
        st.markdown(f"""
        <div style='text-align: center; padding: 30px; background: {color}20; border-radius: 15px; border: 3px solid {color}; margin-top: 20px;'>
            <span style='font-size: 60px;'>{emoji}</span><br>
            <span style='font-size: 24px; font-weight: bold; color: {color};'>{estado}</span><br>
            <small style='color: #475569;'>Tiempo ingresado: {tiempo_input}</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Si hay datos cargados, mostrar análisis
        if 'df_calidad_procesado' in st.session_state:
            st.markdown("---")
            st.markdown("#### 📊 Análisis de Tiempos del Dataset")
            
            df = st.session_state['df_calidad_procesado']
            
            if 'TalkingTime_seg' in df.columns and 'Nombre Agente' in df.columns:
                # Calcular tiempo total por agente
                tiempo_por_agente = df.groupby('Nombre Agente')['TalkingTime_seg'].sum().reset_index()
                tiempo_por_agente.columns = ['Agente', 'Tiempo Total (seg)']
                tiempo_por_agente['Tiempo Total'] = tiempo_por_agente['Tiempo Total (seg)'].apply(sec_to_hhmmss)
                
                # Aplicar semáforo de logueo
                tiempo_por_agente['Semáforo'] = tiempo_por_agente['Tiempo Total (seg)'].apply(
                    lambda x: aplicar_semaforo_tiempo(x, 'TIEMPO_LOGUEO')
                )
                tiempo_por_agente['Estado'] = tiempo_por_agente['Semáforo'].apply(lambda x: x[0] + ' ' + x[2])
                
                # Contar por semáforo
                col1, col2, col3 = st.columns(3)
                
                verdes = len([x for x in tiempo_por_agente['Semáforo'] if x[0] == '🟢'])
                amarillos = len([x for x in tiempo_por_agente['Semáforo'] if x[0] == '🟡'])
                rojos = len([x for x in tiempo_por_agente['Semáforo'] if x[0] == '🔴'])
                
                with col1:
                    st.markdown(f"""
                    <div style='text-align:center; padding:20px; background:#D1FAE5; border-radius:10px;'>
                        <span style='font-size:40px;'>🟢</span><br>
                        <span style='font-size:28px; font-weight:bold; color:#065F46;'>{verdes}</span><br>
                        <small style='color:#065F46;'>Tiempo OK</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div style='text-align:center; padding:20px; background:#FEF3C7; border-radius:10px;'>
                        <span style='font-size:40px;'>🟡</span><br>
                        <span style='font-size:28px; font-weight:bold; color:#92400E;'>{amarillos}</span><br>
                        <small style='color:#92400E;'>En Límite</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div style='text-align:center; padding:20px; background:#FEE2E2; border-radius:10px;'>
                        <span style='font-size:40px;'>🔴</span><br>
                        <span style='font-size:28px; font-weight:bold; color:#991B1B;'>{rojos}</span><br>
                        <small style='color:#991B1B;'>Bajo Tiempo</small>
                    </div>
                    """, unsafe_allow_html=True)
    
    # =========================================================================
    # TAB 4: KPIs DE VENTAS
    # =========================================================================
    with tab4:
        st.markdown("### 💰 KPIs de Ventas (Customer)")
        
        if 'df_calidad_ventas' not in st.session_state:
            st.info("ℹ️ Carga el archivo de ventas (Customer) en la pestaña 'Carga de Datos' para ver los KPIs")
            
            # Mostrar estructura esperada
            st.markdown("""
            <div style='background: #EFF6FF; padding: 15px; border-radius: 10px; border-left: 4px solid #3B82F6; margin-top: 20px;'>
                <strong>📋 Estructura esperada del archivo Customer:</strong><br>
                <ul style='margin: 10px 0;'>
                    <li><strong>Vendedor</strong> - Nombre del vendedor</li>
                    <li><strong>Estado</strong> - Estado de la venta (PORTA APROBADA, FIBRA APROBADA, etc.)</li>
                    <li><strong>Producto</strong> - Tipo de producto vendido</li>
                    <li><strong>Producto Anterior</strong> - PREPAGO, POSPAGO o vacío</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            # Estados de venta aprobada
            st.markdown("---")
            st.markdown("#### ✅ Estados de Venta Aprobada")
            estados_aprobados = ['PORTA APROBADA', 'FIBRA APROBADA', 'CORPO APROBADO', 'FIBRA CUIT APROBADA']
            for estado in estados_aprobados:
                st.markdown(f"- {estado}")
            
            # Objetivos
            st.markdown("---")
            st.markdown("#### 🎯 Objetivos Mensuales")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                **Vendedor Estándar:**
                - 60 ventas cargadas
                - 50 ventas aprobadas
                """)
            with col2:
                st.markdown("""
                **Nuevo Ingreso:**
                - 1er mes: 10 ventas/semana (2/día)
                - 2do mes: 15 ventas/semana (3/día)
                - Objetivo mes: 45 ventas
                """)
        else:
            df_ventas = st.session_state['df_calidad_ventas'].copy()
            
            # Detectar columnas
            col_vendedor = next((c for c in df_ventas.columns if 'vendedor' in c.lower()), None)
            col_estado = next((c for c in df_ventas.columns if 'estado' in c.lower()), None)
            col_producto = next((c for c in df_ventas.columns if 'producto' in c.lower() and 'anterior' not in c.lower()), None)
            col_prod_anterior = next((c for c in df_ventas.columns if 'producto' in c.lower() and 'anterior' in c.lower()), None)
            
            if col_vendedor and col_estado:
                # Renombrar columnas
                df_ventas = df_ventas.rename(columns={
                    col_vendedor: 'Vendedor',
                    col_estado: 'Estado'
                })
                if col_producto:
                    df_ventas = df_ventas.rename(columns={col_producto: 'Producto'})
                if col_prod_anterior:
                    df_ventas = df_ventas.rename(columns={col_prod_anterior: 'Producto Anterior'})
                
                # Estados aprobados
                estados_aprobados = ['PORTA APROBADA', 'FIBRA APROBADA', 'CORPO APROBADO', 'FIBRA CUIT APROBADA']
                df_ventas['Estado_upper'] = df_ventas['Estado'].astype(str).str.upper().str.strip()
                df_ventas['Aprobada'] = df_ventas['Estado_upper'].isin(estados_aprobados)
                
                # Configuración de objetivos
                st.markdown("#### ⚙️ Configuración de Objetivos")
                col1, col2 = st.columns(2)
                with col1:
                    objetivo_cargadas = st.number_input("Objetivo Ventas Cargadas", value=60, min_value=1)
                with col2:
                    objetivo_aprobadas = st.number_input("Objetivo Ventas Aprobadas", value=50, min_value=1)
                
                # Calcular KPIs por vendedor
                kpis_vendedor = []
                
                for vendedor in df_ventas['Vendedor'].dropna().unique():
                    df_vend = df_ventas[df_ventas['Vendedor'] == vendedor]
                    
                    cargadas = len(df_vend)
                    aprobadas = len(df_vend[df_vend['Aprobada'] == True])
                    efectividad = (aprobadas / cargadas * 100) if cargadas > 0 else 0
                    cumplimiento = (aprobadas / objetivo_aprobadas * 100) if objetivo_aprobadas > 0 else 0
                    
                    emoji, color, estado = aplicar_semaforo_cumplimiento(cumplimiento)
                    
                    kpis_vendedor.append({
                        'Vendedor': vendedor,
                        'Ventas Cargadas': cargadas,
                        'Ventas Aprobadas': aprobadas,
                        'Efectividad (%)': round(efectividad, 1),
                        'Cumplimiento (%)': round(cumplimiento, 1),
                        'Semáforo': emoji,
                        'Estado': estado
                    })
                
                df_kpis = pd.DataFrame(kpis_vendedor)
                df_kpis = df_kpis.sort_values('Ventas Aprobadas', ascending=False)
                
                # Métricas globales
                st.markdown("---")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_cargadas = df_kpis['Ventas Cargadas'].sum()
                    st.metric("📦 Total Cargadas", f"{total_cargadas:,}")
                
                with col2:
                    total_aprobadas = df_kpis['Ventas Aprobadas'].sum()
                    st.metric("✅ Total Aprobadas", f"{total_aprobadas:,}")
                
                with col3:
                    efectividad_global = (total_aprobadas / total_cargadas * 100) if total_cargadas > 0 else 0
                    st.metric("📈 Efectividad Global", f"{efectividad_global:.1f}%")
                
                with col4:
                    vendedores_cumpliendo = len(df_kpis[df_kpis['Cumplimiento (%)'] >= 90])
                    st.metric("🎯 Cumpliendo Objetivo", f"{vendedores_cumpliendo}/{len(df_kpis)}")
                
                # Resumen por semáforo
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                
                verdes = len(df_kpis[df_kpis['Semáforo'] == '🟢'])
                amarillos = len(df_kpis[df_kpis['Semáforo'] == '🟡'])
                rojos = len(df_kpis[df_kpis['Semáforo'] == '🔴'])
                
                with col1:
                    st.markdown(f"""
                    <div style='text-align:center; padding:20px; background:#D1FAE5; border-radius:10px;'>
                        <span style='font-size:40px;'>🟢</span><br>
                        <span style='font-size:28px; font-weight:bold; color:#065F46;'>{verdes}</span><br>
                        <small style='color:#065F46;'>Cumplido (≥90%)</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div style='text-align:center; padding:20px; background:#FEF3C7; border-radius:10px;'>
                        <span style='font-size:40px;'>🟡</span><br>
                        <span style='font-size:28px; font-weight:bold; color:#92400E;'>{amarillos}</span><br>
                        <small style='color:#92400E;'>En Proceso (60-89%)</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div style='text-align:center; padding:20px; background:#FEE2E2; border-radius:10px;'>
                        <span style='font-size:40px;'>🔴</span><br>
                        <span style='font-size:28px; font-weight:bold; color:#991B1B;'>{rojos}</span><br>
                        <small style='color:#991B1B;'>Bajo (&lt;60%)</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Tabla de KPIs
                st.markdown("---")
                st.markdown("#### 📋 Detalle por Vendedor")
                
                def color_cumplimiento(val):
                    if val >= 90:
                        return 'background-color: #D1FAE5; color: #065F46; font-weight: bold;'
                    elif val >= 60:
                        return 'background-color: #FEF3C7; color: #92400E; font-weight: bold;'
                    else:
                        return 'background-color: #FEE2E2; color: #991B1B; font-weight: bold;'
                
                styled_kpis = df_kpis.style.applymap(color_cumplimiento, subset=['Cumplimiento (%)'])
                st.dataframe(styled_kpis, use_container_width=True, height=400)
                
                # Gráfico de barras
                st.markdown("---")
                st.markdown("#### 📊 Comparativa de Ventas por Vendedor")
                
                top_vendedores = df_kpis.head(15)
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    name='Cargadas',
                    x=top_vendedores['Vendedor'],
                    y=top_vendedores['Ventas Cargadas'],
                    marker_color='#93C5FD'
                ))
                fig.add_trace(go.Bar(
                    name='Aprobadas',
                    x=top_vendedores['Vendedor'],
                    y=top_vendedores['Ventas Aprobadas'],
                    marker_color='#3B82F6'
                ))
                
                fig.add_hline(y=objetivo_aprobadas, line_dash="dash", line_color="#10B981",
                             annotation_text=f"Objetivo: {objetivo_aprobadas}")
                
                fig.update_layout(
                    barmode='group',
                    height=400,
                    paper_bgcolor='#FFFFFF',
                    plot_bgcolor='#FAFBFC',
                    xaxis_tickangle=-45,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Descargar
                st.markdown("---")
                csv_kpis = df_kpis.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Descargar KPIs (CSV)",
                    data=csv_kpis,
                    file_name=f"kpis_ventas_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("⚠️ No se encontraron las columnas necesarias (Vendedor, Estado)")
    
    # =========================================================================
    # TAB 5: ANÁLISIS CRUZADO E IQC
    # =========================================================================
    with tab5:
        st.markdown("### 🏆 Índice de Calidad Compuesto (IQC)")
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%); 
                    padding: 20px; border-radius: 15px; margin-bottom: 25px; color: white;'>
            <h4 style='margin:0 0 10px 0; color: white;'>📊 Fórmula IQC</h4>
            <p style='margin:0; font-family: monospace; font-size: 1.1rem;'>
                IQC = (Puntaje_EVA × 0.40) + (Efectividad_Ventas × 0.30) + (Engagement × 0.30)
            </p>
            <hr style='border-color: rgba(255,255,255,0.3); margin: 15px 0;'>
            <small>
                <strong>Puntaje EVA:</strong> Calificación de evaluaciones de llamadas<br>
                <strong>Efectividad Ventas:</strong> % de conversión (Aprobadas/Cargadas)<br>
                <strong>Engagement:</strong> Adherencia operativa (login, tipificaciones)
            </small>
        </div>
        """, unsafe_allow_html=True)
        
        # Verificar datos necesarios
        tiene_mitrol = 'df_calidad_procesado' in st.session_state
        tiene_solicitudes = 'df_calidad_solicitudes' in st.session_state
        tiene_eva = 'resumen_vendedores' in st.session_state or 'metricas_globales' in st.session_state
        
        # Status de datos
        col1, col2, col3 = st.columns(3)
        with col1:
            if tiene_eva:
                st.success("✅ Datos EVA disponibles")
            else:
                st.warning("⚠️ Ir a Panel Ejecutivo para generar datos EVA")
        with col2:
            if tiene_mitrol:
                st.success("✅ Datos Mitrol cargados")
            else:
                st.warning("⚠️ Cargar Mitrol en pestaña 'Carga de Datos'")
        with col3:
            if tiene_solicitudes:
                st.success("✅ Datos Ventas cargados")
            else:
                st.warning("⚠️ Cargar Solicitudes en pestaña 'Carga de Datos'")
        
        st.markdown("---")
        
        if tiene_mitrol and tiene_solicitudes:
            # Configurar pesos del IQC
            st.markdown("#### ⚖️ Configuración de Pesos")
            col1, col2, col3 = st.columns(3)
            with col1:
                peso_eva = st.slider("Peso EVA (%)", 0, 100, 40, 5, key='peso_eva')
            with col2:
                peso_ventas = st.slider("Peso Ventas (%)", 0, 100, 30, 5, key='peso_ventas')
            with col3:
                peso_engagement = st.slider("Peso Engagement (%)", 0, 100, 30, 5, key='peso_engagement')
            
            total_pesos = peso_eva + peso_ventas + peso_engagement
            if total_pesos != 100:
                st.warning(f"⚠️ La suma de pesos es {total_pesos}%, debe ser 100%")
            else:
                st.success(f"✅ Pesos configurados correctamente: {peso_eva}% EVA + {peso_ventas}% Ventas + {peso_engagement}% Engagement")
            
            st.markdown("---")
            
            # Calcular métricas
            if st.button("📊 Calcular IQC", type="primary", use_container_width=True):
                with st.spinner("Calculando Índice de Calidad Compuesto..."):
                    df_mitrol = st.session_state['df_calidad_procesado'].copy()
                    df_ventas = st.session_state['df_calidad_solicitudes'].copy()
                    df_mapeo = st.session_state.get('df_mapeo_vendedores', pd.DataFrame())
                    
                    # ============================================
                    # 1. MÉTRICAS DE VENTAS (Efectividad)
                    # ============================================
                    # Identificar columnas
                    col_vendedor = None
                    col_estado = None
                    for c in df_ventas.columns:
                        if 'vendedor' in c.lower():
                            col_vendedor = c
                        if 'estado' in c.lower():
                            col_estado = c
                    
                    if col_vendedor and col_estado:
                        # Agrupar por vendedor - convertir a string primero
                        df_ventas[col_estado] = df_ventas[col_estado].astype(str)
                        df_ventas['es_aprobada'] = df_ventas[col_estado].str.contains('APROB', case=False, na=False)
                        ventas_por_vendedor = df_ventas.groupby(col_vendedor).agg(
                            total_ventas=('es_aprobada', 'count'),
                            ventas_aprobadas=('es_aprobada', 'sum')
                        ).reset_index()
                        ventas_por_vendedor.columns = ['Vendedor_Ventas', 'Total_Ventas', 'Ventas_Aprobadas']
                        ventas_por_vendedor['Efectividad_Ventas'] = (
                            ventas_por_vendedor['Ventas_Aprobadas'] / 
                            ventas_por_vendedor['Total_Ventas'] * 100
                        ).fillna(0)
                        ventas_por_vendedor['Vendedor_norm'] = ventas_por_vendedor['Vendedor_Ventas'].astype(str).str.upper().str.strip()
                    else:
                        ventas_por_vendedor = pd.DataFrame()
                    
                    # ============================================
                    # 2. MÉTRICAS MITROL (Engagement)
                    # ============================================
                    # Calcular engagement basado en tipificaciones y tiempos
                    engagement_cols = ['Vendedor', 'Equipo']
                    
                    # Buscar columnas de tipificación
                    cols_tipif_ok = [c for c in df_mitrol.columns if 'exitoso' in c.lower() and 'no' not in c.lower()]
                    cols_tipif_no = [c for c in df_mitrol.columns if 'no exitoso' in c.lower() or 'noexitoso' in c.lower()]
                    
                    df_mitrol_agg = df_mitrol.groupby('Vendedor').agg({
                        c: 'sum' for c in cols_tipif_ok + cols_tipif_no if c in df_mitrol.columns
                    }).reset_index() if cols_tipif_ok or cols_tipif_no else pd.DataFrame()
                    
                    if not df_mitrol_agg.empty and cols_tipif_ok:
                        df_mitrol_agg['Total_Tipif_OK'] = df_mitrol_agg[cols_tipif_ok].sum(axis=1) if cols_tipif_ok else 0
                        df_mitrol_agg['Total_Tipif_NO'] = df_mitrol_agg[cols_tipif_no].sum(axis=1) if cols_tipif_no else 0
                        df_mitrol_agg['Total_Tipif'] = df_mitrol_agg['Total_Tipif_OK'] + df_mitrol_agg['Total_Tipif_NO']
                        df_mitrol_agg['Engagement'] = (
                            df_mitrol_agg['Total_Tipif_OK'] / df_mitrol_agg['Total_Tipif'] * 100
                        ).fillna(50)
                    else:
                        # Si no hay tipificaciones, usar engagement base
                        df_mitrol_agg = df_mitrol[['Vendedor']].drop_duplicates()
                        df_mitrol_agg['Engagement'] = 70  # Valor base
                    
                    df_mitrol_agg['Vendedor_norm'] = df_mitrol_agg['Vendedor'].str.upper().str.strip()
                    
                    # ============================================
                    # 3. MÉTRICAS EVA (Puntaje Evaluaciones)
                    # ============================================
                    puntaje_eva_por_vendedor = pd.DataFrame()
                    if tiene_eva and 'resumen_vendedores' in st.session_state:
                        # Usar datos de EVA si existen
                        df_eva = st.session_state.get('resumen_vendedores', pd.DataFrame())
                        if not df_eva.empty and 'vendedor' in [c.lower() for c in df_eva.columns]:
                            col_vend_eva = [c for c in df_eva.columns if 'vendedor' in c.lower()][0]
                            col_punt_eva = [c for c in df_eva.columns if 'punt' in c.lower() or 'score' in c.lower() or 'nota' in c.lower()]
                            if col_punt_eva:
                                puntaje_eva_por_vendedor = df_eva[[col_vend_eva, col_punt_eva[0]]].copy()
                                puntaje_eva_por_vendedor.columns = ['Vendedor_EVA', 'Puntaje_EVA']
                                puntaje_eva_por_vendedor['Vendedor_norm'] = puntaje_eva_por_vendedor['Vendedor_EVA'].str.upper().str.strip()
                    
                    # ============================================
                    # 4. UNIFICAR DATOS - CREAR IQC
                    # ============================================
                    # Base: vendedores de Mitrol
                    df_iqc = df_mitrol_agg[['Vendedor', 'Vendedor_norm', 'Engagement']].copy()
                    
                    # Unir ventas
                    if not ventas_por_vendedor.empty:
                        df_iqc = df_iqc.merge(
                            ventas_por_vendedor[['Vendedor_norm', 'Total_Ventas', 'Ventas_Aprobadas', 'Efectividad_Ventas']],
                            on='Vendedor_norm',
                            how='left'
                        )
                    else:
                        df_iqc['Total_Ventas'] = 0
                        df_iqc['Ventas_Aprobadas'] = 0
                        df_iqc['Efectividad_Ventas'] = 50
                    
                    # Unir EVA
                    if not puntaje_eva_por_vendedor.empty:
                        df_iqc = df_iqc.merge(
                            puntaje_eva_por_vendedor[['Vendedor_norm', 'Puntaje_EVA']],
                            on='Vendedor_norm',
                            how='left'
                        )
                    else:
                        df_iqc['Puntaje_EVA'] = 70  # Valor base si no hay datos EVA
                    
                    # Rellenar NaN
                    df_iqc['Engagement'] = df_iqc['Engagement'].fillna(50)
                    df_iqc['Efectividad_Ventas'] = df_iqc['Efectividad_Ventas'].fillna(50)
                    df_iqc['Puntaje_EVA'] = df_iqc['Puntaje_EVA'].fillna(70)
                    
                    # Normalizar métricas a escala 0-100
                    df_iqc['EVA_norm'] = df_iqc['Puntaje_EVA'].clip(0, 100)
                    df_iqc['Ventas_norm'] = df_iqc['Efectividad_Ventas'].clip(0, 100)
                    df_iqc['Engagement_norm'] = df_iqc['Engagement'].clip(0, 100)
                    
                    # CALCULAR IQC
                    df_iqc['IQC'] = (
                        df_iqc['EVA_norm'] * (peso_eva / 100) +
                        df_iqc['Ventas_norm'] * (peso_ventas / 100) +
                        df_iqc['Engagement_norm'] * (peso_engagement / 100)
                    )
                    
                    # Clasificar rendimiento
                    def clasificar_iqc(score):
                        if score >= 80:
                            return '🟢 Excelente'
                        elif score >= 60:
                            return '🟡 Adecuado'
                        elif score >= 40:
                            return '🟠 En Desarrollo'
                        else:
                            return '🔴 Requiere Atención'
                    
                    df_iqc['Clasificación'] = df_iqc['IQC'].apply(clasificar_iqc)
                    
                    # Ordenar por IQC
                    df_iqc = df_iqc.sort_values('IQC', ascending=False).reset_index(drop=True)
                    df_iqc['Ranking'] = range(1, len(df_iqc) + 1)
                    
                    # Guardar en session_state
                    st.session_state['df_iqc'] = df_iqc
                
                # =========================================
                # MOSTRAR RESULTADOS IQC
                # =========================================
                if 'df_iqc' in st.session_state:
                    df_iqc = st.session_state['df_iqc']
                    
                    st.markdown("### 🏆 Ranking de Calidad Integral")
                    
                    # KPIs resumen
                    col1, col2, col3, col4 = st.columns(4)
                    excelentes = len(df_iqc[df_iqc['IQC'] >= 80])
                    adecuados = len(df_iqc[(df_iqc['IQC'] >= 60) & (df_iqc['IQC'] < 80)])
                    desarrollo = len(df_iqc[(df_iqc['IQC'] >= 40) & (df_iqc['IQC'] < 60)])
                    atencion = len(df_iqc[df_iqc['IQC'] < 40])
                    
                    with col1:
                        st.markdown(f"""
                        <div style='background: #D1FAE5; padding: 15px; border-radius: 10px; text-align: center;'>
                            <span style='font-size: 28px;'>🟢</span><br>
                            <span style='font-size: 24px; font-weight: bold; color: #065F46;'>{excelentes}</span><br>
                            <small style='color: #065F46;'>Excelente (≥80)</small>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""
                        <div style='background: #FEF3C7; padding: 15px; border-radius: 10px; text-align: center;'>
                            <span style='font-size: 28px;'>🟡</span><br>
                            <span style='font-size: 24px; font-weight: bold; color: #92400E;'>{adecuados}</span><br>
                            <small style='color: #92400E;'>Adecuado (60-79)</small>
                        </div>
                        """, unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"""
                        <div style='background: #FFEDD5; padding: 15px; border-radius: 10px; text-align: center;'>
                            <span style='font-size: 28px;'>🟠</span><br>
                            <span style='font-size: 24px; font-weight: bold; color: #9A3412;'>{desarrollo}</span><br>
                            <small style='color: #9A3412;'>En Desarrollo (40-59)</small>
                        </div>
                        """, unsafe_allow_html=True)
                    with col4:
                        st.markdown(f"""
                        <div style='background: #FEE2E2; padding: 15px; border-radius: 10px; text-align: center;'>
                            <span style='font-size: 28px;'>🔴</span><br>
                            <span style='font-size: 24px; font-weight: bold; color: #991B1B;'>{atencion}</span><br>
                            <small style='color: #991B1B;'>Atención (&lt;40)</small>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Gráfico radar para top 5
                    st.markdown("#### 📊 Comparativa Top 5 Agentes")
                    top5 = df_iqc.head(5)
                    
                    fig_radar = go.Figure()
                    colores = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']
                    for i, (_, row) in enumerate(top5.iterrows()):
                        fig_radar.add_trace(go.Scatterpolar(
                            r=[row['EVA_norm'], row['Ventas_norm'], row['Engagement_norm'], row['EVA_norm']],
                            theta=['EVA', 'Ventas', 'Engagement', 'EVA'],
                            fill='toself',
                            name=f"{row['Ranking']}. {row['Vendedor'][:15]}",
                            line_color=colores[i],
                            opacity=0.7
                        ))
                    
                    fig_radar.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                        showlegend=True,
                        height=400,
                        paper_bgcolor='white'
                    )
                    st.plotly_chart(fig_radar, use_container_width=True)
                    
                    # Tabla detallada
                    st.markdown("#### 📋 Tabla Detallada IQC")
                    
                    cols_mostrar = ['Ranking', 'Vendedor', 'IQC', 'Clasificación', 
                                    'Puntaje_EVA', 'Efectividad_Ventas', 'Engagement',
                                    'Total_Ventas', 'Ventas_Aprobadas']
                    cols_disponibles = [c for c in cols_mostrar if c in df_iqc.columns]
                    df_mostrar = df_iqc[cols_disponibles].copy()
                    
                    # Formatear números
                    for col in ['IQC', 'Puntaje_EVA', 'Efectividad_Ventas', 'Engagement']:
                        if col in df_mostrar.columns:
                            df_mostrar[col] = df_mostrar[col].round(1)
                    
                    # Aplicar estilos
                    def style_iqc(val):
                        if val >= 80:
                            return 'background-color: #D1FAE5; color: #065F46; font-weight: bold;'
                        elif val >= 60:
                            return 'background-color: #FEF3C7; color: #92400E; font-weight: bold;'
                        elif val >= 40:
                            return 'background-color: #FFEDD5; color: #9A3412; font-weight: bold;'
                        else:
                            return 'background-color: #FEE2E2; color: #991B1B; font-weight: bold;'
                    
                    styled_df = df_mostrar.style.applymap(style_iqc, subset=['IQC'])
                    st.dataframe(styled_df, use_container_width=True, height=400)
                    
                    # Sistema de Alertas
                    st.markdown("---")
                    st.markdown("### ⚠️ Sistema de Alertas")
                    
                    alertas = df_iqc[df_iqc['IQC'] < 50]
                    if len(alertas) > 0:
                        st.error(f"🚨 **{len(alertas)} agentes requieren atención inmediata:**")
                        for _, agente in alertas.iterrows():
                            problemas = []
                            if agente.get('Puntaje_EVA', 100) < 60:
                                problemas.append("EVA bajo")
                            if agente.get('Efectividad_Ventas', 100) < 40:
                                problemas.append("Baja efectividad ventas")
                            if agente.get('Engagement', 100) < 50:
                                problemas.append("Engagement bajo")
                            
                            st.markdown(f"""
                            <div style='background: #FEE2E2; padding: 10px 15px; border-radius: 8px; 
                                        margin: 5px 0; border-left: 4px solid #EF4444;'>
                                <strong>{agente['Vendedor']}</strong> · IQC: {agente['IQC']:.1f}<br>
                                <small style='color: #991B1B;'>Áreas críticas: {', '.join(problemas) if problemas else 'Múltiples indicadores'}</small>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.success("✅ No hay agentes en estado crítico")
                    
                    # Descargar reporte IQC
                    st.markdown("---")
                    csv_iqc = df_iqc.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Descargar Reporte IQC Completo (CSV)",
                        data=csv_iqc,
                        file_name=f"reporte_iqc_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
        else:
            st.info("ℹ️ Carga los archivos de Mitrol y Solicitudes en la pestaña 'Carga de Datos' para calcular el IQC")


def cargar_datos_calidad_procesados():
    """Carga los datos de calidad preprocesados desde el JSON"""
    ruta_json = os.path.join(os.path.dirname(__file__), 'datos_calidad', 'datos_calidad_procesados.json')
    
    if os.path.exists(ruta_json):
        try:
            with open(ruta_json, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error cargando datos de calidad: {e}")
            return None
    else:
        return None


def pagina_metricas_calidad():
    """Página de Métricas de Calidad - 3 Apartados: Tiempos, Ventas, Llamadas + Comparativa"""
    
    st.markdown('<p class="main-header">📊 COMMAND · Métricas de Calidad</p>', unsafe_allow_html=True)
    st.markdown(
        """
        <div style='background: #F1F5F9; padding: 20px; border-radius: 12px; border-left: 5px solid #6366F1;'>
            <h3 style='margin: 0; color: #1E293B;'>🛠️ En desarrollo</h3>
            <p style='margin: 8px 0 0 0; color: #475569;'>
                Este apartado estara disponible pronto con metricas de tiempos, ventas y llamadas.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    return
    
    # Obtener permisos del usuario actual
    permisos = obtener_permisos_usuario()
    
    # Cargar datos preprocesados
    datos = cargar_datos_calidad_procesados()
    
    if datos is None:
        st.warning("⚠️ **No hay datos procesados.** Ejecute el proceso `procesar_calidad.py` primero.")
        return
    
    fecha_proceso = datos.get('fecha_proceso', 'N/A')
    datos_tiempos = datos.get('tiempos', {})
    datos_ventas = datos.get('ventas', {})
    datos_llamadas = datos.get('llamadas', {})
    
    # Obtener listas de agentes y equipos para filtros
    tiempos_vendedor = datos_tiempos.get('por_vendedor', [])
    ventas_vendedor = datos_ventas.get('por_vendedor', [])
    llamadas_vendedor = datos_llamadas.get('por_vendedor', [])
    
    # =========================================================================
    # APLICAR FILTRO POR PERMISOS
    # =========================================================================
    if permisos['rol'] == 'vendedor':
        # Vendedor: Solo puede ver sus propios datos
        nombre_vendedor = permisos['nombre_usuario'].lower()
        tiempos_vendedor = [v for v in tiempos_vendedor if nombre_vendedor in str(v.get('vendedor', '')).lower()]
        ventas_vendedor = [v for v in ventas_vendedor if nombre_vendedor in str(v.get('vendedor', '')).lower()]
        llamadas_vendedor = [v for v in llamadas_vendedor if nombre_vendedor in str(v.get('vendedor', '')).lower()]
        equipo_usuario = permisos['equipo'] if permisos['equipo'] else "Sin Equipo"
        st.info(f"👤 Mostrando métricas de: **{permisos['nombre_usuario']}** | Equipo: **{equipo_usuario}**")
        
    elif permisos['rol'] == 'supervisor' and permisos['equipos_permitidos']:
        # Supervisor: Solo puede ver datos de su equipo
        equipo_supervisor = permisos['equipos_permitidos'][0]
        tiempos_vendedor = [v for v in tiempos_vendedor if v.get('equipo') == equipo_supervisor]
        ventas_vendedor = [v for v in ventas_vendedor if v.get('supervisor') == equipo_supervisor]
        llamadas_vendedor = [v for v in llamadas_vendedor if v.get('equipo') == equipo_supervisor]
        st.info(f"🏢 Mostrando métricas del equipo: **{equipo_supervisor}**")
    
    # Crear sets de agentes y equipos únicos - POR SECCIÓN
    agentes_tiempos = set()
    equipos_tiempos = set()
    agentes_ventas = set()
    equipos_ventas = set()  # supervisores en ventas
    agentes_llamadas = set()
    equipos_llamadas = set()
    
    for v in tiempos_vendedor:
        if v.get('vendedor'): agentes_tiempos.add(v['vendedor'])
        if v.get('equipo') and v.get('equipo') != 'Sin Equipo': equipos_tiempos.add(v['equipo'])
    
    for v in ventas_vendedor:
        if v.get('vendedor'): agentes_ventas.add(v['vendedor'])
        if v.get('supervisor') and v.get('supervisor') not in ['Sin Supervisor', '']: 
            equipos_ventas.add(v['supervisor'])
    
    for v in llamadas_vendedor:
        if v.get('vendedor'): agentes_llamadas.add(v['vendedor'])
        if v.get('equipo') and v.get('equipo') != 'Sin Equipo': equipos_llamadas.add(v['equipo'])
    
    # Listas globales (unión de todas)
    todos_agentes = sorted(list(agentes_tiempos | agentes_ventas | agentes_llamadas))
    todos_equipos = sorted(list(equipos_tiempos | equipos_ventas | equipos_llamadas))
    
    # Listas por sección ordenadas
    agentes_tiempos = sorted(list(agentes_tiempos))
    equipos_tiempos = sorted(list(equipos_tiempos))
    agentes_ventas = sorted(list(agentes_ventas))
    equipos_ventas = sorted(list(equipos_ventas))
    agentes_llamadas = sorted(list(agentes_llamadas))
    equipos_llamadas = sorted(list(equipos_llamadas))
    
    # Header con fecha
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%); 
                padding: 15px 20px; border-radius: 10px; margin-bottom: 20px; color: white;'>
        <p style='margin: 0; font-size: 0.9rem;'>📅 <strong>Última actualización:</strong> {fecha_proceso}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # =========================================================================
    # FILTROS GLOBALES - Ajustados según permisos
    # =========================================================================
    if permisos['puede_ver_todos']:
        # Admin: Mostrar filtros completos
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1E3A5F 0%, #334155 100%); 
                    padding: 20px; border-radius: 12px; margin-bottom: 20px;'>
            <p style='margin: 0 0 10px 0; font-size: 1.1rem; font-weight: 700; color: #FFFFFF;'>
                🔍 FILTROS DE VISUALIZACIÓN
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col_filtro1, col_filtro2, col_filtro3 = st.columns([1.5, 2, 2])
        
        with col_filtro1:
            st.markdown("""
            <p style='color: #1E3A5F; font-weight: 700; font-size: 1rem; margin-bottom: 8px;'>
                📋 Tipo de Vista:
            </p>
            """, unsafe_allow_html=True)
            tipo_filtro = st.radio("", ["🌐 General", "🏢 Por Equipo", "👤 Por Agente"], 
                                   horizontal=False, key='tipo_filtro_calidad', label_visibility="collapsed")
        
        equipo_seleccionado = None
        agente_seleccionado = None
        
        with col_filtro2:
            if tipo_filtro == "🏢 Por Equipo":
                st.markdown("""
                <p style='color: #1E3A5F; font-weight: 700; font-size: 1rem; margin-bottom: 8px;'>
                    🏢 Seleccionar Equipo:
                </p>
                """, unsafe_allow_html=True)
                equipo_seleccionado = st.selectbox("", ['Seleccione un equipo...'] + todos_equipos, 
                                                   key='equipo_calidad', label_visibility="collapsed")
                if equipo_seleccionado == 'Seleccione un equipo...':
                    equipo_seleccionado = None
            elif tipo_filtro == "👤 Por Agente":
                st.markdown("""
                <p style='color: #1E3A5F; font-weight: 700; font-size: 1rem; margin-bottom: 8px;'>
                    👤 Seleccionar Agente:
                </p>
                """, unsafe_allow_html=True)
                agente_seleccionado = st.selectbox("", ['Seleccione un agente...'] + todos_agentes, 
                                                   key='agente_calidad', label_visibility="collapsed")
                if agente_seleccionado == 'Seleccione un agente...':
                    agente_seleccionado = None
            else:
                st.markdown("""
                <div style='background: #EFF6FF; padding: 15px; border-radius: 8px; border-left: 4px solid #3B82F6;'>
                    <p style='margin: 0; color: #1E40AF; font-weight: 600;'>
                        ℹ️ Vista general: mostrando todos los datos
                    </p>
                </div>
                """, unsafe_allow_html=True)
    elif permisos['rol'] == 'supervisor':
        # Supervisor: Solo puede filtrar por agente dentro de su equipo
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1E3A5F 0%, #334155 100%); 
                    padding: 20px; border-radius: 12px; margin-bottom: 20px;'>
            <p style='margin: 0 0 10px 0; font-size: 1.1rem; font-weight: 700; color: #FFFFFF;'>
                🔍 FILTROS DE VISUALIZACIÓN
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col_filtro1, col_filtro2 = st.columns([1.5, 2])
        
        with col_filtro1:
            st.markdown("""
            <p style='color: #1E3A5F; font-weight: 700; font-size: 1rem; margin-bottom: 8px;'>
                📋 Tipo de Vista:
            </p>
            """, unsafe_allow_html=True)
            tipo_filtro = st.radio("", ["🌐 Todo el Equipo", "👤 Por Agente"], 
                                   horizontal=False, key='tipo_filtro_calidad', label_visibility="collapsed")
        
        equipo_seleccionado = permisos['equipos_permitidos'][0] if permisos['equipos_permitidos'] else None
        agente_seleccionado = None
        
        with col_filtro2:
            if tipo_filtro == "👤 Por Agente":
                st.markdown("""
                <p style='color: #1E3A5F; font-weight: 700; font-size: 1rem; margin-bottom: 8px;'>
                    👤 Seleccionar Agente:
                </p>
                """, unsafe_allow_html=True)
                agente_seleccionado = st.selectbox("", ['Seleccione un agente...'] + todos_agentes, 
                                                   key='agente_calidad', label_visibility="collapsed")
                if agente_seleccionado == 'Seleccione un agente...':
                    agente_seleccionado = None
            else:
                st.markdown("""
                <div style='background: #EFF6FF; padding: 15px; border-radius: 8px; border-left: 4px solid #3B82F6;'>
                    <p style='margin: 0; color: #1E40AF; font-weight: 600;'>
                        ℹ️ Mostrando datos de todo el equipo
                    </p>
                </div>
                """, unsafe_allow_html=True)
    else:
        # Vendedor: Sin filtros, solo ve sus datos
        tipo_filtro = "👤 Por Agente"
        equipo_seleccionado = None
        agente_seleccionado = todos_agentes[0] if todos_agentes else None
    
    # col_filtro3 solo para admin (muestra info adicional)
    if permisos['puede_ver_todos']:
        with col_filtro3:
            if tipo_filtro == "🏢 Por Equipo" and equipo_seleccionado:
                # Mostrar agentes del equipo
                agentes_equipo = [v['vendedor'] for v in tiempos_vendedor if v.get('equipo') == equipo_seleccionado]
                agentes_equipo += [v['vendedor'] for v in ventas_vendedor if v.get('supervisor') == equipo_seleccionado]
                agentes_equipo += [v['vendedor'] for v in llamadas_vendedor if v.get('equipo') == equipo_seleccionado]
                agentes_equipo = sorted(list(set(agentes_equipo)))
                
                # Verificar disponibilidad en cada sección
                en_tiempos = equipo_seleccionado in equipos_tiempos
                en_ventas = equipo_seleccionado in equipos_ventas
                en_llamadas = equipo_seleccionado in equipos_llamadas
                
                st.markdown(f"""
                <div style='background: #DCFCE7; padding: 15px; border-radius: 8px; border-left: 4px solid #22C55E;'>
                    <p style='margin: 0 0 8px 0; color: #166534; font-weight: 700; font-size: 1.1rem;'>
                        👥 {len(agentes_equipo)} agentes en este equipo
                    </p>
                    <p style='margin: 0; color: #166534; font-size: 0.85rem;'>
                        ⏱️ Tiempos: {'✅' if en_tiempos else '❌'} | 
                        💼 Ventas: {'✅' if en_ventas else '❌'} | 
                        📞 Llamadas: {'✅' if en_llamadas else '❌'}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            elif tipo_filtro == "👤 Por Agente" and agente_seleccionado:
                # Verificar disponibilidad en cada sección
                en_tiempos = agente_seleccionado in agentes_tiempos
                en_ventas = agente_seleccionado in agentes_ventas
                en_llamadas = agente_seleccionado in agentes_llamadas
                
                st.markdown(f"""
                <div style='background: #DCFCE7; padding: 15px; border-radius: 8px; border-left: 4px solid #22C55E;'>
                    <p style='margin: 0 0 8px 0; color: #166534; font-weight: 700;'>
                        ✅ Mostrando datos de: <strong>{agente_seleccionado}</strong>
                    </p>
                    <p style='margin: 0; color: #166534; font-size: 0.85rem;'>
                        ⏱️ Tiempos: {'✅' if en_tiempos else '❌'} | 
                        💼 Ventas: {'✅' if en_ventas else '❌'} | 
                        📞 Llamadas: {'✅' if en_llamadas else '❌'}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            elif tipo_filtro == "🏢 Por Equipo" and not equipo_seleccionado:
                # Mostrar info de disponibilidad de equipos
                st.markdown(f"""
                <div style='background: #FEF3C7; padding: 15px; border-radius: 8px; border-left: 4px solid #F59E0B;'>
                    <p style='margin: 0; color: #92400E; font-size: 0.85rem;'>
                        ⚠️ <strong>Equipos disponibles:</strong><br>
                        ⏱️ Tiempos: {len(equipos_tiempos)} equipos<br>
                        💼 Ventas: {len(equipos_ventas)} supervisores<br>
                        📞 Llamadas: {len(equipos_llamadas)} equipos
                    </p>
                </div>
                """, unsafe_allow_html=True)
            elif tipo_filtro == "👤 Por Agente" and not agente_seleccionado:
                # Mostrar info de disponibilidad de agentes
                st.markdown(f"""
                <div style='background: #FEF3C7; padding: 15px; border-radius: 8px; border-left: 4px solid #F59E0B;'>
                    <p style='margin: 0; color: #92400E; font-size: 0.85rem;'>
                        ⚠️ <strong>Agentes disponibles:</strong><br>
                        ⏱️ Tiempos: {len(agentes_tiempos)}<br>
                        💼 Ventas: {len(agentes_ventas)}<br>
                        📞 Llamadas: {len(agentes_llamadas)}
                    </p>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Función helper para normalizar nombres (quitar espacios, mayúsculas, etc.)
    def normalizar_nombre(nombre):
        if not nombre:
            return ""
        return str(nombre).upper().replace(" ", "").replace(".", "").strip()
    
    # Función helper para filtrar datos con matching flexible
    def filtrar_datos(lista_datos, campo_equipo='equipo', campo_vendedor='vendedor'):
        if not lista_datos:
            return []
        if tipo_filtro == "🌐 General":
            return lista_datos
        elif tipo_filtro == "🏢 Por Equipo" and equipo_seleccionado:
            # Buscar por equipo o supervisor
            return [v for v in lista_datos 
                    if v.get(campo_equipo) == equipo_seleccionado 
                    or v.get('supervisor') == equipo_seleccionado
                    or v.get('equipo') == equipo_seleccionado]
        elif tipo_filtro == "👤 Por Agente" and agente_seleccionado:
            # Matching flexible: por nombre exacto o normalizado
            agente_norm = normalizar_nombre(agente_seleccionado)
            return [v for v in lista_datos 
                    if v.get(campo_vendedor) == agente_seleccionado 
                    or normalizar_nombre(v.get(campo_vendedor)) == agente_norm
                    or normalizar_nombre(v.get('agente')) == agente_norm]
        return lista_datos
    
    # 4 TABS PRINCIPALES (agregamos Comparativa)
    tab1, tab2, tab3 = st.tabs(["⏱️ TIEMPOS", "💼 VENTAS", "📞 LLAMADAS"])
    
    # =========================================================================
    # TAB 1: TIEMPOS (Break, Coaching, Administrativo, Baño, etc.)
    # =========================================================================
    with tab1:
        st.markdown("### ⏱️ Reporte de Tiempos por Agente")
        
        tiempos_filtrados = filtrar_datos(tiempos_vendedor, campo_equipo='equipo', campo_vendedor='vendedor')
        totales_t = datos_tiempos.get('totales', {})
        
        if not tiempos_filtrados:
            st.info("No hay datos de tiempos disponibles para el filtro seleccionado")
        else:
            # Calcular totales para los datos filtrados
            if tipo_filtro != "🌐 General":
                # Recalcular totales para el subconjunto filtrado
                df_temp = pd.DataFrame(tiempos_filtrados)
                totales_t = {
                    'break_prom_fmt': pd.to_timedelta(df_temp['break_seg'].mean(), unit='s').components if 'break_seg' in df_temp.columns else '00:00:00',
                    'coaching_prom_fmt': pd.to_timedelta(df_temp['coaching_seg'].mean(), unit='s').components if 'coaching_seg' in df_temp.columns else '00:00:00',
                    'administrativo_prom_fmt': pd.to_timedelta(df_temp['administrativo_seg'].mean(), unit='s').components if 'administrativo_seg' in df_temp.columns else '00:00:00',
                    'baño_prom_fmt': pd.to_timedelta(df_temp['baño_seg'].mean(), unit='s').components if 'baño_seg' in df_temp.columns else '00:00:00',
                    'almuerzo_prom_fmt': pd.to_timedelta(df_temp['almuerzo_seg'].mean(), unit='s').components if 'almuerzo_seg' in df_temp.columns else '00:00:00',
                    'logueo_prom_fmt': pd.to_timedelta(df_temp['logueo_seg'].mean(), unit='s').components if 'logueo_seg' in df_temp.columns else '00:00:00',
                }
                # Formatear tiempos
                for k in list(totales_t.keys()):
                    if '_prom_fmt' in k:
                        base_k = k.replace('_prom_fmt', '_seg')
                        if base_k in df_temp.columns:
                            seg = df_temp[base_k].mean()
                            if pd.notna(seg):
                                h = int(seg // 3600)
                                m = int((seg % 3600) // 60)
                                s = int(seg % 60)
                                totales_t[k] = f"{h:02d}:{m:02d}:{s:02d}"
                            else:
                                totales_t[k] = '00:00:00'
                
                # Totales en segundos
                totales_t['break'] = df_temp['break_seg'].sum() if 'break_seg' in df_temp.columns else 0
                totales_t['coaching'] = df_temp['coaching_seg'].sum() if 'coaching_seg' in df_temp.columns else 0
                totales_t['administrativo'] = df_temp['administrativo_seg'].sum() if 'administrativo_seg' in df_temp.columns else 0
                totales_t['baño'] = df_temp['baño_seg'].sum() if 'baño_seg' in df_temp.columns else 0
                totales_t['almuerzo'] = df_temp['almuerzo_seg'].sum() if 'almuerzo_seg' in df_temp.columns else 0
                totales_t['llamada_manual'] = df_temp['llamada_manual_seg'].sum() if 'llamada_manual_seg' in df_temp.columns else 0
            
            # Título según filtro
            if tipo_filtro == "👤 Por Agente" and agente_seleccionado:
                st.markdown(f"#### 👤 Tiempos de: **{agente_seleccionado}**")
            elif tipo_filtro == "🏢 Por Equipo" and equipo_seleccionado:
                st.markdown(f"#### 🏢 Tiempos del Equipo: **{equipo_seleccionado}** ({len(tiempos_filtrados)} agentes)")
            
            # KPIs de tiempos
            st.markdown("#### 📊 Promedios")
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            with col1:
                st.metric("☕ Break", totales_t.get('break_prom_fmt', '00:00:00'))
            with col2:
                st.metric("📚 Coaching", totales_t.get('coaching_prom_fmt', '00:00:00'))
            with col3:
                st.metric("📋 Admin", totales_t.get('administrativo_prom_fmt', '00:00:00'))
            with col4:
                st.metric("🚻 Baño", totales_t.get('baño_prom_fmt', '00:00:00'))
            with col5:
                st.metric("🍽️ Almuerzo", totales_t.get('almuerzo_prom_fmt', '00:00:00'))
            with col6:
                st.metric("⏰ Logueo", totales_t.get('logueo_prom_fmt', '00:00:00'))
            
            st.markdown("---")
            
            # Gráfico de distribución de tiempos
            st.markdown("#### 📊 Distribución de Tiempos Auxiliares")
            
            tiempos_dist = {
                'Break': totales_t.get('break', 0) / 3600 if totales_t.get('break') else 0,
                'Coaching': totales_t.get('coaching', 0) / 3600 if totales_t.get('coaching') else 0,
                'Administrativo': totales_t.get('administrativo', 0) / 3600 if totales_t.get('administrativo') else 0,
                'Baño': totales_t.get('baño', 0) / 3600 if totales_t.get('baño') else 0,
                'Almuerzo': totales_t.get('almuerzo', 0) / 3600 if totales_t.get('almuerzo') else 0,
                'Llamada Manual': totales_t.get('llamada_manual', 0) / 3600 if totales_t.get('llamada_manual') else 0
            }
            
            col1, col2 = st.columns(2)
            with col1:
                fig_pie = go.Figure(data=[go.Pie(
                    labels=list(tiempos_dist.keys()),
                    values=list(tiempos_dist.values()),
                    hole=0.4,
                    marker_colors=['#3B82F6', '#8B5CF6', '#F59E0B', '#EF4444', '#10B981', '#6366F1']
                )])
                fig_pie.update_layout(title="Distribución de Tiempos Auxiliares (horas)", height=350)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # Top 10 con más tiempo auxiliar (o barra individual si es un agente)
                df_t = pd.DataFrame(tiempos_filtrados)
                if len(df_t) > 1:
                    df_t = df_t.sort_values('tiempo_auxiliar_seg', ascending=False).head(10)
                    fig_bar = go.Figure()
                    fig_bar.add_trace(go.Bar(
                        x=df_t['vendedor'],
                        y=df_t['tiempo_auxiliar_seg'] / 60,
                        marker_color='#EF4444',
                        text=df_t['tiempo_auxiliar_fmt'],
                        textposition='outside'
                    ))
                    fig_bar.update_layout(title="Top 10 Mayor Tiempo Auxiliar", yaxis_title="Minutos", height=350, xaxis_tickangle=-45)
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    # Agente individual - mostrar desglose
                    agente_data = tiempos_filtrados[0]
                    tiempos_ind = {
                        'Break': agente_data.get('break_seg', 0) / 60,
                        'Coaching': agente_data.get('coaching_seg', 0) / 60,
                        'Admin': agente_data.get('administrativo_seg', 0) / 60,
                        'Baño': agente_data.get('baño_seg', 0) / 60,
                        'Almuerzo': agente_data.get('almuerzo_seg', 0) / 60,
                        'Logueo': agente_data.get('logueo_seg', 0) / 60
                    }
                    fig_bar = go.Figure()
                    fig_bar.add_trace(go.Bar(
                        x=list(tiempos_ind.keys()),
                        y=list(tiempos_ind.values()),
                        marker_color=['#3B82F6', '#8B5CF6', '#F59E0B', '#EF4444', '#10B981', '#6366F1'],
                        text=[f"{v:.1f} min" for v in tiempos_ind.values()],
                        textposition='outside'
                    ))
                    fig_bar.update_layout(title=f"Desglose de Tiempos - {agente_seleccionado}", yaxis_title="Minutos", height=350)
                    st.plotly_chart(fig_bar, use_container_width=True)
            
            st.markdown("---")
            
            # Tabla detallada
            st.markdown("#### 📋 Detalle por Vendedor/Agente")
            
            df_tiempos = pd.DataFrame(tiempos_filtrados)
            
            # Seleccionar columnas relevantes
            cols_mostrar = ['vendedor', 'equipo', 'break_fmt', 'coaching_fmt', 'administrativo_fmt', 
                           'baño_fmt', 'almuerzo_fmt', 'logueo_fmt', 'tiempo_auxiliar_fmt', 'pct_productivo']
            cols_disponibles = [c for c in cols_mostrar if c in df_tiempos.columns]
            df_display = df_tiempos[cols_disponibles].copy()
            df_display.columns = ['Vendedor', 'Equipo', 'Break', 'Coaching', 'Admin', 'Baño', 'Almuerzo', 'Logueo', 'T. Auxiliar', '% Productivo'][:len(cols_disponibles)]
            
            st.dataframe(df_display.sort_values('Vendedor' if 'Vendedor' in df_display.columns else df_display.columns[0]), use_container_width=True, height=400)
    
    # =========================================================================
    # TAB 2: VENTAS
    # =========================================================================
    with tab2:
        st.markdown("### 💼 Reporte de Ventas")
        
        ventas_filtradas = filtrar_datos(ventas_vendedor, campo_equipo='supervisor', campo_vendedor='vendedor')
        totales_v = datos_ventas.get('totales', {})
        ventas_supervisor = datos_ventas.get('por_supervisor', [])
        
        if not ventas_filtradas:
            st.info("No hay datos de ventas disponibles para el filtro seleccionado")
        else:
            # Recalcular totales si hay filtro
            if tipo_filtro != "🌐 General":
                df_temp = pd.DataFrame(ventas_filtradas)
                totales_v = {
                    'total_ventas': df_temp['total_ventas'].sum() if 'total_ventas' in df_temp.columns else 0,
                    'total_aprobadas': df_temp['aprobadas'].sum() if 'aprobadas' in df_temp.columns else 0,
                    'total_canceladas': df_temp['canceladas'].sum() if 'canceladas' in df_temp.columns else 0,
                    'total_preventa': df_temp['preventa'].sum() if 'preventa' in df_temp.columns else 0,
                    'total_pendientes': df_temp['pendientes'].sum() if 'pendientes' in df_temp.columns else 0,
                    'promedio_aprobadas_esperado': round(df_temp['aprobadas'].mean(), 1) if 'aprobadas' in df_temp.columns else 0,
                }
                total_v = totales_v['total_ventas']
                total_ap = totales_v['total_aprobadas']
                totales_v['tasa_aprobacion_global'] = round((total_ap / total_v * 100), 1) if total_v > 0 else 0
            
            # Título según filtro
            if tipo_filtro == "👤 Por Agente" and agente_seleccionado:
                st.markdown(f"#### 👤 Ventas de: **{agente_seleccionado}**")
            elif tipo_filtro == "🏢 Por Equipo" and equipo_seleccionado:
                st.markdown(f"#### 🏢 Ventas del Equipo: **{equipo_seleccionado}** ({len(ventas_filtradas)} vendedores)")
            
            # KPIs
            st.markdown("#### 📊 Métricas")
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%); 
                            padding: 15px; border-radius: 12px; text-align: center; color: white;'>
                    <p style='margin: 0; font-size: 0.8rem;'>💼 TOTAL VENTAS</p>
                    <p style='margin: 5px 0 0 0; font-size: 1.8rem; font-weight: bold;'>{totales_v.get('total_ventas', 0):,}</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #10B981 0%, #059669 100%); 
                            padding: 15px; border-radius: 12px; text-align: center; color: white;'>
                    <p style='margin: 0; font-size: 0.8rem;'>✅ APROBADAS</p>
                    <p style='margin: 5px 0 0 0; font-size: 1.8rem; font-weight: bold;'>{totales_v.get('total_aprobadas', 0):,}</p>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%); 
                            padding: 15px; border-radius: 12px; text-align: center; color: white;'>
                    <p style='margin: 0; font-size: 0.8rem;'>❌ CANCELADAS</p>
                    <p style='margin: 5px 0 0 0; font-size: 1.8rem; font-weight: bold;'>{totales_v.get('total_canceladas', 0):,}</p>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                tasa = totales_v.get('tasa_aprobacion_global', 0)
                color_tasa = '#10B981' if tasa >= 60 else '#F59E0B' if tasa >= 40 else '#EF4444'
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, {color_tasa} 0%, {color_tasa}CC 100%); 
                            padding: 15px; border-radius: 12px; text-align: center; color: white;'>
                    <p style='margin: 0; font-size: 0.8rem;'>📈 TASA APROB.</p>
                    <p style='margin: 5px 0 0 0; font-size: 1.8rem; font-weight: bold;'>{tasa}%</p>
                </div>
                """, unsafe_allow_html=True)
            with col5:
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%); 
                            padding: 15px; border-radius: 12px; text-align: center; color: white;'>
                    <p style='margin: 0; font-size: 0.8rem;'>📊 PROM. ESPERADO</p>
                    <p style='margin: 5px 0 0 0; font-size: 1.8rem; font-weight: bold;'>{totales_v.get('promedio_aprobadas_esperado', 0)}</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                if len(ventas_filtradas) > 1:
                    st.markdown("#### 🏆 Top 10 Vendedores por Ventas Aprobadas")
                    df_v = pd.DataFrame(ventas_filtradas).head(10)
                else:
                    st.markdown(f"#### 📊 Desglose de Ventas - {agente_seleccionado}")
                    df_v = pd.DataFrame(ventas_filtradas)
                
                if len(df_v) > 1:
                    colores = []
                    for _, row in df_v.iterrows():
                        if row['tasa_aprobacion'] >= 70: colores.append('#10B981')
                        elif row['tasa_aprobacion'] >= 50: colores.append('#F59E0B')
                        else: colores.append('#EF4444')
                    
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=df_v['vendedor'],
                        y=df_v['aprobadas'],
                        marker_color=colores,
                        text=df_v['aprobadas'],
                        textposition='outside'
                    ))
                    prom = totales_v.get('promedio_aprobadas_esperado', 0)
                    fig.add_hline(y=prom, line_dash="dash", line_color="#8B5CF6", annotation_text=f"Promedio: {prom}")
                    fig.update_layout(height=400, xaxis_tickangle=-45, yaxis_title="Ventas Aprobadas")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    # Agente individual - mostrar estados
                    agente_data = ventas_filtradas[0]
                    estados = {
                        'Aprobadas': agente_data.get('aprobadas', 0),
                        'Canceladas': agente_data.get('canceladas', 0),
                        'Preventa': agente_data.get('preventa', 0),
                        'Pendientes': agente_data.get('pendientes', 0)
                    }
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=list(estados.keys()),
                        y=list(estados.values()),
                        marker_color=['#10B981', '#EF4444', '#F59E0B', '#6B7280'],
                        text=list(estados.values()),
                        textposition='outside'
                    ))
                    fig.update_layout(height=400, yaxis_title="Cantidad")
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 📊 Distribución de Estados")
                fig_pie = go.Figure(data=[go.Pie(
                    labels=['Aprobadas', 'Canceladas', 'Preventa', 'Pendientes'],
                    values=[totales_v.get('total_aprobadas', 0), totales_v.get('total_canceladas', 0),
                            totales_v.get('total_preventa', 0), totales_v.get('total_pendientes', 0)],
                    hole=0.4,
                    marker_colors=['#10B981', '#EF4444', '#F59E0B', '#6B7280']
                )])
                fig_pie.update_layout(height=400)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            st.markdown("---")
            
            # Tabla por vendedor
            st.markdown("#### 📋 Detalle por Vendedor")
            
            df_ventas = pd.DataFrame(ventas_filtradas)
            cols_disponibles = [c for c in ['vendedor', 'supervisor', 'total_ventas', 'aprobadas', 'canceladas', 
                                           'tasa_aprobacion', 'dif_vs_promedio', 'dif_aprobadas_vs_esperado', 'estado'] if c in df_ventas.columns]
            df_ventas_display = df_ventas[cols_disponibles].copy()
            cols_names = ['Vendedor', 'Supervisor', 'Total', 'Aprobadas', 'Canceladas', 
                         'Tasa %', 'Dif vs Prom', 'Dif Aprob vs Esp', 'Estado'][:len(cols_disponibles)]
            df_ventas_display.columns = cols_names
            
            def color_tasa_tabla(val):
                if val >= 70: return 'background-color: #D1FAE5; color: #065F46;'
                elif val >= 50: return 'background-color: #FEF3C7; color: #92400E;'
                else: return 'background-color: #FEE2E2; color: #991B1B;'
            
            if 'Tasa %' in df_ventas_display.columns:
                styled = df_ventas_display.style.applymap(color_tasa_tabla, subset=['Tasa %'])
                st.dataframe(styled, use_container_width=True, height=400)
            else:
                st.dataframe(df_ventas_display, use_container_width=True, height=400)
    
    # =========================================================================
    # TAB 3: LLAMADAS
    # =========================================================================
    with tab3:
        st.markdown("### 📞 Reporte de Llamadas")
        
        llamadas_filtradas = filtrar_datos(llamadas_vendedor, campo_equipo='equipo', campo_vendedor='vendedor')
        totales_ll = datos_llamadas.get('totales', {})
        
        if not llamadas_filtradas:
            st.info("No hay datos de llamadas disponibles para el filtro seleccionado")
        else:
            # Recalcular totales si hay filtro
            if tipo_filtro != "🌐 General":
                df_temp = pd.DataFrame(llamadas_filtradas)
                total = df_temp['total_llamadas'].sum() if 'total_llamadas' in df_temp.columns else 0
                cortadas = df_temp['cortadas'].sum() if 'cortadas' in df_temp.columns else 0
                sup_1 = df_temp['supera_1min'].sum() if 'supera_1min' in df_temp.columns else 0
                sup_5 = df_temp['supera_5min'].sum() if 'supera_5min' in df_temp.columns else 0
                capta = df_temp['capta_atencion'].sum() if 'capta_atencion' in df_temp.columns else 0
                
                # TMO promedio
                if 'tmo_seg' in df_temp.columns:
                    tmo_prom = df_temp['tmo_seg'].mean()
                    h, m, s = int(tmo_prom // 3600), int((tmo_prom % 3600) // 60), int(tmo_prom % 60)
                    tmo_fmt = f"{h:02d}:{m:02d}:{s:02d}"
                else:
                    tmo_fmt = '00:00:00'
                
                totales_ll = {
                    'total_llamadas': total,
                    'total_cortadas': cortadas,
                    'supera_1min': sup_1,
                    'supera_5min': sup_5,
                    'capta_atencion': capta,
                    'tmo_global_fmt': tmo_fmt,
                    'pct_cortadas': round((cortadas / total * 100), 1) if total > 0 else 0,
                    'pct_supera_1min': round((sup_1 / total * 100), 1) if total > 0 else 0,
                    'pct_supera_5min': round((sup_5 / total * 100), 1) if total > 0 else 0,
                    'pct_capta_atencion': round((capta / total * 100), 1) if total > 0 else 0,
                    'menos_30seg': total - sup_1 - cortadas  # Aproximación
                }
            
            # Título según filtro
            if tipo_filtro == "👤 Por Agente" and agente_seleccionado:
                st.markdown(f"#### 👤 Llamadas de: **{agente_seleccionado}**")
            elif tipo_filtro == "🏢 Por Equipo" and equipo_seleccionado:
                st.markdown(f"#### 🏢 Llamadas del Equipo: **{equipo_seleccionado}** ({len(llamadas_filtradas)} agentes)")
            
            # KPIs
            st.markdown("#### 📊 Métricas")
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            with col1:
                st.metric("📞 Total Llamadas", f"{totales_ll.get('total_llamadas', 0):,}")
            with col2:
                st.metric("⏱️ TMO", totales_ll.get('tmo_global_fmt', '00:00:00'))
            with col3:
                st.metric("❌ Cortadas", f"{totales_ll.get('total_cortadas', 0):,} ({totales_ll.get('pct_cortadas', 0)}%)")
            with col4:
                st.metric("⏰ >1 min", f"{totales_ll.get('supera_1min', 0):,} ({totales_ll.get('pct_supera_1min', 0)}%)")
            with col5:
                st.metric("⏰ >5 min", f"{totales_ll.get('supera_5min', 0):,} ({totales_ll.get('pct_supera_5min', 0)}%)")
            with col6:
                st.metric("🎯 Capta Atención", f"{totales_ll.get('capta_atencion', 0):,} ({totales_ll.get('pct_capta_atencion', 0)}%)")
            
            st.markdown("---")
            
            # Gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📊 Distribución de Llamadas por Duración")
                total = totales_ll.get('total_llamadas', 1)
                menos_30 = totales_ll.get('menos_30seg', 0)
                sup_1 = totales_ll.get('supera_1min', 0)
                sup_5 = totales_ll.get('supera_5min', 0)
                entre_30_60 = max(0, total - menos_30 - sup_1)
                entre_1_5 = max(0, sup_1 - sup_5)
                
                categorias = ['< 30 seg', '30s - 1min', '1 - 5 min', '> 5 min']
                valores = [menos_30, entre_30_60, entre_1_5, sup_5]
                colores = ['#EF4444', '#F59E0B', '#10B981', '#3B82F6']
                
                fig_bar = go.Figure()
                fig_bar.add_trace(go.Bar(x=categorias, y=valores, marker_color=colores, text=valores, textposition='outside'))
                fig_bar.update_layout(height=350, yaxis_title="Cantidad")
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                st.markdown("#### 🎯 Capta de Atención (>1min y no cortadas)")
                fig_pie = go.Figure(data=[go.Pie(
                    labels=['Capta Atención', 'No Capta'],
                    values=[totales_ll.get('capta_atencion', 0), total - totales_ll.get('capta_atencion', 0)],
                    hole=0.5,
                    marker_colors=['#10B981', '#E5E7EB']
                )])
                fig_pie.update_layout(height=350)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            st.markdown("---")
            
            # Gráfico de agentes
            if len(llamadas_filtradas) > 1:
                st.markdown("#### 🏆 Top 10 Agentes por Cantidad de Llamadas")
                df_ll = pd.DataFrame(llamadas_filtradas).head(10)
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=df_ll['vendedor'],
                    y=df_ll['total_llamadas'],
                    marker_color='#3B82F6',
                    text=df_ll['total_llamadas'],
                    textposition='outside',
                    name='Total Llamadas'
                ))
                fig.add_trace(go.Bar(
                    x=df_ll['vendedor'],
                    y=df_ll['capta_atencion'],
                    marker_color='#10B981',
                    text=df_ll['capta_atencion'],
                    textposition='outside',
                    name='Capta Atención'
                ))
                fig.update_layout(barmode='group', height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Tabla detallada
            st.markdown("#### 📋 Detalle por Vendedor/Agente")
            
            df_llamadas = pd.DataFrame(llamadas_filtradas)
            cols_disponibles = [c for c in ['vendedor', 'equipo', 'total_llamadas', 'tmo_fmt', 'cortadas', 
                                         'pct_cortadas', 'supera_1min', 'supera_5min', 'capta_atencion', 
                                         'pct_capta_atencion', 'estado'] if c in df_llamadas.columns]
            df_ll_display = df_llamadas[cols_disponibles].copy()
            cols_names = ['Vendedor', 'Equipo', 'Total', 'TMO', 'Cortadas', '% Cortadas',
                         '>1min', '>5min', 'Capta', '% Capta', 'Estado'][:len(cols_disponibles)]
            df_ll_display.columns = cols_names
            
            def color_capta(val):
                if val >= 50: return 'background-color: #D1FAE5; color: #065F46;'
                elif val >= 35: return 'background-color: #FEF3C7; color: #92400E;'
                else: return 'background-color: #FEE2E2; color: #991B1B;'
            
            if '% Capta' in df_ll_display.columns:
                styled = df_ll_display.style.applymap(color_capta, subset=['% Capta'])
                st.dataframe(styled, use_container_width=True, height=400)
            else:
                st.dataframe(df_ll_display, use_container_width=True, height=400)


def pagina_resumen_corporativo(datos):
    """Página de Resumen Corporativo - Vista consolidada de equipos y vendedores"""
    st.markdown('<div class="main-header">📊 COMMAND · Resumen Corporativo</div>', unsafe_allow_html=True)
    
    # Subtítulo
    st.markdown("""
    <div style='background: #F0F9FF; padding: 12px 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #0EA5E9;'>
        <p style='margin: 0; color: #0C4A6E; font-size: 0.95rem;'>
            <strong>Vista Consolidada de Rendimiento</strong> · Resumen ejecutivo de equipos y vendedores con sus planes de acción
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Obtener permisos del usuario actual
    permisos = obtener_permisos_usuario()
    
    # Vendedores no tienen acceso a esta página
    if permisos['rol'] == 'vendedor':
        st.warning("⚠️ Esta sección está disponible solo para supervisores y administradores.")
        return
    
    # Función auxiliar para normalizar nombres de archivo
    def normalizar_nombre_archivo(nombre):
        """Normaliza el nombre del equipo para buscar el archivo de coaching"""
        import unicodedata
        # Eliminar acentos
        nombre_sin_acentos = ''.join(
            c for c in unicodedata.normalize('NFD', nombre)
            if unicodedata.category(c) != 'Mn'
        )
        # Reemplazar espacios y convertir a mayúsculas
        return nombre_sin_acentos.replace(" ", "_").upper()
    
    # Cargar datos necesarios
    listado_vendedores, equipos_vendedores = cargar_listado_vendedores()
    coaching_data = datos.get('coaching', {})
    
    # Selector de tipo de resumen
    st.markdown("### 🎯 Selecciona el Tipo de Resumen")
    
    col1, col2 = st.columns(2)
    with col1:
        tipo_resumen = st.radio(
            "Tipo de Análisis:",
            ["👥 Resumen de Equipo", "👤 Resumen de Vendedor"],
            key="tipo_resumen_corporativo"
        )
    
    st.markdown("--- ")
    # =========================================================================
    # RESUMEN DE EQUIPO
    # =========================================================================
    if tipo_resumen == "👥 Resumen de Equipo":
        st.markdown("### 👥 Resumen de Equipo")
        
        # Obtener lista de equipos disponibles
        equipos_disponibles = [e for e in equipos_vendedores.keys() if e and e != "nan" and e != "Sin Equipo"]
        equipos_disponibles = sorted(equipos_disponibles)
        
        # Restricción por rol
        if permisos['rol'] == 'supervisor' and permisos['equipos_permitidos']:
            equipo_supervisor = permisos['equipos_permitidos'][0]
            if equipo_supervisor in equipos_disponibles:
                equipos_disponibles = [equipo_supervisor]
            else:
                st.warning(f"⚠️ No se encontraron datos para el equipo: {equipo_supervisor}")
                return
        
        if not equipos_disponibles:
            st.warning("⚠️ No se encontraron equipos configurados.")
            return
        
        equipo_seleccionado = st.selectbox(
            "Selecciona un Equipo:",
            equipos_disponibles,
            key="equipo_resumen_corp"
        )
        
        if equipo_seleccionado:
            # Normalizar nombre del equipo para el archivo
            nombre_archivo = normalizar_nombre_archivo(equipo_seleccionado)
            ruta_coaching = f"reportes/coaching_equipos/coaching_{nombre_archivo}.json"
            
            if os.path.exists(ruta_coaching):
                try:
                    coaching_equipo_data = cargar_coaching_equipo(ruta_coaching)
                    
                    # Header del equipo
                    vendedores_equipo = equipos_vendedores.get(equipo_seleccionado, [])
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #1E3A5F 0%, #3B82F6 100%); 
                                padding: 20px; border-radius: 15px; margin: 20px 0; color: white;
                                box-shadow: 0 4px 15px rgba(30, 58, 95, 0.3);'>
                        <h3 style='margin:0; color: #FFFFFF;'>📊 Equipo: {equipo_seleccionado}</h3>
                        <p style='margin: 10px 0 0 0; color: #E0E7FF;'>
                            <strong>{len(vendedores_equipo)}</strong> vendedores en este equipo
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Métricas principales
                    metricas = (coaching_equipo_data or {}).get('metricas', {})
                    coaching_ia = (coaching_equipo_data or {}).get('coaching_ia', {})
                    comparativa = (coaching_equipo_data or {}).get('comparativa', {})
                    
                    # Métricas clave en columnas
                    st.markdown("#### 📈 Indicadores Principales")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        puntaje_ia = comparativa.get('puntaje_ia', {}).get('equipo', 0)
                        st.metric("⭐ Puntaje", f"{puntaje_ia:.1f}")
                    
                    with col2:
                        conversion = comparativa.get('conversion', {}).get('equipo', 0)
                        st.metric("💰 Conversión", f"{conversion:.1f}%")
                    
                    with col3:
                        fibra = comparativa.get('fibra', {}).get('equipo', 0)
                        st.metric("📡 Fibra", f"{fibra:.1f}%")
                    
                    with col4:
                        ranking = comparativa.get('puntaje_ia', {}).get('ranking', 'N/A')
                        st.metric("🏆 Ranking", ranking)
                    
                    st.markdown("---")
                    
                    # Gráficos de criterios de evaluación
                    evaluaciones = metricas.get('evaluaciones', {})
                    criterios = evaluaciones.get('criterios', {})
                    
                    if criterios:
                        st.markdown("#### 📊 Criterios de Evaluación (Promedio)")
                        
                        # Preparar datos para gráfico de barras usando constante global
                        nombres = [CRITERIOS_NOMBRES.get(k, k) for k in criterios.keys()]
                        valores = list(criterios.values())
                        
                        # Crear gráfico de barras horizontal con colores por valor
                        fig_bar = px.bar(
                            y=nombres,
                            x=valores,
                            orientation='h',
                            labels={'y': 'Criterio', 'x': 'Puntaje'},
                            color=valores,
                            color_continuous_scale=[[0, '#EF4444'], [0.4, '#F59E0B'], [0.6, '#3B82F6'], [1, '#10B981']],
                            text=valores
                        )
                        fig_bar.update_traces(
                            texttemplate='%{text:.1f}',
                            textposition='outside',
                            textfont_size=12,
                            textfont=dict(color="#000000")
                        )

                        fig_bar.update_layout(
                            height=450,
                            showlegend=False,
                            paper_bgcolor='#FFFFFF',
                            plot_bgcolor='#FAFBFC',
                            yaxis={'categoryorder': 'total ascending'},
                            xaxis={'range': [0, 100]},
                            coloraxis_showscale=False,
                            margin=dict(l=10, r=60, t=30, b=30),
                            font=dict(color="#000000")
                        )

                        fig_bar.update_xaxes(
                            tickfont=dict(color="#000000"),
                            title=dict(font=dict(color="#000000"))
                        )

                        fig_bar.update_yaxes(
                            tickfont=dict(color="#000000"),
                            title=dict(font=dict(color="#000000"))
                        )

                        fig_bar.add_vline(
                            x=80,
                            line_dash="dot",
                            line_color="#10B981",
                            annotation_text="Meta: 80",
                            annotation_font_color="#000000"
                        )

                        st.plotly_chart(fig_bar, use_container_width=True)
                    
                    st.markdown("---")
                    
                    # Diagnóstico del equipo
                    if coaching_ia:
                        diagnostico = coaching_ia.get('diagnostico', {})
                        if diagnostico:
                            st.markdown("#### 🔍 Diagnóstico del Equipo")
                            
                            col_d1, col_d2, col_d3, col_d4 = st.columns(4)
                            with col_d1:
                                nivel = diagnostico.get('nivel_rendimiento', 'N/A')
                                st.metric("📊 Nivel", nivel)
                            with col_d2:
                                puntaje = diagnostico.get('puntaje_equipo', 0)
                                st.metric("⭐ Puntaje", f"{puntaje:.1f}")
                            with col_d3:
                                posicion = diagnostico.get('posicion_ranking', 'N/A')
                                st.metric("🏆 Posición", posicion)
                            with col_d4:
                                tendencia = diagnostico.get('tendencia', 'N/A')
                                st.metric("📈 Tendencia", tendencia)
                        
                        # Resumen ejecutivo
                        resumen = coaching_ia.get('resumen_ejecutivo', '')
                        if resumen:
                            st.markdown("#### 📋 Resumen Ejecutivo")
                            st.markdown(f"""
                            <div style='background: #F8FAFC; padding: 15px; border-radius: 8px; border-left: 4px solid #3B82F6;'>
                                <p style='margin: 0; color: #1E293B; line-height: 1.6;'>{resumen}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("---")
                        
                        # Fortalezas y Áreas de Mejora
                        col_fm1, col_fm2 = st.columns(2)

                        # =========================
                        # Obtener datos
                        # =========================
                        fortalezas = coaching_ia.get('fortalezas_equipo', [])
                        mejoras = coaching_ia.get('areas_mejora_prioritarias', [])

                        # =========================
                        # Normalizar áreas de fortalezas (lower + strip)
                        # =========================
                        areas_fortalezas = {
                            f.get("area", "").strip().lower()
                            for f in fortalezas
                            if f.get("area")
                        }

                        # =========================
                        # Filtrar mejoras que NO estén en fortalezas
                        # =========================
                        mejoras_filtradas = [
                            m for m in mejoras
                            if m.get("area", "").strip().lower() not in areas_fortalezas
                        ]

                        with col_fm1:
                            st.markdown("#### 💪 Fortalezas del Equipo")

                            for fort in fortalezas:
                                st.markdown(f"""
                                <div style='background: #ECFDF5; padding: 12px; border-radius: 8px; margin: 8px 0; border-left: 4px solid #10B981;'>
                                    <strong style='color: #065F46;'>{fort.get('area', 'N/A')}</strong>
                                    <p style='margin: 5px 0; color: #047857; font-size: 0.9rem;'>{fort.get('evidencia', '')}</p>
                                    <p style='margin: 0; color: #064E3B; font-size: 0.85rem;'><em>Impacto: {fort.get('impacto', '')}</em></p>
                                </div>
                                """, unsafe_allow_html=True)

                        with col_fm2:
                            st.markdown("#### 🎯 Áreas de Mejora Prioritarias")

                            for mejora in mejoras_filtradas:
                                st.markdown(f"""
                                <div style='background: #FEF3C7; padding: 12px; border-radius: 8px; margin: 8px 0; border-left: 4px solid #F59E0B;'>
                                    <strong style='color: #92400E;'>{mejora.get('area', 'N/A')}</strong>
                                    <p style='margin: 5px 0; color: #B45309; font-size: 0.9rem;'>{mejora.get('situacion_actual', '')}</p>
                                    <p style='margin: 0; color: #78350F; font-size: 0.85rem;'><strong>Meta:</strong> {mejora.get('meta', '')}</p>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        st.markdown("---")
                        
                        # Plan de Acción del Equipo
                        st.markdown("#### 📝 Plan de Acción del Equipo- EN PROCESO")
                        plan_accion = coaching_ia.get('plan_accion_equipo', [])
                        
                        if plan_accion:
                            for i, accion in enumerate(plan_accion, 1):
                                prioridad = accion.get('prioridad', 0)
                                try:
                                    pnum = int(prioridad)
                                except Exception:
                                    pnum = 2
                                color_prioridad = '#E74C3C' if pnum == 1 else '#F39C12' if pnum == 2 else '#3B82F6'
                                bg_prioridad = '#FFF1F0' if pnum == 1 else '#FFFBEB' if pnum == 2 else '#EFF6FF'
                                
                                html = f"""<details style='border-radius:8px; overflow:hidden; margin: 8px 0; border: 1px solid rgba(0,0,0,0.04);'>
<summary style='list-style:none; display:flex; align-items:center; gap:12px; padding:10px 12px; cursor:pointer; background: {bg_prioridad}; border-left:4px solid {color_prioridad};'>
<span style='background:{color_prioridad}; color:white; padding:4px 10px; border-radius:12px; font-weight:700; font-size:0.85rem;'>P{pnum}</span>
<strong style="color: #1E293B;">Acción #{i}: {accion.get('accion', 'N/A')}</strong>
</summary>
<div style='padding:12px; background:{bg_prioridad}; color:#475569;'>
<div style='display:flex; gap:20px; margin-bottom:8px;'>
<div style='flex:1;'>
<strong>Responsable:</strong> {accion.get('responsable', 'N/A')}<br>
<strong>Plazo:</strong> {accion.get('plazo', 'N/A')}
</div>
<div style='flex:1;'>
<strong>Indicador de Éxito:</strong> {accion.get('indicador_exito', 'N/A')}<br>
<strong>Recursos Necesarios:</strong> {accion.get('recursos_necesarios', 'N/A')}
</div>
</div>
</div>
</details>"""
                                st.markdown(html, unsafe_allow_html=True)
                        else:
                            st.info("No hay plan de acción registrado para este equipo.")
                    
                except Exception as e:
                    st.error(f"Error al cargar datos del equipo: {str(e)}")
            else:
                st.warning(f"⚠️ No se encontraron datos de coaching para el equipo: {equipo_seleccionado}")
    
    # =========================================================================
    # RESUMEN DE VENDEDOR
    # =========================================================================
    else:
        st.markdown("### 👤 Resumen de Vendedor")
        
        # Verificar si hay datos de coaching
        if not coaching_data:
            st.warning("⚠️ No hay datos de coaching disponibles para vendedores.")
            return
        
        # Obtener lista de vendedores
        vendedores_disponibles = sorted(list(coaching_data.keys()))
        
        # Aplicar filtro por permisos
        if permisos['rol'] == 'supervisor' and permisos['equipos_permitidos']:
            equipo_supervisor = permisos['equipos_permitidos'][0]
            vendedores_equipo = equipos_vendedores.get(equipo_supervisor, [])
            # Filtrar vendedores del equipo del supervisor - usar matching más preciso
            vendedores_filtrados = []
            for v in vendedores_disponibles:
                v_lower = v.lower().strip()
                # Buscar coincidencia exacta o por nombre completo
                for ve in vendedores_equipo:
                    ve_lower = ve.lower().strip()
                    # Coincidencia si el nombre del vendedor está en la lista del equipo
                    if v_lower == ve_lower or ve_lower in v_lower:
                        vendedores_filtrados.append(v)
                        break
            vendedores_disponibles = vendedores_filtrados
        
        if not vendedores_disponibles:
            st.warning("⚠️ No se encontraron vendedores con datos de coaching.")
            return
        
        vendedor_seleccionado = st.selectbox(
            "Selecciona un Vendedor:",
            vendedores_disponibles,
            key="vendedor_resumen_corp"
        )
        
        if vendedor_seleccionado and vendedor_seleccionado in coaching_data:
            vendedor_data = coaching_data[vendedor_seleccionado]
            
            # Header del vendedor
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #1E3A5F 0%, #3B82F6 100%); 
                        padding: 20px; border-radius: 15px; margin: 20px 0; color: white;
                        box-shadow: 0 4px 15px rgba(30, 58, 95, 0.3);'>
                <h3 style='margin:0; color: #FFFFFF;'>👤 Vendedor: {vendedor_seleccionado}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Métricas principales del vendedor
            metricas = vendedor_data.get('metricas', {})
            comparativa = vendedor_data.get('comparativa', {})
            
            st.markdown("#### 📈 Indicadores Principales")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                puntaje_ia = comparativa.get('puntaje_ia', {}).get('agente', 0)
                st.metric("⭐ Puntaje", f"{puntaje_ia:.1f}")
            
            with col2:
                conversion = comparativa.get('conversion', {}).get('agente', 0)
                st.metric("💰 Conversión", f"{conversion:.1f}%")
            
            with col3:
                fibra = comparativa.get('fibra', {}).get('agente', 0)
                st.metric("📡 Fibra", f"{fibra:.1f}%")
            
            with col4:
                evaluaciones = metricas.get('evaluaciones', {})
                total_eval = evaluaciones.get('total_evaluadas', 0)
                st.metric("📞 Evaluaciones", total_eval)
            
            st.markdown("---")
            
            # Gráficos del vendedor
            criterios = evaluaciones.get('criterios', {})
            
            if criterios:
                st.markdown("#### 📊 Criterios de Evaluación")
                
                # Gráfico de barras horizontal usando constante global
                nombres = [CRITERIOS_NOMBRES.get(k, k) for k in criterios.keys()]
                valores = list(criterios.values())
                
                fig_bar = px.bar(
                    y=nombres,
                    x=valores,
                    orientation='h',
                    labels={'y': 'Criterio', 'x': 'Puntaje'},
                    color=valores,
                    color_continuous_scale=[[0, '#EF4444'], [0.4, '#F59E0B'], [0.6, '#3B82F6'], [1, '#10B981']],
                    text=valores
                )
                fig_bar.update_traces(
                    texttemplate='%{text:.1f}',
                    textposition='outside',
                    textfont_size=12,
                    textfont=dict(color="#000000")
                )

                fig_bar.update_layout(
                    height=450,
                    showlegend=False,
                    paper_bgcolor='#FFFFFF',
                    plot_bgcolor='#FAFBFC',
                    yaxis={'categoryorder': 'total ascending'},
                    xaxis={'range': [0, 100]},
                    coloraxis_showscale=False,
                    margin=dict(l=10, r=60, t=30, b=30),
                    font=dict(color="#000000")
                )

                fig_bar.update_xaxes(
                    tickfont=dict(color="#000000"),
                    title=dict(font=dict(color="#000000"))
                )

                fig_bar.update_yaxes(
                    tickfont=dict(color="#000000"),
                    title=dict(font=dict(color="#000000"))
                )

                fig_bar.add_vline(
                    x=80,
                    line_dash="dot",
                    line_color="#10B981",
                    annotation_text="Meta: 80",
                    annotation_font_color="#000000"
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            st.markdown("---")
            
            # Análisis de Coaching del vendedor (texto)
            analisis_coaching = vendedor_data.get('analisis_coaching', '')
            
            if analisis_coaching:
                st.markdown("#### 📋 Análisis y Plan de Acción")
                
                # Mostrar el análisis completo en un expander
                with st.expander("**Ver Análisis Completo de Coaching**", expanded=True):
                    st.markdown(analisis_coaching)
            else:
                st.info("No hay análisis de coaching disponible para este vendedor.")


def main():
    """Función principal del dashboard"""
    
    # ==========================================================================
    # VERIFICACIÓN DE AUTENTICACIÓN
    # ==========================================================================
    if 'autenticado' not in st.session_state or not st.session_state['autenticado']:
        mostrar_login()
        return
    
    # Obtener datos del usuario autenticado
    datos_usuario = st.session_state.get('datos_usuario', {})
    nombre_usuario = datos_usuario.get('nombre', 'Usuario')
    rol_usuario = datos_usuario.get('rol', 'vendedor')
    
    # Cargar datos: preferir pre-carga en background iniciada en el login
    if st.session_state.get('datos_preload_started'):
        # Si la pre-carga ya completó, usamos los datos ya cargados
        if _DATOS_PRELOAD is not None:
            datos = _DATOS_PRELOAD
        else:
            # Pre-carga en curso: esperar silenciosamente hasta que termine
            import time
            while _DATOS_LOADING:
                time.sleep(0.1)
            datos = _DATOS_PRELOAD or cargar_datos()
    else:
        # No hubo pre-carga: cargar de forma síncrona (comportamiento por defecto)
        with st.spinner('Cargando datos...'):
            datos = cargar_datos()
    
    transcripciones = datos.get('transcripciones', [])
    if transcripciones:
        df = crear_df_llamadas(transcripciones)
    else:
        df_eval = datos.get('evaluaciones_gemini_df')
        if df_eval is None:
            df_eval = datos.get('evaluaciones')
        df = crear_df_llamadas_desde_evaluaciones(df_eval)
        if df.empty:
            st.error("No se encontraron transcripciones procesadas ni evaluaciones. Verifica 'reportes/evaluaciones_gemini.csv'.")
            return
        st.info("No se encontraron JSON de transcripciones. Usando solo 'reportes/evaluaciones_gemini.csv'.")
    
    # Crear DataFrame de llamadas
    
    
    # Sidebar - Logo COMMAND y Usuario
    st.sidebar.markdown("""
    <div class="command-logo-container">
        <div class="command-title">📈 COMMAND</div>
        <div class="command-subtitle">Sistema de Rendimiento Comercial</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Info del usuario logueado
    st.sidebar.markdown(f"""
    <div style='background: linear-gradient(135deg, #1E3A5F 0%, #3B82F6 100%); 
                padding: 12px; border-radius: 8px; margin: 10px 0;'>
        <p style='color: white; margin: 0; font-size: 0.9rem;'>
            👤 <strong>{nombre_usuario}</strong><br>
            <small style='opacity: 0.8;'>Rol: {rol_usuario.title()}</small>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Botón cerrar sesión
    if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
        cerrar_sesion()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📊 Panel de Control")
    
    # Obtener usuario actual y permisos para el menú
    usuario_actual = st.session_state.get('usuario', '').lower()
    datos_usuario = st.session_state.get('datos_usuario', {})
    rol_usuario = datos_usuario.get('rol', 'vendedor')
    es_admin_calidad = usuario_actual in ['matias', 'calidad']
    
    # Menú según rol del usuario
    if rol_usuario == 'vendedor':
        # Vendedores: Solo ven módulos relevantes para ellos
        paginas = {
            "📱 Mis Productos Ofrecidos": "planes",
            "⚠️ Mis Reclamos": "quejas",
            "🤖 Mi Evaluación": "gemini",
            "🎯 Mi Plan de Mejora": "coaching",
        }
    elif rol_usuario == 'supervisor':
        # Supervisores: Ven módulos de su equipo
        paginas = {
            "📱 Productos del Equipo": "planes",
            "⚠️ Reclamos del Equipo": "quejas",
            "🤖 Evaluaciones del Equipo": "gemini",
            "🎯 Planes de Mejora": "coaching",
            "👥 Análisis de Mi Equipo": "equipos",
            "📊 Resumen Corporativo": "resumen_corporativo",
            "📊 Métricas de Calidad": "metricas_calidad"
        }
    else:
        # Admin: Acceso completo
        paginas = {
            "📱 Análisis de Productos": "planes",
            # "⚠️ Gestión de Reclamos": "quejas",
            "🤖 Evaluación Automatizada": "gemini",
            "🎯 Planes de Mejora": "coaching",
            "👥 Análisis de Equipos": "equipos",
            "📊 Resumen Corporativo": "resumen_corporativo",
            "📊 Métricas de Calidad": "metricas_calidad"
        }
        # Agregar Indicadores de Calidad solo para admin/calidad
        if es_admin_calidad:
            paginas["📞 Indicadores de Calidad (Admin)"] = "calidad"
        # Agregar Comparativa de Períodos solo para admin/supervisor
        paginas["📅 Comparativa de Períodos"] = "comparativa"
    seleccion = st.sidebar.radio("Módulos disponibles:", list(paginas.keys()))
    
    # =========================================================================
    # FILTROS DE FECHA EN SIDEBAR
    # =========================================================================
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📅 Filtro por Fechas")
    
    # Obtener rango de fechas disponibles desde evaluaciones_gemini_df
    fecha_min_disp = None
    fecha_max_disp = None
    
    if 'evaluaciones_gemini_df' in datos and datos['evaluaciones_gemini_df'] is not None:
        df_eval = datos['evaluaciones_gemini_df']
        if 'fecha_llamada' in df_eval.columns:
            fechas_validas = df_eval['fecha_llamada'].dropna()
            if len(fechas_validas) > 0:
                fecha_min_disp = fechas_validas.min().date() if hasattr(fechas_validas.min(), 'date') else fechas_validas.min()
                fecha_max_disp = fechas_validas.max().date() if hasattr(fechas_validas.max(), 'date') else fechas_validas.max()
    
    # Inicializar filtros de fecha en session_state
    if 'filtro_fecha_inicio' not in st.session_state:
        st.session_state['filtro_fecha_inicio'] = fecha_min_disp
    if 'filtro_fecha_fin' not in st.session_state:
        st.session_state['filtro_fecha_fin'] = fecha_max_disp
    
    if fecha_min_disp and fecha_max_disp:
        # Selector de período predefinido
        periodos_predefinidos = {
            "📆 Todo el período": None,
            "📅 Semana 12-16 Enero": (datetime(2026, 1, 12).date(), datetime(2026, 1, 16).date()),
            "📅 Semana 19-24 Enero": (datetime(2026, 1, 19).date(), datetime(2026, 1, 24).date()),
            "🔧 Personalizado": "custom"
        }
        
        periodo_sel = st.sidebar.selectbox(
            "Período a analizar:",
            list(periodos_predefinidos.keys()),
            key="periodo_predefinido"
        )
        
        if periodo_sel == "📆 Todo el período":
            st.session_state['filtro_fecha_inicio'] = fecha_min_disp
            st.session_state['filtro_fecha_fin'] = fecha_max_disp
        elif periodo_sel == "🔧 Personalizado":
            col_f1, col_f2 = st.sidebar.columns(2)
            with col_f1:
                fecha_inicio = st.date_input(
                    "Desde:",
                    value=st.session_state.get('filtro_fecha_inicio', fecha_min_disp),
                    min_value=fecha_min_disp,
                    max_value=fecha_max_disp,
                    key="date_input_inicio"
                )
                st.session_state['filtro_fecha_inicio'] = fecha_inicio
            with col_f2:
                fecha_fin = st.date_input(
                    "Hasta:",
                    value=st.session_state.get('filtro_fecha_fin', fecha_max_disp),
                    min_value=fecha_min_disp,
                    max_value=fecha_max_disp,
                    key="date_input_fin"
                )
                st.session_state['filtro_fecha_fin'] = fecha_fin
        else:
            # Período predefinido
            rango = periodos_predefinidos.get(periodo_sel)
            if rango and isinstance(rango, tuple):
                st.session_state['filtro_fecha_inicio'] = rango[0]
                st.session_state['filtro_fecha_fin'] = rango[1]
        
        # Mostrar período seleccionado
        fecha_ini = st.session_state.get('filtro_fecha_inicio', fecha_min_disp)
        fecha_fin = st.session_state.get('filtro_fecha_fin', fecha_max_disp)
        if fecha_ini and fecha_fin:
            st.sidebar.markdown(f"""
            <div style='background: linear-gradient(135deg, #1E3A5F 0%, #2563EB 100%); padding: 10px 14px; border-radius: 8px; margin: 5px 0; border-left: 4px solid #60A5FA; box-shadow: 0 2px 8px rgba(0,0,0,0.2);'>
                <small style='color: #FFFFFF;'>
                    <strong style='color: #93C5FD;'>📅 Mostrando:</strong><br>
                    <span style='color: #FFFFFF; font-weight: 600;'>{fecha_ini.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}</span>
                </small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.sidebar.info("📊 Las fechas se cargarán con los datos")
    
    # Info adicional en sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📈 Indicadores Clave")
    st.sidebar.markdown(f"**Total Operaciones:** {len(df):,}")
    if 'dia' in df.columns and df['dia'].notna().any():
        fecha_min = df['dia'].dropna().min()
        fecha_max = df['dia'].dropna().max()
        st.sidebar.markdown(f"**Período:** {fecha_min} a {fecha_max}")
    st.sidebar.markdown(f"**Vendedores Activos:** {df['agente'].nunique()}")
    
    # Renderizar página seleccionada
    if paginas[seleccion] == "planes":
        pagina_planes_ofrecidos(datos, df)
    elif paginas[seleccion] == "quejas":
        pagina_quejas_no_resueltas(datos)
    elif paginas[seleccion] == "gemini":
        pagina_evaluaciones_gemini(datos)
    elif paginas[seleccion] == "coaching":
        pagina_coaching_vendedores(datos)
    elif paginas[seleccion] == "equipos":
        pagina_analisis_equipos(datos)
    elif paginas[seleccion] == "resumen_corporativo":
        pagina_resumen_corporativo(datos)
    elif paginas[seleccion] == "metricas_calidad":
        pagina_metricas_calidad()
    elif paginas[seleccion] == "calidad":
        pagina_calidad()
    elif paginas[seleccion] == "comparativa":
        pagina_comparativa_periodos(datos)
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"<small>COMMAND v2.0 · Sistema de Rendimiento Comercial<br>Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</small>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()


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


# Directorio base del script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
    'byl': {
        'password_hash': hash_password('123'),
        'nombre': 'Byl',
        'rol': 'supervisor',
        'equipo': None,
        'permisos': ['dashboard', 'coaching', 'evaluaciones', 'reportes']
    },
    'diana': {
        'password_hash': hash_password('123'),
        'nombre': 'Diana',
        'rol': 'supervisor',
        'equipo': None,
        'permisos': ['dashboard', 'coaching', 'evaluaciones', 'reportes']
    },
    'marina': {
        'password_hash': hash_password('123'),
        'nombre': 'Marina',
        'rol': 'supervisor',
        'equipo': 'MARINA MARTINEZ',
        'permisos': ['dashboard', 'coaching', 'evaluaciones', 'reportes']
    },
    'calidad': {
        'password_hash': hash_password('123'),
        'nombre': 'Calidad',
        'rol': 'supervisor',
        'equipo': None,
        'permisos': ['dashboard', 'coaching', 'evaluaciones', 'reportes', 'calidad']
    },
    'melani': {
        'password_hash': hash_password('123'),
        'nombre': 'Melani',
        'rol': 'supervisor',
        'equipo': 'MELANIE CARMONA',
        'permisos': ['dashboard', 'coaching', 'evaluaciones', 'reportes']
    },
    'josefina': {
        'password_hash': hash_password('123'),
        'nombre': 'Josefina',
        'rol': 'supervisor',
        'equipo': 'JOSEFINA ZEBALLOS',
        'permisos': ['dashboard', 'coaching', 'evaluaciones', 'reportes']
    },
    'yasmin': {
        'password_hash': hash_password('123'),
        'nombre': 'Yasmin',
        'rol': 'supervisor',
        'equipo': 'ARENAS YASMIN',
        'permisos': ['dashboard', 'coaching', 'evaluaciones', 'reportes']
    },
    'nati': {
        'password_hash': hash_password('123'),
        'nombre': 'Nati',
        'rol': 'supervisor',
        'equipo': 'NATALI SANCHE',
        'permisos': ['dashboard', 'coaching', 'evaluaciones', 'reportes']
    },
    'capacitacion': {
        'password_hash': hash_password('123'),
        'nombre': 'Capacitación',
        'rol': 'supervisor',
        'equipo': None,
        'permisos': ['dashboard', 'coaching', 'evaluaciones', 'reportes']
    },
}

def verificar_credenciales(usuario, password):
    """Verifica las credenciales del usuario"""
    usuario = usuario.lower().strip()
    if usuario in USUARIOS:
        if USUARIOS[usuario]['password_hash'] == hash_password(password):
            return True, USUARIOS[usuario]
    return False, None

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
        
        # Card del formulario
        st.markdown('<div class="login-form-card">', unsafe_allow_html=True)
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
                        st.session_state['autenticado'] = True
                        st.session_state['usuario'] = usuario.lower()
                        st.session_state['datos_usuario'] = datos_usuario
                        st.rerun()
                    else:
                        st.error("Usuario o contraseña incorrectos")
                else:
                    st.warning("Por favor complete todos los campos")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
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
            # Convertir lista a diccionario por agente (aplicando mapeo de nombres)
            datos['coaching'] = {}
            for item in coaching_list:
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
    
    if 'planes' not in datos:
        st.warning("⚠️ No hay datos de planes disponibles.")
        return
    
    planes = datos['planes']
    stats = planes.get('estadisticas', {})
    total_llamadas = planes.get('total_llamadas', 0)
    
    # =========================================================================
    # SECCIÓN 1: PLANES DE PORTA
    # =========================================================================
    st.markdown('<p class="section-header">📱 Análisis de Ofertas de Planes Móviles</p>', unsafe_allow_html=True)
    
    planes_stats = stats.get('planes', {})
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📞 Total Operaciones", f"{total_llamadas:,}")
    with col2:
        con_plan = planes_stats.get('con_plan', 0)
        pct = planes_stats.get('porcentaje_con_plan', 0)
        st.metric("✅ Oferta Realizada", f"{con_plan:,}", f"{pct:.1f}%")
    with col3:
        sin_plan = planes_stats.get('sin_plan', 0)
        pct_sin = 100 - pct if pct else 0
        st.metric("❌ Sin Oferta", f"{sin_plan:,}", f"{pct_sin:.1f}%", delta_color="inverse")
    with col4:
        # Plan más usado como primer ofrecimiento
        primer_plan_conteo = stats.get('primer_plan_conteo', {})
        if primer_plan_conteo:
            top_plan = max(primer_plan_conteo, key=primer_plan_conteo.get)
            st.metric("🥇 Plan Principal", top_plan.upper(), f"{primer_plan_conteo[top_plan]} veces")
    
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
    st.markdown('<p class="section-header">🏠 Análisis de Ofertas de Fibra Óptica</p>', unsafe_allow_html=True)
    
    fibra_stats = stats.get('fibra', {})
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ofrece = fibra_stats.get('ofrece', 0)
        pct_ofrece = fibra_stats.get('porcentaje_ofrece', 0)
        st.metric("✅ Oferta Realizada", f"{ofrece:,}", f"{pct_ofrece:.1f}%")
    with col2:
        no_ofrece = fibra_stats.get('no_ofrece', 0)
        pct_no = 100 - pct_ofrece if pct_ofrece else 0
        st.metric("❌ Sin Oferta de Fibra", f"{no_ofrece:,}", f"-{pct_no:.1f}%", delta_color="inverse")
    with col3:
        # Indicador visual
        if pct_ofrece < 30:
            st.error(f"⚠️ Solo {pct_ofrece:.1f}% ofrece Fibra - Requiere acción inmediata")
        elif pct_ofrece < 50:
            st.warning(f"⚠️ {pct_ofrece:.1f}% ofrece Fibra - Área de mejora")
        else:
            st.success(f"✅ {pct_ofrece:.1f}% ofrece Fibra - Cumplimiento adecuado")
    
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
                st.markdown("**🚨 Vendedores con Menor Oferta de Fibra:**")
                st.dataframe(df_sin_fibra, use_container_width=True, hide_index=True, height=180)
    
    st.markdown("---")
    
    # =========================================================================
    # SECCIÓN 3: PROMOCIONES
    # =========================================================================
    st.markdown('<p class="section-header">🎁 Análisis de Cumplimiento de Promociones</p>', unsafe_allow_html=True)
    
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
    st.markdown('<div class="main-header">🎯 COMMAND · Planes de Mejora y Desarrollo de Vendedores</div>', unsafe_allow_html=True)
    
    # Subtítulo corporativo
    st.markdown("""
    <div style='background: #F8FAFC; padding: 12px 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #10B981;'>
        <p style='margin: 0; color: #334155; font-size: 0.95rem;'>
            <strong>Planes de Acción Individualizados</strong> · Recomendaciones basadas en análisis de rendimiento para cada vendedor
        </p>
    </div>
    """, unsafe_allow_html=True)
    
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
                'Agente': agente,  # Ya tiene nombre real aplicado
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
    
    with tab3:
        st.markdown("### 📈 Ranking y Prioridades de Mejora")
        
        # Filtro por equipo para el ranking
        _, equipos_vendedores_ranking = cargar_listado_vendedores()
        equipos_ranking = ["Todos los Equipos"] + sorted([e for e in equipos_vendedores_ranking.keys() if e and e != "Sin Equipo"])
        if "Sin Equipo" in equipos_vendedores_ranking:
            equipos_ranking.append("Sin Equipo")
        
        equipo_filtro_ranking = st.selectbox(
            "🏢 Filtrar por Equipo",
            equipos_ranking,
            key="equipo_filtro_ranking",
            help="Selecciona un equipo para ver su ranking específico"
        )
        
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
            df_mejora['Potencial'] = (100 - df_mejora['Puntaje IA']) * (df_mejora['Evaluaciones'] / df_mejora['Evaluaciones'].max())
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
                    <div style='background: #FFFFFF; padding: 12px; border-radius: 8px; margin: 5px 0;
                                border-left: 4px solid {color}; box-shadow: 0 2px 6px rgba(0,0,0,0.08);'>
                        <strong style='color: #1E293B;'>{i}. {row['Agente']}</strong><br>
                        <small style='color: #475569;'>Puntaje: {row['Puntaje IA']:.1f} | Críticas: {row['Tasa_Criticas']:.1f}% | Eval: {row['Evaluaciones']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### 🟢 Top Performers")
                
                top_performers = df_ranking.sort_values('Puntaje IA', ascending=False).head(10)
                
                for i, (_, row) in enumerate(top_performers.iterrows(), 1):
                    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                    st.markdown(f"""
                    <div style='background: #FFFFFF; padding: 12px; border-radius: 8px; margin: 5px 0;
                                border-left: 4px solid #10B981; box-shadow: 0 2px 6px rgba(0,0,0,0.08);'>
                        <strong style='color: #1E293B;'>{medal} {row['Agente']}</strong><br>
                        <small style='color: #475569;'>Puntaje: {row['Puntaje IA']:.1f} | Conv: {row['Conversión']:.1f}% | Excelentes: {row['Excelentes']}</small>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Distribución de puntajes - Gráfico profesional para juntas corporativas
        st.markdown("---")
        st.markdown("#### 📊 Distribución de Puntajes del Equipo")
        
        # Usar df_ranking filtrado para el gráfico
        df_grafico = df_ranking if 'df_ranking' in dir() and len(df_ranking) > 0 else df_equipo
        
        # Calcular estadísticas
        promedio = df_grafico['Puntaje IA'].mean()
        mediana = df_grafico['Puntaje IA'].median()
        
        # Definir colores por zona para las barras del histograma
        colores_zona = {
            'Crítico': '#DC2626',      # Rojo
            'En Desarrollo': '#F59E0B', # Amarillo/Naranja
            'Bueno': '#3B82F6',         # Azul
            'Excelente': '#10B981'      # Verde
        }
        
        # Crear datos para histograma coloreado por zona
        puntajes = df_grafico['Puntaje IA'].values
        
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
            xaxis_title=dict(text="Puntaje IA", font=dict(size=14, color='#1E293B', family="Arial Black")),
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
            criticos = len(df_ranking[df_ranking['Puntaje IA'] < 30])
            st.markdown(f"<div style='text-align:center; padding:10px; background:#FEE2E2; border-radius:8px; border-left: 4px solid #DC2626;'><span style='font-size:24px; font-weight:bold; color:#DC2626;'>{criticos}</span><br><small style='color:#991B1B; font-weight:600;'>Críticos (&lt;30)</small></div>", unsafe_allow_html=True)
        with col_stat2:
            bajos = len(df_ranking[(df_ranking['Puntaje IA'] >= 30) & (df_ranking['Puntaje IA'] < 60)])
            st.markdown(f"<div style='text-align:center; padding:10px; background:#FEF3C7; border-radius:8px; border-left: 4px solid #F59E0B;'><span style='font-size:24px; font-weight:bold; color:#B45309;'>{bajos}</span><br><small style='color:#78350F; font-weight:600;'>En Desarrollo (30-60)</small></div>", unsafe_allow_html=True)
        with col_stat3:
            buenos = len(df_ranking[(df_ranking['Puntaje IA'] >= 60) & (df_ranking['Puntaje IA'] < 80)])
            st.markdown(f"<div style='text-align:center; padding:10px; background:#DBEAFE; border-radius:8px; border-left: 4px solid #3B82F6;'><span style='font-size:24px; font-weight:bold; color:#1D4ED8;'>{buenos}</span><br><small style='color:#1E3A8A; font-weight:600;'>Buenos (60-80)</small></div>", unsafe_allow_html=True)
        with col_stat4:
            excelentes = len(df_ranking[df_ranking['Puntaje IA'] >= 80])
            st.markdown(f"<div style='text-align:center; padding:10px; background:#D1FAE5; border-radius:8px; border-left: 4px solid #10B981;'><span style='font-size:24px; font-weight:bold; color:#059669;'>{excelentes}</span><br><small style='color:#065F46; font-weight:600;'>Excelentes (≥80)</small></div>", unsafe_allow_html=True)
        
        # Recomendaciones generales
        st.markdown("---")
        st.markdown("### 💡 Recomendaciones para el Equipo")
        
        prom_puntaje = df_ranking['Puntaje IA'].mean()
        prom_conv = df_ranking['Conversión'].mean()
        agentes_bajo_prom = len(df_ranking[df_ranking['Puntaje IA'] < prom_puntaje])
        agentes_criticos = len(df_ranking[df_ranking['vs Equipo'] < -15])
        
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
    st.markdown('<div class="main-header">⚠️ COMMAND · Gestión de Reclamos y Quejas Pendientes</div>', unsafe_allow_html=True)
    
    # Subtítulo corporativo
    st.markdown("""
    <div style='background: #FEF2F2; padding: 12px 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #EF4444;'>
        <p style='margin: 0; color: #7F1D1D; font-size: 0.95rem;'>
            <strong>Panel de Seguimiento de Reclamos</strong> · Casos que requieren atención y resolución
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if 'quejas' not in datos:
        st.warning("⚠️ No hay datos de quejas disponibles.")
        return
    
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
    
    # Obtener mapeo de equipos para los filtros
    _, equipos_vendedores = cargar_listado_vendedores()
    
    # Aplicar mapeo de nombres a todo el dataframe (usando función global)
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
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Resumen Ejecutivo", "👤 Análisis por Vendedor", "🎯 Indicadores de Calidad", "🔍 Detalle de Evaluaciones"])
    
    with tab1:
        # =============================================================================
        # MÉTRICAS PRINCIPALES
        # =============================================================================
        st.markdown('<p class="section-header">📈 Indicadores Generales de Evaluación</p>', unsafe_allow_html=True)
        
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
            excelentes = len(df[df['puntaje_total'] >= 80])
            st.metric("🌟 Rendimiento Excelente", f"{excelentes:,} ({excelentes/total*100:.1f}%)")
        with col4:
            criticos = len(df[df['puntaje_total'] <= 20])
            st.metric("🔴 Requieren Atención", f"{criticos:,} ({criticos/total*100:.1f}%)")
        with col5:
            cero = len(df[df['puntaje_total'] == 0])
            st.metric("⚠️ Sin Evaluación", f"{cero:,} ({cero/total*100:.1f}%)")
        
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
                st.markdown("**⚠️ Requieren Plan de Mejora:**")
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
                
                # ========== SELECTORES DE COMPARACIÓN ==========
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

def pagina_calidad():
    """Página de Calidad - Análisis de Llamadas Call Center"""
    
    st.markdown('<p class="main-header">📞 COMMAND · Indicadores de Calidad y Cumplimiento</p>', unsafe_allow_html=True)
    
    # Subtítulo corporativo
    st.markdown("""
    <div style='background: #F8FAFC; padding: 12px 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #06B6D4;'>
        <p style='margin: 0; color: #334155; font-size: 0.95rem;'>
            <strong>Control de Calidad Operativa</strong> · Métricas de tiempo, cumplimiento y KPIs de ventas
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs principales
    tab1, tab2, tab3, tab4 = st.tabs([
        "📤 Carga de Datos", 
        "📊 Métricas por Vendedor", 
        "🚦 Semáforos de Tiempo",
        "💰 KPIs de Cumplimiento"
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
                <li><strong>Detalle Interacciones (Campaña - Lote).csv</strong> - Datos de llamadas</li>
                <li><strong>CargaAgentes.xlsx</strong> - Mapeo de agentes a vendedores (opcional)</li>
                <li><strong>Customer.csv/xlsx</strong> - Datos de ventas para KPIs (opcional)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📁 Archivo de Interacciones")
            archivo_interacciones = st.file_uploader(
                "Subir Detalle Interacciones (CSV)", 
                type=['csv'], 
                key='calidad_interacciones'
            )
            
            st.markdown("#### 👥 Archivo de Agentes")
            archivo_agentes = st.file_uploader(
                "Subir CargaAgentes (Excel)", 
                type=['xlsx', 'xls'], 
                key='calidad_agentes'
            )
        
        with col2:
            st.markdown("#### 💼 Archivo de Ventas (Customer)")
            archivo_ventas = st.file_uploader(
                "Subir Customer (CSV/Excel)", 
                type=['csv', 'xlsx', 'xls'], 
                key='calidad_ventas'
            )
            
            st.markdown("#### ⚙️ Configuración")
            
            # Filtro de agentes válidos
            agentes_validos_default = "MZA 1, MZA 2, MZA 3, MZA 4, MZA 5, MZA 6, MZA 7, MZA 8, MZA 9, MZA 10, MZA 11, MZA 12, MZA 13, MZA 14, MZA 15, 304, 305, 306"
            agentes_validos_input = st.text_area(
                "Agentes válidos (separados por coma):",
                value=agentes_validos_default,
                height=80,
                key='agentes_validos'
            )
        
        # Procesar archivos si se cargan
        if archivo_interacciones is not None:
            try:
                # Cargar CSV de interacciones
                df_inter = pd.read_csv(archivo_interacciones, encoding='latin-1')
                st.session_state['df_calidad_interacciones'] = df_inter
                
                st.success(f"✅ Archivo de interacciones cargado: {len(df_inter):,} registros")
                
                # Mostrar preview
                with st.expander("👁️ Vista previa de datos", expanded=False):
                    st.dataframe(df_inter.head(10), use_container_width=True)
                    st.markdown(f"**Columnas detectadas:** {', '.join(df_inter.columns.tolist())}")
                
            except Exception as e:
                st.error(f"❌ Error al cargar archivo: {str(e)}")
        
        if archivo_agentes is not None:
            try:
                df_agentes = pd.read_excel(archivo_agentes)
                st.session_state['df_calidad_agentes'] = df_agentes
                st.success(f"✅ Archivo de agentes cargado: {len(df_agentes):,} registros")
            except Exception as e:
                st.error(f"❌ Error al cargar agentes: {str(e)}")
        
        if archivo_ventas is not None:
            try:
                if archivo_ventas.name.endswith('.csv'):
                    df_ventas = pd.read_csv(archivo_ventas, encoding='latin-1')
                else:
                    df_ventas = pd.read_excel(archivo_ventas)
                st.session_state['df_calidad_ventas'] = df_ventas
                st.success(f"✅ Archivo de ventas cargado: {len(df_ventas):,} registros")
            except Exception as e:
                st.error(f"❌ Error al cargar ventas: {str(e)}")
        
        # Botón para procesar datos
        st.markdown("---")
        if st.button("🚀 Procesar Datos", type="primary", use_container_width=True):
            if 'df_calidad_interacciones' not in st.session_state:
                st.warning("⚠️ Primero debes cargar el archivo de interacciones")
            else:
                with st.spinner("Procesando datos..."):
                    df_inter = st.session_state['df_calidad_interacciones'].copy()
                    
                    # Normalizar nombres de columnas
                    df_inter.columns = df_inter.columns.str.strip()
                    
                    # Detectar columnas relevantes
                    col_agente = next((c for c in df_inter.columns if 'agente' in c.lower()), None)
                    col_tipificacion = next((c for c in df_inter.columns if 'tipificaci' in c.lower()), None)
                    col_origen_corte = next((c for c in df_inter.columns if 'origen' in c.lower() and 'corte' in c.lower()), None)
                    col_talking = next((c for c in df_inter.columns if 'talking' in c.lower()), None)
                    col_inicio = next((c for c in df_inter.columns if 'inicio' in c.lower()), None)
                    col_campana = next((c for c in df_inter.columns if 'campa' in c.lower()), None)
                    
                    # Renombrar columnas
                    rename_map = {}
                    if col_agente: rename_map[col_agente] = 'Nombre Agente'
                    if col_tipificacion: rename_map[col_tipificacion] = 'Tipificación'
                    if col_origen_corte: rename_map[col_origen_corte] = 'Origen Corte'
                    if col_talking: rename_map[col_talking] = 'TalkingTime'
                    if col_inicio: rename_map[col_inicio] = 'Inicio'
                    if col_campana: rename_map[col_campana] = 'Campaña'
                    
                    df_inter = df_inter.rename(columns=rename_map)
                    
                    # Normalizar a minúsculas para comparaciones
                    if 'Tipificación' in df_inter.columns:
                        df_inter['Tipificación_lower'] = df_inter['Tipificación'].astype(str).str.lower().str.strip()
                    if 'Origen Corte' in df_inter.columns:
                        df_inter['Origen Corte_lower'] = df_inter['Origen Corte'].astype(str).str.lower().str.strip()
                    
                    # Convertir TalkingTime a segundos
                    if 'TalkingTime' in df_inter.columns:
                        df_inter['TalkingTime_seg'] = df_inter['TalkingTime'].apply(to_seconds_calidad)
                    
                    # Determinar turno
                    if 'Inicio' in df_inter.columns:
                        df_inter['Turno'] = df_inter['Inicio'].apply(determinar_turno)
                    
                    # Filtrar agentes válidos si se especifican
                    agentes_lista = [a.strip() for a in agentes_validos_input.split(',')]
                    if 'Nombre Agente' in df_inter.columns and agentes_lista:
                        # Filtro flexible - solo si coincide parcialmente
                        df_inter['agente_valido'] = df_inter['Nombre Agente'].astype(str).apply(
                            lambda x: any(av.lower() in x.lower() for av in agentes_lista if av)
                        )
                    
                    # Guardar datos procesados
                    st.session_state['df_calidad_procesado'] = df_inter
                    st.success("✅ Datos procesados correctamente")
                    
                    # Mostrar resumen
                    st.markdown("### 📊 Resumen de Datos Procesados")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("📞 Total Llamadas", f"{len(df_inter):,}")
                    with col2:
                        agentes_unicos = df_inter['Nombre Agente'].nunique() if 'Nombre Agente' in df_inter.columns else 0
                        st.metric("👥 Agentes", f"{agentes_unicos}")
                    with col3:
                        if 'TalkingTime_seg' in df_inter.columns:
                            tiempo_total = df_inter['TalkingTime_seg'].sum()
                            st.metric("⏱️ Tiempo Total", sec_to_hhmmss(tiempo_total))
                    with col4:
                        if 'Turno' in df_inter.columns:
                            turnos = df_inter['Turno'].value_counts().to_dict()
                            turno_principal = max(turnos, key=turnos.get) if turnos else "N/A"
                            st.metric("🌅 Turno Principal", turno_principal)
    
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
    
    # Cargar datos
    with st.spinner('Cargando datos...'):
        datos = cargar_datos()
    
    if 'transcripciones' not in datos or not datos['transcripciones']:
        st.error("No se encontraron transcripciones procesadas. Asegúrate de tener archivos en 'total_transcripciones/procesados/'")
        return
    
    # Crear DataFrame de llamadas
    df = crear_df_llamadas(datos['transcripciones'])
    
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
    
    paginas = {
        "🏠 Panel Ejecutivo": "resumen",
        "📋 Gestión de Cierres": "cierres",
        "📱 Análisis de Productos": "planes",
        "⚠️ Gestión de Reclamos": "quejas",
        "⏱️ Control de Tiempos": "duracion",
        "🔮 Clasificación de Llamadas": "clasificacion",
        "🤖 Evaluación Automatizada": "gemini",
        "🎯 Planes de Mejora": "coaching",
        "👥 Rendimiento de Vendedores": "agentes",
        "📅 Análisis por Período": "temporal",
        "🔍 Detalle de Operaciones": "detalle",
        "📞 Indicadores de Calidad": "calidad"
    }
    
    seleccion = st.sidebar.radio("Módulos disponibles:", list(paginas.keys()))
    
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
    elif paginas[seleccion] == "calidad":
        pagina_calidad()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"<small>COMMAND v2.0 · Sistema de Rendimiento Comercial<br>Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</small>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()

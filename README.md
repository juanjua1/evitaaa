# EVA - Evaluación de Vendedores Automática

Sistema integral de análisis y evaluación de agentes de call center. Automatiza la transcripción de llamadas, evaluación con IA (Gemini), y presenta métricas en un dashboard ejecutivo.

## Arquitectura

```
EVA/
├── dashboard_eva.py          # Dashboard Streamlit (app principal)
├── requirements.txt          # Dependencias Python
├── credenciales_eva.csv      # Credenciales de acceso al dashboard
├── LISTADO-DE-VENDEDORES.csv # Mapeo de agentes → equipos
├── .streamlit/config.toml    # Configuración de Streamlit
├── datos_calidad/            # Datos de calidad procesados (JSON)
└── reportes/                 # Reportes generados
    ├── coaching_vendedores/  # Coaching individual por agente
    ├── coaching_equipos/     # Coaching por equipo/supervisora
    ├── evaluaciones_gemini.csv
    ├── planes/               # Análisis de ofertas de planes
    ├── quejas/               # Análisis de quejas
    └── resumen_vendedores_integral.*
```

## Pipeline de Procesamiento (local)

Scripts numerados que se ejecutan en orden:

| # | Script | Función |
|---|--------|---------|
| 1 | `1_scraper_eva.py` | Scraping de interacciones desde plataforma |
| 2 | `2_preproc_audio.py` | Preprocesamiento de audio |
| 3 | `3_speech_eva.py` | Transcripción con WhisperX |
| 4 | `4_evaluacion_gemini.py` | Evaluación con Gemini AI |
| 5 | `5_coaching_vendedores.py` | Generación de coaching individual |
| 6 | `6_coaching_equipos.py` | Coaching por equipos |
| 7 | `7_corregir_diarizacion.py` | Corrección de diarización |
| 8 | `8_cruzar_con_basurita.py` | Cruce con datos de tipificación |
| 10 | `10_reporte_agentes.py` | Reporte por agentes |
| 11 | `11_analisis_planes_ofrecidos.py` | Análisis de planes ofrecidos |
| 12 | `12_corregir_errores_whisper.py` | Corrección de errores de Whisper |
| 13 | `13_analisis_quejas.py` | Análisis de quejas |
| 13 | `13_analisis_cierres_comerciales.py` | Análisis de cierres |
| 14 | `14_analisis_integral.py` | Análisis integral |
| 15 | `15_clasificacion_completa.py` | Clasificación completa |
| 16 | `16_generar_consolidado_gemini.py` | Consolidado Gemini |
| 17 | `17_clasificacion_agentes_equipos.py` | Clasificación agentes/equipos |

## Deployment

El dashboard se despliega en **Streamlit Cloud** desde la rama `main`.

```bash
# Ejecutar localmente
streamlit run dashboard_eva.py
```

## Stack Tecnológico

- **Frontend**: Streamlit + Plotly
- **Transcripción**: WhisperX
- **Evaluación IA**: Google Gemini
- **Scraping**: Selenium
- **Datos**: Pandas, JSON

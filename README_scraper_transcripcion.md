# EVA - Descarga de Audios y Transcripción

## Descripción

Este paquete contiene los scripts necesarios para descargar audios de llamadas desde la plataforma Mitrol y transcribirlos con diarización (identificación de hablantes) usando WhisperX + ECAPA-TDNN.

---

## Archivos incluidos

| Archivo | Descripción |
|---------|-------------|
| `1_scraper_eva.py` | Descarga automática de audios desde Mitrol (Selenium) |
| `3_speech_eva.py` | Transcripción con WhisperX + diarización ECAPA-TDNN |
| `config.py` | Configuración: credenciales, rutas y API key |

---

## Requisitos

### Python 3.10+

### Dependencias para descarga (`1_scraper_eva.py`)
```bash
pip install selenium webdriver-manager requests
```

### Dependencias para transcripción (`3_speech_eva.py`)
```bash
pip install whisperx torch torchaudio speechbrain scikit-learn numpy
```

### Otros
- **Google Chrome** instalado (usado por Selenium para el scraping)
- **GPU NVIDIA** recomendada para transcripción (funciona sin GPU pero más lento)

---

## Configuración (`config.py`)

Editar `config.py` con tus datos antes de ejecutar:

```python
user = "tu_usuario"              # Usuario de Mitrol
password = "tu_contraseña"       # Contraseña de Mitrol
url = "https://apps-alc.mitrol.cloud/reportes/login.aspx"  # URL de login
carpeta_audios = r"C:\ruta\a\audios_descargados"            # Carpeta destino audios
carpeta_trancripciones = r"C:\ruta\a\transcripciones"       # Carpeta destino transcripciones
api_key = "tu_api_key_gemini"    # API key de Google Gemini (para otros scripts)
```

---

## Uso

### Paso 1: Descarga de audios

```bash
python 1_scraper_eva.py
```

**¿Qué hace?**
- Abre Chrome en modo automatizado y se loguea en Mitrol
- Navega al módulo de reportes de interacciones
- Selecciona los usuarios configurados en `USUARIOS_A_SELECCIONAR` (MZA 1, MZA 2, etc.)
- Filtra por horario (08:00 a 23:00 por defecto)
- Descarga los audios WAV de todas las páginas de resultados
- Usa **20 workers** para descarga concurrente (configurable con `MAX_WORKERS`)
- Guarda **checkpoints** para reanudar si se interrumpe
- Los audios se guardan en `carpeta_audios` definida en `config.py`
- Genera un log en `descarga_log.txt` dentro de la carpeta de audios

**Configuración importante (dentro del script):**
- `USUARIOS_A_SELECCIONAR`: Lista de agentes a descargar
- `MAX_WORKERS`: Workers concurrentes de descarga (default: 20)
- `HORA_INICIO_AUTO` / `HORA_FIN_AUTO`: Rango horario del filtro (default: 08 a 23)

---

### Paso 2: Transcripción de audios

```bash
python 3_speech_eva.py
```

**¿Qué hace?**
- Lee los archivos `.wav` de la carpeta de audios
- Transcribe cada audio con **WhisperX** (modelo `large-v3`, idioma español)
- Aplica **diarización forzada a 2 hablantes** (agente y cliente) usando **ECAPA-TDNN**
- Genera un JSON por cada audio con la transcripción segmentada por hablante
- Detecta automáticamente quién es el agente y quién es el cliente
- Muestra progreso y estimación de tiempo restante

**Configuración (dentro del script, sección MAIN):**
- `CARPETA_ENTRADA`: Carpeta de audios WAV (default: `audios_descargados/`)
- `CARPETA_SALIDA`: Carpeta de transcripciones (default: `transcripciones/`)
- `USAR_ECAPA`: `True` para usar ECAPA-TDNN (recomendado), `False` para método básico por pausas
- `NUM_WORKERS`: Workers paralelos (recomendado: 1 con ECAPA)

**Formato de salida (JSON):**
```json
{
  "archivo": "amza1_1_260119102327574_ACD_66639.wav",
  "fecha_procesamiento": "2026-01-19T10:30:00",
  "duracion_segundos": 245.3,
  "metodo_diarizacion": "ecapa-tdnn",
  "segmentos": [
    {
      "speaker": "Agente",
      "start": 0.5,
      "end": 5.2,
      "text": "Hola buenas tardes Movistar le habla..."
    },
    {
      "speaker": "Cliente",
      "start": 5.3,
      "end": 8.1,
      "text": "Sí hola buenas tardes..."
    }
  ]
}
```

**Rendimiento estimado:**
- Con GPU: ~400 audios/hora
- Sin GPU: ~200 audios/hora

---

## Flujo completo

```
1. Configurar config.py con credenciales y rutas
2. python 1_scraper_eva.py    → Descarga audios WAV
3. python 3_speech_eva.py     → Genera transcripciones JSON
```

---

## Notas

- Si la descarga se interrumpe, al volver a ejecutar `1_scraper_eva.py` reanuda desde el último checkpoint.
- Si la transcripción se interrumpe, al volver a ejecutar `3_speech_eva.py` detecta los ya procesados y continúa con los pendientes.
- Los nombres de archivo de audio siguen el formato: `{agente}_{campaign}_{fecha}_{tipo}_{id}.wav`

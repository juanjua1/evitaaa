# Análisis de Productos Ofrecidos (Planes + Fibra)

## Qué hace

El script `11_analisis_planes_ofrecidos.py` analiza las transcripciones mejoradas para detectar:

- **Planes móviles ofrecidos**: 4GB, 8GB, 15GB, 30GB
- **Fibra óptica**: si el agente ofreció internet hogar

Extrae automáticamente el **agente** y la **fecha** del nombre de cada archivo.

---

## Requisitos previos

1. Tener las **transcripciones mejoradas** en la carpeta `transcripciones_mejoradas/`
   - Son los archivos `*_mejorado.json` generados por el pipeline de mejora con Gemini
2. Los archivos deben seguir el formato de nombre: `amzaX_1_YYMMDD..._mejorado.json`
   - Ejemplo: `amza10_1_260209105133829_ACD_95297_mejorado.json`
   - De ahí se extrae: agente = `amza10`, fecha = `09/02`

---

## Cómo ejecutar

```bash
cd c:\Users\rodri\Documents\codigo-WC\eva
python 11_analisis_planes_ofrecidos.py
```

---

## Configuración

En el script se pueden ajustar estas variables:

| Variable | Valor actual | Descripción |
|---|---|---|
| `CARPETA_TRANSCRIPCIONES` | `transcripciones_mejoradas` | Carpeta con los JSON mejorados |
| `CARPETA_SALIDA` | `reportes/planes` | Donde se guardan los reportes |
| `PLANES_VALIDOS` | `4gb, 8gb, 15gb, 30gb` | Planes que se detectan |

### Detección de planes

El script usa regex para detectar menciones de planes, incluyendo **errores comunes de Whisper** como:
- "4 llenas" en vez de "4 gigas"
- "ocho libras" en vez de "8 gigas"
- "cuatro chicas" en vez de "4 gigas"

### Detección de fibra

Busca menciones de: `fibra`, `fibra óptica`, `internet hogar`, `internet en casa`, `wifi casa`, `movistar hogar`, velocidades como `100 megas`, `300 mb`, etc.

### Solo analiza lo que dice el AGENTE

No cuenta menciones del cliente. Solo lo que dice el hablante etiquetado como `AGENTE` en la conversación.

---

## Archivos de salida

Se generan en `reportes/planes/`:

| Archivo | Contenido |
|---|---|
| `analisis_planes_detallado.csv` | Detalle por llamada: archivo, agente, fecha, planes ofrecidos, fibra |
| `llamadas_sin_fibra.csv` | Lista de llamadas donde NO se ofreció fibra |
| `resumen_planes.json` | Resumen con totales, conteo por plan y desglose por agente |

---

## Ver resultados en el Dashboard

1. Ejecutar el script para generar los datos:
   ```bash
   python 11_analisis_planes_ofrecidos.py
   ```

2. Levantar el dashboard:
   ```bash
   streamlit run dashboard_eva.py --server.port 8501
   ```

3. Ir a la sección **📱 Análisis de Portafolio de Productos** en el menú lateral

El dashboard muestra:
- Métricas generales (total llamadas, % con plan ofrecido, % con fibra)
- Gráfico de barras de planes más ofrecidos
- Pie chart del primer plan ofrecido (estrategia inicial del vendedor)
- Distribución de ofertas de fibra
- Ranking de vendedores con menor oferta de fibra

### Filtros disponibles

- Por **equipo** (si sos admin/supervisor)
- Por **vendedor** individual
- Los vendedores solo ven sus propios datos

---

## Troubleshooting

| Problema | Causa | Solución |
|---|---|---|
| Agente sale como "desconocido" | El nombre del archivo no tiene formato `amzaX_...` | Verificar nombres de archivos en `transcripciones_mejoradas/` |
| Fecha sale como "desconocida" | El nombre del archivo no tiene el patrón `YYMMDD` | Idem |
| Dashboard no muestra datos | No se ejecutó el script 11 antes | Ejecutar `python 11_analisis_planes_ofrecidos.py` primero |
| Vendedores sin equipo no aparecen | El dashboard filtra vendedores que no están en `LISTADO-DE-VENDEDORES.csv` | Agregar el vendedor al listado |

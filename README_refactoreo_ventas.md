# README — Refactoreo del Sistema de Ventas (Tab Ventas)

## Contexto

El dashboard `dashboard_eva.py` (sistema COMMAND/EVA) es un panel Streamlit para gestión de calidad de un call center de Movistar Argentina. La pestaña de **Ventas** (tab2) fue completamente refactoreada para usar un único CSV de solicitudes como fuente de datos.

## Cambio Realizado

### Antes (sistema viejo)
- **2 file uploaders** separados: uno para CSV semanal y otro para CSV mensual
- Parser basado en bloques de texto (`_parsear_ventas_csv()`) que requería un formato CSV específico con headers por equipo
- **3 vistas** en toggle: Solicitudes / Semanal / Mensual
- La vista "Solicitudes" leía de `datos_calidad_procesados.json`
- Las vistas Semanal/Mensual leían de CSVs con formato propietario (bloques con vendedores y efectividad de carga/aprobación)
- Campos: `vendedores_aprob`, `vendedores_carga`, `efectividad_equipo`, `efectividad_carga`, `objetivo`

### Después (sistema nuevo)
- **1 file uploader** único: `CSV de Solicitudes (contiene todos los equipos)`
- Parser automático `_construir_datos_ventas()` que procesa el CSV estándar de solicitudes
- **2 vistas** en toggle: Semanal / Mensual (se eliminó Solicitudes)
- Ambas vistas leen del mismo JSON generado: `datos_ventas_csv.json`
- Campos: `cargadas`, `aprobadas`, `canceladas`, `pendientes`, `tasa_aprobacion`, `estado`

## Formato del CSV de Solicitudes (entrada)

El CSV esperado es el export estándar de solicitudes con estas columnas clave:
- **Vendedor**: nombre del vendedor
- **Ejecutivo**: nombre completo (ej: "ARENAS YASMIN") — el segundo nombre se usa para mapear el equipo
- **Estado de Solicitud**: texto libre que se clasifica automáticamente
- **Fecha de Venta**: formato `dd/mm/yyyy` — se usa para agrupar por semana ISO

El CSV puede tener cualquier cantidad de columnas adicionales (57 en el caso actual); solo se usan las 4 mencionadas.

## Lógica de Clasificación de Estados

```
APROB|ACTIVAD → aprobada
CANCEL|OTRO CALL|DEVOLUCION → cancelada
todo lo demás → pendiente
```

Se busca con regex case-insensitive en el campo "Estado de Solicitud".

## Mapeo de Equipos

Del campo **Ejecutivo** se extrae la segunda palabra y se convierte a mayúsculas:
```
"ARENAS YASMIN"    → EQUIPO YASMIN
"CARMONA MELANIE"  → EQUIPO MELANIE
"MARTINEZ MARINA"  → EQUIPO MARINA
"BYL VENTAS"       → EQUIPO VENTAS
```

## Estructura del JSON generado (`datos_ventas_csv.json`)

```json
{
  "semanal": {
    "fecha_proceso": "2026-01-25 14:30",
    "semanas": {
      "1": {
        "semana": 1,
        "rango": "02/01 - 02/01",
        "total_solicitudes": 49,
        "equipos": [ ... ],
        "totales": { ... }
      },
      "2": { ... },
      "3": { ... },
      "4": { ... }
    }
  },
  "mensual": {
    "fecha_proceso": "2026-01-25 14:30",
    "rango": "02/01/2026 - 25/01/2026",
    "equipos": [ ... ],
    "totales": { ... }
  }
}
```

Cada **equipo** tiene:
```json
{
  "equipo": "EQUIPO MELANIE",
  "ejecutivo": "CARMONA MELANIE",
  "num_vendedores": 12,
  "totales": {
    "ventas_cargadas": 339,
    "ventas_aprobadas": 220,
    "ventas_canceladas": 18,
    "ventas_pendientes": 101,
    "efectividad_equipo": 64.9,
    "tasa_aprobacion": 64.9
  },
  "vendedores": [ ... ]
}
```

Cada **vendedor** tiene:
```json
{
  "vendedor": "GONZALEZ MARIA",
  "equipo": "EQUIPO MELANIE",
  "ejecutivo": "CARMONA MELANIE",
  "cargadas": 28,
  "aprobadas": 20,
  "canceladas": 2,
  "pendientes": 6,
  "efectividad_aprobacion": 71.4,
  "tasa_aprobacion": 71.4,
  "estado": "VERDE"
}
```

Estado del vendedor: `VERDE` (≥70%), `AMARILLO` (≥50%), `ROJO` (<50%).

## Vistas del Dashboard

### Vista Semanal
- **Selector de semana**: dropdown con "Semana X (rango) — N solicitudes"
- **6 KPIs**: Cargadas, Aprobadas, Canceladas, Pendientes, Vendedores, Tasa Aprob.
- **Gráfico comparativo por equipo**: barras agrupadas (Cargadas/Aprobadas/Canceladas/Pendientes)
- **Tabla resumen por equipo**: con Ejecutivo, Vendedores, Tasa Aprob. % (coloreada por semáforo)
- **Expanders por equipo**: semáforo + KPIs + gráfico de vendedores (coloreado por tasa) + tabla detallada

### Vista Mensual
- **Rango de fechas** mostrado en header
- **6 KPIs**: iguales a semanal pero con datos del mes completo
- **Multiselect de equipos**: filtro interactivo
- **Gráfico comparativo por equipo**: 4 barras (Cargadas/Aprobadas/Canceladas/Pendientes)
- **Tabla resumen por equipo**: con Tasa Aprob. % coloreada
- **Expanders por equipo**: misma estructura que semanal

## Datos de Prueba Validados

Con `solicitudes.csv` (2700 filas, enero 2026):
- 8 equipos, 80 vendedores únicos
- 4 semanas ISO (1-4)
- 1742 aprobadas, 163 canceladas, 795 pendientes
- Tasa global: 64.5%

## Archivos Modificados

- `dashboard_eva.py`: refactoreo completo de la sección de Ventas (tab2)
  - File uploader: 2 → 1
  - Parser: `_parsear_ventas_csv()` → `_construir_datos_ventas()`
  - Toggle: 3 opciones → 2 opciones
  - Semanal: reescrita con selector por semana
  - Mensual: actualizada con nuevos campos
  - Solicitudes: eliminada completamente

## Fecha

2025-06-17

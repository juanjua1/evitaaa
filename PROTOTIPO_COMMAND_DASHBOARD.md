# PROTOTIPO: COMMAND · Sistema de Rendimiento Comercial

> **Versión:** 2.0 · **Tecnología:** Python + Streamlit + Plotly  
> **Propósito:** Especificación completa de módulos, secciones, métricas y gráficos del dashboard ejecutivo COMMAND.

---

## Objetivo General

COMMAND es un **dashboard ejecutivo de auditoría y gestión del rendimiento** para equipos de ventas en call centers. Su objetivo principal es brindar visibilidad integral sobre:

- La **calidad de las interacciones** entre vendedores y clientes, evaluada automáticamente con Inteligencia Artificial.
- El **rendimiento comercial** de cada vendedor y equipo (conversión, productos ofrecidos, cumplimiento de protocolo).
- La **gestión de reclamos y quejas** no resueltas por parte del equipo.
- Los **planes de mejora y coaching** individuales y grupales basados en datos objetivos.
- La **comparativa temporal** del rendimiento entre distintas semanas o períodos.

El sistema procesa transcripciones de llamadas, las evalúa con IA (Gemini) según criterios de calidad predefinidos, y presenta los resultados en un entorno visual e interactivo, segmentado por rol de usuario.

---

## Sistema de Roles y Permisos

| Rol | Acceso | Descripción |
|-----|--------|-------------|
| **Admin** | Total | Ve todos los equipos, todos los vendedores, todos los módulos. Puede comparar períodos e ingresar a indicadores avanzados de calidad. |
| **Supervisor** | Equipo propio | Ve métricas de su equipo y puede comparar vendedores dentro de él. Accede a Resumen Corporativo y Métricas de Calidad. |
| **Vendedor** | Datos propios | Solo ve sus propias evaluaciones, productos y plan de mejora. Los vendedores del equipo Melanie Carmona tienen acceso directo al Resumen Corporativo (en lugar del menú estándar), ya que ese equipo utiliza una modalidad de seguimiento diferente. |

---

## Sidebar y Navegación

La barra lateral izquierda contiene:

1. **Logo COMMAND** — Título "📈 COMMAND · Sistema de Rendimiento Comercial"
2. **Info del usuario** — Nombre y rol del usuario logueado
3. **Botón Cerrar Sesión**
4. **Menú de módulos** — Radio buttons con los módulos disponibles según el rol
5. **Filtro de fechas** — Selector de período:
   - 📆 Todo el período
   - 📅 Semana 12-16 Enero
   - 📅 Semana 19-24 Enero
   - 🔧 Personalizado (rango libre con fecha inicio y fin)
6. **Indicadores Clave** — Resumen rápido:
   - Total Operaciones
   - Período de datos
   - Vendedores Activos
7. **Footer** — Versión y fecha de actualización

### Menú según rol

| Rol | Módulos visibles |
|-----|-----------------|
| Vendedor (otros equipos) | 📱 Mis Productos Ofrecidos · ⚠️ Mis Reclamos · 🤖 Mi Evaluación · 🎯 Mi Plan de Mejora |
| Vendedor (equipo Melanie Carmona) | 📊 Resumen Corporativo |
| Supervisor | 📱 Productos del Equipo · ⚠️ Reclamos del Equipo · 🤖 Evaluaciones del Equipo · 🎯 Planes de Mejora · 👥 Análisis de Mi Equipo · 📊 Resumen Corporativo · 📊 Métricas de Calidad |
| Admin | 📱 Análisis de Productos · 🤖 Evaluación Automatizada · 🎯 Planes de Mejora · 👥 Análisis de Equipos · 📊 Resumen Corporativo · 📊 Métricas de Calidad · 📞 Indicadores de Calidad (Admin) · 📅 Comparativa de Períodos |

---

## Módulos del Dashboard

---

### Módulo 1 — 📱 Análisis de Portafolio de Productos

**Título:** `COMMAND · Análisis de Portafolio de Productos`  
**Estado:** ✅ Activo  
**Objetivo:** Analizar qué productos (planes móviles y fibra óptica) están siendo ofrecidos por los vendedores en cada interacción, detectando brechas de oferta y estrategias de primer contacto.

#### Filtros disponibles (según rol)
- **Vendedor:** Sin filtros, ve solo sus datos automáticamente.
- **Supervisor:** Filtro de vendedor dentro de su equipo.
- **Admin:** Filtro por equipo + filtro por vendedor individual.

#### Sección 1 — 📱 Análisis de Ofertas de Planes Móviles

**Métricas (fila de KPIs):**
| Métrica | Descripción |
|---------|-------------|
| 📞 Total Operaciones | Total de llamadas en el período |
| ✅ Oferta Realizada | Llamadas donde se ofreció al menos un plan |
| ❌ Sin Oferta | Llamadas sin ningún plan ofrecido |
| 🌐 Ofreció Fibra | Cantidad de veces que se ofreció fibra óptica |
| 🥇 Plan Principal | El plan más ofrecido como primer producto |

**Gráficos:**

1. **Gráfico de barras — "Planes Más Ofrecidos"**
   - Eje X: Planes (4GB, 8GB, 15GB, 30GB)
   - Eje Y: Cantidad de veces ofrecido
   - Color: escala azul (claro → oscuro según volumen)
   - Muestra los 4 planes principales

2. **Gráfico de torta — "Primer Plan Ofrecido (Estrategia Inicial)"**
   - Muestra la distribución porcentual del primer plan ofrecido por los vendedores
   - Indica la estrategia de entrada comercial del equipo

---

#### Sección 2 — 🏠 Análisis de Ofertas de Fibra Óptica

**Métricas (fila de KPIs):**
| Métrica | Descripción |
|---------|-------------|
| ✅ Oferta Realizada | Llamadas donde se ofreció fibra |
| ❌ Sin Oferta de Fibra | Llamadas donde NO se ofreció fibra |
| Alerta | Indicador automático: ⚠️ crítico si <30%, advertencia si <50%, ✅ si ≥50% |

**Gráficos:**

1. **Gráfico de torta tipo donut — "Distribución de Ofertas de Fibra"**
   - Segmentos: Ofrece Fibra (verde) vs No Ofrece Fibra (rojo)
   - Muestra etiquetas con porcentaje y nombre

2. **Tabla — "Vendedores con Menor Oferta de Fibra"**
   - Columnas: Agente | Sin Fibra % | Total llamadas
   - Ordenada de mayor a menor brecha
   - Permite identificar quiénes requieren refuerzo

---

#### Sección 3 — 🎁 Análisis de Cumplimiento de Promociones *(comentada — pendiente)*

> Esta sección está temporalmente deshabilitada en el código.  
> Mostrará cumplimiento de mención de promociones en días de promo, métricas de adherencia a campañas y gráfico de barras apiladas (menciona / no menciona).

---

### Módulo 2 — 🤖 Evaluación Automatizada de Calidad (IA)

**Título:** `COMMAND · Evaluación Automatizada de Calidad`  
**Estado:** ✅ Activo  
**Objetivo:** Mostrar el resultado de las evaluaciones automáticas realizadas por IA (Gemini) sobre cada interacción. Cada llamada es puntuada del 0 al 100 en base a 10 criterios de calidad, permitiendo identificar fortalezas y áreas de mejora por vendedor y equipo.

#### Criterios de Evaluación IA (10 criterios, 0-100 c/u):

| Criterio | Descripción |
|----------|-------------|
| Saludo y Presentación | El vendedor se presenta correctamente al inicio |
| Identificación Cliente | Verifica datos del cliente |
| Detección de Necesidades | Indaga qué necesita el cliente |
| Oferta de Productos | Presenta el producto adecuado |
| Manejo de Objeciones | Responde objeciones del cliente |
| Cierre de Venta | Concreta la venta o acción siguiente |
| Despedida | Cierre cortés y profesional |
| Proactividad | Iniciativa en la conversación |
| Empatía | Conexión emocional con el cliente |
| Resolución de Problemas | Soluciona consultas o inconvenientes |

#### Filtros disponibles
- **Vendedor:** Solo ve sus evaluaciones.
- **Supervisor:** Filtra por su equipo; puede ver vendedores individuales.
- **Admin:** Puede filtrar por equipo y vendedor; accede a todos los datos.
- **Filtro de fechas** (global desde sidebar).

---

#### Tab 1 — 📊 Resumen Ejecutivo *(admin/supervisor)* / Mi Rendimiento *(vendedor)*

**Métricas (fila de KPIs):**
| Métrica | Descripción |
|---------|-------------|
| 📊 Total Evaluaciones | Cantidad de llamadas evaluadas |
| ⭐ Índice de Calidad | Puntaje promedio del equipo/vendedor |
| 🌟 Rendimiento Excelente | Llamadas con puntaje ≥ 80 |
| 🔴 Requieren Atención | Llamadas con puntaje ≤ 20 |

**Gráficos:**

1. **Gráfico de torta — "Distribución por Rango de Puntaje"**
   - Rangos: Crítico (0-20) | Bajo (21-40) | Regular (41-60) | Bueno (61-80) | Excelente (81-100)
   - Muestra el porcentaje de llamadas en cada rango de calidad

2. **Gráfico de barras horizontal — "Ranking de Rendimiento por Vendedor"**
   - Eje Y: Nombre del vendedor
   - Eje X: Puntaje promedio
   - Ordenado de mayor a menor puntaje
   - Línea de referencia (meta)

3. **Gráfico de barras agrupadas por criterio** *(para admin/supervisor)*
   - Muestra el puntaje promedio por equipo en cada uno de los 10 criterios
   - Permite comparar equipos o vendedores en criterios específicos

---

#### Tab 2 — 👤 Análisis por Vendedor *(admin/supervisor)*

**Filtro:** Selector de vendedor individual

**Métricas individuales:**
| Métrica | Descripción |
|---------|-------------|
| 📊 Operaciones Evaluadas | Total de llamadas del vendedor |
| 🎯 Índice de Rendimiento | Puntaje promedio con delta vs equipo |
| 🌟 Gestiones Destacadas | Llamadas con puntaje ≥ 80 |
| 🔴 Gestiones Críticas | Llamadas con puntaje ≤ 20 |

**Gráficos:**

1. **Gráfico de barras horizontal — "Puntaje por Criterio"**
   - Compara el puntaje del vendedor seleccionado vs el promedio del equipo en cada criterio
   - Color verde = supera al equipo, rojo = por debajo del equipo

2. **Tabla de diferencias por criterio**
   - Columnas: Criterio | Vendedor | Equipo | Diferencia
   - Muestra claramente dónde el vendedor está por encima o por debajo

3. **Indicador de Posicionamiento Percentil**
   - Texto: "Este agente se encuentra en el percentil X de su equipo"

4. **Histograma de distribución de puntajes del vendedor**

5. **Explorador de Evaluaciones** — Tabla detallada de cada evaluación individual con puntaje, fecha, criterios y observaciones de la IA

---

### Módulo 3 — 🎯 Planes de Mejora y Coaching de Vendedores

**Título:** `COMMAND · Planes de Mejora y Desarrollo de Vendedores`  
**Estado:** ✅ Activo  
**Objetivo:** Mostrar el plan de acción personalizado de cada vendedor basado en el análisis de IA, las áreas de mejora identificadas, comparativas con el equipo, y el ranking de evolución.

#### Métricas globales del módulo:
| Métrica | Descripción |
|---------|-------------|
| 👥 Vendedores Evaluados | Cantidad con plan de coaching activo |
| 📊 Puntaje Promedio | Promedio del equipo en evaluaciones IA |

---

#### Tab 1 — 📋 Coaching Individual

**Para Vendedores:** Tab único "Mi Plan de Coaching"  
**Para Admin/Supervisor:** Tab con selector de vendedor

**Contenido por vendedor seleccionado:**

1. **Métricas del vendedor:**
   - Puntaje IA, percentil en el equipo, total evaluaciones, delta vs equipo

2. **Indicador de posicionamiento:**
   - Texto destacado: "Estás en el percentil X — superás al X% de tus compañeros"

3. **Gráfico de barras horizontal — "Comparativa por Criterio"**
   - Puntaje del vendedor vs promedio del equipo en cada uno de los 10 criterios
   - Barras en azul (vendedor) y naranja (equipo)
   - Tabla de diferencias adjunta

4. **Plan de Acción** — Análisis generado por IA con:
   - Áreas críticas de mejora
   - Puntos fuertes
   - Recomendaciones específicas
   - Acciones concretas para la semana

5. **Áreas de Mejora Frecuentes** — Lista de los criterios con menor puntaje recurrente

6. **Datos Adicionales del Vendedor** — Información de contacto y equipo

---

#### Tab 2 — 📊 Comparativa del Equipo

**Filtro:** Selector de equipo (solo admin)

**Gráfico de barras — Puntaje promedio por vendedor del equipo**
- Ordenado de mayor a menor
- Línea de meta (80 puntos)
- Colores: verde (≥80), azul (60-79), naranja (40-59), rojo (<40)

**Tabla resumen del equipo:**
- Columnas: Vendedor | Puntaje | Nivel | Total Evaluaciones

---

#### Tab 3 — 📈 Ranking de Mejora

**Objetivo:** Mostrar qué vendedores mejoraron más entre períodos

**Gráfico de barras — Delta de puntaje entre períodos**
- Ordenado de mayor a menor mejora
- Colores: verde (mejoró), rojo (bajó)

**Tabla de evolución:**
- Columnas: Vendedor | Puntaje P1 | Puntaje P2 | Diferencia | Tendencia

---

### Módulo 4 — 👥 Análisis y Desarrollo de Equipos

**Título:** `COMMAND · Análisis y Desarrollo de Equipos`  
**Estado:** ✅ Activo  
**Objetivo:** Analizar el rendimiento de cada equipo como unidad, comparar equipos entre sí, y generar planes de acción grupales basados en los datos de evaluación IA.

> Solo disponible para Admin y Supervisores.

#### Filtros disponibles
- **Supervisor:** Solo ve su equipo.
- **Admin:** Selector de equipo + comparativa entre todos los equipos.

---

#### Tab 1 — 📋 Análisis por Equipo

**Selector de equipo** (admin) o visualización directa (supervisor)

**Sección — 📈 Métricas del Equipo:**
| Métrica | Descripción |
|---------|-------------|
| 👥 Vendedores | Cantidad de vendedores en el equipo |
| 📊 Puntaje Promedio | Promedio de evaluaciones IA del equipo |
| 📝 Total Evaluaciones | Llamadas evaluadas del equipo |

**Sección — 👥 Detalle por Vendedor:**

**Gráfico de barras — Puntaje por vendedor del equipo**
- Eje X: Nombre del vendedor
- Eje Y: Puntaje promedio IA
- Colores según nivel (excelente / bueno / regular / crítico)

**Sección — 🎯 Plan de Mejora del Equipo**
- Análisis generado por IA para el equipo completo
- Identifica patrones grupales y áreas de mejora colectiva

**Sección — 🤖 Plan de Acción del Equipo**
- Métricas de nivel y puntaje del equipo
- Recomendaciones accionables para el supervisor

---

#### Tab 2 — 📊 Comparativa de Equipos *(solo admin)*

**Gráficos de barras comparativos:**

1. **Puntaje Promedio por Equipo** — Barras verticales por equipo, ordenadas de mayor a menor
2. **% Excelentes (≥80) por Equipo** — Proporción de gestiones destacadas
3. **% Críticos (≤20) por Equipo** — Proporción de gestiones que requieren atención urgente
4. **Total Evaluaciones por Equipo** — Volumen de llamadas procesadas por equipo

**Sección — 🏆 Ranking de Equipos:**
- Tabla con ranking de todos los equipos
- Columnas: Posición | Equipo | Puntaje Promedio | % Excelentes | % Críticos | Total Evaluaciones

---

### Módulo 5 — 📊 Resumen Corporativo

**Título:** `COMMAND · Resumen Corporativo`  
**Estado:** ✅ Activo  
**Objetivo:** Vista consolidada y ejecutiva del rendimiento de equipos y vendedores. Para vendedores del equipo Melanie Carmona, muestra directamente su resumen individual. Para admin/supervisor, permite navegar entre todos los equipos.

#### Vista para Vendedor (equipo Mel)

**Métricas personales:**
| Métrica | Descripción |
|---------|-------------|
| ⭐ Puntaje IA | Puntaje propio con delta vs equipo |
| 📞 Evaluaciones | Total de llamadas evaluadas |

**Indicador de posicionamiento:** Percentil en el equipo

**Gráfico de barras horizontal — Mis Criterios de Evaluación**
- Un bar por cada uno de los 10 criterios
- Colores: rojo (bajo) → naranja → azul → verde (alto)
- Línea de meta en 80 puntos
- Valores visibles en las barras

**Plan de Acción y Coaching** — Análisis IA completo expandible

---

#### Vista para Admin/Supervisor

**Gráfico de barras horizontal por equipo:**
- Puntaje promedio de cada equipo
- Con indicadores de tendencia

**Tabla consolidada de vendedores:**
- Columnas: Vendedor | Equipo | Puntaje IA | Nivel | Evaluaciones | Áreas Críticas

**Plan de acción por equipo:**
- Análisis y recomendaciones IA por equipo

---

### Módulo 6 — 📊 Métricas de Calidad

**Título:** `COMMAND · Métricas de Calidad`  
**Estado:** 🔧 En desarrollo  
**Objetivo:** Mostrar métricas operativas de calidad: tiempos de atención, ventas cerradas, y volumen de llamadas. Integra datos de sistema Mitrol y solicitudes de ventas (Customer).

**Secciones planificadas:**
1. **Tiempos de Atención** — TMO, tiempo en línea, tiempo productivo, distribución de duraciones por vendedor y equipo
2. **Ventas** — Solicitudes procesadas, tasa de conversión, ventas por vendedor y equipo
3. **Llamadas** — Volumen total, llamadas atendidas, abandonadas, cortadas
4. **Comparativa entre períodos** — Evolución semanal de las 3 categorías anteriores

---

### Módulo 7 — 📞 Indicadores de Calidad (Admin)

**Título:** `COMMAND · Indicadores de Calidad y Cumplimiento`  
**Estado:** 🔧 En desarrollo  
**Objetivo:** Análisis avanzado de calidad operativa para administradores, cruzando datos del sistema Mitrol (tiempos) con datos de solicitudes/ventas. Solo accesible para usuario Admin o usuario "calidad".

---

#### Tab 1 — 📤 Carga de Datos

**Carga de archivos:**
- **Archivo Mitrol** (CSV): Acumuladores de agentes — tiempos, métricas de llamadas
- **Archivo Solicitudes** (CSV): Datos de ventas del sistema Customer
- **Mapeo de Vendedores**: Carga automática desde `LISTADO-DE-VENDEDORES.csv`

**Proceso:** Botón "🚀 Procesar y Unificar Datos"
- Normaliza nombres de agentes
- Cruza Mitrol con solicitudes por vendedor
- Resumen post-proceso: Registros Mitrol | Agentes | Solicitudes

---

#### Tab 2 — 📊 Métricas por Vendedor

**Filtros:** Turno, Equipo, Vendedor individual

**Tabla de métricas por agente:**
- TMO (Tiempo Medio de Operación)
- Tiempo logueado
- Tiempo productivo / improductivo
- Llamadas atendidas
- Ventas/solicitudes

**Gráficos:**
- Barras de TMO por vendedor
- Distribución de tiempos (ring chart)

---

#### Tab 3 — 🚦 Semáforos de Tiempo

**Objetivo:** Indicadores visuales de cumplimiento de tiempos estándar.

**Métricas por vendedor:**
| Métrica | Descripción |
|---------|-------------|
| 📞 Total Llamadas | Llamadas del período |
| ✂️ Llamadas Cortadas | Llamadas con duración anormalmente corta |
| 🎯 Captan Atención | Agentes que lograron mantener al cliente |
| 📱 Ya Tiene MVS | Clientes que ya tienen el servicio |
| 📞 Contestador | Llamadas a contestador automático |

**Gráficos:**
- Gráfico de barras: Llamadas totales vs cortadas por vendedor
- Histograma: Distribución de duraciones por vendedor

---

#### Tab 4 — 💰 KPIs de Cumplimiento

**Métricas por vendedor:**
- Ventas realizadas vs objetivo
- % cumplimiento de meta de ventas
- Tasa de contacto efectivo
- Eficiencia (ventas/hora productiva)

**Gráficos:**
- Barras de cumplimiento de meta por vendedor
- Comparativa equipo vs vendedor individual

---

#### Tab 5 — 🏆 Análisis Cruzado (IQC)

**IQC = Índice de Calidad Cruzado**  
Combina métricas de Mitrol (tiempos) con evaluaciones IA (calidad) y ventas (resultados) en un índice unificado.

**Gráfico scatter:** Puntaje IA vs Ventas por vendedor  
**Ranking IQC:** Ordenado por índice compuesto

---

### Módulo 8 — 📅 Comparativa de Períodos

**Título:** `COMMAND · Comparativa de Períodos`  
**Estado:** 🔧 En desarrollo  
**Objetivo:** Comparar el rendimiento entre dos períodos o semanas de trabajo, identificando mejoras, retrocesos y tendencias a nivel equipo y vendedor.

#### Configuración

**Selector de Período 1 (🔵)** y **Período 2 (🔴):**
- Semana 12-16 Enero
- Semana 19-24 Enero
- Personalizado (rango libre)

**Filtro por Equipos:** Multiselect para comparar equipos específicos

---

#### Métricas Comparativas Principales (fila de KPIs):

| Métrica | Descripción |
|---------|-------------|
| 📊 Total Evaluaciones | Cantidad P1 vs P2 con delta |
| ⭐ Puntaje Promedio | Promedio P1 vs P2 con delta |
| 🌟 % Excelentes (≥80) | % en cada período con delta |
| 🔴 % Críticos (≤20) | % en cada período con delta |
| 👥 Agentes Evaluados | Cantidad de agentes en cada período |

---

#### Tab 1 — 📊 Distribución por Rango

**Gráficos de torta — uno por período:**
- Distribución de llamadas en rangos: Crítico | Bajo | Regular | Bueno | Excelente
- Permite ver si la distribución mejoró entre períodos

---

#### Tab 2 — 📈 Comparativa por Criterio

**Gráfico de barras agrupadas:**
- Eje X: Criterios de evaluación (10 criterios)
- Grupos: P1 vs P2
- Permite ver en qué criterios mejoró o bajó el equipo

---

#### Tab 3 — 👥 Evolución por Agente

**Gráficos de barras por vendedor:**
- Puntaje en P1 vs P2
- Ordenado por delta (mejora/caída)
- Colores: verde (mejoró), rojo (bajó)

---

#### Tab 4 — 📋 Detalle Completo

**Tabla comparativa completa:**
- Todos los vendedores con puntaje P1, P2, delta, tendencia, total evaluaciones

---

### Módulo 9 — ⚠️ Gestión de Reclamos y Quejas

**Título:** `COMMAND · Gestión de Reclamos y Quejas Pendientes`  
**Estado:** 🔧 En desarrollo  
**Objetivo:** Identificar y gestionar los reclamos y quejas de clientes que no fueron resueltos durante la llamada, permitiendo al equipo hacer seguimiento y reducir la tasa de quejas no resueltas.

> La implementación está disponible en el código pero temporalmente deshabilitada.

#### Filtros disponibles
- **Vendedor:** Solo ve sus propios reclamos.
- **Supervisor:** Filtro de vendedor dentro de su equipo.
- **Admin:** Filtro por equipo + vendedor.

---

#### Métricas Principales (fila de KPIs):

| Métrica | Descripción |
|---------|-------------|
| 📞 Total Llamadas | Total de llamadas del período |
| 🔍 Analizadas | Llamadas analizadas (excluye ventas cerradas y continuaciones) |
| 😤 Con Queja | Llamadas donde hubo queja detectada por IA |
| ✅ Resueltas | Quejas que el vendedor resolvió en la llamada |
| ❌ NO Resueltas | Quejas que quedaron pendientes |

---

#### Gráficos:

1. **Gráfico de torta tipo donut — "Estado de Quejas"**
   - Segmentos: Resueltas (verde) vs No Resueltas (rojo)
   - Con porcentajes y valores

2. **Gráfico de barras horizontal — "Tipos de Quejas No Resueltas"**
   - Muestra las categorías de queja más frecuentes (ej: precio, cobertura, facturación)
   - Colores en escala roja según gravedad

3. **Gráfico de barras apiladas — "Agentes con Más Quejas No Resueltas"**
   - Eje X: Nombre del agente
   - Barras apiladas: Resueltas (verde) + No Resueltas (rojo)
   - Tabla debajo con detalle: Agente | Total Quejas | Resueltas | No Resueltas | % No Resueltas

4. **Tabla de Detalle — "Detalle de Quejas No Resueltas"**
   - Columnas: Agente | ID Interacción | Duración (seg) | Cant. Quejas | No Resueltas | Primera Queja

---

## Sistema de Login

El dashboard requiere autenticación. La pantalla de login muestra:
- Logo COMMAND
- Formulario de usuario y contraseña
- Iconos de características: Análisis de Datos · Gestión de Equipos · Mejora Continua

Los usuarios y credenciales están definidos en el archivo `credenciales_eva.csv`.

> ⚠️ **Nota de seguridad:** El almacenamiento de credenciales en un archivo CSV es apropiado únicamente para entornos de desarrollo o prototipado. Para producción se recomienda migrar a un sistema de autenticación seguro (base de datos con contraseñas hasheadas, OAuth 2.0, o un servicio de identidad dedicado).

---

## Flujo de Datos

```
Llamadas grabadas
        │
        ▼
1_scraper_eva.py — Descarga y preprocesa audio
        │
        ▼
3_speech_eva.py — Transcripción de audio a texto
        │
        ▼
4_evaluacion_gemini.py — Evaluación IA con Gemini
        │
        ▼
reportes/evaluaciones_gemini.csv — Datos procesados
        │
        ▼
dashboard_eva.py — Dashboard visual (COMMAND)
```

---

## Tecnologías Utilizadas

| Componente | Tecnología |
|------------|------------|
| Frontend / Dashboard | Streamlit |
| Gráficos interactivos | Plotly Express + Plotly Graph Objects |
| Procesamiento de datos | Pandas + NumPy |
| Evaluación IA | Google Gemini API |
| Transcripción | Speech-to-text |
| Estilos | CSS personalizado embebido |
| Autenticación | Sistema propio con hash SHA-256 |

---

## Resumen de Módulos y Estado

| # | Módulo | Ícono | Estado | Disponible para |
|---|--------|-------|--------|----------------|
| 1 | Análisis de Productos | 📱 | ✅ Activo | Todos |
| 2 | Evaluación Automatizada IA | 🤖 | ✅ Activo | Todos |
| 3 | Planes de Mejora / Coaching | 🎯 | ✅ Activo | Todos |
| 4 | Análisis de Equipos | 👥 | ✅ Activo | Admin / Supervisor |
| 5 | Resumen Corporativo | 📊 | ✅ Activo | Todos |
| 6 | Métricas de Calidad | 📊 | 🔧 En desarrollo | Admin / Supervisor |
| 7 | Indicadores de Calidad (Admin) | 📞 | 🔧 En desarrollo | Admin / Calidad |
| 8 | Comparativa de Períodos | 📅 | 🔧 En desarrollo | Admin |
| 9 | Gestión de Reclamos y Quejas | ⚠️ | 🔧 En desarrollo | Todos |

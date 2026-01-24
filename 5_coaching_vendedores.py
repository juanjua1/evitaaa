"""
Script de Coaching IA para Vendedores
Genera análisis exhaustivos y planes de acción personalizados usando Gemini Pro
Actúa como un Jefe de Ventas experimentado
"""

import os
import json
import pandas as pd
from datetime import datetime
import time
import sys

# Suprimir warnings
import warnings
warnings.filterwarnings("ignore")

import google.generativeai as genai
from config import api_key

# Configurar API
genai.configure(api_key=api_key)

# Usar modelo más potente para análisis exhaustivo
MODEL_NAME = "gemini-2.0-flash"  # Más capaz que lite, bueno para análisis complejos

# Directorios
DIR_REPORTES = "reportes"
DIR_COACHING = os.path.join(DIR_REPORTES, "coaching_vendedores")
os.makedirs(DIR_COACHING, exist_ok=True)

def log(mensaje, tipo="info"):
    """Logger con timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    emoji = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}.get(tipo, "")
    print(f"[{timestamp}] {emoji} {mensaje}")


def cargar_datos_completos():
    """Carga todos los datos disponibles para el análisis"""
    datos = {}
    
    # Cargar evaluaciones de Gemini
    ruta_eval = os.path.join(DIR_REPORTES, "evaluaciones_gemini.csv")
    if os.path.exists(ruta_eval):
        datos['evaluaciones'] = pd.read_csv(ruta_eval)
        log(f"Cargadas {len(datos['evaluaciones'])} evaluaciones de IA")
    
    # Cargar clasificación completa
    ruta_clasif = os.path.join(DIR_REPORTES, "clasificacion_completa", "clasificacion_completa.csv")
    if os.path.exists(ruta_clasif):
        datos['clasificacion'] = pd.read_csv(ruta_clasif)
        log(f"Cargadas {len(datos['clasificacion'])} clasificaciones")
    
    # Cargar análisis integral
    ruta_integral = os.path.join(DIR_REPORTES, "analisis_integral", "analisis_integral.csv")
    if os.path.exists(ruta_integral):
        datos['integral'] = pd.read_csv(ruta_integral)
        log(f"Cargados {len(datos['integral'])} registros integrales")
    
    # Cargar cierres comerciales
    ruta_cierres = os.path.join(DIR_REPORTES, "cierres_comerciales", "cierres_comerciales.csv")
    if os.path.exists(ruta_cierres):
        datos['cierres'] = pd.read_csv(ruta_cierres, sep=';')
        log(f"Cargados {len(datos['cierres'])} cierres comerciales")
    
    return datos


def obtener_metricas_agente(agente, datos):
    """Recopila todas las métricas disponibles de un agente"""
    metricas = {
        'agente': agente,
        'evaluaciones': {},
        'clasificacion': {},
        'integral': {},
        'cierres': {}
    }
    
    # Métricas de evaluaciones IA
    if 'evaluaciones' in datos:
        df_ag = datos['evaluaciones'][datos['evaluaciones']['agente'] == agente]
        if len(df_ag) > 0:
            metricas['evaluaciones'] = {
                'total_evaluadas': len(df_ag),
                'puntaje_promedio': round(df_ag['puntaje_total'].mean(), 1),
                'puntaje_min': df_ag['puntaje_total'].min(),
                'puntaje_max': df_ag['puntaje_total'].max(),
                'desviacion_std': round(df_ag['puntaje_total'].std(), 1),
                'llamadas_excelentes': len(df_ag[df_ag['puntaje_total'] >= 80]),
                'llamadas_criticas': len(df_ag[df_ag['puntaje_total'] <= 20]),
                'criterios': {}
            }
            
            # Puntajes por criterio
            criterios = ['saludo_presentacion', 'identificacion_cliente', 'deteccion_necesidades',
                        'oferta_productos', 'manejo_objeciones', 'cierre', 'despedida',
                        'proactividad', 'empatia', 'resolucion_problemas']
            
            for c in criterios:
                if c in df_ag.columns:
                    metricas['evaluaciones']['criterios'][c] = round(df_ag[c].mean(), 1)
            
            # Áreas de mejora frecuentes
            areas_mejora = []
            for areas in df_ag['areas_mejora'].dropna():
                if isinstance(areas, str):
                    for area in areas.split(','):
                        area = area.strip().strip('"').strip("'").strip('[').strip(']')
                        if area:
                            areas_mejora.append(area)
            
            if areas_mejora:
                from collections import Counter
                metricas['evaluaciones']['areas_mejora_frecuentes'] = dict(Counter(areas_mejora).most_common(5))
            
            # Fortalezas
            fortalezas = []
            for fort in df_ag['fortalezas'].dropna():
                if isinstance(fort, str):
                    for f in fort.split(','):
                        f = f.strip().strip('"').strip("'").strip('[').strip(']')
                        if f:
                            fortalezas.append(f)
            
            if fortalezas:
                from collections import Counter
                metricas['evaluaciones']['fortalezas_frecuentes'] = dict(Counter(fortalezas).most_common(5))
            
            # Ejemplos de resúmenes (las 3 mejores y 3 peores)
            mejores = df_ag.nlargest(3, 'puntaje_total')[['puntaje_total', 'resumen']].to_dict('records')
            peores = df_ag.nsmallest(3, 'puntaje_total')[['puntaje_total', 'resumen']].to_dict('records')
            metricas['evaluaciones']['ejemplos_mejores'] = mejores
            metricas['evaluaciones']['ejemplos_peores'] = peores
    
    # Métricas de clasificación
    if 'clasificacion' in datos:
        df_ag = datos['clasificacion'][datos['clasificacion']['agente'] == agente]
        if len(df_ag) > 0:
            metricas['clasificacion'] = {
                'total_llamadas': len(df_ag),
                'con_saludo': len(df_ag[df_ag.get('tiene_saludo', False) == True]) if 'tiene_saludo' in df_ag.columns else 0,
                'con_cierre': len(df_ag[df_ag.get('tiene_cierre', False) == True]) if 'tiene_cierre' in df_ag.columns else 0,
                'con_identificacion': len(df_ag[df_ag.get('tiene_identificacion', False) == True]) if 'tiene_identificacion' in df_ag.columns else 0,
                'ofrece_plan': len(df_ag[df_ag.get('ofrece_plan', False) == True]) if 'ofrece_plan' in df_ag.columns else 0,
                'ofrece_fibra': len(df_ag[df_ag.get('ofrece_fibra', False) == True]) if 'ofrece_fibra' in df_ag.columns else 0,
                'ventas': len(df_ag[df_ag.get('es_venta', False) == True]) if 'es_venta' in df_ag.columns else 0,
                'score_calidad_prom': round(df_ag['score_calidad'].mean(), 1) if 'score_calidad' in df_ag.columns else 0,
            }
            
            # Calcular porcentajes
            total = metricas['clasificacion']['total_llamadas']
            if total > 0:
                metricas['clasificacion']['pct_saludo'] = round(metricas['clasificacion']['con_saludo'] / total * 100, 1)
                metricas['clasificacion']['pct_cierre'] = round(metricas['clasificacion']['con_cierre'] / total * 100, 1)
                metricas['clasificacion']['pct_plan'] = round(metricas['clasificacion']['ofrece_plan'] / total * 100, 1)
                metricas['clasificacion']['pct_fibra'] = round(metricas['clasificacion']['ofrece_fibra'] / total * 100, 1)
                metricas['clasificacion']['tasa_conversion'] = round(metricas['clasificacion']['ventas'] / total * 100, 1)
    
    # Métricas integrales (duración, etc.)
    if 'integral' in datos:
        df_ag = datos['integral'][datos['integral']['agente'] == agente]
        if len(df_ag) > 0:
            metricas['integral'] = {
                'duracion_promedio_seg': round(df_ag['duracion_seg'].mean(), 0) if 'duracion_seg' in df_ag.columns else 0,
                'duracion_promedio_min': round(df_ag['duracion_seg'].mean() / 60, 1) if 'duracion_seg' in df_ag.columns else 0,
            }
            
            # Distribución por rango de duración
            if 'rango_duracion' in df_ag.columns:
                rangos = df_ag['rango_duracion'].value_counts().to_dict()
                metricas['integral']['distribucion_duracion'] = rangos
    
    # Métricas de cierres
    if 'cierres' in datos:
        df_ag = datos['cierres'][datos['cierres']['agente'] == agente]
        if len(df_ag) > 0:
            metricas['cierres'] = {
                'total_ventas': len(df_ag),
                'porcentaje_cierre_prom': round(df_ag['porcentaje'].mean(), 1) if 'porcentaje' in df_ag.columns else 0,
            }
    
    return metricas


def calcular_comparativa_general(agente, datos):
    """Calcula cómo se compara el agente con el promedio general"""
    comparativa = {}
    
    if 'evaluaciones' in datos:
        df = datos['evaluaciones']
        df_ag = df[df['agente'] == agente]
        
        if len(df_ag) > 0:
            prom_general = df['puntaje_total'].mean()
            prom_agente = df_ag['puntaje_total'].mean()
            
            comparativa['puntaje_ia'] = {
                'agente': round(prom_agente, 1),
                'general': round(prom_general, 1),
                'diferencia': round(prom_agente - prom_general, 1),
                'percentil': round((df['puntaje_total'] < prom_agente).mean() * 100, 1)
            }
            
            # Por criterio
            criterios = ['saludo_presentacion', 'identificacion_cliente', 'deteccion_necesidades',
                        'oferta_productos', 'manejo_objeciones', 'cierre', 'despedida',
                        'proactividad', 'empatia', 'resolucion_problemas']
            
            comparativa['criterios'] = {}
            for c in criterios:
                if c in df.columns and c in df_ag.columns:
                    prom_gen = df[c].mean()
                    prom_ag = df_ag[c].mean()
                    comparativa['criterios'][c] = {
                        'agente': round(prom_ag, 1),
                        'general': round(prom_gen, 1),
                        'diferencia': round(prom_ag - prom_gen, 1)
                    }
    
    if 'clasificacion' in datos:
        df = datos['clasificacion']
        df_ag = df[df['agente'] == agente]
        
        if len(df_ag) > 0 and 'es_venta' in df.columns:
            tasa_general = df['es_venta'].mean() * 100
            tasa_agente = df_ag['es_venta'].mean() * 100
            
            comparativa['conversion'] = {
                'agente': round(tasa_agente, 1),
                'general': round(tasa_general, 1),
                'diferencia': round(tasa_agente - tasa_general, 1)
            }
    
    return comparativa


def generar_prompt_coaching(agente, metricas, comparativa, metricas_generales):
    """Genera el prompt para el análisis de coaching"""
    
    prompt = f"""
Eres un JEFE DE VENTAS experimentado y mentor de alto rendimiento en telecomunicaciones (Movistar Argentina). 
Tu misión es analizar exhaustivamente el desempeño del vendedor y crear un plan de acción 
personalizado para ayudarlo a alcanzar su MÁXIMO POTENCIAL.

## ⚠️ REGLAS CRÍTICAS DEL NEGOCIO (OBLIGATORIAS):

### FRASES PROHIBIDAS - NUNCA SUGERIR:
- "¿Te parece bien si...?" → NO se pregunta, se procede directamente
- "¿Le gustaría que...?" → Frase prohibida de cierre
- "¿Te interesaría conocer...?" → NO se pregunta, se comenta directamente
- "Podría interesarle" → Debe decir "LE VA a interesar"
- "Período de prueba gratuito" → NO EXISTE
- "Estaré encantado de ayudarte en el futuro" → Solo acompañamiento durante portabilidad
- "Vi que visitó nuestra página web" → NO tienen acceso a esa info
- "Investigar necesidades antes de la llamada" → NO se puede hacer

### ACCIONES CORRECTAS POR CRITERIO:

1. **IDENTIFICACIÓN DEL CLIENTE**: 
   - CORRECTO: "Hola, ¿me comunico con [Nombre]?" para verificar que es la persona correcta
   - Es IMPORTANTE verificar identidad para asegurar contacto correcto

2. **DETECCIÓN DE NECESIDADES**:
   - INCORRECTO: "¿Qué es lo más importante para ti en un plan?"
   - CORRECTO: "¿Qué es lo que más usás del celular?" / "¿Cuántos GB tenés en tu plan?"

3. **CIERRE DE VENTAS**:
   - NUNCA preguntar "¿te parece bien si procedemos?" 
   - CORRECTO: Asignar sucursal directamente o buscar domicilio del cliente
   - REGLA: Nunca preguntar si quiere seguir, DIRECTAMENTE proceder

4. **DESPEDIDA**:
   - INCORRECTO: "Estaré encantado de ayudarte en el futuro"
   - CORRECTO: Ofrecer acompañamiento SOLO durante la portabilidad

5. **OFERTA DE FIBRA (Proactividad)**:
   - INCORRECTO: "¿Te interesaría conocer nuestros servicios de fibra?"
   - CORRECTO: Comentar DIRECTAMENTE sobre fibra sin preguntar
   - REGLA: TODOS deben ofrecer fibra de forma directa, sin preguntar

6. **MANEJO DE OBJECIONES**:
   - INCORRECTO: Respuestas genéricas iguales para todos
   - CORRECTO: Rebatir la objeción PUNTUAL de CADA cliente
   - Sincronizar/personalizar la respuesta según el cliente específico

7. **SALUDO Y PRESENTACIÓN**:
   - INCORRECTO: "Tengo una oferta que podría interesarle"
   - CORRECTO: "Tengo una oferta que le VA a interesar"
   - NO personalizar con info de visitas web (no tienen acceso)

8. **MANEJO DE PRECIO**:
   - INCORRECTO: Textos muy formales/corporativos
   - CORRECTO: "Es lógico que mires el precio. A varios clientes les pasó eso al comienzo, y cuando empezaron a usar la conexión y vieron la diferencia en el servicio, entendieron que el valor estaba ahí."

## VENDEDOR A ANALIZAR: {agente}

## DATOS DEL VENDEDOR:

### 📊 MÉTRICAS DE EVALUACIÓN IA:
{json.dumps(metricas.get('evaluaciones', {}), indent=2, ensure_ascii=False)}

### 📋 MÉTRICAS DE CLASIFICACIÓN:
{json.dumps(metricas.get('clasificacion', {}), indent=2, ensure_ascii=False)}

### ⏱️ MÉTRICAS DE DURACIÓN:
{json.dumps(metricas.get('integral', {}), indent=2, ensure_ascii=False)}

### 💰 MÉTRICAS DE CIERRES:
{json.dumps(metricas.get('cierres', {}), indent=2, ensure_ascii=False)}

## COMPARATIVA CON EL EQUIPO:
{json.dumps(comparativa, indent=2, ensure_ascii=False)}

## PROMEDIOS GENERALES DEL EQUIPO:
- Puntaje IA promedio del equipo: {metricas_generales.get('puntaje_prom_equipo', 'N/A')}
- Tasa de conversión del equipo: {metricas_generales.get('tasa_conversion_equipo', 'N/A')}%
- Total de agentes: {metricas_generales.get('total_agentes', 'N/A')}

---

## TU ANÁLISIS DEBE INCLUIR:

### 1. DIAGNÓSTICO GENERAL (2-3 párrafos)
- ¿Cómo está este vendedor comparado con el equipo?
- ¿Cuál es su nivel actual? (Crítico / Necesita Mejora / Promedio / Bueno / Excelente)
- ¿Cuál es su potencial de mejora?

### 2. FORTALEZAS IDENTIFICADAS (mínimo 3)
- Aspectos positivos que debe mantener y potenciar
- Ejemplos concretos de lo que hace bien

### 3. ÁREAS CRÍTICAS DE MEJORA (mínimo 3)
- Debilidades que impactan directamente en sus resultados
- Por qué cada área es importante mejorar

### 4. ANÁLISIS DETALLADO POR COMPETENCIA
Para cada criterio evaluado, indica:
- Nivel actual (Crítico/Bajo/Regular/Bueno/Excelente)
- Qué está haciendo mal o bien
- Cómo mejorar específicamente (RESPETANDO LAS REGLAS DEL NEGOCIO)

### 5. PLAN DE ACCIÓN SEMANAL (4 semanas)
**Semana 1:** [Foco principal y acciones específicas]
**Semana 2:** [Siguiente prioridad]
**Semana 3:** [Consolidación]
**Semana 4:** [Optimización]

### 6. TÉCNICAS Y SCRIPTS RECOMENDADOS
⚠️ IMPORTANTE: Todas las frases y scripts deben respetar las REGLAS DEL NEGOCIO listadas arriba.
- Frases específicas para verificar identidad del cliente
- Preguntas correctas para detectar necesidades ("¿Qué es lo que más usás del celular?")
- Cómo ofrecer fibra de forma directa (sin preguntar si le interesa)
- Técnicas de cierre DIRECTO (asignar sucursal, buscar domicilio)
- Manejo de objeciones personalizado según tipo de cliente

### 7. METAS CUANTIFICABLES
- Meta de puntaje IA a alcanzar en 30 días
- Meta de tasa de conversión
- Meta de ofrecimiento de productos
- KPIs específicos a mejorar

### 8. MENSAJE MOTIVACIONAL PERSONALIZADO
Un mensaje directo y motivador para este vendedor, reconociendo su esfuerzo
y visualizando su potencial de crecimiento.

---

IMPORTANTE: 
- Sé específico y práctico, no genérico
- Usa los datos proporcionados para personalizar cada recomendación
- El tono debe ser de mentor que cree en el potencial del vendedor
- Las acciones deben ser ejecutables y medibles
- NO incluyas frases introductorias como "¡Aquí tienes!", "¡Absolutamente!", "¡Claro!" o similares
- Empieza DIRECTAMENTE con el título "## ANÁLISIS DEL VENDEDOR: {agente}"
- NO repitas el nombre del vendedor en frases introductorias innecesarias
"""
    
    return prompt


def generar_coaching_agente(agente, datos, model, metricas_generales):
    """Genera el análisis de coaching para un agente"""
    
    # Obtener métricas del agente
    metricas = obtener_metricas_agente(agente, datos)
    comparativa = calcular_comparativa_general(agente, datos)
    
    # Verificar que hay suficientes datos
    if metricas['evaluaciones'].get('total_evaluadas', 0) < 3:
        return None, "Insuficientes evaluaciones (mínimo 3)"
    
    # Generar prompt
    prompt = generar_prompt_coaching(agente, metricas, comparativa, metricas_generales)
    
    try:
        response = model.generate_content(prompt)
        analisis = response.text
        
        # Estructurar resultado
        resultado = {
            'agente': agente,
            'fecha_generacion': datetime.now().isoformat(),
            'metricas': metricas,
            'comparativa': comparativa,
            'analisis_coaching': analisis,
            'modelo_usado': MODEL_NAME
        }
        
        return resultado, None
        
    except Exception as e:
        return None, str(e)


def main():
    print("\n" + "="*70)
    print("  🎯 GENERADOR DE COACHING PERSONALIZADO CON IA")
    print("  📊 Análisis exhaustivo para cada vendedor")
    print("="*70 + "\n")
    
    # Cargar datos
    log("Cargando todos los datos disponibles...")
    datos = cargar_datos_completos()
    
    if 'evaluaciones' not in datos:
        log("No se encontraron evaluaciones de IA. Ejecuta primero 4_evaluacion_gemini.py", "error")
        return
    
    # Inicializar modelo
    log(f"Inicializando modelo {MODEL_NAME}...")
    model = genai.GenerativeModel(MODEL_NAME)
    
    # Obtener lista de agentes con suficientes datos
    df_eval = datos['evaluaciones']
    agentes_counts = df_eval['agente'].value_counts()
    agentes_validos = agentes_counts[agentes_counts >= 3].index.tolist()
    
    log(f"Agentes con suficientes datos: {len(agentes_validos)}")
    
    # Calcular métricas generales
    metricas_generales = {
        'puntaje_prom_equipo': round(df_eval['puntaje_total'].mean(), 1),
        'tasa_conversion_equipo': round(datos['clasificacion']['es_venta'].mean() * 100, 1) if 'clasificacion' in datos and 'es_venta' in datos['clasificacion'].columns else 'N/A',
        'total_agentes': len(agentes_validos)
    }
    
    # Cargar coaching existente
    archivo_coaching = os.path.join(DIR_COACHING, "coaching_completo.json")
    if os.path.exists(archivo_coaching):
        with open(archivo_coaching, 'r', encoding='utf-8') as f:
            coaching_existente = json.load(f)
        agentes_procesados = [c['agente'] for c in coaching_existente]
        log(f"Coaching existente: {len(agentes_procesados)} agentes")
    else:
        coaching_existente = []
        agentes_procesados = []
    
    # Filtrar agentes pendientes
    if len(sys.argv) > 1:
        max_agentes = int(sys.argv[1])
        log(f"Procesando máximo {max_agentes} agentes")
    else:
        max_agentes = len(agentes_validos)
    
    agentes_pendientes = [a for a in agentes_validos if a not in agentes_procesados][:max_agentes]
    
    if not agentes_pendientes:
        log("Todos los agentes ya tienen coaching generado", "success")
        return
    
    log(f"Pendientes a procesar: {len(agentes_pendientes)}")
    print("-" * 70)
    
    # Procesar cada agente
    resultados = coaching_existente.copy()
    errores = 0
    
    for i, agente in enumerate(agentes_pendientes, 1):
        print(f"\n[{i}/{len(agentes_pendientes)}] Generando coaching para: {agente}")
        log("Recopilando datos del agente...")
        
        resultado, error = generar_coaching_agente(agente, datos, model, metricas_generales)
        
        if error:
            log(f"Error: {error}", "error")
            errores += 1
            continue
        
        resultados.append(resultado)
        log(f"Coaching generado exitosamente", "success")
        
        # Guardar individual
        archivo_individual = os.path.join(DIR_COACHING, f"coaching_{agente.replace(' ', '_')}.json")
        with open(archivo_individual, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        
        # Guardar consolidado
        with open(archivo_coaching, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)
        
        # Rate limiting (3 segundos para modelo más potente)
        if i < len(agentes_pendientes):
            log("Esperando 3 segundos (rate limiting)...")
            time.sleep(3)
    
    # Generar CSV resumen
    log("\nGenerando resumen CSV...")
    
    resumen_data = []
    for r in resultados:
        metricas = r.get('metricas', {})
        eval_data = metricas.get('evaluaciones', {})
        clasif_data = metricas.get('clasificacion', {})
        
        resumen_data.append({
            'agente': r['agente'],
            'fecha_coaching': r['fecha_generacion'],
            'puntaje_ia': eval_data.get('puntaje_promedio', 0),
            'llamadas_evaluadas': eval_data.get('total_evaluadas', 0),
            'llamadas_excelentes': eval_data.get('llamadas_excelentes', 0),
            'llamadas_criticas': eval_data.get('llamadas_criticas', 0),
            'tasa_conversion': clasif_data.get('tasa_conversion', 0),
            'pct_saludo': clasif_data.get('pct_saludo', 0),
            'pct_cierre': clasif_data.get('pct_cierre', 0),
            'tiene_coaching': True
        })
    
    df_resumen = pd.DataFrame(resumen_data)
    df_resumen.to_csv(os.path.join(DIR_COACHING, "resumen_coaching.csv"), index=False)
    
    # Resumen final
    print("\n" + "="*70)
    log("PROCESO FINALIZADO", "success")
    log(f"Coaching generado: {len(resultados)} agentes")
    log(f"Errores: {errores}")
    log(f"Archivos en: {DIR_COACHING}")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

"""
Mejora de Transcripciones con Gemini - Equipo Melanie Carmona
==============================================================
Toma las transcripciones de WhisperX y las pasa por Gemini para:
1. Corregir errores de transcripción de Whisper (nombres, planes, etc.)
2. Identificar quién es AGENTE y quién es CLIENTE
3. Mejorar coherencia del texto
4. Detectar tipo de llamada y resultado

Fecha: Febrero 2026
"""

import json
import os
import time
import re
import threading
import google.generativeai as genai
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

BASE_DIR = Path(r"C:\Users\rodri\Documents\codigo-WC\eva")
INPUT_DIR = BASE_DIR / "transcripciones"
OUTPUT_DIR = BASE_DIR / "transcripciones_mejoradas"
REPORTE_DIR = BASE_DIR / "reportes" / "mejora_gemini"

# API Key
from config import api_key
API_KEY = api_key

MODEL_NAME = "gemini-2.0-flash-lite"
DELAY_BETWEEN_CALLS = 0.5  # Segundos entre llamadas
MAX_RETRIES = 3
NUM_WORKERS = 5  # Instancias paralelas
MAX_OUTPUT_TOKENS = 65536  # Flash-lite soporta hasta 65536 tokens
MAX_INPUT_SEGMENTS = 500   # Limitar segmentos para evitar respuestas truncadas

# ============================================================================
# PROMPT DE MEJORA
# ============================================================================

PROMPT_MEJORA = """Eres un experto en corrección y mejora de transcripciones automáticas de un call center de ventas de Movistar Argentina (Mendoza).

## TRANSCRIPCIÓN ORIGINAL (generada por WhisperX, puede tener errores):
{transcripcion}

## TAREA
Analiza y mejora esta transcripción. Debes:

1. **CORREGIR ERRORES DE WHISPER**: Whisper suele transcribir mal:
   - "gigas" → aparece como "llenas", "llegas", "libras", "sigas", "chicas", etc.
   - Nombres propios mal escritos
   - Palabras cortadas o sin sentido
   - "fibra" → puede aparecer como "libra", "fila", etc.
   - Números y planes (ej: "plan de 15", "plan de 20 gigas")

2. **IDENTIFICAR ROLES**: Determina quién es el AGENTE (vendedor Movistar) y quién es el CLIENTE.
   - AGENTE: Se presenta ("Habla con X de Movistar"), ofrece productos, valida datos
   - CLIENTE: Responde, pregunta precios, acepta/rechaza

3. **CLASIFICAR LA LLAMADA**:
   - Tipo: VENTA | SEGUIMIENTO | RECLAMO | SIN_CONTACTO | NO_ATENDIDA
   - Resultado: VENTA_EXITOSA | RECHAZO | PENDIENTE | SIN_DECISION | CORTE

4. **PRODUCTOS MENCIONADOS**: Lista los planes/productos ofrecidos (ej: "plan 15gb", "fibra 100mb", "combo fibra+móvil")

RESPONDE SOLO con este JSON (sin texto adicional, sin markdown):
{{
  "conversacion_mejorada": [
    {{
      "hablante": "AGENTE" o "CLIENTE",
      "inicio": <número>,
      "fin": <número>,
      "texto": "<texto corregido y mejorado>"
    }}
  ],
  "analisis": {{
    "agente_detectado": "Hablante A" o "Hablante B",
    "confianza_roles": "ALTA" | "MEDIA" | "BAJA",
    "tipo_llamada": "VENTA" | "SEGUIMIENTO" | "RECLAMO" | "SIN_CONTACTO" | "NO_ATENDIDA",
    "resultado": "VENTA_EXITOSA" | "RECHAZO" | "PENDIENTE" | "SIN_DECISION" | "CORTE",
    "productos_mencionados": [],
    "plan_vendido": null,
    "incluye_fibra": false,
    "calidad_transcripcion_original": "BUENA" | "REGULAR" | "MALA",
    "correcciones_realizadas": "<breve descripción de qué se corrigió>"
  }}
}}
"""

# ============================================================================
# FUNCIONES
# ============================================================================

def configurar_gemini():
    genai.configure(api_key=API_KEY)
    return genai.GenerativeModel(MODEL_NAME)


def formatear_transcripcion(conversacion):
    """Formatea la conversación para el prompt."""
    lineas = []
    for seg in conversacion:
        hablante = seg.get('hablante', 'Desconocido')
        texto = seg.get('texto', '')
        inicio = seg.get('inicio', 0)
        fin = seg.get('fin', 0)
        lineas.append(f"[{inicio:.1f}s-{fin:.1f}s] {hablante}: {texto}")
    return '\n'.join(lineas)


def limpiar_json_response(texto):
    """Limpia la respuesta de Gemini para obtener JSON válido."""
    texto = texto.strip()
    
    # Quitar markdown
    if texto.startswith('```json'):
        texto = texto[7:]
    if texto.startswith('```'):
        texto = texto[3:]
    if texto.endswith('```'):
        texto = texto[:-3]
    texto = texto.strip()
    
    return texto


def reparar_json_truncado(texto):
    """Intenta reparar JSON truncado cerrando estructuras abiertas."""
    texto = texto.strip()
    if not texto:
        return texto
    
    # Si ya es válido, retornar
    try:
        json.loads(texto)
        return texto
    except json.JSONDecodeError:
        pass
    
    # Estrategia 1: Encontrar el último objeto/array completo
    # Buscar el ultimo cierre de llave balanceado
    depth_curly = 0
    depth_bracket = 0
    last_valid_pos = -1
    in_string = False
    escape_next = False
    
    for i, c in enumerate(texto):
        if escape_next:
            escape_next = False
            continue
        if c == '\\':
            if in_string:
                escape_next = True
            continue
        if c == '"' and not escape_next:
            in_string = not in_string
            continue
        if in_string:
            continue
        if c == '{':
            depth_curly += 1
        elif c == '}':
            depth_curly -= 1
            if depth_curly == 0:
                last_valid_pos = i
        elif c == '[':
            depth_bracket += 1
        elif c == ']':
            depth_bracket -= 1
    
    # Si encontramos un cierre balanceado de nivel 0, truncar ahí
    if last_valid_pos > 0:
        candidato = texto[:last_valid_pos + 1]
        try:
            json.loads(candidato)
            return candidato
        except json.JSONDecodeError:
            pass
    
    # Estrategia 2: Reparación por fuerza bruta — cerrar lo que falta
    reparado = texto
    
    # Si estamos dentro de un string, cerrarlo
    # Contar comillas no escapadas
    comillas = 0
    esc = False
    for c in reparado:
        if esc:
            esc = False
            continue
        if c == '\\':
            esc = True
            continue
        if c == '"':
            comillas += 1
    
    if comillas % 2 != 0:
        # String sin cerrar — quitar el último string incompleto
        # Buscar la última comilla de apertura
        last_quote = reparado.rfind('"')
        if last_quote > 0:
            # Buscar el inicio de este par key/value y truncar
            corte = reparado.rfind(',', 0, last_quote)
            corte2 = reparado.rfind('[', 0, last_quote)
            corte3 = reparado.rfind('{', 0, last_quote)
            corte = max(corte, corte2, corte3)
            if corte > 0:
                if reparado[corte] == ',':
                    reparado = reparado[:corte]
                else:
                    reparado = reparado[:corte + 1]
    
    # Ahora cerrar brackets/braces abiertos
    depth_curly = 0
    depth_bracket = 0
    in_str = False
    esc = False
    for c in reparado:
        if esc:
            esc = False
            continue
        if c == '\\':
            if in_str:
                esc = True
            continue
        if c == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if c == '{':
            depth_curly += 1
        elif c == '}':
            depth_curly -= 1
        elif c == '[':
            depth_bracket += 1
        elif c == ']':
            depth_bracket -= 1
    
    # Cerrar lo que falte
    reparado += ']' * max(0, depth_bracket)
    reparado += '}' * max(0, depth_curly)
    
    try:
        json.loads(reparado)
        return reparado
    except json.JSONDecodeError:
        pass
    
    # Estrategia 3: Extraer el array conversacion_mejorada al menos
    match = re.search(r'"conversacion_mejorada"\s*:\s*\[', texto)
    if match:
        start = match.end() - 1  # posición del [
        # Encontrar el cierre del array
        depth = 0
        last_complete_item = start
        in_s = False
        esc = False
        for i in range(start, len(texto)):
            c = texto[i]
            if esc:
                esc = False
                continue
            if c == '\\' and in_s:
                esc = True
                continue
            if c == '"':
                in_s = not in_s
                continue
            if in_s:
                continue
            if c == '[':
                depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0:
                    last_complete_item = i
                    break
            elif c == '}' and depth == 1:
                last_complete_item = i
        
        array_text = texto[start:last_complete_item + 1]
        if not array_text.endswith(']'):
            # Truncar hasta el último } completo dentro del array
            lp = array_text.rfind('}')
            if lp > 0:
                array_text = array_text[:lp + 1] + ']'
        
        # Construir JSON mínimo
        minimal = '{"conversacion_mejorada": ' + array_text + ', "analisis": {"tipo_llamada": "VENTA", "resultado": "PENDIENTE", "calidad_transcripcion_original": "REGULAR", "correcciones_realizadas": "reparación parcial por truncamiento"}}'
        try:
            json.loads(minimal)
            return minimal
        except json.JSONDecodeError:
            pass
    
    return texto  # Devolver sin cambios, dejará que falle


def procesar_con_gemini(model, transcripcion_text):
    """Envía transcripción a Gemini y obtiene mejora."""
    
    prompt = PROMPT_MEJORA.format(transcripcion=transcripcion_text)
    
    for intento in range(MAX_RETRIES):
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=MAX_OUTPUT_TOKENS,
                    response_mime_type="application/json",
                )
            )
            
            texto_resp = limpiar_json_response(response.text)
            
            # Intento 1: parsear directamente
            try:
                return json.loads(texto_resp)
            except json.JSONDecodeError:
                pass
            
            # Intento 2: reparación robusta de JSON truncado
            try:
                reparado = reparar_json_truncado(texto_resp)
                resultado = json.loads(reparado)
                print(f"🔧", end="")
                return resultado
            except json.JSONDecodeError as e:
                raise e
                    
        except json.JSONDecodeError as e:
            print(f"      ⚠️ JSON inválido (intento {intento+1}): {str(e)[:50]}")
            if intento < MAX_RETRIES - 1:
                time.sleep(2)
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower() or "resource" in error_msg.lower():
                wait = 30 * (intento + 1)
                print(f"      ⚠️ Rate limit, esperando {wait}s...")
                time.sleep(wait)
            else:
                print(f"      ❌ Error Gemini (intento {intento+1}): {str(e)[:60]}")
                if intento < MAX_RETRIES - 1:
                    time.sleep(3)
    
    return None


def procesar_archivo(model, json_path):
    """Procesa un archivo de transcripción."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        conversacion = data.get('conversacion', [])
        if not conversacion or len(conversacion) < 2:
            return {"status": "skip", "archivo": json_path.name, "msg": "Sin conversación suficiente"}
        
        # Limitar segmentos para evitar respuestas truncadas
        if len(conversacion) > MAX_INPUT_SEGMENTS:
            conversacion = conversacion[:MAX_INPUT_SEGMENTS]
        
        # Formatear para Gemini
        texto_transcripcion = formatear_transcripcion(conversacion)
        
        # Si es muy corta (< 3 segmentos con texto real), saltar
        textos_reales = [s for s in conversacion if len(s.get('texto', '').strip()) > 3]
        if len(textos_reales) < 3:
            return {"status": "skip", "archivo": json_path.name, "msg": "Conversación muy corta"}
        
        # Enviar a Gemini
        resultado_gemini = procesar_con_gemini(model, texto_transcripcion)
        
        if not resultado_gemini:
            return {"status": "error", "archivo": json_path.name, "msg": "Sin respuesta de Gemini"}
        
        # Construir archivo mejorado
        data_mejorada = data.copy()
        
        # Agregar análisis de Gemini
        analisis = resultado_gemini.get('analisis', {})
        data_mejorada['mejora_gemini'] = {
            'analisis': analisis,
            'fecha_mejora': datetime.now().isoformat(),
            'modelo': MODEL_NAME
        }
        
        # Si Gemini devolvió conversación mejorada, reemplazar
        conv_mejorada = resultado_gemini.get('conversacion_mejorada', [])
        if conv_mejorada and len(conv_mejorada) > 0:
            data_mejorada['conversacion_original'] = data.get('conversacion', [])
            data_mejorada['conversacion'] = conv_mejorada
            
            # Reconstruir transcripción completa
            data_mejorada['transcripcion_completa'] = ' '.join(
                seg.get('texto', '') for seg in conv_mejorada
            )
        
        # Guardar
        output_name = json_path.name.replace('_transcripcion.json', '_mejorado.json')
        output_path = OUTPUT_DIR / output_name
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data_mejorada, f, ensure_ascii=False, indent=2)
        
        return {
            "status": "ok",
            "archivo": json_path.name,
            "calidad": analisis.get('calidad_transcripcion_original', '?'),
            "tipo": analisis.get('tipo_llamada', '?'),
            "resultado": analisis.get('resultado', '?'),
            "correcciones": analisis.get('correcciones_realizadas', '')
        }
        
    except Exception as e:
        return {"status": "error", "archivo": json_path.name, "msg": str(e)}


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 70)
    print("  🤖 MEJORA DE TRANSCRIPCIONES CON GEMINI")
    print("=" * 70)
    print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  📂 Input:  {INPUT_DIR}")
    print(f"  📂 Output: {OUTPUT_DIR}")
    print(f"  🧠 Modelo: {MODEL_NAME}")
    print("=" * 70)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORTE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Listar transcripciones disponibles
    todos = sorted(INPUT_DIR.glob("*_transcripcion.json"))
    print(f"\n  📊 Transcripciones disponibles: {len(todos)}")
    
    # Ver cuáles ya están mejoradas
    ya_mejorados = set()
    if OUTPUT_DIR.exists():
        for f in OUTPUT_DIR.iterdir():
            if f.name.endswith('_mejorado.json'):
                nombre_orig = f.name.replace('_mejorado.json', '_transcripcion.json')
                ya_mejorados.add(nombre_orig)
    
    pendientes = [f for f in todos if f.name not in ya_mejorados]
    print(f"  ✅ Ya mejoradas: {len(ya_mejorados)}")
    print(f"  ⏳ Pendientes: {len(pendientes)}")
    
    if not pendientes:
        print("\n  ✅ ¡Todas las transcripciones ya están mejoradas!")
        return
    
    print(f"\n  🚀 Iniciando mejora de {len(pendientes)} transcripciones con {NUM_WORKERS} workers...\n")
    
    # Configurar Gemini - un modelo por worker
    models = [configurar_gemini() for _ in range(NUM_WORKERS)]
    
    # Procesar en paralelo
    stats = defaultdict(int)
    stats_lock = threading.Lock()
    print_lock = threading.Lock()
    counter = [0]  # mutable para compartir entre threads
    inicio = datetime.now()
    total = len(pendientes)
    
    def worker(args):
        idx, json_path = args
        model = models[idx % NUM_WORKERS]
        resultado = procesar_archivo(model, json_path)
        
        with stats_lock:
            stats[resultado['status']] += 1
            counter[0] += 1
            i = counter[0]
        
        nombre_corto = json_path.stem[:50]
        with print_lock:
            if resultado['status'] == 'ok':
                print(f"  [{i}/{total}] {nombre_corto}... ✅ {resultado.get('tipo','?')} | {resultado.get('resultado','?')} | Calidad: {resultado.get('calidad','?')}")
            elif resultado['status'] == 'skip':
                print(f"  [{i}/{total}] {nombre_corto}... ⏭️ {resultado.get('msg', '')}")
            else:
                print(f"  [{i}/{total}] {nombre_corto}... ❌ {resultado.get('msg', '')[:50]}")
            
            if i % 50 == 0:
                elapsed = (datetime.now() - inicio).total_seconds()
                vel = stats['ok'] / (elapsed / 3600) if elapsed > 0 else 0
                print(f"\n  📊 Progreso: {i}/{total} | ✅{stats['ok']} ❌{stats['error']} ⏭️{stats['skip']} | {vel:.0f}/hora\n")
        
        time.sleep(DELAY_BETWEEN_CALLS)
        return resultado
    
    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        futures = {executor.submit(worker, (i, path)): path for i, path in enumerate(pendientes)}
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"  ❌ Error inesperado: {str(e)[:60]}")
    
    # Resumen
    elapsed = (datetime.now() - inicio).total_seconds()
    
    print(f"\n{'='*70}")
    print(f"  🎉 PROCESO COMPLETADO")
    print(f"{'='*70}")
    print(f"  ✅ Mejoradas: {stats['ok']}")
    print(f"  ⏭️ Saltadas:  {stats['skip']}")
    print(f"  ❌ Errores:   {stats['error']}")
    print(f"  ⏱️ Tiempo:    {elapsed/60:.1f} minutos")
    print(f"  📂 Salida:    {OUTPUT_DIR}")
    print(f"{'='*70}")
    
    # Guardar reporte
    reporte = {
        "fecha": datetime.now().isoformat(),
        "modelo": MODEL_NAME,
        "total_procesados": sum(stats.values()),
        "estadisticas": dict(stats),
        "tiempo_minutos": round(elapsed / 60, 1)
    }
    reporte_path = REPORTE_DIR / f"reporte_mejora_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(reporte_path, 'w', encoding='utf-8') as f:
        json.dump(reporte, f, ensure_ascii=False, indent=2)
    print(f"  📄 Reporte: {reporte_path}")


if __name__ == "__main__":
    main()

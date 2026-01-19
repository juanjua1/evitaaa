"""
Corrector de Diarización para Transcripciones EVA
=================================================
Este script post-procesa los JSON de transcripciones para:
1. Separar turnos de habla que están mezclados en un mismo segmento
2. Identificar correctamente quién es el AGENTE (vendedor de Movistar)
3. Reasignar los hablantes basándose en patrones de conversación

Autor: Sistema EVA
Versión: 1.0
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from copy import deepcopy

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

# Patrones para identificar al AGENTE (vendedor)
PATRONES_AGENTE = [
    # Presentaciones típicas del agente
    r"mi nombre es \w+",
    r"me llamo \w+",
    r"soy \w+.{0,20}(movistar|asesor|asesora|beneficios)",
    r"te hablo de (movistar|beneficios)",
    r"me comunico (de|desde) (movistar|beneficios)",
    r"te llamo de (movistar|beneficios)",
    r"área de beneficios",
    r"te contacto para brindarte",
    r"tenía un beneficio exclusivo",
    r"campaña de recuperación",
    # Frases típicas de venta
    r"el plan (que|de) \d+ (gigas|gb)",
    r"te queda (a|en) \$?\d+",
    r"precio.{0,20}(promocional|día de hoy)",
    r"whatsapp gratis",
    r"llamadas (libres|ilimitadas|gratis)",
    # Solicitudes de datos (solo el agente pide)
    r"me (podrías|podés|puede) (brindar|confirmar|dar)",
    r"(últimos|tres) (dígitos|números).{0,10}dni",
    r"(confirmas|confirmás) (tu|el|los)",
    r"tu (nombre completo|fecha de nacimiento|correo|mail|email)",
    r"me figura (en el sistema|que)",
    r"voy a verificar",
]

# Patrones para identificar al CLIENTE
PATRONES_CLIENTE = [
    # Respuestas típicas del cliente
    r"^(sí|si|no|ok|bien|dale|claro|ajá|aha)[\.,\?!]?$",
    r"¿quién habla\??",
    r"¿de (qué|que) empresa\??",
    r"¿cuánto (me )?(saldría|sale|cuesta)\??",
    r"el plan me sirve",
    r"no (me )?interesa",
    r"tengo deuda",
    r"la tengo suspendida",
    r"no puedo pagar",
    # El cliente da sus datos (respuestas cortas con números)
    r"^[\d\s,\.]+$",  # Solo números
    r"mi (mail|correo|email) es",
    r"del \d{2}",  # Fechas de nacimiento "del 94"
]

# Patrones de preguntas (generalmente del agente)
PATRONES_PREGUNTA_AGENTE = [
    r"¿hablo con \w+\??",
    r"¿(puede|puede) ser\??",
    r"¿(es|está) correcto\??",
    r"¿(qué|que) te parece\??",
    r"¿(cuánto|cuanto) (estás|estas) (pagando|abonando)\??",
    r"¿(tenés|tienes|tenes) (e-?sim|chip)\??",
    r"¿te (llego|llegó)\??",
]

# Marcadores de cambio de turno dentro de un texto
MARCADORES_CAMBIO_TURNO = [
    # Pregunta seguida de respuesta corta
    (r"\?[\s]*", r"(Sí|Si|No|Claro|Dale|Ok|Bien|Ajá|Perfecto|Exacto)[\.,]?\s"),
    # Respuesta corta seguida de continuación del agente
    (r"(Sí|Si|No|Claro|Dale|Ok|Bien)[\.,]?\s+", r"(Perfecto|Bien|Bueno|Ok|Exacto|Claro)[\.,]?\s"),
]


# =============================================================================
# FUNCIONES DE ANÁLISIS DE TEXTO
# =============================================================================

def normalizar_texto(texto: str) -> str:
    """Normaliza el texto para comparaciones."""
    return texto.lower().strip()


def es_patron_agente(texto: str) -> float:
    """
    Calcula un score de probabilidad de que el texto sea del AGENTE.
    Returns: Score entre 0 y 1
    """
    texto_lower = normalizar_texto(texto)
    matches = 0
    
    for patron in PATRONES_AGENTE:
        if re.search(patron, texto_lower):
            matches += 1
    
    for patron in PATRONES_PREGUNTA_AGENTE:
        if re.search(patron, texto_lower):
            matches += 0.5
    
    # Penalizar si parece cliente
    for patron in PATRONES_CLIENTE:
        if re.search(patron, texto_lower):
            matches -= 0.5
    
    # Normalizar score
    return min(1.0, max(0.0, matches / 3))


def es_patron_cliente(texto: str) -> float:
    """
    Calcula un score de probabilidad de que el texto sea del CLIENTE.
    Returns: Score entre 0 y 1
    """
    texto_lower = normalizar_texto(texto)
    matches = 0
    
    for patron in PATRONES_CLIENTE:
        if re.search(patron, texto_lower):
            matches += 1
    
    # El texto muy corto suele ser del cliente
    if len(texto.split()) <= 5:
        matches += 0.3
    
    # Penalizar si parece agente
    for patron in PATRONES_AGENTE:
        if re.search(patron, texto_lower):
            matches -= 1
    
    return min(1.0, max(0.0, matches / 2))


def detectar_cambios_turno(texto: str) -> List[Tuple[int, str]]:
    """
    Detecta posibles puntos de cambio de turno dentro de un texto.
    
    Returns:
        Lista de tuplas (posición, tipo_cambio)
    """
    cambios = []
    texto_lower = texto.lower()
    
    # PATRÓN 1: Pregunta seguida de respuesta corta del cliente
    # Ej: "¿Puede ser? Sí," -> cambio después de "?"
    patron_pr = r'\?\s*(sí|si|no|claro|dale|ok|bien|ajá|aha|exacto|perfecto|y creo|no sé|el de)'
    for match in re.finditer(patron_pr, texto_lower):
        pos = match.start() + 1  # Después del ?
        cambios.append((pos, "pregunta_respuesta"))
    
    # PATRÓN 2: Respuesta corta seguida de continuación del agente
    # Ej: "Sí. Bien, entonces" o "No. Mirá," -> cambio después del punto
    patron_rc = r'(?:^|[\.\?]\s*)(sí|si|no|claro|dale|ok|bien|ajá|exacto|imagínate|y creo de \d+)[\.,]\s*(bien|bueno|perfecto|ok|claro|entonces|mirá|mira|nosotros|porque|justamente)'
    for match in re.finditer(patron_rc, texto_lower):
        # Buscar el punto o coma después de la respuesta corta
        respuesta = match.group(1)
        pos_respuesta_fin = match.start() + len(respuesta) + 1
        if pos_respuesta_fin < len(texto):
            # Encontrar el final de la respuesta (. o ,)
            for i in range(match.start(), min(match.end(), len(texto))):
                if texto_lower[i] in '.,':
                    cambios.append((i + 1, "respuesta_continuacion"))
                    break
    
    # PATRÓN 3: Datos del cliente intercalados
    # Ej: "¿Cuánto? Algo de 100.000" o "tus últimos 300 del DNI son 38, 31"
    patron_datos = r'(\?)\s*(\d[\d\s,\.]+|algo de \d+|y creo de \d+|del \d{2})'
    for match in re.finditer(patron_datos, texto_lower):
        pos = match.start() + 1
        cambios.append((pos, "cliente_da_datos"))
    
    # PATRÓN 4: "¿quién habla?" es siempre del cliente
    patron_quien = r'\?\s*(¿quién habla|¿de qué empresa|¿cuánto me saldría|¿y cuánto)'
    for match in re.finditer(patron_quien, texto_lower):
        pos = match.start() + 1
        cambios.append((pos, "pregunta_cliente"))
    
    # PATRÓN 5: Frases típicas que indican cambio de hablante
    # El cliente dice algo y el agente responde
    patrones_cambio = [
        r'(la tengo suspendida[^\.]*\.)\s*(imagínate|claro)',
        r'(no lo pude pagar[^\.]*\.)\s*(y la verdad)',
        r'(por lo menos necesito \d+[^\.]*\.)\s*(ajá|bien)',
        r'(el plan me sirve[^\.]*\.)\s*(bien|mirá)',
        r'(no me interesa[^\.]*\.)\s*(ok|entiendo)',
    ]
    for patron in patrones_cambio:
        for match in re.finditer(patron, texto_lower):
            # El cambio está entre el grupo 1 y 2
            pos = match.start() + len(match.group(1))
            cambios.append((pos, "frase_cambio"))
    
    # PATRÓN 6: Cuando el agente confirma datos y el cliente corrige
    # Ej: "Ayelo, ¿es correcto? Ayelo, Ayelo se pronuncie."
    patron_correccion = r'(¿es correcto\?)\s*([a-záéíóú]+,\s*[a-záéíóú]+\s+se\s+pronunc)'
    for match in re.finditer(patron_correccion, texto_lower):
        pos = match.start() + len(match.group(1))
        cambios.append((pos, "cliente_corrige"))
    
    # Eliminar duplicados cercanos (dentro de 5 caracteres)
    cambios_filtrados = []
    cambios_ordenados = sorted(set(cambios), key=lambda x: x[0])
    ultimo_pos = -10
    for pos, tipo in cambios_ordenados:
        if pos > ultimo_pos + 5:
            cambios_filtrados.append((pos, tipo))
            ultimo_pos = pos
    
    return cambios_filtrados


def dividir_segmento_por_turnos(segmento: Dict) -> List[Dict]:
    """
    Intenta dividir un segmento que contiene múltiples turnos de habla.
    
    Args:
        segmento: Diccionario con hablante, texto, inicio, fin, etc.
    
    Returns:
        Lista de segmentos divididos
    """
    texto = segmento.get("texto", "")
    
    if not texto or len(texto) < 15:
        return [segmento]
    
    # Detectar cambios de turno
    cambios = detectar_cambios_turno(texto)
    
    if not cambios:
        return [segmento]
    
    # Dividir el texto en los puntos de cambio
    segmentos_divididos = []
    inicio_texto = 0
    inicio_tiempo = segmento["inicio"]
    duracion_total = segmento["fin"] - segmento["inicio"]
    texto_total_len = len(texto)
    
    # Determinar hablante inicial basado en el contenido
    hablante_actual = segmento.get("hablante", "Hablante B")
    
    for i, (pos, tipo) in enumerate(cambios):
        # Extraer el fragmento de texto
        fragmento = texto[inicio_texto:pos].strip()
        
        if fragmento and len(fragmento) > 2:
            # Estimar tiempos basándose en proporción de texto
            proporcion_inicio = inicio_texto / texto_total_len
            proporcion_fin = pos / texto_total_len
            
            tiempo_inicio = inicio_tiempo + (duracion_total * proporcion_inicio)
            tiempo_fin = inicio_tiempo + (duracion_total * proporcion_fin)
            
            nuevo_seg = {
                "hablante": hablante_actual,
                "inicio": round(tiempo_inicio, 2),
                "fin": round(tiempo_fin, 2),
                "duracion": round(tiempo_fin - tiempo_inicio, 2),
                "texto": fragmento,
                "confianza": segmento.get("confianza"),
                "_dividido": True,
                "_tipo_cambio": tipo
            }
            segmentos_divididos.append(nuevo_seg)
            
            # Alternar hablante para el siguiente segmento
            if hablante_actual == "Hablante A":
                hablante_actual = "Hablante B"
            else:
                hablante_actual = "Hablante A"
        
        inicio_texto = pos
    
    # Agregar el último fragmento
    fragmento_final = texto[inicio_texto:].strip()
    if fragmento_final and len(fragmento_final) > 2:
        proporcion_inicio = inicio_texto / texto_total_len
        tiempo_inicio = inicio_tiempo + (duracion_total * proporcion_inicio)
        
        nuevo_seg = {
            "hablante": hablante_actual,
            "inicio": round(tiempo_inicio, 2),
            "fin": segmento["fin"],
            "duracion": round(segmento["fin"] - tiempo_inicio, 2),
            "texto": fragmento_final,
            "confianza": segmento.get("confianza"),
            "_dividido": True
        }
        segmentos_divididos.append(nuevo_seg)
    
    return segmentos_divididos if segmentos_divididos else [segmento]


# =============================================================================
# IDENTIFICACIÓN DEL AGENTE
# =============================================================================

def analizar_primer_segmento(conversacion: List[Dict]) -> Dict:
    """
    Analiza los primeros segmentos para identificar patrones iniciales.
    
    El agente típicamente:
    - Inicia la llamada con "Hola, ¿hablo con [nombre]?"
    - Se presenta: "Mi nombre es X, de Movistar"
    
    El cliente típicamente:
    - Responde "Sí, ¿quién habla?"
    """
    info = {
        "primer_hablante": None,
        "agente_probable": None,
        "presentacion_detectada": None
    }
    
    for seg in conversacion[:10]:
        texto = seg.get("texto", "").lower()
        hablante = seg.get("hablante", "")
        
        # Detectar saludo inicial del agente
        if re.search(r'hola.*¿hablo con', texto):
            info["agente_probable"] = hablante
            info["presentacion_detectada"] = "saludo_inicial"
            break
        
        # Detectar presentación
        if re.search(r'mi nombre es \w+|soy \w+.*movistar|te hablo de.*movistar', texto):
            info["agente_probable"] = hablante
            info["presentacion_detectada"] = "presentacion"
            break
        
        # Detectar pregunta típica de cliente
        if re.search(r'¿quién habla|¿de qué empresa', texto):
            # Este es el cliente, el otro es el agente
            info["agente_probable"] = "Hablante A" if hablante == "Hablante B" else "Hablante B"
            info["presentacion_detectada"] = "pregunta_cliente"
            break
    
    return info


def identificar_agente(conversacion: List[Dict]) -> str:
    """
    Identifica cuál hablante es el AGENTE basándose en patrones.
    
    Returns:
        Nombre del hablante que es el agente ("Hablante A" o "Hablante B")
    """
    # Primero intentar con análisis del inicio
    info_inicio = analizar_primer_segmento(conversacion)
    if info_inicio.get("agente_probable"):
        return info_inicio["agente_probable"]
    
    # Si no se detectó, usar scoring
    scores = {"Hablante A": 0, "Hablante B": 0}
    tiempo_total = {"Hablante A": 0, "Hablante B": 0}
    
    for seg in conversacion:
        hablante = seg.get("hablante", "Hablante A")
        texto = seg.get("texto", "")
        duracion = seg.get("duracion", 0)
        
        if hablante not in scores:
            continue
        
        tiempo_total[hablante] += duracion
        
        # Calcular scores
        score_agente = es_patron_agente(texto)
        score_cliente = es_patron_cliente(texto)
        
        scores[hablante] += (score_agente - score_cliente)
    
    # El agente generalmente habla MUCHO más que el cliente
    for h in tiempo_total:
        if tiempo_total[h] > 100:  # Más de 100 segundos
            scores[h] += 2
    
    # El hablante con mayor score es el agente
    agente = max(scores, key=scores.get)
    
    return agente


def reasignar_hablantes(conversacion: List[Dict], agente_original: str) -> List[Dict]:
    """
    Reasigna los hablantes como "Agente" y "Cliente".
    Además, corrige asignaciones erróneas basándose en el contenido.
    
    Args:
        conversacion: Lista de segmentos
        agente_original: Nombre del hablante identificado como agente
    
    Returns:
        Conversación con hablantes reasignados
    """
    cliente_original = "Hablante B" if agente_original == "Hablante A" else "Hablante A"
    
    nueva_conversacion = []
    
    for i, seg in enumerate(conversacion):
        nuevo_seg = deepcopy(seg)
        hablante_original = seg.get("hablante", "Hablante A")
        texto = seg.get("texto", "").strip()
        texto_lower = texto.lower()
        
        # Determinar el rol basándose en el hablante original
        if hablante_original == agente_original:
            rol_asignado = "Agente"
        else:
            rol_asignado = "Cliente"
        
        # CORRECCIONES basadas en contenido
        
        # Frases que SOLO dice el agente
        frases_solo_agente = [
            r'mi nombre es \w+',
            r'me estoy comunicando',
            r'te comento',
            r'te brindo',
            r'te quiero brindar',
            r'el plan (que|de) \d+ (gigas|gb)',
            r'plan de \d+ gigas de base',
            r'\$[\d\.,]+ pesos al día de hoy',
            r'whatsapp gratis',
            r'llamadas (libres|ilimitadas|gratis)',
            r'¿me (podrías|podés) (brindar|confirmar)',
            r'(últimos|tres) (dígitos|números).{0,10}dni',
            r'me figura (en el sistema|que)',
            r'aguárdame',
            r'dame (un|dos) segunditos',
            r'campaña de recuperación',
            r'volver a la compañía',
            r'te paso a comentar',
            r'voy a verificar',
            r'¿vos (recordarás|has hecho|tenés)',
            r'justamente.{0,10}(te|yo|nosotros)',
            r'te voy a (generar|enviar|mandar)',
            r'quédate (tranquilo|en línea)',
        ]
        
        # Frases que SOLO dice el cliente (respuestas a preguntas del agente)
        frases_solo_cliente = [
            r'^sí[\.,]?$',
            r'^no[\.,]?$',
            r'^bien[\.,]?$',
            r'^dale[\.,]?$',
            r'^ok[\.,]?$',
            r'^ajá[\.,]?$',
            r'^claro[\.,]?$',
            r'^exacto[\.,]?$',
            r'¿quién habla',
            r'¿de qué empresa',
            r'¿cuánto me (saldría|sale)',
            r'no me interesa',
            r'no puedo pagar',
            r'tengo deuda',
            r'la tengo suspendida',
            r'el plan me sirve',
            r'imagínate',
            r'y creo de \d+',
            r'^del \d{2}\.?$',  # Respuesta de fecha "del 94"
            # Respuestas de uso personal
            r'(uso|necesito|tengo).{0,20}(gigas|gb)',
            r'no uso más de',
            r'por lo menos necesito',
            r'no,?\s*no,?\s*\d+ no',  # "No, no, 16 no"
            r'sí,?\s*(pero|solo|sí)',
            r'es más,?\s*yo',
            # Datos personales que da el cliente
            r'mi (mail|correo|email) es',
            r'mi apellido',
            r'se pronuncia',
            r'doble [a-z]',
            r'yo (estuve|tengo|tuve)',
        ]
        
        # Verificar si debemos corregir
        es_frase_agente = any(re.search(p, texto_lower) for p in frases_solo_agente)
        es_frase_cliente = any(re.search(p, texto_lower) for p in frases_solo_cliente)
        
        # Lógica de corrección
        if es_frase_agente and not es_frase_cliente:
            if rol_asignado == "Cliente":
                rol_asignado = "Agente"
                nuevo_seg["_corregido"] = "era_cliente_ahora_agente"
        
        if es_frase_cliente and not es_frase_agente:
            if rol_asignado == "Agente":
                rol_asignado = "Cliente"
                nuevo_seg["_corregido"] = "era_agente_ahora_cliente"
        
        # Caso especial: respuestas muy cortas (< 5 palabras) después de una pregunta son del cliente
        if len(texto.split()) <= 4 and texto_lower.strip('.,!?') in ['sí', 'no', 'bien', 'dale', 'ok', 'ajá', 'claro', 'exacto', 'perfecto']:
            if rol_asignado == "Agente":
                rol_asignado = "Cliente"
                nuevo_seg["_corregido"] = "respuesta_corta_cliente"
        
        nuevo_seg["hablante"] = rol_asignado
        nuevo_seg["_hablante_original"] = hablante_original
        
        nueva_conversacion.append(nuevo_seg)
    
    return nueva_conversacion


# =============================================================================
# CORRECCIÓN DE TURNOS ALTERNADOS
# =============================================================================

def corregir_turnos_por_contexto(conversacion: List[Dict]) -> List[Dict]:
    """
    Corrige la asignación de hablantes basándose en el contexto conversacional.
    
    Reglas:
    1. Las preguntas seguidas de respuestas cortas sugieren cambio de turno
    2. El agente hace las preguntas de verificación de datos
    3. El cliente da respuestas cortas y datos personales
    """
    conversacion_corregida = []
    
    for i, seg in enumerate(conversacion):
        nuevo_seg = deepcopy(seg)
        texto = seg.get("texto", "").strip()
        texto_lower = texto.lower()
        
        # Verificar si el segmento actual debería cambiar de hablante
        hablante_actual = seg.get("hablante", "Agente")
        
        # Analizar el contenido
        score_agente = es_patron_agente(texto)
        score_cliente = es_patron_cliente(texto)
        
        # Si hay una diferencia significativa, considerar reasignar
        if score_agente > 0.5 and hablante_actual == "Cliente":
            # Podría ser error, el cliente no dice frases de agente
            nuevo_seg["_posible_error"] = "texto_parece_agente"
        
        if score_cliente > 0.5 and hablante_actual == "Agente":
            # Podría ser error, el agente no da respuestas de cliente
            nuevo_seg["_posible_error"] = "texto_parece_cliente"
        
        conversacion_corregida.append(nuevo_seg)
    
    return conversacion_corregida


# =============================================================================
# PROCESAMIENTO PRINCIPAL
# =============================================================================

def procesar_transcripcion(data: Dict) -> Dict:
    """
    Procesa una transcripción completa para corregir la diarización.
    
    Args:
        data: Diccionario con la transcripción original
    
    Returns:
        Diccionario con la transcripción corregida
    """
    resultado = deepcopy(data)
    conversacion_original = data.get("conversacion", [])
    
    if not conversacion_original:
        return resultado
    
    # Paso 1: Dividir segmentos que tienen múltiples turnos
    conversacion_dividida = []
    segmentos_divididos = 0
    
    for seg in conversacion_original:
        segmentos_nuevos = dividir_segmento_por_turnos(seg)
        conversacion_dividida.extend(segmentos_nuevos)
        if len(segmentos_nuevos) > 1:
            segmentos_divididos += 1
    
    # Paso 2: Identificar quién es el agente
    agente_detectado = identificar_agente(conversacion_dividida)
    
    # Paso 3: Reasignar hablantes como Agente/Cliente
    conversacion_reasignada = reasignar_hablantes(conversacion_dividida, agente_detectado)
    
    # Paso 4: Corregir por contexto
    conversacion_final = corregir_turnos_por_contexto(conversacion_reasignada)
    
    # Paso 5: Fusionar segmentos consecutivos del mismo hablante si son muy cortos
    conversacion_fusionada = fusionar_segmentos_consecutivos(conversacion_final)
    
    # Actualizar resultado
    resultado["conversacion"] = conversacion_fusionada
    resultado["hablantes"] = ["Agente", "Cliente"]
    
    # Recalcular tiempo por hablante
    tiempo_por_hablante = {"Agente": 0, "Cliente": 0}
    for seg in conversacion_fusionada:
        h = seg.get("hablante", "Agente")
        if h in tiempo_por_hablante:
            tiempo_por_hablante[h] += seg.get("duracion", 0)
    
    resultado["tiempo_por_hablante"] = {k: round(v, 2) for k, v in tiempo_por_hablante.items()}
    
    # Regenerar transcripción completa
    resultado["transcripcion_completa"] = " ".join([
        seg.get("texto", "") for seg in conversacion_fusionada
    ])
    
    # Metadata de corrección
    resultado["correccion_diarizacion"] = {
        "agente_detectado_original": agente_detectado,
        "segmentos_divididos": segmentos_divididos,
        "total_segmentos_original": len(conversacion_original),
        "total_segmentos_corregido": len(conversacion_fusionada),
        "fecha_correccion": datetime.now().isoformat(),
        "version": "1.0"
    }
    
    return resultado


def fusionar_segmentos_consecutivos(conversacion: List[Dict], umbral_tiempo: float = 0.5) -> List[Dict]:
    """
    Fusiona segmentos consecutivos del mismo hablante si están muy cerca.
    """
    if not conversacion:
        return conversacion
    
    fusionada = []
    
    for seg in conversacion:
        if not fusionada:
            fusionada.append(deepcopy(seg))
            continue
        
        ultimo = fusionada[-1]
        
        # Mismo hablante y están cerca en tiempo
        gap = seg.get("inicio", 0) - ultimo.get("fin", 0)
        
        if seg.get("hablante") == ultimo.get("hablante") and gap < umbral_tiempo:
            # Fusionar
            ultimo["fin"] = seg.get("fin", ultimo["fin"])
            ultimo["duracion"] = round(ultimo["fin"] - ultimo["inicio"], 2)
            ultimo["texto"] = (ultimo.get("texto", "") + " " + seg.get("texto", "")).strip()
            if "_dividido" in seg:
                ultimo["_fusionado"] = True
        else:
            fusionada.append(deepcopy(seg))
    
    return fusionada


def procesar_archivo(ruta_entrada: str, ruta_salida: str = None) -> Dict:
    """
    Procesa un archivo JSON de transcripción.
    
    Args:
        ruta_entrada: Ruta al archivo JSON original
        ruta_salida: Ruta para guardar el resultado (opcional)
    
    Returns:
        Diccionario con la transcripción corregida
    """
    with open(ruta_entrada, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    resultado = procesar_transcripcion(data)
    
    if ruta_salida:
        with open(ruta_salida, "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        print(f"✅ Guardado: {ruta_salida}")
    
    return resultado


def procesar_carpeta(carpeta_entrada: str, carpeta_salida: str = None):
    """
    Procesa todos los archivos JSON en una carpeta.
    
    Args:
        carpeta_entrada: Carpeta con transcripciones originales
        carpeta_salida: Carpeta para guardar resultados (opcional, si no se especifica sobrescribe)
    """
    if carpeta_salida:
        os.makedirs(carpeta_salida, exist_ok=True)
    
    archivos = list(Path(carpeta_entrada).glob("*.json"))
    total = len(archivos)
    
    print(f"\n{'='*60}")
    print(f"  CORRECTOR DE DIARIZACIÓN EVA v1.0")
    print(f"{'='*60}")
    print(f"  📁 Entrada: {carpeta_entrada}")
    print(f"  📁 Salida: {carpeta_salida or 'Sobrescribir originales'}")
    print(f"  📊 Archivos: {total}")
    print(f"{'='*60}\n")
    
    procesados = 0
    errores = 0
    
    for i, archivo in enumerate(archivos, 1):
        try:
            nombre = archivo.name
            print(f"[{i}/{total}] {nombre[:50]}...", end=" ")
            
            if carpeta_salida:
                ruta_salida = Path(carpeta_salida) / nombre
            else:
                ruta_salida = archivo
            
            resultado = procesar_archivo(str(archivo), str(ruta_salida))
            
            info = resultado.get("correccion_diarizacion", {})
            divididos = info.get("segmentos_divididos", 0)
            
            print(f"✅ ({divididos} segmentos divididos)")
            procesados += 1
            
        except Exception as e:
            print(f"❌ Error: {str(e)[:50]}")
            errores += 1
    
    print(f"\n{'='*60}")
    print(f"  RESUMEN")
    print(f"{'='*60}")
    print(f"  ✅ Procesados: {procesados}")
    print(f"  ❌ Errores: {errores}")
    print(f"{'='*60}\n")


# =============================================================================
# FUNCIÓN DE VISUALIZACIÓN
# =============================================================================

def mostrar_conversacion(data: Dict, max_segmentos: int = 30):
    """
    Muestra la conversación de forma legible.
    """
    print(f"\n{'='*60}")
    print(f"  CONVERSACIÓN: {data.get('archivo', 'N/A')}")
    print(f"{'='*60}")
    
    conversacion = data.get("conversacion", [])[:max_segmentos]
    
    for seg in conversacion:
        hablante = seg.get("hablante", "?")
        texto = seg.get("texto", "")
        inicio = seg.get("inicio", 0)
        
        # Formatear
        emoji = "🧑‍💼" if hablante == "Agente" else "👤"
        
        # Truncar texto largo
        if len(texto) > 80:
            texto = texto[:77] + "..."
        
        print(f"\n{emoji} [{inicio:>6.1f}s] {hablante}:")
        print(f"   {texto}")
    
    if len(data.get("conversacion", [])) > max_segmentos:
        print(f"\n   ... ({len(data['conversacion']) - max_segmentos} segmentos más)")
    
    print(f"\n{'='*60}\n")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import sys
    
    # Ejemplo de uso
    if len(sys.argv) > 1:
        ruta = sys.argv[1]
        
        if os.path.isfile(ruta):
            resultado = procesar_archivo(ruta)
            mostrar_conversacion(resultado)
        elif os.path.isdir(ruta):
            carpeta_salida = sys.argv[2] if len(sys.argv) > 2 else None
            procesar_carpeta(ruta, carpeta_salida)
    else:
        # Demo con el archivo de muestra
        print("\n" + "="*60)
        print("  USO:")
        print("  python 7_corregir_diarizacion.py <archivo.json>")
        print("  python 7_corregir_diarizacion.py <carpeta_entrada> [carpeta_salida]")
        print("="*60 + "\n")
        
        # Procesar ejemplo
        muestra = r"muestra eva\muestra eva"
        if os.path.exists(muestra):
            archivos = list(Path(muestra).glob("*.json"))[:1]
            if archivos:
                print("Demo con primer archivo de muestra:\n")
                resultado = procesar_archivo(str(archivos[0]))
                mostrar_conversacion(resultado, max_segmentos=15)

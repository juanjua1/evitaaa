"""
Script para procesar y enriquecer transcripciones del 19-24 de enero
ANTES de pasarlas por la clasificación de IA.

Pasos:
1. Corregir diarización (identificar AGENTE vs CLIENTE)
2. Cruzar con reporte de interacciones (agregar metadatos)
3. Aplicar correcciones de errores de Whisper

Autor: EVA System
Fecha: 26/01/2026
"""

import os
import json
import re
import csv
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from copy import deepcopy

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

CARPETA_TRANSCRIPCIONES = r"C:\Users\rodri\Documents\codigo-WC\eva\transcripciones_19-24_enero"
CSV_REPORTE = r"C:\Users\rodri\Documents\codigo-WC\eva\Detalle Interacciones (Campaña - Lote).csv"
CARPETA_SALIDA = r"C:\Users\rodri\Documents\codigo-WC\eva\transcripciones_procesadas"

# =============================================================================
# PATRONES PARA IDENTIFICAR AGENTE
# =============================================================================

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
    # Solicitudes de datos
    r"me (podrías|podés|puede) (brindar|confirmar|dar)",
    r"(últimos|tres) (dígitos|números).{0,10}dni",
    r"(confirmas|confirmás) (tu|el|los)",
    r"tu (nombre completo|fecha de nacimiento|correo|mail|email)",
    r"me figura (en el sistema|que)",
    r"voy a verificar",
]

PATRONES_CLIENTE = [
    r"^(sí|si|no|ok|bien|dale|claro|ajá|aha)[\.,\?!]?$",
    r"¿quién habla\??",
    r"¿de (qué|que) empresa\??",
    r"¿cuánto (me )?(saldría|sale|cuesta)\??",
    r"el plan me sirve",
    r"no (me )?interesa",
    r"tengo deuda",
    r"la tengo suspendida",
    r"no puedo pagar",
]

# Errores comunes de Whisper para "gigas"
ERRORES_GIGAS = [
    'llenas', 'llegas', 'libras', 'digas', 'dinas', 'sigas', 
    'siglas', 'sidas', 'chicas', 'rigas', 'yidas', 'gigas', 
    'giga', 'gb', 'higas', 'ligas'
]

# =============================================================================
# FUNCIONES DE ANÁLISIS
# =============================================================================

def normalizar_texto(texto: str) -> str:
    """Normaliza el texto para comparaciones."""
    return texto.lower().strip()

def es_patron_agente(texto: str) -> float:
    """Retorna un score de probabilidad de que el texto sea del agente."""
    texto_norm = normalizar_texto(texto)
    score = 0.0
    
    for patron in PATRONES_AGENTE:
        if re.search(patron, texto_norm, re.IGNORECASE):
            score += 1.0
    
    # Penalizar si parece cliente
    for patron in PATRONES_CLIENTE:
        if re.search(patron, texto_norm, re.IGNORECASE):
            score -= 0.5
    
    return score

def extraer_id_interaccion(nombre_archivo: str) -> Optional[str]:
    """
    Extrae el ID de interacción del nombre del archivo.
    Ejemplo: amza10_1_260112104540969_ACD_72207_transcripcion.json -> 260112104540969_ACD_72207
    """
    match = re.search(r'(\d{15}_(?:ACD|MIT)_\d{5})', nombre_archivo)
    if match:
        return match.group(1)
    return None

def corregir_errores_whisper(texto: str) -> str:
    """Corrige errores comunes de Whisper en la transcripción."""
    texto_corregido = texto
    
    # Patrones de corrección para gigas
    for error in ERRORES_GIGAS:
        if error != 'gigas':
            # Buscar patrones como "30 llenas", "20 digas", etc.
            patron = rf'(\d+)\s*{error}'
            texto_corregido = re.sub(patron, r'\1 gigas', texto_corregido, flags=re.IGNORECASE)
    
    return texto_corregido

def identificar_hablante_principal(conversacion: list) -> dict:
    """
    Analiza la conversación para identificar quién es el AGENTE.
    Retorna un diccionario con la asignación de hablantes.
    """
    scores = {}
    
    for turno in conversacion:
        hablante = turno.get('speaker', turno.get('hablante', 'UNKNOWN'))
        texto = turno.get('text', turno.get('texto', ''))
        
        if hablante not in scores:
            scores[hablante] = 0.0
        
        scores[hablante] += es_patron_agente(texto)
    
    # El hablante con mayor score es el AGENTE
    if scores:
        agente_probable = max(scores.keys(), key=lambda k: scores[k])
        return {
            'agente_id': agente_probable,
            'scores': scores
        }
    
    return {'agente_id': None, 'scores': {}}

def corregir_diarizacion(data: dict) -> dict:
    """Corrige la diarización identificando correctamente AGENTE y CLIENTE."""
    data_corregida = deepcopy(data)
    
    # Obtener conversación
    conversacion = data_corregida.get('conversacion', data_corregida.get('transcripcion', []))
    
    if not isinstance(conversacion, list):
        return data_corregida
    
    # Identificar quién es el agente
    resultado = identificar_hablante_principal(conversacion)
    agente_id = resultado['agente_id']
    
    if not agente_id:
        return data_corregida
    
    # Renombrar hablantes
    for turno in conversacion:
        hablante_actual = turno.get('speaker', turno.get('hablante', ''))
        texto = turno.get('text', turno.get('texto', ''))
        
        # Corregir errores de Whisper en el texto
        texto_corregido = corregir_errores_whisper(texto)
        
        if 'text' in turno:
            turno['text'] = texto_corregido
            turno['text_original'] = texto
        elif 'texto' in turno:
            turno['texto'] = texto_corregido
            turno['texto_original'] = texto
        
        # Asignar rol
        if hablante_actual == agente_id:
            turno['rol'] = 'AGENTE'
        else:
            turno['rol'] = 'CLIENTE'
    
    # Actualizar la conversación
    if 'conversacion' in data_corregida:
        data_corregida['conversacion'] = conversacion
    else:
        data_corregida['transcripcion'] = conversacion
    
    # Agregar metadata de corrección
    data_corregida['_correccion_diarizacion'] = {
        'fecha_correccion': datetime.now().isoformat(),
        'agente_identificado': agente_id,
        'scores_hablantes': resultado['scores']
    }
    
    return data_corregida

# =============================================================================
# FUNCIONES DE ENRIQUECIMIENTO
# =============================================================================

def cargar_reporte_interacciones(ruta_csv: str) -> dict:
    """Carga el CSV de interacciones y lo indexa por idInteraccion."""
    print(f"\n📂 Cargando reporte de interacciones: {ruta_csv}")
    
    index = {}
    
    try:
        df = pd.read_csv(ruta_csv, sep=';', encoding='utf-8', low_memory=False)
        print(f"   ✅ {len(df)} registros cargados")
        print(f"   📋 Columnas: {list(df.columns)[:10]}...")
        
        for _, row in df.iterrows():
            id_int = str(row.get('idInteraccion', '')).strip()
            if id_int:
                index[id_int] = row.to_dict()
    except Exception as e:
        print(f"   ❌ Error cargando CSV: {e}")
    
    return index

def enriquecer_con_metadatos(data: dict, metadatos: dict) -> dict:
    """Agrega metadatos del reporte de interacciones al JSON."""
    data_enriquecida = deepcopy(data)
    
    info_llamada = {
        'id_interaccion': metadatos.get('idInteraccion', ''),
        'fecha_inicio': str(metadatos.get('Inicio', '')),
        'agente': {
            'nombre': str(metadatos.get('Nombre Agente', '')),
            'login': str(metadatos.get('LoginId', '')),
            'equipo': str(metadatos.get('Equipo', '')),
        },
        'tiempos': {
            'duracion_total': int(metadatos.get('Duración', 0) or 0),
            'talking_time': int(metadatos.get('TalkingTime', 0) or 0),
            'hold': int(metadatos.get('Hold', 0) or 0),
            'acw': int(metadatos.get('ACW', 0) or 0),
            'en_cola': int(metadatos.get('EnCola', 0) or 0),
        },
        'resultado': {
            'origen_corte': str(metadatos.get('Origen Corte', '')),
            'causa_terminacion': str(metadatos.get('Causa Terminación', '')),
            'tipificacion': str(metadatos.get('Tipificación', '')),
        },
        'campana': {
            'empresa': str(metadatos.get('Empresa', '')),
            'campana': str(metadatos.get('Campaña', '')),
            'lote': str(metadatos.get('Lote', '')),
        },
        'cliente': {
            'telefono': str(metadatos.get('Cliente', '')),
            'nombre': str(metadatos.get('Nombre Cliente', '')),
        },
        'sentido': str(metadatos.get('Sentido', '')),
    }
    
    data_enriquecida['info_llamada'] = info_llamada
    
    return data_enriquecida

# =============================================================================
# PROCESAMIENTO PRINCIPAL
# =============================================================================

def procesar_transcripciones():
    """Procesa todas las transcripciones aplicando los pasos de enriquecimiento."""
    
    print("=" * 70)
    print("🔄 PROCESAMIENTO DE TRANSCRIPCIONES 19-24 ENERO")
    print("=" * 70)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Carpeta origen: {CARPETA_TRANSCRIPCIONES}")
    print(f"📁 Carpeta destino: {CARPETA_SALIDA}")
    
    # Crear carpeta de salida
    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    
    # Paso 1: Cargar reporte de interacciones
    print("\n" + "=" * 70)
    print("PASO 1: Cargar reporte de interacciones")
    print("=" * 70)
    
    reporte_index = cargar_reporte_interacciones(CSV_REPORTE)
    print(f"   📊 {len(reporte_index)} interacciones indexadas")
    
    # Paso 2: Listar archivos JSON
    print("\n" + "=" * 70)
    print("PASO 2: Identificar transcripciones")
    print("=" * 70)
    
    archivos = list(Path(CARPETA_TRANSCRIPCIONES).glob('*.json'))
    print(f"   📁 {len(archivos)} archivos JSON encontrados")
    
    if not archivos:
        print("   ⚠️ No se encontraron archivos JSON")
        return
    
    # Mostrar ejemplo
    print(f"   📋 Ejemplo: {archivos[0].name}")
    
    # Paso 3: Procesar cada archivo
    print("\n" + "=" * 70)
    print("PASO 3: Procesar transcripciones")
    print("=" * 70)
    
    stats = {
        'total': len(archivos),
        'procesados': 0,
        'con_match': 0,
        'sin_match': 0,
        'errores': 0,
        'diarizacion_corregida': 0,
    }
    
    for i, archivo in enumerate(archivos, 1):
        try:
            # Extraer ID de interacción
            id_interaccion = extraer_id_interaccion(archivo.name)
            
            # Cargar JSON
            with open(archivo, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Paso 3a: Corregir diarización y errores de Whisper
            data = corregir_diarizacion(data)
            
            if '_correccion_diarizacion' in data:
                stats['diarizacion_corregida'] += 1
            
            # Paso 3b: Enriquecer con metadatos si hay match
            if id_interaccion and id_interaccion in reporte_index:
                metadatos = reporte_index[id_interaccion]
                data = enriquecer_con_metadatos(data, metadatos)
                stats['con_match'] += 1
            else:
                stats['sin_match'] += 1
            
            # Agregar metadata de procesamiento
            data['_procesamiento'] = {
                'fecha': datetime.now().isoformat(),
                'version': '1.0',
                'archivo_original': archivo.name,
                'id_interaccion': id_interaccion,
                'tiene_metadatos_llamada': id_interaccion in reporte_index if id_interaccion else False
            }
            
            # Guardar archivo procesado
            archivo_salida = Path(CARPETA_SALIDA) / archivo.name.replace('_transcripcion.json', '_procesado.json')
            with open(archivo_salida, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            stats['procesados'] += 1
            
            # Mostrar progreso cada 100 archivos
            if i % 100 == 0 or i == len(archivos):
                print(f"   Procesados: {i}/{len(archivos)} ({i*100//len(archivos)}%)")
                
        except Exception as e:
            print(f"   ❌ Error en {archivo.name}: {e}")
            stats['errores'] += 1
    
    # Resumen final
    print("\n" + "=" * 70)
    print("📊 RESUMEN DEL PROCESAMIENTO")
    print("=" * 70)
    print(f"   Total archivos: {stats['total']}")
    print(f"   ✅ Procesados correctamente: {stats['procesados']}")
    print(f"   📋 Con metadatos de reporte: {stats['con_match']}")
    print(f"   ⚠️  Sin match en reporte: {stats['sin_match']}")
    print(f"   🔧 Diarización corregida: {stats['diarizacion_corregida']}")
    print(f"   ❌ Errores: {stats['errores']}")
    print(f"\n   📁 Archivos guardados en: {CARPETA_SALIDA}")
    
    return stats

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    procesar_transcripciones()

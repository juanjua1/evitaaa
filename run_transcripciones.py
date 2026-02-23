"""
Wrapper para iniciar transcripciones sin confirmación interactiva.
Ejecuta directamente procesar_paralelo() de 3_speech_eva.py
"""
import warnings
warnings.filterwarnings("ignore")

import os
import sys
import json
import time
import traceback
import gc
from pathlib import Path
from datetime import datetime, timedelta

import torch
import whisperx
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity
from concurrent.futures import ProcessPoolExecutor, as_completed

# Importar funciones de 3_speech_eva
sys.path.insert(0, r"C:\Users\rodri\Documents\codigo-WC\eva")
from importlib import util as imp_util
spec = imp_util.spec_from_file_location("speech_eva", r"C:\Users\rodri\Documents\codigo-WC\eva\3_speech_eva.py")
speech_mod = imp_util.module_from_spec(spec)
spec.loader.exec_module(speech_mod)

CARPETA_ENTRADA = r"C:\Users\rodri\Documents\codigo-WC\eva\audios_descargados"
CARPETA_SALIDA = r"C:\Users\rodri\Documents\codigo-WC\eva\transcripciones"
USAR_ECAPA = True
NUM_WORKERS = 1

if __name__ == "__main__":
    total = len(list(Path(CARPETA_ENTRADA).glob("*.wav")))
    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    procesados = len(list(Path(CARPETA_SALIDA).glob("*_transcripcion.json")))
    pendientes = total - procesados

    print(f"\n🔊 Total WAV: {total}", flush=True)
    print(f"✓ Ya procesados: {procesados}", flush=True)
    print(f"⏳ Pendientes: {pendientes}", flush=True)
    print(f"💻 GPU: {'Sí' if torch.cuda.is_available() else 'No'}", flush=True)

    if pendientes == 0:
        print("\n✅ ¡Todo ya procesado!", flush=True)
        sys.exit(0)

    print(f"\n🚀 Iniciando transcripciones...\n", flush=True)

    try:
        speech_mod.procesar_paralelo(
            CARPETA_ENTRADA,
            CARPETA_SALIDA,
            NUM_WORKERS,
            USAR_ECAPA
        )
    except KeyboardInterrupt:
        print("\n⚠️ Interrumpido. Archivos procesados quedaron guardados.", flush=True)
    except Exception as e:
        print(f"\n❌ Error: {e}", flush=True)
        traceback.print_exc()

    print("\n✅ Finalizado", flush=True)

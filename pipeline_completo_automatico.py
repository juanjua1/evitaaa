"""
Pipeline Completo Automático - Mejora + Evaluación
==================================================
Este script ejecuta automáticamente:
1. Pipeline de mejora (identificar roles agente/cliente)
2. Pipeline de evaluación (calificar vendedores)

Déjalo corriendo de noche y al otro día tendrás todo listo.
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
import time

def log(mensaje: str, tipo: str = "INFO"):
    """Imprime mensaje con timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    simbolos = {"INFO": "ℹ️", "OK": "✅", "ERROR": "❌", "WORKING": "⚙️"}
    print(f"{simbolos.get(tipo, 'ℹ️')} [{timestamp}] {mensaje}")

def ejecutar_script(script_path: Path, nombre: str):
    """Ejecuta un script Python y espera a que termine."""
    log(f"Iniciando: {nombre}", "WORKING")
    log(f"Script: {script_path}")
    
    inicio = time.time()
    
    try:
        # Ejecutar script y esperar a que termine
        resultado = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=False,  # Mostrar output en tiempo real
            text=True,
            cwd=script_path.parent
        )
        
        duracion = (time.time() - inicio) / 60  # minutos
        
        if resultado.returncode == 0:
            log(f"{nombre} completado exitosamente en {duracion:.1f} minutos", "OK")
            return True
        else:
            log(f"{nombre} falló con código {resultado.returncode}", "ERROR")
            return False
            
    except Exception as e:
        log(f"Error ejecutando {nombre}: {str(e)}", "ERROR")
        return False

def main():
    """Ejecuta el pipeline completo."""
    print("=" * 80)
    print("🚀 PIPELINE COMPLETO AUTOMÁTICO - EVA")
    print("=" * 80)
    log("Inicio del pipeline completo")
    
    base_dir = Path(__file__).parent
    
    # PASO 1: Mejora de transcripciones (identificar roles)
    print("\n" + "=" * 80)
    print("PASO 1: MEJORA DE TRANSCRIPCIONES")
    print("=" * 80)
    script_mejora = base_dir / "pipeline_mejora_gemini.py"
    
    if not script_mejora.exists():
        log(f"No se encuentra {script_mejora}", "ERROR")
        return
    
    if not ejecutar_script(script_mejora, "Pipeline de Mejora"):
        log("Pipeline de mejora falló. Abortando.", "ERROR")
        return
    
    # PASO 2: Evaluación de transcripciones (calificar vendedores)
    print("\n" + "=" * 80)
    print("PASO 2: EVALUACIÓN DE TRANSCRIPCIONES")
    print("=" * 80)
    script_evaluacion = base_dir / "4_evaluacion_gemini.py"
    
    if not script_evaluacion.exists():
        log(f"No se encuentra {script_evaluacion}", "ERROR")
        return
    
    if not ejecutar_script(script_evaluacion, "Pipeline de Evaluación"):
        log("Pipeline de evaluación falló.", "ERROR")
        return
    
    # COMPLETADO
    print("\n" + "=" * 80)
    print("🎉 PIPELINE COMPLETO FINALIZADO")
    print("=" * 80)
    log("Todos los pasos completados exitosamente", "OK")
    log("Resultados disponibles en: reportes/evaluaciones_gemini.csv", "OK")

if __name__ == "__main__":
    inicio_total = time.time()
    main()
    duracion_total = (time.time() - inicio_total) / 3600  # horas
    print(f"\n⏱️ Tiempo total: {duracion_total:.2f} horas")

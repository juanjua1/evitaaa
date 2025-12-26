import os
import numpy as np
import librosa
import soundfile as sf
import noisereduce as nr
from pathlib import Path
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
import time
import csv
from datetime import datetime

class AudioPreprocessor:
    def __init__(self, input_dir, output_dir, n_processes=None):
        """
        Preprocesador de audio para mejorar transcripciones con multiprocesamiento
        
        Args:
            input_dir: Carpeta con archivos .wav originales
            output_dir: Carpeta donde se guardarán audios procesados
            n_processes: Número de procesos paralelos (None = usar todos los CPUs disponibles)
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar número de procesos
        if n_processes is None:
            self.n_processes = cpu_count()
        else:
            self.n_processes = min(n_processes, cpu_count())
        
        print(f"Usando {self.n_processes} procesos paralelos")
        
    @staticmethod
    def reduce_noise(audio, sr):
        """Reduce ruido del audio usando spectral gating"""
        noise_sample = audio[:int(sr * 0.5)]
        reduced_noise = nr.reduce_noise(
            y=audio,
            sr=sr,
            stationary=True,
            prop_decrease=0.8
        )
        return reduced_noise
    
    @staticmethod
    def normalize_audio(audio):
        """Normaliza el volumen del audio"""
        target_dB = -3.0
        max_amplitude = np.max(np.abs(audio))
        
        if max_amplitude > 0:
            target_amplitude = 10 ** (target_dB / 20)
            audio = audio * (target_amplitude / max_amplitude)
        
        return audio
    
    @staticmethod
    def apply_highpass_filter(audio, sr, cutoff=80):
        """Filtro pasa-altos para eliminar ruido de baja frecuencia"""
        from scipy.signal import butter, sosfilt
        
        sos = butter(5, cutoff, btype='highpass', fs=sr, output='sos')
        filtered = sosfilt(sos, audio)
        return filtered
    
    @staticmethod
    def enhance_speech(audio, sr):
        """Mejora la claridad del habla"""
        threshold = 0.3
        ratio = 3.0
        
        compressed = np.copy(audio)
        mask = np.abs(compressed) > threshold
        compressed[mask] = np.sign(compressed[mask]) * (
            threshold + (np.abs(compressed[mask]) - threshold) / ratio
        )
        
        return compressed
    
    @staticmethod
    def process_single_audio(args):
        """Procesa un archivo de audio (función estática para multiprocesamiento)"""
        input_path, output_path = args
        
        try:
            # Cargar audio
            audio, sr = librosa.load(input_path, sr=None)
            
            # Aplicar preprocesamiento
            audio = AudioPreprocessor.reduce_noise(audio, sr)
            audio = AudioPreprocessor.apply_highpass_filter(audio, sr)
            audio = AudioPreprocessor.enhance_speech(audio, sr)
            audio = AudioPreprocessor.normalize_audio(audio)
            
            # Guardar audio procesado
            sf.write(output_path, audio, sr)
            
            return (True, input_path.name, None)
            
        except Exception as e:
            return (False, input_path.name, str(e))
    
    def get_pending_files(self):
        """Obtiene lista de archivos que aún no han sido procesados"""
        wav_files = list(self.input_dir.glob("*.wav"))
        
        pending_files = []
        for wav_file in wav_files:
            output_path = self.output_dir / f"clean_{wav_file.name}"
            
            # Solo agregar si NO existe el archivo de salida
            if not output_path.exists():
                pending_files.append((wav_file, output_path))
        
        return pending_files
    
    def process_batch(self):
        """Procesa todos los archivos .wav pendientes usando multiprocesamiento"""
        # Obtener archivos pendientes
        pending_files = self.get_pending_files()
        total_files = len(list(self.input_dir.glob("*.wav")))
        already_processed = total_files - len(pending_files)
        
        print(f"\n{'='*60}")
        print(f"Total de archivos .wav: {total_files}")
        print(f"Ya procesados: {already_processed}")
        print(f"Pendientes por procesar: {len(pending_files)}")
        print(f"{'='*60}\n")
        
        if not pending_files:
            print("✓ Todos los archivos ya han sido procesados")
            return
        
        # Estimar tiempo
        print(f"Iniciando procesamiento paralelo...")
        start_time = time.time()
        
        # Procesar en paralelo con barra de progreso
        successful = 0
        failed = 0
        errors = []
        
        with Pool(processes=self.n_processes) as pool:
            results = list(tqdm(
                pool.imap(AudioPreprocessor.process_single_audio, pending_files),
                total=len(pending_files),
                desc="Procesando audios",
                unit="archivo"
            ))
        
        # Contar resultados
        for success, filename, error in results:
            if success:
                successful += 1
            else:
                failed += 1
                errors.append((filename, error))
        
        # Calcular tiempo transcurrido
        elapsed_time = time.time() - start_time
        avg_time = elapsed_time / len(pending_files) if pending_files else 0
        
        # Resumen
        print(f"\n{'='*60}")
        print(f"RESUMEN DEL PROCESAMIENTO")
        print(f"{'='*60}")
        print(f"  ✓ Exitosos: {successful}")
        print(f"  ✗ Fallidos: {failed}")
        print(f"  ⊘ Ya procesados anteriormente: {already_processed}")
        print(f"\n  Tiempo total: {elapsed_time/60:.1f} minutos")
        print(f"  Tiempo promedio por audio: {avg_time:.1f} segundos")
        
        if errors:
            print(f"\n  Errores encontrados:")
            for filename, error in errors[:5]:  # Mostrar solo primeros 5
                print(f"    • {filename}: {error}")
            if len(errors) > 5:
                print(f"    ... y {len(errors)-5} errores más")
        
        print(f"{'='*60}\n")
        
        # Estimación para archivos restantes si se interrumpió
        if failed > 0:
            print(f"💡 Tip: Podés volver a ejecutar el script para reintentar los archivos fallidos")


# Ejemplo de uso
if __name__ == "__main__":
    # Configurar directorios
    INPUT_DIR = "J:\EVA\data\original" #Cambia esto a tu carpeta 
    OUTPUT_DIR = "J:\EVA\data\prosesado" # Cambia esto a tu carpeta
    
    # Crear preprocesador (usa todos los CPUs disponibles)
    preprocessor = AudioPreprocessor(INPUT_DIR, OUTPUT_DIR)
    
    # Procesar todos los audios pendientes
    # Los archivos ya procesados se omiten automáticamente
    preprocessor.process_batch()
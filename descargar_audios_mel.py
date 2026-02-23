"""
Descarga de audios - Equipo Melanie Carmona
============================================
Período: 09/02/2026 al 13/02/2026
Filtro: Solo llamadas >= 1 minuto
Agentes: MZA 1-10, MZA 12 (equipo Mel)
"""

import subprocess
import sys
import os
import time

# Vendedores del equipo Melanie Carmona
USUARIOS_MEL = [
    "MZA 1", "MZA 2", "MZA 3", "MZA 4", "MZA 5",
    "MZA 6", "MZA 7", "MZA 8", "MZA 9", "MZA 10", "MZA 12"
]

# Fechas del 9 al 13 de febrero
FECHAS = [
    "09/02/2026",
    "10/02/2026",
    "11/02/2026",
    "12/02/2026",
    "13/02/2026",
]

DURACION_MINIMA = "01"  # 1 minuto mínimo


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    scraper_path = os.path.join(base_dir, "1_scraper_eva.py")

    if not os.path.exists(scraper_path):
        print("❌ No se encontró 1_scraper_eva.py")
        return

    # Leer el scraper original
    with open(scraper_path, 'r', encoding='utf-8') as f:
        contenido_original = f.read()

    print("=" * 70)
    print("  📥 DESCARGA AUDIOS - EQUIPO MELANIE CARMONA")
    print("=" * 70)
    print(f"\n📅 Fechas: {FECHAS[0]} al {FECHAS[-1]}")
    print(f"👥 Vendedores: {len(USUARIOS_MEL)} ({', '.join(USUARIOS_MEL)})")
    print(f"⏱️  Duración mínima: {DURACION_MINIMA} minuto(s)")
    print(f"⏰ Horario: 08:00 - 23:00")
    print("=" * 70)

    respuesta = input("\n¿Continuar con la descarga? (si/no): ").strip().lower()
    if respuesta not in ['si', 'sí', 's', 'yes', 'y']:
        print("Operación cancelada.")
        return

    # Backup del scraper
    backup_path = scraper_path + ".bak"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(contenido_original)
    print(f"💾 Backup del scraper guardado en {backup_path}")

    try:
        for i, fecha in enumerate(FECHAS, 1):
            print(f"\n{'='*70}")
            print(f"  📅 FECHA {i}/{len(FECHAS)}: {fecha}")
            print(f"{'='*70}\n")

            # Modificar el scraper temporalmente:
            # 1) USUARIOS_A_SELECCIONAR → solo equipo Mel
            # 2) DURACION_MINIMA → "01" (1 minuto)
            contenido_mod = contenido_original

            # Reemplazar lista de usuarios
            import re
            contenido_mod = re.sub(
                r'USUARIOS_A_SELECCIONAR\s*=\s*\[.*?\]',
                'USUARIOS_A_SELECCIONAR = ' + repr(USUARIOS_MEL),
                contenido_mod,
                flags=re.DOTALL
            )

            # Reemplazar duración mínima
            contenido_mod = re.sub(
                r'DURACION_MINIMA\s*=\s*".*?"',
                f'DURACION_MINIMA = "{DURACION_MINIMA}"',
                contenido_mod
            )

            # Escribir versión modificada
            with open(scraper_path, 'w', encoding='utf-8') as f:
                f.write(contenido_mod)

            # Ejecutar enviando la fecha por stdin
            proceso = subprocess.Popen(
                [sys.executable, scraper_path],
                stdin=subprocess.PIPE,
                text=True,
                cwd=base_dir
            )
            proceso.communicate(input=f"{fecha}\n")

            if proceso.returncode != 0:
                print(f"\n⚠️ Error procesando fecha {fecha} (código: {proceso.returncode})")
                continuar = input("¿Continuar con la siguiente fecha? (si/no): ").strip().lower()
                if continuar not in ['si', 'sí', 's', 'yes', 'y']:
                    break
            else:
                print(f"\n✅ Fecha {fecha} completada")

            # Pausa entre fechas
            if i < len(FECHAS):
                print("⏳ Esperando 5 segundos antes de la siguiente fecha...")
                time.sleep(5)

    finally:
        # Restaurar el scraper original SIEMPRE
        with open(backup_path, 'r', encoding='utf-8') as f:
            original = f.read()
        with open(scraper_path, 'w', encoding='utf-8') as f:
            f.write(original)
        # Limpiar backup
        try:
            os.remove(backup_path)
        except Exception:
            pass
        print("\n✅ Scraper original restaurado")

    print("\n" + "=" * 70)
    print("  ✅ DESCARGA EQUIPO MEL FINALIZADA")
    print("=" * 70)


if __name__ == "__main__":
    main()

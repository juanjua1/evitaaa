"""
Setup de la Base de Datos EVA
==============================
Inicializa la base de datos SQLite y migra los datos existentes desde los
archivos CSV / JSON hacia las tablas relacionales.

Uso:
    python setup_database.py                # crea tablas + migra datos
    python setup_database.py --solo-tablas  # solo crea las tablas (sin migrar)
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd

from database import Agente, Evaluacion, Interaccion, SessionLocal, Transcripcion, init_db

BASE_DIR = Path(__file__).parent


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def _parse_bool(value) -> bool | None:
    if pd.isna(value):
        return None
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("true", "1", "si", "sí", "yes")


def _parse_float(value) -> float | None:
    if pd.isna(value):
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _parse_datetime(value, fmt: str = "%Y-%m-%dT%H:%M:%S") -> datetime | None:
    if pd.isna(value) or not str(value).strip():
        return None
    text = str(value).strip()
    for f in (fmt, "%d/%m/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"):
        try:
            return datetime.strptime(text, f)
        except ValueError:
            continue
    return None


def _parse_int(value) -> int | None:
    if pd.isna(value):
        return None
    try:
        return int(float(str(value)))
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Migración de Agentes
# ---------------------------------------------------------------------------

def migrar_agentes(session) -> int:
    csv_path = BASE_DIR / "LISTADO-DE-VENDEDORES.csv"
    if not csv_path.exists():
        print("⚠️  LISTADO-DE-VENDEDORES.csv no encontrado, se omite migración de agentes.")
        return 0

    df = pd.read_csv(csv_path, dtype=str)
    df.columns = [c.strip().strip('"') for c in df.columns]

    # Normalizar nombres de columnas
    col_map = {}
    for col in df.columns:
        lower = col.lower()
        if "usuario" in lower:
            col_map[col] = "usuario"
        elif "nombre" in lower:
            col_map[col] = "nombre"
        elif "equipo" in lower:
            col_map[col] = "equipo"
    df = df.rename(columns=col_map)

    if "usuario" not in df.columns:
        print("⚠️  Columna 'Usuario' no encontrada en el CSV de vendedores.")
        return 0

    ingresados = 0
    for _, row in df.iterrows():
        usuario = str(row.get("usuario", "")).strip().strip('"')
        if not usuario or usuario.lower() == "nan":
            continue

        existing = session.query(Agente).filter_by(usuario=usuario).first()
        if existing:
            continue

        agente = Agente(
            usuario=usuario,
            nombre=str(row.get("nombre", "")).strip().strip('"') or None,
            equipo=str(row.get("equipo", "")).strip().strip('"') or None,
        )
        session.add(agente)
        ingresados += 1

    session.commit()
    print(f"✅ Agentes migrados: {ingresados}")
    return ingresados


def _to_seconds(val) -> int | None:
    """Convierte un valor HH:MM:SS o entero a segundos."""
    raw = str(val).strip()
    if not raw or raw.lower() == "nan":
        return None
    parts = raw.split(":")
    try:
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        return int(float(raw))
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Migración de Interacciones
# ---------------------------------------------------------------------------

def migrar_interacciones(session) -> int:
    csv_paths = list(BASE_DIR.glob("interacciones*.csv")) + list(BASE_DIR.glob("reportes/*.csv"))

    # Filtrar para incluir solo archivos de interacciones/reportes con la columna idInteraccion
    archivos_validos = []
    for p in csv_paths:
        try:
            sample = pd.read_csv(p, sep=";", nrows=1, dtype=str)
            if "idInteraccion" in sample.columns:
                archivos_validos.append(p)
        except Exception:
            pass

    if not archivos_validos:
        print("⚠️  No se encontraron archivos de interacciones.")
        return 0

    # Pre-cargar IDs ya existentes en BD para evitar duplicados
    ids_existentes = {r[0] for r in session.query(Interaccion.id_interaccion).all()}

    ingresados = 0
    for csv_path in archivos_validos:
        try:
            df = pd.read_csv(csv_path, sep=";", dtype=str, encoding="utf-8-sig")
        except Exception as e:
            print(f"⚠️  Error leyendo {csv_path.name}: {e}")
            continue

        for _, row in df.iterrows():
            id_int = str(row.get("idInteraccion", "")).strip()
            if not id_int or id_int.lower() == "nan":
                continue

            if id_int in ids_existentes:
                continue
            ids_existentes.add(id_int)

            # Parsear fecha
            fecha = _parse_datetime(row.get("Inicio", ""), "%d/%m/%Y %H:%M:%S")

            interaccion = Interaccion(
                id_interaccion=id_int,
                agente_usuario=str(row.get("LoginId", row.get("LoginID Agente Cliente", ""))).strip() or None,
                nombre_agente=str(row.get("Nombre Agente", "")).strip() or None,
                cliente_telefono=str(row.get("Cliente", "")).strip().strip('"') or None,
                fecha_inicio=fecha,
                duracion=_to_seconds(row.get("Duración", row.get("Duracion", ""))),
                talking_time=_to_seconds(row.get("TalkingTime", "")),
                tipificacion=str(row.get("Tipificación", row.get("Tipificacion", ""))).strip() or None,
                causa_terminacion=str(row.get("Causa Terminación", row.get("Causa Terminacion", ""))).strip() or None,
                campana=str(row.get("Campaña", row.get("Campana", ""))).strip() or None,
                lote=str(row.get("Lote", "")).strip() or None,
                sentido=str(row.get("Sentido", "")).strip() or None,
                equipo=str(row.get("Equipo", "")).strip() or None,
                sitio=str(row.get("Sitio", "")).strip() or None,
            )
            session.add(interaccion)
            ingresados += 1

        session.commit()

    print(f"✅ Interacciones migradas: {ingresados}")
    return ingresados


# ---------------------------------------------------------------------------
# Migración de Evaluaciones
# ---------------------------------------------------------------------------

def migrar_evaluaciones(session) -> int:
    csv_path = BASE_DIR / "reportes" / "evaluaciones_gemini.csv"
    if not csv_path.exists():
        print("⚠️  evaluaciones_gemini.csv no encontrado, se omite migración de evaluaciones.")
        return 0

    df = pd.read_csv(csv_path, dtype=str)
    ingresados = 0

    for _, row in df.iterrows():
        archivo = str(row.get("archivo", "")).strip()
        if not archivo or archivo.lower() == "nan":
            continue

        if session.query(Evaluacion).filter_by(archivo=archivo).first():
            continue

        agente_usuario = str(row.get("agente", "")).strip() or None

        # Extraer id_interaccion del nombre del archivo.
        # Formato: <agente>_1_<timestamp>_<tipo>_<num>_mejorado.json
        # El id de interacción en la BD es "<timestamp>_<tipo>_<num>"
        id_interaccion = None
        partes = Path(archivo).stem.split("_")  # quita la extensión .json
        # Buscar el segmento "_1_" que separa el prefijo del agente del id
        try:
            idx = partes.index("1")
            id_parts = partes[idx + 1:]
            # Eliminar sufijo "mejorado" si está presente
            if id_parts and id_parts[-1].lower() == "mejorado":
                id_parts = id_parts[:-1]
            if id_parts:
                id_interaccion = "_".join(id_parts)
        except (ValueError, IndexError):
            pass

        evaluacion = Evaluacion(
            archivo=archivo,
            id_interaccion=id_interaccion,
            agente_usuario=agente_usuario,
            saludo_presentacion=_parse_float(row.get("saludo_presentacion")),
            identificacion_cliente=_parse_float(row.get("identificacion_cliente")),
            deteccion_necesidades=_parse_float(row.get("deteccion_necesidades")),
            oferta_productos=_parse_float(row.get("oferta_productos")),
            manejo_objeciones=_parse_float(row.get("manejo_objeciones")),
            cierre=_parse_float(row.get("cierre")),
            despedida=_parse_float(row.get("despedida")),
            proactividad=_parse_float(row.get("proactividad")),
            empatia=_parse_float(row.get("empatia")),
            resolucion_problemas=_parse_float(row.get("resolucion_problemas")),
            puntaje_total=_parse_float(row.get("puntaje_total")),
            primer_plan_ofrecido=str(row.get("primer_plan_ofrecido", "")).strip() or None,
            se_ofrecio_fibra=_parse_bool(row.get("se_ofrecio_fibra")),
            planes_mencionados=str(row.get("planes_mencionados", "")).strip() or None,
            resumen=str(row.get("resumen", "")).strip() or None,
            areas_mejora=str(row.get("areas_mejora", "")).strip() or None,
            fortalezas=str(row.get("fortalezas", "")).strip() or None,
            fecha_evaluacion=_parse_datetime(str(row.get("fecha_evaluacion", ""))),
        )
        session.add(evaluacion)
        ingresados += 1

    session.commit()
    print(f"✅ Evaluaciones migradas: {ingresados}")
    return ingresados


# ---------------------------------------------------------------------------
# Migración de Transcripciones (index de archivos)
# ---------------------------------------------------------------------------

def migrar_transcripciones(session) -> int:
    carpetas = [
        BASE_DIR / "transcripciones_mejoradas",
        BASE_DIR / "transcripciones_mejoradas2",
        BASE_DIR / "transcripciones",
    ]

    ingresados = 0
    for carpeta in carpetas:
        if not carpeta.exists():
            continue
        tiene_mejora = "mejorada" in carpeta.name

        for json_file in carpeta.glob("*.json"):
            archivo = json_file.name
            if session.query(Transcripcion).filter_by(archivo=archivo).first():
                continue

            # Extraer agente del nombre del archivo (primer segmento antes de "_1_")
            partes = archivo.split("_1_")
            agente_usuario = partes[0] if partes else None

            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    contenido = f.read()
            except Exception:
                contenido = None

            transcripcion = Transcripcion(
                archivo=archivo,
                agente_usuario=agente_usuario,
                contenido_json=contenido,
                tiene_mejora=tiene_mejora,
                fecha_procesado=datetime.fromtimestamp(json_file.stat().st_mtime),
            )
            session.add(transcripcion)
            ingresados += 1

        session.commit()

    print(f"✅ Transcripciones indexadas: {ingresados}")
    return ingresados


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Inicializa y migra datos a la BD EVA")
    parser.add_argument(
        "--solo-tablas",
        action="store_true",
        help="Solo crea las tablas sin migrar datos",
    )
    args = parser.parse_args()

    print("🗄️  Inicializando base de datos EVA...")
    init_db()
    print("✅ Tablas creadas correctamente.")

    if args.solo_tablas:
        print("ℹ️  Modo --solo-tablas: se omite la migración de datos.")
        return

    session = SessionLocal()
    try:
        print("\n📂 Migrando datos desde archivos CSV/JSON...")
        migrar_agentes(session)
        migrar_interacciones(session)
        migrar_evaluaciones(session)
        migrar_transcripciones(session)
        print("\n🎉 Migración completada con éxito.")
    except Exception as e:
        session.rollback()
        print(f"❌ Error durante la migración: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()

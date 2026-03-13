"""
Base de datos EVA - Sistema de Evaluación de Ventas
=====================================================
Define el esquema de la base de datos usando SQLAlchemy.

Tablas:
  - agentes        : Vendedores y sus equipos
  - interacciones  : Llamadas telefónicas registradas
  - transcripciones: JSONs de audio transcripto
  - evaluaciones   : Puntuaciones Gemini por llamada
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker

# ---------------------------------------------------------------------------
# Ruta de la base de datos (SQLite, junto a este archivo)
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
DB_PATH = os.environ.get("EVA_DB_PATH", str(BASE_DIR / "eva.db"))
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


# ---------------------------------------------------------------------------
# Declarative base
# ---------------------------------------------------------------------------
class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Modelos
# ---------------------------------------------------------------------------

class Agente(Base):
    """Vendedor / agente de ventas."""

    __tablename__ = "agentes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario = Column(String(50), unique=True, nullable=False)   # ej. "mza1"
    nombre = Column(String(200), nullable=True)
    equipo = Column(String(100), nullable=True)

    interacciones = relationship("Interaccion", back_populates="agente", lazy="dynamic")
    evaluaciones = relationship("Evaluacion", back_populates="agente", lazy="dynamic")
    transcripciones = relationship("Transcripcion", back_populates="agente", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Agente usuario={self.usuario!r} nombre={self.nombre!r}>"


class Interaccion(Base):
    """Llamada telefónica registrada en el sistema."""

    __tablename__ = "interacciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_interaccion = Column(String(100), unique=True, nullable=False)  # ej. "260126145438490_ACD_57137"
    agente_usuario = Column(String(50), ForeignKey("agentes.usuario"), nullable=True)
    nombre_agente = Column(String(200), nullable=True)
    cliente_telefono = Column(String(50), nullable=True)
    fecha_inicio = Column(DateTime, nullable=True)
    duracion = Column(Integer, nullable=True)        # segundos
    talking_time = Column(Integer, nullable=True)    # segundos
    tipificacion = Column(String(200), nullable=True)
    causa_terminacion = Column(String(200), nullable=True)
    campana = Column(String(200), nullable=True)
    lote = Column(String(200), nullable=True)
    sentido = Column(String(50), nullable=True)      # "Entrante" / "Discador Predictivo"
    equipo = Column(String(100), nullable=True)
    sitio = Column(String(100), nullable=True)

    agente = relationship("Agente", back_populates="interacciones")
    transcripcion = relationship("Transcripcion", back_populates="interaccion", uselist=False)
    evaluacion = relationship("Evaluacion", back_populates="interaccion", uselist=False)

    def __repr__(self) -> str:
        return f"<Interaccion id={self.id_interaccion!r} agente={self.agente_usuario!r}>"


class Transcripcion(Base):
    """Transcripción de audio (cruda o mejorada por Gemini)."""

    __tablename__ = "transcripciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    archivo = Column(String(300), unique=True, nullable=False)  # nombre del archivo JSON
    id_interaccion = Column(String(100), ForeignKey("interacciones.id_interaccion"), nullable=True)
    agente_usuario = Column(String(50), ForeignKey("agentes.usuario"), nullable=True)
    contenido_json = Column(Text, nullable=True)   # JSON completo del archivo
    tiene_mejora = Column(Boolean, default=False)  # si fue procesado por Gemini
    fecha_procesado = Column(DateTime, nullable=True)

    agente = relationship("Agente", back_populates="transcripciones")
    interaccion = relationship("Interaccion", back_populates="transcripcion")

    def __repr__(self) -> str:
        return f"<Transcripcion archivo={self.archivo!r} mejora={self.tiene_mejora}>"


class Evaluacion(Base):
    """Evaluación de calidad de una llamada realizada por Gemini."""

    __tablename__ = "evaluaciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    archivo = Column(String(300), unique=True, nullable=False)
    id_interaccion = Column(String(100), ForeignKey("interacciones.id_interaccion"), nullable=True)
    agente_usuario = Column(String(50), ForeignKey("agentes.usuario"), nullable=True)

    # Criterios de evaluación (0-100)
    saludo_presentacion = Column(Float, nullable=True)
    identificacion_cliente = Column(Float, nullable=True)
    deteccion_necesidades = Column(Float, nullable=True)
    oferta_productos = Column(Float, nullable=True)
    manejo_objeciones = Column(Float, nullable=True)
    cierre = Column(Float, nullable=True)
    despedida = Column(Float, nullable=True)
    proactividad = Column(Float, nullable=True)
    empatia = Column(Float, nullable=True)
    resolucion_problemas = Column(Float, nullable=True)
    puntaje_total = Column(Float, nullable=True)

    # Información de productos
    primer_plan_ofrecido = Column(String(300), nullable=True)
    se_ofrecio_fibra = Column(Boolean, nullable=True)
    planes_mencionados = Column(Text, nullable=True)

    # Retroalimentación cualitativa
    resumen = Column(Text, nullable=True)
    areas_mejora = Column(Text, nullable=True)
    fortalezas = Column(Text, nullable=True)

    fecha_evaluacion = Column(DateTime, nullable=True)

    agente = relationship("Agente", back_populates="evaluaciones")
    interaccion = relationship("Interaccion", back_populates="evaluacion")

    def __repr__(self) -> str:
        return f"<Evaluacion archivo={self.archivo!r} puntaje={self.puntaje_total}>"


# ---------------------------------------------------------------------------
# Función de inicialización
# ---------------------------------------------------------------------------

def init_db() -> None:
    """Crea todas las tablas si no existen."""
    Base.metadata.create_all(bind=engine)

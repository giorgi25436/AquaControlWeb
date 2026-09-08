import os
import sqlite3
from datetime import datetime
from datetime import date, timedelta
from pathlib import Path

DATABASE_PATH = Path(os.environ.get("DATABASE_PATH", Path(__file__).with_name("database") / "aqua_control.db"))
DATABASE_DIR = DATABASE_PATH.parent
DATABASE_DIR.mkdir(parents=True, exist_ok=True)


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA busy_timeout = 10000")
    connection.execute("PRAGMA journal_mode = WAL")
    connection.execute("PRAGMA synchronous = FULL")
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS trabajadores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cedula TEXT NOT NULL UNIQUE,
                nombres TEXT NOT NULL,
                apellidos TEXT NOT NULL,
                cargo TEXT NOT NULL,
                telefono TEXT NOT NULL,
                direccion TEXT NOT NULL,
                fecha_ingreso TEXT NOT NULL,
                grupo TEXT NOT NULL CHECK (grupo IN ('A', 'B', 'C')),
                estado TEXT NOT NULL CHECK (estado IN ('Activo', 'Inactivo')),
                observaciones TEXT NOT NULL DEFAULT ''
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                usuario TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                rol TEXT NOT NULL CHECK (rol IN ('Administrador', 'Supervisor', 'Consulta')),
                estado TEXT NOT NULL CHECK (estado IN ('Activo', 'Inactivo')),
                fecha_creacion TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS auditoria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                accion TEXT NOT NULL,
                fecha_hora TEXT NOT NULL,
                detalle TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS ciclos (
                grupo TEXT PRIMARY KEY CHECK (grupo IN ('A', 'B', 'C')),
                fecha_inicio TEXT NOT NULL,
                dias_trabajo INTEGER NOT NULL DEFAULT 22,
                dias_descanso INTEGER NOT NULL DEFAULT 8,
                modo_estado TEXT NOT NULL DEFAULT 'Automatico',
                fecha_inicio_manual TEXT,
                fecha_regreso_manual TEXT
            )
            """
        )
        cycle_columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(ciclos)").fetchall()
        }
        for column, definition in (
            ("modo_estado", "TEXT NOT NULL DEFAULT 'Automatico'"),
            ("fecha_inicio_manual", "TEXT"),
            ("fecha_regreso_manual", "TEXT"),
        ):
            if column not in cycle_columns:
                connection.execute(f"ALTER TABLE ciclos ADD COLUMN {column} {definition}")
        existing = connection.execute("SELECT COUNT(*) FROM ciclos").fetchone()[0]
        if existing == 0:
            today = date.today()
            connection.executemany(
                "INSERT INTO ciclos (grupo, fecha_inicio) VALUES (?, ?)",
                [
                    ("A", today.isoformat()),
                    ("B", (today - timedelta(days=10)).isoformat()),
                    ("C", (today - timedelta(days=20)).isoformat()),
                ],
            )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS asistencias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trabajador_id INTEGER NOT NULL,
                cedula TEXT NOT NULL,
                fecha TEXT NOT NULL,
                hora_entrada TEXT,
                hora_salida TEXT,
                estado TEXT NOT NULL CHECK (
                    estado IN ('Presente', 'Ausente', 'Permiso', 'Vacaciones', 'Descanso programado')
                ),
                observacion TEXT NOT NULL DEFAULT '',
                UNIQUE (trabajador_id, fecha),
                FOREIGN KEY (trabajador_id) REFERENCES trabajadores (id)
            )
            """
        )


def active_worker_count():
    with get_connection() as connection:
        return connection.execute(
            "SELECT COUNT(*) FROM trabajadores WHERE estado = 'Activo'"
        ).fetchone()[0]


def attendance_counts(date, excluded_groups=()):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT a.estado, COUNT(*) AS total
            FROM asistencias a
            JOIN trabajadores t ON t.id = a.trabajador_id
            WHERE a.fecha = ?
              AND NOT (a.estado = 'Ausente' AND t.grupo IN ({placeholders}))
            GROUP BY a.estado
            """.format(placeholders=", ".join("?" for _ in excluded_groups) or "NULL"),
            (date, *excluded_groups),
        ).fetchall()
    return {row["estado"]: row["total"] for row in rows}


def audit(user_id, action, detail="", connection=None):
    if connection is None:
        with get_connection() as connection:
            connection.execute(
                "INSERT INTO auditoria (usuario_id, accion, fecha_hora, detalle) VALUES (?, ?, ?, ?)",
                (user_id, action, datetime.now().isoformat(timespec="seconds"), detail),
            )
    else:
        connection.execute(
            "INSERT INTO auditoria (usuario_id, accion, fecha_hora, detalle) VALUES (?, ?, ?, ?)",
            (user_id, action, datetime.now().isoformat(timespec="seconds"), detail),
        )

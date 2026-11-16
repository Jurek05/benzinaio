import sqlite3
import pandas as pd

def connect(db_path: str) -> sqlite3.Connection:
    """Apre la connessione e abilita PRAGMA foreign_keys = ON."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db(conn: sqlite3.Connection) -> None:
    """Crea le tabelle e gli indici se non esistono."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS impianti (
            id_impianto TEXT PRIMARY KEY,
            gestore TEXT,
            bandiera TEXT,
            tipo TEXT,
            nome TEXT,
            indirizzo TEXT,
            comune TEXT,
            provincia TEXT,
            lat REAL,
            lon REAL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_impianti_geo ON impianti(lat, lon)")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS prezzi (
            id_impianto TEXT NOT NULL,
            carburante TEXT NOT NULL,
            is_self INTEGER NOT NULL,
            prezzo REAL,
            data_comunicazione TEXT,
            PRIMARY KEY (id_impianto, carburante, is_self),
            FOREIGN KEY(id_impianto) REFERENCES impianti(id_impianto) ON DELETE CASCADE
        )
    """)

def save_impianti(conn: sqlite3.Connection, impianti: pd.DataFrame) -> None:
    """Salva o aggiorna i dati anagrafici degli impianti."""
    cols = [
        "id_impianto", "gestore", "bandiera", "tipo", "nome",
        "indirizzo", "comune", "provincia", "lat", "lon"
    ]
    data = impianti[cols].values.tolist()
    conn.executemany("""
        INSERT INTO impianti (
            id_impianto, gestore, bandiera, tipo, nome,
            indirizzo, comune, provincia, lat, lon
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id_impianto) DO UPDATE SET
            gestore=excluded.gestore,
            bandiera=excluded.bandiera,
            tipo=excluded.tipo,
            nome=excluded.nome,
            indirizzo=excluded.indirizzo,
            comune=excluded.comune,
            provincia=excluded.provincia,
            lat=excluded.lat,
            lon=excluded.lon
    """, data)

def save_prezzi(conn: sqlite3.Connection, prezzi: pd.DataFrame) -> None:
    """Salva o aggiorna i prezzi dei carburanti."""
    # Assumiamo che il DataFrame abbia le colonne: id_impianto, carburante, prezzo, is_self, data_comunicazione
    cols = ["id_impianto", "carburante", "is_self", "prezzo", "data_comunicazione"]
    data = prezzi[cols].values.tolist()
    conn.executemany("""
        INSERT INTO prezzi (id_impianto, carburante, is_self, prezzo, data_comunicazione)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(id_impianto, carburante, is_self) DO UPDATE SET
            prezzo=excluded.prezzo,
            data_comunicazione=excluded.data_comunicazione
    """, data)

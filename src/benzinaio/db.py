import sqlite3

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
            id_impianto TEXT,
            carburante TEXT,
            is_self INTEGER,
            prezzo REAL,
            data_comunicazione TEXT,
            PRIMARY KEY (id_impianto, carburante, is_self),
            FOREIGN KEY(id_impianto) REFERENCES impianti(id_impianto) ON DELETE CASCADE
        )
    """)

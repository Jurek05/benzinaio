import sqlite3
import pytest
from benzinaio.db import connect, init_db

@pytest.fixture
def db_conn():
    conn = connect(":memory:")
    init_db(conn)
    yield conn
    conn.close()

def test_tables_exist(db_conn):
    """Verifica che le tabelle esistano dopo init_db."""
    cursor = db_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('impianti', 'prezzi')")
    tables = [row[0] for row in cursor.fetchall()]
    assert "impianti" in tables
    assert "prezzi" in tables

def test_foreign_key_constraint(db_conn):
    """Verifica che inserire un prezzo per un id_impianto inesistente sollevi IntegrityError."""
    with pytest.raises(sqlite3.IntegrityError):
        db_conn.execute("""
            INSERT INTO prezzi (id_impianto, carburante, is_self, prezzo, data_comunicazione)
            VALUES ('non_esistente', 'Benzina', 0, 1.85, '2026-11-16')
        """)

import sqlite3
import pandas as pd
import pytest
from benzinaio.db import connect, init_db, save_impianti, save_prezzi

@pytest.fixture
def conn():
    conn = connect(":memory:")
    init_db(conn)
    return conn

def test_no_duplicate_rows(conn):
    impianti = pd.DataFrame({
        "id_impianto": ["1"],
        "gestore": ["g"],
        "bandiera": ["b"],
        "tipo": ["t"],
        "nome": ["n"],
        "indirizzo": ["i"],
        "comune": ["c"],
        "provincia": ["p"],
        "lat": [1.0],
        "lon": [1.0]
    })
    save_impianti(conn, impianti)
    save_impianti(conn, impianti)

    res = conn.execute("SELECT count(*) FROM impianti").fetchone()[0]
    assert res == 1

def test_update_impianto_retains_prices(conn):
    # Setup: impianto + prezzi
    impianti = pd.DataFrame({
        "id_impianto": ["1"], "gestore": ["g"], "bandiera": ["b"], "tipo": ["t"],
        "nome": ["n"], "indirizzo": ["i"], "comune": ["c"], "provincia": ["p"],
        "lat": [1.0], "lon": [1.0]
    })
    prezzi = pd.DataFrame({
        "id_impianto": ["1"], "carburante": ["Benzina"], "is_self": [1],
        "prezzo": [1.5], "data_comunicazione": ["2023-01-01"]
    })
    save_impianti(conn, impianti)
    save_prezzi(conn, prezzi)

    # Update impianto
    impianti_new = impianti.copy()
    impianti_new["gestore"] = "g2"
    save_impianti(conn, impianti_new)

    res = conn.execute("SELECT prezzo FROM prezzi WHERE id_impianto='1'").fetchone()[0]
    assert res == 1.5

def test_update_impianto_saved(conn):
    impianti = pd.DataFrame({
        "id_impianto": ["1"], "gestore": ["g"], "bandiera": ["b"], "tipo": ["t"],
        "nome": ["n"], "indirizzo": ["i"], "comune": ["c"], "provincia": ["p"],
        "lat": [1.0], "lon": [1.0]
    })
    save_impianti(conn, impianti)

    impianti_new = impianti.copy()
    impianti_new["gestore"] = "g2"
    save_impianti(conn, impianti_new)

    res = conn.execute("SELECT gestore FROM impianti WHERE id_impianto='1'").fetchone()[0]
    assert res == "g2"

import pandas as pd
import pytest
import sqlite3
from benzinaio.ingest import clean_prezzi
from benzinaio.db import connect, init_db, save_impianti, save_prezzi

def test_ingest_to_db():
    # 1. Costruire a mano un piccolo DataFrame "raw"
    raw_data = {
        "id_impianto": ["1", "1", "2"],
        "carburante": ["Benzina", "Gasolio", "Benzina"],
        "prezzo": ["1.800", "1.700", "1.850"],
        "is_self": ["0", "1", "0"],
        "data_comunicazione": ["2026-11-16 08:00:00", "2026-11-16 08:00:00", "2026-11-16 08:00:00"]
    }
    raw_df = pd.DataFrame(raw_data)

    # 2. Passarlo a clean_prezzi e verificare
    cleaned_df = clean_prezzi(raw_df)
    assert "data_comunicazione" in cleaned_df.columns
    assert len(cleaned_df) == 3

    # 3. Salvare in un database :memory:
    conn = connect(":memory:")
    init_db(conn)

    # Inserire impianti per foreign key
    impianti_data = pd.DataFrame({
        "id_impianto": ["1", "2"],
        "gestore": ["G1", "G2"],
        "bandiera": ["B1", "B2"],
        "tipo": ["T1", "T2"],
        "nome": ["N1", "N2"],
        "indirizzo": ["I1", "I2"],
        "comune": ["C1", "C2"],
        "provincia": ["P1", "P2"],
        "lat": [40.0, 41.0],
        "lon": [10.0, 11.0]
    })
    save_impianti(conn, impianti_data)

    # Salvare prezzi
    save_prezzi(conn, cleaned_df)

    # 4. Verificare con una SELECT
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM prezzi")
    rows = cursor.fetchall()

    assert len(rows) == 3
    # Verifica che data_comunicazione non sia vuota
    for row in rows:
        # data_comunicazione è la colonna 4 (indice 4)
        assert row[4] is not None
        assert row[4] != ""

    conn.close()

"""Lettura e validazione dei CSV open data del MIMIT."""

import csv
import io
import re
from pathlib import Path

import pandas as pd

SEP = "|"
FUELS = ("Benzina", "Gasolio", "GPL", "Metano")

# Fascia di prezzi accettati, relativa alla mediana di ciascun carburante.
MIN_RATIO = 0.6
MAX_RATIO = 1.4

# Alcuni nomi di impianto contengono un "|" (verificato sui dati reali):
# lo sostituiamo prima di leggere, altrimenti la riga ha un campo in più.
BAD_TEXT = re.compile(r"[ \t]*\|+[ \t]*gestori\.prezzibenzina\.it")
GOOD_TEXT = " - gestori.prezzibenzina.it"

ITALY_LAT = (35, 48)
ITALY_LON = (6, 19)

ANAGRAFICA_COLUMNS = {
    "idImpianto": "id_impianto",
    "Gestore": "gestore",
    "Bandiera": "bandiera",
    "Tipo Impianto": "tipo",
    "Nome Impianto": "nome",
    "Indirizzo": "indirizzo",
    "Comune": "comune",
    "Provincia": "provincia",
    "Latitudine": "lat",
    "Longitudine": "lon",
}
PREZZI_COLUMNS = {
    "idImpianto": "id_impianto",
    "descCarburante": "carburante",
    "prezzo": "prezzo",
    "isSelf": "is_self",
    "dtComu": "data_comunicazione",
}
TEXT_COLUMNS = ("gestore", "bandiera", "tipo", "nome", "indirizzo", "comune", "provincia")


def _read(path: Path) -> pd.DataFrame:
    text = BAD_TEXT.sub(GOOD_TEXT, path.read_text(encoding="utf-8"))
    return pd.read_csv(
        io.StringIO(text),
        sep=SEP,
        skiprows=1,  # la prima riga è "Estrazione del ..."
        dtype=str,
        quoting=csv.QUOTE_NONE,  # i " nei testi non sono delimitatori
        on_bad_lines="error",  # meglio un errore che perdere righe in silenzio
    )


def read_anagrafica(path: Path) -> pd.DataFrame:
    df = _read(path).rename(columns=ANAGRAFICA_COLUMNS)
    for col in TEXT_COLUMNS:
        df[col] = df[col].str.replace('"', "", regex=False).str.strip()
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    # Validazione minima: coordinate presenti e dentro l'Italia.
    valid = df["lat"].between(*ITALY_LAT) & df["lon"].between(*ITALY_LON)
    return df.loc[valid].drop_duplicates("id_impianto").reset_index(drop=True)


def read_prezzi_raw(path: Path) -> pd.DataFrame:
    return _read(path).rename(columns=PREZZI_COLUMNS)


def clean_prezzi(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw[raw["carburante"].isin(FUELS)].copy()
    df["prezzo"] = pd.to_numeric(df["prezzo"], errors="coerce")
    df["is_self"] = (df["is_self"] == "1").astype(int)
    df = df.dropna(subset=["prezzo"])
    # Scarta i prezzi fuori scala rispetto alla mediana del carburante.
    mediana = df.groupby("carburante")["prezzo"].transform("median")
    ok = df["prezzo"].between(mediana * MIN_RATIO, mediana * MAX_RATIO)
    cols = ["id_impianto", "carburante", "prezzo", "is_self"]
    return df.loc[ok, cols].reset_index(drop=True)


def main() -> None:
    data = Path("data")
    ana = read_anagrafica(data / "anagrafica_impianti_attivi.csv")
    raw = read_prezzi_raw(data / "prezzo_alle_8.csv")
    prezzi = clean_prezzi(raw)

    senza_impianto = (~prezzi["id_impianto"].isin(ana["id_impianto"])).sum()
    print(f"impianti validi:            {len(ana)}")
    print(f"prezzi nel file:            {len(raw)}")
    print(f"prezzi tenuti:              {len(prezzi)}")
    print(f"prezzi senza impianto:      {senza_impianto}")
    print(prezzi.groupby("carburante")["prezzo"].agg(["count", "min", "max"]).round(3))


if __name__ == "__main__":
    main()

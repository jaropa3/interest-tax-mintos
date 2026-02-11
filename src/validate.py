import pandas as pd

def validate_tax_data(df, name):
    if (df["kurs_eur"] <= 0).any():
        raise ValueError(f"{name}: kurs EUR ≤ 0")

    if df["Obrót"].isna().any():
        raise ValueError(f"{name}: brak kwot")

    if df.empty:
        raise ValueError(f"{name}: brak danych po filtracji")
    
def validate_statement_df(df):
    required_cols = {
        "Data",
        "Rodzaj płatności",
        "Obrót"
    }

    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Brak kolumn w CSV: {missing}")

    if df["Obrót"].isna().any():
        raise ValueError("Są puste wartości w kolumnie 'Obrót'")

    if not pd.api.types.is_numeric_dtype(df["Obrót"]):
        raise TypeError("Kolumna 'Obrót' nie jest numeryczna")

    if df["Data"].isna().any():
        raise ValueError("Są puste wartości w kolumnie 'Data'")
    
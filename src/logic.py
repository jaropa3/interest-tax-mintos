#cała logika, funkcje itp.
import pandas as pd

def add_eur_rate(df, df_rates):
    df = df.copy()
    df["Data"] = pd.to_datetime(df["Data"])
    df["data_kursu"] = df["Data"] - pd.Timedelta(days=1)

    df = df.sort_values("data_kursu")

    merged = pd.merge_asof( #merge_asof w pandas to specjalny rodzaj merge/join, używany głównie do łączenia danych czasowych, gdzie nie ma dokładnie tych samych kluczy, ale liczy się najbliższa wartość.
        df,
        df_rates[["data_kursu", "kurs_eur"]],
        on="data_kursu",
        direction="backward"
    )

    if merged["kurs_eur"].isna().any():
        raise ValueError("Brak kursu EUR dla części transakcji")

    return merged

def calculate_pln(df):
    df = df.copy()
    df["kwota_pln"] = df["Obrót"] * df["kurs_eur"]
    return df
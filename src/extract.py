import pandas as pd
import requests


def load_statement(path):
    return pd.read_csv(path)


def fetch_eur_rates(start_date, end_date):
    url = (
        "https://api.nbp.pl/api/exchangerates/rates/A/EUR/"
        f"{start_date:%Y-%m-%d}/{end_date:%Y-%m-%d}/?format=json"
    )

    r = requests.get(url, timeout=10)
    r.raise_for_status()
#Jeżeli:

#status = 200–299 → nic nie robi

#status = 4xx lub 5xx → rzuca wyjątek requests.exceptions.HTTPError

#Czyli przerywa program, jeśli zapytanie HTTP się nie powiodło.
    data = r.json()
    if "rates" not in data or not data["rates"]:
        raise ValueError("NBP API zwróciło pustą odpowiedź")

    df = (
        pd.DataFrame(data["rates"])
        .rename(columns={"effectiveDate": "data_kursu", "mid": "kurs_eur"})
    )

    df["data_kursu"] = pd.to_datetime(df["data_kursu"])
    return df.sort_values("data_kursu")
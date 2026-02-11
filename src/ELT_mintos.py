import pandas as pd
import requests
from pathlib import Path
from config import ODSETKI, OPLATY, TAX_RATE
from validate import validate_tax_data, validate_statement_df
from logic import calculate_pln, add_eur_rate

BASE_DIR = Path(__file__).resolve().parent      # projekt/src
ROOT_DIR = BASE_DIR.parent                     # projekt
STATEMENT_PATH = ROOT_DIR / "data" / "20260203-account-statement.csv"

plik_statement = pd.read_csv(STATEMENT_PATH)




validate_statement_df(plik_statement)

plik_statement['Data'] = pd.to_datetime(plik_statement['Data'])
plik_statement['Data'] = plik_statement['Data'].dt.normalize()

wynik = plik_statement[plik_statement["Rodzaj płatności"].isin(ODSETKI)]
oplaty = plik_statement[plik_statement["Rodzaj płatności"].isin(OPLATY)]

df_kurs_EUR_2025 = wynik[wynik['Data'].dt.year == 2025].copy() # operuj na kopii
df_kurs_EUR_2025['data_kursu'] = df_kurs_EUR_2025['Data'] - pd.Timedelta(days=1)

#ZAKRES
start = df_kurs_EUR_2025['data_kursu'].min().strftime('%Y-%m-%d')
end = df_kurs_EUR_2025['data_kursu'].max().strftime('%Y-%m-%d')
#/ZAKRES

url = f"https://api.nbp.pl/api/exchangerates/rates/A/EUR/{start}/{end}/?format=json"
r = requests.get(url, timeout=10)
r.raise_for_status() #Sprawdza kod HTTP odpowiedzi.

#Jeżeli:

#status = 200–299 → nic nie robi

#status = 4xx lub 5xx → rzuca wyjątek requests.exceptions.HTTPError

#Czyli przerywa program, jeśli zapytanie HTTP się nie powiodło.

data = r.json()['rates']

df_kurs_EUR_2025 = (
    pd.DataFrame(data)
    .rename(columns={'effectiveDate': 'data_kursu', 'mid': 'kurs_eur'})
)

wynik = wynik.copy()

wynik['Data'] = pd.to_datetime(wynik['Data'])
wynik['data_kursu'] = wynik['Data'] - pd.Timedelta(days=1)

df_kurs_EUR_2025['data_kursu'] = pd.to_datetime(df_kurs_EUR_2025['data_kursu'])

wynik = wynik.sort_values('data_kursu')
df_kurs_EUR_2025 = df_kurs_EUR_2025.sort_values('data_kursu')

wynik = add_eur_rate(wynik, df_kurs_EUR_2025)

oplaty = oplaty.copy()
oplaty['Data'] = pd.to_datetime(oplaty['Data'])
oplaty['data_kursu'] = oplaty['Data'] - pd.Timedelta(days=1)
oplaty = oplaty.sort_values('data_kursu')

oplaty = add_eur_rate(oplaty, df_kurs_EUR_2025)

validate_tax_data(wynik, "ODSETKI")
validate_tax_data(oplaty, "OPLATY")

oplaty['kwota_pln'] = oplaty['Obrót'] * oplaty['kurs_eur']

suma_oplat_EUR = oplaty["Obrót"].sum()
suma_oplat_PLN = oplaty["kwota_pln"].sum()

#print(oplaty)

wynik['kwota_pln'] = wynik['Obrót'] * wynik['kurs_eur']
wynik = wynik.drop(columns=['Saldo', 'ID transakcji:'])
#print(wynik)
suma_odsetek_EUR = wynik["Obrót"].sum()
suma_odsetek_PLN = wynik["kwota_pln"].sum()
#print(plik_statement)

print("Suma odsetek w EUR:", suma_odsetek_EUR)
print("Suma odsetek po przewalutowaniu na PLN:", suma_odsetek_PLN)

print("Suma oplat w EUR:", suma_oplat_EUR)
print("Suma oplat po przewalutowaniu na PLN:", suma_oplat_PLN)

print("Wyliczony podatek w PLN to:", (suma_odsetek_PLN + suma_oplat_PLN) * TAX_RATE)

#WAŻNE ⚠️

#Oba DataFrame muszą być posortowane po kolumnie on:

#left = left.sort_values('time')
#right = right.sort_values('time')


#Inaczej pandas rzuci błędem albo zrobi coś dziwnego.

#Kiedy NIE używać merge_asof?

#gdy klucze muszą się dokładnie zgadzać → merge

#gdy chcesz klasyczny SQL join → merge

#gdy nie ma sensu pojęcie „najbliższy” (np. kategorie)
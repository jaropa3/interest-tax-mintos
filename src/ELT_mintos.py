import pandas as pd
import requests
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent      # projekt/src
ROOT_DIR = BASE_DIR.parent                     # projekt
STATEMENT_PATH = ROOT_DIR / "data" / "20260203-account-statement.csv"

plik_statement = pd.read_csv(STATEMENT_PATH)
plik_statement['Data'] = pd.to_datetime(plik_statement['Data'])
plik_statement['Data'] = plik_statement['Data'].dt.normalize()
wynik = plik_statement[plik_statement["Rodzaj płatności"].isin(["Przychody z tytułu odsetek za zwłokę przy uzgodnieniu środków w drodze", "Odsetki otrzymane z tytułu odkupu pożyczki", "Otrzymane odsetki", "Odsetki otrzymane od oczekujących płatności", "Otrzymane opłaty za opóźnienia"])]

oplaty = plik_statement[plik_statement["Rodzaj płatności"].isin(["Mintos Core fee", "Mintos Custom Loans fee", "Potrącanie podatku u źródła"])]



df_kurs_EUR_2025 = wynik[wynik['Data'].dt.year == 2025].copy()
df_kurs_EUR_2025['data_kursu'] = df_kurs_EUR_2025['Data'] - pd.Timedelta(days=1)

#ZAKRES
start = df_kurs_EUR_2025['data_kursu'].min().strftime('%Y-%m-%d')
end = df_kurs_EUR_2025['data_kursu'].max().strftime('%Y-%m-%d')
#/ZAKRES

url = f"https://api.nbp.pl/api/exchangerates/rates/A/EUR/{start}/{end}/?format=json"
r = requests.get(url)
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

wynik = pd.merge_asof(              #merge_asof w pandas to specjalny rodzaj merge/join, używany głównie do łączenia danych czasowych, gdzie nie ma dokładnie tych samych kluczy, ale liczy się najbliższa wartość.
                    wynik,
                    df_kurs_EUR_2025[['data_kursu', 'kurs_eur']],
                    on='data_kursu',                 
                    direction='backward')

oplaty = oplaty.copy()
oplaty['Data'] = pd.to_datetime(oplaty['Data'])
oplaty['data_kursu'] = oplaty['Data'] - pd.Timedelta(days=1)
oplaty = oplaty.sort_values('data_kursu')
oplaty = pd.merge_asof(
                    oplaty,
                    df_kurs_EUR_2025[['data_kursu', 'kurs_eur']],
                    on='data_kursu',
                    direction='backward')

oplaty['kwota_pln'] = oplaty['Obrót'] * oplaty['kurs_eur']

suma_oplat_EUR = oplaty["Obrót"].sum()
suma_oplat_PLN = oplaty["kwota_pln"].sum()

print(oplaty)

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

print("Wyliczony podatek w PLN to:", (suma_odsetek_PLN + suma_oplat_PLN) * 0.19)

#WAŻNE ⚠️

#Oba DataFrame muszą być posortowane po kolumnie on:

#left = left.sort_values('time')
#right = right.sort_values('time')


#Inaczej pandas rzuci błędem albo zrobi coś dziwnego.

#Kiedy NIE używać merge_asof?

#gdy klucze muszą się dokładnie zgadzać → merge

#gdy chcesz klasyczny SQL join → merge

#gdy nie ma sensu pojęcie „najbliższy” (np. kategorie)
import pandas as pd
import requests
from pathlib import Path
from config import ODSETKI, OPLATY, TAX_RATE
from validate import validate_tax_data, validate_statement_df
from logic import calculate_pln, add_eur_rate
from extract import load_statement, fetch_eur_rates

BASE_DIR = Path(__file__).resolve().parent      # projekt/src
ROOT_DIR = BASE_DIR.parent                     # projekt
STATEMENT_PATH = ROOT_DIR / "data" / "20260203-account-statement.csv"

def main():
# EXTRACT
    plik_statement = load_statement(STATEMENT_PATH)
    validate_statement_df(plik_statement)

    plik_statement["Data"] = pd.to_datetime(plik_statement["Data"]).dt.normalize()

#TRANSFORM
    wynik = plik_statement[plik_statement["Rodzaj płatności"].isin(ODSETKI)]
    oplaty = plik_statement[plik_statement["Rodzaj płatności"].isin(OPLATY)]

    if wynik.empty and oplaty.empty:
        raise ValueError("Brak transakcji podatkowych")

#ZAKRES DAT
    min_data = plik_statement['Data'].min() - pd.Timedelta(days=1)
    max_data = plik_statement['Data'].max() - pd.Timedelta(days=1)
#/ZAKRES DAT

    df_kurs_EUR_2025 = fetch_eur_rates(min_data, max_data)
 
    wynik = add_eur_rate(wynik, df_kurs_EUR_2025)
    oplaty = add_eur_rate(oplaty, df_kurs_EUR_2025)

    validate_tax_data(wynik, "ODSETKI")
    validate_tax_data(oplaty, "OPLATY")

    oplaty = calculate_pln(oplaty)
    wynik = calculate_pln(wynik)

   # wynik = wynik.drop(columns=['Saldo', 'ID transakcji:'])

    # LOAD / OUTPUT
    suma_oplat_EUR = oplaty["Obrót"].sum()
    suma_oplat_PLN = oplaty["kwota_pln"].sum()
    suma_odsetek_EUR = wynik["Obrót"].sum()
    suma_odsetek_PLN = wynik["kwota_pln"].sum()

    podatek = round((suma_odsetek_PLN + suma_oplat_PLN) * TAX_RATE, 2)

    print("Suma odsetek w EUR:", suma_odsetek_EUR)
    print("Suma odsetek po przewalutowaniu na PLN:", suma_odsetek_PLN)
    print("Suma oplat w EUR:", suma_oplat_EUR)
    print("Suma oplat po przewalutowaniu na PLN:", suma_oplat_PLN)
    print("Wyliczony podatek w PLN to:", podatek)

if __name__ == "__main__":
    main()

#WAŻNE ⚠️

#Oba DataFrame muszą być posortowane po kolumnie on:

#left = left.sort_values('time')
#right = right.sort_values('time')


#Inaczej pandas rzuci błędem albo zrobi coś dziwnego.

#Kiedy NIE używać merge_asof?

#gdy klucze muszą się dokładnie zgadzać → merge

#gdy chcesz klasyczny SQL join → merge

#gdy nie ma sensu pojęcie „najbliższy” (np. kategorie)
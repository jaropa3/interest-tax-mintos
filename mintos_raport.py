import pandas as pd
import tkinter as tk

root = tk.Tk()
root.title("Raport")
listbox = tk.Listbox(
    root,
    selectmode=tk.SINGLE, # SINGLE / MULTIPLE / EXTENDED
    width=50,
    height=20
)

listbox.pack(padx=10, pady=10)

df = pd.read_excel("20260203-account-statement.xlsx")
kolumna7 = df.iloc[:, 6].unique()
print(kolumna7)

# Dodanie elementów z kolumna7
for item in kolumna7:
    listbox.insert(tk.END, item)

root.mainloop()
import pandas as pd
import hashlib
import base64
import os
import numpy as np
import json
from update_deck import resolve_path

settingsdict = json.load(open("settings.json", "r"))
EXCEL_PATH = resolve_path(settingsdict["excel_path"])

df = pd.read_excel(EXCEL_PATH)
df = df.loc[:,["ID", "Italienisch", "Deutsch"]]
df.replace('', np.nan, inplace=True)
df.dropna(inplace=True)

alreadyThere = set()
dupFound = 0

for index, row in df.iterrows():
    id = row["ID"]
    ita = row["Italienisch"]
    deu = row["Deutsch"]

    if ita in alreadyThere:
        print(f"Duplicate found: {id} {ita} {deu}")
        dupFound += 1
    alreadyThere.add(ita)

print(f"{dupFound} duplicates found")
import pandas as pd
import hashlib
import base64
import os
import numpy as np
import json
from update_deck import resolve_path

settingsdict = json.load(open("settings.json", "r"))
EXCEL_PATH = resolve_path(settingsdict["excel_path"])
excel_header_id = settingsdict["excel_headers"]["id"]
excel_header_native_language = settingsdict["excel_headers"]["native_language"]
excel_header_foreign_language = settingsdict["excel_headers"]["foreign_language"]

df = pd.read_excel(EXCEL_PATH)
df = df.loc[:,[excel_header_id, excel_header_foreign_language, excel_header_native_language]]
df.replace('', np.nan, inplace=True)
df.dropna(inplace=True)


def hash_meanings(input : str):
	meanings = [ a.strip() for a in input.split(",") if a.strip() != "" ]
	
	total_hash = sum([ hash(m) for m in meanings ])
		
	return total_hash

def main():
	idToValue = dict()

	alreadyThere = dict()
	dupFound = 0

	for index, row in df.iterrows():
		id = int(row[excel_header_id])
		foreign = row[excel_header_foreign_language]
		native = row[excel_header_native_language]
		
		idToValue[id] = (foreign, native)

		for modifier, lang in enumerate([foreign, native]):
			modified_hash = hash_meanings(lang) + modifier
			if modified_hash in alreadyThere:
				val = alreadyThere[modified_hash]
			else:
				alreadyThere[modified_hash] = val = list()
			val.append(id)

	for hc, ids in alreadyThere.items():
		if len(ids) > 1:
			print(f"Duplicate found: [{', '.join([str(id) for id in ids])}]")
			for id in ids:
				foreign, native = idToValue[id]
				print(f"\t{foreign}    {native}")
			dupFound += 1

	print(f"{dupFound} duplicates found")

if __name__ == "__main__":
	main()

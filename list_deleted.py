import pandas as pd
import json
from update_deck import resolve_path
import numpy as np
from update_deck import load_excel, get_front_native_id, get_front_foreign_id

def get_card_ids_in_anki(anki_export : str):
	df = pd.read_csv(anki_export, delimiter="\t", header=None)
	df = df.loc[:, [0]]
	return set(a[0] for a in df.values)

def get_ideal_card_ids_in_anki(excel_path : str):
	result = set()

	df = load_excel(excel_path)

	for _, row in df.iterrows():
		result.add(get_front_native_id(row))
		result.add(get_front_foreign_id(row))
	return result

def main():
	settingsdict = json.load(open("settings.json", "r"))
	excel_path = resolve_path(settingsdict["excel_path"])
	anki_export = resolve_path(settingsdict["anki_export_for_diffing"])
	
	ids_in_anki = get_card_ids_in_anki(anki_export)
	ideal_ids_in_anki = get_ideal_card_ids_in_anki(excel_path)

	print(len(ids_in_anki))
	print(len(ideal_ids_in_anki))

	missing = sorted(ideal_ids_in_anki - ids_in_anki)
	unwanted_cards = sorted(ids_in_anki - ideal_ids_in_anki)

	print(f"Missing in anki: {missing}")
	print(f"Unwanted cards in anki: {unwanted_cards}")

if __name__ == "__main__":
	main()

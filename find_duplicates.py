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


def hash_meanings(input : str):
	meanings = [ a.strip() for a in input.split(",") if a.strip() != "" ]
	
	total_hash = sum([ hash(m) for m in meanings ])
	
	def take_masculin(input : str):
		# takes both "immalato / immalata" and "der/die Lehrer/in"
		# immalato / immalata			-> case 1
		# der/die Lehrer/in				-> case 2
		# der Lehrer / die Lehrerin		-> case 1
		
		# moo = re.match(r"(?<case2>(?> *\w+\/\w+ *)+)|(?<case1>(?> *\w+ *)+\/(?> *\w+ *)+)", input)
		# if moo is None:
			# return input
		# elif moo.group("case1") is not None:
			# return input.split("/")[0].strip()
		# elif moo.group("case2") is not None:
		return input
		
	return total_hash

def main():
	idToValue = dict()

	alreadyThere = dict()
	dupFound = 0

	for index, row in df.iterrows():
		id = int(row["ID"])
		ita = row["Italienisch"]
		deu = row["Deutsch"]
		
		idToValue[id] = (ita, deu)

		for modifier, lang in enumerate([ita, deu]):
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
				ita, deu = idToValue[id]
				print(f"\t{ita}    {deu}")
			dupFound += 1

	print(f"{dupFound} duplicates found")

if __name__ == "__main__":
	main()

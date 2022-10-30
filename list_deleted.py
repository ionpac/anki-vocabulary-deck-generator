import pandas as pd
import json
from update_deck import resolve_path
import numpy as np


def main():
	settingsdict = json.load(open("settings.json", "r"))
	EXCEL_PATH = resolve_path(settingsdict["excel_path"])

	df = pd.read_excel(EXCEL_PATH)
	df = df.loc[:,["ID", "Italienisch", "Deutsch"]]
	df.replace('', np.nan, inplace=True)
	df.dropna(inplace=True)
	df["ID"] = df["ID"].map(int)

	# ids = df.iloc[:,["ID"]]
	ids = df["ID"].values.tolist()
	available = set(ids)

	lowest = 0
	highest = np.max(ids)
	all = set(range(lowest, highest + 1))

	deleted = sorted(all - available)

	print("Missing:", deleted)

if __name__ == "__main__":
	main()

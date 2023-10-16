import os
import json
import base64
import pandas as pd
import hashlib
import os
import numpy as np
import re
import subprocess
from google.cloud import texttospeech

def resolve_path(path : str):
    result = subprocess.run(["echo", *path.split(' ')], stdout=subprocess.PIPE, shell=True)
    return result.stdout.decode("utf-8").strip()

settingsdict = json.load(open("settings.json", "r"))
EXCEL_PATH = resolve_path(settingsdict["excel_path"])
OUTPUT_CSV_PATH_FOR_ANKI = resolve_path(settingsdict["csv_for_anki_import"])
AUDIO_OUTPUT_FOLDER = resolve_path(settingsdict["audio_file_output"])
abbreviations = settingsdict["abbreviations"]

def text_to_speech(text_to_speech_client, input_text : str, output_path : str, voice_id : int):
    voices = ["it-IT-Wavenet-A", "it-IT-Wavenet-B", "it-IT-Wavenet-C", "it-IT-Wavenet-D"]
    voice = voices[voice_id%len(voices)]

    synthesis_input = texttospeech.SynthesisInput(text=input_text)
    voice = texttospeech.VoiceSelectionParams(language_code="it-IT", name=voice)
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    response = text_to_speech_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

    with open(output_path, mode="wb") as fp:
        fp.write(response.audio_content)

def prepare_for_text_to_speech(text : str):
    text = re.sub(r"\[[^\]]*\]", "", text)
    
    for abbr, repl in abbreviations.items():
        text = text.replace(abbr, repl)
    
    text = re.sub(r"\/", r" / ", text)
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text

def get_filename(input : str):
    return "ip_it_ge_" + base64.b32encode(hashlib.md5(input.encode("UTF-8")).digest()).decode("ASCII")[:16] + ".mp3"

def get_german_card_content(row):
    return row["Deutsch"]

def get_italian_card_content(row):
    return f"""{row["Italienisch"]} [sound:{row["Filename"]}]"""

def get_front_german_id(row):
    return f"""r{row["ID"]}"""

def get_front_italian_id(row):
    return f"""{row["ID"]}"""

def load_excel(excel_path : str):
    df = pd.read_excel(excel_path)
    df = df.loc[:,["ID", "Italienisch", "Deutsch"]]
    df.replace('', np.nan, inplace=True)
    df.dropna(inplace=True)
    df["ID"] = df["ID"].map(int)

    return df

def main():
    df = load_excel(EXCEL_PATH)
    df["ToRead"] = df["Italienisch"].map(prepare_for_text_to_speech)
    df["Filename"] = df["ToRead"].map(get_filename)
    
    os.makedirs(AUDIO_OUTPUT_FOLDER, exist_ok=True)

    api_client = None
    for index, row in df.iterrows():
        to_read = row["ToRead"]
        # print("ToRead", index, f"\"{to_read}\"")
        
        if row["Filename"] == "":
            continue # was deleted

        output_file = os.path.join(AUDIO_OUTPUT_FOLDER, row["Filename"])

        if os.path.isfile(output_file):
            # print(f"Skipping {index} {to_read}")
            continue

        if api_client is None:
            print("Creating google cloud api client...")
            api_client = texttospeech.TextToSpeechClient()
        
        print(f"Reading {index} {to_read}")
        
        text_to_speech(api_client, to_read, output_file, index)

    rows = []
    for index, row in df.iterrows():
        rows.append([get_front_italian_id(row), get_italian_card_content(row), get_german_card_content(row)])
        rows.append([get_front_german_id(row), get_german_card_content(row), get_italian_card_content(row)])

    df_to_export = pd.DataFrame(rows, columns=["ID", "Front", "Back"])

    df_to_export.to_csv(OUTPUT_CSV_PATH_FOR_ANKI, sep="\t", header=False, index=False)
    print("Finished")

if __name__ == "__main__":
	main()

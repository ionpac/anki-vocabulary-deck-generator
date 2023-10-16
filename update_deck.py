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
excel_path = resolve_path(settingsdict["excel_path"])
output_csv_path_for_anki = resolve_path(settingsdict["csv_for_anki_import"])
audio_output_folder = resolve_path(settingsdict["audio_file_output"])
audio_file_prefix = settingsdict["audio_file_prefix"]
abbreviations = settingsdict["abbreviations"]
voices = settingsdict["google_text_to_speech"]["voices"]
language_code = settingsdict["google_text_to_speech"]["language_code"]
excel_header_id = settingsdict["excel_headers"]["id"]
excel_header_native_language = settingsdict["excel_headers"]["native_language"]
excel_header_foreign_language = settingsdict["excel_headers"]["foreign_language"]
front_native_id_prefix = settingsdict["anki"]["front_native_id_prefix"]
front_foreign_id_prefix = settingsdict["anki"]["front_foreign_id_prefix"]

def text_to_speech(text_to_speech_client, input_text : str, output_path : str, voice_id : int):
    voice = voices[voice_id%len(voices)]

    synthesis_input = texttospeech.SynthesisInput(text=input_text)
    voice = texttospeech.VoiceSelectionParams(language_code=language_code, name=voice)
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
    return audio_file_prefix + base64.b32encode(hashlib.md5(input.encode("UTF-8")).digest()).decode("ASCII")[:16] + ".mp3"

def get_native_card_content(row):
    return row[excel_header_native_language]

def get_foreign_card_content(row):
    return f"""{row[excel_header_foreign_language]} [sound:{row["Filename"]}]"""

def get_front_native_id(row):
    return f"""{front_native_id_prefix}{row[excel_header_id]}"""

def get_front_foreign_id(row):
    return f"""{front_foreign_id_prefix}{row[excel_header_id]}"""

def load_excel(excel_path : str):
    df = pd.read_excel(excel_path)
    df = df.loc[:,[excel_header_id, excel_header_foreign_language, excel_header_native_language]]
    df.replace('', np.nan, inplace=True)
    df.dropna(inplace=True)
    df[excel_header_id] = df[excel_header_id].map(int)

    return df

def main():
    df = load_excel(excel_path)
    df["ToRead"] = df[excel_header_foreign_language].map(prepare_for_text_to_speech)
    df["Filename"] = df["ToRead"].map(get_filename)
    
    os.makedirs(audio_output_folder, exist_ok=True)

    api_client = None
    for index, row in df.iterrows():
        to_read = row["ToRead"]
        # print("ToRead", index, f"\"{to_read}\"")
        
        if row["Filename"] == "":
            continue # was deleted

        output_file = os.path.join(audio_output_folder, row["Filename"])

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
        rows.append([get_front_foreign_id(row), get_foreign_card_content(row), get_native_card_content(row)])
        rows.append([get_front_native_id(row), get_native_card_content(row), get_foreign_card_content(row)])

    df_to_export = pd.DataFrame(rows, columns=["ID", "Front", "Back"])

    df_to_export.to_csv(output_csv_path_for_anki, sep="\t", header=False, index=False)
    print("Finished")

if __name__ == "__main__":
	main()

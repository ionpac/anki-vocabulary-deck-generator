## Prerequisites
Install python. I use version 3.9
Install python packages by running
```
pip install numpy pandas openpyxl google-cloud-texttospeech
```

You also might need to setup a google developer account to use the text to speech API.

## How to use

I recommend to get the example deck running first:
1. Import `SampleDeck.apkg` into anki, so you get the Note Type `CardWithID`
2. Add vocabulary to `ItalianVocabulary.xlsx`
3. Make sure that the setting `audio_file_output` in settings.json contains the path to your anki media directory
4. run `update_deck.py`. This should create a file called `for_anki.csv`
5. Import `for_anki.csv` into the deck SampleDeck. In the import settings, set `Notetype` to `CardWithID` and `Existing Notes` to `Update`. The latter makes sure that no duplicates are created for cards with the same ID. The content is updated instead.

## Configuration
All settings are editable in settings.json. Most of them should be self explanatory.

`abbreviations` sets how the text to speech API should read some abbreviations.
`language_code` and `voices` can be taken from https://cloud.google.com/text-to-speech/docs/voices

`front_native_id_prefix` and `front_foreign_id_prefix` are used to build the ID for the Anki cards. Make sure that they are different for different decks you create with this software. Anki cards are not deck specific and cards with the same ID would be overwritten when running update.py. Even if you put them in different decks.

`audio_file_output` is the directory where anki stores its media files for the anki user. If you called your anki profile something other than "User 1", you will have to edit that setting.

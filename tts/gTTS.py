'''
    Filename: gTTS.py
    Module: Softwareprojekt - Kiez:Schnitzel
    Author: Michael P.

    Date: 11/17/2019
    Python version: 3.6.8

    tested with: Ubuntu 18.04
    
    Install:
    pip3 install gtts

    Command-line mp3 player:
    sudo apt install mpg321
'''

from gtts import gTTS
import os, sys

def main(argv):
    # try to open file with text to read
    try:
        with open(argv[0], 'r') as file:
            # Passing the text from the file to the engine
            gtts = gTTS(text=file.read(), lang='de')
    except (IndexError) as e:
        print(e)
        print(".txt Datei muss angegeben werden.")
        # Passing a 'error' text to the engine
        gtts = gTTS(text="Es wurde keine Textdatei angegeben.", lang='de')

    # Saving the audio to .mp3-file
    gtts.save("gTTS-test.mp3")

    # Play the .mp3-file
    os.system("mpg321 gTTS-test.mp3")

if __name__ == "__main__":
    main(sys.argv[1:])
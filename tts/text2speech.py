'''
    Dateiname: text2speech.py
    Modul: Softwareprojekt - Kiez:Schnitzel
    Autor: Tanita Daniel

    Erstellungssdatum: 17.11.2019
    letzte Aederung: 17.11.2019
    Python Version: 3.7

    Getestet auf: Fedora 29
    Benötigt: pyttsx3, espeak
'''

import sys
import pyttsx3 as pt

def main(argv):
    # erhalte Text-Datei die vorgelesen werden soll
    try:
        text = open(argv[0], 'r')
    except (OSError, IOError) as e:
        print(".txt Datei muss angegeben werden.")

    # richte Stimme und Sprache ein
    engine = pt.init()
    engine.setProperty('voice', "german")
    engine.setProperty('rate',120) # 120 pro min

    # lese Zeile für Zeile vor
    for line in text:
        engine.say(line)
        engine.runAndWait()
    return

if __name__ == "__main__":
    main(sys.argv[1:])
'''
    Autor: Felix Doege, Michael Pluhatsch, Tanita Daniel
    Erstellungssdatum: 20.01.2020
    letzte Aederung: 28.01.2020
    Python Version: 3.7
    Getestet auf: Raspbian Buster
    Benötigt: deepspeech 0.6.0 (https://github.com/mozilla/DeepSpeech), RPi.GPIO
'''
import shutil
import os
import datetime
from deepspeech import Model
import sys
import scipy.io.wavfile as wav
# from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import RPi.GPIO as GPIO
import time
from recorder import Recorder
from multiprocessing import Process

# Raspberry Pi
# Aktueller Ordnerpfad
cwd = os.getcwd()

project_root = cwd + '/Audios/'
buildings = cwd + '/Audios/buildings/'
events = cwd + '/Audios/events/'
nature = cwd + '/Audios/nature/'
people = cwd + '/Audios/people/'
misc = cwd + '/Audios/misc/'

# Liste mit allen Kategorien
list_of_category = ["buildings", "events", "nature", "people", "misc"]
list_of_paths = [buildings, events, nature, people, misc]


# nötige Daten für das englische trainierte Model
MODEL_FILE = 'deepspeech-0.6.0-models/output_graph.tflite'
LANG_MODEL = 'deepspeech-0.6.0-models/lm.binary'
TRIE_FILE = 'deepspeech-0.6.0-models/trie'

# Pins der Objekte
buttonPin = 11 # record
button2Pin = 13 # loeschen
button3Pin = 35  # speichern
ledPin = 7  # record
led2Pin = 5 # beleuchtung
halPin = 37 # Intro

# Kategorien
nature = ['tree', 'trees', 'dog', 'dogs', 'cat', 'cats', 'squirrel',
        'squirrels', 'park', 'bush', 'nature', 'wind', 'water', 'earth',
        'birch', 'bark', 'animal', 'animals', 'pet', 'pets', 'wood', 'rain', 'cloud',
        'raining', 'sky', 'cloudy', 'windy', 'weather', 'sun', 'sunshine', 'forest']
events = ['party', 'parties', 'concert', 'concerts',
          'demo', 'demonstration', 'event', 'events', 'marathon'
          'wedding', 'birthday', 'funeral']
buildings = ['restaurant', 'restaurants', 'cafe', 'cinema', 'cinemas', 'kino',
             'theatre', 'school', 'schools', 'church', 'churchs', 'apartment',
             'apartmentcomplex', 'house', 'library', 'shop', 'store', 'supermarket',
             'door']
people = ['people', 'police', 'firefighter', 'teacher', 'child', 'children',
          'pupil', 'student', 'students', 'grandmother', 'grandfather', 'father',
          'mother', 'mom', 'dad', 'fiance', 'wife', 'husband', 'brother',
          'sister', 'sibling', 'siblings', 'person', 'boyfriend', 'girlfriend', 'friend']

# gibt Dateinamen an
def nameFile():
    # Zeitstempel
    Current_Date = datetime.datetime.today().strftime ('%d-%b-%Y')
    Current_Time = datetime.datetime.now().strftime ('%H-%M-%S')
    return str(Current_Time) + '-' + str(Current_Date) + '-' + '.wav'

# Verschiebe eine Datei in die korrekte Kategorie
def move_file(file, category):
    # Hilfsvariable
    counter = 0
    for i in list_of_category:
        
        if category == i:
            path2source = project_root + file
            #print(path2source) # Testen ob Pfad korrekt
            
            path2target = list_of_paths[counter] + file
            #print(list_of_paths[counter] + file) # Testen ob Pfad korrekt
            # Versuche Datei zu verschieben
            try:
                shutil.move(path2source, path2target)
                print("File was moved to ",category)
            except:
                print("File not found")
        counter = counter + 1

def record(filename):
    rec = Recorder(channels = 1, rate = 16000) # da deepspeech, nur 16000hz 
    recfile = rec.open(filename, 'wb')
    # starte Aufnahme
    recfile.start_recording()
    GPIO.output(ledPin, True)
    print("Start Recording")
    while GPIO.input(buttonPin) == GPIO.HIGH: # solang Knopf gedrückt
        time.sleep(0.25)
    # beende Aufnahme
    recfile.stop_recording()
    recfile.close()
    GPIO.output(ledPin, False)
    print("Stop Recording")
    return filename
    
# ordne Text ein (Kategorie)
def findCategories(text):
    categories = []
    for word in nature:
        if word in text:
            categories.append("nature")
            break
    for word in events:
        if word in text:
            categories.append("events")
            break
    for word in buildings:
        if word in text:
            categories.append("buildings")
            break
    for word in people:
        if word in text:
            categories.append("people")
            break
    if len(categories) == 0:
        categories.append("misc")
    return categories

# erhält .wav Datei und wandelt in Text um (DeepSpeech, englisch)
def s2t(file): 
    ds = Model(MODEL_FILE, 500)
    ds.enableDecoderWithLM(LANG_MODEL, TRIE_FILE, 1.50, 2.25)
    
    fs, audio = wav.read(file)
    data = ds.stt(audio)
    return data

def audioProcessing(filename,file):
    text = s2t(filename)
    cat = findCategories(text)
    #print(text, file)
    move_file(file, cat[0])

def main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(buttonPin, GPIO.IN)
    GPIO.setup(button2Pin, GPIO.IN)
    GPIO.setup(button3Pin, GPIO.IN)
    GPIO.setup(halPin, GPIO.IN)
    GPIO.setup(ledPin, GPIO.OUT)
    GPIO.setup(led2Pin, GPIO.OUT)
    GPIO.output(ledPin, False)
    while(True):
        wait = True
        mounted = GPIO.input(halPin) # zustand des trichters (HIGH - Am sensor, LOW - entfernt vom sensor)
        # von 17 bis 7Uhr geht die Beleuchtung an
        if datetime.datetime.now().time() >= datetime.time(17,0,0,0) or datetime.datetime.now().time() <= datetime.time(7,0,0,0):
            GPIO.output(led2Pin, True)
        else: GPIO.output(led2Pin, False)
        
        print("Waiting ...")
        while wait:
            # starte Aufnahme
            if GPIO.input(buttonPin) == GPIO.HIGH:
                file = nameFile()
                filename = record(project_root + file)
                wait = False
            # spiele Intro ab, wenn Trichter an Saeule war und abgenommen wird
            if GPIO.input(halPin) == GPIO.LOW and mounted == GPIO.HIGH:
                print("Spiele Intro ab...", GPIO.input(halPin))
                mounted = GPIO.LOW
                time.sleep(3) # Intro Länge
            # wenn Trichter zr gehaengt wird
            if GPIO.input(halPin) == GPIO.HIGH and mounted == GPIO.LOW:
                print("Hänge Trichter zurück...", GPIO.input(halPin))
                mounted = GPIO.HIGH
                time.sleep(2)
        time.sleep(1)
        
        delete = False
        wait = True
        print("Möchtest du deine Aufnahme speichern oder löschen? Drücke auf den jeweiligen Knopf.")
        while wait:
            if GPIO.input(button2Pin) == GPIO.HIGH:
                print("Aufnahme wurde gelöscht.")
                delete = True
                wait = False
            if GPIO.input(button3Pin) == GPIO.HIGH:
                print("Aufnahme wurde gespeichert.")
                wait = False
        
        # Audioverarbeitung
        if delete == False:
            try:
                p = Process(target=audioProcessing, args=(filename,file, ))
                p.start()
                #p.join()
            except:
                print("Couldn't process Audio.")

if __name__ == "__main__":
    main()
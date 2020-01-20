'''
    Autor: Felix Doege, Michael Pluhatsch, Tanita Daniel
    Erstellungssdatum: 20.01.2020
    letzte Aederung: 20.01.2020
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
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import RPi.GPIO as GPIO
import time
from recorder import Recorder

# Raspberry Pi
project_root = '/home/pi/Documents/Kiez:Schnitzel/Audios/'
buildings = '/home/pi/Documents/Kiez:Schnitzel/Audios/buildings/'
events = '/home/pi/Documents/Kiez:Schnitzel/Audios/events/'
nature = '/home/pi/Documents/Kiez:Schnitzel/Audios/nature/'
people = '/home/pi/Documents/Kiez:Schnitzel/Audios/people/'
misc = '/home/pi/Documents/Kiez:Schnitzel/Audios/misc/'

# Liste mit allen Kategorien
list_of_category = ["buildings", "events", "nature", "people", "misc"]
list_of_paths = [buildings, events, nature, people, misc]


# nötige Daten für das englische trainierte Model
MODEL_FILE = 'deepspeech-0.6.0-models/output_graph.tflite'
LANG_MODEL = 'deepspeech-0.6.0-models/lm.binary'
TRIE_FILE = 'deepspeech-0.6.0-models/trie'

# Pins der Objekte
buttonPin = 11
button2Pin = 13
ledPin = 7

# Kategorien
nature = ['tree', 'trees', 'dog', 'dogs', 'cat', 'cats', 'squirrel',
        'squirrels', 'park', 'bush', 'nature', 'wind', 'water', 'earth',
        'birch', 'bark', 'animal', 'animals', 'pet', 'pets', 'wood', 'rain', 'cloud',
        'raining', 'sky', 'cloudy', 'windy', 'weather', 'sun', 'sunshine', 'forest']
events = ['party', 'parties', 'concert', 'concerts',
          'demo', 'demonstration', 'event', 'events', 'marathon'
          'wedding', 'birthday', 'funeral']
buildings = ['restaurant', 'restaurants', 'cafe', 'cinema', 'cinemas', 'kino',
             'theater', 'school', 'schools', 'church', 'churchs', 'apartment',
             'apartmentcomplex', 'house', 'library', 'shop', 'store', 'supermarket']
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

def main():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(buttonPin, GPIO.IN)
    GPIO.setup(button2Pin, GPIO.IN)
    GPIO.setup(ledPin, GPIO.OUT)
    GPIO.output(ledPin, False)
    wait = True
    
    print("Waiting ...")
    while wait:
        if GPIO.input(buttonPin) == GPIO.HIGH:
            file = nameFile()
            filename = record(project_root + file)
            wait = False
    time.sleep(1)
    
    print("Möchtest du deine Aufnahme löschen? Dann klicke auf den unteren Knopf. Du hast 5s für deine Entscheidung.")
    start = time.process_time()
    while (time.process_time() - start) < 5:
        if GPIO.input(button2Pin) == GPIO.HIGH:
            print("Aufnahme wurde gelöscht.")
            return
    
    text = s2t(filename)
    cat = findCategories(text)
    print(text, file)
    move_file(file, cat[0])

if __name__ == "__main__":
    main()
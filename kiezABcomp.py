'''
    Autor: Felix Doege, Michael Pluhatsch, Tanita Daniel
    Erstellungssdatum: 28.01.2020
    letzte Aederung: 28.01.2020
    Python Version: 3.7
    Getestet auf: Raspbian Buster
    Benötigt: deepspeech 0.6.0 (https://github.com/mozilla/DeepSpeech), RPi.GPIO
'''
import RPi.GPIO as GPIO
import shutil
import sys, os, time, datetime, random
from deepspeech import Model
import scipy.io.wavfile as wav
from recorder import Recorder
from multiprocessing import Process
from KY040 import KY040
from Button import Button
from HallSensor import HallSensor

# Raspberry Pi
# Root Ornderpfad
cwd = os.getcwd()

# Ordnerpfade der Kategorien
project_root = cwd + '/Audios/'
buildings = cwd + '/Audios/buildings/'
events = cwd + '/Audios/events/'
nature = cwd + '/Audios/nature/'
people = cwd + '/Audios/people/'
misc = cwd + '/Audios/misc/'

# Dateiname vom intro
introFile = 'ex1.wav'

# Position des Drehreglers
position = 0

# Liste mit allen Kategorien
list_of_category = ["buildings", "events", "nature", "people", "misc"]
list_of_paths = [buildings, events, nature, people, misc]


# nötige Daten für das englische trainierte Model
MODEL_FILE = 'deepspeech-0.6.0-models/output_graph.tflite'
LANG_MODEL = 'deepspeech-0.6.0-models/lm.binary'
TRIE_FILE = 'deepspeech-0.6.0-models/trie'

# Alle Pinbelegungen:
# Buttons:
BUTTONPIN = 8   # record
BUTTON2PIN = 10 # delete
BUTTON3PIN = 35 # save
BUTTONINTROPIN = 12


mounted = True


# LEDs
LEDPIN = 7  # record
LED2PIN = 5 # Beleuchtung

# Drehregler
CLOCKPIN = 13
DATAPIN = 11
SWITCHPIN = 15

# HallSensor
HALLPIN = 37 # intro
HALL2PIN = 18 # reset Drehregler

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

# Erstellt einen Dateinamen mit der aktuellen Zeit
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

# Startet eine aufnahme uber ein Mikrofon
def record(filename):
    rec = Recorder(channels = 1, rate = 16000) # da deepspeech, nur 16000hz 
    recfile = rec.open(filename, 'wb')
    # starte Aufnahme
    recfile.start_recording()
    GPIO.output(LEDPIN, True)
    print("Start Recording")
    while GPIO.input(BUTTONPIN) == GPIO.HIGH: # solang Knopf gedrückt
        time.sleep(0.25)
    # beende Aufnahme
    recfile.stop_recording()
    recfile.close()
    GPIO.output(LEDPIN, False)
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
    print(text, file)
    move_file(file, cat[0])

def playIntro(channel):
    global mounted
    if GPIO.input(channel) == 0 and mounted == True:
        command = "pkill aplay"
        os.system(command)

        command = "aplay " + project_root + "/" + introFile + " &"
        #lcd.lcd_messageToLine(sound_item, 1)
        print(command)
        os.system(command)
        mounted = False
    if GPIO.input(channel) == 1 and mounted == False:
        print("Hänge Trichter zurück...")
        mounted = True        

# Spielt eine Audiodatei je nach Position des Drehreglers aus 
def rotaryChange(direction):
    global position
    if direction == 0:
        position += 1
    else:
        position -= 1

    print(str(position%20))
    #lcd.lcd_clear()
    #lcd.lcd_messageToLine("Position :" + str(position%20), 2)

    soundPath = posSwitch(position%20)
    # print(soundPath)

    if soundPath is not None:
        if not os.listdir(soundPath) :
            print("Es gibt keine Datei zum Abspielen.")
        else:
            command = "pkill aplay"
            os.system(command)

            listSounds = []
            for (dirpath, dirnames, filenames) in os.walk(soundPath):
                listSounds.extend(filenames)
                break

            print(*listSounds, sep = "\n")

            sound_item = random.choice(listSounds)
            command = "aplay " + soundPath + sound_item + " &"
            #lcd.lcd_messageToLine(sound_item, 1)
            print(command)
            os.system(command)

# Switch-Case fuer die Positionen des Drehreglers:
# Gibt den Ordnerpfad zur Position aus
def posSwitch(argument):
    cwd=os.getcwd()

    posi = {
    3: cwd + '/Audios/misc/',
    7: cwd + '/Audios/buildings/',
    11: cwd + '/Audios/events/',
    15: cwd + '/Audios/nature/',
    19: cwd + '/Audios/people/'
    }
    return posi.get(argument)

# Drehregler Button
def switchPressed(pin):
    # global lcd
    global position

    command = "pkill aplay"
    os.system(command)

    position = 0
    #lcd.lcd_clear()
    #lcd.lcd_messageToLine("Position reset", 1)
    #lcd.lcd_messageToLine("Position :" + str(position%20), 2)
    print("Position reset.")

def buttonPressed(channel):
    if GPIO.input(channel) == 1:
        print("Record Button pressed")
        file = nameFile()
        filename = record(project_root + file)
    else:
        print("Record Button released")
        delete = False
        print("Möchtest du deine Aufnahme löschen? Dann klicke auf den unteren Knopf. Du hast 5s für deine Entscheidung.")
        start = time.process_time()
        while (time.process_time() - start) < 5:
            if GPIO.input(BUTTON2PIN) == GPIO.HIGH:
                print("Aufnahme wurde gelöscht.")
                delete = True
                break
        
        # Audioverarbeitung
        if delete == False:
            try:
                print("Start")
                p = Process(target=audioProcessing, args=(filename,file, ))
                p.start()
                # p.join()
            except:
                print("Couldn't process Audio.")

# HallSensor
# Called if sensor output changes
def sensorTrigger(channel):
    global position

    if GPIO.input(channel):
        # No magnet
        print("No magnet")
    else:
        # Magnet
        print("Magnet")
        position = 0
        #lcd.lcd_clear()
        #lcd.lcd_messageToLine("Position reset", 1)
        #lcd.lcd_messageToLine("Position :" + str(position%20), 2)
        print("Position reset.")

def main():
    # GPIO.setmode(GPIO.BCM)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    # GPIO.setup(BUTTONPIN, GPIO.IN)
    GPIO.setup(BUTTON2PIN, GPIO.IN)
    GPIO.setup(LEDPIN, GPIO.OUT)
    GPIO.output(LEDPIN, False)

    wait = True

    if(GPIO.input(HALLPIN) == GPIO.HIGH):
        mounted = True
    else:
        mounted = False

    ky040 = KY040(CLOCKPIN, DATAPIN, SWITCHPIN, rotaryChange, switchPressed)
    recordButton = Button(BUTTONPIN, buttonPressed)
    hallIntro = HallSensor(HALLPIN, playIntro)
    hallSensor = HallSensor(HALL2PIN, sensorTrigger)

    ky040.start()
    recordButton.start()
    hallIntro.start()
    hallSensor.start()
    
    print('Start program loop...')
    print("Waiting ...")
    try:
        while(True):          
            
            # print("Waiting ...")
            # while wait:
            #     if GPIO.input(BUTTONPIN) == GPIO.HIGH:
            #         file = nameFile()
            #         # filename = record(project_root + file)
            #         wait = False
            time.sleep(0.1)
            
            # delete = False
            # print("Möchtest du deine Aufnahme löschen? Dann klicke auf den unteren Knopf. Du hast 5s für deine Entscheidung.")
            # start = time.process_time()
            # while (time.process_time() - start) < 5:
            #     if GPIO.input(BUTTON2PIN) == GPIO.HIGH:
            #         print("Aufnahme wurde gelöscht.")
            #         delete = True
            #         break
            
            # # Audioverarbeitung
            # if delete == False:
            #     try:
            #         print("Start")
            #         # p = Process(target=audioProcessing, args=(filename,file, ))
            #         # p.start()
            #         # p.join()
            #     except:
            #         print("Couldn't process Audio.")
    finally:
        print('Stopping GPIO monitoring...')
        ky040.stop()
        recordButton.stop()
        hallIntro.stop()
        hallSensor.stop()

        GPIO.cleanup()
        print('Program ended.')

if __name__ == "__main__":
    main()
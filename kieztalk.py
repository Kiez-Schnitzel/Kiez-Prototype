'''
    Autor: Felix Doege, Michael Pluhatsch, Tanita Daniel
    Erstellungssdatum: 28.01.2020
    letzte Aederung: 03.02.2020
    Python Version: 3.7
    Getestet auf: Raspbian Buster
    Benötigt: deepspeech 0.6.1 (https://github.com/mozilla/DeepSpeech), RPi.GPIO
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
from pydub import AudioSegment

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
introFile = 'kieztalkerIntroGeschichten.wav'
recordIntro = 'kieztalkerIntroAufnahme.wav'

# global record Filename
filename = None
gFile = None

# Position des Drehreglers
position = 0

# Liste mit allen Kategorien
list_of_category = ["buildings", "events", "nature", "people", "misc"]
list_of_paths = [buildings, events, nature, people, misc]


# nötige Daten für das englische trainierte Model
MODEL_FILE = 'deepspeech-0.6.1-models/output_graph.tflite'
LANG_MODEL = 'deepspeech-0.6.1-models/lm.binary'
TRIE_FILE = 'deepspeech-0.6.1-models/trie'

# Alle Pinbelegungen:
# Buttons:
BUTTONPIN = 11   # record
BUTTON2PIN = 7 # delete
BUTTON3PIN = 35 # save
#BUTTONINTROPIN = 12


mounted = True


# LEDs
LEDPIN = 13  # record
LED2PIN = 5 # Beleuchtung

# Drehregler
CLOCKPIN = 33
DATAPIN = 31
SWITCHPIN = 29

# HallSensor
HALLPIN = 37 # intro
HALL2PIN = 36 # reset Drehregler

# Kategorien
nature = ['tree', 'trees', 'dog', 'dogs', 'cat', 'cats', 'squirrel', 'stone', 'rock', 'lake', 'stump', 'bush',
        'squirrels', 'park', 'bush', 'nature', 'wind', 'water', 'earth', 'ground', 'gravel',
        'birch', 'bark', 'animal', 'animals', 'pet', 'pets', 'wood', 'rain', 'cloud',
        'raining', 'sky', 'cloudy', 'windy', 'weather', 'sun', 'sunshine', 'forest', 'grass', 'garden']
events = ['party', 'parties', 'concert', 'concerts', 'christmas', 'show',
          'demo', 'demonstration', 'event', 'events', 'marathon', 'bar', 'restaurant', 'dinner', 'lunch',
          'wedding', 'birthday', 'funeral', 'easter', 'graduation', 'fair', 'celebration']
buildings = ['restaurant', 'restaurants', 'cafe', 'cinema', 'cinemas', 'kino',
             'theatre', 'school', 'schools', 'church', 'churches', 'apartment', 'path',
             'complex', 'house', 'library', 'shop', 'store', 'supermarket', 'street', 'streets', 'corner', 'road', 'roads',
             'door', 'building', 'buildings', 'market', 'factory', 'company', 'train', 'station', 'airport']
people = ['people', 'police', 'firefighter', 'teacher', 'child', 'children',
          'pupil', 'student', 'students', 'grandmother', 'grandfather', 'father', 'community', 'communities', 'worker',
          'mother', 'mom', 'dad', 'fiance', 'wife', 'husband', 'brother', 'shop keeper', 'owner', 'tenant', 'landlord', 'man',
          'woman', 'women', 'men', 'boy',
          'sister', 'sibling', 'siblings', 'person', 'boyfriend', 'girlfriend', 'friend', 'friends', 'daughter', 'son', 'girl']

# Erstellt einen Dateinamen mit der aktuellen Zeit
def nameFile():
    # Zeitstempel
    Current_Date = datetime.datetime.today().strftime('%Y-%m-%d')
    Current_Time = datetime.datetime.now().strftime('%H-%M-%S')
    return str(Current_Date) + '-' + str(Current_Time) + '.wav'

# Verschiebe eine Datei in die korrekte Kategorie
def move_file(file, category):
    # Hilfsvariable
    counter = 0
    for i in list_of_category:
        
        if i in category:
            path2source = project_root + file
            print(path2source) # Testen ob Pfad korrekt
            
            path2target = list_of_paths[counter] + file
            print(list_of_paths[counter] + file) # Testen ob Pfad korrekt
            # Versuche Datei zu verschieben
            try:
                shutil.copy(path2source, path2target)
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
    song = AudioSegment.from_wav(filename)
    song = song+6
    song.export(filename, format='wav')
    print(text, file)
    move_file(file, cat)

def playIntro(channel):
    global mounted
    if GPIO.input(channel) == 0:
        command = "pkill aplay"
        # print(command)
        os.system(command)

        time.sleep(0.01)

        command = "aplay " + introFile + " &"
        #lcd.lcd_messageToLine(sound_item, 1)
        # print(command)
        os.system(command)
        mounted = False

        print("Es haengt kein Trichter!")
    if GPIO.input(channel) == 1:
        command = "killall aplay"
        # print(command)
        os.system(command)

        time.sleep(0.01)
        print("Trichter wurde zurueck gehaengt...")
        mounted = True
        # print(GPIO.input(channel), mounted)
              

# Spielt eine Audiodatei je nach Position des Drehreglers aus 
def rotaryChange(direction):
    global position


    if GPIO.input(DATAPIN) == 1:
        position += 1
    if GPIO.input(DATAPIN) == 0:
        position -= 1

    print(str(position%20))
    #lcd.lcd_clear()
    #lcd.lcd_messageToLine("Position :" + str(position%20), 2)

    soundPath = posSwitch(position%20)
    # Wenn Shuffle ausgewaehlt ist, waehle eine "random" Kategorie
    if position%20 == 9:
        positions = [0,3,4,9,1]
        soundPath = posSwitch(random.choice(positions))
    # print(soundPath)

    # Spiele record intro, wenn ausgewaehlt
    if position%20 == 14:
        soundPath = None
        command = "pkill aplay"
        os.system(command)
        print(command)

        time.sleep(0.01)

        command = "aplay " + recordIntro + " &"
        os.system(command)
        print(command)

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

            # print(*listSounds, sep = "\n")

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
    9: cwd + '/Audios/misc/',
    0: cwd + '/Audios/buildings/',
    3: cwd + '/Audios/events/',
    4: cwd + '/Audios/nature/',
    1: cwd + '/Audios/people/',
    #14: 'Audios/'
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
    global gFile
    global filename

    if GPIO.input(channel) == 1 and gFile is None:
        print("Record Button pressed")
        gFile = nameFile()
        filename = record(project_root + gFile)
    if GPIO.input(channel) == 0 and gFile is not None:
        print("Record Button released")
        delete = True
        print("Möchtest du deine Aufnahme löschen? Drücke auf den jeweiligen Knopf.")
        start = time.process_time()
        while (time.process_time() - start) < 5:
            if GPIO.input(BUTTON2PIN) == GPIO.HIGH:
                delete = True
                break
            if GPIO.input(BUTTON3PIN) == GPIO.HIGH:
                print("Aufnahme wurde gespeichert.")
                delete = False
                break
        
        # Audioverarbeitung
        if delete == False and gFile is not None:
            try:
                print("Start")
                GPIO.output(LEDPIN, True)
                time.sleep(0.25)
                GPIO.output(LEDPIN, False)
                p = Process(target=audioProcessing, args=(filename,gFile, ))
                p.start()
                # p.join()
                gFile = None
                filename = None
            except:
                e = sys.exc_info()[0]
                print("Couldn't process Audio:", e)
                
        if delete == True and gFile is not None:
            gFile = None
            filename = None
            
            GPIO.output(LEDPIN, True)
            time.sleep(0.25)
            GPIO.output(LEDPIN, False)
            time.sleep(0.25)
            GPIO.output(LEDPIN, True)
            time.sleep(0.25)
            GPIO.output(LEDPIN, False)
            print("Aufnahme wurde gelöscht.")


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
    global clkPinLast
    
    # GPIO.setmode(GPIO.BCM)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

    GPIO.setup(BUTTON2PIN, GPIO.IN)
    GPIO.setup(BUTTON3PIN, GPIO.IN)
    GPIO.setup(BUTTON2PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(BUTTON3PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    GPIO.setup(LEDPIN, GPIO.OUT)
    GPIO.output(LEDPIN, False)
    GPIO.setup(LED2PIN, GPIO.OUT)

    ky040 = KY040(CLOCKPIN, DATAPIN, SWITCHPIN, rotaryChange, switchPressed)
    recordButton = Button(BUTTONPIN, buttonPressed)
    hallIntro = HallSensor(HALLPIN, playIntro)
    hallSensor = HallSensor(HALL2PIN, sensorTrigger)

    if(GPIO.input(HALLPIN) == GPIO.HIGH):
        mounted = True
        print("init:", mounted)
    else:
        mounted = False
        print("init:", mounted)

    print(mounted)

    ky040.start()
    recordButton.start()
    hallIntro.start()
    hallSensor.start()

    print('Start program loop...')
    print("Waiting ...")
    try:
        while(True):
            # von 17 bis 7Uhr geht die Beleuchtung an
            if datetime.datetime.now().time() >= datetime.time(17,0,0,0) or datetime.datetime.now().time() <= datetime.time(7,0,0,0):
                GPIO.output(LED2PIN, True)
            else: GPIO.output(LED2PIN, False)
            time.sleep(0.01)
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

'''
    Autor: Tanita Daniel
    Erstellungssdatum: 12.01.2020
    letzte Aederung: 12.01.2020
    Python Version: 3.7
    Getestet auf: Raspbian Buster
    Benötigt: deepspeech 0.6.0 (https://github.com/mozilla/DeepSpeech), RPi.GPIO
'''

from deepspeech import Model
import sys
import scipy.io.wavfile as wav
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import RPi.GPIO as GPIO
import time
from recorder import Recorder

# nötige Daten für das englische trainierte Model
MODEL_FILE = 'deepspeech-0.6.0-models/output_graph.tflite'
LANG_MODEL = 'deepspeech-0.6.0-models/lm.binary'
TRIE_FILE = 'deepspeech-0.6.0-models/trie'

# Pins der Objekte
buttonPin = 11
ledPin = 7

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

# ordne Audio ein
def sentiment_score(text):
    sid_obj = SentimentIntensityAnalyzer()
    sentiment_dict = sid_obj.polarity_scores(text)
    
    if sentiment_dict['compound'] >= 0.05:
        return "Positiv"
    elif sentiment_dict['compound'] <= -0.05:
        return "Negativ"
    else:
        return "Neutral"

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
    GPIO.setup(ledPin, GPIO.OUT)
    GPIO.output(ledPin, False)
    wait = True
    
    print("Waiting ...")
    while wait:
        if GPIO.input(buttonPin) == GPIO.HIGH:
            filename = record('audio.wav')
            wait = False
    time.sleep(1)
    
    #file = 'ex1.wav'
    text = s2t(filename)
    print(text, sentiment_score(text))

if __name__ == "__main__":
    main()
'''
    Autor: Tanita Daniel
    Erstellungssdatum: 07.01.2020
    letzte Aederung: 07.01.2020
    Python Version: 3.7
    Getestet auf: Raspbian Buster
    Benötigt: deepspeech 0.6.1 (https://github.com/mozilla/DeepSpeech)
'''

from deepspeech import Model
import sys
import scipy.io.wavfile as wav

# nötige Daten für das trainierte Model
MODEL_FILE = 'deepspeech-0.6.1-models/output_graph.tflite'
LANG_MODEL = 'deepspeech-0.6.1-models/lm.binary'
TRIE_FILE = 'deepspeech-0.6.1-models/trie'

def main(argv):
    if len(argv) < 1:
        print("No .wav File given.")
        return
    
    ds = Model(MODEL_FILE, 500)
    ds.enableDecoderWithLM(LANG_MODEL, TRIE_FILE, 1.50, 2.25)
    
    fs, audio = wav.read(argv[0])
    data = ds.stt(audio)
    print(data)

if __name__ == "__main__":
    main(sys.argv[1:])
# https://docs.python.org/3/library/shutil.html
# https://stackabuse.com/how-to-create-move-and-delete-files-in-python/

import os
import shutil

file = input("Bitte geben Sie eine Datei an: ")
category = input("Bitte geben Sie eine Kategorie an: ")

# Pfade für Kategorien
# Windows
project_root = 'C:\\Users\\exark\\Dropbox\\Private\\coding IXD\\Files\\project_root\\'
buildings = 'C:\\Users\\exark\\Dropbox\\Private\\coding IXD\\Files\\project_root\\buildings\\'
events = 'C:\\Users\\exark\\Dropbox\\Private\\coding IXD\\Files\\project_root\\events\\'
nature = 'C:\\Users\\exark\\Dropbox\\Private\\coding IXD\\Files\\project_root\\nature\\'
people = 'C:\\Users\\exark\\Dropbox\\Private\\coding IXD\\Files\\project_root\\people\\'
misc = 'C:\\Users\\exark\\Dropbox\\Private\\coding IXD\\Files\\project_root\\misc\\'

"""
# Raspberry Pi
project_root = '/home/pi/project_root/'
buildings = '/home/pi/project_root/buildings/'
events = '/home/pi/project_root/events/'
nature = '/home/pi/project_root/nature/'
people = '/home/pi/project_root/people/'
misc = '/home/pi/project_root/misc/'
"""

# Liste mit allen Kategorien
list_of_category = ["buildings", "events", "nature", "people", "misc"]
list_of_paths = [buildings, events, nature, people, misc]

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


move_file(file, category)
# https://datatofish.com/rename-file-python/
# https://docs.python.org/3/library/os.html#module-os

import os
import datetime

file = input("Bitte geben Sie eine Datei an: ")

# Pfad zur Datei
# Windows
project_root = 'C:\\Users\\exark\\Dropbox\\Private\\coding IXD\\Files\\project_root\\'

"""
# Raspberry Pi
project_root = '/home/pi/project_root/'
"""

# Zeitstempel
Current_Date = datetime.datetime.today().strftime ('%d-%b-%Y')
Current_Time = datetime.datetime.now().strftime ('%H-%M-%S')
#print(Current_Time) # Testausgabe der aktuellen Uhrzeit

# Pfad zur Datei 
path_old_name = project_root + file

# Pfad der umbenannten Datei
path_new_name = project_root + str(Current_Time) + '-' + str(Current_Date) + '-' + file

def rename(file):    
    try:
        os.rename(path_old_name, path_new_name)
        print("File renamed")
    except:
        print("File could not be renamed")

rename(file)

#os.rename(r'C:\Users\Ron\Desktop\Test\Products.txt',r'C:\Users\Ron\Desktop\Test\Shipped Products_' + str(Current_Date) + '.txt')
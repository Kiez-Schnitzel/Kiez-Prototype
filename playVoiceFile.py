import RPi.GPIO as GPIO
from KY040 import KY040
import os, time
import random
#import lcddriver
    
if __name__ == "__main__":

    print('Program start.')

    CLOCKPIN = 6
    DATAPIN = 13
    SWITCHPIN = 5

    #lcd = lcddriver.lcd()
    position = 0

    def rotaryChange(direction):
        global position
        
        if direction == 0:
            position += 1
        else:
            position -= 1 

        print(str(position%20))
        #lcd.lcd_clear()
        #lcd.lcd_messageToLine("Position :" + str(position%20), 2)

        soundPath = posSwitch(position)
        # print(soundPath)

        if soundPath is not None:
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

    def posSwitch(argument):
        posi = {
            3: "/home/pi/Documents/Kiez:Schnitzel/Audios/misc/",
            7: "/home/pi/Documents/Kiez:Schnitzel/Audios/buildings/",
            11: "/home/pi/Documents/Kiez:Schnitzel/Audios/events/",
            15: "/home/pi/Documents/Kiez:Schnitzel/Audios/nature/",
            19: "/home/pi/Documents/Kiez:Schnitzel/Audios/people/"
        }
        return posi.get(argument)
    
    def switchPressed(pin):
        #global lcd
        global position

        command = "pkill aplay"
        os.system(command)

        position = 0
        #lcd.lcd_clear()
        #lcd.lcd_messageToLine("Position reset", 1)
        #lcd.lcd_messageToLine("Position :" + str(position%20), 2)
        print("Position reset.")
        
    GPIO.setmode(GPIO.BCM)
    ky040 = KY040(CLOCKPIN, DATAPIN, SWITCHPIN, rotaryChange, switchPressed)

    print('Launch switch monitor class.')

    ky040.start()
    print('Start program loop...')
    # Clear display
    #lcd.lcd_clear()

    # Show text on display
    #lcd.lcd_messageToLine("Start program...", 1)
    #lcd.lcd_messageToLine("Position :" + str(position%20), 2)
    try:
        while True:
            time.sleep(0.01)
            # print('Sleep...')
    finally:
        print('Stopping GPIO monitoring...')
        ky040.stop()
        GPIO.cleanup()
        print('Program ended.')
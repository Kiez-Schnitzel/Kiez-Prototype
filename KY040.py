import RPi.GPIO as GPIO
from time import sleep


class KY040:

    CLOCKWISE = 0
    ANTICLOCKWISE = 1
    DEBOUNCE = 140

    def __init__(self, clockPin, dataPin, switchPin, rotaryCallback, switchCallback):
        #persist values
        self.clockPin = clockPin
        self.dataPin = dataPin
        self.switchPin = switchPin
        self.rotaryCallback = rotaryCallback
        self.switchCallback = switchCallback

        #setup pins
        GPIO.setup(clockPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(dataPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(switchPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def start(self):
        GPIO.add_event_detect(self.clockPin, GPIO.FALLING, callback=self._clockCallback, bouncetime=self.DEBOUNCE)
        GPIO.add_event_detect(self.switchPin, GPIO.FALLING, callback=self.switchCallback, bouncetime=self.DEBOUNCE)

    def stop(self):
        GPIO.remove_event_detect(self.clockPin)
        GPIO.remove_event_detect(self.switchPin)
    
    def _clockCallback(self, pin):
        if GPIO.input(self.clockPin) == 0:
            self.rotaryCallback(GPIO.input(self.dataPin))

    def _switchCallback(self, pin):
        self.switchCallback()


import RPi.GPIO as GPIO

class Button:

    def __init__(self, buttonPin, pressedCallback):
        #persist values
        self.buttonPin = buttonPin
        self.pressedCallback = pressedCallback

        #setup pins
        GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def start(self):
        GPIO.add_event_detect(self.buttonPin, GPIO.BOTH, callback=self.pressedCallback)

    def stop(self):
        GPIO.remove_event_detect(self.buttonPin)


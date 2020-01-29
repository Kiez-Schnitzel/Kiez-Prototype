import RPi.GPIO as GPIO

class HallSensor:

    def __init__(self, hallPin, sensorCallback):
        #persist values
        self.hallPin = hallPin
        self.sensorCallback = sensorCallback

        #setup pins
        GPIO.setup(hallPin , GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def start(self):
        GPIO.add_event_detect(self.hallPin, GPIO.BOTH, callback=self.sensorCallback, bouncetime=100)  

    def stop(self):
        GPIO.remove_event_detect(self.hallPin)


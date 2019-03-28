import RPi.GPIO as GPIO 
import datetime 
from collections import deque 


D_TX = 8
D_RX = 10 
P1 = 11
P2 = 13
AOS_SAT = 15
CAMERA_CAPTURE = 12 

class pinHandler : 

    def __init__(self): 
        GPIO.setup([P1, P2, CAMERA_CAPTURE], GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 
        GPIO.setup([AOS_SAT], GPIO.OUT, initial=GPIO.HIGH)
        GPIO.add_event_detect(P1, GPIO.BOTH, self.handle) 
        GPIO.add_event_detect(P2, GPIO.BOTH, self.handle)         
        GPIO.add_event_detect(CAMERA_CAPTURE, GPIO.RISING, self.handle) 

        #interval queue
        self.qint = deque(maxlen=2)

    
    def handle(self, pin): 
        dt = datetime.utcnow() 
        microsecond = dt.microsecond 
        self.qint.append(microsecond) 
        if(len(self.qint) ==2):
            interval = self.qint[1]-self.qint[0] 
            print(pin, interval)

    def aos_out(self): 
        GPIO.output(AOS_SAT, GPIO.HIGH) 
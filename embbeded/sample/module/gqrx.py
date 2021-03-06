from scipy.constants import c 
from collections import deque 
from datetime import datetime
import telnetlib  

class gqrx : 
    def __init__(self, center_frequency): 
        self.center_frequency = center_frequency
        self.distance_deque = deque(maxlen=2)
        self.timeutc = deque(maxlen=2) 
        self.gqrx = telnetlib.Telnet("127.0.0.1", 7356) 

    def calculate_corrected_frequency(self,distance):
        dt = datetime.utcnow() 
        self.timeutc.append(dt) 
        self.distance_deque.append(distance) 
        if(len(self.distance_deque) == 2):
            interval = (self.timeutc[1]-self.timeutc[0]).total_seconds()
#            print(self.distance_deque[1], ' - ', self.distance_deque[0], ' = ', self.distance_deque[1]-self.distance_deque[0])
            relative_velocity = (self.distance_deque[1]-self.distance_deque[0])
            delta_f = relative_velocity * self.center_frequency/c 
            corrected_frequency = (self.center_frequency + (-1*delta_f))

#            print("doppler      : ", -1*delta_f," corrected freq        : ", corrected_frequency, end="\r")
#            print(corrected_frequency)
            return corrected_frequency 

    def correct_doppler(self, distance):
        freq = self.calculate_corrected_frequency(distance)
        if type(freq) != type(None) : 
            freq = str(round(freq)).split(".")[0]
            self.gqrx.write(("F "+freq+" \n").encode('ascii'))

        return freq

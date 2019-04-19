from datetime import datetime 
from skyfield.api import Topos, load 
from _thread import * 
from collections import deque 
from scipy.constants import c

from module import direwolf 
from module import gqrx 
from module import tle

from date_time import date_time 
from task import task_runner
from inout import io_handler 
from fifo import fifo 

import schedule
import threading 
import select 
import socket 
import os
import variables

# distance between station and passing satellite 
dis = 0 

# satellite elevation 

# queue dis 
qdis = deque(maxlen=2)

# theading lock 
print_lock = threading.Lock()
    
# delta time in second 
deltaT = 1

# satellite center frequency 
center_frequency = 435880000 #Hz

class main : 
    
    def __init__(self):
        self.distance = 0 
        self.callsign = "YDE2E"
        self.sstv_mode = "Robot36"
        self.calculate_az_el = True
        
        # last edit Fri Apr 19, 13:33:03 | Problem : io butuh fifo, fifo butuh io
        # Status : Done (New Rules, [1] & [2])
        self.io = io_handler(datetime = date_time) 
        self.fifo = fifo(
                callsign = self.callsign, 
                variables = variables, 
                datetime = date_time)

        self.fifo.set_master_io(self.io) # Rule [1] 
        self.io.set_master_fifo(self.fifo) # Rule [1] 
        self.io.set_camera_handler(
                mode = self.sstv_mode,
                datetime = date_time) # Rule [2]

        self.task = task_runner(
                main = self,
                callsign = self.callsign,
                fifo = self.fifo, 
                mode = self.sstv_mode,
                datetime = date_time
                )

    def set_frequency(self) : 
        radio.correct_doppler(self.distance)

    def recv_data(self):
        while True : 
            receive = rx.receive()
            if receive.closed == True : 
                print_lock.release()
                break

            self.task.parse_command(receive.callsign, receive.message)

    def get_az_el(self): 

        global dis, deltaT
        
        append_status = False

        # last elevation
        el_last = ''
        
        while True and self.calculate_az_el :  
            schedule.run_pending()

            # satellite's  obital element 
            tl = tle()
            satellite = tl.satellite

            ts = load.timescale() 
            t = ts.utc(datetime.utcnow().year, 
                       datetime.utcnow().month, 
                       datetime.utcnow().day, 
                       datetime.utcnow().hour, 
                       datetime.utcnow().minute, 
                       datetime.utcnow().second) 
            my_location = Topos('6.2405 S', '106.9501 E') 
            difference = satellite - my_location
            topocentric = difference.at(t) 
            el,az,distance = topocentric.altaz()
            self.distance = distance.m

            #append first distance 
            if(not append_status):
                self.set_frequency()
                append_status = True 

            if str(el) != el_last :
                self.set_frequency()
                
                '''
                print("\n")
                print(satellite)
                print("elevation    : ", el)
                print("azimuth      : ", az) 
                print("slant range  : ", distance.m)
                '''
                el_last = str(el)

if __name__ == "__main__": 

    run = main()
    rx = direwolf('localhost', 8001)
    radio = gqrx(center_frequency, deltaT)  

    while True :
        print('RUNNING')
        print_lock.acquire()
        start_new_thread(run.get_az_el, ())
        start_new_thread(run.recv_data, ())

    
    


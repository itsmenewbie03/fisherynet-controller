from typing import Union
import serial
import time
from datetime import timedelta
import random

class Reader:
    reading: Union[int, float, bytearray] 
    def __init__(self,port:str,baud_rate: int) -> None:
        self.port = port
        self.baud_rate = baud_rate
        
    def read(self):
        return 
        
    def get_reading(self):
        return self.reading

class UltrasonicSensor(Reader):
    def read(self):
        print(":: Starting Ultrasonic Distance Sensor Reader")
        # TODO: properly handle error
        try:
            ser = serial.Serial(self.port, self.baud_rate)
        except:
            print(":: [DEBUG_MODE] failed to connect to serial")
            print(":: [DEBUG_MODE] dummy data ahead")
            data_list = []
            for _ in range(10):
                data_list.append(random.randint(1,500))
            self.reading = sum(data_list) /  len(data_list)
            return 
        
        print(":: Connected to serial port:", self.port)
        start = time.time()
        data_list = []
        while True:
            if len(data_list) == 10:
                print(":: Process Completed")
                print(data_list)
                print(":: Average Distance:", sum(data_list)/len(data_list))
                break
            if ser.in_waiting <= 0:
                continue
            if len(data_list) <= 0:
                end = time.time()
                print(f":: Got data after {timedelta(seconds=int(end)-(start))}")
            # TODO: parse the data
            data = ser.read(ser.in_waiting)
            distance = int(data.split(b':')[1].split(b'\r')[0].decode())
            # WARN: this blindly accepts the reading, 
            # WARN: additional calibration must be added to normalize the readings
            data_list.append(distance)
        ser.close()
        open(f"ultrasonic_sensor_data_{time.time()}.txt", "w").write(str(data_list))
        print(":: Data saved to file")
        self.reading = sum(data_list) /  len(data_list)
from datetime import timedelta
from os import remove
from os import path
import random
import subprocess
import time
from typing import Union

import requests
import serial

class Reader:
    
    reading: Union[int, float, bytearray] 
    
    def __init__(self,port:str | None = None,baud_rate: int = 0) -> None:
        self.port = port
        self.baud_rate = baud_rate
        
    def read(self) -> None:
        return 
        
    def get_reading(self):
        return self.reading

class UltrasonicSensor(Reader):
    
    def __validate(self,distance: int) -> bool:
        """
        Checks if the distance is valid based on observed readings
        """
        if distance >= 500:
            # INFO: this is a null or unreadable data
            # or something is blocking the sensor
            return False
        # if distance in range(200,300):
        #     # INFO: uneven surface detected
        #     # and it's scattered
        #     return False
        # if distance in range(100,199):
        #     # INFO: uneven surface detected
        #     # and it's near with each other
        #     return False
        return True
    
    def read(self) -> None:
        print(":: [READER] Starting Ultrasonic Distance Sensor Reader")
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
        
        print(":: [READER] Connected to serial port:", self.port)
        start = time.time()
        data_list = []
        
        while True:
            if len(data_list) == 20:
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
            print(f":: [DEBUG] {data}")
            distance = int(data.split(b':')[1].split(b'\r')[0].decode())
            
            # WARN: this blindly accepts the reading, 
            # WARN: additional calibration must be added to normalize the readings
            if self.__validate(distance):
                data_list.append(distance)
                
        ser.close()
        self.reading = sum(data_list) /  len(data_list)
        
class Camera(Reader):
    device_idx: int = 0

    def __init__(self) -> None:
        # TODO: load the cached device index
        if path.exists("device_idx.txt"):
            self.device_idx = int(open("device_idx.txt").read())
 
    def capture_image(self,device_idx: int = device_idx, resolution: str="1280x720"):
        """
        Captures an image from the specified device and resolution.

        Args:
            device_idx (int, optional): Index of the video device (default: "/dev/video0").
            resolution (str, optional): Resolution string for fswebcam (default: "1280x720").

        Returns:
            bytearray: The captured image data as a bytearray or None if an error occurs.
        """
        
        device = f"/dev/video{device_idx}"
        command = ["fswebcam", "--no-timestamp", "--no-banner", "-r", resolution, "--png", "1", "-d", device, "imgs/temp.png"]

        # NOTE: i don't understand a single thing below xD
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
            errors = process.stderr.read().decode("utf-8") # pyright: ignore
            if not "Writing PNG" in errors:
                if "Inappropriate ioctl for device" in errors:
                    print(f":: [CAMERA_ERROR] {device} is not a valid device, trying another device...")
                    if device_idx == 3:
                        print(":: [ERROR] No valid device found")
                        return None
                    # NOTE: recursively call the function to try the next device
                    return self.capture_image(device_idx + 1, resolution)
                print(f":: [ERROR] fswebcam failed: {errors}")
                return None
            # TODO: cache the working device_idx
            if device_idx != 0 and not path.exists("device_idx.txt"):
                print(f":: [CAMERA] Device {device} is working, caching the device index")
                open("device_idx.txt", "w").write(str(device_idx))
                
            # INFO: read the image
            data = open("imgs/temp.png", "rb").read()
            # INFO: delete the image because we don't have infinite storage
            remove("imgs/temp.png")
            return bytearray(data)
    
    urls = [
        "https://vimafoods.com/wp-content/uploads/2020/05/tilapia-negra-1481x1536.jpg",
        "https://www.ocean-treasure.com/wp-content/uploads/2020/03/tilapia5.jpg",
        "https://zipgrow.com/wp-content/uploads/2022/05/4fishfarm.png",
        "https://5.imimg.com/data5/TQ/NA/MY-37031394/tilapia-fish.jpg",
    ]
    
    def __random_image(self) -> bytearray:
        url = random.choice(self.urls) 
        print(f":: [CAMERA] returning random image from {url}")
        data = requests.get(url).content
        return bytearray(data)
    
    def read(self) -> None:
        print(":: [READER] Starting Camera Reader")
        img_buf = self.capture_image()
        if not img_buf:
            print(":: [DEBUG_MODE] failed to connect to camera")
            print(":: [DEBUG_MODE] dummy data ahead")
            # NOTE: we will randomly select a URL to fetch and return the buffer
            self.reading = self.__random_image()
            return
        self.reading = img_buf

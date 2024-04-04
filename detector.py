from typing import Optional
import cv2 
import numpy as np
from datetime import datetime

class Detector:
    # TODO: add actual CF
    CF: float = 69
    
    def __init__(self, cf: Optional[float] = None) -> None:
        if cf:
            self.CF = cf
        print(f":: [DETECTOR] initialized with CF {self.CF}")
        return      
    
    def __get_area_px(self, image: bytearray) -> float:
        # Load the image 
        image_buf = np.asarray(image,dtype="uint8");
        img = cv2.imdecode(image_buf,cv2.IMREAD_COLOR)
        # Convert the image to grayscale 
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
        # Apply a threshold to the image to 
        # separate the objects from the background 
        _, thresh = cv2.threshold( 
            gray, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU) 
          
        # Find the contours of the objects in the image 
        contours, _ = cv2.findContours( 
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 
          
        largest_countour = max(contours, key=cv2.contourArea)
        # INFO: Loop through the contours and calculate the area of each object 
        # NOTE: only used for debugging
        for cnt in contours: 
            area = cv2.contourArea(cnt) 
            if area < 1000:
                continue
            x, y, w, h = cv2.boundingRect(cnt) 
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2) 
            cv2.putText(img, str(area), (x, y), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2) 
        # INFO: write the image to a file 
        # used for visualizing how the detection went
        cv2.imwrite(f'sized_{datetime.now()}.png', img) 
        area = cv2.contourArea(largest_countour) 
        return area

    def detect_size(self,image: bytearray,distance: float) -> float:
        area_px: float = self.__get_area_px(image)
        area_est: float = (area_px * self.CF) / distance
        return area_est

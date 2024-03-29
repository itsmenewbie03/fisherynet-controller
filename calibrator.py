from detector import Detector
from reader import Camera, UltrasonicSensor

class Calibrator:
    
    def __init__(self) -> None:
        return  
    
    def calibrate_detection(self):
        # controller = Controller()
        # controller.check_pins([port.GATE_TRIGGER])
        # controller.toggle_pin(port.GATE_TRIGGER,state.HIGH);
        # gate_trigger_state = controller.read_pin(port.GATE_TRIGGER)
        # print(f":: [GATE_TRIGGER] : {gate_trigger_state}")
        
        reader = UltrasonicSensor("/dev/ttyUSB0",115_200) 
        reader.read() 
        distance = reader.get_reading()
        print(f":: [DISTANCE] : {distance}")
        
        camera = Camera()
        camera.read()
        image = camera.get_reading()
        
        detector = Detector(1.5)
        # NOTE: we know that image is indeed a bytearray 
        # we will make pyright shut up
        # This issue with types kinda tells me that I should do some refactoring
        est_size = detector.detect_size(image,float(distance)) # pyright: ignore
        print(f":: [DETECTOR] Estimated Size: {est_size}")

from detector import Detector
from reader import Camera, UltrasonicSensor
from controller import Controller

class Calibrator:
     
    def __init__(self) -> None:
        from config_handler import ConfigHandler
        self.config_handler = ConfigHandler(Controller())
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
        # NOTE: import localy to avoid circular imports
        from connector import CONFIGS
        calibration_factor = self.config_handler.get_config(CONFIGS.CALIBRATION_FACTOR) 
        print(f":: [CALIBRATOR] initialized with calibration_factor of {calibration_factor}")
        detector = Detector(calibration_factor)
        # NOTE: we know that image is indeed a bytearray 
        # we will make pyright shut up
        # This issue with types kinda tells me that I should do some refactoring
        est_size = detector.detect_size(image,float(distance)) # pyright: ignore
        print(f":: [DETECTOR] Estimated Size: {est_size}")
        return est_size

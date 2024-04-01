from time import sleep
from calibrator import Calibrator
from connector import CONFIGS, Connector
from controller import Controller, GPIO_MAPPING as port , PORT_MODE as mode, PORT_STATE as state
from detector import Detector
from reader import Camera, UltrasonicSensor
    
if __name__ == "__main__":
    controller = Controller()
    controller.check_pins([port.GATE_TRIGGER])
    
    if controller.prod:
        print(f":: [BLINK_TEST] performing a blink test...")
        for x in range(5):
            controller.toggle_pin(port.GATE_TRIGGER,state.HIGH if x%2==0 else state.LOW);
            # controller.toggle_pin(port.EXTRA_1,state.HIGH if x%2==0 else state.LOW);
            # controller.toggle_pin(port.EXTRA_2,state.HIGH if x%2==0 else state.LOW);
            sleep(1)
        
    controller.toggle_pin(port.GATE_TRIGGER,state.LOW);
    # controller.toggle_pin(port.EXTRA_1,state.LOW);
    # controller.toggle_pin(port.EXTRA_2,state.LOW);
    
    gate_trigger_state = controller.read_pin(port.GATE_TRIGGER)
    print(f":: [GATE_TRIGGER] : {gate_trigger_state}")

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
    
    connector = Connector(controller)
    connector.calibrator = Calibrator()
    # min_fish_size = connector.get_config(CONFIGS.MIN_FISH_SIZE);
    # print(f":: [CONFIG] Min Fish Size: {min_fish_size} we made it to main")
    connector.start()
    # connector.stop()

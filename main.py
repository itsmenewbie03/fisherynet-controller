from controller import Controller, GPIO_MAPPING as port , PORT_MODE as mode, PORT_STATE as state
from reader import UltrasonicSensor
if __name__ == "__main__":
    controller = Controller()
    controller.toggle_pin(port.GATE_TRIGGER,state.HIGH);

    reader = UltrasonicSensor("deez",69_420) 
    reader.read() 
    print(f":: [DISTANCE] : {reader.get_reading()}")

from controller import Controller, GPIO_MAPPING as port , PORT_MODE as mode, PORT_STATE as state
from reader import UltrasonicSensor
if __name__ == "__main__":
    controller = Controller()
    controller.check_pins([port.GATE_TRIGGER])
    controller.toggle_pin(port.GATE_TRIGGER,state.HIGH);
    gate_trigger_state = controller.read_pin(port.GATE_TRIGGER)
    print(f":: [GATE_TRIGGER] : {gate_trigger_state}")

    reader = UltrasonicSensor("deez",69_420) 
    reader.read() 
    print(f":: [DISTANCE] : {reader.get_reading()}")

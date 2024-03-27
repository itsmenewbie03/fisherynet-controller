from controller import Controller, GPIO_MAPPING as port , PORT_MODE as mode, PORT_STATE as state

if __name__ == "__main__":
    controller = Controller()
    controller.toggle_pin(port.GATE_TRIGGER,state.HIGH);

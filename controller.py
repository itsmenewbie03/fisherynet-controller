from enum import Enum
from pyA20.gpio import gpio # pyright: ignore

class GPIO_MAPPING(Enum):
    GATE_TRIGGER = "PA7"
    # NOTE: add more GPIO as needed
    
class PORT_MODE(Enum):
    INPUT = 0
    OUTPUT = 1
    
class PORT_STATE(Enum):
    HIGH = 1
    LOW = 0
    
class PORT_PULL_MODE(Enum):
    CLEAR = 0
    PULLUP = 1
    PULLDOWN = 2
    
class Controller:
    def __init__(self, test: bool=True):
        self.test = test 
        self.__prepare_pins()
    
    def __prepare_pins(self):
        """
        This function gets called when the class gets instantiated.
        This is done to properly configure the pins.
        e.g setting port.PA7 as OUTPUT. The implementation of this
        would be heavily reliant on the design of the system.
        """
        # TODO: implement the configuration needed
        if not self.test:
            return
        print(f":: [PREPARE_PINS] ...") 
        # NOTE: a dummy setup 
        self.__set_pin_mode(GPIO_MAPPING.GATE_TRIGGER,PORT_MODE.OUTPUT)
        
    def __set_pin_mode(self,pin: GPIO_MAPPING,mode: PORT_MODE):
        """
        This function is for setting the pin mode conveniently.
        This will wrap the function provided by the module.
        """
        if not self.test:
            # NOTE: implement the toggle
            # we are coding on a Laptop not on the Actual Orange PI one
            # so we gotta make the framework for it first
            return
        print(f":: [PORT_MODE_SET] port: {pin}|{pin.value} mode: {mode}|{mode.value}")         
        
    def toggle_pin(self,pin: GPIO_MAPPING, mode: PORT_STATE):
        if not self.test:
            # NOTE: implement the toggle
            # we are coding on a Laptop not on the Actual Orange PI one
            # so we gotta make the framework for it first
            return
        print(f":: [TOGGLE] port: {pin}|{pin.value} mode: {mode}|{mode.value}") 

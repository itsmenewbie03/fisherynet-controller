from enum import Enum
from typing import Optional

from pyA20.gpio import gpio, port  # pyright: ignore


class GPIO_MAPPING(Enum):
    GATE_TRIGGER = port.PA7 if hasattr(port, "PA7") else -69
    EXTRA_1 = port.PA8 if hasattr(port, "PA8") else -70
    EXTRA_2 = port.PA9 if hasattr(port, "PA9") else -71
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
    def __init__(self) -> None:
        self.prod = self.__on_armbian()
        print(f":: [ENV] {'PROD' if self.prod else 'TEST'}")
        if self.prod:
            gpio.init()
        self.__prepare_pins()

    def __on_armbian(self) -> bool:
        """
        This function will check if the system is running on Armbian
        or not. This is done to make the code more portable.
        """
        with open("/etc/os-release") as f:
            os_release_data = {
                line.rstrip().split("=", 1)[0]: line.rstrip().split("=", 1)[1]
                for line in f
            }
        return "armbian" in os_release_data["PRETTY_NAME"].lower()

    def __prepare_pins(self) -> None:
        """
        This function gets called when the class gets instantiated.
        This is done to properly configure the pins.
        e.g setting port.PA7 as OUTPUT. The implementation of this
        would be heavily reliant on the design of the system.
        """
        print(f":: [INIT] Preparing pins...")
        # TODO: implement the configuration needed
        if self.prod:
            self.__set_pin_mode(GPIO_MAPPING.GATE_TRIGGER, PORT_MODE.OUTPUT)
            self.__set_pin_mode(GPIO_MAPPING.EXTRA_1, PORT_MODE.OUTPUT)
            self.__set_pin_mode(GPIO_MAPPING.EXTRA_2, PORT_MODE.OUTPUT)
            return
        # NOTE: a dummy setup
        self.__set_pin_mode(GPIO_MAPPING.GATE_TRIGGER, PORT_MODE.OUTPUT)

    def __check_pin_mode(self, port: GPIO_MAPPING) -> Optional[int]:
        """
        Returns the current mode of the pin
        """
        if self.prod:
            status = gpio.getcfg(port.value)
            return status
        print(f":: [PIN_CHECK] ...")

    def __set_pin_mode(self, pin: GPIO_MAPPING, mode: PORT_MODE) -> None:
        """
        This function is for setting the PIN MODE not STATUS conveniently.
        This will wrap the function provided by the module.
        """
        if self.prod:
            gpio.setcfg(pin.value, mode.value)
            return
        print(f":: [PORT_MODE_SET] port: {pin}|{pin.value} mode: {mode}|{mode.value}")

    def __set_pin_status(self, pin: GPIO_MAPPING, state: PORT_STATE) -> None:
        """
        This function is for setting the PIN STATUS not MODE conveniently.
        This will wrap the function provided by the module.
        """
        if self.prod:
            gpio.output(pin.value, state.value)
            return
        print(
            f":: [PORT_STATUS_SET] port: {pin}|{pin.value} state: {state}|{state.value}"
        )

    def __get_pin_status(self, pin: GPIO_MAPPING) -> Optional[int]:
        if self.prod:
            status = gpio.input(pin.value)
            return status
        print(f":: [PORT_STATUS_GET] port: {pin}|{pin.value}")

    def check_pins(self, pins: list[GPIO_MAPPING]) -> None:
        """
        Checks the current mode of each pins
        """
        if self.prod:
            for pin in pins:
                status = self.__check_pin_mode(pin)
                print(f":: [PIN_CHECK] port: {pin}|{pin.value} status: {status}")
            return
        print(f":: [PIN_CHECK] Checking all pins...")

    def toggle_pin(self, pin: GPIO_MAPPING, state: PORT_STATE) -> None:
        if self.prod:
            self.__set_pin_status(pin, state)
            print(f":: [TOGGLE] port: {pin}|{pin.value} mode: {state}|{state.value}")
            return
        print(f":: [TOGGLE] port: {pin}|{pin.value} mode: {state}|{state.value}")

    def read_pin(self, pin: GPIO_MAPPING) -> Optional[int]:
        if self.prod:
            status = self.__get_pin_status(pin)
            return status
        print(f":: [READ] port: {pin}|{pin.value}")

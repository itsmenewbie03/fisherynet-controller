from enum import Enum
from time import sleep
from typing import Any

import paho.mqtt.client as mqtt

from calibrator import Calibrator
from controller import GPIO_MAPPING, PORT_STATE, Controller
from reporter import Reporter


class CONFIGS(Enum):
    MIN_FISH_SIZE = "min_fish_size"
    CALIBRATION_FACTOR = "calibration_factor"


class Connector:
    is_config_handler = False
    broker = "mqtt.eclipseprojects.io"
    port = 1883
    keepalive = 60
    client: mqtt.Client
    calibrator: Calibrator
    controller: Controller
    # NOTE: making this Any to avoid circular imports
    config_handler: Any
    # NOTE: we store the config here because I think having `config`
    config: dict = {}
    stopped: bool = False

    def __init__(self, controller: Controller, config_handler: Any) -> None:
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)  # pyright: ignore
        self.client.on_connect = self.__on_connect
        self.client.on_message = self.__on_message
        self.client.connect(self.broker, self.port, self.keepalive)
        self.controller = controller
        self.config_handler = config_handler

    def __on_message(self, client, userdata, msg) -> None:
        # INFO: call the internal message handler
        self.__message_handler(msg.topic, msg.payload)

    def __on_connect(self, client, userdata, flags, reason_code, properties) -> None:
        print(
            f":: [{'GENERIC' if not self.is_config_handler else 'CONFIG_HANDLER'}_CONNECTOR] Connected with result code {reason_code}"
        )
        if not self.is_config_handler:
            print(
                ":: [GENERIC_CONNECTOR] Subscribing to COMMANDS and TOGGLE_PORT topic..."
            )
            self.client.subscribe("FISHERYNET|COMMANDS")
            self.client.subscribe("FISHERYNET|TOGGLE_PORT")
            # NOTE: if connector is not a config_hanlder we won't subscribe to CONFIG_RESPONSE
            # early return
            return
        print(":: [CONFIG_HANDLER_CONNECTOR] Subscribing to CONFIG_RESPONSE")
        self.client.subscribe("FISHERYNET|CONFIG_RESPONSE")

    def __message_handler(self, topic: bytes, payload: bytes) -> None:
        """
        Handle the massage according to the topic in which they are sent
        """
        match str(topic):
            case "FISHERYNET|COMMANDS":
                self.__command_handler(payload)

            case "FISHERYNET|CONFIG_RESPONSE":
                print(f":: [MESSAGE_HANDER] Configuration Response: {payload}")
                self.__config_handler(payload)

            case "FISHERYNET|TOGGLE_PORT":
                print(f":: [TOGGLE_HANDLER] {payload}")
                self.__toggle_handler(payload)

            case _:
                print(
                    f":: [MESSAGE_HANDER] handler for topic {topic} is not yet implemented."
                )

    def __command_handler(self, command: bytes):
        match command:
            case b"START_CAMERA_STREAM":
                # TODO: implement the actual handler
                print(f":: [COMMAND_HANDLER]  starting camera stream")

            case b"START_DETECTION_CALIBRATION":
                print(f":: [COMMAND_HANDLER]  detection calibration started")
                est_size = self.calibrator.calibrate_detection()
                # call the get config to compare the estimated size with the minimum fish size
                min_fish_size = self.config_handler.get_config(CONFIGS.MIN_FISH_SIZE)
                is_big = est_size >= min_fish_size
                print(
                    f":: [COMMAND_HANDLER]  estimated size: {est_size}, minimum fish size: {min_fish_size}"
                )
                print(
                    f":: [COMMAND_HANDLER]  the fish is {'big' if is_big else 'small'}"
                )
                # NOTE: we only send the report if the connector is not a config_handler
                # weird this should not be hit since we're not subscribe to COMMANDS
                if is_big:
                    Reporter.send_report(f"est_size={est_size}")  # pyright: ignore
                self.client.publish(
                    "FISHERYNET|CALIBRATION_RESPONSE", f"est_size={est_size}"
                )
            case _:
                print(
                    f":: [COMMAND_HANDLER] handler for command {str(command)} is not yet implemented."
                )

    def __toggle_handler(self, port: bytes):
        port_str = port.decode()
        if not hasattr(GPIO_MAPPING, port_str):
            return
        target_port = getattr(GPIO_MAPPING, port_str)
        state = self.controller.read_pin(target_port)
        if state == None:
            print(f":: [TOGGLE_HANDLER] failed to read {target_port}")
            return
        state = PORT_STATE.HIGH if state == 0 else PORT_STATE.LOW
        print(f":: [TOGGLE_HANDLER] toggled {target_port} to {state}")
        self.controller.toggle_pin(target_port, state)

    def __config_handler(self, config: bytes):
        key, value = config.decode().split("=")
        match key:
            case "min_fish_size":
                print(f":: [CONFIG_HANDLER] Minimum fish size: {value}")
                self.config["min_fish_size"] = int(value)
            case "calibration_factor":
                print(f":: [CONFIG_HANDLER] Calibration factor: {value}")
                self.config["calibration_factor"] = float(value)
            case _:
                pass
                # print(f":: [CONFIG_HANDLER] handler for config {config} is not yet implemented.")

    def get_config(self, config_name: CONFIGS):
        print(f":: [GET_CONFIG] Requesting configuration: {config_name.value}")
        self.client.loop_start()
        # NOTE: we subscribe because we wil only be interested in CONFIG_RESPONSE
        # when we actually request for a configuration
        self.client.publish("FISHERYNET|CONFIG_REQUEST", f"{config_name.value}")

        retry_count = 0
        while not config_name.value in self.config:
            if retry_count > 10:
                print(":: [GET_CONFIG] Maximum retries reached")
                raise Exception("Maximum retries reached")
            print(":: [GET_CONFIG] Waiting for response...")
            retry_count += 1
            sleep(1)

        self.client.loop_stop()
        config_value = self.config[config_name.value]
        print(f":: [GET_CONFIG_SUCCESS] Configuration: {config_value}")
        self.config.pop(config_name.value)
        return config_value

    def start(self) -> None:
        print(":: [MQTT_LISTENER] main listener started! ")
        self.client.loop_start()
        while True:
            if self.stopped:
                print(":: [MQTT_LISTENER] main listener stopped! ")
                self.client.disconnect()
                break
        self.client.loop_stop()

    def stop(self) -> None:
        self.stopped = True

import paho.mqtt.client as mqtt

from time import sleep
from calibrator import Calibrator
from enum import Enum

class CONFIGS(Enum):
    MIN_FISH_SIZE = "min_fish_size"    

class Connector:
    broker = "mqtt.eclipseprojects.io"
    port = 1883
    keepalive = 60
    client: mqtt.Client 
    calibrator: Calibrator
    # NOTE: we store the config here because I think having `config`
    config: dict = {}
    
    def __init__(self) -> None:
        self.client =  mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)    # pyright: ignore 
        self.client.on_connect = self.__on_connect
        self.client.on_message = self.__on_message
        self.client.connect(self.broker,self.port,self.keepalive)    
        
    def __on_message(self,client, userdata, msg) -> None:
        # INFO: call the internal message handler
        self.__message_handler(msg.topic,msg.payload)
        
    def __on_connect(self,client, userdata, flags, reason_code, properties) -> None:
        print(f":: [CONNECTOR] Connected with result code {reason_code}")
        client.subscribe("FISHERYNET|COMMANDS")
        # INFO: topic for configuration response from server
        
    def __message_handler(self, topic: bytes, payload: bytes) -> None:
        """
        Handle the massage according to the topic in which they are sent 
        """
        match str(topic):
            case "FISHERYNET|COMMANDS":
                self.__command_handler(payload)
                
            case "FISHERYNET|CONFIG_RESPONSE":
                # print(f":: [MESSAGE_HANDER] Configuration Response: {payload}")
                self.__config_handler(payload)
                
            case _:
                print(f":: [MESSAGE_HANDER] handler for topic {topic} is not yet implemented.")
                
    def __command_handler(self, command: bytes):
        match command:
            case b"START_CAMERA_STREAM":
                # TODO: implement the actual handler
                print(f":: [COMMAND_HANDLER]  starting camera stream")
                
            case b"START_DETECTION_CALIBRATION":
                print(f":: [COMMAND_HANDLER]  detection calibration started")
                self.calibrator.calibrate_detection()
                
            case _:
                print(f":: [COMMAND_HANDLER] handler for command {str(command)} is not yet implemented.")
                
    def __config_handler(self, config: bytes):
        key, value = config.decode().split("=")
        match key:
            case "min_fish_size":
                print(f":: [CONFIG_HANDLER] Minimum fish size: {value}")
                self.config["min_fish_size"] = int(value)
            case _:
                pass
                # print(f":: [CONFIG_HANDLER] handler for config {config} is not yet implemented.")
                
    def get_config(self,config_name:CONFIGS):
        print(f":: [GET_CONFIG] Requesting configuration: {config_name.value}")
        self.client.loop_start()
        # NOTE: we subscribe because we wil only be interested in CONFIG_RESPONSE
        # when we actually request for a configuration
        self.client.subscribe("FISHERYNET|CONFIG_RESPONSE")
        self.client.publish("FISHERYNET|CONFIG_REQUEST",f"{config_name.value}")
        while not config_name.value in self.config:
            print(":: [GET_CONFIG] Waiting for response...")
            sleep(0.5)
        config_value = self.config[config_name.value]
        print(f":: [GET_CONFIG] Configuration: {config_value}")
        self.client.unsubscribe("FISHERYNET|CONFIG_RESPONSE")
        self.client.loop_stop()
        return config_value
    
    def start(self) -> None:
        self.client.loop_forever()
        
    def stop(self) -> None:
        self.client.disconnect()

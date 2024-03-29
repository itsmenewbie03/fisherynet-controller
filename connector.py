from time import sleep
import paho.mqtt.client as mqtt

from enum import Enum
from calibrator import Calibrator

class CONFIGS(Enum):
    MIN_FISH_SIZE = "min_fish_size"    
    
class Connector:
    broker = "mqtt.eclipseprojects.io"
    port = 1883
    keepalive = 60
    client: mqtt.Client 
    calibrator: Calibrator
    
    def __on_message(self,client, userdata, msg) -> None:
        # print(msg.topic+" "+str(msg.payload))
        # INFO: call the internal message handler
        self.__message_handler(msg.topic,msg.payload)
        
    def __on_connect(self,client, userdata, flags, reason_code, properties) -> None:
        print(f":: [CONNECTOR] Connected with result code {reason_code}")
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("FISHERYNET|COMMANDS")
        
    def __message_handler(self, topic: bytes, payload: bytes) -> None:
        """
        Handle the massage according to the topic in which they are sent 
        """
        match str(topic):
            case "FISHERYNET|COMMANDS":
                self.__command_handler(payload)
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
                
    def __init__(self) -> None:
        self.client =  mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)    # pyright: ignore 
        self.client.on_connect = self.__on_connect
        self.client.on_message = self.__on_message
        self.client.connect(self.broker,self.port,self.keepalive)    
        
    def get_config(self,config_name:CONFIGS):
        self.client.loop_start()
        self.client.publish("FISHERYNET|CONFIG_REQUEST",f"{config_name.value}")
        # NOTE: ensure the message is published
        sleep(2)
        self.client.loop_stop()
        
    def start(self) -> None:
        self.client.loop_forever()
        
    def stop(self) -> None:
        self.client.disconnect()

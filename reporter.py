import paho.mqtt.client as mqtt

class Reporter:
    """
    Class to handle the reporting of the fisherynet system
    This will publish the reports to the FISHERYNET|REPORTS topic
    The report will be in format `est_size=x.y`
    """

    broker = "mqtt.eclipseprojects.io"
    port = 1883
    keepalive = 60

    _client = None  # Use a private static variable for the client

    def __init__(self) -> None:
        pass  # No need for object-specific initialization in a static implementation

    @staticmethod
    def connect():
        """
        Connects the Reporter to the MQTT broker.

        This method is called to establish the connection before sending reports.
        """

        if Reporter._client is None:
            Reporter._client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2) # pyright: ignore
            Reporter._client.on_connect = Reporter.__on_connect
            Reporter._client.on_message = Reporter.__on_message
            Reporter._client.connect(Reporter.broker, Reporter.port, Reporter.keepalive)

    @staticmethod
    def __on_message(client, userdata, msg):
        print(f":: [REPORTER] {msg.topic} {msg.payload}")

    @staticmethod
    def __on_connect(client, userdata, flags, reason_code, properties):
        print(f":: [REPORTER] Connected with result code {reason_code}")

    @staticmethod
    def send_report(report: str) -> None:
        """
        Sends a report to the FISHERYNET|REPORTS topic.

        Validates the report format (est_size=x.y) before publishing.
        """

        Reporter.connect()  # Ensure connection before publishing

        key, value = report.split("=")
        if key != "est_size":
            print(":: [REPORTER] Invalid report format")
            return

        Reporter._client.loop_start()  # Start the client loop for publishing # pyright: ignore
        Reporter._client.publish("FISHERYNET|REPORTS", report, 2) # pyright: ignore
        Reporter._client.loop_stop()  # Stop the client loop after publishingoop_stop() # pyright: ignore

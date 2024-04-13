import queue  # Use queue for thread-safe communication
import threading

import serial


class SensorReaderThread(threading.Thread):
    """
    Thread class to continuously read sensor data from a serial port.
    """

    def __init__(self, port, baudrate, timeout=1):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        self.data_queue = queue.Queue()  # Thread-safe queue for sensor readings
        self.stop_event = threading.Event()  # Event to signal thread termination

    def run(self):
        """
        Continuously reads data from the serial port and stores it in the queue.
        """
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            while not self.stop_event.is_set():
                data = (
                    self.serial.readline().decode("utf-8").strip()
                )  # Decode and strip
                self.data_queue.put(data)  # Add data to the queue
        except Exception as e:
            print(f"Error reading serial port: {e}")
        finally:
            if self.serial:
                self.serial.close()

    def get_latest_reading(self):
        """
        Retrieves the latest reading from the queue (if available).
        Blocks until data is available or a timeout occurs.
        """
        try:
            return self.data_queue.get(timeout=1)  # Block for 1 second
        except queue.Empty:
            return None  # Return None if no data available

    def stop(self):
        """
        Gracefully stops the thread.
        """
        self.stop_event.set()
        self.join()  # Wait for the thread to finish

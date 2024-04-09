from connector import Connector
from controller import Controller


class ConfigHandler(Connector):
    """
    Just a clone of the Connector Class
    We will use this to get configurations
    we are having issues with the network loop.
    If this works I would punch myself
    """

    def __init__(self, controller: Controller) -> None:
        self.is_config_handler = True
        super().__init__(controller, self)

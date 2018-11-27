# coding: utf-8
__all__ = [
    "BaseCommunicator",
    "BaseDeviceHandler",
    "BaseDeviceError",
]


from abc import ABCMeta, abstractmethod


class BaseCommunicator(object, metaclass=ABCMeta):
    """Communicator with a device.

    This is the base class of device communicators.

    Note:
        This class itself is not used, but it is inherited by
        child classes and used.

    Args:
        *args: Valiable length arguments.

    Attribute:
        METHOD (str): Communication method.
        connection (bool): Connection indicator.
            If it is true, the connection has been established.
        terminator (str): Terminator character.
    """
    METHOD = ""

    connection = False
    terminator = ""

    def __init__(self, *args):
        if len(args) != 0:
            self.open(*args)

    def __del__(self):
        if self.connection == True:
            self.close()

    @abstractmethod
    def open(self):
        """Open the connection to the device.

        Note:
            This method must be overridden in the child class.
        """
        pass

    @abstractmethod
    def close(self):
        """Close the connection to the device.

        Note:
            This method must be overridden in the child class.
        """
        pass

    @abstractmethod
    def send(self, msg):
        """Send a message to the device.

        Note:
            This method must be overridden in the child class.

        Args:
            msg (str): A message to send the device.
        """
        pass

    @abstractmethod
    def receive(self, byte):
        """Receive the response of the device.

        Note:
            This method must be overridden in the child class.

        Args:
            byte (int): Bytes to read.
        """
        pass

    def query(self, msg, byte=1024):
        """Query a message to the device.

        Args:
            msg (str): A message to query the device.

        Return:
            ret (bytes): The response of the device.
        """
        self.send(msg)
        ret = self.receive(byte)
        return ret

    @classmethod
    def set_terminator(cls, term_char):
        """Set the termination character.

        Args:
            term_char (str): Termination character.

        Return:
            None
        """
        cls.terminator = term_char
        return


class BaseDeviceHandler(object):
    """A device handler.

    This is the base class of device handlers.

    Note:
        This class itself is not used, but it is inherited by
        child classes and used.

    Args:
        com (weathermonitor.communicator):
            Communicator instance to control the device.

    Attributes:
        MANUFACTURER (str): Manufacturer of the device.
        PRODUCT_NAME (str): Name of the device.
        CLASSIFICATION (str): Classification of the device.
    """
    MANUFACTURER = ""
    PRODUCT_NAME = ""
    CLASSIFICATION = ""

    def __init__(self, com):
        self.com = com
        self.open()

    def open(self):
        """Open the connection to the device.
        Note:
            This method uses the one of "com".
        Return:
            None
        """
        self.com.open()
        return

    def close(self):
        """Close the connection to the device.
        Note:
            This method uses the one of "com".
        Return:
            None
        """
        self.com.close()
        return


class BaseDeviceError(Exception):
    """Base exception class of the weather monitor.

    Note:
        This class itself is not used, but it is inheritted by
        child classes and used.
    """
    pass
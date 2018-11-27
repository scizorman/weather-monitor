# coding: utf-8
__all__ = [
    "SocketCom",
]


import socket
from .core import BaseCommunicator


class SocketCom(BaseCommunicator):
    """The communicator with the device via "Socket".

    This is a child class of the base class
    "weathermonitor.core.BaseCommunicator".

    Args:
        host (str): IP Address of a device.
        port (int): Port of a device.
        timeout (float): A read timeout values.
            Defaults to 1.0.

    Attributes:
        METHOD (str): Communication method.
        connection (bool): Connection indicator.
            If it is true, the connection has been established.
        terminator (str): Termination character.
    """
    METHOD = "Socket"

    def __init__(self, host, port, timeout=1.):
        self.host = host
        self.port = port
        self.timeout = timeout

    def open(self):
        """Open the connection to the device.

        Note:
            This method override the "open" in the base class.

        Return:
            None
        """
        if not self.connection:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.timeout)
            self.sock.connect((self.host, self.port))
            self.connection = True
        return

    def close(self):
        """Close the connection to the device.

        Note:
            This method override the "close" in the base class.

        Return:
            None
        """
        self.sock.close()
        del(self.sock)
        self.connection = False
        return

    def send(self, msg):
        """Send a message to the device.

        Note:
            This method override the "send" in the base class.

        Args:
            msg (str): A message to send the device.

        Return:
            None
        """
        self.sock.send((msg + self.terminator).encode())
        return

    def receive(self, byte=4096):
        """Receive the response of the device.

        Note:
            This method override the "receive" in the base class.

        Args:
            byte (int): Bytes to read. Defaults to 4096.

        Return:
            ret (str): The response of the device.
        """
        ret = self.sock.recv(byte).decode()
        return ret
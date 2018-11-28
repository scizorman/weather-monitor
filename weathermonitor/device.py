# coding: utf-8
__all__ = [
    "TLan08VmHandler",
]


from .core import BaseDeviceHandler
from .exception import TLan08VmError
from .utils import extract_bits


class TLan08VmHandler(BaseDeviceHandler):
    """Control "TLAN-08VM".

    "TLAN-08VM" is the A/D converter with 8 channels.

    Note:
        This class is based on "aerovane.core.BaseDeviceHandler".

    Args:
        com (aerovane.communicator):
            Communicator instance to control the device.

    Attributes:
        MANUFACTURER (str): Manufacturer of the device.
        PRODUCT_NAME (str): Name of the device.
        CLASSIFICATION (str): Classification of the device.
        NUM_CH (int): Number of channels
    """
    MANUFACTURER = "Turtle Industory CO., Ltd."
    PRODUCT_NAME = "TLAN-08VM"
    CLASSIFICATION = "A/D Converter"
    NUM_CH = 8

    def __init__(self, com):
        super().__init__(com)
        self.com.set_terminator("\r\n")
        self.recv_term_char = ">"

        ret = self.com.receive()
        if ret != self.recv_term_char:
            raise TLan08VmError(ret)

    def initialize(self, ch_bit, volt_range, ch_interval, meas_cycle, num_rpt):
        """Execute initial setup of the device.

        Args:
            None

        Return:
            Nonw
        """
        self.set_ch(ch_bit)
        for ch in extract_bits(ch_bit, self.NUM_CH):
            self.set_volt_range(ch, volt_range)
        self.set_ch_interval(ch_interval)
        self.set_meas_cycle(meas_cycle)
        self.set_rep_times(num_rpt)
        return

    def start(self):
        """Start the measurement.

        Return:
            None
        """
        self.com.send("conv begin")
        self._validate_sender()
        return

    def stop(self):
        """Stop the measurement.

        Return:
            None
        """
        self.com.send("conv end")
        self._validate_sender()
        return

    def read_buffer(self, ch):
        """Read the buffer of the specified channel.

        Args:
            ch (int): Channel to read.
                Allowed values are 0-7.

        Return:
            data (float or :obj:`float` of :obj:`list`):
                Buffer of the specified channel.
        """
        ret = self.com.query(f"conv read ch{ch}")
        if ret == f"Empty buffer{self.com.terminator}{self.recv_term_char}":
            data = None
        else:
            data = list(map(
                float,
                ret.strip(self.recv_term_char).split(self.com.terminator)[:-1]
            ))
            if len(data) == 1:
                data = data[0]
        return data

    def set_ch(self, ch_bit):
        """Set channels to measure.

        Args:
            ch_bit (int): Channels to measure.
                Allowed values are 0-255.

        Return:
            None
        """
        self.com.send(f"set ch {ch_bit}")
        self._validate_sender()
        return

    def set_volt_range(self, ch, volt):
        """Set the voltage range of the specified channel.

        Args:
            ch (str): Channel to set. Allowed values are 0-7.
            volt (int or float): Voltage range.
                Allowed values are 1, 2.5, 5 and 10.

        Return:
            None
        """
        self.com.send(f"set ra ch{ch} {str(volt)}v")
        self._validate_sender()
        return

    def set_meas_cycle(self, meas_cycle):
        """Set the measurement cycle.

        Args:
            meas_cycle (int): Measurement cycle (/100 ms).
                Allowed values are 2-65535.

        Return:
            None
        """
        self.com.send(f"set cyclelen {meas_cycle}")
        self._validate_sender()
        return

    def set_ch_interval(self, interval):
        """Set the interval between channels.

        Args:
            interval (int): Interval between channels (/100 ms).
                Allowed values are 2-511.

        Return:
            None
        """
        self.com.send(f"set interval {interval}")
        self._validate_sender()
        return

    def set_rep_times(self, num_rpt):
        """Set repeat times.

        Args:
            num_rpt (int): Repeat times.
                Allowed values are 0-65535.
        Return:
            None
        """
        self.com.send(f"set re {num_rpt}")
        self._validate_sender()
        return

    def get_status(self):
        """Get current status of the device.

        Return:
            ret (str): Current status
        """
        ret = self.com.query("get s").strip(
            self.com.terminator + self.recv_term_char
        )
        return ret

    def _validate_sender(self):
        valid_msg = f"OK{self.com.terminator}{self.recv_term_char}"
        ret = self.com.receive()
        if ret != valid_msg:
            raise TLan08VmError(ret)
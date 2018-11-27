# coding: utf-8
__all__ = [
    "extract_bits",
]


def extract_bits(bit, num_ch):
    """Extract bits of channels which are turend on (1).

    Args:
        bit (int): Bit to check.
        num_ch (int): Number of channels.

    Return:
        chs (:obj:`list` of :obj:`int`): Channels which are turned on (1).

    Example:
        >>> extract_bits(138, 8)
        [1, 3, 7]
    """
    chs = [i for i in range(num_ch) if bit & 2**i]
    return chs
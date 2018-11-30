# coding: utf-8
__all__ = [
    "or_of_bits",
    "extract_bits",
]


def or_of_bits(*bits):
    """OR the given bits.
    Args:
        *bits (int): Bits for OR. More than one argument required.
    Return:
        or_bit (int): OR of the given bits.
    Example:
        >>> or_of_bits(1, 2, 4)
        21 # 0b10101, 0x15
    """
    or_bit = 0
    for bit in bits:
        or_bit |= 2 ** bit

    return or_bit


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
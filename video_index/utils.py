# video_index/utils.py

def int_to_bytes_le(value: int, length: int) -> bytes:
    """
    Convert an integer to a little-endian bytes object of given length.
    
    Parameters
    ----------
    value : int
        The integer to convert.
    length : int
        The length of the resulting bytes object.
        
    Returns
    -------
    bytes
        The little-endian byte representation of the integer.
    """
    return value.to_bytes(length, byteorder='little', signed=False)


def bytes_to_int_le(data: bytes) -> int:
    """
    Convert a little-endian bytes object to an integer.
    
    Parameters
    ----------
    data : bytes
        The bytes to convert.
        
    Returns
    -------
    int
        The integer represented by the bytes.
    """
    return int.from_bytes(data, byteorder='little', signed=False)


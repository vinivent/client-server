import struct

header_format = 'I I B B H'
header_size = struct.calcsize(header_format)

def calculate_checksum(data):
    """
    Calcula o checksum de um dado fornecido.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("Os dados devem ser do tipo bytes ou bytearray.")
    checksum = 0
    for i, byte in enumerate(data):
        checksum += (byte * (i + 1)) % 256
    return checksum % 256

def pack_header(seq_num, ack_num, flags, checksum, payload_len):
    """
    Empacota os dados do cabeçalho em um formato binário.
    """
    return struct.pack(header_format, seq_num, ack_num, flags, checksum, payload_len)

def unpack_header(header_bytes):
    """
    Desempacota os dados do cabeçalho do formato binário.
    """
    if len(header_bytes) != header_size:
        raise ValueError("Tamanho do cabeçalho inválido.")
    return struct.unpack(header_format, header_bytes)

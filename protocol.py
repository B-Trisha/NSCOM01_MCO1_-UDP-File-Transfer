import struct

# B = 1 byte (Type), I = 4 bytes (Seq), I = 4 bytes (Length)
HEADER_FORMAT = "!BII"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)  # 7 bytes

# TFTP Error Codes
ERR_CODES = { 
    0: 'Not defined, see error message (if any).',
    1: 'File not found.',
    2: 'Access violation.',
    3: 'Disk full or allocation exceeded.',
    4: 'Illegal TFTP operation.',
    5: 'Unknown transfer ID.',
    6: 'File already exists.',
    7: 'No such user.',
}

# TFTP Operation Codes
OPCODES = {
    1: "RRQ", 
    2: "WRQ", 
    3: "DATA", 
    4: "ACK", 
    5: "ERROR"
}

# TFTP Default Values
DEFAULT_TFTP_BLK_SIZE = 512
DEFAULT_TFTP_TIMEOUT = 5
DEFAULT_TFTP_PORT = 69

# Message Types
SYN = 1
SYN_ACK = 2
DATA = 3
ACK = 4
FIN = 5
ERROR = 6

def encode_packet(msg_type, seq, payload=b""):
    length = len(payload)
    header = struct.pack(HEADER_FORMAT, msg_type, seq, length)
    return header + payload

def decode_packet(data):
    header = data[:HEADER_SIZE]
    payload = data[HEADER_SIZE:]

    msg_type, seq, length = struct.unpack(HEADER_FORMAT, header)

    if len(payload) != length:
        print("Warning: payload length mismatch!")

    return msg_type, seq, payload
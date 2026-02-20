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
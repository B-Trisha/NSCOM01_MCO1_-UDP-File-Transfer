import struct
import socket

# -----------------------------------------------------------------------
# HEADER FORMAT ---------------------------------------------------------
# -----------------------------------------------------------------------
# Packet Header: Type (1 byte) | Seq Num = (4 bytes) | Length (4 bytes)
# Total header size: 9 bytes
HEADER_FORMAT = "!BII"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

# -----------------------------------------------------------------------
# MESSAGE TYPES ---------------------------------------------------------
# -----------------------------------------------------------------------
SYN = 0         # Connection establishment request
SYN_ACK = 1     # Acknowledgement of SYN
ACK = 2         # General Acknowledgement
DATA = 3        # Data payload transfer
FIN = 4         # Connection termination request
ERROR = 5       # Error notification
REQUEST = 6     # File request (download/upload)

# -----------------------------------------------------------------------
# ERROR CODES (custom) --------------------------------------------------
# -----------------------------------------------------------------------
ERR_FILE_NOT_FOUND = 1
ERR_SESSION_MISMATCH = 2

ERROR_MESSAGES = {
    ERR_FILE_NOT_FOUND: "File not found",
    ERR_SESSION_MISMATCH: "Session mismatch"
}

# -----------------------------------------------------------------------
# OPERATION TYPES (for REQUEST packets) ---------------------------------
# -----------------------------------------------------------------------
OP_DOWNLOAD = b"GET"
OP_UPLOAD = b"PUT"

# -----------------------------------------------------------------------
# TRANSFER PARAMETERS ---------------------------------------------------
# -----------------------------------------------------------------------
CHUNK_SIZE = 1024   # Max payload size /packet
TIMEOUT = 2         # Seconds before timeout
MAX_RETRIES = 5     # Max retransmission attempts

# -----------------------------------------------------------------------
# PACKET ENCODING/DECODING ----------------------------------------------
# -----------------------------------------------------------------------
"""
Encodes packet with header and payload.

Arguments:
 - msg_type: Message type (SYN, ACK, DATA, etc.)
 - seq: Sequence Number
 - payload: Binary payload data
 
Returns:
 - Encoded packet as bytes
"""
def encode_packet(msg_type, seq, payload = b""):
    length = len(payload)
    header = struct.pack(HEADER_FORMAT, msg_type, seq, length)
    return header + payload

"""
Decodes packet from bytes to components.

Arguments:
 - data: Raw packet bytes
 
Returns:
 - Tuple (msg_type, seq, payload)
"""
def decode_packet(data):
    try:
        header = data[:HEADER_SIZE]
        payload = data[HEADER_SIZE:]

        msg_type, seq, length = struct.unpack(HEADER_FORMAT, header)

        if len(payload) != length:
            print(f"Warning: payload length mismatch (expected {length}, got {len(payload)})")

        return msg_type, seq, payload
    except struct.error as e:
        print(f"Error decoding packet: {e}")
        return None, 0, b""

# -----------------------------------------------------------------------
# ERROR HANDLING --------------------------------------------------------
# -----------------------------------------------------------------------
"""
Encodes an error packet.

Arguments:
 - error_code: Error code int
 - error_message: Error description string
 
Returns:
 - Encoded ERROR packet as bytes
"""
def encode_error(error_code, error_message):
    msg = f"{error_code}:{error_message}".encode()
    return encode_packet(ERROR, 0, msg)

"""
Decodes error payload.

Arguments:
 - payload: Error payload bytes
 
Returns:
 - Tuple (error_code, error_message)
"""
def decode_error(payload):
    try:
        decoded = payload.decode()
        parts = decoded.split(":", 1)

        if len(parts) == 2:
            return int(parts[0]), parts[1]

        return -1, decoded
    except:
        return -1, payload.decode(errors = 'replace')

# -----------------------------------------------------------------------
# REQUEST HANDLING ------------------------------------------------------
# -----------------------------------------------------------------------
"""
Encodes a file request packet.

Arguments:
 - filename: Name of file
 - operation: OP_DOWNLOAD / OP_UPLOAD
 
Returns:
 - Encoded REQUEST packet as bytes
"""
def encode_request(filename, operation):
    msg = f"{operation.decode()}:{filename}".encode()
    return encode_packet(REQUEST, 0, msg)

"""
Decodes request payload.

Arguments:
 - payload: Request payload bytes

Returns:
 - Tuple (operation, filename)
"""
def decode_request(payload):
    try:
        decoded = payload.decode()
        parts = decoded.split(":", 1)

        if len(parts) == 2:
            return parts[0], parts[1]

        return "", decoded
    except:
        return "", payload.decode(errors = 'replace')

# -----------------------------------------------------------------------
# STOP-AND-WAIT RELIABILITY ---------------------------------------------
# -----------------------------------------------------------------------
"""
Sends DATA packet and waits for ACK.
Retries on timeout up to max_retries

Arguments:
 - sock: UDP socket
 - data: Payload data to send
 - addr: Destination address
 - seq: Sequence number
 - max_retries: Maximum retry attempts
 
Returns:
 - True if Ack received, False if max retries exceeded
"""
def send_data_reliable(sock, data, addr, seq, max_retries = MAX_RETRIES):
    retries = 0

    while retries < max_retries:
        packet = encode_packet(DATA, seq, data)
        sock.sendto(packet, addr)

        try:
            ack_data, _ = sock.recvfrom(1024)
            msg_type, ack_seq, _ = decode_packet(ack_data)

            # ACK received
            if msg_type == ACK and ack_seq == seq:
                return True

        except socket.timeout:
            retries += 1
            print(f"Timeout waiting for ACK {seq}, retry {retries}/{max_retries}")

    # Max retries exceeded
    return False

"""
Receives Data packet and sends ACK.
Handles duplicate packets by resending ACK.

Arguments:
 - sock: UDP socket
 
Returns:
 - Tuple (seq, payload, addr) if DATA received, else (None, None, None) 
"""
def receive_data_and_ack(sock):
    data, addr = sock.recvfrom(CHUNK_SIZE + 9)
    msg_type, seq, payload = decode_packet(data)

    # Send ACK for this sequence number
    if msg_type == DATA:
        ack_packet = encode_packet(ACK, seq)
        sock.sendto(ack_packet, addr)

        return seq, payload, addr

    return None, None, None
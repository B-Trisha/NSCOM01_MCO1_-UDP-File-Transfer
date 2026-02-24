import socket
from protocol import (
    encode_packet,
    decode_packet,
    SYN,
    SYN_ACK,
    ACK,
    TIMEOUT,
    CHUNK_SIZE
)

# -----------------------------------------------------------------------
# DEFAULTS --------------------------------------------------------------
# -----------------------------------------------------------------------
DEFAULT_IP = "127.0.0.1"
DEFAULT_PORT = 5005

# -----------------------------------------------------------------------
# SERVER STATES ---------------------------------------------------------
# -----------------------------------------------------------------------
STATE_LISTEN = 0
STATE_SYN_RCVD = 1
STATE_ESTABLISHED = 2
STATE_FIN_WAIT = 3

def start_server(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))
    sock.settimeout(TIMEOUT)
    print(f"Server listening on {ip}:{port}...")
    return sock

def handle_packet(sock, data, addr, server_state):
    msg_type, seq, payload = decode_packet(data)

    if server_state == STATE_LISTEN:
        if msg_type == SYN:
            print(f"Received SYN from {addr}")
            # Send SYN-ACK
            response = encode_packet(SYN_ACK, seq)
            sock.sendto(response, addr)

            return STATE_SYN_RCVD

    elif server_state == STATE_SYN_RCVD:
        if msg_type == ACK:
            print(f"Handshake complete with {addr}")

            return STATE_ESTABLISHED

    # If in ESTABLISHED, handle later when implementing file transfer

    return server_state

def main():
    sock = start_server(DEFAULT_IP, DEFAULT_PORT)
    server_state = STATE_LISTEN

    while True:
        try:
            # Buffer size = chunk + header
            data, addr = sock.recvfrom(CHUNK_SIZE + 9)
            server_state = handle_packet(sock, data, addr, server_state)
        except socket.timeout:
            continue

if __name__ == "__main__":
    main()
import socket
from protocol import encode_packet, decode_packet, SYN, SYN_ACK, ACK

# Defaults
DEFAULT_IP = "127.0.0.1"
DEFAULT_PORT = 5005

def start_server(DEFAULT_IP, DEFAULT_PORT):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((DEFAULT_IP, DEFAULT_PORT))
    sock.settimeout(5)
    print(f"Server listening on {DEFAULT_IP}:{DEFAULT_PORT}...")
    return sock

def handle_packet(sock, data, addr):
    msg_type, seq, payload = decode_packet(data)

    if msg_type == SYN:
        print("Received SYN from", addr)
        # Send SYN-ACK
        response = encode_packet(SYN_ACK, seq)
        sock.sendto(response, addr)

    elif msg_type == ACK:
        print("Handshake complete with", addr)

def main():
    sock = start_server(DEFAULT_IP, DEFAULT_PORT)
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            handle_packet(sock, data, addr)
        except socket.timeout:
            continue

if __name__ == "__main__":
    main()
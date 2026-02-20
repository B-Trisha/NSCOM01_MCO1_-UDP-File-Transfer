import socket

# Defaults
DEFAULT_IP = "127.0.0.1"
DEFAULT_PORT = 5005

def start_client(DEFAULT_IP, DEFAULT_PORT):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.settimeout(5)
    return sock

def handshake():
    seq = 0 # starting sequence number

def main():
    sock = start_client(DEFAULT_IP, DEFAULT_PORT)
    server_addr = (DEFAULT_IP, DEFAULT_PORT)
    handshake(sock, server_addr)
    sock.close()


if __name__ == "__main__":
    main()
import socket

# Defaults
DEFAULT_IP = "127.0.0.1"
DEFAULT_PORT = 5005

def start_server(DEFAULT_IP, DEFAULT_PORT):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((DEFAULT_IP, DEFAULT_PORT))
    sock.settimeout(5)
    print(f"Server listening on {DEFAULT_IP}:{DEFAULT_PORT}...")
    return sock



def main():
    sock = start_server(DEFAULT_IP, DEFAULT_PORT)



if __name__ == "__main__":
    main()
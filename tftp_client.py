import socket
from protocol import (
    encode_packet,
    decode_packet,
    SYN,
    SYN_ACK,
    ACK,
    TIMEOUT,
    MAX_RETRIES
)

# -----------------------------------------------------------------------
# DEFAULTS --------------------------------------------------------------
# -----------------------------------------------------------------------
DEFAULT_IP = "127.0.0.1"
DEFAULT_PORT = 5005

# -----------------------------------------------------------------------
# CLIENT STATES ---------------------------------------------------------
# -----------------------------------------------------------------------
STATE_CLOSED = 0
STATE_SYN_SENT = 1
STATE_ESTABLISHED = 2
STATE_FIN_WAIT = 3

def start_client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT)
    return sock

def handshake(sock, server_addr):
    client_state = STATE_CLOSED
    seq = 0
    retries = 0

    print("Sending SYN...")

    while retries < MAX_RETRIES:
        sock.sendto(encode_packet(SYN, seq), server_addr)
        client_state = STATE_SYN_SENT

        try:
            data, addr = sock.recvfrom(1024)
            msg_type, recv_seq, payload = decode_packet(data)

            if msg_type == SYN_ACK:
                print(f"Received SYN-ACK from {addr}")
                # Send final ACK
                sock.sendto(encode_packet(ACK, recv_seq), server_addr)
                print("Handshake complete!")
                return True, STATE_ESTABLISHED
            else:
                print("Unexpected packet, retrying...")

        except socket.timeout:
            print(f"Timeout, retrying ({retries + 1}/{MAX_RETRIES})...")
            retries += 1

    print("Handshake failed: Max retries reached")
    return False, STATE_CLOSED

def menu():
    sock = start_client()
    server_addr = (DEFAULT_IP, DEFAULT_PORT)
    client_state = STATE_CLOSED
    connected = False

    while True:
        print("\n=== Reliable UDP Client ===")
        print("1. Connect to Server")
        print("2. Download File")
        print("3. Upload File")
        print("4. Exit")

        choice = input("Select option: ")

        if choice == "1":
            connected, client_state = handshake(sock, server_addr)

        elif choice == "2":
            if connected:
                filename = input("Enter filename to download: ")
                print(f"Download requested: {filename}")
            else:
                print("You must connect first!")

        elif choice == "3":
            if connected:
                filename = input("Enter filename to upload: ")
                print(f"Upload requested: {filename}")
            else:
                print("You must connect first!")

        elif choice == "4":
            print("Exiting...")
            break

        else:
            print("Invalid option.")

if __name__ == "__main__":
    menu()
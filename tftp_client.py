import socket
from protocol import (
    encode_packet,
    decode_packet,
    encode_request,
    decode_error,
    SYN,
    SYN_ACK,
    ACK,
    DATA,
    REQUEST,
    ERROR,
    TIMEOUT,
    MAX_RETRIES,
    CHUNK_SIZE,
    OP_DOWNLOAD,
    OP_UPLOAD,
    receive_data_and_ack
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

"""
Creates and configures UDP client socket.

Returns:
 - UDP socket
"""
def start_client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT)
    return sock

"""
Performs 3-way handshake with server.

Arguments:
 - sock: UDP socket
 - server_addr: Server address tuple
 
Returns:
 - Tuple (success, state)
"""
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

"""
Downloads file from server using Stop-and-Wait reliability.

Arguments:
 - sock: UDP socket
 - server_addr: Server address tuple
 - filename: Name of file to download
"""
def download_file(sock, server_addr, filename):
    # Send REQUEST packet
    print(f"Requesting download: {filename}")
    request = encode_request(filename, OP_DOWNLOAD)
    sock.sendto(request, server_addr)

    # Receive file data
    received_data = {}
    expected_seq = 0

    print("Receiving file...")

    while True:
        seq, payload, addr = receive_data_and_ack(sock)

        # Not a DATA packet
        if seq is None:
            continue

        # End of file
        if len(payload) == 0:
            print("EOF received")
            break

        print(f"Received chunk seq = {seq}, len = {len(payload)}")
        received_data[seq] = payload

        # Write sequential data to file
        while expected_seq in received_data:
            with open(filename, "ab") as f:
                f.write(received_data[expected_seq])
            del received_data[expected_seq]
            expected_seq += 1

    print(f"Download complete: {filename}")

"""
Client menu loop.
"""
def menu():
    sock = start_client()
    server_addr = (DEFAULT_IP, DEFAULT_PORT)
    client_state = STATE_CLOSED
    connected = False

    try:
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
                    download_file(sock, server_addr, filename)
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
    finally:
        sock.close()
        print("Socket closed.")

if __name__ == "__main__":
    menu()
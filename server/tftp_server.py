import socket
import sys, os

# Add root folder to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from protocol import (
    encode_packet,
    decode_packet,
    encode_error,
    decode_request,
    SYN,
    SYN_ACK,
    ACK,
    FIN,
    FIN_ACK,
    REQUEST,
    TIMEOUT,
    CHUNK_SIZE,
    ERR_FILE_NOT_FOUND,
    send_data_reliable,
    receive_data_and_ack
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

"""
Starts the UDP server socket.

Arguments:
 - ip: IP address to bind to
 - port: Port number to bind to

Returns:
 - UDP socket
"""
def start_server(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))
    sock.settimeout(TIMEOUT)
    print(f"Server listening on {ip}:{port}...")
    return sock

"""
Sends file using Stop-and-Wait reliability.

Arguments:
 - sock: UDP socket
 - addr: Client address
 - filepath: Path to file to send
"""
def send_file(sock, addr, filepath):
    try:
        with open(filepath, "rb") as f:
            seq = 0

            while True:
                chunk = f.read(CHUNK_SIZE)

                # Send empty chunk as EOF signal
                if len(chunk) == 0:
                    print("Sending EOF...")
                    send_data_reliable(sock, b"", addr, seq)
                    break

                # Send chunk reliably
                success = send_data_reliable(sock, chunk, addr, seq)

                if not success:
                    print("Failed to send chunk, giving up")
                    return

                print(f"Sent chunk seq = {seq}, len = {len(chunk)}")
                seq += 1
        print(f"File sent complete: {filepath}")

    except FileNotFoundError:
        print(f"File not found: {filepath}")
        error = encode_error(ERR_FILE_NOT_FOUND, "File not found")
        sock.sendto(error, addr)
        return


"""
Receives a file from client using Stop-and-Wait reliability.

Arguments:
    - sock: UDP socket
    - addr: Client address
    - filename: Path to save the uploaded file
"""
def receive_file(sock, _, filename):
    try:
        expected_seq = 0  

        print(f"Ready to receive file: {filename}")

        # Open the file once in write mode to avoid duplication
        with open(filename, "wb") as f:
            while True:
                # Receive a chunk reliably
                seq, payload, _ = receive_data_and_ack(sock)

                # Not a DATA packet
                if seq is None:
                    continue

                # End of file
                if len(payload) == 0:
                    print("EOF received. File upload complete.")
                    break

                # Write the chunk sequentially
                f.write(payload)
                print(f"Received chunk seq = {seq}, len = {len(payload)}")
                expected_seq += 1

        print(f"File uploaded: {filename}")

    except Exception as e:
        print(f"Error receiving file: {e}")

"""
Handles incoming packets based on server state.

Arguments:
 - sock: UDP Socket
 - data: Packet data
 - addr: Client address
 server_state: Current server state

Returns:
 - Updated server state
"""
def handle_packet(sock, data, addr, server_state):
    msg_type, seq, payload = decode_packet(data)

    if server_state == STATE_LISTEN:
        if msg_type == SYN:
            print(f"Received SYN from {addr}")
            # Send SYN-ACK
            response = encode_packet(SYN_ACK, seq)
            sock.sendto(response, addr)

            print(f"Sent SYN-ACK to {addr}")

            return STATE_SYN_RCVD

    elif server_state == STATE_SYN_RCVD:
        if msg_type == ACK:
            print(f"Handshake complete with {addr}")

            return STATE_ESTABLISHED

    # If ESTABLISHED, handle file transfer
    elif server_state == STATE_ESTABLISHED:
        if msg_type == REQUEST:
            operation, filename = decode_request(payload)

            if operation == "GET":
                print(f"\nDownload request for: {filename}")
                send_file(sock, addr, filename)
            elif operation == "PUT":
                print(f"\nUpload request for: {filename}")
                receive_file(sock, addr, filename)
            
            return server_state
        if msg_type == FIN:
            print(f"Received FIN from {addr}, sending FIN-ACK...")
            fin_response = encode_packet(FIN_ACK, seq)
            sock.sendto(fin_response, addr)
            print("Server connection closed. Back to LISTEN.")
            return STATE_LISTEN

    return server_state


"""
Main server loop.
"""
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
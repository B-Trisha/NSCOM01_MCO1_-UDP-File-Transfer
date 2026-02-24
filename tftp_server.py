import socket
from protocol import (
    encode_packet,
    decode_packet,
    encode_error,
    encode_request,
    decode_request,
    SYN,
    SYN_ACK,
    ACK,
    DATA,
    REQUEST,
    ERROR,
    TIMEOUT,
    CHUNK_SIZE,
    MAX_RETRIES,
    ERR_FILE_NOT_FOUND,
    OP_DOWNLOAD,
    send_data_reliable
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
                    print("Failed to send chunk, closing connection")
                    return

                print(f"Sent chunk seq = {seq}, len = {len(chunk)}")
                seq += 1
        print(f"File sent complete: {filepath}")

    except FileNotFoundError:
        error = encode_error(ERR_FILE_NOT_FOUND, "File not found")
        sock.sendto(error, addr)
        return



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
                print(f"Download request for: {filename}")
            elif operation == "PUT":
                print(f"Upload request for: {filename}")
                # TODO: Implement Upload

        elif msg_type == DATA:
            print("change this later")
            # TODO: Handle incoming data for upload

        return server_state

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
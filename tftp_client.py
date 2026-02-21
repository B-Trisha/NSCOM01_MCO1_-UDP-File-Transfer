import socket
from protocol import encode_packet, decode_packet, SYN, SYN_ACK, ACK

# Defaults
DEFAULT_IP = "127.0.0.1"
DEFAULT_PORT = 5005

def start_client(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)
    return sock

def handshake(sock, server_addr):
    seq = 0
    print("Sending SYN...")
    sock.sendto(encode_packet(SYN, seq), server_addr)

    try:
        data, addr = sock.recvfrom(1024)
        msg_type, seq, payload = decode_packet(data)

        if msg_type == SYN_ACK:
            print("Received SYN-ACK")
            # Send ACK back
            sock.sendto(encode_packet(ACK, seq), server_addr)
            print("Handshake complete!")
            return True  
        else:
            print("Unexpected response")
            return False

    except socket.timeout:
        print("Handshake failed (timeout)")
        return False

def menu(sock, server_addr):
    connected = False

    while True:
        print("\n=== Reliable UDP Client ===")
        print("1. Connect to Server")
        print("2. Download File")
        print("3. Upload File")
        print("4. Exit")

        choice = input("Select option: ")

        if choice == "1":
            connected = handshake(sock, server_addr)

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

def main():
    sock = start_client(DEFAULT_IP, DEFAULT_PORT)
    server_addr = (DEFAULT_IP, DEFAULT_PORT)
    menu(sock, server_addr)
    sock.close()

if __name__ == "__main__":
    main()
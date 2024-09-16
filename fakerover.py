import socket

# Rover details (mock values)
ROVER_PORT = 12345

def start_mock_server():
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', ROVER_PORT))
    
    print(f"Mock server listening on port {ROVER_PORT}...")

    while True:
        # Receive message from client
        message, addr = sock.recvfrom(1024)
        print(f"Received packet from {addr}: {message.decode('utf-8')}")

if __name__ == "__main__":
    start_mock_server()

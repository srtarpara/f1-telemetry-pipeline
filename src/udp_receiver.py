import socket

# The IP address and Port to listen on
UDP_IP = '0.0.0.0'
UDP_PORT = 20777
BUFFER_SIZE = 4096      #Max number of bytes to receive at once

# Creates a UDP socket
# socket.AF_INET specifies IPv4; socket.SOCK_DGRAM specifies UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the IP address and port
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening for UDP packets on {UDP_IP}:{UDP_PORT}...")

try:
    while True:
        # Receive data from the socket
        # recvfrom() blocks until data arrives. It returns a tuple: (bytes_data, sender_address)
        data, addr = sock.recvfrom(BUFFER_SIZE)
    
        print(f"Received packet from {addr} with size {len(data)} bytes")

except KeyboardInterrupt:
    print("\nStopping UDP receiver...")
finally:
    # Clean up and close the socket
    sock.close()


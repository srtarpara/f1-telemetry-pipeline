import socket
import struct


# Dictionary that contains the packet id to its corresponding name
packet_name = {
    0: "Motion",
    1: "Session",
    2: "Lap Data",
    3: "Event",
    4: "Participants",
    5: "Car Setups",
    6: "Car Telemetry",
    7: "Car Status",
    8: "Final Classification",
    9: "Lobby Info",
    10: "Car Damage",
    11: "Session History",
    12: "Tyre Sets",
    13: "Motion Ex",
    14: "Time Trial",
    15: "Lap Positions",
    16: "Car Telemetry 2"
}


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

        # Decodes the data to pull the packet id from the header.
        packet_id = struct.unpack_from("<B", data, 6)[0]

        # Packet ID 6 contains Car Telemetry data for all 24 cars.
        if packet_id == 6:
            # Read the player's car index from byte offset 27 in the packet header.
            # # "<B" reads 1 byte as an unsigned integer (uint8).
            player_car_index = struct.unpack_from("<B", data, 27)[0]

            # Calculate where our car's telemetry data starts in the packet.
            # 29 = Size of the packet header in bytes.
            # 59 = Size of one car's telemetry record in bytes.
            # Multiplying the player index by 59 skips the records of the cars before ours.
            speed_offset = 29 + (player_car_index * 59)

            # Speed is the first field in each car's telemetry record.
            # "<H" reads 2 bytes as a little-endian unsigned integer (uint16).
            # The speed value is measured in km/h.
            speed = struct.unpack_from("<H", data, speed_offset)[0]

            print(f"Speed: {speed} km/h")
            print(f"Player Car Index: {player_car_index}")
            print(f"Received {packet_name[packet_id]} packet from {addr} with size {len(data)} bytes")

except KeyboardInterrupt:
    print("\nStopping UDP receiver...")
finally:
    # Clean up and close the socket
    sock.close()


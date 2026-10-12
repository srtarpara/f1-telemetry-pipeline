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
        # Wait for an incoming UDP packet.
        # recvfrom() returns the raw packet bytes and the sender's address.
        data, addr = sock.recvfrom(BUFFER_SIZE)

        # Read the packet ID from byte offset 6 in the packet header.
        # "<B" reads 1 byte as an unsigned integer (uint8).
        packet_id = struct.unpack_from("<B", data, 6)[0]

        # Packet ID 6 contains Car Telemetry data for all 24 cars.
        if packet_id == 6:

            # Read the player's car index from byte offset 27 in the header.
            # This tells us which of the 24 car records belongs to the player.
            player_car_index = struct.unpack_from("<B", data, 27)[0]

            # Calculate the starting position of the player's telemetry record.
            # 29 = Size of the packet header in bytes.
            # 59 = Size of each car's telemetry record in bytes.
            # Multiplying the car index by 59 skips all preceding car records.
            speed_offset = 29 + (player_car_index * 59)

            # SPEED
            # Speed is the first field in each car's telemetry record.
            # "<H" reads 2 bytes as a little-endian unsigned integer (uint16).
            # The value represents the car's speed in km/h.
            speed = struct.unpack_from("<H", data, speed_offset)[0]

            # THROTTLE
            # Throttle comes immediately after speed, which occupies 2 bytes.
            # "<f" reads 4 bytes as a little-endian floating-point number.
            # Values range from 0.0 (no throttle) to 1.0 (full throttle).
            throttle_offset = speed_offset + 2
            throttle = struct.unpack_from("<f", data, throttle_offset)[0]

            # STEERING
            # Steering comes after throttle, which occupies 4 bytes.
            # "<f" reads another 4-byte floating-point number.
            # Values range from -1.0 to 1.0, indicating steering direction
            # and the amount of steering input.
            steering_offset = throttle_offset + 4
            steering = struct.unpack_from("<f", data, steering_offset)[0]

            # BRAKING
            # Brake input comes after steering, which occupies 4 bytes.
            # Values range from 0.0 (no braking) to 1.0 (full braking).
            braking_offset = steering_offset + 4
            braking = struct.unpack_from("<f", data, braking_offset)[0]

            # GEAR
            # Brake occupies 4 bytes, followed by a 1-byte clutch field.
            # We skip both fields to reach the gear value.
            # "<b" reads 1 byte as a signed integer (int8).
            # The gear can be negative because -1 represents reverse.
            gear_offset = braking_offset + 4 + 1
            gear = struct.unpack_from("<b", data, gear_offset)[0]

            # ENGINE RPM
            # Engine RPM comes immediately after gear, which occupies 1 byte.
            # "<H" reads 2 bytes as an unsigned integer (uint16).
            # The value represents the engine's revolutions per minute.
            enginerpm_offset = gear_offset + 1
            enginerpm = struct.unpack_from("<H", data, enginerpm_offset)[0]

            # Display the decoded telemetry values for the player's car.
            print(f"Speed: {speed} km/h")
            print(f"Player Car Index: {player_car_index}")
            print(f"Player Throttle Input: {throttle}")
            print(f"Player Steering Input: {steering}")
            print(f"Player Braking Input: {braking}")
            print(f"Player Gear: {gear}")
            print(f"Player Engine RPM: {enginerpm}")

            # Display the packet type and total number of bytes received.
            print(f"Received {packet_name[packet_id]} packet with size {len(data)} bytes")

        elif packet_id == 2:

            # Read the player's car index from byte offset 27 in the header.
            # This tells us which of the 24 car records belongs to the player.
            player_car_index = struct.unpack_from("<B", data, 27)[0]

            lapDistance_offset = 29 + (57 * player_car_index) + 19
            lapDistance = struct.unpack_from("<f", data, lapDistance_offset)[0]

            currentLapNum_offset = 29 + (57 * player_car_index) + 32
            currentLapNum = struct.unpack_from("<B", data, currentLapNum_offset)

            print(f"Lap Distance: {lapDistance}")
            print(f"Current Lap: {currentLapNum}")


            # Display the packet type and total number of bytes received.
            print(f"Received {packet_name[packet_id]} packet with size {len(data)} bytes")

except KeyboardInterrupt:
    print("\nStopping UDP receiver...")
finally:
    # Clean up and close the socket
    sock.close()


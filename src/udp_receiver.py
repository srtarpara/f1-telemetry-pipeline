import socket
import struct
import psycopg


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

# Connect to the PostgreSQL database.
conn = psycopg.connect(
    dbname="f1_telemetry",
    user="postgres",
    host="localhost"
)

try:
    while True:

        # Wait for an incoming UDP packet.
        # recvfrom() returns the raw bytes and the sender's address.
        data, addr = sock.recvfrom(BUFFER_SIZE)

        # Every F1 packet begins with a 29-byte header.
        # Read the packet ID at byte offset 6.
        # "<B" = little-endian unsigned 8-bit integer (1 byte).
        packet_id = struct.unpack_from("<B", data, 6)[0]

        # SESSION INFORMATION (COMMON HEADER)

        # Decode the unique session identifier from byte offset 7.
        # "<Q" = little-endian unsigned 64-bit integer (8 bytes).
        # This helps associate telemetry readings with a racing session.
        m_session_uid = struct.unpack_from("<Q", data, 7)[0]

        # Decode the elapsed session time from byte offset 15.
        # "<f" = little-endian 32-bit float (4 bytes).
        # The value represents elapsed session time in seconds.
        m_session_time = struct.unpack_from("<f", data, 15)[0]

        # PACKET ID 1 — SESSION DATA
        if packet_id == 1:

            # Skip the 29-byte header, then move 7 bytes into
            # the Session packet body to locate the track ID.
            trackid_offset = 29 + 7

            # "<b" = signed 8-bit integer (1 byte).
            # A negative value can represent an unavailable track ID.
            m_trackid = struct.unpack_from("<b", data, trackid_offset)[0]

            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO sessions (session_uid, track_id)
                    VALUES (%s, %s)
                    ON CONFLICT (session_uid) DO NOTHING;
                    """,
                    (m_session_uid, m_trackid)
                )

            conn.commit()

            print(f"Session Time: {m_session_time:.3f} seconds")

            # Display the packet type and total number of bytes.
            print(
                f"Received {packet_name[packet_id]} "
                f"packet with size {len(data)} bytes"
            )

        # PACKET ID 6 — CAR TELEMETRY
        elif packet_id == 6:

            # Read the player's car index from byte offset 27
            # in the common packet header.
            # This identifies which of the 24 car records is ours.
            player_car_index = struct.unpack_from("<B", data, 27)[0]

            # Calculate the start of the player's telemetry record.
            # 29 = packet header size in bytes.
            # 59 = size of one CarTelemetryData record in bytes.
            # Multiplying by the car index skips preceding records.
            telemetry_record_offset = 29 + (player_car_index * 59)

            # SPEED
            # Speed starts at offset 0 within the car record.
            # "<H" = unsigned 16-bit integer (2 bytes).
            # The value is measured in km/h.
            speed_offset = telemetry_record_offset
            speed = struct.unpack_from("<H", data, speed_offset)[0]

            # THROTTLE
            # Throttle starts immediately after the 2-byte speed field.
            # "<f" = 32-bit float (4 bytes).
            # Values range from 0.0 (none) to 1.0 (full throttle).
            throttle_offset = speed_offset + 2
            throttle = struct.unpack_from("<f", data, throttle_offset)[0]

            # STEERING
            # Steering follows the 4-byte throttle field.
            # Values range from -1.0 to 1.0.
            steering_offset = throttle_offset + 4
            steering = struct.unpack_from("<f", data, steering_offset)[0]

            # BRAKING
            # Brake input follows the 4-byte steering field.
            # Values range from 0.0 (none) to 1.0 (full braking).
            braking_offset = steering_offset + 4
            braking = struct.unpack_from("<f", data, braking_offset)[0]

            # GEAR
            # Skip the 4-byte brake field and 1-byte clutch field.
            # "<b" = signed 8-bit integer (1 byte).
            # -1 represents reverse gear.
            gear_offset = braking_offset + 4 + 1
            gear = struct.unpack_from("<b", data, gear_offset)[0]

            # ENGINE RPM
            # Engine RPM follows the 1-byte gear field.
            # "<H" = unsigned 16-bit integer (2 bytes).
            enginerpm_offset = gear_offset + 1
            enginerpm = struct.unpack_from("<H", data, enginerpm_offset)[0]

            # Display session information and decoded car telemetry.
            print(f"Session ID: {m_session_uid}")
            print(f"Session Time: {m_session_time:.3f} seconds")
            print(f"Speed: {speed} km/h")
            print(f"Player Car Index: {player_car_index}")
            print(f"Player Throttle Input: {throttle:.3f}")
            print(f"Player Steering Input: {steering:.3f}")
            print(f"Player Braking Input: {braking:.3f}")
            print(f"Player Gear: {gear}")
            print(f"Player Engine RPM: {enginerpm}")

            # Display the packet type and total packet size.
            print(
                f"Received {packet_name[packet_id]} "
                f"packet with size {len(data)} bytes"
            )

        # PACKET ID 2 — LAP DATA
        elif packet_id == 2:

            # Identify the player's car using the index
            # stored at byte offset 27 in the packet header.
            player_car_index = struct.unpack_from("<B", data, 27)[0]

            # Calculate the beginning of the player's LapData record.
            # 29 = packet header size in bytes.
            # 57 = size of each LapData record in bytes.
            lap_record_offset = 29 + (57 * player_car_index)

            # LAP DISTANCE
            # Move 20 bytes into the player's LapData record.
            # "<f" = 32-bit float (4 bytes).
            # The distance is measured in meters.
            lapDistance_offset = lap_record_offset + 20
            lapDistance = struct.unpack_from(
                "<f", data, lapDistance_offset
            )[0]

            # CURRENT LAP NUMBER
            # Move 33 bytes into the player's LapData record.
            # "<B" = unsigned 8-bit integer (1 byte).
            currentLapNum_offset = lap_record_offset + 33
            currentLapNum = struct.unpack_from(
                "<B", data, currentLapNum_offset
            )[0]

            # LAST LAP TIME
            # Starts at offset 0 within the player's LapData record.
            # "<I" = unsigned 32-bit integer (4 bytes).
            # The value is measured in milliseconds.
            lastLapTime_offset = lap_record_offset
            m_lastLapTimeInMS = struct.unpack_from(
                "<I", data, lastLapTime_offset
            )[0]

            # CURRENT LAP TIME
            # Starts 4 bytes after the beginning of the record.
            # "<I" = unsigned 32-bit integer (4 bytes).
            # The value is measured in milliseconds.
            currentLapTime_offset = lap_record_offset + 4
            m_currentLapTimeInMS = struct.unpack_from(
                "<I", data, currentLapTime_offset
            )[0]

            # CURRENT LAP INVALID
            # Move 37 bytes into the player's LapData record.
            # "<B" = unsigned 8-bit integer (1 byte).
            # 0 = valid lap; 1 = invalid lap.
            currentLapInvalid_offset = lap_record_offset + 37
            m_currentLapInvalid = struct.unpack_from(
                "<B", data, currentLapInvalid_offset
            )[0]

            if currentLapNum > 1 and m_lastLapTimeInMS > 0:

                # The last lap time belongs to the previous lap.
                completed_lap_number = currentLapNum - 1

                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO laps (
                            session_uid,
                            lap_number,
                            last_lap_time_ms,
                            lap_valid
                        )
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (session_uid, lap_number) DO NOTHING;
                        """,
                        (m_session_uid, completed_lap_number, m_lastLapTimeInMS, None)
                    )
                conn.commit()
            
        
            # Display the packet type and total packet size.
            print(
                f"Received {packet_name[packet_id]} "
                f"packet with size {len(data)} bytes"
            )


except KeyboardInterrupt:
    print("\nStopping UDP receiver...")
finally:
    conn.close()
    # Clean up and close the socket
    sock.close()


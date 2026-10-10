# F1 Telemetry Pipeline — Engineering Journal

## Project Overview

**Project:** F1 Telemetry Data Pipeline  
**Goal:** Build a real-time data pipeline that captures telemetry from F1 26 on PC, processes the data using Python, and stores it in PostgreSQL for analysis.

**Core Technologies:** Python, PostgreSQL, UDP, Git, GitHub

---

# Entry 001 — Project Setup

**Date:** 2026-10-10 
**Milestone:** Project Setup
**Status:** Completed
**Objective:** Initial Setup of Project Files
**Description:** Just initial file setup and some search on telemetry and UDP.

# Entry 002 — Receiving Live UDP Telemetry

**Date:** 2026-10-10 
**Milestone:** Receiving UDP Telemetry
**Status:** Completed
**Objective:** Receive UDP Telemetry from F126 game
**Description:** Created a socket programming script in Python to receive data from the F126 game. Had some issues regarding packet size. I initally set it to 1024 bytes as the buffer but that was clearly too small, so I increased it to 4096 bytes. Next steps will be to decode the data coming in.

# Entry 003 — Identifying Incoming UDP Telemetry Packets

**Date:** 2026-10-10  
**Milestone:** Identifying UDP Telemetry Packets  
**Status:** Completed  
**Objective:** Identify the different types of UDP telemetry packets received from the F1 26 game.  
**Description:** Updated the Python UDP receiver to read the packet header and identify incoming telemetry packets using their packet IDs. Used the F1 telemetry documentation to determine the byte offset of the packet ID and Python's `struct.unpack_from()` to decode it from the raw binary data. Learned about byte offsets, data types, and little-endian byte ordering. Next steps will be to filter for Car Telemetry packets and extract actual values such as car speed.

# Entry 004 — Decoding Car Telemetry Data

**Date:** 2026-10-10  
**Milestone:** Extracting Car Telemetry Data  
**Status:** Completed  
**Objective:** Decode raw Car Telemetry packets to extract the player's car speed.  
**Description:** Updated the Python UDP receiver to filter for Car Telemetry packets (ID 6) and extract the player's car index from the packet header. Used the F1 telemetry documentation to calculate the byte offset of the player's telemetry record, accounting for the 29-byte header and 59-byte records for each car. Used `struct.unpack_from()` to decode the speed value as a `uint16` and successfully verified that the extracted speed matched the in-game dashboard. Next steps will be to identify which telemetry data points to collect and plan how to structure the data for storage in PostgreSQL.

# Entry 005 — Decoding Core Car Telemetry Fields

**Date:** 2026-10-10  
**Milestone:** Decoding Core Car Telemetry Fields  
**Status:** Completed  
**Objective:** Extract the core driving telemetry values from the F1 26 Car Telemetry packets.

**Description:** Expanded the Python UDP receiver to decode additional data from Car Telemetry packets (ID 6), including throttle, steering, brake, gear, and engine RPM alongside speed. Used the F1 telemetry documentation to identify each field's data type, size, and byte offset within the player's car telemetry record. Used Python's `struct.unpack_from()` with the appropriate format characters to decode floating-point values and signed and unsigned integers. Successfully tested the decoded values in-game and verified that they responded correctly to driving inputs. Next steps will be to decode Lap Data packets (ID 2) to extract lap numbers, lap distances, and timing information for post-session lap analysis.
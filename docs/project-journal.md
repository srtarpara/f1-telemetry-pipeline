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


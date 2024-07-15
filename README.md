# CCSDS Imagery Transmission Project
Simulation of data transfer between a satellite (raspberry pi) and a ground station (PC) over Wi-Fi LAN using CCSDS over UDP.
Also works locally by binding to localhost.

# Overview

The project is built to simulate a file transmission over UDP using the CCSDS Space Packet protocol. In the simulation, the satellite gathers an image (or any other file, default is `satellite_imagery.jpeg`).
It then figures out how many chunks the image has to be split up into to fit into the UDP and CCSDS specs, and sends out the packets one-by-one, utilizing the CCSDS sequence count field in the primary header.
On the other side, the ground is constantly listening to the bound socket. It identifies a chunked transmission by looking for sync UDP packets, which are simply encoded "txstart" and "txend" strings. It then uses
the same CCSDS protocol class to parse the received header data and write into a file with default name of `received_imagery.jpeg`.

The Ground station writes a report into the transmission_report.txt file, which includes all timestamps of the received chunks.

# Prerequisites
1. Ensure that python3 is installed.
2. `pip install -r requirements.txt` - very few requirements, use venv if desired.

# How To Run Locally
1. Start the ground station - this will bind to port 8080 on localhost. 

`python ground_station.py`, or `python ground_station.py --out received_filename` to specify custom received filename to write into.
2. Run the satellite image transmission. 

`python satellite.py` or `python satellite.py --transmit transmit_filename` to specify custom source image.

# How To Run On Pi
1. `python ground_station.py --ip pi_ip --port port`
2. `python satellite.py --ip ground_ip --port port`

# How This Can Be Improved
1. Class hierarchy for the ccsds.py protocol is a bit over-complicated. Should use composition instead of inheritance
2. Re-request missing packets if they were detected (akin to TCP)
3. Use cyclic redundancy checks on the received packets and the entire image after reception.
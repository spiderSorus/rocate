# OT-ZMZYQ-799 (CF-RU5106) RFID Antenna Capabilities

This document outlines the proven capabilities, data structures, and limitations of the OT-ZMZYQ-799 long-range UHF RFID reader, specifically based on tests conducted over its USB serial interface.

## Hardware & Protocol Identification
*   **Hardware Model:** OT-ZMZYQ-799 (OEM version of the Chafon CF-RU5106)
*   **Internal Firmware:** `UHFReader18`
*   **Communication Interface Tested:** USB (Internal RS232 to USB converter)
*   **Baud Rate:** 57600 baud (Default)
*   **Protocol:** Proprietary Chafon Hexadecimal Protocol (Command/Answer mode)

## Data Output Capabilities

Based on raw mathematical analysis of the USB serial packets, here is exactly what data the antenna can and cannot provide:

### 1. Tag EPC (Electronic Product Code) - [SUPPORTED]
When the antenna successfully queries a tag in its field of view, it returns a 20-byte packet. 
*   The reader successfully decodes and outputs the **12-byte (96-bit) EPC hex string** of the tag (e.g., `E280699500005012D7B47DE8`).
*   The reader can successfully query the tag continuously (polling), providing real-time "presence" data (i.e., whether the tag is currently in the antenna's beam or not).

### 2. RSSI (Signal Strength / dB) - [NOT SUPPORTED VIA USB]
While the *hardware* of the reader utilizes signal strength internally (to trigger its buzzer), the `UHFReader18` firmware **does not append RSSI data** to the standard USB inventory response (`0x01` command). 
*   **Mathematical Proof:** A standard tag read packet is exactly 20 bytes. The first 6 bytes are headers/lengths, the next 12 bytes are the EPC, and the final 2 bytes are the CRC-16 checksum. There are zero remaining bytes in the packet for RSSI metadata.
*   *Note:* The hardware also features Wiegand (WG) and RS485 ports. It is theoretically possible that Auto-Read streams pushed to the RS485 port *might* contain a different data structure, but over USB polling, RSSI is unavailable.

---

## Prototype Triangulation Strategy (Single Antenna)

Because raw RSSI is unavailable over USB, standard "distance-based" trilateration is not possible. However, because UHF RFID antennas are highly directional (usually projecting a 60° to 70° cone), you can use **Spatial Intersection (Radar Sweeping)** for highly accurate localization using a single moving antenna.

### Requirements for the Prototype
1.  **The RFID Antenna (OT-ZMZYQ-799):** Provides a rapid binary stream of `TAG IN VIEW` or `NO TAG`.
2.  **GPS Module:** Provides global location (`Latitude`, `Longitude`).
3.  **IMU / Accelerometer / Compass:** Provides the exact angle/heading the antenna is pointing.

### The Algorithm
1.  **Data Logging:** A Python script continuously polls the RFID antenna while reading from the GPS and IMU.
2.  **The Sweep:** As the user sweeps the antenna left-to-right, the script logs the exact IMU angle when the tag *first* comes into view, and the angle when the tag *disappears*.
3.  **Vector Calculation:** The center point between those two angles is the exact trajectory of the tag relative to the GPS location.
4.  **Triangulation:** As the user moves to a second GPS location and repeats the sweep, the script draws a second trajectory vector. The physical location of the tag is the mathematical intersection of those vectors on a map.

This binary "Sweep" method is standard practice in mobile robotics and drone-based RFID inventory systems, as it completely bypasses the severe inaccuracies caused by multipath interference inherent in raw RSSI data.

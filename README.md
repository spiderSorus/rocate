# Rocate — UHF RFID Serial Protocol Driver & Radar-Sweep Triangulation Toolkit

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**Rocate** is a Python hardware communication toolkit, protocol analyzer, and spatial localization engine for long-range directional **UHF RFID readers** (specifically the **OT-ZMZYQ-799 / Chafon CF-RU5106** running `UHFReader18` firmware over USB/RS-232 serial).

Built for **hardware hackers, robotics/inventory engineers, and RFID researchers**, Rocate decodes the proprietary 57600-baud Chafon hexadecimal command/answer protocol with CRC-16 validation, tracks real-time 96-bit EPC tag presence across multiple antennas, and implements a **Single-Antenna Directional Radar-Sweep Triangulation** strategy to localize UHF tags without relying on noisy or firmware-omitted USB RSSI values.

---

## Built With

- **Language**: **Python 3.9+**
- **Serial Transport**: `pyserial` (`>= 3.5`) for non-blocking 57600-baud UART/USB packet framing.
- **Custom Protocol Stack (`chafon_rfid/`)**:
  - `base.py` & `crc.py` — Binary command serializer, frame parser, and `CRC-16` (`0xFFFF` polynomial `0x8408`) verifier.
  - `command.py` & `response.py` — Command opcodes (`G2_TAG_INVENTORY`, `CF_SET_WORK_MODE_18`, RF power configuration, frequency band tuning).
  - `uhfreader18.py` — `UHFReader18` 20-byte inventory response frame decoder extracting 12-byte (96-bit) Electronic Product Code (`EPC`) identifiers.

---

## Repository Structure

- `app.py` — Multi-antenna threaded `RFIDTracker` application with automatic Command-Mode initialization, live EPC presence tracking, and configurable room entry/exit debouncing.
- `chafon_rfid/` — Reusable Python driver package for Chafon `UHFReader18` / `CF-RU5106` readers.
- `active_reader.py` & `reader.py` — Continuous active inventory polling and tag event logger.
- `configure_reader.py` — Utility for switching reader work modes (Command/Answer vs. Auto-Read/Trigger) and RF power levels.
- `probe_rssi.py` & `test_commands.py` — Protocol reverse-engineering tools that systematically probe all 256 hex opcodes (`0x00..0xFF`) and inspect raw byte frames.
- `listen_only.py` — Passive serial sniffer for inspecting raw hex packets and verifying framing.
- `RFID_CAPABILITIES.md` — Technical packet structure analysis and mathematical specification for directional radar-sweep triangulation.

---

## How to Run

### Prerequisites
- **Python 3.9+**
- One or more **OT-ZMZYQ-799 / Chafon CF-RU5106** UHF RFID antennas connected via USB-Serial (e.g., `/dev/cu.usbserial-*` on macOS or `/dev/ttyUSB*` on Linux).

### 1. Install Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Multi-Antenna Tag Tracker (`app.py`)
Update `reader_ports` in `app.py` (or pass your serial device path) and start the tracker:
```bash
python3 app.py
```

### 3. Run Protocol Diagnostic & Configuration Tools
```bash
# Force reader into Command/Answer mode and verify configuration:
python3 configure_reader.py

# Passively sniff raw hex frames coming from the reader:
python3 listen_only.py

# Probe supported firmware opcodes (0x00..0xFF):
python3 test_commands.py
```

---

## Technical Findings & Radar-Sweep Triangulation

As documented in [`RFID_CAPABILITIES.md`](RFID_CAPABILITIES.md), mathematical analysis of the 20-byte USB inventory packet (`6 header/status bytes + 12 EPC bytes + 2 CRC-16 bytes`) proves that `UHFReader18` firmware omits RSSI bytes over USB Command Mode.

To achieve sub-meter localization without RSSI, **Rocate** uses **Directional Cone Spatial Intersection (Radar Sweeping)**:
1. The directional UHF patch antenna projects a focused ~60°–70° RF beam cone.
2. Sweeping the antenna across a room yields crisp binary `TAG_IN_VIEW` entry ($\theta_{\text{start}}$) and exit ($\theta_{\text{end}}$) angles.
3. The bisector $\theta_{\text{center}} = \frac{\theta_{\text{start}} + \theta_{\text{end}}}{2}$ defines a bearing ray from the antenna's origin $(x_n, y_n)$.
4. Intersecting bearing rays from two or more sweep positions (or multiple fixed antennas) triangulates the physical 2D/3D location of each EPC tag without multipath RSSI distortion.

---

## Roadmap & Planned Work Ahead (35+ Hours)

- [ ] **Phase 1 — IMU + GPS Sensor Fusion & Sweep Bearing Solver (~8 hrs)**
  - [ ] Add serial/I2C/UDP ingestion for IMU heading (compass/gyro yaw angle $\theta$) and GPS/local coordinates synced with `RFIDTracker` EPC timestamps.
  - [ ] Implement the angular sweep detector computing $\theta_{\text{start}}$, $\theta_{\text{end}}$, beamwidth confidence, and bearing ray vectors per EPC tag.
- [ ] **Phase 2 — Multi-Ray Spatial Triangulation & Probability Heatmap Engine (~8 hrs)**
  - [ ] Implement least-squares ray intersection and 2D occupancy-grid Bayesian probability updates combining multiple sweeps or multiple fixed antenna cones.
  - [ ] Support configurable antenna beam profiles (cone angle, max range attenuation, sidelobe suppression).
- [ ] **Phase 3 — Real-Time Web Radar Dashboard & Tag Registry (~8 hrs)**
  - [ ] Build a lightweight FastAPI/WebSocket + HTML5 Canvas radar UI displaying live antenna sweep cones, triangulated tag pins, and room presence history.
  - [ ] Add a persistent SQLite/JSON tag metadata registry mapping raw 96-bit hex EPCs (e.g. `E2806995...`) to human-readable item names and categories.
- [ ] **Phase 4 — RS-485 Auto-Read Transport & Hardware Simulator (`pytest`) (~8 hrs)**
  - [ ] Add RS-485 & Wiegand packet decoders to `chafon_rfid/` and verify whether RS-485 streaming frames expose hardware RSSI registers.
  - [ ] Build a virtual serial reader emulator (`MockUHFReader18`) and comprehensive `pytest` test suite covering CRC-16 edge cases, multi-tag inventory frames, and triangulation geometry.
- [ ] **Phase 5 — CLI Packaging & Config File Support (~4 hrs)**
  - [ ] Package `rocate` via `pyproject.toml` with CLI subcommands (`rocate track`, `rocate sweep`, `rocate probe`, `rocate configure`) and YAML/TOML port configuration.

---

## License

Released under the [MIT License](LICENSE).

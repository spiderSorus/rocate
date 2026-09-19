import serial
import time
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Passive Reader (Listen Only).")
    parser.add_argument('-p', '--port', type=str, default='/dev/cu.usbserial-310', help="Serial port")
    parser.add_argument('-b', '--baud', type=int, default=57600, help="Baud rate (typically 57600)")
    args = parser.parse_args()

    try:
        ser = serial.Serial(args.port, args.baud, timeout=0.1)
        print(f"🔌 Connected to {args.port} at {args.baud} baud.")
        print("📡 Listening for data when you scan a tag... (Press Ctrl+C to exit)\n")
        
        while True:
            if ser.in_waiting > 0:
                raw_data = ser.read(ser.in_waiting)
                hex_data = raw_data.hex().upper()
                ascii_data = raw_data.decode('ascii', errors='replace').replace('\r', '\\r').replace('\n', '\\n')
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] RAW BYTES: {hex_data} | ASCII: {ascii_data}")
            time.sleep(0.05)
            
    except serial.SerialException as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Exiting...")
        if 'ser' in locals() and ser.is_open:
            ser.close()
        sys.exit(0)

if __name__ == "__main__":
    main()

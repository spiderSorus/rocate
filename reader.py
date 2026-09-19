import serial
import time
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Read data from the LR-RFID antenna via USB Serial.")
    parser.add_argument(
        '-p', '--port',
        type=str,
        default='/dev/cu.usbserial-310',
        help="Serial port of the RFID reader (default: /dev/cu.usbserial-310)"
    )
    parser.add_argument(
        '-b', '--baud',
        type=int,
        default=9600,
        help="Baud rate (default: 9600)"
    )
    args = parser.parse_args()

    try:
        # Initialize serial connection
        ser = serial.Serial(args.port, args.baud, timeout=1)
        print(f"🔌 Connected to {args.port} at {args.baud} baud.")
        print("📡 Listening for RFID data... (Press Ctrl+C to exit)\n")
        
        while True:
            if ser.in_waiting > 0:
                # Read line from serial port, decoding to string
                raw_data = ser.readline()
                line = raw_data.decode('utf-8', errors='ignore').strip()
                
                # Only print if there's actual data
                if line or raw_data:
                    # Print ascii string if possible, else raw hex representation
                    display_data = line if line else raw_data.hex()
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 🏷️  Tag Detected: {display_data}")
            time.sleep(0.1)
            
    except serial.SerialException as e:
        print(f"❌ Error opening serial port {args.port}: {e}")
        print("Make sure the device is plugged in and no other program is using the port.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Exiting...")
        if 'ser' in locals() and ser.is_open:
            ser.close()
        sys.exit(0)

if __name__ == "__main__":
    main()

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
                # Read all available bytes in the buffer
                raw_data = ser.read(ser.in_waiting)
                
                # Format as Hex and ASCII
                hex_data = " ".join([f"{b:02X}" for b in raw_data])
                ascii_data = raw_data.decode('ascii', errors='replace').replace('\r', '\\r').replace('\n', '\\n')
                
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] HEX: {hex_data}  |  ASCII: {ascii_data}")
            time.sleep(0.05)
            
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

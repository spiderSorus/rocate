import serial
import time
from chafon_rfid.base import ReaderCommand

def test_command(ser, cmd_hex, cmd_name):
    print(f"\n--- Testing {cmd_name} (0x{cmd_hex:02X}) ---")
    cmd = ReaderCommand(cmd_hex)
    ser.write(cmd.serialize())
    time.sleep(0.5)
    
    if ser.in_waiting:
        resp = ser.read(ser.in_waiting)
        print(f"✅ Response: {resp.hex().upper()}")
    else:
        print("❌ No response.")

def main():
    port = '/dev/cu.usbserial-310'
    baud = 57600
    try:
        ser = serial.Serial(port, baud, timeout=0.2)
        print(f"🔌 Connected to {port} at {baud} baud.")
        
        print("\n🚀 Commencing Brute-Force Scan of all 256 possible commands...")
        print("This will take about 25 seconds. Please keep a tag in front of the antenna!\n")
        
        for cmd_hex in range(256):
            cmd = ReaderCommand(cmd_hex)
            ser.write(cmd.serialize())
            time.sleep(0.1)
            
            if ser.in_waiting:
                resp = ser.read(ser.in_waiting)
                # Ignore generic 'Format Error' or 'Parameter Error' responses if they are very common, 
                # but for now, print everything that responds so we don't miss anything.
                print(f"✅ [0x{cmd_hex:02X}] Responded with: {resp.hex().upper()}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

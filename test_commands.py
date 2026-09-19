import serial
import time
import sys
from chafon_rfid.uhfreader288m import G2InventoryCommand

def main():
    port = '/dev/cu.usbserial-310'
    baud = 57600
    try:
        ser = serial.Serial(port, baud, timeout=0.2)
        print(f"🔌 Connected to {port} at {baud} baud.")
        
        # Test 288M style inventory
        print("\n--- Testing 288M style G2_TAG_INVENTORY (0x01 with parameters) ---")
        cmd = G2InventoryCommand()
        print(f"Sending: {cmd.serialize().hex().upper()}")
        ser.write(cmd.serialize())
        
        time.sleep(0.3)
        if ser.in_waiting > 0:
            raw = ser.read(ser.in_waiting)
            print(f"Response: {raw.hex().upper()}")
        else:
            print("No response.")
            
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()

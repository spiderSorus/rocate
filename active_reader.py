import serial
import time
import sys
import argparse
from chafon_rfid.base import ReaderCommand, CommandRunner
from chafon_rfid.command import G2_TAG_INVENTORY, CF_GET_READER_INFO
from chafon_rfid.uhfreader18 import G2InventoryResponseFrame as G2InventoryResponseFrame18
from chafon_rfid.response import G2_TAG_INVENTORY_STATUS_MORE_FRAMES

class SerialTransport:
    def __init__(self, ser):
        self.ser = ser

    def write(self, data):
        self.ser.write(data)

    def read_frame(self):
        # A frame starts with length byte
        if not self.ser.is_open:
            return None
            
        # Read the first byte (length)
        length_bytes = self.ser.read(1)
        if not length_bytes:
            return None
            
        length = length_bytes[0]
        # Frame has 'length' more bytes
        rest_of_frame = self.ser.read(length)
        return length_bytes + rest_of_frame


def main():
    parser = argparse.ArgumentParser(description="Active Reader using Chafon protocol.")
    parser.add_argument('-p', '--port', type=str, default='/dev/cu.usbserial-310', help="Serial port")
    parser.add_argument('-b', '--baud', type=int, default=57600, help="Baud rate (typically 57600 or 115200)")
    args = parser.parse_args()

    try:
        ser = serial.Serial(args.port, args.baud, timeout=0.5)
        print(f"🔌 Connected to {args.port} at {args.baud} baud.")
        
        transport = SerialTransport(ser)
        
        # Optionally, get reader info to verify connection
        print("Checking connection (Get Reader Info)...")
        info_cmd = ReaderCommand(CF_GET_READER_INFO)
        transport.write(info_cmd.serialize())
        resp = transport.read_frame()
        if resp:
            print(f"✅ Received response: {resp.hex().upper()}")
        else:
            print("⚠️ No response for info command. Will try inventory anyway.")

        print("📡 Polling for RFID data... (Press Ctrl+C to exit)\n")
        
        inventory_cmd = ReaderCommand(G2_TAG_INVENTORY)
        
        while True:
            # Send inventory command
            transport.write(inventory_cmd.serialize())
            
            # Read all response frames for this command
            inventory_status = None
            while inventory_status is None or inventory_status == G2_TAG_INVENTORY_STATUS_MORE_FRAMES:
                frame_data = transport.read_frame()
                if not frame_data:
                    break
                
                try:
                    resp_frame = G2InventoryResponseFrame18(frame_data)
                    inventory_status = resp_frame.result_status
                    
                    for tag in resp_frame.get_tag():
                        epc_hex = tag.epc.hex().upper()
                        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 🏷️  Tag Detected: {epc_hex}")
                        
                except Exception as e:
                    print(f"Frame parsing error: {e}, Raw: {frame_data.hex()}")
                    break

            time.sleep(0.1)
            
    except serial.SerialException as e:
        print(f"❌ Error opening serial port {args.port}: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Exiting...")
        if 'ser' in locals() and ser.is_open:
            ser.close()
        sys.exit(0)

if __name__ == "__main__":
    main()

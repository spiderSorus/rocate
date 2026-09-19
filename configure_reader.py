import serial
import sys
from chafon_rfid.base import ReaderCommand
from chafon_rfid.command import CF_SET_WORK_MODE_18

def main():
    port = '/dev/cu.usbserial-310'
    baud = 57600

    try:
        ser = serial.Serial(port, baud, timeout=1)
        print(f"🔌 Connected to {port} at {baud} baud.")
        
        # 0x35 command to set Work Mode
        # Payload: 
        # Byte 0: Mode (0x00 = Command/Answer Mode)
        # Byte 1-5: Other parameters (using common defaults: 0x02, 0x01, 0x00, 0x01, 0x00)
        data_payload = [0x00, 0x02, 0x01, 0x00, 0x01, 0x00]
        cmd = ReaderCommand(CF_SET_WORK_MODE_18, data=data_payload)
        
        raw_cmd = cmd.serialize()
        print(f"Sending Command to set Answer Mode: {raw_cmd.hex().upper()}")
        
        ser.write(raw_cmd)
        
        # Wait for response
        resp = ser.read(100)
        
        if resp:
            print(f"✅ Response received: {resp.hex().upper()}")
            status = resp[3] if len(resp) >= 4 else -1
            if status == 0:
                print("🎉 Successfully set reader to Command/Answer mode!")
                print("You can now run active_reader.py and it should read the tags properly.")
            else:
                print(f"⚠️ Command accepted but returned status code: {status:02X}")
        else:
            print("❌ No response received from reader.")
            
    except serial.SerialException as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

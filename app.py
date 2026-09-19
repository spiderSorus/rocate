import serial
import time
import threading
from chafon_rfid.base import ReaderCommand
from chafon_rfid.command import G2_TAG_INVENTORY
from chafon_rfid.uhfreader18 import G2InventoryResponseFrame as G2InventoryResponseFrame18
from chafon_rfid.response import G2_TAG_INVENTORY_STATUS_MORE_FRAMES

class RFIDTracker:
    def __init__(self, port, baud=57600):
        self.port = port
        self.baud = baud
        self.ser = None
        self.running = False
        
        # Keep track of last seen time for each tag
        # self.tags = { "EPC_HEX": <timestamp> }
        self.seen_tags = {}

    def connect(self):
        self.ser = serial.Serial(self.port, self.baud, timeout=0.1)
        print(f"🔌 Connected to {self.port} at {self.baud} baud.")
        
    def start_polling(self, callback):
        self.running = True
        self.thread = threading.Thread(target=self._poll_loop, args=(callback,))
        self.thread.daemon = True
        self.thread.start()
        
    def _poll_loop(self, callback):
        inventory_cmd = ReaderCommand(G2_TAG_INVENTORY)
        raw_cmd = inventory_cmd.serialize()
        
        while self.running:
            print(f"[{time.strftime('%H:%M:%S')}] 📡 Pinging antenna... ", end="", flush=True)
            self.ser.write(raw_cmd)
            
            # Read response frame
            length_bytes = self.ser.read(1)
            tags_found_this_ping = 0
            if length_bytes:
                length = length_bytes[0]
                rest_of_frame = self.ser.read(length)
                frame_data = length_bytes + rest_of_frame
                
                try:
                    resp_frame = G2InventoryResponseFrame18(frame_data)
                    for tag in resp_frame.get_tag():
                        tags_found_this_ping += 1
                        epc = tag.epc.hex().upper()
                        self.seen_tags[epc] = time.time()
                        callback(self.port, epc)
                except Exception:
                    pass
            
            if tags_found_this_ping == 0:
                print("❌ No Tags")
            else:
                print(f"✅ Found {tags_found_this_ping} tag(s)")
                
            time.sleep(1.0)
            
    def stop(self):
        self.running = False
        if self.ser:
            self.ser.close()

# ==========================================
# CUSTOM LOGIC / APP 
# ==========================================

# This will store the tags currently in the room
active_tags_in_room = set()

def on_tag_scanned(reader_port, epc):
    """
    This function is called instantly whenever ANY reader detects a tag.
    """
    if epc not in active_tags_in_room:
        active_tags_in_room.add(epc)
        print(f"✨ NEW TAG ENTERED: {epc} (Detected by {reader_port})")
    else:
        # We already know about this tag, so we just silently update its timestamp internally
        pass

def main():
    # If you have multiple antennas (readers), just add their ports here!
    reader_ports = [
        '/dev/cu.usbserial-310',
        # '/dev/cu.usbserial-xxx',
        # '/dev/cu.usbserial-yyy'
    ]
    
    trackers = []
    
    try:
        for port in reader_ports:
            tracker = RFIDTracker(port)
            tracker.connect()
            tracker.start_polling(on_tag_scanned)
            trackers.append(tracker)
            
        print("\n📡 All antennas are now tracking! Waiting for tags...\n")
        
        # Main thread loop: You can also use this to clean up tags that left the room!
        while True:
            current_time = time.time()
            
            # Check for tags that haven't been seen in the last 5 seconds
            for tracker in trackers:
                tags_to_remove = []
                for epc, last_seen in tracker.seen_tags.items():
                    if current_time - last_seen > 5.0:
                        tags_to_remove.append(epc)
                        
                for epc in tags_to_remove:
                    del tracker.seen_tags[epc]
                    if epc in active_tags_in_room:
                        active_tags_in_room.remove(epc)
                        print(f"👋 TAG LEFT: {epc} (Lost signal on {tracker.port})")
                        
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping all trackers...")
        for t in trackers:
            t.stop()

if __name__ == "__main__":
    main()

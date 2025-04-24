import asyncio
import threading
import logging
from bleak import BleakClient, BleakScanner
from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger()

# Official from SFS-Link Manual v1.2
# SFS_Link[S/N]
SFS_DEVICE_NAME = "SFS-Link [047]"
SFS_ADDRESS = "54:32:04:78:64:4A"
# SFS_UUID = "6f000009-b5a3-f393-e0a9-e50e24dcca9e"
SFS_CHARACTERISTIC_UUID = "6f000009-b5a3-f393-e0a9-e50e24dcca9e"


class ScoreboardManager(QObject):
    """
    Manages the BLE connection to the SFS-Link scoreboard.
    Runs the asyncio event loop in a background thread.
    Emits a PyQt signal whenever new scoreboard data arrives.
    """

    scoreboard_updated = pyqtSignal(dict)  # scoreboard info

    def __init__(self, parent=None):
        super().__init__(parent)
        self.loop = None
        self.thread = None
        self.client = None
        self.running = False
        self.current_data = {}
        self.data_lock = threading.Lock()  # Initialize the lock

    def start(self):
        """Launch the asyncio event loop in a background thread."""
        if self.thread and self.thread.is_alive():
            logger.warning("ScoreboardManager is already running.")
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop(self): #*(4/23)
        """Stop the asyncio event loop and disconnect the BLE client."""
        self.running = False
        if self.loop and self.client and getattr(self.client, "is_connected", False):
            try:
                #schedule async disconnect on the event loop
                future = asyncio.run_coroutine_threadsafe(self._stop_async(), self.loop)
                future.result(5)  # Wait for the disconnect to complete
            except Exception as e:
                logger.error(f"Error stopping the BLE client: {e}", exc_info=True)
            
            #stop the event loop
            if self.loop:
                self.loop.call_soon_threadsafe(self.loop.stop)
            
            #wait for thread to exit
            if self.thread:
                self.thread.join(timeout=5)
            #housekeeping
            self.client = None
            self.loop = None
            self.thread = None
            logger.info("ScoreboardManager stopped.")


    async def _stop_async(self):
        """Asynchronously disconnect the BLE client."""
        if self.client and self.client.is_connected:
            await self.client.disconnect()

    def _run_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self._main_task())
        except Exception as e:
            logger.error(f"Exception in scoreboard manager loop: {e}", exc_info=True)
        finally:
            self.loop.close()

    async def _main_task(self):
        logger.info("Scanning for BLE devices...")
        target_device = await self._find_target_device()
        if not target_device:
            logger.error(f"Device with name {SFS_DEVICE_NAME} or address {SFS_ADDRESS} not found.")
            self.running = False
            return

        logger.info(f"Connecting to device {target_device.name} at {target_device.address}")
        async with BleakClient(target_device.address) as client:
            self.client = client
            if not client.is_connected:
                logger.error("Failed to connect to the device.")
                self.running = False
                return

            logger.info(f"Successfully connected to {target_device.address}")

            # List available services and characteristics
            logger.info("Listing available services and characteristics:")
            for service in client.services:
                logger.info(f"Service: {service.uuid}")
                for char in service.characteristics:
                    logger.info(f"  Characteristic: {char.uuid} - Properties: {char.properties}")

            # Validate and read the characteristic
            if SFS_CHARACTERISTIC_UUID in [char.uuid for service in client.services for char in service.characteristics]:
                await self._poll_characteristic(client, SFS_CHARACTERISTIC_UUID)
            else:
                logger.error(f"Characteristic {SFS_CHARACTERISTIC_UUID} not found on the device.")
                self.running = False

        self.client = None

    async def _find_target_device(self):
        devices = await BleakScanner.discover(timeout=5.0)
        for d in devices:
            logger.info(f"Found device: {d.name} - {d.address}")
            if d.name == SFS_DEVICE_NAME or d.address == SFS_ADDRESS:
                return d
        return None

    async def _poll_characteristic(self, client, uuid):
        """Poll the specified characteristic value in a loop."""
        while self.running and client.is_connected:
            try:
                value = await client.read_gatt_char(uuid)
                self._notification_handler(0, value)
            except Exception as read_err:
                logger.error(f"Error reading characteristic {uuid}: {read_err}", exc_info=True)
                break
            await asyncio.sleep(0.9)  # Adjust the polling interval as needed

    def _notification_handler(self, sender: int, data: bytearray):
        """
        Handle notifications from the BLE device.
        The data is a 14-char string of hex from the SFS-Link.
        e.g. b'06125602140A38' => decode to "06 12 56 02 14 0A 38"
        """
        raw_str = data.decode("ascii", errors="ignore").strip()
        logger.info(f"Raw characteristic value: {raw_str}")
        if len(raw_str) != 14:
            logger.warning(f"Unexpected scoreboard data len={len(raw_str)}: {raw_str}")
            return

        if raw_str == "00000000000000":
            self.scoreboard_updated.emit({})
            return

        parsed_data = self._parse_sfs_link_hex(raw_str)
        if parsed_data:
            logger.info(f"Parsed data: {parsed_data}")
            with self.data_lock:  # Acquire the lock before modifying shared data
                self.current_data = parsed_data
            self.scoreboard_updated.emit(parsed_data)

    def _parse_sfs_link_hex(self, hex_str: str) -> dict:
        hex_pairs = [hex_str[i : i + 2] for i in range(0, 14, 2)]
        if len(hex_pairs) != 7:
            return {}

        try:
            b2 = int(hex_pairs[0], 16)  # Right score (BCD)
            b3 = int(hex_pairs[1], 16)  # Left score (BCD)
            b4 = int(hex_pairs[2], 16)  # Seconds (BCD)
            b5 = int(hex_pairs[3], 16)  # Minutes (BCD)
            b6 = int(hex_pairs[4], 16)  # Lamp bits
            b7 = int(hex_pairs[5], 16)  # Match bits
            b9 = int(hex_pairs[6], 16)  # Penalty bits
        except ValueError as e:
            logger.error(f"Invalid hex in scoreboard data: {hex_str} => {e}")
            return {}

        #Decode the BCD fields
        right_score = decode_bcd(b2)
        left_score = decode_bcd(b3)
        seconds = decode_bcd(b4)
        minutes = decode_bcd(b5)
        lamp_bits = parse_lamp_bits(b6)
        match_bits = parse_matches_and_priorities(b7)
        penalty = parse_penalty_bits(b9)    

        parsed_data = {
            "right_score": right_score,
            "left_score":  left_score,
            "seconds":     seconds,
            "minutes":     minutes,
            "lamp_bits":   lamp_bits,
            "match_bits":  match_bits,
            "penalty":     penalty,
        }
        return(parsed_data)
        #print(parsed_data) #TEST PRINT GO BRR

# Helper functions for parsing the SFS-Link data  
def decode_bcd(bcd: int) -> int:
    """Decode a Binary-Coded Decimal (BCD) value."""
    return (bcd >> 4) * 10 + (bcd & 0x0F)

def parse_lamp_bits(b6: int) -> dict:
    """
    Parse 6th byte (b6) for lamp states.
    Returns dictionary indicating which lamps are ON (True) or OFF (False).
    """
    return {
        
        "left_white": bool(b6 & 0x01),# D0
        "right_white": bool(b6 & 0x02),# D1
        "left_red": bool(b6 & 0x04), # D2
        "right_green": bool(b6 & 0x08),  # D3
        "right_yellow": bool(b6 & 0x10), # D4 
        "left_yellow": bool(b6 & 0x20), # D5 
        # D6 and D7 are not used
    }

def parse_matches_and_priorities(b7: int) -> dict:
    """
    Parse7th byte (b7) for num of matches and priority lamps.

    b7 bits:
      D0..D1 => number of matches (0..3)
      D2 => right priority (1=ON)
      D3 => left priority (1=ON)
      D4..D7 => unused
    """
    # bits D0..D1 (mask 0b0011)
    num_matches = b7 & 0x03 
    # bit D2 (0b0100)
    right_priority = bool(b7 & 0x04)  
    # bit D3 (0b1000)
    left_priority  = bool(b7 & 0x08)  

    return {
        "num_matches": num_matches,
        "right_priority": right_priority,
        "left_priority": left_priority
    }

def parse_penalty_bits(b9: int) -> dict:
    """
    Parse 9th byte for red/yellow penalty card lights.

    Bits D0..D3 are:
      D0 => Right Red
      D1 => Left Red
      D2 => Right Yellow
      D3 => Left Yellow
    Bits D4..D7 are ignored/unused as per doc.
    """
    return {
        "penalty_right_red": bool(b9 & 0x01),# D0
        "penalty_left_red": bool(b9 & 0x02), # D1
        "penalty_right_yellow": bool(b9 & 0x04),  # D2
        "penalty_left_yellow": bool(b9 & 0x08),# D3
    }



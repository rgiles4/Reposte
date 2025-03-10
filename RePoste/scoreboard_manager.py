import asyncio
import threading
import logging
from bleak import BleakClient
from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger()

# Official from SFS-Link Manual v1.2
# SFS_Link[S/N]
SFS_DEVICE_NAME = "SFS_Link[047]"
SFS_ADDRESS = "54:32:04:78:64:4A"
SFS_UUID = "6f000009-b5a3-f393-e0a9-e50e24dcca9e"


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
        
    def start(self):
        """Launch the asyncio event loop in a background thread."""
        if self.thread and self.thread.is_alive():
            logger.warning("ScoreboardManager is already running.")
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop the asyncio event loop and background thread."""
        if not self.running:
            return

        self.running = False
        if self.loop and not self.loop.is_closed():
            asyncio.run_coroutine_threadsafe(self._stop_async(), self.loop)
        if self.thread and self.thread.is_alive():
            self.thread.join()
        self.thread = None

    async def _stop_async(self):
        """Asynchronously disconnect the BLE client."""
        if self.client and self.client.is_connected:
            await self.client.disconnect()

    def _run_loop(self):
        """Run the asyncio event loop."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self._main_task(SFS_ADDRESS, SFS_UUID))
        except Exception as e:
            logger.error(f"Exception in scoreboard manager loop: {e}", exc_info=True)
        finally:
            self.loop.close()

    async def _main_task(self, address, uuid):
        """Main task to connect to the BLE device and read data at a controlled rate."""
        try:
            async with BleakClient(address) as client:
                if not client.is_connected:
                    logger.error(f"Failed to connect to {address}")
                    return

                logger.info(f"Successfully connected to {address}")
                while self.running and client.is_connected:
                    try:
                        value = await client.read_gatt_char(uuid)
                        self._notification_handler(0, value)
                    except Exception as read_err:
                        logger.error(f"Error reading characteristic {uuid}: {read_err}", exc_info=True)
                        # Break out of the loop if a read error occurs
                        break
                    # Increased sleep interval to reduce pressure on BLE read
                    await asyncio.sleep(0.1)  # 100ms between reads
        except Exception as e:
            logger.error(f"Error in main task: {e}", exc_info=True)


    # async def _read_characteristic(self, client, uuid):
    #     """Read the characteristic value using its UUID."""
    #     print("Reading characteristic...")
    #     try:
    #         value = await client.read_gatt_char(uuid)
    #         # logger.info(f"Value of characteristic {uuid}: {value}") # logger go brr
    #         self._notification_handler(0, value)
    #     except Exception as e:
    #         logger.error(f"Error reading characteristic {uuid}: {e}", exc_info=True)

    def _notification_handler(self, sender: int, data: bytearray):
        """
        Handle notifications from the BLE device.
        The data is a 14-char string of hex from the SFS-Link.
        e.g. b'06125602140A38' => decode to "06 12 56 02 14 0A 38"
        """
        raw_str = data.decode("ascii", errors="ignore").strip()
        if len(raw_str) != 14:
            logger.warning(f"Unexpected scoreboard data len={len(raw_str)}: {raw_str}")
            return

        if raw_str == "00000000000000":
            self.scoreboard_updated.emit({})
            return

        parsed_data = self._parse_sfs_link_hex(raw_str)
        if parsed_data:
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



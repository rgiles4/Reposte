import asyncio
import threading
import logging
from bleak import BleakClient
from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger()

SFS_DEVICE_NAME = "SFS_Link[047]"
SFS_ADDRESS = "54:32:04:78:64:4A"
SFS_UUID = "6f000009-b5a3-f393-e0a9-e50e24dcca9e"


class ScoreboardManager(QObject):
    """
    Manages the BLE connection to the SFS-Link scoreboard.
    Runs the asyncio event loop in a background thread.
    Emits a PyQt signal whenever new scoreboard data arrives.
    """

    scoreboard_updated = pyqtSignal(dict)  # Emits updated scoreboard data

    def __init__(self, parent=None):
        super().__init__(parent)
        self.loop = None
        self.thread = None
        self.client = None
        self.running = False
        self.current_data = {}

        # Store the most recent scoreboard data in a single byte array
        self.current_byte_array = bytearray(7)  # Initialize empty 7-byte array
        self.previous_byte_array = bytearray(7)

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

    def _is_data_ready_for_update(self):
        """
        Determines if data is ready for update.
        For example, you could check some conditions before calling read.            """
        # Compare byte array with value to see if there is any new change
        if self.current_byte_array != self.previous_byte_array:
            self.previous_byte_array = self.current_byte_array
            return True
        return False

    async def _main_task(self, address, uuid):
        """Main task to connect to the BLE device and read data."""
        try:
            async with BleakClient(address) as client:
                if client.is_connected:
                    logger.info(f"Successfully connected to {address}")
                    while self.running: #Need to find a way to have this loop be used as an if statement that look for any new updates within the bytearray
                        if self._is_data_ready_for_update():
                            await self._read_characteristic(client, uuid)
                        await asyncio.sleep(0.01)  # Sleep for 10ms
                else:
                    logger.error(f"Failed to connect to {address}")
        except Exception as e:
            logger.error(f"Error in main task: {e}", exc_info=True)
        
    async def _read_characteristic(self, client, uuid):
        """Read the characteristic value using its UUID."""
        try:
            value = await client.read_gatt_char(uuid)
            self._notification_handler(0, value)
        except Exception as e:
            logger.error(f"Error reading characteristic {uuid}: {e}", exc_info=True)

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

        # Convert hex string into a byte array (7 bytes)
        new_byte_array = bytearray(int(raw_str[i:i+2], 16) for i in range(0, 14, 2))

        # Only update if the data has changed
        if new_byte_array != self.current_byte_array:
            self.current_byte_array = new_byte_array  # Update the stored byte array
            self.previous_byte_array = self.current_byte_array # Set previous byte array to current
            self.previous
            parsed_data = self._parse_sfs_link_bytes(new_byte_array)
            self.current_data = parsed_data
            self.scoreboard_updated.emit(parsed_data)  # Send updated data to UI

    def _parse_sfs_link_bytes(self, byte_data: bytearray) -> dict:
        """
        Parses the received 7-byte array into structured scoreboard data.
        """

        try:
            b2 = byte_data[0]  # Right score (BCD)
            b3 = byte_data[1]  # Left score (BCD)
            b4 = byte_data[2]  # Seconds (BCD)
            b5 = byte_data[3]  # Minutes (BCD)
            b6 = byte_data[4]  # Lamp bits
            b7 = byte_data[5]  # Match bits
            b9 = byte_data[6]  # Penalty bits
        except IndexError as e:
            logger.error(f"Invalid byte array length: {byte_data} => {e}")
            return {}

        # Decode values from bytes
        right_score = decode_bcd(b2)
        left_score = decode_bcd(b3)
        seconds = decode_bcd(b4)
        minutes = decode_bcd(b5)
        lamp_bits = parse_lamp_bits(b6)
        match_bits = parse_matches_and_priorities(b7)
        penalty = parse_penalty_bits(b9)

        parsed_data = {
            "right_score": right_score,
            "left_score": left_score,
            "seconds": seconds,
            "minutes": minutes,
            "lamp_bits": lamp_bits,
            "match_bits": match_bits,
            "penalty": penalty,
        }
        return parsed_data


# Utility functions for decoding BCD values and bit parsing
def decode_bcd(bcd: int) -> int:
    """Decode a Binary-Coded Decimal (BCD) value."""
    return (bcd >> 4) * 10 + (bcd & 0x0F)

def parse_lamp_bits(b6: int) -> dict:
    """Parse lamp states from the 6th byte."""
    return {
        "left_white": bool(b6 & 0x01),
        "right_white": bool(b6 & 0x02),
        "left_red": bool(b6 & 0x04),
        "right_green": bool(b6 & 0x08),
        "right_yellow": bool(b6 & 0x10),
        "left_yellow": bool(b6 & 0x20),
    }

def parse_matches_and_priorities(b7: int) -> dict:
    """Parse number of matches and priority lamps from the 7th byte."""
    return {
        "num_matches": b7 & 0x03,  # Bits D0-D1
        "right_priority": bool(b7 & 0x04),  # Bit D2
        "left_priority": bool(b7 & 0x08),  # Bit D3
    }

def parse_penalty_bits(b9: int) -> dict:
    """Parse penalty card lights from the 9th byte."""
    return {
        "penalty_right_red": bool(b9 & 0x01),
        "penalty_left_red": bool(b9 & 0x02),
        "penalty_right_yellow": bool(b9 & 0x04),
        "penalty_left_yellow": bool(b9 & 0x08),
    }

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

        # Store scoreboard data in memory if needed
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
        # If already stopped, do nothing
        if not self.running:
            return

        self.running = False
        if self.loop and not self.loop.is_closed():
            asyncio.run_coroutine_threadsafe(self._stop_async(), self.loop)
        if self.thread and self.thread.is_alive():
            self.thread.join()
        self.thread = None

    async def _stop_async(self):
        if self.client and self.client.is_connected:
            await self.client.disconnect()

    def _run_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(
                self._main_task(SFS_ADDRESS, SFS_UUID)
            )
        except Exception as e:
            logger.error(f"Exception in scoreboard manager loop: {e}")
        finally:
            # The loop closes here
            self.loop.close()

    async def _main_task(self, address, uuid):

        try:
            # Create BleakClient instance
            async with BleakClient(address) as client:
                # Check if connected
                if client.is_connected:
                    print(f"Successfully connected to {address}")
                    # Read the characteristic value using its UUID
                    value = await client.read_gatt_char(uuid)
                    print(f"Value of characteristic {uuid}: {value}")
                else:
                    print(f"Failed to connect to {address}")
        except Exception as e:
            print(f"Error: {e}")

    def _notification_handler(self, sender: int, data: bytearray):
        """
        The data is a 14-char string of hex from the SFS-Link.
        e.g. b'06125602140A38' => decode to "06 12 56 02 14 0A 38"
        """
        # Convert raw bytes to string
        raw_str = data.decode("ascii", errors="ignore").strip()
        if len(raw_str) != 14:
            logger.warning(
                f"Unexpected scoreboard data len={len(raw_str)}: {raw_str}"
            )
            return

        # Check if it's "00000000000000" => means scoreboard not detected
        if raw_str == "00000000000000":
            # Optionally emit an empty scoreboard update or handle offline
            self.scoreboard_updated.emit({})
            return

        parsed_data = self._parse_sfs_link_hex(raw_str)
        if parsed_data:
            self.current_data = parsed_data
            self.scoreboard_updated.emit(parsed_data)

    def _parse_sfs_link_hex(self, hex_str: str) -> dict:
        """
        SFS-Link doc: 14 hex chars => 7 bytes: Favero bytes 2..7,9
         Byte2 => Right Score
         Byte3 => Left Score
         Byte4 => Seconds
         Byte5 => Minutes
         Byte6 => Lamp bits
         Byte7 => Match bits
         Byte9 => Penalty bits
        """
        # break into 7 pairs, each 2 hex chars
        # e.g. "06125602140A38" => ["06","12","56","02","14","0A","38"]
        hex_pairs = [hex_str[i : i + 2] for i in range(0, 14, 2)]
        if len(hex_pairs) != 7:
            return {}

        # Convert each pair to an int
        try:
            b2 = int(hex_pairs[0], 16)
            b3 = int(hex_pairs[1], 16)
            b4 = int(hex_pairs[2], 16)
            b5 = int(hex_pairs[3], 16)
            b6 = int(hex_pairs[4], 16)
            b7 = int(hex_pairs[5], 16)
            b9 = int(hex_pairs[6], 16)
        except ValueError as e:
            logger.error(f"Invalid hex in scoreboard data: {hex_str} => {e}")
            return {}

        # Map to Favero fields
        right_score = b2
        left_score = b3
        seconds = b4
        minutes = b5 & 0x0F  # If Favero uses lower nibble for minutes
        lamp_bits = b6
        match_bits = b7
        penalty = b9

        return {
            "right_score": right_score,
            "left_score": left_score,
            "seconds": seconds,
            "minutes": minutes,
            "lamp_bits": lamp_bits,
            "match_bits": match_bits,
            "penalty": penalty,
        }
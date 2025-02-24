import asyncio
import threading
import logging
from bleak import BleakClient, BleakScanner
from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger()

# Official from SFS-Link Manual v1.2
# SFS_Link[S/N]
SFS_DEVICE_NAME = "SFS_Link[047]"
SFS_UUID = "6F000000-B5A3-F393-E0A9-E50E24DCCA9E"

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
            self.loop.run_until_complete(self._main_task())
        except Exception as e:
            logger.error(f"Exception in scoreboard manager loop: {e}")
        finally:
            # The loop closes here
            self.loop.close()

    async def _main_task(self):
        """Scan, connect, subscribe to SFS-Link characteristic notifications."""
        logger.info("ScoreboardManager: scanning for SFS-Link...")
        found_device = None
        try:
            devices = await BleakScanner.discover(timeout=5.0)
            for d in devices:
                if d.name and d.name.startswith(SFS_DEVICE_NAME):
                    found_device = d
                    break
        except Exception as e:
            logger.error(f"BLE scan failed: {e}")
            self.running = False
            return

        if not found_device:
            logger.error("SFS-Link device not found. Stopping manager.")
            self.running = False
            return

        logger.info(f"Found SFS-Link: {found_device.name} [{found_device.address}]")
        self.client = BleakClient(found_device.address)
        try:
            await self.client.connect()
            logger.info("Connected to SFS-Link!")
            # Start notifications on the same UUID for characteristic
            await self.client.start_notify(SFS_UUID, self._notification_handler)

            # Keep the loop alive while running
            while self.running and self.client.is_connected:
                await asyncio.sleep(1)

            logger.info("ScoreboardManager: stopping notifications.")
            await self.client.stop_notify(SFS_UUID)

        except Exception as e:
            logger.error(f"Error connecting or receiving data: {e}")
        finally:
            if self.client and self.client.is_connected:
                await self.client.disconnect()
            self.running = False
            logger.info("ScoreboardManager: disconnected and stopped.")

    def _notification_handler(self, sender: int, data: bytearray):
        """
        The data is a 14-char string of hex from the SFS-Link.
        e.g. b'06125602140A38' => decode to "06 12 56 02 14 0A 38"
        """
        # Convert raw bytes to string
        raw_str = data.decode('ascii', errors='ignore').strip()
        if len(raw_str) != 14:
            logger.warning(f"Unexpected scoreboard data len={len(raw_str)}: {raw_str}")
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
        hex_pairs = [hex_str[i:i+2] for i in range(0, 14, 2)]
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
        left_score  = b3
        seconds     = b4
        minutes     = b5 & 0x0F # If Favero uses lower nibble for minutes
        lamp_bits   = b6
        match_bits  = b7
        penalty     = b9

        return {
            "right_score": right_score,
            "left_score":  left_score,
            "seconds":     seconds,
            "minutes":     minutes,
            "lamp_bits":   lamp_bits,
            "match_bits":  match_bits,
            "penalty":     penalty,
        }
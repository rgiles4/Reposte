import asyncio
from bleak import BleakClient

SFS_ADDRESS = "54:32:04:78:64:4A"
SFS_UUID = "6f000009-b5a3-f393-e0a9-e50e24dcca9e"

async def simple_read():
    async with BleakClient(SFS_ADDRESS) as client:
        if client.is_connected:
            value = await client.read_gatt_char(SFS_UUID)
            print(f"Read value: {value}")

asyncio.run(simple_read())
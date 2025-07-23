import asyncio
from livef1.adapters.realtime_client import RealF1Client

client = RealF1Client(topics=["CarData.z"])

@client.callback("process_telemetry")
async def handle_telemetry(records):
    telemetry_data = records.get("CarData.z")
    if telemetry_data:
        for record in telemetry_data:
            print(f"Telemetry: {record}")

client.run()

import asyncio
from livef1.adapters import RealF1Client

# Initialize client with topics to subscribe
client = RealF1Client(
    topics=["CarData.z", "Position.z"],
    log_file_name="race_data.json"
)

# Define callback for incoming data
@client.callback("telemetry_handler")
async def handle_data(records):
    for record in records:
        print(record)  # Process incoming data

# Run client in async main function
async def main():
    # Use _async_run() instead of run()
    await client._async_run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopping F1 data collection...")
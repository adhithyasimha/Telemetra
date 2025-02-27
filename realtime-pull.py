import asyncio
from livef1.adapters import RealF1Client

# Initialize client for telemetry data
telemetry = RealF1Client(
    topics=["CarData.z"],  # Car telemetry
    log_file_name="telemetry.json"
)

# Initialize client for position data (fixed 'topic' to 'topics')
position = RealF1Client(
    topics=["Position.z"],  # Corrected parameter name
    log_file_name="position.json"
)

# Define callback for telemetry data
@telemetry.callback("telemetry_handler")
async def handle_telemetry_data(records):
    for record in records:
        print(record)  # Process incoming telemetry data

# Define callback for position data
@position.callback("position_handler")
async def handle_position_data(records):
    for record in records:
        print(record)  # Process incoming position data

# Main function to run both clients concurrently
async def main():
    await asyncio.gather(
        telemetry._async_run(),
        position._async_run()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopping F1 data collection...")
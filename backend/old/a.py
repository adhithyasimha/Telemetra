import asyncio
import json
from livef1.adapters import RealF1Client
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize F1 client without any log file
client = RealF1Client(
    topics=["DriverList", "SessionInfo"],
    log_file_name=None
)

def write_to_file(filename, data):
    """Helper function to write raw data to a file"""
    try:
        with open(filename, 'a') as f:
            f.write(f"{json.dumps(data)}\n")
    except Exception as e:
        logger.error(f"Error writing to {filename}: {e}")

# Callback to handle incoming data
@client.callback("handle_data")
async def handle(records):
    try:
        if "DriverList" in records:
            write_to_file("driver.json", records["DriverList"])
        
        if "SessionInfo" in records:
            write_to_file("session.json", records["SessionInfo"])
            
    except Exception as e:
        logger.error(f"Error in callback: {e}")

async def main():
    try:
        # Clear existing files at start
        open("driver.json", 'w').close()
        open("session.json", 'w').close()
        
        # Run for 5 seconds only
        await asyncio.wait_for(client._async_run(), timeout=5.0)
        
    except asyncio.TimeoutError:
        logger.info("5 second timeout reached - stopping")
    except Exception as e:
        logger.error(f"Error in main: {e}")
    finally:
        logger.info("Client stopped")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown complete")
    finally:
        logger.info("Program finished")
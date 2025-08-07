import asyncio
import json
import logging
import sys
import boto3
from datetime import datetime
from livef1.adapters import RealF1Client


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


s3 = boto3.client("s3")
DRIVER_BUCKET = "f1-driverlist"
SESSION_BUCKET = "f1-session-info"


DRIVER_FILE = "driver_list.json"
SESSION_FILE = "session_info.json"


client = RealF1Client(
    topics=["DriverList", "SessionInfo"]
)

def save_and_upload(filename, data, bucket, prefix):
    try:
        # Save to local file
        with open(filename, "w") as f:
            json.dump(data, f)
        logger.info(f"Saved to {filename}")

        # Upload to S3
        timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        key = f"{prefix}/{timestamp}.json"
        with open(filename, "rb") as f:
            s3.put_object(Bucket=bucket, Key=key, Body=f)
        logger.info(f"Uploaded to s3://{bucket}/{key}")
    except Exception as e:
        logger.error(f"Error saving/uploading {filename}: {e}")

@client.callback("handle_data")
async def handle(records):
    try:
        if "DriverList" in records:
            save_and_upload(DRIVER_FILE, records["DriverList"], DRIVER_BUCKET, "drivers")
        if "SessionInfo" in records:
            save_and_upload(SESSION_FILE, records["SessionInfo"], SESSION_BUCKET, "session_info")
    except Exception as e:
        logger.error(f"Error in handle(): {e}")


async def main():
    try:
        task = asyncio.create_task(client._async_run())
        await asyncio.sleep(5)  # run only for 5 seconds
        task.cancel()
        logger.info("Stopped RealF1Client after 5 seconds.")
    except Exception as e:
        logger.error(f"Main loop error: {e}")


if __name__ == "__main__":
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(main())
    finally:
        loop.close()

import asyncio
import json
import logging
import boto3
from datetime import datetime
from livef1.adapters import RealF1Client

# Initialize logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# S3 Configuration
S3_CLIENT = boto3.client('s3')
DRIVER_BUCKET = "f1-drivers-list"
SESSION_BUCKET = "f1-session"
REGION = "ap-south-1"

# Initialize F1 client
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

def upload_to_s3(filename, bucket, data_type):
    """Upload collected data to S3"""
    try:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        s3_key = f"{data_type}/{timestamp}.json"
        
        # Upload the file
        with open(filename, 'rb') as f:
            S3_CLIENT.put_object(
                Bucket=bucket,
                Key=s3_key,
                Body=f
            )
        logger.info(f"Successfully uploaded {filename} to s3://{bucket}/{s3_key}")
        return True
    except Exception as e:
        logger.error(f"Error uploading to S3: {e}")
        return False

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
        logger.info("Starting data collection for 5 seconds...")
        await asyncio.wait_for(client._async_run(), timeout=5.0)
        
    except asyncio.TimeoutError:
        logger.info("5 second timeout reached - stopping collection")
    except Exception as e:
        logger.error(f"Error in main: {e}")
    finally:
        # Upload files to S3
        logger.info("Starting S3 upload process...")
        
        driver_success = upload_to_s3("driver.json", DRIVER_BUCKET, "drivers")
        session_success = upload_to_s3("session.json", SESSION_BUCKET, "sessions")
        
        if driver_success and session_success:
            logger.info("All files uploaded successfully to S3")
        else:
            logger.warning("Some files failed to upload to S3")
        
        logger.info("Client stopped")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown complete")
    finally:
        logger.info("Program finished")

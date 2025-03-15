from kafka import KafkaConsumer
import json
import redis
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Kafka Consumer for driver_list
try:
    consumer = KafkaConsumer(
        'driver_list',
        bootstrap_servers='localhost:9092',
        auto_offset_reset='earliest',
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        consumer_timeout_ms=10000  # Timeout after 10s if no messages
    )
    logger.info("Kafka consumer initialized successfully")
except Exception as e:
    logger.error(f"Failed to connect to Kafka: {e}")
    raise

# Redis connection
try:
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    logger.info("Connected to Redis")
except Exception as e:
    logger.error(f"Failed to connect to Redis: {e}")
    raise

def send_driver_list_to_redis():
    """
    Consumes Driver List records from Kafka and sends them to Redis.
    """
    logger.info("Starting Kafka consumer for driver_list...")
    try:
        for message in consumer:
            driver_data = message.value
            logger.info(f"Received message from Kafka: {driver_data}")
            
            # Iterate over driver entries (e.g., '63': {...}, '1': {...})
            for driver_no, details in driver_data.items():
                if driver_no.isdigit():  # Only process numeric keys
                    # Store as a hash with driver_no as key
                    r.hset(driver_no, mapping=details)
                    logger.info(f"Inserted driver {details['RacingNumber']} into Redis")
            break  # Stop after first batch—Driver List is one-time
    except StopIteration:
        logger.warning("No messages received from Kafka within timeout period")
    except Exception as e:
        logger.error(f"Error processing Kafka message: {e}")

if __name__ == "__main__":
    try:
        send_driver_list_to_redis()
    except KeyboardInterrupt:
        logger.info("Stopping Redis sink...")
    finally:
        consumer.close()
        logger.info("Resources cleaned up")
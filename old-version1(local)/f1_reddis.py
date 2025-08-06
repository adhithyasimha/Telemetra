from kafka import KafkaConsumer
import json
import redis
import logging
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Kafka Consumer for all F1 topics
try:
    consumer = KafkaConsumer(
        'driver_list', 'telemetry', 'position', 'session_info', 'track_status',
        'session_status', 'timing_data_f1', 'weather_data', 'team_radio',
        'race_control_messages', 'heartbeat',
        bootstrap_servers='localhost:9092',
        auto_offset_reset='earliest',
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        consumer_timeout_ms=5000  # 5s timeout to avoid premature exit
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

def clean_data(data):
    """
    Remove None values and convert all values to strings for Redis compatibility.
    """
    return {k: str(v) if v is not None else "" for k, v in data.items()}

def send_to_redis():
    """
    Consumes Kafka topics and sends them to Redis in real-time.
    """
    logger.info("Starting live Kafka consumer...")
    while True:
        try:
            for message in consumer:
                topic = message.topic
                data = message.value
                timestamp = data.get('Utc', str(int(time.time() * 1000)))
                receive_time = time.time()

                logger.info(f"Received message at {receive_time} - Topic: {topic}, Data: {data}")

                try:
                    if topic == 'driver_list':
                        for driver_no, details in data.items():
                            if driver_no.isdigit():
                                cleaned_details = clean_data(details)
                                r.hset(f"driver:{driver_no}", mapping=cleaned_details)
                                logger.info(f"Updated driver {cleaned_details.get('RacingNumber', driver_no)} into Redis")

                    elif topic == 'telemetry':
                        driver_no = str(data.get('DriverNo', ''))
                        if driver_no:
                            cleaned_data = clean_data(data)
                            r.hset(f"latest:telemetry:{driver_no}", mapping=cleaned_data)
                            r.expire(f"latest:telemetry:{driver_no}", 300)
                            logger.info(f"Stored telemetry for {driver_no} at {timestamp}")

                    elif topic == 'position':
                        driver_no = str(data.get('DriverNo', ''))
                        if driver_no:
                            cleaned_data = clean_data(data)
                            r.hset(f"latest:position:{driver_no}", mapping=cleaned_data)
                            r.expire(f"latest:position:{driver_no}", 300)
                            logger.info(f"Stored position for {driver_no} at {timestamp}")

                    elif topic == 'timing_data_f1':
                        driver_no = str(data.get('DriverNo', ''))
                        if driver_no:
                            cleaned_data = clean_data(data)
                            r.hset(f"latest:timing:{driver_no}", mapping=cleaned_data)
                            r.expire(f"latest:timing:{driver_no}", 300)
                            logger.info(f"Stored timing data for {driver_no} at {timestamp}")

                    elif topic in ['session_info', 'track_status', 'session_status',
                                  'weather_data', 'team_radio', 'race_control_messages', 'heartbeat']:
                        cleaned_data = clean_data(data)
                        key = f"{topic}:{timestamp}"
                        r.hset(key, mapping=cleaned_data)
                        r.expire(key, 300)
                        logger.info(f"Stored {topic} data at {timestamp}")

                except Exception as e:
                    logger.error(f"Error processing message from topic {topic}: {e}, Data: {data}")
                    continue

        except StopIteration:
            logger.warning("No messages received within timeout, retrying...")
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error in Kafka consumer loop: {e}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        send_to_redis()
    except KeyboardInterrupt:
        logger.info("Stopping Redis sink...")
    finally:
        consumer.close()
        logger.info("Resources cleaned up")
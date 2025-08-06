from confluent_kafka import Consumer, KafkaException
import json
import redis


def read_config(path="client.properties"):
    config = {}
    with open(path, "r") as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                config[k.strip()] = v.strip()
    return config

# Function to clean the  data for Redis
def clean_data_for_redis(data):
    """Remove None values and convert non-serializable types to strings"""
    cleaned = {}
    for key, value in data.items():
        if value is not None:
            # Convert complex types to JSON strings if needed
            if isinstance(value, (dict, list)):
                cleaned[key] = json.dumps(value)
            else:
                cleaned[key] = str(value)
    return cleaned


redis_client = redis.Redis(
    host="clustercfg.formula1.ppjruj.memorydb.ap-south-1.amazonaws.com",
    port=6379,
    ssl=True,
    decode_responses=True
)

# need to FLUSH MemoryDB before start
print("Connecting to MemoryDB...")
try:
    redis_client.ping()
    keys_before = redis_client.dbsize()
    print(f"Keys in MemoryDB before flush: {keys_before}")
    
    # Flushing  all data
    redis_client.flushall()
    
    keys_after = redis_client.dbsize()
    print(f"✓ MemoryDB flushed! Keys remaining: {keys_after}")
    print("Starting fresh with clean database...")
    
except redis.ConnectionError as e:
    print(f"✗ Failed to connect to MemoryDB: {e}")
    exit(1)
except Exception as e:
    print(f"✗ Error flushing MemoryDB: {e}")
    exit(1)

# Kafka setup
consumer_config = read_config()
consumer_config.update({
    "group.id": "f1-consumer-group",
    "auto.offset.reset": "latest"
})

topics = [
    "telemetry", "rcm", "teamradio", "trackstatus",
    "sess_status", "currenttyres", "lapcount", "timedata", "tlarcm", "weatherdata"
]

consumer = Consumer(consumer_config)
consumer.subscribe(topics)

print("Kafka consumer started and writing to MemoryDB...")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
            
        if msg.error():
            raise KafkaException(msg.error())
        
        topic = msg.topic()
        
        try:
            data = json.loads(msg.value().decode("utf-8"))
        except json.JSONDecodeError as e:
            print(f"JSON decode error for topic {topic}: {e}")
            continue
        
        driver_no = data.get("DriverNo")
        if not driver_no:
            print(f"Skipping message from {topic}: no DriverNo field")
            continue
        

        cleaned_data = clean_data_for_redis(data)
        
        if not cleaned_data:
            print(f"Skipping message from {topic}: no valid data after cleaning")
            continue
        
        try:
            # Write latest per-driver telemetry
            redis_client.hset(f"latest:{topic}:{driver_no}", mapping=cleaned_data)
            print(f"[{topic}] → latest:{topic}:{driver_no} ({len(cleaned_data)} fields)")
            
        except redis.RedisError as e:
            print(f"Redis error for {topic}:{driver_no}: {e}")
            continue
          
except KeyboardInterrupt:
    print("Stopping consumer...")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    consumer.close()
    print("Consumer closed.")
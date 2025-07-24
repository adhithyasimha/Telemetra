from confluent_kafka import Consumer, KafkaException
import json
import sys

# Load config
def read_config(path="backend/kafka_ingres/client.properties"):
    config = {}
    with open(path, "r") as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                config[k.strip()] = v.strip()
    return config

# Set group.id and auto.offset.reset
consumer_config = read_config()
consumer_config.update({
    "group.id": "f1-consumer-group",
    "auto.offset.reset": "latest"  # or "earliest" for all data
})

# Kafka topics to consume
topics = [
    "position", "telemetry", "rcm", "teamradio", "trackstatus",
    "sess_status", "currenttyres", "lapcount", "timedata", "tlarcm", "weatherdata"
]

# Initialize consumer
consumer = Consumer(consumer_config)
consumer.subscribe(topics)

print("🚦 Kafka consumer started...")

try:
    while True:
        msg = consumer.poll(1.0)  # timeout in seconds
        if msg is None:
            continue
        if msg.error():
            raise KafkaException(msg.error())

        topic = msg.topic()
        data = json.loads(msg.value().decode("utf-8"))
        print(f"[{topic}] {data}")

        # TODO: Save to memory/db, serve via API, or push to S3 etc.

except KeyboardInterrupt:
    print("👋 Stopping consumer...")

finally:
    consumer.close()

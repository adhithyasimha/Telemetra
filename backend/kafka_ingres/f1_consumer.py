from confluent_kafka import Consumer, KafkaException
import json
import sys

# Load config
def read_config(path="client.properties"):
    config = {}
    with open(path, "r") as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                config[k.strip()] = v.strip()
    return config

consumer_config = read_config()
consumer_config.update({
    "group.id": "f1-consumer-group",
    "auto.offset.reset": "latest"  
})

# Kafka topics to consume
topics = [
    "telemetry", "rcm", "teamradio", "trackstatus",
    "sess_status", "currenttyres", "lapcount", "timedata", "tlarcm", "weatherdata"
]

# Initialize consumer
consumer = Consumer(consumer_config)
consumer.subscribe(topics)

print("🚦 Kafka consumer started...")

try:
    while True:
        msg = consumer.poll(1.0) 
        if msg is None:
            continue
        if msg.error():
            raise KafkaException(msg.error())

        topic = msg.topic()
        data = json.loads(msg.value().decode("utf-8"))
        print(f"[{topic}] {data}")

        # TODO: 

except KeyboardInterrupt:
    print("Stopping consumer...")

finally:
    consumer.close()

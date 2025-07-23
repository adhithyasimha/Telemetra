from livef1.adapters.realtime_client import RealF1Client
from confluent_kafka import Producer
import asyncio
import json
import datetime

# Read Kafka config from properties file
def read_config(path="client.properties"):
    config = {}
    with open(path, "r") as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                config[k.strip()] = v.strip()
    return config

# Kafka producer setup
kafka_config = read_config()
producer = Producer(kafka_config)

# LiveF1 topics → Confluent Kafka topics (must match)
topic_mapping = {
    "CurrentTyres": "currenttyres",
    "Heartbeat": "heartbeat",
    "LapCount": "lapcount",
    "Position.z": "position",
    "RaceControlMessages": "rcm",
    "SessionStatus": "sess_status",
    "TeamRadio": "teamradio",
    "CarData.z": "telemetry",
    "TimingData": "timedata",
    "TlaRcm": "tlarcm",
    "TrackStatus": "trackstatus",
    "WeatherData": "weatherdata"
}

# Initialize LiveF1 client
client = RealF1Client(
    topics=list(topic_mapping.keys()),  # LiveF1 data sources
    log_file_name="livef1_session.json"  # optional local log
)

# Generic handler for all topics
@client.callback("kafka_forwarder")
async def send_to_kafka(records):
    for topic_key, data in records.items():
        kafka_topic = topic_mapping.get(topic_key)
        if kafka_topic and data:
            for record in data:
                message = json.dumps(record)
                producer.produce(
                    topic=kafka_topic,
                    key=str(datetime.datetime.utcnow().timestamp()),
                    value=message
                )
                print(f"[{kafka_topic}] {message}")
    producer.flush()

# Run LiveF1 client
if __name__ == "__main__":
    client.run()

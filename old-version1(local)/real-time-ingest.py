import asyncio
from livef1.adapters import RealF1Client
from kafka import KafkaProducer
import json

# Kafka Producer Initialization
producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# Initialize clients for each data type
session_info = RealF1Client(topics=["SessionInfo"])
telemetry = RealF1Client(topics=["CarData.z"])
track_status = RealF1Client(topics=["TrackStatus"])
session_status = RealF1Client(topics=["SessionStatus"])
timing_data_f1 = RealF1Client(topics=["TimingDataF1"])
position = RealF1Client(topics=["Position.z"])
weather_data = RealF1Client(topics=["WeatherData"])
team_radio = RealF1Client(topics=["TeamRadio"])
race_control_messages = RealF1Client(topics=["RaceControlMessages"])
heartbeat = RealF1Client(topics=["Heartbeat"])
driver_list = RealF1Client(topics=["DriverList"])

# General Kafka sender
async def send_to_kafka(topic, records):
    for record in records:
        producer.send(topic, record)
        print(f"Sent to {topic}: {record}")

# Topic-specific Kafka sender
async def process_and_send(topic_name, records, kafka_topic):
    topic_data = records.get(topic_name)
    if topic_data:
        for record in topic_data:
            producer.send(kafka_topic, record)
            print(f"Sent to {kafka_topic}: {record}")

# Attach callbacks with topic extraction
session_info.callback("session_info_handler")(lambda records: asyncio.create_task(process_and_send("SessionInfo", records, "session_info")))
track_status.callback("track_status_handler")(lambda records: asyncio.create_task(process_and_send("TrackStatus", records, "track_status")))
session_status.callback("session_status_handler")(lambda records: asyncio.create_task(process_and_send("SessionStatus", records, "session_status")))
timing_data_f1.callback("timing_data_f1_handler")(lambda records: asyncio.create_task(process_and_send("TimingDataF1", records, "timing_data_f1")))
position.callback("position_handler")(lambda records: asyncio.create_task(process_and_send("Position.z", records, "position")))
weather_data.callback("weather_data_handler")(lambda records: asyncio.create_task(process_and_send("WeatherData", records, "weather_data")))
team_radio.callback("team_radio_handler")(lambda records: asyncio.create_task(process_and_send("TeamRadio", records, "team_radio")))
race_control_messages.callback("race_control_messages_handler")(lambda records: asyncio.create_task(process_and_send("RaceControlMessages", records, "race_control_messages")))
heartbeat.callback("heartbeat_handler")(lambda records: asyncio.create_task(process_and_send("Heartbeat", records, "heartbeat")))
driver_list.callback("driver_list_handler")(lambda records: asyncio.create_task(process_and_send("DriverList", records, "driver_list")))
telemetry.callback("telemetry_handler")(lambda records: asyncio.create_task(process_and_send("CarData.z", records, "telemetry")))

# Run all clients concurrently
async def main():
    await asyncio.gather(
        session_info._async_run(),
        track_status._async_run(),
        session_status._async_run(),
        timing_data_f1._async_run(),
        position._async_run(),
        weather_data._async_run(),
        team_radio._async_run(),
        race_control_messages._async_run(),
        heartbeat._async_run(),
        # driver_list._async_run(),
        telemetry._async_run()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopping F1 data collection...")

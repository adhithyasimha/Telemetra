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

tyre_stint_series = RealF1Client(topics=["TyreStintSeries"])
driver_list = RealF1Client(topics=["DriverList"])

# Define callback function for sending data to Kafka
async def send_to_kafka(topic, records):
    for record in records:
        producer.send(topic, record)
        print(f"Sent to {topic}: {record}")

# Attach callbacks
session_info.callback("session_info_handler")(lambda records: asyncio.create_task(send_to_kafka("session_info", records)))
track_status.callback("track_status_handler")(lambda records: asyncio.create_task(send_to_kafka("track_status", records)))
session_status.callback("session_status_handler")(lambda records: asyncio.create_task(send_to_kafka("session_status", records)))
timing_data_f1.callback("timing_data_f1_handler")(lambda records: asyncio.create_task(send_to_kafka("timing_data_f1", records)))
position.callback("position_handler")(lambda records: asyncio.create_task(send_to_kafka("position", records)))
weather_data.callback("weather_data_handler")(lambda records: asyncio.create_task(send_to_kafka("weather_data", records)))
team_radio.callback("team_radio_handler")(lambda records: asyncio.create_task(send_to_kafka("team_radio", records)))
race_control_messages.callback("race_control_messages_handler")(lambda records: asyncio.create_task(send_to_kafka("race_control_messages", records)))
heartbeat.callback("heartbeat_handler")(lambda records: asyncio.create_task(send_to_kafka("heartbeat", records)))
tyre_stint_series.callback("tyre_stint_series_handler")(lambda records: asyncio.create_task(send_to_kafka("tyre_stint_series", records)))
driver_list.callback("driver_list_handler")(lambda records: asyncio.create_task(send_to_kafka("driver_list", records)))
telemetry.callback("telemetry_handler")(lambda records: asyncio.create_task(send_to_kafka("telemetry", records)))

# Main function to run all clients concurrently
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
        tyre_stint_series._async_run(),
        driver_list._async_run(),
        telemetry._async_run()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopping F1 data collection...")

import asyncio
from livef1.adapters import RealF1Client

# Initialize clients for each data type
session_info = RealF1Client(
    topics=["SessionInfo"],
    log_file_name="session_info.json"
)

track_status = RealF1Client(
    topics=["TrackStatus"],
    log_file_name="track_status.json"
)

session_status = RealF1Client(
    topics=["SessionStatus"],
    log_file_name="session_status.json"
)

timing_data_f1 = RealF1Client(
    topics=["TimingDataF1"],
    log_file_name="timing_data_f1.json"
)

position = RealF1Client(
    topics=["Position.z"],
    log_file_name="position.json"
)

weather_data = RealF1Client(
    topics=["WeatherData"],
    log_file_name="weather_data.json"
)

team_radio = RealF1Client(
    topics=["TeamRadio"],
    log_file_name="team_radio.json"
)

race_control_messages = RealF1Client(
    topics=["RaceControlMessages"],
    log_file_name="race_control_messages.json"
)

heartbeat = RealF1Client(
    topics=["Heartbeat"],
    log_file_name="heartbeat.json"
)

lap_series = RealF1Client(
    topics=["LapSeries"],
    log_file_name="lap_series.json"
)

tyre_stint_series = RealF1Client(
    topics=["TyreStintSeries"],
    log_file_name="tyre_stint_series.json"
)



driver_list = RealF1Client(
    topics=["DriverList"],
    log_file_name="driver_list.json"
)

# Define callback function for handling data
async def handle_data(client_name, records):
    for record in records:
        print(f"{client_name}: {record}")

# Attach callbacks
session_info.callback("session_info_handler")(lambda records: asyncio.create_task(handle_data("SessionInfo", records)))
track_status.callback("track_status_handler")(lambda records: asyncio.create_task(handle_data("TrackStatus", records)))
session_status.callback("session_status_handler")(lambda records: asyncio.create_task(handle_data("SessionStatus", records)))
timing_data_f1.callback("timing_data_f1_handler")(lambda records: asyncio.create_task(handle_data("TimingDataF1", records)))
position.callback("position_handler")(lambda records: asyncio.create_task(handle_data("Position", records)))
weather_data.callback("weather_data_handler")(lambda records: asyncio.create_task(handle_data("WeatherData", records)))
team_radio.callback("team_radio_handler")(lambda records: asyncio.create_task(handle_data("TeamRadio", records)))
race_control_messages.callback("race_control_messages_handler")(lambda records: asyncio.create_task(handle_data("RaceControlMessages", records)))
heartbeat.callback("heartbeat_handler")(lambda records: asyncio.create_task(handle_data("Heartbeat", records)))
lap_series.callback("lap_series_handler")(lambda records: asyncio.create_task(handle_data("LapSeries", records)))
tyre_stint_series.callback("tyre_stint_series_handler")(lambda records: asyncio.create_task(handle_data("TyreStintSeries", records)))
driver_list.callback("driver_list_handler")(lambda records: asyncio.create_task(handle_data("DriverList", records)))

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
        lap_series._async_run(),
        tyre_stint_series._async_run(),
        driver_list._async_run()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopping F1 data collection...")

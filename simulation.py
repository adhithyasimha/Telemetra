import requests
import time
import json

# Base URL for Open F1 API
API_BASE_URL = "https://api.openf1.org/v1"

# Get live race data (car data, driver positions, etc.)
def get_live_race_data(meeting_key, session_key):
    url = f"{API_BASE_URL}/car_data?meeting_key={meeting_key}&session_key={session_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching race data: {response.status_code}")
        return None

# Get weather data (air temperature, track temperature, humidity)
def get_weather_data(meeting_key, session_key):
    url = f"{API_BASE_URL}/weather?meeting_key={meeting_key}&session_key={session_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        weather_data = response.json()
        # Assuming the weather data is a list, and we're taking the first entry (latest data)
        if isinstance(weather_data, list) and len(weather_data) > 0:
            return weather_data[0]  # Extract the latest weather data
        else:
            print("No weather data available")
            return None
    else:
        print(f"Error fetching weather data: {response.status_code}")
        return None

# Get radio communication for driver during the race
def get_radio_data(meeting_key, session_key):
    url = f"{API_BASE_URL}/team_radio?meeting_key={meeting_key}&session_key={session_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching radio data: {response.status_code}")
        return None

# Get lap details for a specific driver
def get_lap_data(meeting_key, session_key, driver_number, lap_number):
    url = f"{API_BASE_URL}/laps?meeting_key={meeting_key}&session_key={session_key}&driver_number={driver_number}&lap_number={lap_number}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching lap data: {response.status_code}")
        return None

# Simulate real-time updates for the race
def simulate_race(meeting_key, session_key, driver_number, total_laps=10):
    print(f"Starting race simulation for meeting {meeting_key} session {session_key}...\n")
    
    # Simulating race lap by lap
    for lap in range(1, total_laps + 1):
        print(f"\n--- Lap {lap} ---")
        
        # Get real-time race data
        race_data = get_live_race_data(meeting_key, session_key)
        weather_data = get_weather_data(meeting_key, session_key)
        radio_data = get_radio_data(meeting_key, session_key)
        lap_data = get_lap_data(meeting_key, session_key, driver_number, lap)

        # Process and display driver data for each lap
        if race_data:
            for driver in race_data["drivers"]:
                driver_number = driver.get("driver_number", "Unknown")
                position = driver.get("position", "N/A")
                speed = driver.get("speed", "N/A")
                throttle = driver.get("throttle", "N/A")
                brake = driver.get("brake", "N/A")
                gear = driver.get("n_gear", "N/A")
                rpm = driver.get("rpm", "N/A")
                
                # Display the driver's real-time data
                print(f"Driver {driver_number} - Position: {position}, Speed: {speed} km/h, Throttle: {throttle}%, Brake: {brake}%, Gear: {gear}, RPM: {rpm}")
        
        # Process and display lap data
        if lap_data:
            lap_duration = lap_data[0].get("lap_duration", "N/A")
            sector_1 = lap_data[0].get("duration_sector_1", "N/A")
            sector_2 = lap_data[0].get("duration_sector_2", "N/A")
            sector_3 = lap_data[0].get("duration_sector_3", "N/A")
            print(f"Lap Duration: {lap_duration}s, Sector 1: {sector_1}s, Sector 2: {sector_2}s, Sector 3: {sector_3}s")

        # Display weather data
        if weather_data:
            air_temp = weather_data.get("air_temperature", "N/A")
            track_temp = weather_data.get("track_temperature", "N/A")
            humidity = weather_data.get("humidity", "N/A")
            rainfall = weather_data.get("rainfall", "N/A")
            print(f"Weather - Air Temp: {air_temp}°C, Track Temp: {track_temp}°C, Humidity: {humidity}%, Rainfall: {'Yes' if rainfall else 'No'}")
        
        # Display radio message if available
        if radio_data:
            for message in radio_data.get("messages", []):
                message_text = message.get("message", "No message")
                print(f"Radio Message: {message_text}")
        
        # Simulate the passage of time (one second per lap for real-time feel)
        time.sleep(1)

# Define the meeting_key (use "latest" for the current session) and session_key
meeting_key = "latest"  # Use "latest" to refer to the current race session
session_key = "latest"  # Use "latest" for the latest session data
driver_number = 1  # Change this to the driver's number you want to simulate for

# Start the race simulation
simulate_race(meeting_key, session_key, driver_number, total_laps=5)

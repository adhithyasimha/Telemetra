import requests
import os
import time

# API endpoint and parameters
url = "https://api.openf1.org/v1/team_radio"
params = {
    "session_key": "9165",  # Race session for 2023 Singapore GP
    "driver_number": 55     # Carlos Sainz's driver number
}

# Create a directory to store the downloaded files
output_folder = "Sainz_Singapore_GP_Race_Radio"
os.makedirs(output_folder, exist_ok=True)

# Fetch data from the API
try:
    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise an HTTPError for bad responses
    data = response.json()

    # Download each recording
    for message in data:
        recording_url = message["recording_url"]
        file_name = os.path.join(output_folder, os.path.basename(recording_url))
        
        print(f"Downloading: {file_name}")
        
        try:
            audio_response = requests.get(recording_url, stream=True)
            audio_response.raise_for_status()  # Raise an HTTPError for bad responses
            
            # Save the audio file
            with open(file_name, "wb") as file:
                for chunk in audio_response.iter_content(chunk_size=1024):
                    file.write(chunk)
            print(f"Downloaded: {file_name}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {recording_url}: {e}")
        
        # Respectful rate-limiting (optional)
        time.sleep(1)

except requests.exceptions.RequestException as e:
    print(f"Failed to fetch data from the API: {e}")

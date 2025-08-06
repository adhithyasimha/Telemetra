import requests
from datetime import datetime
from typing import TypedDict, List, Dict, Any, Optional
import json
import matplotlib.pyplot as plt


class TrackPosition(TypedDict):
    x: float
    y: float


class Corner(TypedDict):
    angle: float
    length: float
    number: int
    trackPosition: TrackPosition


class CandidateLap(TypedDict):
    driverNumber: str
    lapNumber: int
    lapStartDate: str
    lapStartSessionTime: float
    lapTime: float
    session: str
    sessionStartTime: float


class Map(TypedDict):
    corners: List[Corner]
    marshalLights: List[Corner]
    marshalSectors: List[Corner]
    candidateLap: CandidateLap
    circuitKey: int
    circuitName: str
    countryIocCode: str
    countryKey: int
    countryName: str
    location: str
    meetingKey: str
    meetingName: str
    meetingOfficialName: str
    raceDate: str
    rotation: float
    round: int
    trackPositionTime: List[float]
    x: List[float]
    y: List[float]
    year: int


def fetch_map(circuit_key: int, year: int = None) -> Map:
    """Fetch F1 track map data for a given circuit key and year."""
    if year is None:
        year = datetime.now().year
        
    # Try current year first, then fallback to previous years
    years_to_try = [year, year-1, year-2, 2024, 2023, 2022]
    
    for try_year in years_to_try:
        try:
            url = f"https://api.multiviewer.app/api/v1/circuits/{circuit_key}/{try_year}"
            print(f"Trying URL: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, timeout=10, headers=headers)
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"Successfully fetched data for year {try_year}")
                return response.json()
            elif response.status_code == 403:
                print(f"403 Forbidden for year {try_year} - trying next year")
                continue
            elif response.status_code == 404:
                print(f"404 Not Found for year {try_year} - trying next year")
                continue
            else:
                response.raise_for_status()
                
        except requests.RequestException as e:
            print(f"Error fetching map for year {try_year}: {e}")
            continue
    
    print("Failed to fetch data for all attempted years")
    return None


def process_session_data(session_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process F1 session data and extract relevant information."""
    processed_data = {
        "event_name": session_data.get("Meeting_OfficialName"),
        "circuit_key": session_data.get("Meeting_Circuit_Key"),
        "location": session_data.get("Meeting_Location"),
        "country": session_data.get("Meeting_Country_Name"),
        "session_type": session_data.get("Type"),
        "start_date": session_data.get("StartDate"),
        "end_date": session_data.get("EndDate")
    }
    
    # Extract year from the start date
    if processed_data["start_date"]:
        try:
            processed_data["year"] = int(processed_data["start_date"][:4])
        except (ValueError, TypeError):
            processed_data["year"] = datetime.now().year
            
    return processed_data


def plot_track_map(map_data: Map) -> None:
    """Plot the track map using matplotlib."""
    plt.figure(figsize=(10, 8))
    
    # Plot the track outline
    plt.plot(map_data["x"], map_data["y"], 'k-', linewidth=3)
    
    # Add corner numbers
    for corner in map_data["corners"]:
        pos = corner["trackPosition"]
        plt.text(pos["x"], pos["y"], str(corner["number"]), 
                 fontsize=8, ha='center', va='center',
                 bbox=dict(facecolor='white', alpha=0.7))
    
    # Add title and information
    plt.title(f"{map_data['circuitName']} - {map_data['countryName']}")
    plt.figtext(0.05, 0.02, f"Race: {map_data['meetingOfficialName']}")
    plt.figtext(0.05, 0.01, f"Date: {map_data['raceDate']}")
    
    # Remove axes
    plt.axis('off')
    plt.axis('equal')  # Ensure the track has correct proportions
    
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # Example session data from the 2025 Australian Grand Prix qualifying
    session_data = {
        'SessionKey': None, 
        'timestamp': None, 
        'Meeting_Key': 1254, 
        'Meeting_Name': 'Australian Grand Prix', 
        'Meeting_OfficialName': 'FORMULA 1 LOUIS VUITTON AUSTRALIAN GRAND PRIX 2025', 
        'Meeting_Location': 'Melbourne', 
        'Meeting_Number': 1, 
        'Meeting_Country_Key': 5, 
        'Meeting_Country_Code': 'AUS', 
        'Meeting_Country_Name': 'Australia', 
        'Meeting_Circuit_Key': 10, 
        'Meeting_Circuit_ShortName': 'Melbourne', 
        'ArchiveStatus_Status': 'Generating', 
        'Key': 9689, 
        'Type': 'Qualifying', 
        'Name': 'Qualifying', 
        'StartDate': '2025-03-15T16:00:00', 
        'EndDate': '2025-03-15T17:00:00', 
        'GmtOffset': '11:00:00', 
        'Path': '2025/2025-03-16_Australian_Grand_Prix/2025-03-15_Qualifying/', 
        '_kf': True
    }
    
    # Process the session data
    processed_data = process_session_data(session_data)
    print(f"Processing data for {processed_data['event_name']}")
    print(f"Circuit key: {processed_data['circuit_key']}")
    print(f"Year: {processed_data['year']}")
    
    # Fetch the map data
    print(f"\nAttempting to fetch map data...")
    map_data = fetch_map(processed_data['circuit_key'], processed_data['year'])
    
    if map_data:
        print("\nTrack Information:")
        print(f"Circuit: {map_data['circuitName']}")
        print(f"Location: {map_data['location']}, {map_data['countryName']}")
        print(f"Number of corners: {len(map_data['corners'])}")
        
        # Plot the track map
        try:
            plot_track_map(map_data)
            print("\nTrack map displayed. Close the window to continue.")
        except Exception as e:
            print(f"\nCouldn't display track map: {e}")
            print("To view the track, make sure matplotlib is installed:")
            print("/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 -m pip install matplotlib")
    else:
        print("\nFailed to fetch track map data.")
        print("Possible reasons:")
        print("1. The API might require authentication")
        print("2. The circuit key (10) might not be available for recent years")
        print("3. The API might be rate-limited or temporarily unavailable")
        print("\nTry visiting the API URL manually in a browser:")
        print("https://api.multiviewer.app/api/v1/circuits/10/2024")
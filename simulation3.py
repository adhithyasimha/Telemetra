import random
import time
from dataclasses import dataclass, field
from typing import List, Dict
from enum import Enum
import os

def clear_console():
    os.system('clear')

class Weather(Enum):
    DRY = "Dry"
    LIGHT_RAIN = "Light Rain"
    HEAVY_RAIN = "Heavy Rain"

class TireCompound:
    SOFT = {"name": "Soft", "max_laps": 20, "pace_delta": -1.2, "wear_rate": 1.5}
    MEDIUM = {"name": "Medium", "max_laps": 25, "pace_delta": 0, "wear_rate": 1.0}
    HARD = {"name": "Hard", "max_laps": 30, "pace_delta": 0.8, "wear_rate": 0.7}

class TeamPerformance:
    FACTORS = {
        "Red Bull": {"S1": 0.97, "S2": 0.96, "S3": 0.97, "base": 0.95},
        "Mercedes": {"S1": 0.98, "S2": 0.97, "S3": 0.98, "base": 0.96},
        "Ferrari": {"S1": 0.98, "S2": 0.98, "S3": 0.97, "base": 0.96},
        "McLaren": {"S1": 0.99, "S2": 0.99, "S3": 0.99, "base": 0.97},
        "Aston Martin": {"S1": 1.00, "S2": 1.00, "S3": 1.00, "base": 0.98},
        "Alpine": {"S1": 1.01, "S2": 1.01, "S3": 1.01, "base": 0.99},
        "Williams": {"S1": 1.02, "S2": 1.02, "S3": 1.02, "base": 1.00},
        "AlphaTauri": {"S1": 1.03, "S2": 1.03, "S3": 1.03, "base": 1.01},
        "Alfa Romeo": {"S1": 1.04, "S2": 1.04, "S3": 1.04, "base": 1.02},
        "Haas": {"S1": 1.05, "S2": 1.05, "S3": 1.05, "base": 1.03}
    }

@dataclass
class Driver:
    name: str
    number: int
    team: str
    skill: float
    wet_skill: float
    aggression: float
    tire_management: float

@dataclass
class Car:
    driver: Driver
    position: int = 0
    gap_to_leader: float = 0.0
    current_tire: Dict = field(default_factory=lambda: TireCompound.SOFT)
    tire_age: int = 0
    sector1_time: float = 0.0
    sector2_time: float = 0.0
    sector3_time: float = 0.0
    last_lap: float = 0.0
    total_race_time: float = 0.0
    pit_timer: float = 0.0
    pit_stops: int = 0
    in_pit: bool = False
    dnf: bool = False
    dnf_reason: str = ""
    drs_available: bool = False

class F1Simulator:
    def __init__(self):
        self.circuit_name = "Marina Bay Street Circuit"
        self.total_laps = 61
        self.current_lap = 0
        self.safety_car = False
        self.safety_car_laps = 0
        self.weather = Weather.DRY
        self.base_laptime = 98.0
        self.team_pit_times = {
            "Red Bull": 2.0,
            "Mercedes": 2.2,
            "Ferrari": 2.3,
            "McLaren": 2.4,
            "Aston Martin": 2.5,
            "Alpine": 2.6,
            "Williams": 2.7,
            "AlphaTauri": 2.8,
            "Alfa Romeo": 2.9,
            "Haas": 3.0
        }
        
        self.drivers = [
            Driver("Max Verstappen", 1, "Red Bull", 0.98, 0.95, 0.90, 0.92),
            Driver("Sergio Perez", 11, "Red Bull", 0.94, 0.88, 0.85, 0.90),
            Driver("Lewis Hamilton", 44, "Mercedes", 0.97, 0.96, 0.85, 0.94),
            Driver("George Russell", 63, "Mercedes", 0.95, 0.92, 0.87, 0.93),
            Driver("Charles Leclerc", 16, "Ferrari", 0.96, 0.93, 0.89, 0.91),
            Driver("Carlos Sainz", 55, "Ferrari", 0.94, 0.91, 0.86, 0.90),
            Driver("Lando Norris", 4, "McLaren", 0.93, 0.90, 0.88, 0.89),
            Driver("Oscar Piastri", 81, "McLaren", 0.91, 0.88, 0.84, 0.87),
            Driver("Fernando Alonso", 14, "Aston Martin", 0.95, 0.94, 0.89, 0.93),
            Driver("Lance Stroll", 18, "Aston Martin", 0.90, 0.87, 0.85, 0.86),
            Driver("Pierre Gasly", 10, "Alpine", 0.92, 0.89, 0.86, 0.88),
            Driver("Esteban Ocon", 31, "Alpine", 0.91, 0.88, 0.85, 0.87),
            Driver("Alex Albon", 23, "Williams", 0.90, 0.87, 0.84, 0.86),
            Driver("Logan Sargeant", 2, "Williams", 0.88, 0.85, 0.83, 0.84),
            Driver("Yuki Tsunoda", 22, "AlphaTauri", 0.89, 0.86, 0.85, 0.85),
            Driver("Daniel Ricciardo", 3, "AlphaTauri", 0.91, 0.88, 0.86, 0.88),
            Driver("Valtteri Bottas", 77, "Alfa Romeo", 0.90, 0.87, 0.84, 0.86),
            Driver("Zhou Guanyu", 24, "Alfa Romeo", 0.89, 0.86, 0.83, 0.85),
            Driver("Kevin Magnussen", 20, "Haas", 0.89, 0.86, 0.85, 0.84),
            Driver("Nico Hulkenberg", 27, "Haas", 0.90, 0.87, 0.84, 0.85)
        ]
        
        self.cars = [Car(driver) for driver in self.drivers]

    def calculate_sector_time(self, car: Car, sector: int) -> float:
        base_sector = self.base_laptime / 3
        team_factor = TeamPerformance.FACTORS[car.driver.team][f"S{sector}"]
        skill_factor = 1 - ((car.driver.skill - 0.8) * 0.5)
        tire_delta = car.current_tire["pace_delta"] / 3
        tire_deg = (car.tire_age / car.current_tire["max_laps"]) * 0.7
        
        if car.in_pit and sector == 3:
            return base_sector + self.team_pit_times[car.driver.team]
            
        random_factor = random.uniform(-0.3, 0.3) * car.driver.skill
        return (base_sector * team_factor * skill_factor) + tire_delta + tire_deg + random_factor

    def handle_pit_stop(self, car: Car):
        if car.pit_timer >= self.team_pit_times[car.driver.team]:
            car.in_pit = False
            car.pit_timer = 0
            car.pit_stops += 1
            available_compounds = [TireCompound.SOFT, TireCompound.MEDIUM, TireCompound.HARD]
            car.current_tire = random.choice([c for c in available_compounds if c != car.current_tire])
            car.tire_age = 0
        else:
            car.pit_timer += 1

    def run_race(self):
        print(f"\nRace Start - {self.circuit_name}")
        
        for lap in range(1, self.total_laps + 1):
            self.current_lap = lap
            print(f"\nLap {lap}/{self.total_laps}")
            print(f"Weather: {self.weather.value}")
            
            for sector in range(1, 4):
                print(f"\nSector {sector}:")
                for car in self.cars:  # Process all cars, including DNF
                    if not car.dnf:
                        sector_time = self.calculate_sector_time(car, sector)
                        if sector == 1:
                            car.sector1_time = sector_time
                        elif sector == 2:
                            car.sector2_time = sector_time
                        else:
                            car.sector3_time = sector_time
                            car.last_lap = car.sector1_time + car.sector2_time + car.sector3_time
                            car.total_race_time += car.last_lap
                        
                        if car.in_pit:
                            self.handle_pit_stop(car)
                            
                        if random.random() < 0.005:  # DNF chance
                            car.dnf = True
                            car.dnf_reason = random.choice(["Engine", "Gearbox", "Collision", "Hydraulics"])
                            print(f"⚠️ DNF: {car.driver.name} - {car.dnf_reason}")
                
                # Display all cars
                print("\nPositions:")
                all_cars = sorted(self.cars, key=lambda x: float('inf') if x.dnf else x.total_race_time)
                leader_time = next((car.total_race_time for car in all_cars if not car.dnf), 0)
                
                for pos, car in enumerate(all_cars, 1):
                    status = f"DNF - {car.dnf_reason}" if car.dnf else ("IN PIT" if car.in_pit else car.current_tire["name"])
                    gap = "DNF" if car.dnf else f"+{car.total_race_time - leader_time:.3f}s"
                    sector_time = getattr(car, f"sector{sector}_time", 0.0)
                    print(f"{pos}. {car.driver.name:15} | S{sector}: {sector_time:.3f} | Gap: {gap} | {status} ({car.tire_age})")
                
                time.sleep(1)
            
            time.sleep(2)
            clear_console()

if __name__ == "__main__":
    sim = F1Simulator()
    sim.run_race()
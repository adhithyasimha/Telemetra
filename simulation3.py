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

@dataclass
class Driver:
    name: str
    number: int
    team: str
    skill: float
    wet_skill: float
    aggression: float
    tire_management: float
    preferred_strategy: List[Dict] = field(default_factory=list)

@dataclass
class Car:
    driver: Driver
    position: int = 0
    gap_to_leader: float = 0.0
    current_tire: Dict = field(default_factory=lambda: TireCompound.SOFT)
    tire_age: int = 0
    lap_time: float = 0.0
    last_lap: float = 0.0
    pit_stops: int = 0
    in_pit: bool = False
    pit_time_remaining: float = 0.0
    dnf: bool = False
    dnf_reason: str = ""
    total_race_time: float = 0.0
    gap_to_front: float = 0.0

class F1Simulator:
    def __init__(self):
        self.circuit_name = "Marina Bay Street Circuit"
        self.total_laps = 61
        self.current_lap = 0
        self.safety_car = False
        self.safety_car_laps = 0
        self.weather = Weather.DRY
        self.base_laptime = 98.0
        self.dnf_count = 0  # Track number of DNFs
        
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
        
        self.assign_strategies()
        self.cars = [Car(driver) for driver in self.drivers]
        self.initialize_race()

    def initialize_race(self):
        # Assign starting tires: Top 10 on Soft, others on Medium or Hard
        for i, car in enumerate(self.cars):
            if i < 10:
                car.current_tire = TireCompound.SOFT
            else:
                car.current_tire = random.choice([TireCompound.MEDIUM, TireCompound.HARD])
            car.tire_age = 0

    def assign_strategies(self):
        strategies = {
            "Red Bull": [TireCompound.SOFT, TireCompound.HARD],
            "Mercedes": [TireCompound.MEDIUM, TireCompound.HARD],
            "Ferrari": [TireCompound.SOFT, TireCompound.MEDIUM],
            "default": [TireCompound.MEDIUM, TireCompound.HARD]
        }
        for driver in self.drivers:
            driver.preferred_strategy = strategies.get(driver.team, strategies["default"])

    def calculate_lap_time(self, car: Car) -> float:
        base = self.base_laptime
        skill_factor = 1 - ((car.driver.skill - 0.8) * 0.5)
        tire_delta = car.current_tire["pace_delta"]
        tire_deg = (car.tire_age / car.current_tire["max_laps"]) * 2.0
        
        if self.safety_car:
            return base * 1.4
        if car.in_pit:
            return base + 23.0
            
        variation = random.uniform(-0.3, 0.3)
        final_time = (base * skill_factor) + tire_delta + tire_deg + variation
        
        return final_time

    def calculate_overtake_probability(self, car1: Car, car2: Car) -> float:
        if car1.position == 1:  # Race leader cannot overtake
            return 0.0
        if abs(car1.gap_to_front) < 1.0:
            pace_delta = car2.lap_time - car1.lap_time
            tire_advantage = car2.tire_age - car1.tire_age
            skill_factor = car1.driver.skill - car2.driver.skill
            return min(0.8, max(0.1, (pace_delta + tire_advantage/10 + skill_factor) * 0.3))
        return 0.0

    def handle_safety_car(self):
        if self.safety_car:
            self.safety_car_laps -= 1
            if self.safety_car_laps <= 0:
                self.safety_car = False
                print("\n🏁 Safety Car in this lap!")
            return True
        return False

    def ensure_team_tire_difference(self, car: Car):
        # Ensure teammates have different tires
        teammate = next((c for c in self.cars if c.driver.team == car.driver.team and c != car), None)
        if teammate and car.current_tire == teammate.current_tire:
            # Switch to the other available tire
            available_tires = [t for t in [TireCompound.SOFT, TireCompound.MEDIUM, TireCompound.HARD] if t != teammate.current_tire]
            car.current_tire = random.choice(available_tires)

    def run_race(self):
        print(f"\nRace Start - {self.circuit_name}")
        
        for lap in range(1, self.total_laps + 1):
            self.current_lap = lap
            print(f"\nLap {lap}/{self.total_laps}")
            print(f"Weather: {self.weather.value}")
            
            if self.handle_safety_car():
                continue
            
            for car in self.cars:
                if not car.dnf:
                    # Incident check (max 3 DNFs)
                    if self.dnf_count < 3 and random.random() < 0.01:
                        car.dnf = True
                        car.dnf_reason = "Crash"
                        self.dnf_count += 1
                        self.safety_car = True
                        self.safety_car_laps = 5
                        print(f"\n💥 Incident: {car.driver.name} - DNF ({car.dnf_reason})")
                        continue
                    
                    # Pit stop check
                    car.tire_age += 1
                    if car.tire_age >= car.current_tire["max_laps"]:
                        if not car.in_pit:
                            car.in_pit = True
                            car.pit_time_remaining = 1.5  # 1.5 seconds pit time
                            print(f"\n🔧 Pit Stop: {car.driver.name}")
                            # Assign tires based on team strategy
                            car.current_tire = car.driver.preferred_strategy[car.pit_stops % len(car.driver.preferred_strategy)]
                            self.ensure_team_tire_difference(car)
                            car.pit_stops += 1
                            car.tire_age = 0
                    
                    if car.in_pit:
                        car.pit_time_remaining -= 0.1  # Simulate pit time
                        if car.pit_time_remaining <= 0:
                            car.in_pit = False
                    
                    car.lap_time = self.calculate_lap_time(car)
                    car.total_race_time += car.lap_time
            
            # Overtaking
            for i, car in enumerate(self.cars[:-1]):
                if car.dnf:
                    continue
                next_car = self.cars[i+1]
                if not next_car.dnf:
                    if random.random() < self.calculate_overtake_probability(car, next_car):
                        car.position, next_car.position = next_car.position, car.position
                        print(f"\n⚡ Overtake: {car.driver.name} passes {next_car.driver.name}")
            
            # Display positions
            sorted_cars = sorted(self.cars, key=lambda x: x.total_race_time if not x.dnf else float('inf'))
            print("\nPositions:")
            leader_time = sorted_cars[0].total_race_time
            for pos, car in enumerate(sorted_cars, 1):
                gap = car.total_race_time - leader_time
                status = "DNF - " + car.dnf_reason if car.dnf else ("IN PIT" if car.in_pit else f"{car.current_tire['name']}")
                print(f"{pos}. {car.driver.name:15} | +{gap:.3f}s | {status} ({car.tire_age} laps)")
            
            time.sleep(2)
            clear_console()

if __name__ == "__main__":
    sim = F1Simulator()
    sim.run_race()
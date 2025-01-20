import random
import time
from dataclasses import dataclass, field
from typing import Dict
from enum import Enum
import os

def clear_console():
    os.system('clear')

class RaceStatus(Enum):
    GREEN = "\U0001F7E2 Racing"
    YELLOW = "\U0001F7E1 Yellow Flag"
    SC = "\U0001F6A8 Safety Car"
    VSC = "\U0001F7E1 Virtual Safety Car"
    RED = "\U0001F534 Red Flag"

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
    def update_status(self) -> str:
        if self.dnf:
            return f"DNF ({self.dnf_reason})"
        if self.in_pit:
            return "In Pit"
        return "Running"

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
    dnf_lap: int = 0
    race_status: str = "Running"

class F1Simulator:
    def __init__(self):
        self.circuit_name = "Marina Bay Street Circuit"
        self.total_laps = 61
        self.current_lap = 0
        self.race_status = RaceStatus.GREEN
        self.safety_car = False
        self.safety_car_laps = 0
        self.weather = Weather.DRY
        self.base_laptime = 98.0
        self.dnf_count = 0
        self.max_dnf = 2
        self.drs_enabled = False

        self.team_pit_times = {
            "Red Bull": 1.5,
            "Mercedes": 1.5,
            "Ferrari": 1.5,
            "McLaren": 1.5,
            "Aston Martin": 1.5,
            "Alpine": 1.5,
            "Williams": 1.5,
            "AlphaTauri": 1.5,
            "Alfa Romeo": 1.5,
            "Haas": 1.5
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
        self.initialize_race()

    def initialize_race(self):
        for i, car in enumerate(self.cars):
            car.position = i + 1
            if i < 10:
                car.current_tire = TireCompound.SOFT
            else:
                car.current_tire = random.choice([TireCompound.MEDIUM, TireCompound.HARD])

    def display_race_banner(self):
        print("\n" + "=" * 80)
        print(f"Lap {self.current_lap}/{self.total_laps} | {self.race_status.value} | {self.weather.value}")
        if self.safety_car:
            print("\U0001F6A8 Safety Car Period - Delta Time: +1.5s")
        if self.drs_enabled:
            print("\U0001F6A8 DRS Enabled")
        print("=" * 80 + "\n")

    def calculate_sector_time(self, car: Car, sector: int) -> float:
        base_sector = self.base_laptime / 3
        team_factor = TeamPerformance.FACTORS[car.driver.team][f"S{sector}"]
        skill_factor = 1 - ((car.driver.skill - 0.8) * 0.5)
        tire_delta = car.current_tire["pace_delta"] / 3
        tire_deg = (car.tire_age / car.current_tire["max_laps"]) * 0.7

        if self.safety_car:
            return base_sector * 1.4

        if car.in_pit and sector == 3:
            return base_sector + self.team_pit_times[car.driver.team]

        random_factor = random.uniform(-0.2, 0.2) * car.driver.skill
        return (base_sector * team_factor * skill_factor) + tire_delta + tire_deg + random_factor

    def handle_pit_stop(self, car: Car):
        if car.pit_timer >= 25:  # Total pit time (including entry and exit)
            car.in_pit = False
            car.pit_timer = 0
            car.pit_stops += 1

            # Strategic tire choice
            if self.current_lap > (self.total_laps - 15):
                car.current_tire = TireCompound.SOFT
            elif car.position <= 6:
                car.current_tire = TireCompound.MEDIUM
            else:
                car.current_tire = TireCompound.HARD

            car.tire_age = 0
        else:
            car.pit_timer += 1

    def check_incidents(self, car: Car) -> bool:
        if self.dnf_count >= self.max_dnf or car.dnf or random.random() > 0.001:
            return False

        car.dnf = True
        car.dnf_lap = self.current_lap
        car.dnf_reason = random.choice(["Engine", "Gearbox", "Collision", "Hydraulics"])
        self.dnf_count += 1

        if not self.safety_car and random.random() < 0.7:
            self.safety_car = True
            self.safety_car_laps = 5
            self.race_status = RaceStatus.SC
            print(f"\n\U0001F4A5 Incident: {car.driver.name} - {car.dnf_reason}")
            print("\U0001F6A8 Safety Car Deployed")
        return True

    def handle_drs_overtakes(self, all_cars):
        for i in range(len(all_cars) - 1):
            car_ahead = all_cars[i]
            car_behind = all_cars[i + 1]

            if car_ahead.dnf or car_behind.dnf:
                continue

            gap = car_behind.total_race_time - car_ahead.total_race_time
            if self.drs_enabled and gap <= 1.0:  # DRS range
                print(f"\U0001F697\U0001F4A8 {car_behind.driver.name} overtakes {car_ahead.driver.name} in DRS zone!")

                # Overtake mechanics
                overtake_gap = 0.5  # Gap formed for the new leader
                car_behind.total_race_time = car_ahead.total_race_time - overtake_gap

                # Swap positions
                car_behind.position, car_ahead.position = car_ahead.position, car_behind.position
                all_cars[i], all_cars[i + 1] = all_cars[i + 1], all_cars[i]

    def run_race(self):
        print(f"\nRace Start - {self.circuit_name}")

        for lap in range(1, self.total_laps + 1):
            self.current_lap = lap

            if self.current_lap > 10:
                self.drs_enabled = True

            self.display_race_banner()

            for sector in range(1, 4):
                print(f"\nSector {sector}:")

                for car in [c for c in self.cars if not c.dnf]:
                    if sector == 1:
                        car.tire_age += 1
                        if car.tire_age >= car.current_tire["max_laps"]:
                            car.in_pit = True

                    sector_time = self.calculate_sector_time(car, sector)
                    setattr(car, f"sector{sector}_time", sector_time)
                    if sector == 3:
                        car.last_lap = car.sector1_time + car.sector2_time + car.sector3_time
                        car.total_race_time += car.last_lap

                    if car.in_pit:
                        self.handle_pit_stop(car)

                    self.check_incidents(car)

                print("\nPositions:")
                all_cars = sorted(self.cars, key=lambda x: float('inf') if x.dnf else x.total_race_time)
                leader_time = next((c.total_race_time for c in all_cars if not c.dnf), 0)

                for pos, car in enumerate(all_cars, 1):
                    car.last_position = pos
                    status = car.update_status()

                    if car.dnf:
                        print(f"{pos}. {car.driver.name:15} | {status}")
                    else:
                        gap = f"+{car.total_race_time - leader_time:.3f}s"
                        sector_time = getattr(car, f"sector{sector}_time", 0.0)
                        print(f"{pos}. {car.driver.name:15} | S{sector}: {sector_time:.3f} | Gap: {gap} | Tire Age: {car.tire_age} | {status}")

                if sector == 3 and not self.safety_car:
                    self.handle_drs_overtakes(all_cars)

                time.sleep(1)

            if self.safety_car:
                self.safety_car_laps -= 1
                if self.safety_car_laps <= 0:
                    self.safety_car = False
                    self.race_status = RaceStatus.GREEN
                    print("\n\U0001F3C1 Safety Car In This Lap!")

            time.sleep(2)
            clear_console()

if __name__ == "__main__":
    sim = F1Simulator()
    sim.run_race()

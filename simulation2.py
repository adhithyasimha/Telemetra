import random
import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
from rich.console import Console
from rich.table import Table
from rich.live import Live
import datetime

class Weather(Enum):
    DRY = "Dry"
    LIGHT_RAIN = "Light Rain"
    HEAVY_RAIN = "Heavy Rain"

class Flag(Enum):
    GREEN = "Green Flag"
    YELLOW = "Yellow Flag"
    RED = "Red Flag"
    SAFETY_CAR = "Safety Car"
    VSC = "Virtual Safety Car"

class IncidentType(Enum):
    MECHANICAL = "Mechanical Failure"
    PUNCTURE = "Tire Puncture"
    COLLISION = "Collision"
    SPIN = "Spin"
    BRAKE_FAILURE = "Brake Failure"
    ENGINE_FAILURE = "Engine Failure"

@dataclass
class CarComponents:
    engine_wear: float = 0.0
    gearbox_wear: float = 0.0
    brake_wear: float = 0.0
    tire_wear: Dict[str, float] = field(default_factory=lambda: {
        "FL": 0.0, "FR": 0.0, "RL": 0.0, "RR": 0.0
    })
    tire_temps: Dict[str, float] = field(default_factory=lambda: {
        "FL": 80.0, "FR": 80.0, "RL": 80.0, "RR": 80.0
    })

@dataclass
class Driver:
    name: str
    number: int
    team: str
    skill: float
    aggression: float
    wet_skill: float
    tire_management: float

@dataclass
class Car:
    driver: Driver
    components: CarComponents = field(default_factory=CarComponents)
    position: int = 0
    fuel_load: float = 110.0
    lap_time: float = 0.0
    gap_to_leader: float = 0.0
    pit_stops: int = 0
    in_pit: bool = False
    dnf: bool = False
    dnf_reason: str = ""
    current_tire_compound: str = "Soft"
    last_pit_lap: int = 0

class Circuit:
    def __init__(self):
        self.name = "Marina Bay Street Circuit"
        self.length = 5.063
        self.laps = 61
        self.sectors = 3
        self.corners = 23
        self.base_laptime = 98.0
        self.pit_loss_time = 23.0
        self.track_temp = 30.0
        self.humidity = 85.0

class RaceControl:
    def __init__(self):
        self.flag_status = Flag.GREEN
        self.safety_car = False
        self.vsc = False
        self.incidents = []
        self.debris_sectors = set()

class F1Simulator:
    def __init__(self):
        self.console = Console()
        self.circuit = Circuit()
        self.race_control = RaceControl()
        self.weather = Weather.DRY
        self.current_lap = 0
        
        self.drivers = [
            Driver("Max Verstappen", 1, "Red Bull", 0.98, 0.90, 0.95, 0.92),
            Driver("Sergio Perez", 11, "Red Bull", 0.94, 0.85, 0.88, 0.90),
            Driver("Lewis Hamilton", 44, "Mercedes", 0.97, 0.85, 0.96, 0.94),
            Driver("George Russell", 63, "Mercedes", 0.95, 0.87, 0.92, 0.93),
            Driver("Charles Leclerc", 16, "Ferrari", 0.96, 0.89, 0.93, 0.91),
            Driver("Carlos Sainz", 55, "Ferrari", 0.94, 0.86, 0.91, 0.90),
            Driver("Lando Norris", 4, "McLaren", 0.93, 0.88, 0.90, 0.89),
            Driver("Oscar Piastri", 81, "McLaren", 0.91, 0.84, 0.88, 0.87),
            Driver("Fernando Alonso", 14, "Aston Martin", 0.95, 0.89, 0.94, 0.93),
            Driver("Lance Stroll", 18, "Aston Martin", 0.90, 0.85, 0.87, 0.86),
            # Add remaining 10 drivers
        ]
        
        self.cars = [Car(driver) for driver in self.drivers]

    def check_incidents(self, car: Car) -> Optional[IncidentType]:
        # Component failures
        if random.random() < 0.001 * (1 + car.components.engine_wear):
            return IncidentType.ENGINE_FAILURE
        
        # Tire failures
        for tire, wear in car.components.tire_wear.items():
            if wear > 90 and random.random() < 0.05:
                return IncidentType.PUNCTURE
        
        # Collision chance
        if random.random() < 0.001 * car.driver.aggression:
            return IncidentType.COLLISION
        
        return None

    def simulate_lap(self):
        for car in self.cars:
            if car.dnf:
                continue

            # Check for incidents
            incident = self.check_incidents(car)
            if incident:
                car.dnf = True
                car.dnf_reason = incident.value
                self.race_control.incidents.append((self.current_lap, car, incident))
                continue

            # Update components
            car.components.engine_wear += random.uniform(0.1, 0.3)
            car.components.gearbox_wear += random.uniform(0.1, 0.2)
            
            # Tire degradation
            for tire in car.components.tire_wear:
                wear_factor = 1.0 + (car.driver.aggression * 0.2)
                car.components.tire_wear[tire] += random.uniform(0.5, 1.5) * wear_factor
            
            # Fuel consumption
            car.fuel_load -= 1.8  # kg per lap

    def calculate_lap_time(self, car: Car) -> float:
        base = self.circuit.base_laptime
        skill_factor = car.driver.skill
        tire_factor = 1.0 + (sum(car.components.tire_wear.values()) / 400)
        fuel_factor = 1.0 + (car.fuel_load / 110 * 0.1)
        
        if car.in_pit:
            return base + self.circuit.pit_loss_time
            
        return base * skill_factor * tire_factor * fuel_factor

    def run_race(self):
        with Live(self.create_race_table(), refresh_per_second=1) as live:
            for lap in range(1, self.circuit.laps + 1):
                self.current_lap = lap
                self.simulate_lap()
                
                # Update positions and gaps
                active_cars = [car for car in self.cars if not car.dnf]
                for car in active_cars:
                    car.lap_time = self.calculate_lap_time(car)
                
                active_cars.sort(key=lambda x: x.lap_time)
                
                # Update race table
                table = self.create_race_table()
                for pos, car in enumerate(active_cars, 1):
                    table.add_row(
                        str(pos),
                        f"{car.driver.name}",
                        car.driver.team,
                        f"{car.lap_time:.3f}",
                        car.current_tire_compound,
                        f"{sum(car.components.tire_wear.values())/4:.1f}%",
                        str(car.pit_stops),
                        "In Pit" if car.in_pit else "Running" if not car.dnf else f"DNF - {car.dnf_reason}"
                    )
                
                live.update(table)
                time.sleep(1)

    def create_race_table(self) -> Table:
        table = Table(title=f"Singapore GP - Lap {self.current_lap}/{self.circuit.laps}")
        table.add_column("Pos")
        table.add_column("Driver")
        table.add_column("Team")
        table.add_column("Last Lap")
        table.add_column("Tires")
        table.add_column("Wear")
        table.add_column("Stops")
        table.add_column("Status")
        return table

if __name__ == "__main__":
    sim = F1Simulator()
    sim.run_race()
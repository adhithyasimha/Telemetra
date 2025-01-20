import random
import time
from dataclasses import dataclass, field
from typing import Dict, List
from enum import Enum
import os

def clear_console():
    os.system('clear')

PURPLE = '\033[95m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

class RaceStatus(Enum):
    GREEN = "🟢 Racing"
    YELLOW = "🟡 Yellow Flag"
    SC = "🚨 Safety Car"
    VSC = "🟡 Virtual Safety Car"
    RED = "🔴 Red Flag"

class Weather(Enum):
    DRY = "Dry"
    LIGHT_RAIN = "Light Rain"
    HEAVY_RAIN = "Heavy Rain"

class TeamPerformance:
    FACTORS = {
        "Red Bull": {"S1": 0.96, "S2": 0.92, "S3": 0.97, "base": 0.96},
        "Mercedes": {"S1": 0.99, "S2": 0.98, "S3": 0.98, "base": 0.93},
        "Ferrari": {"S1": 0.98, "S2": 0.92, "S3": 0.99, "base": 0.91},
        "McLaren": {"S1": 0.90, "S2": 0.91, "S3": 0.94, "base": 0.91},
        "Aston Martin": {"S1": 1.00, "S2": 1.00, "S3": 1.00, "base": 0.98},
        "Alpine": {"S1": 1.01, "S2": 1.01, "S3": 1.01, "base": 0.99},
        "Williams": {"S1": 1.02, "S2": 1.02, "S3": 1.02, "base": 1.00},
        "AlphaTauri": {"S1": 1.03, "S2": 1.03, "S3": 1.03, "base": 1.01},
        "Alfa Romeo": {"S1": 1.04, "S2": 1.04, "S3": 1.04, "base": 1.02},
        "Haas": {"S1": 1.05, "S2": 1.05, "S3": 1.05, "base": 1.03}
    }

@dataclass
class Sector:
    time: float = 0.0
    personal_best: float = float('inf')
    session_best: float = float('inf')

@dataclass
class Driver:
    name: str
    number: int
    team: str
    skill: float
    wet_skill: float
    aggression: float
    tire_management: float
    sectors: List[Sector] = field(default_factory=lambda: [Sector() for _ in range(3)])
    fastest_lap: float = float('inf')
    current_lap_time: float = 0.0
    status: str = "In Garage"

@dataclass
class QualifyingSession:
    name: str
    duration: int
    remaining_time: float
    eliminated_positions: List[int]

class F1Simulator:
    def __init__(self):
        self.circuit_name = "Marina Bay Street Circuit"
        self.weather = Weather.DRY
        self.base_laptime = 98.0
        self.session_best_sectors = [float('inf')] * 3
        self.session_best_lap = float('inf')
        
        self.sessions = {
            "Q1": QualifyingSession("Q1", 18, 18*60, list(range(16, 21))),
            "Q2": QualifyingSession("Q2", 15, 15*60, list(range(11, 16))),
            "Q3": QualifyingSession("Q3", 12, 12*60, [])
        }
        
        self.drivers = [
            Driver("Max Verstappen", 1, "Red Bull", 0.98, 0.95, 0.90, 0.92),
            Driver("Sergio Perez", 11, "Red Bull", 0.94, 0.88, 0.85, 0.90),
            Driver("Lewis Hamilton", 44, "Mercedes", 0.97, 0.96, 0.97, 0.94),
            Driver("George Russell", 63, "Mercedes", 0.95, 0.92, 0.87, 0.93),
            Driver("Charles Leclerc", 16, "Ferrari", 0.96, 0.93, 0.89, 0.91),
            Driver("Carlos Sainz", 55, "Ferrari", 0.94, 0.91, 0.86, 0.90),
            Driver("Lando Norris", 4, "McLaren", 0.93, 0.90, 0.90, 0.89),
            Driver("Oscar Piastri", 81, "McLaren", 0.91, 0.88, 0.88, 0.89),
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

    def simulate_sector_time(self, driver: Driver, sector: int) -> float:
        base_time = self.base_laptime / 3
        team_factor = TeamPerformance.FACTORS[driver.team][f"S{sector}"]
        skill_factor = 1 - ((driver.skill - 0.8) * 0.5)
        random_factor = random.uniform(-0.2, 0.2) * driver.skill
        
        sector_time = base_time * team_factor * skill_factor + random_factor
        
        if sector_time < driver.sectors[sector-1].personal_best:
            driver.sectors[sector-1].personal_best = sector_time
        
        if sector_time < self.session_best_sectors[sector-1]:
            self.session_best_sectors[sector-1] = sector_time
            
        return sector_time

    def format_sector_time(self, time: float, personal_best: float, session_best: float) -> str:
        if time == 0.0:
            return f"{YELLOW}No Time{RESET}"
        if abs(time - session_best) < 0.001:
            return f"{PURPLE}{time:.3f}{RESET}"
        if abs(time - personal_best) < 0.001:
            return f"{GREEN}{time:.3f}{RESET}"
        return f"{time:.3f}"

    def display_qualifying_status(self, session: str, drivers: List[Driver]):
        clear_console()
        print(f"\n{session} - {self.circuit_name}")
        print(f"Weather: {self.weather.value}")
        print(f"Time Remaining: {self.sessions[session].remaining_time/60:.1f} minutes")
        print("\nPos  Driver          S1      S2      S3      Time     Status")
        print("-" * 65)

        sorted_drivers = sorted(drivers, key=lambda d: d.fastest_lap)
        for pos, driver in enumerate(sorted_drivers, 1):
            s1 = self.format_sector_time(driver.sectors[0].time,
                                       driver.sectors[0].personal_best,
                                       self.session_best_sectors[0])
            s2 = self.format_sector_time(driver.sectors[1].time,
                                       driver.sectors[1].personal_best,
                                       self.session_best_sectors[1])
            s3 = self.format_sector_time(driver.sectors[2].time,
                                       driver.sectors[2].personal_best,
                                       self.session_best_sectors[2])
            
            lap_time = driver.fastest_lap
            if lap_time == float('inf'):
                lap_time_str = "No Time"
            else:
                lap_time_str = f"{lap_time:.3f}"
            
            print(f"{pos:2d}.  {driver.name:<14} {s1:>7} {s2:>7} {s3:>7} {lap_time_str:>8} {driver.status:>10}")

    def run_session(self, session_name: str, drivers: List[Driver]):
        session_time = self.sessions[session_name].remaining_time
        
        while session_time > 0:
            for driver in drivers:
                if random.random() < 0.3:  # 30% chance of doing a lap
                    driver.status = "Out Lap"
                    self.display_qualifying_status(session_name, drivers)
                    time.sleep(0.5)
                    
                    driver.status = "Flying Lap"
                    current_lap = 0
                    for sector in range(3):
                        sector_time = self.simulate_sector_time(driver, sector + 1)
                        driver.sectors[sector].time = sector_time
                        current_lap += sector_time
                        self.display_qualifying_status(session_name, drivers)
                        time.sleep(0.5)
                    
                    if current_lap < driver.fastest_lap:
                        driver.fastest_lap = current_lap
                    
                    driver.status = "In Lap"
                    self.display_qualifying_status(session_name, drivers)
                    time.sleep(0.5)
                    
                driver.status = "In Garage"
            
            session_time -= 5
            self.display_qualifying_status(session_name, drivers)
            time.sleep(0.5)

    def conduct_qualifying(self):
        print("\nQualifying Session Start")
        
        # Q1 - All drivers
        print("\nQ1 Session - Eliminating positions 16-20")
        active_drivers = self.drivers.copy()
        self.run_session("Q1", active_drivers)
        active_drivers.sort(key=lambda d: d.fastest_lap)
        eliminated = active_drivers[15:]
        active_drivers = active_drivers[:15]
        
        print("\nQ1 Eliminated:")
        for pos, driver in enumerate(eliminated, 16):
            print(f"{pos}. {driver.name:<15} {driver.fastest_lap:.3f}")
        time.sleep(3)
        
        # Q2 - Top 15 drivers
        print("\nQ2 Session - Eliminating positions 11-15")
        self.run_session("Q2", active_drivers)
        active_drivers.sort(key=lambda d: d.fastest_lap)
        eliminated_q2 = active_drivers[10:]
        active_drivers = active_drivers[:10]
        
        print("\nQ2 Eliminated:")
        for pos, driver in enumerate(eliminated_q2, 11):
            print(f"{pos}. {driver.name:<15} {driver.fastest_lap:.3f}")
        time.sleep(3)
        
        # Q3 - Top 10 shootout
        print("\nQ3 Session - Final Qualifying")
        self.run_session("Q3", active_drivers)
        active_drivers.sort(key=lambda d: d.fastest_lap)
        
        print("\nFinal Grid:")
        print("Pos  Driver          Time     Gap")
        print("-" * 40)
        
        # Print top 10
        pole_time = active_drivers[0].fastest_lap
        for pos, driver in enumerate(active_drivers, 1):
            gap = f"+{(driver.fastest_lap - pole_time):.3f}" if pos > 1 else "POLE"
            print(f"{pos:2d}.  {driver.name:<15} {driver.fastest_lap:.3f}  {gap}")
        
        # Print 11-15
        for pos, driver in enumerate(eliminated_q2, 11):
            print(f"{pos:2d}.  {driver.name:<15} {driver.fastest_lap:.3f}")
        
        # Print 16-20
        for pos, driver in enumerate(eliminated, 16):
            print(f"{pos:2d}.  {driver.name:<15} {driver.fastest_lap:.3f}")

if __name__ == "__main__":
    sim = F1Simulator()
    sim.conduct_qualifying()
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pandas as pd
import matplotlib.patches as patches
from matplotlib.collections import PatchCollection
from matplotlib.colors import LinearSegmentedColormap
import io
import time

class F1Simulation:
    def __init__(self, track_csv=None):
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.drivers = []
        self.timer_text = None
        self.leaderboard_text = None
        self.race_time = 0
        self.start_time = None
        
        # If no CSV provided, use sample data
        if track_csv:
            self.df = pd.read_csv(track_csv, comment='#')
        else:
            # Create sample track data as CSV-like content
            csv_content = """x,y,right_width,left_width
            0,0,5,5
            20,10,5,5
            40,30,5,5
            60,60,5,5
            80,100,5,5
            100,140,5,5
            120,160,5,5
            140,170,5,5
            160,160,5,5
            180,140,5,5
            200,100,5,5
            220,60,5,5
            240,30,5,5
            260,10,5,5
            280,0,5,5
            240,-20,5,5
            200,-30,5,5
            160,-20,5,5
            120,0,5,5
            80,10,5,5
            40,10,5,5
            0,0,5,5
            """
            self.df = pd.read_csv(io.StringIO(csv_content))
        
        # Get column names
        self.x_col = self.df.columns[0]  # First column for x coordinates
        self.y_col = self.df.columns[1]  # Second column for y coordinates
        self.right_col = self.df.columns[2]  # Third column for right track width
        self.left_col = self.df.columns[3]  # Fourth column for left track width
        
        # Create a smooth interpolated track
        self.create_smooth_track()
        
        # Initialize drivers
        self.initialize_drivers()

    def create_smooth_track(self):
        """Create a smooth interpolated track with more points"""
        # Original track points
        x = self.df[self.x_col].values
        y = self.df[self.y_col].values
        right = self.df[self.right_col].values
        left = self.df[self.left_col].values
        
        # Create a parameter along the track
        t = np.zeros(len(x))
        for i in range(1, len(t)):
            t[i] = t[i-1] + np.sqrt((x[i] - x[i-1])**2 + (y[i] - y[i-1])**2)
        
        # Normalize to [0, 1]
        if t[-1] > 0:
            t = t / t[-1]
        
        # Interpolate to get a smooth track
        num_points = 1000
        self.t_smooth = np.linspace(0, 1, num_points)
        self.x_smooth = np.interp(self.t_smooth, t, x)
        self.y_smooth = np.interp(self.t_smooth, t, y)
        self.right_smooth = np.interp(self.t_smooth, t, right)
        self.left_smooth = np.interp(self.t_smooth, t, left)
        
        # Calculate track direction vectors
        dx = np.gradient(self.x_smooth)
        dy = np.gradient(self.y_smooth)
        self.track_length = sum(np.sqrt(dx**2 + dy**2))
        
        # Calculate normal vectors
        norm = np.sqrt(dx**2 + dy**2)
        norm[norm == 0] = 1  # Avoid division by zero
        self.nx = -dy / norm
        self.ny = dx / norm
        
        # Create outer and inner boundaries for drawing
        self.outer_x = self.x_smooth + self.right_smooth * self.nx
        self.outer_y = self.y_smooth + self.right_smooth * self.ny
        self.inner_x = self.x_smooth - self.left_smooth * self.nx
        self.inner_y = self.y_smooth - self.left_smooth * self.ny
        
        # Create closed path for fill
        self.track_x = np.concatenate([self.outer_x, self.inner_x[::-1], [self.outer_x[0]]])
        self.track_y = np.concatenate([self.outer_y, self.inner_y[::-1], [self.outer_y[0]]])
        
        # Calculate colors for track sections (alternating asphalt and red/blue)
        self.track_colors = np.ones((len(self.t_smooth), 4))  # RGBA
        
        # Add racing line
        racing_t = np.linspace(0, 1, num_points)
        racing_factor = 0.5 + 0.3 * np.sin(racing_t * 2 * np.pi * 3)  # Oscillates between sides
        self.racing_x = self.x_smooth + (self.right_smooth * self.nx - self.left_smooth * self.nx) * racing_factor
        self.racing_y = self.y_smooth + (self.right_smooth * self.ny - self.left_smooth * self.ny) * racing_factor

    def initialize_drivers(self):
        """Initialize F1 drivers with colors, positions, and speeds"""
        driver_data = [
            {"name": "HAM", "team": "Mercedes", "color": (0, 0.82, 0.75), "number": 44},
            {"name": "VER", "team": "Red Bull", "color": (0.02, 0, 0.94), "number": 1},
            {"name": "LEC", "team": "Ferrari", "color": (0.86, 0, 0), "number": 16},
            {"name": "NOR", "team": "McLaren", "color": (1, 0.53, 0), "number": 4},
            {"name": "PER", "team": "Red Bull", "color": (0.02, 0, 0.94), "number": 11},
            {"name": "SAI", "team": "Ferrari", "color": (0.86, 0, 0), "number": 55},
            {"name": "RUS", "team": "Mercedes", "color": (0, 0.82, 0.75), "number": 63},
            {"name": "PIA", "team": "McLaren", "color": (1, 0.53, 0), "number": 81}
        ]
        
        for i, driver in enumerate(driver_data):
            # Start drivers at different positions
            t_pos = i * 0.05
            idx = int(t_pos * len(self.t_smooth)) % len(self.t_smooth)
            
            # Slightly offset from center
            offset = (i % 2) * 2 - 1  # -1 or 1
            
            # Calculate position
            x = self.x_smooth[idx] + offset * self.nx[idx] * min(self.right_smooth[idx], self.left_smooth[idx]) * 0.3
            y = self.y_smooth[idx] + offset * self.ny[idx] * min(self.right_smooth[idx], self.left_smooth[idx]) * 0.3
            
            # Add driver
            driver_dict = {
                "name": driver["name"],
                "team": driver["team"],
                "color": driver["color"],
                "number": driver["number"],
                "t_pos": t_pos,  # Position along track (0 to 1)
                "x": x,
                "y": y,
                "speed": 0.0003 + (0.0001 * np.random.random()),  # Random speed variation
                "lap": 1,
                "best_lap": float('inf'),
                "last_lap_time": 0,
                "last_lap_start": 0
            }
            
            self.drivers.append(driver_dict)

    def draw_track(self):
        """Draw the racing track"""
        # Fill the track
        self.ax.fill(self.track_x, self.track_y, color='#333333', zorder=1)
        
        # Add a track centerline
        self.ax.plot(self.x_smooth, self.y_smooth, 'w--', linewidth=1, alpha=0.5, zorder=2)
        
        # Add racing line
        self.ax.plot(self.racing_x, self.racing_y, 'r-', linewidth=1.5, alpha=0.7, zorder=2)
        
        # Add start/finish line
        start_idx = 0
        norm_x = self.right_smooth[start_idx] * self.nx[start_idx]
        norm_y = self.right_smooth[start_idx] * self.ny[start_idx]
        
        self.ax.plot(
            [self.x_smooth[start_idx] - self.left_smooth[start_idx] * self.nx[start_idx], 
             self.x_smooth[start_idx] + self.right_smooth[start_idx] * self.nx[start_idx]],
            [self.y_smooth[start_idx] - self.left_smooth[start_idx] * self.ny[start_idx], 
             self.y_smooth[start_idx] + self.right_smooth[start_idx] * self.ny[start_idx]],
            'w-', linewidth=4, zorder=3
        )
        
        # Add some sector markers (DRS zones, turns)
        sectors = [
            {"pos": 0.2, "name": "DRS Zone 1", "color": "green"},
            {"pos": 0.5, "name": "DRS Zone 2", "color": "green"},
            {"pos": 0.8, "name": "DRS Zone 3", "color": "green"}
        ]
        
        for sector in sectors:
            idx = int(sector["pos"] * len(self.t_smooth))
            
            # Create a rectangle at the position
            rect_width = 10
            rect_height = 5
            rect_x = self.x_smooth[idx] - rect_width/2
            rect_y = self.y_smooth[idx] - rect_height/2
            
            rectangle = patches.Rectangle(
                (rect_x, rect_y), rect_width, rect_height, 
                linewidth=1, edgecolor='white', facecolor=sector["color"], alpha=0.7,
                zorder=3
            )
            self.ax.add_patch(rectangle)
            
            # Add text
            self.ax.text(
                self.x_smooth[idx], self.y_smooth[idx], sector["name"],
                horizontalalignment='center', verticalalignment='center',
                color='white', fontsize=8, fontweight='bold', zorder=4
            )

        # Add some turn markers
        turns = [0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95]
        for i, t in enumerate(turns):
            idx = int(t * len(self.t_smooth))
            circle = patches.Circle(
                (self.x_smooth[idx], self.y_smooth[idx]), 
                2.5, facecolor='black', edgecolor='white', zorder=3
            )
            self.ax.add_patch(circle)
            self.ax.text(
                self.x_smooth[idx], self.y_smooth[idx], str(i+1),
                horizontalalignment='center', verticalalignment='center',
                color='white', fontsize=8, fontweight='bold', zorder=4
            )

    def draw_driver(self, driver):
        """Draw a single driver on the track"""
        circle = patches.Circle(
            (driver["x"], driver["y"]), 
            3, facecolor=driver["color"], edgecolor='white', zorder=5
        )
        self.ax.add_patch(circle)
        
        # Add driver name
        self.ax.text(
            driver["x"], driver["y"], driver["name"][0],
            horizontalalignment='center', verticalalignment='center',
            color='white', fontsize=8, fontweight='bold', zorder=6
        )

    def update_drivers(self, delta_time):
        """Update driver positions based on their speed"""
        for driver in self.drivers:
            # Update position along track
            prev_t = driver["t_pos"]
            driver["t_pos"] = (driver["t_pos"] + driver["speed"] * delta_time) % 1
            
            # Check if completed a lap
            if driver["t_pos"] < prev_t:
                driver["lap"] += 1
                
                # Calculate lap time
                current_time = self.race_time
                lap_time = current_time - driver["last_lap_start"]
                driver["last_lap_time"] = lap_time
                driver["last_lap_start"] = current_time
                
                # Update best lap
                if lap_time < driver["best_lap"]:
                    driver["best_lap"] = lap_time
            
            # Get smooth index
            idx = int(driver["t_pos"] * len(self.t_smooth))
            
            # Racing line adherence (with some randomness)
            # Use the racing line with random variations
            adherence = 0.8 + 0.2 * np.random.random()  # 80-100% adherence to racing line
            
            # Mix between track center and racing line
            racing_idx = idx % len(self.racing_x)
            driver["x"] = self.racing_x[racing_idx]
            driver["y"] = self.racing_y[racing_idx]
            
            # Add small random variations in speed (to simulate race dynamics)
            if np.random.random() < 0.02:  # 2% chance per update
                # Small speed adjustment ±5%
                driver["speed"] *= 0.95 + 0.1 * np.random.random()

        # Sort drivers by position (lap and track position)
        self.drivers.sort(key=lambda d: (-d["lap"], d["t_pos"]))

    def draw_leaderboard(self):
        """Draw the race leaderboard"""
        if self.leaderboard_text:
            self.leaderboard_text.remove()
        
        # Format leaderboard text
        leader = self.drivers[0]
        
        leaderboard = "LEADERBOARD\n"
        leaderboard += "─" * 25 + "\n"
        leaderboard += f"{'POS':<3}{'DRIVER':<6}{'LAP':<4}{'GAP':<8}{'LAST':<8}\n"
        leaderboard += "─" * 25 + "\n"
        
        for i, driver in enumerate(self.drivers):
            # Calculate gap to leader
            if i == 0:
                gap = "LEADER"
            else:
                lap_diff = leader["lap"] - driver["lap"]
                if lap_diff > 0:
                    gap = f"+{lap_diff} LAP"
                else:
                    # Calculate time gap based on position
                    pos_diff = leader["t_pos"] - driver["t_pos"]
                    if pos_diff < 0:
                        pos_diff += 1
                    time_gap = pos_diff / driver["speed"]
                    gap = f"+{time_gap:.1f}s"
            
            # Format last lap time
            if driver["last_lap_time"] > 0:
                last_lap = f"{driver['last_lap_time']/1000:.1f}s"
            else:
                last_lap = "―"
            
            leaderboard += f"{i+1:<3}{driver['name']:<6}{driver['lap']:<4}{gap:<8}{last_lap:<8}\n"
        
        # Calculate properties for the text box
        props = dict(boxstyle='round', facecolor='white', alpha=0.7)
        
        # Add text box to the plot
        self.leaderboard_text = self.ax.text(
            0.02, 0.98, leaderboard,
            transform=self.ax.transAxes,
            fontsize=9, fontfamily='monospace',
            verticalalignment='top', bbox=props
        )

    def draw_race_info(self):
        """Draw race timer and other info"""
        if self.timer_text:
            self.timer_text.remove()
            
        # Format race time
        minutes = int(self.race_time / 60000)
        seconds = int((self.race_time % 60000) / 1000)
        milliseconds = int(self.race_time % 1000)
        
        race_info = f"RACE TIME: {minutes:02d}:{seconds:02d}.{milliseconds:03d}"
        
        # Calculate properties for the text box
        props = dict(boxstyle='round', facecolor='black', alpha=0.7)
        
        # Add text box to the plot
        self.timer_text = self.ax.text(
            0.5, 0.02, race_info,
            transform=self.ax.transAxes,
            fontsize=10, color='white', fontweight='bold',
            horizontalalignment='center', bbox=props
        )

    def animate(self, frame):
        """Animation function for each frame"""
        self.ax.clear()
        
        # Set axis limits and properties
        x_min, x_max = min(self.track_x), max(self.track_x)
        y_min, y_max = min(self.track_y), max(self.track_y)
        
        # Add some margin
        margin = max((x_max - x_min), (y_max - y_min)) * 0.1
        self.ax.set_xlim(x_min - margin, x_max + margin)
        self.ax.set_ylim(y_min - margin, y_max + margin)
        
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        self.ax.set_title('F1 Race Simulation', fontsize=16, fontweight='bold')
        
        # Update race time
        current_time = time.time()
        if self.start_time is None:
            self.start_time = current_time
        
        self.race_time = (current_time - self.start_time) * 1000  # in milliseconds
        
        # Draw track
        self.draw_track()
        
        # Update driver positions
        self.update_drivers(50)  # Fixed time step for smoother animation
        
        # Draw drivers
        for driver in self.drivers:
            self.draw_driver(driver)
        
        # Draw leaderboard
        self.draw_leaderboard()
        
        # Draw race info
        self.draw_race_info()
        
        return []

    def run_simulation(self):
        """Run the race simulation"""
        # Set up animation
        ani = animation.FuncAnimation(
            self.fig, self.animate, frames=None,
            interval=40, blit=True
        )
        
        plt.tight_layout()
        plt.show()

# Create and run the simulation
if __name__ == "__main__":
    # You can replace 'None' with your CSV file path
    simulation = F1Simulation(None)
    simulation.run_simulation()
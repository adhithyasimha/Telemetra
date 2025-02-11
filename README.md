# Contents of `README.md`

# F1 Airflow Pipeline

This project orchestrates the execution of qualifying and race simulations for a racing event using Apache Airflow.

## Project Structure

- **dags/**: Contains the DAG definition for orchestrating the simulations.
  - `f1_simulation_dag.py`: Defines the tasks to run the qualifying and race simulations.
  
- **scripts/**: Contains the simulation scripts.
  - `qualifying_simulation.py`: Simulates the qualifying session.
  - `race_simulation.py`: Contains the logic for simulating the race.

- **tests/**: Contains unit tests for the DAG.
  - `test_dag.py`: Tests the setup and execution of the DAG tasks.

- **requirements.txt**: Lists the dependencies required for the project.

## Setup Instructions

1. Clone the repository.
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Start the Apache Airflow web server and scheduler.
4. Access the Airflow UI to trigger the DAG and monitor the execution of the simulations.

## Functionality Overview

The project defines an Apache Airflow DAG that orchestrates the execution of the qualifying simulation followed by the race simulation, with a 5-second wait in between.
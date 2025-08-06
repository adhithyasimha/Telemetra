from flask import Flask, render_template, jsonify
import redis
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

@app.route('/')
def dashboard():
    driver_keys = [k for k in r.keys('driver:*') if k.split(':')[1].isdigit()]
    drivers = {k.split(':')[1]: r.hgetall(k) for k in driver_keys}
    
    # Fetch latest timing data for positions and lap times
    timing = {d: r.hgetall(f"latest:timing:{d}") or {} for d in drivers}
    
    # Sort drivers by Position (from timing_data_f1)
    sorted_drivers = sorted(
        drivers.items(),
        key=lambda x: int(timing[x[0]].get('Position', '999'))  # Default to 999 if no position
    )
    
    return render_template('dashboard.html', drivers=dict(sorted_drivers), timing=timing)

@app.route('/telemetry/<driver_no>')
def get_telemetry(driver_no):
    telemetry = r.hgetall(f"latest:telemetry:{driver_no}") or {}
    return jsonify(telemetry)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
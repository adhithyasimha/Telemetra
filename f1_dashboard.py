from flask import Flask, render_template
import redis

app = Flask(__name__)
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

@app.route('/')
def dashboard():
    # Fetch drivers
    driver_keys = [k for k in r.keys('driver:*') if k.split(':')[1].isdigit()]
    drivers = {k.split(':')[1]: r.hgetall(k) for k in driver_keys}
    
    # Fetch latest Telemetry
    telemetry = {d: r.hgetall(f"latest:telemetry:{d}") or {} for d in drivers}

    return render_template('dashboard.html', drivers=drivers, telemetry=telemetry)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7680, debug=True)
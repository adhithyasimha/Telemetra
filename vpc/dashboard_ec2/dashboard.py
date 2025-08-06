from flask import Flask, render_template, jsonify
import redis
import json
import boto3
from botocore.exceptions import ClientError

app = Flask(__name__)

# Redis connection
r = redis.Redis(
    host='clustercfg.formula1.ppjruj.memorydb.ap-south-1.amazonaws.com',
    port=6379,
    db=0,
    decode_responses=True,
    ssl=True
)

# DynamoDB connection
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
drivers_table = dynamodb.Table('drivers')

def get_driver_info(driver_no):
    """Get driver info from DynamoDB by DriverNo"""
    try:
        response = drivers_table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('DriverNo').eq(str(driver_no))
        )
        
        if response['Items']:
            driver_info = response['Items'][0]
            return {
                'Tla': driver_info.get('Tla', f"#{driver_no}"),
                'TeamColour': driver_info.get('TeamColour', 'FFFFFF'),
                'BroadcastName': driver_info.get('BroadcastName', f"Driver {driver_no}")
            }
        else:
            return {
                'Tla': f"#{driver_no}",
                'TeamColour': 'FFFFFF',
                'BroadcastName': f"Driver {driver_no}"
            }
    except ClientError as e:
        print(f"Error fetching driver info for {driver_no}: {e}")
        return {
            'Tla': f"#{driver_no}",
            'TeamColour': 'FFFFFF',
            'BroadcastName': f"Driver {driver_no}"
        }

@app.route('/')
def dashboard():
    # Get all driver keys for timing data
    driver_keys = [k for k in r.keys('driver:*') if k.split(':')[1].isdigit()]
    drivers = {k.split(':')[1]: r.hgetall(k) for k in driver_keys}
    timing = {d: r.hgetall(f"latest:timingdata:{d}") or {} for d in drivers}
    
    sorted_drivers = sorted(
        drivers.items(),
        key=lambda x: int(timing[x[0]].get('Position', '999'))
    )
    
    return render_template('dashboard.html', drivers=dict(sorted_drivers), timing=timing)

@app.route('/api/telemetry')
def get_all_telemetry():
    """Get combined telemetry and timing data for all drivers"""
    try:
        # Find all telemetry keys
        telemetry_keys = r.keys('latest:telemetry:*')
        combined_data = []
        
        for key in telemetry_keys:
            driver_no = key.split(':')[-1]
            
            # Get telemetry data
            telemetry_data = r.hgetall(key)
            
            # Get timing data
            timing_data = r.hgetall(f"latest:timedata:{driver_no}") or {}
            
            # Get driver info from DynamoDB
            driver_info = get_driver_info(driver_no)
            
            if telemetry_data:
                # Extract sector times - looking for Sectors_X_Value pattern
                s1_time = timing_data.get('Sectors_0_Value', 'N/A')
                s2_time = timing_data.get('Sectors_1_Value', 'N/A') 
                s3_time = timing_data.get('Sectors_2_Value', 'N/A')
                
                # Get gap to leader and position
                gap_to_leader = timing_data.get('GapToLeader', 'N/A')
                position = timing_data.get('Position', '999')
                
                # Get driver TLA and team color from DynamoDB
                driver_tla = driver_info['Tla']
                team_color = driver_info['TeamColour']
                
                # Combine telemetry and timing data
                processed_data = {
                    'Position': position,
                    'DriverNo': telemetry_data.get('DriverNo', driver_no),
                    'DriverTla': driver_tla,
                    'TeamColor': team_color,
                    'gap_to_leader': gap_to_leader,
                    'speed': telemetry_data.get('speed', '0'),
                    'throttle': telemetry_data.get('throttle', '0'),
                    'brake': telemetry_data.get('brake', '0'),
                    'drs': telemetry_data.get('drs', '0'),
                    's1': s1_time,
                    's2': s2_time,
                    's3': s3_time,
                    'timestamp': telemetry_data.get('timestamp', 'N/A')
                }
                combined_data.append(processed_data)
        
        # Sort by position (1st, 2nd, 3rd, etc.)
        combined_data.sort(key=lambda x: int(x['Position']) if str(x['Position']).isdigit() else 999)
        
        return jsonify(combined_data)
    
    except Exception as e:
        print(f"Error fetching telemetry: {e}")
        return jsonify([])

@app.route('/telemetry/<driver_no>')
def get_telemetry(driver_no):
    """Get telemetry data for a specific driver"""
    telemetry = r.hgetall(f"latest:telemetry:{driver_no}") or {}
    return jsonify(telemetry)

@app.route('/api/drivers')
def get_all_drivers():
    """Get list of all active drivers"""
    try:
        telemetry_keys = r.keys('latest:telemetry:*')
        drivers = []
        for key in telemetry_keys:
            driver_no = key.split(':')[-1]
            drivers.append(driver_no)
        
        drivers.sort(key=lambda x: int(x) if x.isdigit() else 999)
        return jsonify(drivers)
    
    except Exception as e:
        print(f"Error fetching drivers: {e}")
        return jsonify([])

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

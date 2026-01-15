import json
import time
import threading
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
from pymongo import MongoClient
from bson.objectid import ObjectId

# --- CONFIGURATION ---
MQTT_BROKER = "192.168.10.12"
MQTT_TOPIC = "home/sensors/data"
MQTT_USER = "chick"
MQTT_PASS = "tastychicken"

EVENT_TIMEOUT = 3.0  # Seconds of silence before "Event Ended"

# --- STATE TRACKING ---
active_events = {}

# --- DATABASE ---
client = MongoClient("mongodb://localhost:27017/")
db = client["security_system"]
collection = db["intrusion_logs"]

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secure_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# --- BACKGROUND MONITOR ---
def monitor_timeouts():
    while True:
        time.sleep(1)
        now = time.time()
        rooms_to_remove = []

        for room, data in active_events.items():
            if now - data['last_seen'] > EVENT_TIMEOUT:
                # Event Ended
                start_dt = datetime.fromtimestamp(data['start_ts'])
                end_dt = datetime.fromtimestamp(data['last_seen'])
                
                record = {
                    "room": room,
                    "start_time": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "end_time": end_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "nearest_distance": round(data['min_dist'], 1),
                    "duration_sec": round(data['last_seen'] - data['start_ts'], 1)
                }
                
                res = collection.insert_one(record)
                record['_id'] = str(res.inserted_id)
                
                # Notify History Page (New Record)
                socketio.emit('new_historical_record', record)
                
                # Notify Dashboard (Stop Alert)
                socketio.emit('status_update', {"room": room, "active": False})
                
                rooms_to_remove.append(room)

        for r in rooms_to_remove:
            del active_events[r]

bg_thread = threading.Thread(target=monitor_timeouts)
bg_thread.daemon = True
bg_thread.start()

# --- MQTT CALLBACKS ---
def on_connect(client, userdata, flags, rc):
    print("MQTT Connected")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        room = payload.get('room')
        dist = float(payload.get('distance'))
        now = time.time()

        if room not in active_events:
            # New Event
            active_events[room] = { "start_ts": now, "min_dist": dist, "last_seen": now }
        else:
            # Update Event
            active_events[room]['last_seen'] = now
            if dist < active_events[room]['min_dist']:
                active_events[room]['min_dist'] = dist
        
        # Send Live Data for Scatter Plot & Sound
        socketio.emit('status_update', {
            "room": room, 
            "active": True, 
            "dist": dist,
            "timestamp": datetime.now().strftime("%H:%M:%S") 
        })

    except Exception as e:
        print(f"Error: {e}")

mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, 1883, 60)
mqtt_client.loop_start()

# --- ROUTES ---
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/api/records')
def get_records():
    records = list(collection.find().sort("_id", -1))
    for r in records: r['_id'] = str(r['_id'])
    return jsonify(records)

@app.route('/api/delete/<id>', methods=['DELETE'])
def delete_record(id):
    collection.delete_one({"_id": ObjectId(id)})
    return jsonify({"status": "deleted"})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
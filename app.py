from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
from plc_engine import PLCEngine
import json

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
plc = PLCEngine()

# Initialize some example I/O points
plc.add_io_point("X0", "input", "I0.0")
plc.add_io_point("X1", "input", "I0.1")
plc.add_io_point("Y0", "output", "Q0.0")
plc.add_io_point("Y1", "output", "Q0.1")
plc.add_timer("T1")
plc.add_counter("C1")
plc.add_analog_input("AI0", "IW0")
plc.add_analog_output("AO0", "QW0")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    return jsonify(plc.get_status())

@app.route('/api/io/<io_type>/<name>', methods=['POST'])
def set_io(io_type, name):
    data = request.get_json()
    if io_type == 'input':
        plc.set_input(name, data.get('value', False))
    return jsonify({'success': True})

@app.route('/api/analog_input/<name>', methods=['POST'])
def set_analog_input(name):
    data = request.get_json()
    plc.set_analog_input(name, float(data.get('value', 0)))
    return jsonify({'success': True})

@socketio.on('connect')
def handle_connect():
    socketio.emit('status_update', plc.get_status())

@socketio.on('disconnect')
def handle_disconnect():
    pass

def emit_status():
    while True:
        socketio.sleep(0.1)
        socketio.emit('status_update', plc.get_status())

if __name__ == '__main__':
    plc.start()
    socketio.start_background_task(emit_status)
    socketio.run(app, debug=True) 
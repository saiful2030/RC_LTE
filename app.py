from flask import Flask, render_template
from flask_socketio import SocketIO
import logging

# ================== Logging ==================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')  # Windows friendly

latest_frame = None
last_motor, last_servo = None, None  # untuk memeriksa perubahan

VALID_MOTOR = {"MAJU", "MUNDUR", "STOP"}
VALID_SERVO = {"KIRI", "KANAN", "CENTER"}

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("video")
def handle_video(data):
    global latest_frame
    latest_frame = data
    socketio.emit("video", data)  # broadcast ke semua client

@socketio.on("control")
def handle_control(data):
    """
    data format: MOTOR;SERVO
    Contoh: MAJU;KIRI, MUNDUR;KANAN, STOP;CENTER
    """
    global last_motor, last_servo

    motor, servo = "UNKNOWN", "UNKNOWN"
    if ";" in data:
        motor, servo = data.split(";")

    # Validasi input
    if motor not in VALID_MOTOR or servo not in VALID_SERVO:
        logging.warning(f"Data kontrol tidak valid: {data}")
        return  # hentikan proses jika data tidak valid

    # Log hanya jika ada perubahan
    if (motor, servo) != (last_motor, last_servo):
        logging.info(f"Motor: {motor}, Servo: {servo}")
        last_motor, last_servo = motor, servo

    # Broadcast ke semua client
    socketio.emit("control", data)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)

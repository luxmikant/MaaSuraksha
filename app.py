import os
import sqlite3
import joblib
import numpy as np
from flask import Flask, request, jsonify, send_from_directory, g, session
from flask_cors import CORS

try:
    import psycopg2
    from psycopg2 import errors as pg_errors
    from psycopg2.extras import RealDictCursor
except Exception:
    psycopg2 = None
    pg_errors = None
    RealDictCursor = None

app = Flask(__name__, static_folder=".", template_folder=".")
app.secret_key = os.getenv("SECRET_KEY", "change_me_in_production")
app.config["SESSION_COOKIE_HTTPONLY"] = True
if os.getenv("FLASK_ENV") == "production":
    app.config["SESSION_COOKIE_SECURE"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "None"

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN")
if FRONTEND_ORIGIN:
    CORS(app, resources={r"/api/*": {"origins": [FRONTEND_ORIGIN]}}, supports_credentials=True)
else:
    CORS(app, resources={r"/api/*": {"origins": "*"}})

DATABASE_URL = os.getenv("DATABASE_URL")
SQLITE_PATH = os.getenv("DATABASE_PATH", "maasuraksha.db")
IS_POSTGRES = bool(DATABASE_URL)

MODEL_PATH = os.getenv("MODEL_PATH", "maternal_risk_model.pkl")
try:
    model = joblib.load(MODEL_PATH)
    if isinstance(model, np.ndarray):
        print("Warning: The loaded model is a numpy array, not a model object. Using mock prediction.")
        model = None
except Exception as e:
    print(f"Error loading model: {e}")
    model = None


def is_unique_violation(exc):
    if isinstance(exc, sqlite3.IntegrityError):
        return True
    if pg_errors is not None and isinstance(exc, pg_errors.UniqueViolation):
        return True
    return "unique" in str(exc).lower()


def execute_sql(cursor, query, params=()):
    if IS_POSTGRES:
        query = query.replace("?", "%s")
    cursor.execute(query, params)


def get_db():
    db = getattr(g, "_database", None)
    if db is not None:
        return db

    if IS_POSTGRES:
        if psycopg2 is None:
            raise RuntimeError("DATABASE_URL is set, but psycopg2 is not installed.")
        ssl_mode = os.getenv("PGSSLMODE", "require")
        db = psycopg2.connect(DATABASE_URL, sslmode=ssl_mode, cursor_factory=RealDictCursor)
        db.autocommit = False
        g._database = db
        return db

    db = sqlite3.connect(SQLITE_PATH)
    db.row_factory = sqlite3.Row
    g._database = db
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        if IS_POSTGRES:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS predictions (
                    id SERIAL PRIMARY KEY,
                    age DOUBLE PRECISION,
                    gestational_month INTEGER,
                    blood_pressure TEXT,
                    hemoglobin DOUBLE PRECISION,
                    complications TEXT,
                    risk_level TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS daily_tracker (
                    id SERIAL PRIMARY KEY,
                    mood TEXT,
                    water_intake INTEGER,
                    sleep_hours DOUBLE PRECISION,
                    symptoms TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL
                )
                """
            )
        else:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    age REAL,
                    gestational_month INTEGER,
                    blood_pressure TEXT,
                    hemoglobin REAL,
                    complications TEXT,
                    risk_level TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS daily_tracker (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mood TEXT,
                    water_intake INTEGER,
                    sleep_hours REAL,
                    symptoms TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL
                )
                """
            )
        db.commit()


def seed_users():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        defaults = [
            ("mother1", "mother123", "patient"),
            ("asha1", "asha123", "asha"),
        ]
        for username, password, role in defaults:
            try:
                execute_sql(
                    cursor,
                    "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                    (username, password, role),
                )
            except Exception as exc:
                db.rollback()
                if not is_unique_violation(exc):
                    raise
        db.commit()


init_db()
seed_users()

# --- ROUTES FOR HTML FILES ---
@app.route('/')
@app.route('/index.html')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/form.html')
def form():
    return send_from_directory('.', 'form.html')

@app.route('/dashboard.html')
def dashboard():
    return send_from_directory('.', 'dashboard.html')

@app.route('/tracker.html')
def tracker():
    return send_from_directory('.', 'tracker.html')

@app.route('/login.html')
def login_page():
    return send_from_directory('.', 'login.html')

# --- ROUTES FOR STATIC FILES (CSS, JS, ASSETS) ---
@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/assets/<path:path>')
def send_assets(path):
    return send_from_directory('assets', path)

# --- API ROUTES ---

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'patient')

    if not username or not password:
        return jsonify({"status": "error", "message": "Username and password required"}), 400

    db = get_db()
    cursor = db.cursor()
    try:
        execute_sql(cursor, 'INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, password, role))
        db.commit()
        session['user'] = username
        session['role'] = role
        return jsonify({"status": "success", "message": "Signup successful", "role": role})
    except Exception as exc:
        db.rollback()
        if is_unique_violation(exc):
            return jsonify({"status": "error", "message": "Username already exists"}), 400
        return jsonify({"status": "error", "message": "Signup failed"}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')

    db = get_db()
    cursor = db.cursor()
    execute_sql(cursor, 'SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()

    if user:
        user_data = dict(user)
        session['user'] = user_data['username']
        session['role'] = user_data['role']
        return jsonify({"status": "success", "message": "Login successful", "role": user_data['role']})
    else:
        return jsonify({"status": "error", "message": "Invalid username or password"}), 401


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"status": "success", "message": "Logged out"})


@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.get_json(silent=True) or {}
    try:
        age = float(data.get('age', 25))
        bp_raw = data.get('blood_pressure', '120/80')
        bp_split = bp_raw.split('/')
        diastolic_bp = float(bp_split[1]) if len(bp_split) > 1 else 80.0

        bs = 7.0
        body_temp = 37.0
        heart_rate = 75.0

        features = np.array([[age, diastolic_bp, bs, body_temp, heart_rate]])

        if model is not None and hasattr(model, 'predict'):
            prediction_idx = model.predict(features)[0]
            risk_mapping = {0: "Low Risk", 1: "Mid Risk", 2: "High Risk"}
            predicted_risk = risk_mapping.get(prediction_idx, "Unknown Risk")
        else:
            if diastolic_bp > 90 or age > 35:
                predicted_risk = "High Risk"
            elif diastolic_bp > 85 or age > 30:
                predicted_risk = "Mid Risk"
            else:
                predicted_risk = "Low Risk"

        db = get_db()
        cursor = db.cursor()
        execute_sql(
            cursor,
            """
            INSERT INTO predictions
            (age, gestational_month, blood_pressure, hemoglobin, complications, risk_level)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                age,
                int(data.get('gestational_month', 0)),
                bp_raw,
                float(data.get('hemoglobin', 12.0)),
                data.get('complications', 'No'),
                predicted_risk,
            ),
        )
        db.commit()

        return jsonify({"status": "success", "risk_level": predicted_risk})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM predictions ORDER BY timestamp DESC LIMIT 20')
    rows = cursor.fetchall()
    alerts = [dict(row) for row in rows]
    return jsonify({"alerts": alerts})


@app.route('/api/tracker', methods=['POST'])
def save_tracker():
    data = request.get_json(silent=True) or {}
    try:
        db = get_db()
        cursor = db.cursor()
        execute_sql(
            cursor,
            """
            INSERT INTO daily_tracker (mood, water_intake, sleep_hours, symptoms)
            VALUES (?, ?, ?, ?)
            """,
            (
                data.get('mood'),
                data.get('water_intake'),
                data.get('sleep_hours'),
                data.get('symptoms'),
            ),
        )
        db.commit()
        return jsonify({"status": "success", "message": "Tracker data saved!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/api/tracker', methods=['GET'])
def get_tracker():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM daily_tracker ORDER BY timestamp DESC LIMIT 7')
    rows = cursor.fetchall()
    logs = [dict(row) for row in rows]
    return jsonify({"logs": logs})


if __name__ == '__main__':
    app.run(
        debug=os.getenv("FLASK_DEBUG") == "1",
        host='0.0.0.0',
        port=int(os.getenv("PORT", 5000)),
    )

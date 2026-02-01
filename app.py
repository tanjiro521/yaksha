
import os
import pickle
import joblib
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import random
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import json

# ---------------------

# Initialize Flask app
# We set static_folder to '.' so it can serve style.css and script.js from the same directory
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # Enable CORS for local development

# ------------------------------------------------------------------------------
# MODEL LOADING SECTION
# ------------------------------------------------------------------------------
# instructions:
# 1. In your Colab notebook, save your trained model:
#    import joblib
#    joblib.dump(model, 'fraud_detection_model.pkl')
# 2. Download 'fraud_detection_model.pkl' and place it in this folder.
# 3. Uncomment the lines below to load the real model.

model = None
try:
    if os.path.exists('fraud_detection_model.pkl'):
        model = joblib.load('fraud_detection_model.pkl')
        print("Model loaded successfully!")
    else:
        print("Warning: 'fraud_detection_model.pkl' not found. Using simulation mode.")
except Exception as e:
    print(f"Error loading model: {e}")

# ------------------------------------------------------------------------------
# ROUTES
# ------------------------------------------------------------------------------

@app.route('/')
def home():
    """Serve the Authentication/Landing page"""
    return send_from_directory('.', 'auth.html')

@app.route('/dashboard')
def dashboard():
    """Serve the Main Dashboard"""
    return send_from_directory('.', 'dashboard.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve other static files like web.html, style.css, script.js"""
    if os.path.exists(path):
        return send_from_directory('.', path)
    return "File not found", 404

# --- Prediction Endpoint ---

# --- Yaksha Chatbot Logic ---
class YakshaChatbot:
    def get_response(self, user_message, context=None):
        """
        Generates a response based on user message and context.
        Context: { 'riskScore': int, 'riskFactors': list }
        """
        msg = user_message.lower()
        response = ""
        
        # 1. Contextual Analysis (If a fraud was just detected)
        if context and context.get('riskFactors') and ("explain" in msg or "why" in msg or "what happened" in msg or "details" in msg):
            factors = context.get('riskFactors', [])
            score = context.get('riskScore', 0)
            
            response += f"I have analyzed the transaction. The threat level is {score}%. "
            
            for factor in factors:
                if "Impossible Location" in factor:
                    response += " I detected the 'Superman Effect'. The card was used in two distant locations nearly simultaneously. This is physical impossibility and a sign of cloning. "
                elif "Frequency" in factor:
                    response += " The 'Swift Hand' anomaly was present. Too many transactions occurred in a short span, suggesting a bot or a thief testing the card. "
                elif "Spike" in factor or "Amount" in factor:
                    response += " The 'Heavy Coffer' alert. A withdrawal or purchase was made that vastly exceeds typical patterns. "
            
            response += " I recommend freezing the card immediately."
            return response

        # 2. General Knowledge / FAQ
        
        # Greetings
        if any(x in msg for x in ["hello", "hi", "hey", "greetings"]):
            return "Greetings, traveler. The Vault is secure. How may I assist you in protecting your wealth?"
            
        # Identity
        if "who are you" in msg or "what are you" in msg:
            return "I am Yaksha, the Ancient Guardian of Digital Wealth. My vigil is eternal, my vision absolute."
            
        # Fraud Solutions / Prevention
        if "solution" in msg or "prevent" in msg or "protect" in msg or "safe" in msg:
            return ("To protect your treasure: \n"
                    "1. Enable 2-Factor Authentication (The Double Lock).\n"
                    "2. Set transaction limits (The Gatekeeper).\n"
                    "3. Monitor your alerts (The Watchtower).\n"
                    "4. Never share your OTP (The Key) with anyone.")
                    
        # Credit Card Doubts
        if "credit card" in msg or "card" in msg:
            if "lost" in msg or "stolen" in msg:
                return "If your key (card) is lost, you must seal the gates instantly. Contact your bank to freeze the card. Do not hesitate."
            if "cvv" in msg:
                return "The CVV is the secret rune on the back of your card. Never share it. If compromised, the lock is broken."
            return "The credit card is a powerful tool, but dangerous if unguarded. Keep it close, check your statements for shadows, and never lend it to strangers."
            
        # Default fallback
        return "I hear you, but the path is unclear. Ask me about 'fraud prevention', 'credit card security', or show me a transaction to analyze."

chatbot_engine = YakshaChatbot()

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        context = data.get('context', {}) # { riskScore: ..., riskFactors: ... }
        
        print(f"Chat Request: {user_message} | Context: {context}")
        
        reply = chatbot_engine.get_response(user_message, context)
        
        return jsonify({'reply': reply})
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({'reply': "My vision is clouded (System Error). Please try again."}), 500

# --- Prediction Endpoint ---
# --- Prediction Endpoint ---
# --- Behavioral Analysis Plugin ---
class BehavioralAnalyzer:
    def __init__(self):
        # In-memory storage for demonstration. 
        # In production, use Redis or a specific DB per user.
        self.history = [] 
        # Config
        self.MAX_HISTORY = 10
        self.VELOCITY_WINDOW_SECONDS = 300 # 5 minutes
        
    def add_transaction(self, amount, lat, long, timestamp):
        """Add transaction to history and trim older ones."""
        self.history.append({
            'amount': amount,
            'lat': lat,
            'long': long,
            'timestamp': timestamp
        })
        # Keep only recent N
        if len(self.history) > self.MAX_HISTORY:
            self.history.pop(0)

    def analyze(self, current_amount, current_lat, current_long, current_time_unix):
        """
        Analyze current transaction against history.
        Returns: {risk_score, specific_metrics}
        """
        if not self.history:
            return {
                'score': 0, 
                'factors': [], 
                'details': {'velocity': 0, 'avg_spending': 0, 'dist_km': 0}
            }
            
        factors = []
        risk_score = 0
        
        # 1. Velocity Check (Frequency)
        # Count tx in last N seconds
        recent_count = sum(1 for tx in self.history 
                           if current_time_unix - tx['timestamp'] < self.VELOCITY_WINDOW_SECONDS)
        
        velocity_risk = 0
        if recent_count >= 5: 
            velocity_risk = 80
            factors.append("High Transaction Frequency")
        elif recent_count >= 3: 
            velocity_risk = 40
            factors.append("Moderate Transaction Frequency")
            
        # 2. Amount Deviation
        avg_amount = sum(tx['amount'] for tx in self.history) / len(self.history)
        deviation_ratio = current_amount / (avg_amount + 1) # Avoid div/0
        
        deviation_risk = 0
        if deviation_ratio > 5:
            deviation_risk = 90
            factors.append("Extreme Spending Spike")
        elif deviation_ratio > 3:
            deviation_risk = 50
            factors.append("Unusual Spending Amount")
            
        # 3. Location Anomaly (Teleportation check)
        # Simple Haversine-ish or Euclidean for speed
        # 1 deg lat approx 111km. 
        last_tx = self.history[-1]
        time_diff = abs(current_time_unix - last_tx['timestamp'])
        if time_diff < 60: time_diff = 60 # Min 1 min to avoid crazy spikes
        
        # Distance (Euclidean approximation is okay for "impossible" jumps)
        # deg_diff = sqrt((lat2-lat1)^2 + (long2-long1)^2)
        import math
        d_lat = current_lat - last_tx['lat']
        d_long = current_long - last_tx['long']
        deg_dist = math.sqrt(d_lat**2 + d_long**2)
        # Approx km
        dist_km = deg_dist * 111
        
        speed_kmh = (dist_km / time_diff) * 3600
        
        location_risk = 0
        if speed_kmh > 900: # Faster than a plane
            location_risk = 100
            factors.append("Impossible Location Jump")
        elif speed_kmh > 200: # Very fast driving/train
            location_risk = 30
            
        # Combine Scores (Max or Weighted Avg)
        # We take the maximum specific behavioral risk
        behavioral_score = max(velocity_risk, deviation_risk, location_risk)
        
        return {
            'score': behavioral_score,
            'factors': factors,
            'details': {
                'velocity': recent_count,
                'avg_spending': round(avg_amount, 2),
                'dist_km': round(dist_km, 2)
            }
        }

# Global Instance
analyzer = BehavioralAnalyzer()

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        last_tx = analyzer.history[-1] if analyzer.history else None
        print(f"Received data: {data}")
        
        # 1. Extract Frontend Data
        amount = float(data.get('amount', 0))
        merchant = data.get('merchant', 'unknown')
        category = data.get('cardType', 'misc_net')  
        location_input = data.get('location', 'Unknown, UNK')
        time_str = data.get('time', '00:00')
        date_str = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # Parse City/State from location
        if ',' in location_input:
            city, state = [x.strip() for x in location_input.split(',', 1)]
        else:
            city, state = location_input, "UNK"

        # 2. Mock/Default Missing Features 
        # Smart Lat/Long Generation based on History & Input
        # This allows the user to DEMO the specific anomalies.
        # Smart Geolocation (Mock Geocoding)
        CITY_COORDS = {
            # --- India ---
            'kolkata': (22.5726, 88.3639), 'calcutta': (22.5726, 88.3639),
            'delhi': (28.7041, 77.1025), 'new delhi': (28.7041, 77.1025),
            'mumbai': (19.0760, 72.8777), 'bombay': (19.0760, 72.8777),
            'chennai': (13.0827, 80.2707), 'madras': (13.0827, 80.2707),
            'bangalore': (12.9716, 77.5946), 'bengaluru': (12.9716, 77.5946),
            'hyderabad': (17.3850, 78.4867),
            'pune': (18.5204, 73.8567),
            'ahmedabad': (23.0225, 72.5714),
            'jaipur': (26.9124, 75.7873),
            'surat': (21.1702, 72.8311),
            'lucknow': (26.8467, 80.9462),
            'kanpur': (26.4499, 80.3319),
            'indore': (22.7196, 75.8577),
            'bhopal': (23.2599, 77.4126),
            'patna': (25.5941, 85.1376),
            'vadodara': (22.3072, 73.1812),
            'ghaziabad': (28.6692, 77.4538),
            'ludhiana': (30.9010, 75.8573),
            'agra': (27.1767, 78.0081),
            'nashik': (19.9975, 73.7898),
            'faridabad': (28.4089, 77.3178),
            'meerut': (28.9845, 77.7064),
            'rajkot': (22.3039, 70.8022),
            'varanasi': (25.3176, 82.9739), 'banaras': (25.3176, 82.9739),
            'srinagar': (34.0837, 74.7973),
            'aurangabad': (19.8762, 75.3433),
            'dhanbad': (23.7957, 86.4304),
            'amritsar': (31.6340, 74.8723),
            'allahabad': (25.4358, 81.8463), 'prayagraj': (25.4358, 81.8463),
            'ranchi': (23.3441, 85.3096),
            'coimbatore': (11.0168, 76.9558),
            'jabalpur': (23.1815, 79.9864),
            'gwalior': (26.2183, 78.1828),
            'vijayawada': (16.5062, 80.6480),
            'jodhpur': (26.2389, 73.0243),
            'madurai': (9.9252, 78.1198),
            'raipur': (21.2514, 81.6296),
            'kota': (25.2138, 75.8648),
            'guwahati': (26.1445, 91.7362),
            'chandigarh': (30.7333, 76.7794),
            'mysore': (12.2958, 76.6394),
            'gurgaon': (28.4595, 77.0266), 'gurugram': (28.4595, 77.0266),
            'noida': (28.5355, 77.3910),
            'dehradun': (30.6340, 78.0297),
            'nagpur': (21.1458, 79.0882),
            'visakhapatnam': (17.6868, 83.2185), 'vizag': (17.6868, 83.2185),
            'kochi': (9.9312, 76.2673), 'cochin': (9.9312, 76.2673),
            'goa': (15.2993, 74.1240),
            'bhubaneswar': (20.2961, 85.8245),
            'thiruvananthapuram': (8.5241, 76.9366), 'trivandrum': (8.5241, 76.9366),
            
            # --- USA ---
            'new york': (40.7128, -74.0060), 'nyc': (40.7128, -74.0060),
            'los angeles': (34.0522, -118.2437), 'la': (34.0522, -118.2437),
            'san francisco': (37.7749, -122.4194), 'sf': (37.7749, -122.4194),
            'chicago': (41.8781, -87.6298),
            'washington dc': (38.9072, -77.0369), 'dc': (38.9072, -77.0369),
            'miami': (25.7617, -80.1918),
            'las vegas': (36.1699, -115.1398), 'vegas': (36.1699, -115.1398),
            'seattle': (47.6062, -122.3321),
            'boston': (42.3601, -71.0589),
            'houston': (29.7604, -95.3698),

            # --- Europe ---
            'london': (51.5074, -0.1278),
            'paris': (48.8566, 2.3522),
            'berlin': (52.5200, 13.4050),
            'madrid': (40.4168, -3.7038),
            'rome': (41.9028, 12.4964),
            'amsterdam': (52.3676, 4.9041),
            'zurich': (47.3769, 8.5417),
            'moscow': (55.7558, 37.6173),
            'istanbul': (41.0082, 28.9784),

            # --- Asia ---
            'tokyo': (35.6762, 139.6503),
            'singapore': (1.3521, 103.8198),
            'dubai': (25.2048, 55.2708),
            'beijing': (39.9042, 116.4074),
            'shanghai': (31.2304, 121.4737),
            'hong kong': (22.3193, 114.1694), 'hk': (22.3193, 114.1694),
            'bangkok': (13.7563, 100.5018),
            'seoul': (37.5665, 126.9780),
            'jakarta': (-6.2088, 106.8456),
            
            # --- Rest of World ---
            'sydney': (-33.8688, 151.2093),
            'melbourne': (-37.8136, 144.9631),
            'toronto': (43.6510, -79.3470),
            'vancouver': (49.2827, -123.1207),
            'mexico city': (19.4326, -99.1332),
            'rio de janeiro': (-22.9068, -43.1729), 'rio': (-22.9068, -43.1729),
            'sao paulo': (-23.5505, -46.6333),
            'cairo': (30.0444, 31.2357),
            'johannesburg': (-26.2041, 28.0473),
            'cape town': (-33.9249, 18.4241),
        }
        
        loc_lower = location_input.lower().strip()
        
        if loc_lower in CITY_COORDS:
            base_lat, base_long = CITY_COORDS[loc_lower]
            # Add small noise for realism within city (0.02 deg ~ 2km)
            lat = base_lat + random.uniform(-0.02, 0.02)
            long = base_long + random.uniform(-0.02, 0.02)
        else:
            # Deterministic Random based on name hash (So "UnknownCity" always maps to same place)
            # Use hash of string to seed
            seed_val = sum(ord(c) for c in loc_lower)
            random.seed(seed_val) 
            # Weighted towards India/Asia for demo probability
            if seed_val % 2 == 0:
                lat = random.uniform(8, 32) # India Lat
                long = random.uniform(70, 90) # India Long
            else:
                lat = random.uniform(-50, 60)
                long = random.uniform(-120, 140)
            random.seed() # Reset seed to clock

        # Clamp values
        lat = max(-90, min(90, lat))
        long = max(-180, min(180, long))
        
        merch_lat = lat + random.uniform(-0.1, 0.1)
        merch_long = long + random.uniform(-0.1, 0.1)
        city_pop = random.randint(10000, 1000000)
        job = "Engineer" 
        age = random.uniform(18, 90)
        trans_num = f"txn_{random.randint(100000, 999999)}"

        # Date/Time Processing
        try:
            t = datetime.strptime(time_str, "%H:%M").time()
            d = datetime.strptime(date_str, "%Y-%m-%d").date()
            trans_dt = datetime.combine(d, t)
        except:
            trans_dt = datetime.now()
        
        trans_date_trans_time_unix = trans_dt.timestamp()

        # 3. Model Logic
        risk_score = 0
        is_fraud = False
        
        if model:
            # ... (Existing Model Code) ...
            encoders = {}
            if os.path.exists('encoders.pkl'):
                try:
                    encoders = joblib.load('encoders.pkl')
                except:
                    pass

            def get_encoded_value(col_name, val):
                if col_name in encoders:
                    try:
                        return encoders[col_name].transform([str(val)])[0]
                    except:
                        return abs(hash(val)) % 10000
                else:
                    return abs(hash(val)) % 10000

            merchant_encoded = get_encoded_value('merchant', merchant)
            category_encoded = get_encoded_value('category', category)
            city_encoded = get_encoded_value('city', city)
            state_encoded = get_encoded_value('state', state)
            job_encoded = get_encoded_value('job', job)
            trans_num_encoded = get_encoded_value('trans_num', trans_num)

            features = np.array([[
                amount, lat, long, city_pop, merch_lat, merch_long, 
                merchant_encoded, category_encoded, city_encoded, state_encoded, 
                job_encoded, trans_num_encoded, age, trans_date_trans_time_unix
            ]])
            
            prediction = model.predict(features)[0]
            is_fraud = bool(prediction)
            
            if hasattr(model, 'predict_proba'):
                prob = model.predict_proba(features)[0][1] 
                risk_score = int(prob * 100)
            else:
                risk_score = 95 if is_fraud else 5

        else:
            # Simulation Logic
            if amount > 5000: risk_score += 40
            if "online" in merchant.lower(): risk_score += 15
            if location_input.lower() == "foreign": risk_score += 30
            risk_score += random.randint(0, 20)
            if risk_score > 100: risk_score = 99
            is_fraud = risk_score > 75
            
        # 4. Behavioral Analysis Fusion
        # Analyze BEFORE adding current (or AFTER? usually current is checked against past)
        # We check against past first.
        behavioral_result = analyzer.analyze(amount, lat, long, trans_date_trans_time_unix)
        
        # Update history
        analyzer.add_transaction(amount, lat, long, trans_date_trans_time_unix)
        
        # Fuse Scores: Take the higher of ML score or Behavioral Score
        final_risk_score = max(risk_score, behavioral_result['score'])
        if final_risk_score > 75: is_fraud = True
        
        # Generate Response
        response = {
            'isFraud': is_fraud,
            'riskScore': final_risk_score,
            'mlScore': risk_score,
            'behavioralScore': behavioral_result['score'],
            'riskFactors': behavioral_result['factors'],
            'details': behavioral_result['details'],
            'locationData': {
                'current': {'lat': lat, 'long': long},
                'previous': {'lat': last_tx['lat'], 'long': last_tx['long']} if last_tx else None
            },
            'message': 'Analysis complete'
        }
        print(f"Result: {response}")
        return jsonify(response)

    except Exception as e:
        print(f"Prediction error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ------------------------------------------------------------------------------
# GOOGLE SHEETS INTEGRATION
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# GOOGLE SHEETS INTEGRATION (WITH FALLBACK)
# ------------------------------------------------------------------------------
SHEET_URL = "https://docs.google.com/spreadsheets/d/1eAR4xzFW0Vd-R7-d0pgnYMmbORxW81_vmCSudnrUjkk/edit"
SIGNUP_GID = 0
SIGNIN_GID = 2080158186

class MockWorksheet:
    """Class to simulate Google Sheets but with LOCAL JSON PERSISTENCE."""
    def __init__(self, name):
        self.name = name
        self.db_file = 'local_db.json'
        self.data_store = self._load_data()
        print(f"[Info] Initialized Local DB for '{name}'. Data saved to {self.db_file}.")

    def _load_data(self):
        """Load specific sheet data from the single JSON DB file."""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    all_data = json.load(f)
                    return all_data.get(self.name, [])
            except:
                return []
        return []

    def _save_data(self):
        """Save current sheet data to the JSON DB file."""
        all_data = {}
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    all_data = json.load(f)
            except:
                pass
        
        all_data[self.name] = self.data_store
        
        with open(self.db_file, 'w') as f:
            json.dump(all_data, f, indent=4)

    def append_row(self, row):
        self.data_store.append(row)
        self._save_data()
        print(f"[Local DB] Appended row to {self.name}: {row}")
    
    def col_values(self, col_index):
        # Return list of values in that column (1-indexed in gspread, 0-indexed logic here)
        idx = col_index - 1
        return [row[idx] for row in self.data_store if len(row) > idx]

    def find(self, query):
        # Simple find, returns a MockCell or None
        for r_item, row in enumerate(self.data_store):
            for c_idx, cell_val in enumerate(row):
                if cell_val == query:
                    return type('MockCell', (), {'row': r_item + 1, 'col': c_idx + 1})
        return None

    def row_values(self, row_num):
        # 1-indexed row_num
        idx = row_num - 1
        if 0 <= idx < len(self.data_store):
            return self.data_store[idx]
        return []

    def get_worksheet_by_id(self, gid):
        return self

# Global instances (Loaded once)
MOCK_SIGNUP_SHEET = MockWorksheet("Signup Data")
MOCK_SIGNIN_SHEET = MockWorksheet("Signin Data")
    
def get_worksheet(gid):
    """Authenticates and returns the specific worksheet by GID. Falls back to Mock."""
    try:
        scope = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]
        
        if not os.path.exists('credentials.json'):
            print("Warning: credentials.json not found. Using Simulation Mode.")
            return MOCK_SIGNUP_SHEET if gid == SIGNUP_GID else MOCK_SIGNIN_SHEET
            
        creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
        client = gspread.authorize(creds)
        
        sh = client.open_by_url(SHEET_URL)
        return sh.get_worksheet_by_id(gid)

    except Exception as e:
        print(f"Error connecting to Google Sheets (GID {gid}): {e}. Using Simulation Mode.")
        return MOCK_SIGNUP_SHEET if gid == SIGNUP_GID else MOCK_SIGNIN_SHEET

@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        name = data.get('fullname')
        email = data.get('email')
        password = data.get('password') # In real app, hash this!
        
        print(f"Signup attempt for: {email}")
        
        sheet = get_worksheet(SIGNUP_GID)
        if sheet:
            # Check if user already exists
            try:
                # Basic check: Get all emails (Column C is usually 3)
                # Assuming columns: Name(A), Time(B), Email(C) based on user prompt order?
                # User prompt: "name , time ... , mail" 
                # Let's stick to: Col 1=Name, Col 2=Time, Col 3=Email
                existing_emails = sheet.col_values(3)
                if email in existing_emails:
                    return jsonify({'error': 'User already exists using this email.'}), 400
            except:
                pass # If sheet is empty or error, proceed

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Store: Name, Time, Mail
            sheet.append_row([name, timestamp, email, password]) # storing pwd for demo valid check
            print("Signup data saved.")
            return jsonify({'message': 'Signup successful', 'name': name, 'email': email})
        else:
            return jsonify({'error': 'Database connection failed'}), 500

    except Exception as e:
        print(f"Signup error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        print(f"Login attempt for: {email}")
        
        # 1. Verify User from Signup Sheet
        signup_sheet = get_worksheet(SIGNUP_GID)
        user_name = "Member" # Default
        
        if signup_sheet:
            try:
                cell = signup_sheet.find(email)
                if cell:
                    # Found user. In real app, check password (Col 4).
                    # For stored format [Name, Time, Email, Password]
                    # Name is Col 1.
                    row_vals = signup_sheet.row_values(cell.row)
                    # row_vals is list, 0-indexed. Name=0, Time=1, Email=2, Paswd=3
                    stored_pwd = row_vals[3] if len(row_vals) > 3 else ""
                    
                    if stored_pwd != password:
                         return jsonify({'error': 'Invalid password'}), 401
                    
                    user_name = row_vals[0]
                else:
                    return jsonify({'error': 'User not found. Please Sign Up first.'}), 404
            except gspread.CellNotFound:
                return jsonify({'error': 'User not found. Please Sign Up first.'}), 404
            except Exception as e:
                print(f"Auth check warning: {e}")
                # Fallback implementation if sheet struct differs
                pass
        
        # 2. Log to Signin Sheet
        signin_sheet = get_worksheet(SIGNIN_GID)
        if signin_sheet:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Store: Name, Time, Mail (as requested)
            signin_sheet.append_row([user_name, timestamp, email])
            print("Login logged.")
        else:
            print("Skipped saving to Login Sheet")

        return jsonify({'message': 'Login successful', 'name': user_name, 'email': email})

    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Flask Server...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, port=5000)


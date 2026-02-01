import pandas as pd
import numpy as np
import pickle
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from datetime import datetime
import os

# ------------------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------------------
CSV_FILENAME = 'credit_card_fraud_realistic_1000.csv'  # Updated to match user file
MODEL_FILENAME = 'fraud_detection_model.pkl'
ENCODERS_FILENAME = 'encoders.pkl'

def train():
    if not os.path.exists(CSV_FILENAME):
        print(f"Error: File '{CSV_FILENAME}' not found. Please rename your CSV file to '{CSV_FILENAME}' and place it in this folder.")
        return

    print("Loading data...")
    try:
        df = pd.read_csv(CSV_FILENAME)
        print(f"Loaded {len(df)} rows.")
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # --------------------------------------------------------------------------
    # PREPROCESSING
    # --------------------------------------------------------------------------
    print("Preprocessing data...")
    
    # 1. Target Variable
    # Look for 'is_fraud' or 'class' or similar
    target_col = None
    possible_targets = ['is_fraud', 'isFraud', 'Class', 'fraud']
    for col in possible_targets:
        if col in df.columns:
            target_col = col
            break
            
    if not target_col:
        print(f"Error: Could not find target column. Expected one of: {possible_targets}")
        return

    # 2. Date/Time Processing
    # Expected format: 'trans_date_trans_time' (YYYY-MM-DD HH:MM:SS)
    if 'trans_date_trans_time' in df.columns:
        df['trans_date_trans_time'] = pd.to_datetime(df['trans_date_trans_time'])
        df['trans_date_trans_time_unix'] = df['trans_date_trans_time'].astype('int64') // 10**9
    else:
        # Fallback if specific col missing, try to generate random/default or look for others
        print("Warning: 'trans_date_trans_time' column missing. Using placeholder.")
        df['trans_date_trans_time_unix'] = 0

    # 3. Age Calculation
    if 'dob' in df.columns:
        df['dob'] = pd.to_datetime(df['dob'])
        # Simple age calc
        df['age'] = (datetime.now() - df['dob']).dt.days // 365
    elif 'age' not in df.columns:
        print("Warning: 'dob' or 'age' column missing. Using default age 30.")
        df['age'] = 30

    # 4. Categorical Encoding
    encoders = {}
    cat_columns = ['merchant', 'category', 'city', 'state', 'job', 'trans_num']
    
    for col in cat_columns:
        if col in df.columns:
            print(f"Encoding {col}...")
            le = LabelEncoder()
            # Convert to string to handle mixed types
            df[col] = df[col].astype(str)
            df[f'{col}_encoded'] = le.fit_transform(df[col])
            encoders[col] = le
        else:
            print(f"Warning: Column '{col}' missing. Filling with 0.")
            df[f'{col}_encoded'] = 0

    # 5. Feature Selection
    # Must match app.py expected input order!
    # amount, lat, long, city_pop, merch_lat, merch_long, 
    # merchant_encoded, category_encoded, city_encoded, state_encoded, 
    # job_encoded, trans_num_encoded, age, trans_date_trans_time_unix
    
    feature_cols = [
        'amt', 'lat', 'long', 'city_pop', 'merch_lat', 'merch_long',
        'merchant_encoded', 'category_encoded', 'city_encoded', 'state_encoded',
        'job_encoded', 'trans_num_encoded', 'age', 'trans_date_trans_time_unix'
    ]
    
    # Handle map 'amt' to 'amount' if needed
    if 'amount' in df.columns and 'amt' not in df.columns:
        df['amt'] = df['amount']
    
    # Verify all features exist
    missing_features = [f for f in feature_cols if f not in df.columns]
    if missing_features:
        print(f"Error: Missing required columns: {missing_features}")
        return

    X = df[feature_cols]
    y = df[target_col]

    # --------------------------------------------------------------------------
    # TRAINING
    # --------------------------------------------------------------------------
    print("Training Random Forest Model (this may take a minute)...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)
    
    score = model.score(X_test, y_test)
    print(f"Training Complete! Accuracy: {score:.2%}")

    # --------------------------------------------------------------------------
    # SAVING
    # --------------------------------------------------------------------------
    print(f"Saving model to {MODEL_FILENAME}...")
    joblib.dump(model, MODEL_FILENAME)
    
    print(f"Saving encoders to {ENCODERS_FILENAME}...")
    joblib.dump(encoders, ENCODERS_FILENAME)
    
    print("Done! You can now run 'python app.py'.")

if __name__ == "__main__":
    train()

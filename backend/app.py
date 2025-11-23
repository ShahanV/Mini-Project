from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import numpy as np
import os
import pandas as pd

from xgboost import XGBRegressor   # ✅ use real XGBRegressor
import joblib                      # ✅ to load metadata

app = Flask(__name__)
CORS(app)

# ------------- Load the ML model + metadata -------------
try:
    # ✅ Load XGBoost model saved as JSON
    xgb = XGBRegressor()
    xgb.load_model("xgb_model.json")

    # ✅ Load metadata (threshold, slope, columns)
    model_meta = joblib.load("model_meta.pkl")

    DURATION_THRESHOLD = model_meta.get("threshold", 30)
    slope = float(model_meta["slope"])
    feature_columns = model_meta.get(
        "columns",
        ['Gender', 'Age', 'Height', 'Weight', 'Duration', 'Heart_Rate', 'Body_Temp']
    )

    print("XGBoost model and metadata loaded successfully!")
except Exception as e:
    print(f"Error loading model or metadata: {e}")
    xgb = None
    DURATION_THRESHOLD = 30
    slope = 0.0
    feature_columns = None

# Simple in-memory storage (use database in production)
users = {}
predictions_history = {}

# ------------- Hybrid prediction helper -------------
def hybrid_predict_from_features(features_dict):
    """
    features_dict: dict with keys matching model input features
                   e.g. {'Gender': 0, 'Age': 61, 'Height': 179, ...}

    Uses:
      - XGBoost for Duration <= threshold
      - Smooth continuation from XGBoost at threshold + slope * extra_time for Duration > threshold
    """
    # Build single-row DataFrame from input dict
    row_df = pd.DataFrame([features_dict])

    # Ensure all feature columns exist and are in correct order
    for col in feature_columns:
        if col not in row_df.columns:
            # If some column was present during training but not in request, fill with 0
            row_df[col] = 0

    row_df = row_df[feature_columns]

    duration_value = float(row_df['Duration'].iloc[0])

    if duration_value <= DURATION_THRESHOLD:
        return float(xgb.predict(row_df)[0])
    else:
        # Smooth continuation from XGBoost at DURATION_THRESHOLD
        row_thr = row_df.copy()
        row_thr['Duration'] = float(DURATION_THRESHOLD)
        base_at_thr = float(xgb.predict(row_thr)[0])
        extra_time = duration_value - DURATION_THRESHOLD
        return base_at_thr + slope * extra_time


@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if username in users:
        return jsonify({'success': False, 'message': 'User already exists'}), 400
    
    users[username] = password
    predictions_history[username] = []
    return jsonify({'success': True, 'message': 'Registration successful'}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if username not in users:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    if users[username] != password:
        return jsonify({'success': False, 'message': 'Invalid password'}), 401
    
    return jsonify({'success': True, 'message': 'Login successful', 'username': username}), 200


@app.route('/api/predict', methods=['POST'])
def predict():
    # lin is no longer needed, we use slope from metadata
    if xgb is None or feature_columns is None:
        return jsonify({'success': False, 'message': 'Model not loaded'}), 500
    
    try:
        data = request.json
        username = data.get('username')
        
        # Extract features from request
        gender_str = data.get('gender')
        # NOTE: make sure this matches your training encoding:
        # here: male -> 0, female -> 1
        gender = 0 if gender_str == 'male' else 1

        age = float(data.get('age'))
        height = float(data.get('height'))
        weight = float(data.get('weight'))
        duration = float(data.get('duration'))
        heart_rate = float(data.get('heart_rate'))
        body_temp = float(data.get('body_temp'))
        
        # Create feature dict (names must match training columns)
        features = {
            'Gender': gender,
            'Age': age,
            'Height': height,
            'Weight': weight,
            'Duration': duration,
            'Heart_Rate': heart_rate,
            'Body_Temp': body_temp
        }
        
        # Make prediction using hybrid model
        calories_burnt = hybrid_predict_from_features(features)
        
        # Store prediction in history
        prediction_record = {
            'id': len(predictions_history.get(username, [])) + 1,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'gender': gender_str,
            'age': age,
            'height': height,
            'weight': weight,
            'duration': duration,
            'heart_rate': heart_rate,
            'body_temp': body_temp,
            'calories_burnt': round(float(calories_burnt), 2)
        }
        
        if username not in predictions_history:
            predictions_history[username] = []
        
        predictions_history[username].append(prediction_record)
        
        return jsonify({
            'success': True,
            'calories_burnt': round(float(calories_burnt), 2),
            'prediction': prediction_record
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/history/<username>', methods=['GET'])
def get_history(username):
    if username not in predictions_history:
        return jsonify({'success': True, 'history': []}), 200
    
    return jsonify({
        'success': True,
        'history': predictions_history[username]
    }), 200


@app.route('/api/statistics/<username>', methods=['GET'])
def get_statistics(username):
    if username not in predictions_history or not predictions_history[username]:
        return jsonify({
            'success': True,
            'statistics': {
                'total_predictions': 0,
                'avg_calories': 0,
                'max_calories': 0,
                'min_calories': 0,
                'total_duration': 0
            }
        }), 200
    
    history = predictions_history[username]
    calories = [p['calories_burnt'] for p in history]
    durations = [p['duration'] for p in history]
    
    statistics = {
        'total_predictions': len(history),
        'avg_calories': round(sum(calories) / len(calories), 2),
        'max_calories': round(max(calories), 2),
        'min_calories': round(min(calories), 2),
        'total_duration': round(sum(durations), 2),
        'avg_duration': round(sum(durations) / len(durations), 2)
    }
    
    return jsonify({'success': True, 'statistics': statistics}), 200


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

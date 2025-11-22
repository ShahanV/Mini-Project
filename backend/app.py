from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import pickle
import numpy as np
import json
import os

app = Flask(__name__)
CORS(app)

# Load the ML model
try:
    with open('model.pkl', 'rb') as f:
        model = pickle.load(f)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Simple in-memory storage (use database in production)
users = {}
predictions_history = {}

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
    if model is None:
        return jsonify({'success': False, 'message': 'Model not loaded'}), 500
    
    try:
        data = request.json
        username = data.get('username')
        
        # Extract features
        gender = 1 if data.get('gender') == 'male' else 0
        age = float(data.get('age'))
        height = float(data.get('height'))
        weight = float(data.get('weight'))
        duration = float(data.get('duration'))
        heart_rate = float(data.get('heart_rate'))
        body_temp = float(data.get('body_temp'))
        
        # Create feature array (adjust order based on your model training)
        features = np.array([[gender, age, height, weight, duration, heart_rate, body_temp]])
        
        # Make prediction
        calories_burnt = model.predict(features)[0]
        
        # Store prediction in history
        prediction_record = {
            'id': len(predictions_history.get(username, [])) + 1,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'gender': data.get('gender'),
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
    app.run(debug=True, port=5000)
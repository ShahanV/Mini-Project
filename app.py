import streamlit as st
import pickle
import pandas as pd
import numpy as np
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="Calorie Burnt Tracker",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for beautiful styling
st.markdown("""
    <style>
    /* Main background gradient */
    .stApp {
        background: linear-gradient(135deg, #fff5f0 0%, #ffe5e5 50%, #ffebf0 100%);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #ea580c 0%, #dc2626 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(234, 88, 12, 0.3);
    }
    
    .main-header h1 {
        color: white;
        text-align: center;
        margin: 0;
        font-size: 3rem;
        font-weight: 800;
    }
    
    .main-header p {
        color: #fed7aa;
        text-align: center;
        margin: 0.5rem 0 0 0;
        font-size: 1.2rem;
    }
    
    /* Card styling */
    .stCard {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid #fed7aa;
    }
    
    /* Result card */
    .result-card {
        background: linear-gradient(135deg, #ea580c 0%, #dc2626 100%);
        padding: 3rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        box-shadow: 0 15px 40px rgba(234, 88, 12, 0.4);
        margin: 2rem 0;
        animation: slideIn 0.5s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .result-card h2 {
        font-size: 5rem;
        font-weight: 900;
        margin: 1rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        color: white;
    }
    
    .result-card p {
        font-size: 1.8rem;
        color: #fed7aa;
        margin: 0;
    }
    
    /* History card */
    .history-item {
        background: linear-gradient(90deg, #fff7ed 0%, #ffe4e6 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #ea580c;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #ea580c 0%, #dc2626 100%);
        color: white !important;
        font-weight: 700;
        font-size: 1.2rem;
        padding: 0.8rem 2rem;
        border-radius: 10px;
        border: none;
        box-shadow: 0 4px 6px rgba(234, 88, 12, 0.3);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(234, 88, 12, 0.4);
        color: white !important;
    }
    
    /* Input styling */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        border: 2px solid #fed7aa;
        border-radius: 8px;
        padding: 0.5rem;
        font-size: 1rem;
        color: #292524 !important;
        background-color: white !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #ea580c;
        box-shadow: 0 0 0 2px rgba(234, 88, 12, 0.1);
    }
    
    /* Radio button styling */
    .stRadio > div {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #fed7aa;
    }
    
    .stRadio > div label {
        color: #292524 !important;
    }
    
    .stRadio > div > div > div > label {
        color: #292524 !important;
    }
    
    .stRadio > div > div > div > label > div {
        color: #292524 !important;
    }
    
    .stRadio label[data-baseweb="radio"] {
        color: #292524 !important;
    }
    
    .stRadio label[data-baseweb="radio"] > div:last-child {
        color: #292524 !important;
    }
    
    .stRadio * {
        color: #292524 !important;
    }
    
    /* Force all radio text to be visible */
    [data-baseweb="radio"] * {
        color: #292524 !important;
    }
    
    /* Label styling */
    .stTextInput > label,
    .stNumberInput > label,
    .stSelectbox > label,
    .stRadio > label {
        font-weight: 600 !important;
        color: #292524 !important;
        font-size: 1rem !important;
    }
    
    /* Section headers */
    h3 {
        color: #292524 !important;
        font-weight: 700 !important;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        color: #292524 !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #57534e !important;
        font-weight: 600 !important;
    }
    
    /* Form styling */
    .stForm {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        border: 2px solid #fed7aa;
    }
    
    /* Divider */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 2px solid #fed7aa;
    }
    
    /* Error message */
    .stAlert {
        background-color: white !important;
        color: #dc2626 !important;
        border: 2px solid #fca5a5 !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #ea580c !important;
    }
    </style>
""", unsafe_allow_html=True)

# Load the model
@st.cache_resource
def load_model():
    try:
        with open('xgb_model.pkl', 'rb') as f:
            model = pickle.load(f)
        return model
    except FileNotFoundError:
        st.error("⚠️ Model file 'xgb_model.pkl' not found. Please upload the model file to the same directory.")
        return None

# Initialize session state for history
if 'history' not in st.session_state:
    st.session_state.history = []

# Header
st.markdown("""
    <div class="main-header">
        <h1>🔥 Calorie Burnt Tracker</h1>
        <p>Track your fitness journey with precision</p>
    </div>
""", unsafe_allow_html=True)

# Load model
model = load_model()

if model is not None:
    # Create two columns for layout
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("### 📊 Enter Your Details")
        
        # Create form
        with st.form("calorie_form"):
            # Gender
            gender = st.radio(
                "Gender",
                options=["Male", "Female"],
                horizontal=True
            )
            
            # Age
            age = st.number_input(
                "Age (years)",
                min_value=10,
                max_value=100,
                value=25,
                step=1
            )
            
            # Height
            height = st.number_input(
                "Height (cm)",
                min_value=100.0,
                max_value=250.0,
                value=170.0,
                step=0.1
            )
            
            # Weight
            weight = st.number_input(
                "Weight (kg)",
                min_value=30.0,
                max_value=200.0,
                value=70.0,
                step=0.1
            )
            
            # Duration
            duration = st.number_input(
                "Duration (minutes)",
                min_value=1.0,
                max_value=300.0,
                value=30.0,
                step=1.0
            )
            
            # Heart Rate
            heart_rate = st.number_input(
                "❤️ Heart Rate (bpm)",
                min_value=40.0,
                max_value=220.0,
                value=120.0,
                step=1.0
            )
            
            # Body Temperature
            body_temp = st.number_input(
                "🌡️ Body Temperature (°C)",
                min_value=35.0,
                max_value=42.0,
                value=37.0,
                step=0.1
            )
            
            # Submit button
            submitted = st.form_submit_button("🔥 Calculate Calories Burnt")
        
        if submitted:
            # Prepare data for prediction
            # Convert gender to binary (assuming your model uses 0/1)
            gender_binary = 0 if gender == "Male" else 1
            
            # Create dataframe with the same structure as training data
            input_data = pd.DataFrame({
                'Gender': [gender_binary],
                'Age': [age],
                'Height': [height],
                'Weight': [weight],
                'Duration': [duration],
                'Heart_Rate': [heart_rate],
                'Body_Temp': [body_temp]
            })
            
            # Make prediction
            with st.spinner("Calculating..."):
                prediction = model.predict(input_data)
                calories_burnt = int(round(prediction[0]))
            
            # Store in history
            history_entry = {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'calories': calories_burnt,
                'gender': gender,
                'age': age,
                'height': height,
                'weight': weight,
                'duration': duration,
                'heart_rate': heart_rate,
                'body_temp': body_temp
            }
            st.session_state.history.insert(0, history_entry)
            
            # Display result
            st.markdown(f"""
                <div class="result-card">
                    <p>Calories Burned</p>
                    <h2>{calories_burnt}</h2>
                    <p style="font-size: 1rem; margin-top: 1rem; color: #fed7aa;">🔥 Great workout!</p>
                </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📜 History")
        
        if len(st.session_state.history) > 0:
            # Clear history button
            if st.button("🗑️ Clear History"):
                st.session_state.history = []
                st.rerun()
            
            st.markdown("---")
            
            # Display history
            for idx, entry in enumerate(st.session_state.history):
                st.markdown(f"""
                    <div class="history-item">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <span style="font-size: 1.8rem; font-weight: 800; color: #ea580c;">
                                🔥 {entry['calories']} cal
                            </span>
                            <span style="font-size: 0.8rem; color: #78716c;">
                                {entry['timestamp']}
                            </span>
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; font-size: 0.9rem; color: #57534e;">
                            <div>⏱️ Duration: {entry['duration']} min</div>
                            <div>❤️ HR: {entry['heart_rate']} bpm</div>
                            <div>⚖️ Weight: {entry['weight']} kg</div>
                            <div>👤 Age: {entry['age']} yrs</div>
                            <div>📏 Height: {entry['height']} cm</div>
                            <div>🌡️ Temp: {entry['body_temp']}°C</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                if idx < len(st.session_state.history) - 1:
                    st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="text-align: center; padding: 3rem; color: #a8a29e;">
                    <div style="font-size: 4rem; margin-bottom: 1rem;">📅</div>
                    <p style="font-size: 1.2rem; color: #78716c;">No history yet</p>
                    <p style="color: #a8a29e;">Start tracking your workouts!</p>
                </div>
            """, unsafe_allow_html=True)
        
        # Statistics
        if len(st.session_state.history) > 0:
            st.markdown("---")
            st.markdown("### 📈 Statistics")
            
            total_calories = sum([entry['calories'] for entry in st.session_state.history])
            avg_calories = total_calories / len(st.session_state.history)
            max_calories = max([entry['calories'] for entry in st.session_state.history])
            total_workouts = len(st.session_state.history)
            
            stat_col1, stat_col2 = st.columns(2)
            
            with stat_col1:
                st.metric("Total Calories", f"{total_calories:.0f}")
                st.metric("Max Burn", f"{max_calories:.0f}")
            
            with stat_col2:
                st.metric("Average", f"{avg_calories:.0f}")
                st.metric("Total Workouts", total_workouts)

else:
    st.error("Unable to load the model. Please ensure 'xgb_model.pkl' is in the same directory as this script.")

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #a8a29e; padding: 2rem 0;">
        <p>Made with ❤️ for fitness enthusiasts | Track • Analyze • Improve</p>
    </div>
""", unsafe_allow_html=True)
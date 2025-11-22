import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder
import plotly.express as px
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Calorie Burnt Tracker",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;900&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container */
    .stApp {
        background: linear-gradient(135deg, #fef3c7 0%, #fed7aa 50%, #fdba74 100%);
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #ea580c 0%, #dc2626 100%);
        color: white;
        font-weight: 700;
        font-size: 1.2rem;
        padding: 1rem 3rem;
        border-radius: 50px;
        border: none;
        box-shadow: 0 10px 30px rgba(234, 88, 12, 0.3);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 40px rgba(234, 88, 12, 0.4);
        background: linear-gradient(135deg, #dc2626 0%, #ea580c 100%);
    }
    
    /* Input fields */
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 15px;
        border: 2px solid #fed7aa;
        padding: 0.8rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        background: white;
    }
    
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #ea580c;
        box-shadow: 0 0 0 3px rgba(234, 88, 12, 0.1);
    }
    
    /* Cards */
    .metric-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        border: 2px solid #fed7aa;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(234, 88, 12, 0.2);
    }
    
    /* History card */
    .history-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        border-left: 5px solid #ea580c;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .history-card:hover {
        transform: translateX(5px);
        box-shadow: 0 8px 20px rgba(234, 88, 12, 0.15);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: white;
        padding: 1rem;
        border-radius: 15px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 2rem;
        background: transparent;
        border-radius: 10px;
        color: #78716c;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #ea580c 0%, #dc2626 100%);
        color: white;
    }
    
    /* Remove padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Slider */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #ea580c 0%, #dc2626 100%);
    }
</style>
""", unsafe_allow_html=True)

# Load and train model
@st.cache_resource
def load_model():
    try:
        # Load dataset (you should replace this with your actual dataset path)
        # For demo purposes, I'll create sample data structure
        # Replace this with: df = pd.read_csv('your_dataset.csv')
        
        # Sample data structure - replace with your actual data loading
        np.random.seed(42)
        n_samples = 1000
        
        df = pd.DataFrame({
            'Gender': np.random.choice(['male', 'female'], n_samples),
            'Age': np.random.randint(18, 70, n_samples),
            'Height': np.random.randint(150, 200, n_samples),
            'Weight': np.random.randint(50, 120, n_samples),
            'Duration': np.random.randint(10, 60, n_samples),
            'Heart_Rate': np.random.randint(60, 180, n_samples),
            'Body_Temp': np.random.uniform(36.5, 40.0, n_samples)
        })
        
        # Calculate calories (sample formula - replace with your actual target)
        df['Calories'] = (
            0.5 * df['Weight'] + 
            0.3 * df['Duration'] + 
            0.4 * df['Heart_Rate'] + 
            10 * (df['Gender'] == 'male').astype(int) +
            np.random.normal(0, 20, n_samples)
        )
        
        # Encode gender
        le = LabelEncoder()
        df['Gender_Encoded'] = le.fit_transform(df['Gender'])
        
        # Features and target
        X = df[['Gender_Encoded', 'Age', 'Height', 'Weight', 'Duration', 'Heart_Rate', 'Body_Temp']]
        y = df['Calories']
        
        # Train model
        model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        return model, le
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None, None

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []

if 'page' not in st.session_state:
    st.session_state.page = 'home'

# Load model
model, le = load_model()

# HOME PAGE
if st.session_state.page == 'home':
    st.markdown("<div style='height: 5vh;'></div>", unsafe_allow_html=True)
    
    # Hero Section - using columns for better layout
    hero_html = """
    <div style="max-width: 1000px; margin: 0 auto; background: white; padding: 4rem 3rem; 
                border-radius: 30px; box-shadow: 0 25px 70px rgba(234, 88, 12, 0.2);
                text-align: center; border: 3px solid #fed7aa;
                background: linear-gradient(135deg, #ffffff 0%, #fff7ed 100%);">
        <div style="font-size: 6rem; margin-bottom: 1rem;">🔥</div>
        <h1 style="color: #ea580c; font-size: 4rem; font-weight: 900; 
                   margin-bottom: 1rem; text-shadow: 2px 2px 4px rgba(234, 88, 12, 0.1);
                   letter-spacing: -1px;">
            Calorie Burnt Tracker
        </h1>
        <p style="color: #78716c; font-size: 1.4rem; line-height: 1.9; 
                 margin-bottom: 2rem; max-width: 800px; margin-left: auto; 
                 margin-right: auto;">
            Transform your fitness journey with our <strong style="color: #ea580c;">AI-powered</strong> 
            calorie tracking system. Get accurate predictions based on your unique body metrics 
            and workout intensity.
        </p>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 3vh;'></div>", unsafe_allow_html=True)
    
    # Get Started Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔥 GET STARTED NOW", use_container_width=True):
            st.session_state.page = 'tracker'
            st.rerun()
    
    st.markdown("<div style='height: 3vh;'></div>", unsafe_allow_html=True)

# TRACKER PAGE
elif st.session_state.page == 'tracker':
    if model is not None:
        # Header with back button
        col_back, col_space = st.columns([1, 11])
        with col_back:
            if st.button("← Back", key="back_home"):
                st.session_state.page = 'home'
                st.rerun()
        
        st.markdown("""
            <div style="text-align: center; margin-bottom: 2rem;">
                <h1 style="color: #ea580c; font-size: 3.5rem; font-weight: 900; 
                           margin-bottom: 0.5rem;">
                    🔥 Calorie Tracker Dashboard
                </h1>
                <p style="color: #78716c; font-size: 1.2rem;">
                    Track your fitness journey with precision
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Create tabs
        tab1, tab2 = st.tabs(["📊 Calculate Calories", "📈 History & Analytics"])
        
        with tab1:
            col1, col2 = st.columns([1, 1], gap="large")
            
            with col1:
                st.markdown("""
                    <div style="background: white; padding: 2rem; border-radius: 20px;
                                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                                border: 2px solid #fed7aa;">
                        <div style="text-align: center; margin-bottom: 1.5rem;">
                            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📋</div>
                            <h2 style="color: #ea580c; font-weight: 700; margin: 0;">
                                Your Fitness Metrics
                            </h2>
                            <p style="color: #78716c; font-size: 0.95rem; margin-top: 0.5rem;">
                                Enter your workout details below
                            </p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
                
                # Input fields
                gender = st.selectbox("👤 Gender", ["male", "female"], index=0)
                age = st.number_input("🎂 Age (years)", min_value=10, max_value=100, value=25)
                height = st.number_input("📏 Height (cm)", min_value=100, max_value=250, value=170)
                weight = st.number_input("⚖️ Weight (kg)", min_value=30, max_value=200, value=70)
                duration = st.number_input("⏱️ Duration (minutes)", min_value=1, max_value=180, value=30)
                heart_rate = st.number_input("💓 Heart Rate (bpm)", min_value=40, max_value=200, value=100)
                body_temp = st.number_input("🌡️ Body Temperature (°C)", min_value=35.0, max_value=42.0, value=37.0, step=0.1)
                
                st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
                
                # Calculate button
                if st.button("🔥 CALCULATE CALORIES", use_container_width=True, key="calc_btn"):
                    # Prepare input
                    gender_encoded = le.transform([gender])[0]
                    input_data = np.array([[gender_encoded, age, height, weight, duration, heart_rate, body_temp]])
                    
                    # Predict
                    calories = model.predict(input_data)[0]
                    
                    # Add to history
                    st.session_state.history.append({
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'gender': gender,
                        'age': age,
                        'height': height,
                        'weight': weight,
                        'duration': duration,
                        'heart_rate': heart_rate,
                        'body_temp': body_temp,
                        'calories': round(calories, 2)
                    })
                    
                    st.success("✅ Calculation complete!")
                    st.rerun()
            
            with col2:
                # Results container
                if st.session_state.history:
                    latest = st.session_state.history[-1]
                    
                    st.markdown(f"""
                        <div style="background: white; padding: 2.5rem; border-radius: 20px;
                                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                                    border: 2px solid #fed7aa; min-height: 500px;">
                            <div style="text-align: center; margin-bottom: 1rem;">
                                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🔥</div>
                                <h2 style="color: #ea580c; font-weight: 700; margin: 0;">
                                    Your Results
                                </h2>
                                <p style="color: #78716c; font-size: 0.95rem; margin-top: 0.5rem;">
                                    Calories burned during this workout
                                </p>
                            </div>
                            <div style="text-align: center; margin: 2.5rem 0; 
                                        background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%);
                                        padding: 2rem; border-radius: 15px;
                                        border: 2px solid #fed7aa;">
                                <div style="font-size: 4.5rem; font-weight: 900; 
                                           background: linear-gradient(135deg, #ea580c 0%, #dc2626 100%);
                                           -webkit-background-clip: text;
                                           -webkit-text-fill-color: transparent;
                                           background-clip: text;
                                           line-height: 1;">
                                    {latest['calories']}
                                </div>
                                <div style="color: #78716c; font-size: 1.3rem; font-weight: 600; margin-top: 0.8rem;">
                                    Calories Burned
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
                    
                    # Workout summary in separate cards
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown(f"""
                            <div style="background: white; padding: 1.5rem; border-radius: 15px;
                                        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
                                        border: 2px solid #fed7aa; text-align: center; margin-bottom: 1rem;">
                                <div style="color: #78716c; font-size: 0.9rem; margin-bottom: 0.5rem;">⏱️ Duration</div>
                                <div style="color: #ea580c; font-size: 1.8rem; font-weight: 700;">{latest['duration']} min</div>
                            </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f"""
                            <div style="background: white; padding: 1.5rem; border-radius: 15px;
                                        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
                                        border: 2px solid #fed7aa; text-align: center;">
                                <div style="color: #78716c; font-size: 0.9rem; margin-bottom: 0.5rem;">💓 Heart Rate</div>
                                <div style="color: #ea580c; font-size: 1.8rem; font-weight: 700;">{latest['heart_rate']} bpm</div>
                            </div>
                        """, unsafe_allow_html=True)
                    with col_b:
                        st.markdown(f"""
                            <div style="background: white; padding: 1.5rem; border-radius: 15px;
                                        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
                                        border: 2px solid #fed7aa; text-align: center; margin-bottom: 1rem;">
                                <div style="color: #78716c; font-size: 0.9rem; margin-bottom: 0.5rem;">⚖️ Weight</div>
                                <div style="color: #ea580c; font-size: 1.8rem; font-weight: 700;">{latest['weight']} kg</div>
                            </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f"""
                            <div style="background: white; padding: 1.5rem; border-radius: 15px;
                                        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
                                        border: 2px solid #fed7aa; text-align: center;">
                                <div style="color: #78716c; font-size: 0.9rem; margin-bottom: 0.5rem;">🌡️ Body Temp</div>
                                <div style="color: #ea580c; font-size: 1.8rem; font-weight: 700;">{latest['body_temp']}°C</div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                        <div style="background: white; padding: 2rem; border-radius: 20px;
                                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                                    border: 2px solid #fed7aa; min-height: 500px;
                                    display: flex; align-items: center; justify-content: center;">
                            <div style="text-align: center; color: #78716c;">
                                <div style="font-size: 4rem; margin-bottom: 1rem;">📊</div>
                                <h2 style="color: #ea580c; margin-bottom: 1rem;">Results</h2>
                                <p style="font-size: 1.1rem;">👆 Enter your details and click 'Calculate Calories' to see results!</p>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        
        with tab2:
            if st.session_state.history:
                st.markdown("""
                    <h2 style="color: #ea580c; font-weight: 700; margin-bottom: 1.5rem;">
                        Your Fitness Journey
                    </h2>
                """, unsafe_allow_html=True)
                
                # Convert to dataframe
                df_history = pd.DataFrame(st.session_state.history)
                
                # Calculate y-axis range for better visualization
                min_cal = df_history['calories'].min()
                max_cal = df_history['calories'].max()
                y_range = max_cal - min_cal
                y_padding = max(y_range * 0.2, 10)  # At least 10 units padding
                
                # Chart with better styling
                fig = px.line(df_history, x='timestamp', y='calories',
                             title='Calories Burned Over Time')
                fig.update_traces(
                    line_color='#ea580c', 
                    line_width=4,
                    marker=dict(size=12, color='#dc2626', line=dict(width=2, color='white')),
                    fill='tozeroy',
                    fillcolor='rgba(234, 88, 12, 0.1)'
                )
                fig.update_layout(
                    plot_bgcolor='rgba(255, 247, 237, 0.5)',
                    paper_bgcolor='white',
                    font=dict(family='Poppins', size=14, color='#292524'),
                    title=dict(
                        text='🔥 Calories Burned Over Time',
                        font=dict(size=24, color='#ea580c', family='Poppins'),
                        x=0.5,
                        xanchor='center'
                    ),
                    xaxis=dict(
                        title='Workout Sessions',
                        gridcolor='rgba(234, 88, 12, 0.1)',
                        showgrid=True,
                        zeroline=False
                    ),
                    yaxis=dict(
                        title='Calories Burned',
                        gridcolor='rgba(234, 88, 12, 0.1)',
                        showgrid=True,
                        zeroline=False,
                        range=[min_cal - y_padding, max_cal + y_padding]
                    ),
                    hovermode='x unified',
                    margin=dict(l=60, r=40, t=80, b=60),
                    height=450
                )
                
                # Add a container for the chart
                st.markdown("""
                    <div style="background: white; padding: 1.5rem; border-radius: 20px;
                                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                                border: 2px solid #fed7aa; margin-bottom: 2rem;">
                    </div>
                """, unsafe_allow_html=True)
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div style="color: #ea580c; font-size: 2rem; font-weight: 900;">
                                {len(df_history)}
                            </div>
                            <div style="color: #78716c;">Total Workouts</div>
                        </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div style="color: #ea580c; font-size: 2rem; font-weight: 900;">
                                {round(df_history['calories'].sum(), 0)}
                            </div>
                            <div style="color: #78716c;">Total Calories</div>
                        </div>
                    """, unsafe_allow_html=True)
                with col3:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div style="color: #ea580c; font-size: 2rem; font-weight: 900;">
                                {round(df_history['calories'].mean(), 0)}
                            </div>
                            <div style="color: #78716c;">Avg Calories</div>
                        </div>
                    """, unsafe_allow_html=True)
                with col4:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div style="color: #ea580c; font-size: 2rem; font-weight: 900;">
                                {round(df_history['duration'].sum(), 0)}
                            </div>
                            <div style="color: #78716c;">Total Minutes</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
                
                # Recent activity
                st.markdown("""
                    <h3 style="color: #292524; font-weight: 700; margin-bottom: 1rem;">
                        Recent Activity
                    </h3>
                """, unsafe_allow_html=True)
                
                for record in reversed(st.session_state.history[-5:]):
                    st.markdown(f"""
                        <div class="history-card">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <div style="color: #292524; font-weight: 700; font-size: 1.1rem;">
                                        {record['calories']} calories
                                    </div>
                                    <div style="color: #78716c; font-size: 0.9rem;">
                                        {record['timestamp']} • {record['duration']} min • {record['heart_rate']} bpm
                                    </div>
                                </div>
                                <div style="font-size: 2rem;">🔥</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Clear history button
                st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
                if st.button("🗑️ Clear History", key="clear_hist"):
                    st.session_state.history = []
                    st.rerun()
            else:
                st.info("📊 No workout history yet. Start calculating calories to see your progress!")
    else:
        st.error("❌ Failed to load the model. Please check your dataset and try again.")
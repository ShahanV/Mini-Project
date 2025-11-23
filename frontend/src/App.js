import React, { useState, useEffect, useCallback } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Flame, Activity, User, Lock, TrendingUp, Calendar, Clock } from 'lucide-react';

const API_URL = 'https://mini-project-rijs.onrender.com/api';

// Custom Tooltip Component
const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-white p-4 border-2 border-orange-500 rounded-xl shadow-xl">
        <p className="text-xs text-gray-500 mb-2">{data.date}</p>
        <div className="space-y-1">
          <p className="text-sm font-semibold text-orange-600">
            🔥 Calories: {data.calories_burnt} kcal
          </p>
          <p className="text-sm text-gray-700">
            ⏱️ Duration: {data.duration} min
          </p>
          <p className="text-sm text-gray-700">
            💓 Heart Rate: {data.heart_rate} bpm
          </p>
          <p className="text-sm text-gray-700">
            🌡️ Body Temp: {data.body_temp}°C
          </p>
        </div>
      </div>
    );
  }
  return null;
};

export default function CalorieBurntTracker() {
  const [currentPage, setCurrentPage] = useState('login');
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loggedInUser, setLoggedInUser] = useState(null);
  const [formData, setFormData] = useState({
    gender: 'male',
    age: '',
    height: '',
    weight: '',
    duration: '',
    heart_rate: '',
    body_temp: ''
  });
  const [prediction, setPrediction] = useState(null);
  const [history, setHistory] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchHistory = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/history/${loggedInUser}`);
      const data = await response.json();
      if (data.success) setHistory(data.history);
    } catch (error) {
      console.error('Error fetching history:', error);
    }
  }, [loggedInUser]);

  const fetchStatistics = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/statistics/${loggedInUser}`);
      const data = await response.json();
      if (data.success) setStatistics(data.statistics);
    } catch (error) {
      console.error('Error fetching statistics:', error);
    }
  }, [loggedInUser]);

  useEffect(() => {
    if (loggedInUser && currentPage === 'history') {
      fetchHistory();
      fetchStatistics();
    }
  }, [loggedInUser, currentPage, fetchHistory, fetchStatistics]);

  const handleAuth = async () => {
    setLoading(true);
    const endpoint = isLogin ? '/login' : '/register';
    
    try {
      const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setLoggedInUser(username);
        setCurrentPage('predict');
        setPassword('');
      } else {
        alert(data.message);
      }
    } catch (error) {
      alert('Cannot connect to server. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const handlePredict = async () => {
    setLoading(true);
    
    try {
      const response = await fetch(`${API_URL}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...formData, username: loggedInUser })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setPrediction(data.calories_burnt);
        // Stays visible until user makes another prediction
      } else {
        alert(data.message);
      }
    } catch (error) {
      alert('Prediction error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setLoggedInUser(null);
    setCurrentPage('login');
    setUsername('');
    setFormData({
      gender: 'male',
      age: '',
      height: '',
      weight: '',
      duration: '',
      heart_rate: '',
      body_temp: ''
    });
  };

  // Login/Register Page
  if (currentPage === 'login') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-500 via-red-500 to-pink-500 flex items-center justify-center p-4">
        <div className="absolute inset-0 bg-black opacity-10"></div>
        
        <div className="relative bg-white rounded-3xl shadow-2xl p-8 w-full max-w-md transform transition-all">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-orange-500 to-red-500 rounded-full mb-4 shadow-lg">
              <Flame className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">
              Calorie Burnt Tracker
            </h1>
            <p className="text-gray-600 mt-2">Track your fitness journey</p>
          </div>

          <div className="flex gap-2 mb-6 bg-gray-100 rounded-full p-1">
            <button
              onClick={() => setIsLogin(true)}
              className={`flex-1 py-2 rounded-full font-medium transition-all ${
                isLogin ? 'bg-white shadow-md text-orange-600' : 'text-gray-600'
              }`}
            >
              Login
            </button>
            <button
              onClick={() => setIsLogin(false)}
              className={`flex-1 py-2 rounded-full font-medium transition-all ${
                !isLogin ? 'bg-white shadow-md text-orange-600' : 'text-gray-600'
              }`}
            >
              Register
            </button>
          </div>

          <div className="space-y-4">
            <div className="relative">
              <User className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAuth()}
                className="w-full pl-10 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:border-orange-500 focus:outline-none transition-colors"
              />
            </div>
            
            <div className="relative">
              <Lock className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAuth()}
                className="w-full pl-10 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:border-orange-500 focus:outline-none transition-colors"
              />
            </div>

            <button
              onClick={handleAuth}
              disabled={loading}
              className="w-full bg-gradient-to-r from-orange-500 to-red-500 text-white py-3 rounded-xl font-semibold hover:shadow-lg transform hover:-translate-y-0.5 transition-all disabled:opacity-50"
            >
              {loading ? 'Processing...' : isLogin ? 'Login' : 'Register'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Main App (Predict & History)
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-orange-500 to-red-500 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Flame className="w-8 h-8" />
              <h1 className="text-2xl font-bold">Calorie Burnt Tracker</h1>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-white/90">Welcome, {loggedInUser}</span>
              <button
                onClick={handleLogout}
                className="bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex gap-1">
            <button
              onClick={() => setCurrentPage('predict')}
              className={`px-6 py-4 font-medium transition-all ${
                currentPage === 'predict'
                  ? 'border-b-2 border-orange-500 text-orange-600'
                  : 'text-gray-600 hover:text-orange-600'
              }`}
            >
              Calculate Calories
            </button>
            <button
              onClick={() => setCurrentPage('history')}
              className={`px-6 py-4 font-medium transition-all ${
                currentPage === 'history'
                  ? 'border-b-2 border-orange-500 text-orange-600'
                  : 'text-gray-600 hover:text-orange-600'
              }`}
            >
              History & Statistics
            </button>
          </div>
        </div>
      </div>

      {/* Prediction Page */}
      {currentPage === 'predict' && (
        <div className="max-w-4xl mx-auto p-6">
          <div className="bg-white rounded-2xl shadow-lg p-8 mb-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
              <Activity className="w-7 h-7 text-orange-500" />
              Calculate Calories Burnt
            </h2>

            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Gender</label>
                  <select
                    value={formData.gender}
                    onChange={(e) => setFormData({...formData, gender: e.target.value})}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-orange-500 focus:outline-none"
                  >
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Age (years)</label>
                  <input
                    type="number"
                    value={formData.age}
                    onChange={(e) => setFormData({...formData, age: e.target.value})}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-orange-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Height (cm)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={formData.height}
                    onChange={(e) => setFormData({...formData, height: e.target.value})}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-orange-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Weight (kg)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={formData.weight}
                    onChange={(e) => setFormData({...formData, weight: e.target.value})}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-orange-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Duration (minutes)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={formData.duration}
                    onChange={(e) => setFormData({...formData, duration: e.target.value})}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-orange-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Heart Rate (bpm)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={formData.heart_rate}
                    onChange={(e) => setFormData({...formData, heart_rate: e.target.value})}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-orange-500 focus:outline-none"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Body Temperature (°C)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={formData.body_temp}
                    onChange={(e) => setFormData({...formData, body_temp: e.target.value})}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-orange-500 focus:outline-none"
                  />
                </div>
              </div>

              <button
                onClick={handlePredict}
                disabled={loading}
                className="w-full bg-gradient-to-r from-orange-500 to-red-500 text-white py-4 rounded-xl font-semibold text-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all disabled:opacity-50"
              >
                {loading ? 'Calculating...' : 'Calculate Calories Burnt 🔥'}
              </button>
            </div>
          </div>

          {/* Result Display */}
          {prediction && (
            <div className="bg-gradient-to-r from-orange-500 to-red-500 rounded-2xl shadow-xl p-8 text-white relative">
              <button
                onClick={() => setPrediction(null)}
                className="absolute top-4 right-4 bg-white/20 hover:bg-white/30 rounded-full p-2 transition-colors"
              >
                <span className="text-xl">×</span>
              </button>
              <div className="text-center">
                <Flame className="w-16 h-16 mx-auto mb-4" />
                <h3 className="text-2xl font-semibold mb-2">Calories Burnt</h3>
                <p className="text-6xl font-bold">{prediction}</p>
                <p className="text-xl mt-2 opacity-90">kcal</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* History & Statistics Page */}
      {currentPage === 'history' && (
        <div className="max-w-7xl mx-auto p-6">
          {/* Statistics Cards */}
          {statistics && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-white rounded-xl shadow-md p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600 text-sm">Total Workouts</p>
                    <p className="text-3xl font-bold text-orange-600">{statistics.total_predictions}</p>
                  </div>
                  <Activity className="w-10 h-10 text-orange-500 opacity-50" />
                </div>
              </div>

              <div className="bg-white rounded-xl shadow-md p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600 text-sm">Avg Calories</p>
                    <p className="text-3xl font-bold text-red-600">{statistics.avg_calories}</p>
                  </div>
                  <Flame className="w-10 h-10 text-red-500 opacity-50" />
                </div>
              </div>

              <div className="bg-white rounded-xl shadow-md p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600 text-sm">Max Calories</p>
                    <p className="text-3xl font-bold text-pink-600">{statistics.max_calories}</p>
                  </div>
                  <TrendingUp className="w-10 h-10 text-pink-500 opacity-50" />
                </div>
              </div>

              <div className="bg-white rounded-xl shadow-md p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600 text-sm">Total Duration</p>
                    <p className="text-3xl font-bold text-purple-600">{statistics.total_duration}</p>
                  </div>
                  <Clock className="w-10 h-10 text-purple-500 opacity-50" />
                </div>
              </div>
            </div>
          )}

          {/* Charts */}
          {history.length > 0 && (
            <div className="bg-white rounded-xl shadow-md p-6 mb-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-gray-800">📈 Calorie Burning Progress</h3>
                <div className="text-sm text-gray-500">
                  Last {Math.min(history.length, 10)} workouts
                </div>
              </div>
              
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={history.slice(-10)} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                    <defs>
                      <linearGradient id="colorCalories" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#f97316" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#f97316" stopOpacity={0.1}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis 
                      dataKey="id" 
                      label={{ value: 'Workout #', position: 'insideBottom', offset: -5 }}
                      tick={{ fill: '#666' }}
                    />
                    <YAxis 
                      label={{ value: 'Calories (kcal)', angle: -90, position: 'insideLeft' }}
                      tick={{ fill: '#666' }}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Line 
                      type="monotone" 
                      dataKey="calories_burnt" 
                      stroke="#f97316" 
                      strokeWidth={3}
                      dot={{ fill: '#f97316', r: 5 }}
                      activeDot={{ r: 7, fill: '#ea580c' }}
                      fill="url(#colorCalories)"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* Summary Stats Below Chart */}
              <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t border-gray-200">
                <div className="text-center">
                  <p className="text-2xl font-bold text-orange-600">
                    {history.length > 0 ? Math.max(...history.map(h => h.calories_burnt)) : 0}
                  </p>
                  <p className="text-xs text-gray-600 mt-1">Peak Calories</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-red-600">
                    {history.length > 0 ? (history.reduce((sum, h) => sum + h.calories_burnt, 0) / history.length).toFixed(0) : 0}
                  </p>
                  <p className="text-xs text-gray-600 mt-1">Average Calories</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-pink-600">
                    {history.reduce((sum, h) => sum + h.calories_burnt, 0).toFixed(0)}
                  </p>
                  <p className="text-xs text-gray-600 mt-1">Total Burned</p>
                </div>
              </div>
            </div>
          )}

          {/* History Table */}
          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <Calendar className="w-5 h-5 text-orange-500" />
              Workout History
            </h3>
            
            {history.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No workout history yet. Start tracking your calories!</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b-2 border-gray-200">
                      <th className="text-left py-3 px-4 text-gray-600 font-semibold">Date</th>
                      <th className="text-left py-3 px-4 text-gray-600 font-semibold">Duration</th>
                      <th className="text-left py-3 px-4 text-gray-600 font-semibold">Heart Rate</th>
                      <th className="text-left py-3 px-4 text-gray-600 font-semibold">Calories</th>
                    </tr>
                  </thead>
                  <tbody>
                    {history.slice().reverse().map((record) => (
                      <tr key={record.id} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-4">{record.date}</td>
                        <td className="py-3 px-4">{record.duration} min</td>
                        <td className="py-3 px-4">{record.heart_rate} bpm</td>
                        <td className="py-3 px-4">
                          <span className="bg-orange-100 text-orange-700 px-3 py-1 rounded-full font-semibold">
                            {record.calories_burnt} kcal
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
# STREAMLIT WEATHER FORECAST APP
import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import pytz
import folium
from streamlit_folium import folium_static
import json
import os

# Set page config for better appearance
st.set_page_config(
    page_title="Weather Forecast App",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .weather-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 5px solid #667eea;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
    .day-night-card {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }
    .time-display {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# STRETCH GOAL A: Date and Time Display Functions
def display_date_time(location_name, timezone_offset):
    """Display current date and time for user and location"""
    # Get user's local time
    local_time = datetime.now()
    formatted_local = local_time.strftime("%A, %B %d, %Y, %I:%M %p")
    
    # Calculate location time based on timezone offset
    location_time = local_time + timedelta(seconds=timezone_offset)
    formatted_location = location_time.strftime("%A, %B %d, %Y, %I:%M %p")
    
    return formatted_local, formatted_location

# STRETCH GOAL B: Settings Management Functions
def load_settings():
    """Load user settings from JSON file"""
    if os.path.exists('settings.json'):
        with open('settings.json', 'r') as f:
            return json.load(f)
    return {"default_location": "", "favorites": [], "temp_unit": "celsius"}

def save_settings(settings):
    """Save user settings to JSON file"""
    with open('settings.json', 'w') as f:
        json.dump(settings, f, indent=2)

def manage_settings():
    """Manage user settings in sidebar"""
    settings = load_settings()
    
    st.sidebar.markdown("### ⚙️ Settings")
    
    # Default location setting
    default = st.sidebar.text_input("Default Location", settings.get("default_location", ""))
    if default != settings.get("default_location", ""):
        settings["default_location"] = default
        save_settings(settings)
    
    # Temperature unit preference
    temp_unit = st.sidebar.selectbox("Temperature Unit", ["celsius", "fahrenheit"], 
                                    index=0 if settings.get("temp_unit") == "celsius" else 1)
    if temp_unit != settings.get("temp_unit"):
        settings["temp_unit"] = temp_unit
        save_settings(settings)
    
    # Favorite locations management
    st.sidebar.markdown("#### Favorites")
    new_favorite = st.sidebar.text_input("Add Favorite Location")
    if st.sidebar.button("Add") and new_favorite:
        if new_favorite not in settings.get("favorites", []):
            settings["favorites"] = settings.get("favorites", []) + [new_favorite]
            save_settings(settings)
    
    # Display and manage favorites
    favorites = settings.get("favorites", [])
    if favorites:
        st.sidebar.markdown("**Your favorites:**")
        for fav in favorites:
            col1, col2 = st.sidebar.columns([4, 1])
            col1.write(fav)
            if col2.button("❌", key=f"remove_{fav}", help="Remove from favorites"):
                settings["favorites"] = [f for f in favorites if f != fav]
                save_settings(settings)
                st.rerun()
    
    return settings

# STRETCH GOAL C: Map Functions
def create_location_map(lat, lon, city_name):
    """Create an interactive map for the location"""
    m = folium.Map(location=[lat, lon], zoom_start=10, tiles='OpenStreetMap')
    folium.Marker([lat, lon], popup=city_name).add_to(m)
    return m

# Day Night Function
def agg_day_night(df_weather, variables):
    """Aggregate weather data by day/night periods"""
    df_weather['hour'] = df_weather['time'].dt.hour
    df_weather['period'] = df_weather['hour'].apply(lambda h: 'Day' if 6 <= h < 18 else 'Night')
    df_weather['date'] = df_weather['time'].dt.date
    agg = df_weather.groupby(['date', 'period'])[['temp', 'humidity']].mean().reset_index()
    return (agg)

# Plotting functions from notebook
def plot_feels_like_comparison(df_weather):
    """Create temperature vs feels like comparison chart"""
    df_weather['time'] = pd.to_datetime(df_weather['time'])
    now = pd.Timestamp.now()
    next_week = now + pd.Timedelta(days=7)
    df_week = df_weather[(df_weather['time'] <= next_week) & (df_weather['time'] >= now)].copy()

    # Create comparison chart
    fig, ax = plt.subplots(figsize=(18, 6))

    # Plot both lines with different colors and styles
    ax.plot(df_week['time'], df_week['temp'],
            marker='o', color='#FF6B6B', linewidth=3, markersize=8,
            label='Actual Temperature', alpha=0.8)
    ax.plot(df_week['time'], df_week['feels_like'],
            marker='s', color='#4ECDC4', linewidth=3, markersize=8,
            label='Feels Like', alpha=0.8)

    # Enhanced styling
    ax.set_title('🌡️ Temperature vs Feels Like Comparison', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Date & Time', fontsize=12)
    ax.set_ylabel('Temperature (°C)', fontsize=12)
    ax.legend(fontsize=12, loc='upper right')
    ax.grid(True, alpha=0.3, linestyle='--')

    # Add value annotations on points
    for idx, row in df_week.iterrows():
        ax.annotate(f'{row["temp"]:.1f}',
                    (row['time'], row['temp']),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha='center',
                    fontsize=8, color='#FF6B6B')
        ax.annotate(f'{row["feels_like"]:.1f}',
                    (row['time'], row['feels_like']),
                    textcoords="offset points",
                    xytext=(0, -15),
                    ha='center',
                    fontsize=8, color='#4ECDC4')

    # Improve X-axis formatting
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m/%d %H:%M'))
    ax.xaxis.set_major_locator(plt.matplotlib.dates.HourLocator(interval=6))
    ax.tick_params(axis='x', rotation=45, labelsize=10)

    plt.tight_layout()
    return fig

def plot_weather_3_charts(df_weather, variables):
    """Create multi-variable weather forecast charts"""
    df_weather['time'] = pd.to_datetime(df_weather['time'])
    now = pd.Timestamp.now()
    next_week = now + pd.Timedelta(days=7)
    df_week = df_weather[(df_weather['time'] <= next_week) & (df_weather['time'] >= now)].copy()

    # Improved chart appearance
    fig, axes = plt.subplots(len(variables), 1, figsize=(18, 12), sharex=True)
    if len(variables) == 1:
        axes = [axes]

    # Beautiful gradient colors
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']  # Red, Teal, Blue
    titles = ['🌡️ Temperature Forecast', '💧 Humidity Forecast', '💨 Wind Speed Forecast']
    units = ['°C', '%', 'm/s']

    for i, variable in enumerate(variables):
        # Create gradient line
        sns.lineplot(data=df_week, x='time', y=variable, ax=axes[i],
                     marker='o', color=colors[i], linewidth=3, markersize=8, alpha=0.8)

        # Enhanced styling
        axes[i].set_title(titles[i], fontsize=16, fontweight='bold', pad=20)
        axes[i].grid(True, alpha=0.3, linestyle='--')
        axes[i].set_ylabel(f'{variable.capitalize()} ({units[i]})', fontsize=12)

        # Add value annotations on points
        for idx, row in df_week.iterrows():
            axes[i].annotate(f'{row[variable]:.1f}',
                             (row['time'], row[variable]),
                             textcoords="offset points",
                             xytext=(0, 10),
                             ha='center',
                             fontsize=8)

        if i == len(variables) - 1:
            axes[i].set_xlabel('Date & Time', fontsize=12)

    # Improve X-axis formatting to show hours clearly
    for ax in axes:
        # Format x-axis to show date and time clearly
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m/%d %H:%M'))
        ax.xaxis.set_major_locator(plt.matplotlib.dates.HourLocator(interval=6))  # Show every 6 hours
        ax.tick_params(axis='x', rotation=45, labelsize=10)

    plt.tight_layout()
    return fig

def plot_cloud_heatmap(df_weather):
    """Create a heatmap showing cloud coverage by day and hour"""
    df_weather['time'] = pd.to_datetime(df_weather['time'])
    df_weather['day'] = df_weather['time'].dt.date
    df_weather['hour'] = df_weather['time'].dt.hour

    # Create pivot table for heatmap
    cloud_matrix = df_weather.pivot(index='day', columns='hour', values='clouds')

    # Create heatmap
    fig, ax = plt.subplots(figsize=(16, 8))
    sns.heatmap(cloud_matrix, annot=True, fmt="g", cmap='Blues',
                cbar_kws={'label': 'Cloud Coverage (%)'}, ax=ax)

    # Enhanced styling
    ax.set_title('☁️ Cloud Coverage Heatmap (Day vs Hour)', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Hour of Day', fontsize=12)
    ax.set_ylabel('Date', fontsize=12)

    # Improve readability
    ax.tick_params(axis='both', labelsize=10)

    plt.tight_layout()
    return fig

# Main header
st.markdown("""
<div class="main-header">
    <h1>🌤️ Weather Forecast App</h1>
    <p>Get real-time weather data and forecasts for any city worldwide</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for city input - Moved to top
with st.sidebar:
    st.markdown("### 🏙️ Search City")
    
    # Load settings for default location
    settings = load_settings()
    default_city = settings.get("default_location", "London")
    city = st.text_input("Enter city name:", value=default_city, placeholder="e.g., London, New York, Tokyo")

    if st.button("🔍 Get Weather", type="primary", use_container_width=True):
        st.session_state.search_clicked = True

# Settings management - Moved below city input
settings = manage_settings()

# Main content
if 'search_clicked' in st.session_state and st.session_state.search_clicked:
    if city:
        # Current weather section
        st.markdown("## 🌡️ Current Weather")

        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "units": "metric",
            "appid": "d7f9a1a58aafc08d64d4f2076ce20004"
        }

        try:
            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()

                # Get weather data
                main_city_name = data['name']
                main_country = data['sys']['country']
                main_date = datetime.fromtimestamp(data['dt']).date()
                main_temperature = data['main']['temp']
                main_humidity = data['main']['humidity']
                main_wind_speed = data['wind']['speed']
                main_wind_direction = data['wind']['deg']
                main_sunrise = datetime.fromtimestamp(data['sys']['sunrise'])
                main_sunset = datetime.fromtimestamp(data['sys']['sunset'])
                main_feels_like = data['main']['feels_like']
                main_pressure = data['main']['pressure']
                main_description = data['weather'][0]['description'].title()
                timezone_offset = data['timezone']

                # STRETCH GOAL A: Display date and time
                local_time, location_time = display_date_time(main_city_name, timezone_offset)
                st.markdown(f"""
                <div class="time-display">
                    <h4>🕐 Time Information</h4>
                    <p><strong>Your time:</strong> {local_time}</p>
                    <p><strong>Time in {main_city_name}:</strong> {location_time}</p>
                </div>
                """, unsafe_allow_html=True)

                # Display current weather in cards with city and country info
                st.markdown(f"""
                <div class="weather-card">
                    <h3>📍 {main_city_name}, {main_country}</h3>
                    <p>Current weather conditions</p>
                </div>
                """, unsafe_allow_html=True)

                # STRETCH GOAL C: Display weather icon
                if 'weather' in data and len(data['weather']) > 0:
                    icon_code = data['weather'][0]['icon']
                    icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
                    st.image(icon_url, width=50)

                # Display current weather in cards with equal height and perfect alignment
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.markdown(f"""
                    <div class="metric-card" style="height: 160px; display: flex; flex-direction: column; justify-content: space-between; align-items: center;">
                        <div style="text-align: center;">
                            <h4 style="margin: 0 0 10px 0;">🌡️ Temperature</h4>
                            <h2 style="margin: 0; font-size: 2.5rem;">{main_temperature:.1f}°C</h2>
                        </div>
                        <p style="margin: 0; font-size: 0.9rem;">Feels like {main_feels_like:.1f}°C</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <div class="metric-card" style="height: 160px; display: flex; flex-direction: column; justify-content: space-between; align-items: center;">
                        <div style="text-align: center;">
                            <h4 style="margin: 0 0 10px 0;">💧 Humidity</h4>
                            <h2 style="margin: 0; font-size: 2.5rem;">{main_humidity}%</h2>
                        </div>
                        <p style="margin: 0; font-size: 0.9rem;">{main_description}</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    st.markdown(f"""
                    <div class="metric-card" style="height: 160px; display: flex; flex-direction: column; justify-content: space-between; align-items: center;">
                        <div style="text-align: center;">
                            <h4 style="margin: 0 0 10px 0;">💨 Wind</h4>
                            <h2 style="margin: 0; font-size: 2.5rem;">{main_wind_speed} m/s</h2>
                        </div>
                        <p style="margin: 0; font-size: 0.9rem;">Direction: {main_wind_direction}°</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col4:
                    st.markdown(f"""
                    <div class="metric-card" style="height: 160px; display: flex; flex-direction: column; justify-content: space-between; align-items: center;">
                        <div style="text-align: center;">
                            <h4 style="margin: 0 0 10px 0;">🌅 Sunrise/Sunset</h4>
                        </div>
                        <div style="text-align: center;">
                            <p style="margin: 5px 0; font-size: 0.9rem;">🌅 {main_sunrise.strftime('%H:%M')}</p>
                            <p style="margin: 5px 0; font-size: 0.9rem;">🌇 {main_sunset.strftime('%H:%M')}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # STRETCH GOAL C: Display location map
                if 'coord' in data:
                    lat, lon = data['coord']['lat'], data['coord']['lon']
                    st.markdown("### 🗺️ Location Map")
                    map_obj = create_location_map(lat, lon, main_city_name)
                    folium_static(map_obj)

                # Forecast section
                url = "https://api.openweathermap.org/data/2.5/forecast"
                params = {
                    "q": city,
                    "units": "metric",
                    "appid": "d7f9a1a58aafc08d64d4f2076ce20004"
                }

                try:
                    response = requests.get(url, params=params)

                    if response.status_code == 200:
                        data_forecast = response.json()

                        # Process data
                        weather = []
                        for forecast in data_forecast["list"]:
                            time = forecast["dt_txt"]
                            temp = forecast["main"]["temp"]
                            humidity = forecast["main"]["humidity"]
                            description = forecast["weather"][0]["description"]
                            wind_speed = forecast["wind"]["speed"]
                            feels_like = forecast["main"]["feels_like"]
                            wind_direction = forecast["wind"]["deg"]
                            clouds = forecast["clouds"]["all"]

                            weather.append(
                                [time, temp, description, humidity, wind_speed, feels_like, wind_direction, clouds])

                        df_weather = pd.DataFrame(weather,
                                                  columns=["time", "temp", "description", "humidity", "wind_speed",
                                                           "feels_like", "wind_direction", "clouds"])

                        # Day/Night Analysis with better styling
                        df_weather['time'] = pd.to_datetime(df_weather['time'])
                        variables = ['temp', 'humidity']
                        day_night_agg = agg_day_night(df_weather, variables)

                        # Display day/night analysis in a beautiful card
                        st.markdown("""
                        <div class="day-night-card">
                            <h3>🌙 Day/Night Analysis</h3>
                        </div>
                        """, unsafe_allow_html=True)

                        # Create transposed table for temperature only
                        temp_data = day_night_agg[['date', 'period', 'temp']].copy()
                        temp_pivot = temp_data.pivot(index='period', columns='date', values='temp')
                        
                        # Add daily average row
                        daily_avg = temp_data.groupby('date')['temp'].mean()
                        temp_pivot.loc['Daily Average'] = daily_avg
                        
                        # Style the table with custom formatting
                        styled_temp_table = temp_pivot.style.format('{:.1f}°C').background_gradient(
                            cmap='RdYlBu_r', axis=1
                        ).set_properties(**{
                            'background-color': '#f8f9fa',
                            'color': '#495057',
                            'font-weight': 'bold',
                            'text-align': 'center',
                            'border': '1px solid #dee2e6'
                        }).set_table_styles([
                            {'selector': 'th', 'props': [
                                ('background-color', '#667eea'),
                                ('color', 'white'),
                                ('font-weight', 'bold'),
                                ('text-align', 'center'),
                                ('border', '1px solid #495057')
                            ]},
                            {'selector': 'td', 'props': [
                                ('text-align', 'center'),
                                ('padding', '8px'),
                                ('border', '1px solid #dee2e6')
                            ]}
                        ])
                        
                        st.markdown("### 🌡️ Temperature by Day and Period")
                        st.dataframe(styled_temp_table, use_container_width=True)

                        # Statistics in cards
                        st.markdown("### 📈 Summary Statistics")
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            day_temp_avg = day_night_agg[day_night_agg['period'] == 'Day']['temp'].mean()
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>🌞 Day Average</h4>
                                <h2>{day_temp_avg:.1f}°C</h2>
                            </div>
                            """, unsafe_allow_html=True)

                        with col2:
                            night_temp_avg = day_night_agg[day_night_agg['period'] == 'Night']['temp'].mean()
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>🌙 Night Average</h4>
                                <h2>{night_temp_avg:.1f}°C</h2>
                            </div>
                            """, unsafe_allow_html=True)

                        with col3:
                            temp_diff = day_temp_avg - night_temp_avg
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>🌡️ Difference</h4>
                                <h2>{temp_diff:.1f}°C</h2>
                            </div>
                            """, unsafe_allow_html=True)

                        # Add forecast charts
                        st.markdown("## 📊 Detailed Forecast Charts")

                        # Temperature vs Feels Like comparison chart
                        st.markdown("### 🌡️ Temperature vs Feels Like Comparison")
                        feels_like_fig = plot_feels_like_comparison(df_weather)
                        st.pyplot(feels_like_fig)

                        # Multi-variable forecast chart
                        st.markdown("### 📈 Weather Forecast Analysis")
                        multi_fig = plot_weather_3_charts(df_weather, ['temp', 'humidity', 'wind_speed'])
                        st.pyplot(multi_fig)

                        # Cloud coverage section at the bottom
                        st.markdown("## ☁️ Cloud Coverage Analysis")

                        # Calculate average cloud coverage
                        avg_clouds = df_weather['clouds'].mean()

                        # Create cloud coverage card
                        st.markdown(f"""
                        <div class="weather-card">
                            <h3>☁️ Cloud Coverage</h3>
                            <div style="display: flex; align-items: center; justify-content: space-between; margin: 1rem 0;">
                                <div style="text-align: center; flex: 1;">
                                    <h2 style="color: #667eea; font-size: 3rem; margin: 0;">{avg_clouds:.0f}%</h2>
                                    <p style="margin: 0; color: #666;">Average Cloud Coverage</p>
                                </div>
                                <div style="flex: 1; text-align: center;">
                                    <div style="width: 120px; height: 120px; border-radius: 50%; background: conic-gradient(#87CEEB 0deg {avg_clouds * 3.6}deg, #f0f0f0 {avg_clouds * 3.6}deg 360deg); display: flex; align-items: center; justify-content: center; margin: 0 auto;">
                                        <div style="width: 80px; height: 80px; border-radius: 50%; background: white; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; font-weight: bold; color: #667eea;">
                                            ☁️
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div style="margin-top: 1rem; padding: 1rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 10px;">
                                <h4 style="margin: 0 0 0.5rem 0; color: #495057;">📊 Cloud Coverage Details</h4>
                                <p style="margin: 0; color: #6c757d;">
                                    {f"High cloud coverage ({avg_clouds:.0f}%) - Expect overcast conditions" if avg_clouds > 70 else f"Moderate cloud coverage ({avg_clouds:.0f}%) - Partly cloudy conditions" if avg_clouds > 30 else f"Low cloud coverage ({avg_clouds:.0f}%) - Mostly clear skies"}
                                </p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Add cloud coverage heatmap
                        st.markdown("### 🗺️ Cloud Coverage Heatmap")
                        heatmap_fig = plot_cloud_heatmap(df_weather)
                        st.pyplot(heatmap_fig)

                    else:
                        st.error(f"❌ Error: {response.status_code}")

                except Exception as e:
                    st.error(f"❌ Error: {e}")

            else:
                st.error(f"❌ Error: {response.status_code}")
                st.write(response.text)

        except Exception as e:
            st.error(f"❌ Error: {e}")
    else:
        st.warning("⚠️ Please enter a city name")
else:
    # Welcome message
    st.markdown("""
    <div class="weather-card">
        <h2>👋 Welcome to Weather Forecast App</h2>
        <p>Enter a city name in the sidebar to get started!</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """
    Main function to run the weather forecast application.
    This function is called when the script is run directly.
    """
    # The Streamlit app runs automatically when imported
    # This function is here for compatibility with the project structure
    pass

if __name__ == "__main__":
    main()
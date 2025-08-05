# Weather Forecast App

## Project Description
A comprehensive weather forecast application built with Streamlit that provides real-time weather data and detailed forecasts for any city worldwide. The app features an intuitive interface with current weather conditions, 5-day forecasts, interactive charts, and advanced analytics including day/night temperature analysis.

## Features
- **Current Weather Display**: Real-time temperature, humidity, wind speed, and conditions
- **Interactive Maps**: Location visualization using Folium
- **Advanced Analytics**: Day/night temperature analysis with styled tables
- **Multiple Charts**: Temperature vs feels like comparison, multi-variable forecasts, cloud coverage heatmaps
- **Time Zone Support**: Displays local time and location-specific time
- **Settings Management**: Persistent user preferences including favorites and default location
- **Responsive Design**: Beautiful UI with custom CSS styling

## Files Description
- `weather_app_new.py` - Main application file (executable with main() function)
- `requirements.txt` - Python dependencies
- `settings.json` - User settings storage (auto-generated)
- `notebook2.ipynb` - Development notebook with analysis functions

## How to Run

### Option 1: Direct Python Execution
```bash
python weather_app_new.py
```

### Option 2: Using Streamlit (Recommended)
```bash
streamlit run weather_app_new.py
```

### Option 3: Using Batch Scripts (Windows)
- `start_app.bat` - Run with default Python
- `run_app.bat` - Run with specific Python path

## Installation
1. Install Python 3.9 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application using one of the methods above

## Usage Instructions
1. Enter a city name in the sidebar search box
2. Click "Get Weather" to fetch current conditions
3. Explore the various sections:
   - Current weather cards
   - Interactive location map
   - Day/night temperature analysis
   - Detailed forecast charts
   - Cloud coverage analysis
4. Use the settings sidebar to manage favorites and preferences

## Technical Details
- **Framework**: Streamlit
- **Data Source**: OpenWeatherMap API
- **Visualization**: Matplotlib, Seaborn, Folium
- **Data Processing**: Pandas
- **Styling**: Custom CSS with gradient backgrounds

## Dependencies
- streamlit>=1.28.0
- requests>=2.31.0
- pandas>=2.0.0
- matplotlib>=3.7.0
- seaborn>=0.12.0
- pytz
- folium
- streamlit-folium

## Author
[Your Name] - [Your Email]

## Project Structure
```
weather_app/
├── weather_app_new.py      # Main application
├── requirements.txt        # Dependencies
├── README.md              # This file
├── settings.json          # User settings (auto-generated)
├── notebook2.ipynb        # Development notebook
└── *.bat/*.ps1           # Windows execution scripts
``` 
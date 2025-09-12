"""
Module for scraping weather data from National Weather Service API (USA Only)
"""
import requests
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from config.config import Config
from src.core.news_types import WeatherDict
from src.utils.validation import validate_string

logger = logging.getLogger(__name__)

def get_coordinates_for_city(city: str) -> Optional[Dict[str, float]]:
    """
    Get latitude and longitude coordinates for a city using the National Weather Service API
    
    Args:
        city (str): City name to get coordinates for
        
    Returns:
        Optional[Dict[str, float]]: Dictionary with lat/lon coordinates or None if failed
    """
    try:
        # Validate city name
        validated_city = validate_string(city, "City name", min_length=1, max_length=100)
    except ValueError as e:
        logger.error(f"Invalid city name: {e}")
        return None
    
    # National Weather Service API endpoint for geocoding
    url = "https://geocoding-api.open-meteo.com/v1/search"
    
    # Parameters for the API request
    params = {
        'name': validated_city,
        'count': 1,
        'language': 'en',
        'format': 'json'
    }
    
    try:
        # Make the API request
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        # Parse the JSON response
        data = response.json()
        
        # Extract coordinates
        if 'results' in data and len(data['results']) > 0:
            result = data['results'][0]
            coordinates = {
                'latitude': result.get('latitude', 0.0),
                'longitude': result.get('longitude', 0.0)
            }
            return coordinates
        else:
            logger.error(f"No coordinates found for city: {validated_city}")
            return None
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching coordinates for {validated_city}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error processing coordinates for {validated_city}: {e}")
        return None

def fetch_weather_data(city: str) -> Optional[WeatherDict]:
    """
    Fetch comprehensive weather data from National Weather Service API including
    current conditions, hourly forecast, and detailed forecast
    
    Args:
        city (str): City name to fetch weather for
        
    Returns:
        Optional[WeatherDict]: Comprehensive weather data or None if failed
    """
    try:
        # Validate city name
        validated_city = validate_string(city, "City name", min_length=1, max_length=100)
    except ValueError as e:
        logger.error(f"Invalid city name: {e}")
        return None
    
    # Get coordinates for the city
    coordinates = get_coordinates_for_city(validated_city)
    if not coordinates:
        logger.error(f"Could not get coordinates for city: {validated_city}")
        return None
    
    # National Weather Service API endpoint for points
    points_url = f"https://api.weather.gov/points/{coordinates['latitude']},{coordinates['longitude']}"
    
    try:
        # Make the API request to get the forecast URLs
        headers = {'User-Agent': 'News Collector App (contact@example.com)'}
        points_response = requests.get(points_url, headers=headers, timeout=10)
        points_response.raise_for_status()
        
        # Parse the JSON response
        points_data = points_response.json()
        
        # Get the various URLs we need
        properties = points_data.get('properties', {})
        forecast_url = properties.get('forecast', '')
        forecast_hourly_url = properties.get('forecastHourly', '')
        observation_stations_url = properties.get('observationStations', '')
        
        if not forecast_url:
            logger.error(f"No forecast URL found for coordinates: {coordinates}")
            return None
        
        # Fetch current observations
        current_temp = 0
        current_humidity = 0
        current_pressure = 0
        current_wind_speed = 0
        current_visibility = 0
        current_description = ""
        
        if observation_stations_url:
            try:
                stations_response = requests.get(observation_stations_url, headers=headers, timeout=10)
                stations_response.raise_for_status()
                stations_data = stations_response.json()
                
                # Get the first station URL
                stations = stations_data.get('observationStations', [])
                if stations:
                    station_url = stations[0]
                    observation_url = f"{station_url}/observations/latest"
                    
                    observation_response = requests.get(observation_url, headers=headers, timeout=10)
                    observation_response.raise_for_status()
                    observation_data = observation_response.json()
                    
                    # Extract current weather data
                    obs_props = observation_data.get('properties', {})
                    current_temp = obs_props.get('temperature', {}).get('value', 0)
                    # Convert from Celsius to Fahrenheit for consistency with NWS forecasts
                    if current_temp is not None:
                        current_temp = round((current_temp * 9/5) + 32)
                    current_humidity = obs_props.get('relativeHumidity', {}).get('value', 0)
                    # Convert pressure from Pa to hPa
                    current_pressure = obs_props.get('barometricPressure', {}).get('value', 0)
                    if current_pressure is not None:
                        current_pressure = round(current_pressure / 100, 1)
                    current_wind_speed = obs_props.get('windSpeed', {}).get('value', 0)
                    # Convert from km/h to mph
                    if current_wind_speed is not None:
                        current_wind_speed = round(current_wind_speed * 0.621371, 1)
                    current_visibility = obs_props.get('visibility', {}).get('value', 0)
                    # Convert from meters to miles
                    if current_visibility is not None:
                        current_visibility = round(current_visibility * 0.000621371, 1)
                    current_description = obs_props.get('textDescription', '')
            except Exception as e:
                logger.warning(f"Could not fetch current observations: {e}")
        
        # Fetch detailed forecast
        forecast_response = requests.get(forecast_url, headers=headers, timeout=10)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()
        
        # Extract current weather data (first period in the forecast)
        periods = forecast_data.get('properties', {}).get('periods', [])
        if not periods:
            logger.error(f"No forecast periods found for city: {validated_city}")
            return None
        
        current_period = periods[0]
        
        # Use current observations if available, otherwise use forecast data
        temperature = current_temp if current_temp != 0 else current_period.get('temperature', 0)
        description = current_description if current_description else current_period.get('shortForecast', '')
        
        # Convert API response to our WeatherDict format
        weather_data: WeatherDict = {
            'city': validated_city,
            'country': 'US',  # National Weather Service is US-only
            'temperature': temperature,
            'feels_like': temperature,  # NWS doesn't provide feels like in API
            'humidity': current_humidity or 0,
            'pressure': current_pressure or 0,
            'description': description,
            'wind_speed': current_wind_speed or 0,
            'visibility': current_visibility or 0,
            'collected_at': datetime.now().isoformat()
        }
        
        # Add detailed forecast data
        forecast_list = []
        for period in periods[:10]:  # Get forecast for next 10 periods
            forecast_entry = {
                'datetime': period.get('startTime', ''),
                'temperature': period.get('temperature', 0),
                'feels_like': period.get('temperature', 0),  # NWS doesn't provide feels like
                'humidity': 0,  # NWS doesn't provide hourly humidity
                'pressure': 0,  # NWS doesn't provide hourly pressure
                'description': period.get('shortForecast', ''),
                'wind_speed': 0,  # NWS doesn't provide hourly wind in this endpoint
                'precipitation_probability': period.get('probabilityOfPrecipitation', {}).get('value', 0)
            }
            forecast_list.append(forecast_entry)
        
        weather_data['forecast'] = forecast_list
        
        # Fetch hourly forecast if available
        if forecast_hourly_url:
            try:
                hourly_response = requests.get(forecast_hourly_url, headers=headers, timeout=10)
                hourly_response.raise_for_status()
                hourly_data = hourly_response.json()
                
                hourly_forecast = []
                hourly_periods = hourly_data.get('properties', {}).get('periods', [])
                for period in hourly_periods[:24]:  # Get next 24 hours
                    hourly_entry = {
                        'datetime': period.get('startTime', ''),
                        'temperature': period.get('temperature', 0),
                        'feels_like': period.get('temperature', 0),  # NWS doesn't provide feels like
                        'humidity': 0,  # NWS doesn't provide hourly humidity
                        'pressure': 0,  # NWS doesn't provide hourly pressure
                        'description': period.get('shortForecast', ''),
                        'wind_speed': 0,  # NWS doesn't provide hourly wind in this endpoint
                        'precipitation_probability': period.get('probabilityOfPrecipitation', {}).get('value', 0)
                    }
                    hourly_forecast.append(hourly_entry)
                
                weather_data['hourly_forecast'] = hourly_forecast
            except Exception as e:
                logger.warning(f"Could not fetch hourly forecast: {e}")
        
        logger.info(f"Successfully fetched comprehensive weather data for {validated_city}")
        return weather_data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching weather data for {validated_city}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error processing weather data for {validated_city}: {e}")
        return None

def collect_weather(city: str) -> Optional[WeatherDict]:
    """
    Collect complete weather information including current weather and forecast
    
    Args:
        city (str): City name to collect weather for
        
    Returns:
        Optional[WeatherDict]: Complete weather data or None if failed
    """
    # Fetch comprehensive weather data
    weather_data = fetch_weather_data(city)
    return weather_data
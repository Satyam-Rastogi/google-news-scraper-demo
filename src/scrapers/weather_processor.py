"""
Module for processing weather data including saving to file
"""
import logging
import os
import json
import csv
from datetime import datetime
from typing import List, Optional
from config.config import Config
from src.core.news_types import WeatherDict
from src.utils.validation import validate_path, validate_string, sanitize_filename
from src.utils.retry_utils import retry_for_file_operations

logger = logging.getLogger(__name__)

@retry_for_file_operations
def save_weather_data(weather_data: WeatherDict, city: str, output_format: str = None, output_dir: str = None) -> bool:
    """
    Save weather data to file in specified format
    
    Args:
        weather_data (WeatherDict): Weather data to save
        city (str): City name (used for filename)
        output_format (str): Output format (json or csv)
        output_dir (str): Output directory
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Use provided values or defaults from config
        output_format = output_format or Config.OUTPUT_FORMAT
        output_dir = output_dir or Config.OUTPUT_DIR
        
        # Validate output directory
        validated_output_dir = validate_path(output_dir, "Output directory")
        
        # Create output directory if it doesn't exist
        os.makedirs(validated_output_dir, exist_ok=True)
        
        # Sanitize city name for filename
        sanitized_city = sanitize_filename(city)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"weather_{sanitized_city}_{timestamp}.{output_format}"
        filepath = os.path.join(validated_output_dir, filename)
        
        if output_format.lower() == 'json':
            return _save_weather_as_json(weather_data, filepath)
        elif output_format.lower() == 'csv':
            return _save_weather_as_csv(weather_data, filepath)
        else:
            logger.error(f"Unsupported output format: {output_format}")
            return False
            
    except Exception as e:
        logger.error(f"Error saving weather data: {e}")
        return False

def _save_weather_as_json(weather_data: WeatherDict, filepath: str) -> bool:
    """
    Save weather data as JSON
    
    Args:
        weather_data (WeatherDict): Weather data to save
        filepath (str): Path to save file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(weather_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Weather data saved to {filepath}")
        return True
    except Exception as e:
        logger.error(f"Error saving weather data as JSON to {filepath}: {e}")
        return False

def _save_weather_as_csv(weather_data: WeatherDict, filepath: str) -> bool:
    """
    Save weather data as CSV
    
    Args:
        weather_data (WeatherDict): Weather data to save
        filepath (str): Path to save file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Flatten the weather data for CSV
        flattened_data = {
            'city': weather_data.get('city', ''),
            'country': weather_data.get('country', ''),
            'temperature': weather_data.get('temperature', 0.0),
            'feels_like': weather_data.get('feels_like', 0.0),
            'humidity': weather_data.get('humidity', 0.0),
            'pressure': weather_data.get('pressure', 0.0),
            'description': weather_data.get('description', ''),
            'wind_speed': weather_data.get('wind_speed', 0.0),
            'visibility': weather_data.get('visibility', 0.0),
            'collected_at': weather_data.get('collected_at', ''),
        }
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=flattened_data.keys())
            writer.writeheader()
            writer.writerow(flattened_data)
        logger.info(f"Weather data saved to {filepath}")
        return True
    except Exception as e:
        logger.error(f"Error saving weather data as CSV to {filepath}: {e}")
        return False

def display_weather_summary(weather_data: WeatherDict) -> None:
    """
    Display a formatted summary of weather data
    
    Args:
        weather_data (WeatherDict): Weather data to display
    """
    try:
        city = weather_data.get('city', 'Unknown')
        country = weather_data.get('country', '')
        temp = weather_data.get('temperature', 0.0)
        desc = weather_data.get('description', 'No description')
        humidity = weather_data.get('humidity', 0.0)
        wind_speed = weather_data.get('wind_speed', 0.0)
        
        location = f"{city}, {country}" if country else city
        
        print(f"\n{'='*60}")
        print(f"Weather Summary for {location}")
        print(f"{'='*60}")
        print(f"Temperature: {temp}°C (feels like {weather_data.get('feels_like', 0.0)}°C)")
        print(f"Condition: {desc.title()}")
        if humidity > 0:
            print(f"Humidity: {humidity}%")
        if wind_speed > 0:
            print(f"Wind Speed: {wind_speed} m/s")
        
        # Show additional information if available
        if weather_data.get('pressure') and weather_data['pressure'] > 0:
            print(f"Pressure: {weather_data['pressure']} hPa")
        
        if weather_data.get('visibility') and weather_data['visibility'] > 0:
            print(f"Visibility: {weather_data['visibility']} meters")
        
        # Show forecast if available
        if weather_data.get('forecast'):
            print(f"\nExtended Forecast:")
            forecast = weather_data['forecast'][:7]  # Show first 7 entries
            for entry in forecast:
                dt = entry.get('datetime', '')[:10]  # Show only date
                temp = entry.get('temperature', 0.0)
                desc = entry.get('description', 'No description')
                print(f"  {dt}: {temp}°C, {desc}")
            
            if len(weather_data['forecast']) > 7:
                print(f"  ... and {len(weather_data['forecast']) - 7} more days")
        
        print(f"{'='*60}")
        
    except Exception as e:
        logger.error(f"Error displaying weather summary: {e}")
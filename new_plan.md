# Implementation Plan: CLI Extension for News and Weather Features

## Overview
This document outlines the implementation plan for extending the CLI to support news, weather, or both using flags as specified in the feature request.

## Current Architecture Analysis
The current system is a comprehensive news collection tool with:
- Main entry point: `src/core/main.py`
- Modular structure with separate components for scraping, parsing, and processing
- Configuration management via `config/config.py` and `config/settings.cfg`
- Support for various output formats (JSON/CSV)
- Scheduled execution capabilities
- Current dependencies: selenium, beautifulsoup4, requests, newspaper3k, etc.

## Implementation Strategy

### 1. CLI Flag Implementation
We need to add new flags to the argument parser in `src/core/main.py`:

#### New Flags:
- `--news` / `-n`: Fetch only news (default behavior)
- `--weather` / `-w`: Fetch only weather
- `--nw`: Fetch both news and weather

### 2. Weather Functionality Implementation
Since weather functionality is not currently implemented, we need to:

#### a. Create Weather Modules
- `src/scrapers/weather_scraper.py`: Core weather scraping logic
- `src/scrapers/weather_parser.py`: Parse weather data from sources
- `src/scrapers/weather_processor.py`: Process and format weather data

#### b. Weather Data Structure
- Create a new type definition in `src/core/news_types.py` for weather data
- Define consistent data structure for weather information

#### c. Weather Sources
- Use the National Weather Service API (USA Only) which is free and open
- No API key required

### 3. Modular Architecture for Future Extensions
To ensure the system can easily accommodate new features like sports or finance:

#### a. Command Handler Pattern
- Implement a command handler system that routes to appropriate modules
- Create abstract base classes for different data types

#### b. Plugin Architecture
- Design a plugin system where new data types can be added with minimal changes
- Standardize interfaces for data collection, processing, and output

## Detailed Implementation Plan

### Phase 1: CLI Flag Integration (1-2 days)

1. **Modify `src/core/main.py`**:
   - Add new CLI flags to the argument parser:
     ```python
     parser.add_argument("--news", "-n", action="store_true", help="Fetch only news")
     parser.add_argument("--weather", "-w", action="store_true", help="Fetch only weather")
     parser.add_argument("--nw", action="store_true", help="Fetch both news and weather")
     ```
   - Add logic to determine which mode to run based on flags
   - Implement the prompting mechanism for --nw flag

2. **Update main_cli function**:
   - Modify to handle different modes (news only, weather only, both)
   - Add conditional logic to route to appropriate modules

3. **Add validation**:
   - Ensure only one of --news, --weather, or --nw is specified
   - Handle default behavior when no flags are provided (default to news)

### Phase 2: Weather Functionality (3-5 days)

1. **Research and select weather API**:
   - Use National Weather Service API (USA Only)
   - No API key required

2. **Create weather data structures**:
   - Add `WeatherDict` type definition in `src/core/news_types.py`
   - Define fields like city, temperature, description, forecast, etc.

3. **Implement weather modules**:
   - Create `src/scrapers/weather_scraper.py`:
     - Function to fetch weather data from National Weather Service API
     - Implement error handling for API failures
   - Create `src/scrapers/weather_processor.py`:
     - Process and format weather data
     - Integrate with existing output system (JSON/CSV)
   - Create `src/scrapers/weather_parser.py` (if needed):
     - Parse API response into consistent format

4. **Configuration**:
   - No additional configuration needed for National Weather Service API
   - Update `config/config.py` to remove unnecessary settings
   - Add default values and validation

### Phase 3: Combined Functionality (1-2 days)

1. **Implement --nw flag behavior**:
   - Create prompting mechanism for news query
   - Create prompting mechanism for weather query
   - Ensure sequential processing of both data types
   - Maintain consistent output formatting

2. **Output handling**:
   - Ensure both news and weather data are saved appropriately
   - Handle different output formats (JSON/CSV) for combined data

### Phase 4: Modularity and Extensibility (2-3 days)

1. **Refactor for modularity**:
   - Create abstract base classes for data collectors
   - Implement command handler pattern
   - Ensure clear separation between news and weather functionality

2. **Testing**:
   - Create unit tests for new weather functionality
   - Ensure existing tests still pass
   - Add integration tests for combined functionality

## Technical Implementation Details

### 1. CLI Flag Implementation Details

In `src/core/main.py`, we need to:

1. Add the new arguments to the parser:
   ```python
   # Add new flags for weather functionality
   parser.add_argument("--news", "-n", action="store_true", help="Fetch only news")
   parser.add_argument("--weather", "-w", action="store_true", help="Fetch only weather")
   parser.add_argument("--nw", action="store_true", help="Fetch both news and weather")
   ```

2. Add validation logic to ensure only one mode is selected:
   ```python
   # Validate mode selection
   mode_flags = [args.news, args.weather, args.nw]
   if sum(mode_flags) > 1:
       parser.error("Only one of --news, --weather, or --nw can be specified")
   ```

3. Determine the mode to run:
   ```python
   # Determine mode
   if args.nw:
       mode = "both"
   elif args.weather:
       mode = "weather"
   else:
       mode = "news"  # default
   ```

### 2. Weather Module Implementation

#### Weather Data Structure
In `src/core/news_types.py`, add:
```python
class WeatherDict(TypedDict, total=False):
    city: str
    country: str
    temperature: float
    feels_like: float
    humidity: int
    pressure: int
    description: str
    wind_speed: float
    visibility: int
    forecast: List[Dict[str, Any]]
    collected_at: str
```

#### Weather Scraper
In `src/scrapers/weather_scraper.py`:
```python
import requests
from typing import Dict, Any, Optional
from config.config import Config

def fetch_weather_data(city: str) -> Optional[Dict[str, Any]]:
    """Fetch weather data from National Weather Service API"""
    # No API key required for National Weather Service API
    
    # First get coordinates for the city
    coordinates = get_coordinates_for_city(city)
    if not coordinates:
        return None
    
    # Then get weather data from National Weather Service API
    url = f"https://api.weather.gov/points/{coordinates['latitude']},{coordinates['longitude']}"
    # ... implementation details ...
```

### 3. Configuration Updates

In `config/settings.cfg`, no changes needed for weather settings.

In `config/config.py`, remove:
```python
# Weather settings
WEATHER_API_KEY: str = ""  # OpenWeatherMap API key
```

### 4. Dependency Management

No additional dependencies needed. The National Weather Service API works with the existing requests library.

## Risk Assessment and Mitigation

### 1. Weather API Limitations
**Risk**: API rate limits, availability issues, or geographic limitations
**Mitigation**: 
- Implement caching mechanism
- Add fallback data sources
- Design graceful degradation when weather data is unavailable
- Note that the API is US-only

### 2. Code Complexity
**Risk**: Adding weather functionality might complicate the existing news-focused codebase
**Mitigation**:
- Use modular design patterns
- Maintain clear separation between news and weather functionality
- Implement abstraction layers to minimize coupling

### 3. Backward Compatibility
**Risk**: Changes might break existing functionality or CLI usage
**Mitigation**:
- Ensure all existing CLI options continue to work
- Maintain default behavior when no new flags are used
- Thoroughly test existing functionality after changes

## Testing Strategy

1. **Unit Tests**:
   - Test weather data fetching and parsing
   - Test CLI flag validation
   - Test combined functionality

2. **Integration Tests**:
   - Test end-to-end weather collection
   - Test end-to-end combined news+weather collection

3. **Regression Tests**:
   - Ensure all existing functionality still works
   - Run existing test suite

## Timeline and Milestones

| Week | Tasks | Deliverables |
|------|-------|--------------|
| Week 1 | CLI flag implementation, initial weather module structure | Working CLI with new flags, basic weather module skeleton |
| Week 2 | Weather API integration, data processing | Fully functional weather collection |
| Week 3 | Combined functionality, modular architecture | Complete implementation with extensibility |
| Week 4 | Testing, documentation, final review | Production-ready implementation |

## Success Criteria
1. All new CLI flags work as specified
2. Existing functionality remains unchanged
3. Weather data is collected and formatted consistently
4. Combined news+weather functionality works as specified
5. System is extensible for future features
6. All tests pass
7. Documentation is updated

## Future Enhancements
After implementing the core functionality, we can consider:
- Adding sports or finance data collection
- Implementing more sophisticated weather data processing
- Adding data visualization capabilities
- Creating a unified dashboard for all collected data types
- Supporting international weather APIs for global coverage
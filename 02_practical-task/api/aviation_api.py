"""Integration with aviation data APIs."""
import requests
import logging
import os
import sys
import json
from datetime import datetime

# Add parent directory to import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import AVIATION_API_KEY

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AviationAPI:
    """Wrapper for aviation data API."""
    
    def __init__(self, api_key=AVIATION_API_KEY):
        """Initialize with API key."""
        self.api_key = api_key
        self.base_url = "https://api.aviationstack.com/v1"
    
    def get_flights(self, **params):
        """
        Get flight data from the API.
        
        Args:
            **params: Query parameters for the API call
                      (e.g., dep_iata, arr_iata, flight_status)
        
        Returns:
            Dictionary with response data or None if request failed
        """
        url = f"{self.base_url}/flights"
        params["access_key"] = self.api_key
        
        try:
            logger.info(f"Requesting flight data with params: {params}")
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Retrieved {len(data.get('data', []))} flights")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return None
    
    def get_airport_flights(self, iata_code, status=None, limit=100):
        """
        Get flights for a specific airport.
        
        Args:
            iata_code: IATA code of the airport
            status: Optional flight status filter
            limit: Maximum number of results
        
        Returns:
            List of flight dictionaries
        """
        params = {
            "dep_iata": iata_code,
            "limit": limit
        }
        
        if status:
            params["flight_status"] = status
        
        result = self.get_flights(**params)
        return result.get("data", []) if result else []
    
    def get_delayed_flights(self, min_delay_minutes=120):
        """
        Get all delayed flights across Europe.
        
        Args:
            min_delay_minutes: Minimum delay in minutes to consider
        
        Returns:
            List of delayed flight dictionaries
        """
        # Note: This is a simplified implementation. In reality, you might need
        # to query multiple major airports and filter results
        params = {
            "flight_status": "active",
            "limit": 100
        }
        
        result = self.get_flights(**params)
        if not result:
            return []
        
        # Filter flights with significant delays
        delayed_flights = []
        for flight in result.get("data", []):
            departure_delay = flight.get("departure", {}).get("delay", 0)
            arrival_delay = flight.get("arrival", {}).get("delay", 0)
            
            max_delay = max(departure_delay, arrival_delay)
            if max_delay >= min_delay_minutes:
                delayed_flights.append(flight)
        
        logger.info(f"Found {len(delayed_flights)} flights delayed by {min_delay_minutes}+ minutes")
        return delayed_flights

    def get_flight_by_number(self, flight_number):
        """
        Get details for a specific flight by flight number.
        
        Args:
            flight_number: IATA flight number (e.g., 'LH1234')
        
        Returns:
            Flight dictionary or None if not found
        """
        params = {
            "flight_iata": flight_number
        }
        
        result = self.get_flights(**params)
        if not result or not result.get("data"):
            return None
        
        return result["data"][0]
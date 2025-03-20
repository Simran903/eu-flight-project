"""Module for collecting flight data from various sources."""
import os
import sys
import logging
import json
import time
from datetime import datetime, timedelta
import requests

# Add parent directory to import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import AVIATION_API_KEY
from db.models import Flight, Airport, Airline, FlightStatus
from db.database import SessionLocal

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_real_time_flight_data(airport_code):
    """
    Simulates fetching real-time flight data from an API.
    
    In a production environment, this would connect to a real flight data API.
    For this simulation, we generate mock data.
    
    Args:
        airport_code: IATA code of the airport
        
    Returns:
        List of flight dictionaries with status information
    """
    logger.info(f"Fetching flight data for airport: {airport_code}")
    
    # In a real implementation, this would make an API call like:
    # url = f"https://api.aviationstack.com/v1/flights?access_key={AVIATION_API_KEY}&dep_iata={airport_code}"
    # response = requests.get(url)
    # return response.json()['data']
    
    # For simulation, we'll return mock data
    return generate_mock_flight_data(airport_code)

def generate_mock_flight_data(airport_code):
    """Generate mock flight data for simulation purposes."""
    logger.info(f"Generating mock flight data for {airport_code}")
    
    # Get current time
    now = datetime.now()
    
    # Mock airlines and destinations
    airlines = [
        {"name": "Lufthansa", "iata": "LH", "icao": "DLH"},
        {"name": "Eurowings", "iata": "EW", "icao": "EWG"},
        {"name": "Ryanair", "iata": "FR", "icao": "RYR"},
        {"name": "Air France", "iata": "AF", "icao": "AFR"},
        {"name": "British Airways", "iata": "BA", "icao": "BAW"}
    ]
    
    destinations = [
        {"name": "London Heathrow", "iata": "LHR", "icao": "EGLL"},
        {"name": "Paris Charles de Gaulle", "iata": "CDG", "icao": "LFPG"},
        {"name": "Amsterdam Schiphol", "iata": "AMS", "icao": "EHAM"},
        {"name": "Madrid Barajas", "iata": "MAD", "icao": "LEMD"},
        {"name": "Rome Fiumicino", "iata": "FCO", "icao": "LIRF"}
    ]
    
    # Generate 10 random flights
    flights = []
    for i in range(10):
        # Select random airline and destination
        airline = airlines[i % len(airlines)]
        destination = destinations[i % len(destinations)]
        
        # Generate scheduled times
        scheduled_departure = now + timedelta(hours=i, minutes=30*i)
        scheduled_arrival = scheduled_departure + timedelta(hours=2)
        
        # Decide if flight is delayed (30% chance)
        is_delayed = i % 3 == 0
        delay_minutes = 150 if is_delayed else 10
        
        actual_departure = scheduled_departure + timedelta(minutes=delay_minutes) if scheduled_departure < now else None
        actual_arrival = scheduled_arrival + timedelta(minutes=delay_minutes) if scheduled_arrival < now else None
        
        # Set flight status
        if now < scheduled_departure:
            status = "scheduled"
        elif now < scheduled_departure + timedelta(minutes=delay_minutes):
            status = "boarding"
        elif now < scheduled_arrival + timedelta(minutes=delay_minutes):
            status = "in-air"
        else:
            status = "landed"
        
        # Create flight dictionary
        flight = {
            "flight": {
                "number": f"{airline['iata']}{1000+i}",
                "iata": f"{airline['iata']}{1000+i}",
                "icao": f"{airline['icao']}{1000+i}"
            },
            "airline": airline,
            "departure": {
                "airport": f"Airport {airport_code}",
                "iata": airport_code,
                "scheduled": scheduled_departure.isoformat(),
                "actual": actual_departure.isoformat() if actual_departure else None
            },
            "arrival": {
                "airport": destination["name"],
                "iata": destination["iata"],
                "scheduled": scheduled_arrival.isoformat(),
                "actual": actual_arrival.isoformat() if actual_arrival else None
            },
            "status": status,
            "delay": delay_minutes if is_delayed else 0
        }
        
        flights.append(flight)
    
    return flights

def process_flight_data(flight_data):
    """
    Process flight data and update the database.
    
    Args:
        flight_data: List of flight dictionaries from API
    """
    logger.info(f"Processing {len(flight_data)} flights")
    
    db = SessionLocal()
    try:
        for flight_info in flight_data:
            # Extract data from API response
            flight_number = flight_info["flight"]["iata"]
            airline_iata = flight_info["airline"]["iata"]
            departure_iata = flight_info["departure"]["iata"]
            arrival_iata = flight_info["arrival"]["iata"]
            
            # Look up or create airline
            airline = db.query(Airline).filter_by(iata_code=airline_iata).first()
            if not airline:
                logger.warning(f"Airline {airline_iata} not found in database")
                continue
                
            # Look up airports
            departure_airport = db.query(Airport).filter_by(iata_code=departure_iata).first()
            arrival_airport = db.query(Airport).filter_by(iata_code=arrival_iata).first()
            
            if not departure_airport or not arrival_airport:
                logger.warning(f"Airports not found: {departure_iata} or {arrival_iata}")
                continue
            
            # Get or create flight
            flight = db.query(Flight).filter_by(
                flight_number=flight_number,
                scheduled_departure=datetime.fromisoformat(flight_info["departure"]["scheduled"])
            ).first()
            
            if not flight:
                # Create new flight
                flight = Flight(
                    flight_number=flight_number,
                    airline_id=airline.id,
                    departure_airport_id=departure_airport.id,
                    arrival_airport_id=arrival_airport.id,
                    scheduled_departure=datetime.fromisoformat(flight_info["departure"]["scheduled"]),
                    scheduled_arrival=datetime.fromisoformat(flight_info["arrival"]["scheduled"]),
                    status=flight_info["status"]
                )
                db.add(flight)
                db.flush()  # Get ID for the new flight
            
            # Update actual times if available
            if flight_info["departure"]["actual"]:
                flight.actual_departure = datetime.fromisoformat(flight_info["departure"]["actual"])
            
            if flight_info["arrival"]["actual"]:
                flight.actual_arrival = datetime.fromisoformat(flight_info["arrival"]["actual"])
            
            flight.status = flight_info["status"]
            
            # Update flight status
            flight_status = db.query(FlightStatus).filter_by(flight_id=flight.id).first()
            if not flight_status:
                flight_status = FlightStatus(flight_id=flight.id)
                db.add(flight_status)
            
            # Calculate delay
            delay_minutes = flight_info.get("delay", 0)
            flight_status.delay_minutes = delay_minutes
            flight_status.is_delayed = delay_minutes >= 120  # 2 hours threshold
            flight_status.last_updated = datetime.now()
            
            db.commit()
            
    except Exception as e:
        logger.error(f"Error processing flight data: {str(e)}")
        db.rollback()
    finally:
        db.close()

def simulate_data_collection():
    """Simulate collecting data from multiple airports."""
    # List of airport codes to simulate collection from
    airport_codes = ['FRA', 'MUC', 'BER', 'HAM', 'DUS']
    
    for airport_code in airport_codes:
        logger.info(f"Simulating data collection for airport: {airport_code}")
        
        # Fetch flight data
        flight_data = fetch_real_time_flight_data(airport_code)
        
        # Process the data
        process_flight_data(flight_data)
        
        # Sleep to simulate API rate limits
        time.sleep(1)
    
    logger.info("Simulation completed")

if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else None
    
    if command == "simulate":
        simulate_data_collection()
    else:
        print("Available commands: simulate")
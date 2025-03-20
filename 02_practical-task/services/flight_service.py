"""Service for flight data operations."""
import os
import sys
import logging
from datetime import datetime, timedelta
from sqlalchemy import and_, or_

# Add parent directory to import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import SessionLocal
from db.models import Flight, Airport, Airline, FlightStatus
from config import DELAY_THRESHOLD_MINUTES

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FlightService:
    """Service for managing flight data."""
    
    def __init__(self):
        """Initialize with database session."""
        self.db = SessionLocal()
    
    def __del__(self):
        """Close database session on cleanup."""
        self.db.close()
    
    def get_flights_by_airport(self, airport_code):
        """
        Get all flights departing from or arriving at a specific airport.
        
        Args:
            airport_code: IATA code of the airport
        
        Returns:
            List of Flight objects
        """
        airport = self.db.query(Airport).filter(Airport.iata_code == airport_code).first()
        if not airport:
            logger.warning(f"Airport not found: {airport_code}")
            return []
        
        flights = self.db.query(Flight).filter(
            or_(
                Flight.departure_airport_id == airport.id,
                Flight.arrival_airport_id == airport.id
            )
        ).all()
        
        return flights
    
    def get_flight_by_number(self, flight_number):
        """
        Get flight by flight number.
        
        Args:
            flight_number: Flight number (e.g., 'LH1234')
        
        Returns:
            Flight object or None if not found
        """
        return self.db.query(Flight).filter(Flight.flight_number == flight_number).first()
    
    def get_delayed_flights(self, min_delay_minutes=DELAY_THRESHOLD_MINUTES):
        """
        Get all flights delayed by at least the specified number of minutes.
        
        Args:
            min_delay_minutes: Minimum delay in minutes (default: 120)
        
        Returns:
            List of Flight objects with corresponding FlightStatus
        """
        return self.db.query(Flight).join(FlightStatus).filter(
            and_(
                FlightStatus.is_delayed == True,
                FlightStatus.delay_minutes >= min_delay_minutes
            )
        ).all()
    
    def create_flight(self, flight_number, airline_id, departure_airport_id, arrival_airport_id,
                     scheduled_departure, scheduled_arrival, status="scheduled"):
        """
        Create a new flight.
        
        Args:
            flight_number: Flight number (e.g., 'LH1234')
            airline_id: ID of the airline
            departure_airport_id: ID of the departure airport
            arrival_airport_id: ID of the arrival airport
            scheduled_departure: Scheduled departure time (datetime)
            scheduled_arrival: Scheduled arrival time (datetime)
            status: Initial flight status
        
        Returns:
            Newly created Flight object
        """
        flight = Flight(
            flight_number=flight_number,
            airline_id=airline_id,
            departure_airport_id=departure_airport_id,
            arrival_airport_id=arrival_airport_id,
            scheduled_departure=scheduled_departure,
            scheduled_arrival=scheduled_arrival,
            status=status
        )
        
        try:
            self.db.add(flight)
            self.db.commit()
            self.db.refresh(flight)
            
            # Create initial flight status
            flight_status = FlightStatus(
                flight_id=flight.id,
                is_delayed=False,
                delay_minutes=0
            )
            self.db.add(flight_status)
            self.db.commit()
            
            logger.info(f"Created flight: {flight_number}")
            return flight
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating flight: {str(e)}")
            raise
    
    def update_flight_status(self, flight_id, actual_departure=None, actual_arrival=None, 
                           status=None, delay_minutes=None, delay_reason=None):
        """
        Update flight status.
        
        Args:
            flight_id: ID of the flight
            actual_departure: Actual departure time (datetime)
            actual_arrival: Actual arrival time (datetime)
            status: Updated flight status
            delay_minutes: Delay in minutes
            delay_reason: Reason for delay
        
        Returns:
            Updated Flight object
        """
        flight = self.db.query(Flight).filter(Flight.id == flight_id).first()
        if not flight:
            logger.warning(f"Flight not found: {flight_id}")
            return None
        
        # Update flight information
        if actual_departure:
            flight.actual_departure = actual_departure
        
        if actual_arrival:
            flight.actual_arrival = actual_arrival
        
        if status:
            flight.status = status
        
        # Update flight status
        flight_status = self.db.query(FlightStatus).filter(FlightStatus.flight_id == flight_id).first()
        if not flight_status:
            flight_status = FlightStatus(flight_id=flight_id)
            self.db.add(flight_status)
        
        if delay_minutes is not None:
            flight_status.delay_minutes = delay_minutes
            flight_status.is_delayed = delay_minutes >= DELAY_THRESHOLD_MINUTES
        
        if delay_reason:
            flight_status.delay_reason = delay_reason
        
        flight_status.last_updated = datetime.now()
        
        try:
            self.db.commit()
            logger.info(f"Updated flight: {flight.flight_number}")
            return flight
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating flight: {str(e)}")
            raise

    def get_flights_for_claims(self):
        """
        Get all flights eligible for compensation claims.
        
        Returns:
            List of flights delayed by more than the threshold
        """
        three_months_ago = datetime.now() - timedelta(days=90)
        
        return self.db.query(Flight).join(FlightStatus).filter(
            and_(
                FlightStatus.is_delayed == True,
                FlightStatus.delay_minutes >= DELAY_THRESHOLD_MINUTES,
                Flight.scheduled_departure >= three_months_ago
            )
        ).all()


# Command-line interface functions
def query_airport(airport_code):
    """Get all flights for an airport code."""
    service = FlightService()
    flights = service.get_flights_by_airport(airport_code)
    
    print(f"Flights for airport {airport_code}:")
    for flight in flights:
        print(f"  {flight.flight_number}: {flight.departure_airport.city} -> {flight.arrival_airport.city}")
        print(f"    Scheduled: {flight.scheduled_departure} -> {flight.scheduled_arrival}")
        if flight.actual_departure:
            print(f"    Actual: {flight.actual_departure} -> {flight.actual_arrival or 'N/A'}")
        print(f"    Status: {flight.status}")
        if flight.flight_status.is_delayed:
            print(f"    Delayed: {flight.flight_status.delay_minutes} minutes")
            if flight.flight_status.delay_reason:
                print(f"    Reason: {flight.flight_status.delay_reason}")
        print("")

def find_delayed():
    """Find all delayed flights."""
    service = FlightService()
    flights = service.get_delayed_flights()
    
    print(f"Flights delayed by {DELAY_THRESHOLD_MINUTES}+ minutes:")
    for flight in flights:
        print(f"  {flight.flight_number}: {flight.departure_airport.city} -> {flight.arrival_airport.city}")
        print(f"    Delay: {flight.flight_status.delay_minutes} minutes")
        if flight.flight_status.delay_reason:
            print(f"    Reason: {flight.flight_status.delay_reason}")
        print("")

def get_flight(flight_number):
    """Get details for a specific flight."""
    service = FlightService()
    flight = service.get_flight_by_number(flight_number)
    
    if not flight:
        print(f"Flight {flight_number} not found")
        return
    
    print(f"Flight {flight_number} details:")
    print(f"  Airline: {flight.airline.name}")
    print(f"  Route: {flight.departure_airport.city} ({flight.departure_airport.iata_code}) -> "
          f"{flight.arrival_airport.city} ({flight.arrival_airport.iata_code})")
    print(f"  Scheduled: {flight.scheduled_departure} -> {flight.scheduled_arrival}")
    if flight.actual_departure:
        print(f"  Actual: {flight.actual_departure} -> {flight.actual_arrival or 'N/A'}")
    print(f"  Status: {flight.status}")
    if flight.flight_status.is_delayed:
        print(f"  Delayed: {flight.flight_status.delay_minutes} minutes")
        if flight.flight_status.delay_reason:
            print(f"  Reason: {flight.flight_status.delay_reason}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m services.flight_service <command> [args]")
        print("Commands:")
        print("  query_airport <airport_code>")
        print("  find_delayed")
        print("  get_flight <flight_number>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "query_airport" and len(sys.argv) >= 3:
        query_airport(sys.argv[2])
    elif command == "find_delayed":
        find_delayed()
    elif command == "get_flight" and len(sys.argv) >= 3:
        get_flight(sys.argv[2])
    else:
        print("Invalid command or missing arguments")
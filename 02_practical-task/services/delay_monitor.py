import os
import sys
import logging
import time
import schedule
import json
from datetime import datetime, timedelta

# Add parent directory to import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import SessionLocal
from db.models import Flight, FlightStatus, Airport
from api.flight_data import fetch_real_time_flight_data, process_flight_data
from config import DELAY_THRESHOLD_MINUTES

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DelayMonitor:
    """Service for monitoring flight delays."""
    
    def __init__(self):
        """Initialize with database session."""
        self.db = SessionLocal()
    
    def __del__(self):
        """Close database session on cleanup."""
        self.db.close()
    
    def check_all_airports(self):
        """
        Check all airports for delayed flights.
        """
        logger.info("Starting flight delay monitoring scan")
        
        # Get all European airports
        airports = self.db.query(Airport).all()
        
        for airport in airports:
            logger.info(f"Checking flights for {airport.name} ({airport.iata_code})")
            
            # Fetch real-time data
            flight_data = fetch_real_time_flight_data(airport.iata_code)
            
            # Process the data
            process_flight_data(flight_data)
        
        logger.info("Completed flight delay monitoring scan")
    
    def generate_daily_report(self):
        """
        Generate a daily report of delayed flights.
        
        Returns:
            Dictionary with report data
        """
        logger.info("Generating daily delay report")
        
        # Get yesterday's date range
        yesterday = datetime.now().date() - timedelta(days=1)
        start_date = datetime.combine(yesterday, datetime.min.time())
        end_date = datetime.combine(yesterday, datetime.max.time())
        
        # Query delayed flights
        delayed_flights = self.db.query(Flight).join(FlightStatus).filter(
            FlightStatus.is_delayed == True,
            FlightStatus.delay_minutes >= DELAY_THRESHOLD_MINUTES,
            Flight.scheduled_departure >= start_date,
            Flight.scheduled_departure <= end_date
        ).all()
        
        # Calculate statistics
        total_flights = self.db.query(Flight).filter(
            Flight.scheduled_departure >= start_date,
            Flight.scheduled_departure <= end_date
        ).count()
        
        total_delayed = len(delayed_flights)
        delay_percentage = (total_delayed / total_flights * 100) if total_flights > 0 else 0
        
        avg_delay = 0
        if total_delayed > 0:
            avg_delay = sum(flight.flight_status.delay_minutes for flight in delayed_flights) / total_delayed
        
        # Group by airline
        airline_stats = {}
        for flight in delayed_flights:
            airline_name = flight.airline.name
            if airline_name not in airline_stats:
                airline_stats[airline_name] = {
                    'count': 0,
                    'total_delay': 0
                }
            
            airline_stats[airline_name]['count'] += 1
            airline_stats[airline_name]['total_delay'] += flight.flight_status.delay_minutes
        
        # Create report
        report = {
            'date': yesterday.isoformat(),
            'total_flights': total_flights,
            'delayed_flights': total_delayed,
            'delay_percentage': round(delay_percentage, 2),
            'average_delay_minutes': round(avg_delay, 2),
            'airlines': [
                {
                    'name': airline,
                    'delayed_flights': stats['count'],
                    'average_delay': round(stats['total_delay'] / stats['count'], 2)
                }
                for airline, stats in airline_stats.items()
            ]
        }
        
        # Save report to file
        report_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'reports')
        os.makedirs(report_dir, exist_ok=True)
        
        report_file = os.path.join(report_dir, f"delay_report_{yesterday.isoformat()}.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Daily report saved to {report_file}")
        return report
    
    def identify_claim_eligible_flights(self):
        """
        Identify flights eligible for compensation claims.
        
        Returns:
            List of eligible flight IDs
        """
        three_months_ago = datetime.now() - timedelta(days=90)
        
        eligible_flights = self.db.query(Flight).join(FlightStatus).filter(
            FlightStatus.is_delayed == True,
            FlightStatus.delay_minutes >= DELAY_THRESHOLD_MINUTES,
            Flight.scheduled_departure >= three_months_ago,
            Flight.status == "landed"  # Only completed flights
        ).all()
        
        logger.info(f"Identified {len(eligible_flights)} flights eligible for compensation claims")
        
        return [flight.id for flight in eligible_flights]
    
    def start_monitoring_schedule(self):
        """Start the scheduled monitoring jobs."""
        logger.info("Starting flight delay monitoring schedule")
        
        # Schedule airport scans every hour
        schedule.every(1).hours.do(self.check_all_airports)
        
        # Generate daily report at midnight
        schedule.every().day.at("00:00").do(self.generate_daily_report)
        
        # Check for claim-eligible flights once a day
        schedule.every().day.at("01:00").do(self.identify_claim_eligible_flights)
        
        # Run the scheduler
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else None
    
    monitor = DelayMonitor()
    
    if command == "check":
        monitor.check_all_airports()
    elif command == "report":
        report = monitor.generate_daily_report()
        print(json.dumps(report, indent=2))
    elif command == "claims":
        eligible_flights = monitor.identify_claim_eligible_flights()
        print(f"Eligible flight IDs: {eligible_flights}")
    elif command == "start":
        monitor.start_monitoring_schedule()
    else:
        print("Available commands: check, report, claims, start")
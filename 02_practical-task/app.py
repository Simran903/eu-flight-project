"""Main application entry point for EU Flight Monitor."""
import os
import sys
import logging
import argparse
from services.delay_monitor import DelayMonitor
from api.flight_data import simulate_data_collection
from services.flight_service import query_airport, find_delayed, get_flight
from services.airport_service import AirportService
from db.database import create_tables, seed_sample_data

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_database():
    """Initialize the database with tables and sample data."""
    logger.info("Setting up database...")
    create_tables()
    seed_sample_data()
    logger.info("Database setup complete")

def simulate_data():
    """Run the data collection simulation."""
    logger.info("Starting data collection simulation...")
    simulate_data_collection()
    logger.info("Simulation complete")

def start_monitoring():
    """Start the flight delay monitoring service."""
    logger.info("Starting flight delay monitoring service...")
    monitor = DelayMonitor()
    monitor.start_monitoring_schedule()

def export_airports(output_file):
    """Export all airports to a JSON file."""
    logger.info(f"Exporting airports to {output_file}...")
    service = AirportService()
    count = service.export_airports_to_json(output_file)
    logger.info(f"Exported {count} airports")

def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(description='EU Flight Monitor')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Setup database command
    setup_parser = subparsers.add_parser('setup', help='Setup the database')
    
    # Simulate data command
    simulate_parser = subparsers.add_parser('simulate', help='Simulate data collection')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Start the flight delay monitoring service')
    
    # Export airports command
    export_parser = subparsers.add_parser('export', help='Export airports to JSON')
    export_parser.add_argument('--output', '-o', required=True, help='Output JSON file')
    
    # Query airport command
    query_parser = subparsers.add_parser('query', help='Query flights by airport')
    query_parser.add_argument('airport', help='IATA airport code')
    
    # Find delayed flights command
    delayed_parser = subparsers.add_parser('delayed', help='Find delayed flights')
    
    # Get flight details command
    flight_parser = subparsers.add_parser('flight', help='Get flight details')
    flight_parser.add_argument('flight_number', help='Flight number')
    
    args = parser.parse_args()
    
    if args.command == 'setup':
        setup_database()
    elif args.command == 'simulate':
        simulate_data()
    elif args.command == 'monitor':
        start_monitoring()
    elif args.command == 'export':
        export_airports(args.output)
    elif args.command == 'query':
        query_airport(args.airport)
    elif args.command == 'delayed':
        find_delayed()
    elif args.command == 'flight':
        get_flight(args.flight_number)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
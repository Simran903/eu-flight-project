import os
import sys
import logging
import csv
import json
from sqlalchemy import or_

# Add parent directory to import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import SessionLocal
from db.models import Airport

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AirportService:
    """Service for managing airport data."""
    
    def __init__(self):
        """Initialize with database session."""
        self.db = SessionLocal()
    
    def __del__(self):
        """Close database session on cleanup."""
        self.db.close()
    
    def get_all_airports(self):
        """
        Get all airports in the database.
        
        Returns:
            List of Airport objects
        """
        return self.db.query(Airport).all()
    
    def get_airport_by_code(self, code):
        """
        Get airport by IATA or ICAO code.
        
        Args:
            code: IATA or ICAO code
        
        Returns:
            Airport object or None if not found
        """
        return self.db.query(Airport).filter(
            or_(Airport.iata_code == code, Airport.icao_code == code)
        ).first()
    
    def get_airports_by_country(self, country):
        """
        Get all airports in a specific country.
        
        Args:
            country: Country name
        
        Returns:
            List of Airport objects
        """
        return self.db.query(Airport).filter(Airport.country == country).all()
    
    def create_airport(self, name, iata_code, icao_code, country, city, latitude, longitude):
        """
        Create a new airport.
        
        Args:
            name: Airport name
            iata_code: IATA code (3 letters)
            icao_code: ICAO code (4 letters)
            country: Country name
            city: City name
            latitude: Latitude coordinate
            longitude: Longitude coordinate
        
        Returns:
            Newly created Airport object
        """
        airport = Airport(
            name=name,
            iata_code=iata_code,
            icao_code=icao_code,
            country=country,
            city=city,
            latitude=latitude,
            longitude=longitude
        )
        
        try:
            self.db.add(airport)
            self.db.commit()
            self.db.refresh(airport)
            logger.info(f"Created airport: {name} ({iata_code})")
            return airport
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating airport: {str(e)}")
            raise
    
    def import_airports_from_csv(self, csv_file_path):
        """
        Import airports from a CSV file.
        
        Expected CSV format:
        name,iata_code,icao_code,country,city,latitude,longitude
        
        Args:
            csv_file_path: Path to CSV file
        
        Returns:
            Number of airports imported
        """
        count = 0
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    # Check if airport already exists
                    existing = self.get_airport_by_code(row['iata_code'])
                    if existing:
                        continue
                    
                    # Create new airport
                    self.create_airport(
                        name=row['name'],
                        iata_code=row['iata_code'],
                        icao_code=row['icao_code'],
                        country=row['country'],
                        city=row['city'],
                        latitude=float(row['latitude']),
                        longitude=float(row['longitude'])
                    )
                    count += 1
            
            logger.info(f"Imported {count} airports from CSV")
            return count
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error importing airports: {str(e)}")
            raise
    
    def export_airports_to_json(self, json_file_path):
        """
        Export all airports to a JSON file.
        
        Args:
            json_file_path: Path to output JSON file
        
        Returns:
            Number of airports exported
        """
        airports = self.get_all_airports()
        
        airports_data = [
            {
                'id': airport.id,
                'name': airport.name,
                'iata_code': airport.iata_code,
                'icao_code': airport.icao_code,
                'country': airport.country,
                'city': airport.city,
                'latitude': airport.latitude,
                'longitude': airport.longitude
            }
            for airport in airports
        ]
        
        try:
            with open(json_file_path, 'w', encoding='utf-8') as file:
                json.dump(airports_data, file, indent=2)
            
            logger.info(f"Exported {len(airports)} airports to {json_file_path}")
            return len(airports)
            
        except Exception as e:
            logger.error(f"Error exporting airports: {str(e)}")
            raise
"""SQLAlchemy models for the European Flight Monitor system."""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from db.database import Base

class Airport(Base):
    """Airport model representing European airports."""
    __tablename__ = "airports"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    iata_code = Column(String(3), unique=True, index=True)
    icao_code = Column(String(4), unique=True, index=True)
    country = Column(String, nullable=False)
    city = Column(String, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Relationships
    departures = relationship("Flight", back_populates="departure_airport", 
                             foreign_keys="Flight.departure_airport_id")
    arrivals = relationship("Flight", back_populates="arrival_airport", 
                           foreign_keys="Flight.arrival_airport_id")
    
    def __repr__(self):
        return f"<Airport {self.name} ({self.iata_code})>"

class Airline(Base):
    """Airline model for all airlines operating in Europe."""
    __tablename__ = "airlines"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    iata_code = Column(String(2), unique=True, index=True)
    icao_code = Column(String(3), unique=True, index=True)
    country = Column(String)
    
    # Relationships
    flights = relationship("Flight", back_populates="airline")
    
    def __repr__(self):
        return f"<Airline {self.name} ({self.iata_code})>"

class Flight(Base):
    """Flight model representing individual flights."""
    __tablename__ = "flights"
    
    id = Column(Integer, primary_key=True, index=True)
    flight_number = Column(String, index=True, nullable=False)
    airline_id = Column(Integer, ForeignKey("airlines.id"))
    departure_airport_id = Column(Integer, ForeignKey("airports.id"))
    arrival_airport_id = Column(Integer, ForeignKey("airports.id"))
    scheduled_departure = Column(DateTime, nullable=False)
    scheduled_arrival = Column(DateTime, nullable=False)
    actual_departure = Column(DateTime)
    actual_arrival = Column(DateTime)
    status = Column(String)  # scheduled, in-air, landed, cancelled, etc.
    
    # Relationships
    airline = relationship("Airline", back_populates="flights")
    departure_airport = relationship("Airport", back_populates="departures", 
                                   foreign_keys=[departure_airport_id])
    arrival_airport = relationship("Airport", back_populates="arrivals", 
                                 foreign_keys=[arrival_airport_id])
    flight_status = relationship("FlightStatus", back_populates="flight", uselist=False)
    
    def __repr__(self):
        return f"<Flight {self.flight_number}>"
    
    @property
    def departure_delay_minutes(self):
        """Calculate departure delay in minutes."""
        if not self.actual_departure or not self.scheduled_departure:
            return None
        delay = (self.actual_departure - self.scheduled_departure).total_seconds() / 60
        return max(0, int(delay))
    
    @property
    def arrival_delay_minutes(self):
        """Calculate arrival delay in minutes."""
        if not self.actual_arrival or not self.scheduled_arrival:
            return None
        delay = (self.actual_arrival - self.scheduled_arrival).total_seconds() / 60
        return max(0, int(delay))

class FlightStatus(Base):
    """Status details for flights, including delay information."""
    __tablename__ = "flight_status"
    
    id = Column(Integer, primary_key=True, index=True)
    flight_id = Column(Integer, ForeignKey("flights.id"), unique=True)
    is_delayed = Column(Boolean, default=False)
    delay_minutes = Column(Integer, default=0)
    delay_reason = Column(String)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    flight = relationship("Flight", back_populates="flight_status")
    
    def __repr__(self):
        return f"<FlightStatus flight_id={self.flight_id} delayed={self.is_delayed}>"
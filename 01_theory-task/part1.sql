-- 1. Database Design
-- • Design a database schema to store data for European airports, flight schedules, flight statuses,
-- and delays.
-- • Describe the tables (e.g., Airports, Flights, Airlines, FlightStatus) and their relationships.
-- • Explain how you would ensure data accuracy and maintain scalability.

-- Airports table: Stores information about all European airports
CREATE TABLE Airports (
    airport_id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    iata_code CHAR(3) UNIQUE,
    icao_code CHAR(4) UNIQUE,
    country VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    timezone VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Airlines table: Stores information about airlines operating in Europe
CREATE TABLE Airlines (
    airline_id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    iata_code CHAR(2) UNIQUE,
    icao_code CHAR(3) UNIQUE,
    country VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Flight schedules: Stores regular flight information
CREATE TABLE FlightSchedules (
    schedule_id INT PRIMARY KEY,
    flight_number VARCHAR(10) NOT NULL,
    airline_id INT NOT NULL,
    departure_airport_id INT NOT NULL,
    arrival_airport_id INT NOT NULL,
    scheduled_departure_time TIME NOT NULL,
    scheduled_arrival_time TIME NOT NULL,
    days_of_operation VARCHAR(7), -- e.g., "1234567" for all days, "135" for Mon, Wed, Fri
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (airline_id) REFERENCES Airlines(airline_id),
    FOREIGN KEY (departure_airport_id) REFERENCES Airports(airport_id),
    FOREIGN KEY (arrival_airport_id) REFERENCES Airports(airport_id)
);

-- Flights table: Stores actual flight instances
CREATE TABLE Flights (
    flight_id INT PRIMARY KEY,
    schedule_id INT,
    flight_date DATE NOT NULL,
    actual_departure_time DATETIME,
    actual_arrival_time DATETIME,
    status VARCHAR(50) DEFAULT 'Scheduled', -- e.g., Scheduled, Departed, Arrived, Delayed, Cancelled
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (schedule_id) REFERENCES FlightSchedules(schedule_id)
);

-- FlightDelays table: Tracks delay information specifically
CREATE TABLE FlightDelays (
    delay_id INT PRIMARY KEY,
    flight_id INT NOT NULL,
    departure_delay_minutes INT DEFAULT 0,
    arrival_delay_minutes INT DEFAULT 0,
    delay_reason VARCHAR(255),
    is_claimable BOOLEAN DEFAULT FALSE, -- Flag for delays over 2 hours
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (flight_id) REFERENCES Flights(flight_id)
);

-- ClaimableFlights view: Convenient view for flights delayed by more than 2 hours
CREATE VIEW ClaimableFlights AS
SELECT 
    f.flight_id,
    fs.flight_number,
    a.name AS airline_name,
    dep.name AS departure_airport,
    arr.name AS arrival_airport,
    f.flight_date,
    f.actual_departure_time,
    fs.scheduled_departure_time,
    fd.departure_delay_minutes,
    fd.arrival_delay_minutes
FROM Flights f
JOIN FlightSchedules fs ON f.schedule_id = fs.schedule_id
JOIN Airlines a ON fs.airline_id = a.airline_id
JOIN Airports dep ON fs.departure_airport_id = dep.airport_id
JOIN Airports arr ON fs.arrival_airport_id = arr.airport_id
JOIN FlightDelays fd ON f.flight_id = fd.flight_id
WHERE fd.departure_delay_minutes > 120 OR fd.arrival_delay_minutes > 120;



-- ## To ensure data accuracy and scalability:

-- Data Validation: Implement constraints and validation rules at both application and database levels.
-- Indexing Strategy: Create appropriate indexes for frequently queried fields (e.g., flight numbers, dates, airports).
-- Partitioning: Partition the Flights and FlightDelays tables by date to improve query performance.
-- Archiving Strategy: Move historical data to archive tables after a certain period.
-- Caching Layer: Implement Redis or a similar caching solution for frequently accessed data.
-- Automated Testing: Implement data consistency checks and reconciliation processes.
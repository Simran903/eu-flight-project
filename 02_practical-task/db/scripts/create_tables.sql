-- Airports table
CREATE TABLE IF NOT EXISTS airports (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    iata_code CHAR(3) UNIQUE,
    icao_code CHAR(4) UNIQUE,
    country VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    latitude FLOAT,
    longitude FLOAT
);

-- Create index on airport codes
CREATE INDEX IF NOT EXISTS idx_airport_iata ON airports(iata_code);
CREATE INDEX IF NOT EXISTS idx_airport_icao ON airports(icao_code);

-- Airlines table
CREATE TABLE IF NOT EXISTS airlines (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    iata_code CHAR(2) UNIQUE,
    icao_code CHAR(3) UNIQUE,
    country VARCHAR(100)
);

-- Create index on airline codes
CREATE INDEX IF NOT EXISTS idx_airline_iata ON airlines(iata_code);
CREATE INDEX IF NOT EXISTS idx_airline_icao ON airlines(icao_code);

-- Flights table
CREATE TABLE IF NOT EXISTS flights (
    id SERIAL PRIMARY KEY,
    flight_number VARCHAR(10) NOT NULL,
    airline_id INTEGER REFERENCES airlines(id),
    departure_airport_id INTEGER REFERENCES airports(id),
    arrival_airport_id INTEGER REFERENCES airports(id),
    scheduled_departure TIMESTAMP NOT NULL,
    scheduled_arrival TIMESTAMP NOT NULL,
    actual_departure TIMESTAMP,
    actual_arrival TIMESTAMP,
    status VARCHAR(20)
);

-- Create index on flight number and airports
CREATE INDEX IF NOT EXISTS idx_flight_number ON flights(flight_number);
CREATE INDEX IF NOT EXISTS idx_departure_airport ON flights(departure_airport_id);
CREATE INDEX IF NOT EXISTS idx_arrival_airport ON flights(arrival_airport_id);
CREATE INDEX IF NOT EXISTS idx_departure_time ON flights(scheduled_departure);

-- Flight status table
CREATE TABLE IF NOT EXISTS flight_status (
    id SERIAL PRIMARY KEY,
    flight_id INTEGER UNIQUE REFERENCES flights(id),
    is_delayed BOOLEAN DEFAULT FALSE,
    delay_minutes INTEGER DEFAULT 0,
    delay_reason VARCHAR(255),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on delayed flights
CREATE INDEX IF NOT EXISTS idx_delayed_flights ON flight_status(is_delayed) WHERE is_delayed = TRUE;
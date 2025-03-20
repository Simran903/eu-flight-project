# European Flight Monitoring System

A comprehensive system to monitor European flights, track delays, and support passenger refund claims.

## Features

- Complete European airport database
- Real-time flight monitoring
- Delay detection (2+ hours)
- Scalable database design
- Support for EU flight compensation claims
- Historical flight data analytics

## Setup Instructions

### 1. Clone or Download the Project
```bash
git clone https://github.com/yourusername/eu_flight_monitor.git
cd eu_flight_monitor
```

### 2. Set Up the Environment
```bash
# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Database
* Create a PostgreSQL database named `eu_flight_monitor`
* Edit `config.py` with your database credentials

### 4. Initialize the Database
```bash
python app.py setup
```

### 5. Run the Simulation
```bash
python app.py simulate
```

### 6. Query Flight Data
```bash
# Query flights for an airport
python app.py query FRA

# Find delayed flights
python app.py delayed

# Get details for a specific flight
python app.py flight LH1234
```

### 7. Start Monitoring Service (optional)
```bash
python app.py monitor
```

## Database Details

The system uses PostgreSQL with the following main tables:
- `airports` - Information about European airports
- `airlines` - Airline company details
- `flights` - Flight schedules and status
- `delays` - Tracked flight delays and reasons
- `compensation_claims` - EU261 compensation claim tracking

### Database Creation

You can initialize the database manually using:

```sql
-- Execute the SQL scripts in db/scripts/create_tables.sql
-- Insert sample data using db/scripts/sample_data.sql
```

## Usage Examples

### Basic Flight Query
```python
from services.flight_service import FlightService

# Initialize service
flight_service = FlightService()

# Get all flights for Frankfurt Airport
frankfurt_flights = flight_service.query_airport("FRA")
print(f"Found {len(frankfurt_flights)} flights")
```

### Finding Delayed Flights
```python
# Get all flights delayed by more than 2 hours
delayed_flights = flight_service.find_delayed(hours=2)
for flight in delayed_flights:
    print(f"Flight {flight.flight_number} delayed by {flight.delay_minutes} minutes")
```

### Monitoring Mode
In monitoring mode, the system continuously checks flight status and logs delays:

```bash
python app.py monitor --interval 5 --log-file delays.log
```

## API Integration

The system can connect to external flight data APIs:
- FlightAware API
- Eurocontrol Network Manager API
- OpenSky Network

Configure API keys in `config.py` before using these integrations.

## Testing

Run the test suite with:

```bash
python -m pytest tests/
```

## Troubleshooting

Common issues:
- Database connection errors: Check PostgreSQL credentials in `config.py`
- API rate limiting: Adjust timing in `api_client.py`
- Memory usage concerns: Use the `--limit` flag in monitoring mode
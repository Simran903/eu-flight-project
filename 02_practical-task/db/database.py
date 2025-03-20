import sys
import os
import logging
from sqlalchemy import text
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Add parent directory to import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_CONNECTION_STRING

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create SQLAlchemy base class
Base = declarative_base()

# Create engine
engine = create_engine(DB_CONNECTION_STRING)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency for getting DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables in the database."""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tables created successfully")

def execute_sql_script(script_path):
    """Execute SQL script file."""
    logger.info(f"Executing SQL script: {script_path}")
    with open(script_path, 'r') as f:
        sql = f.read()

    with engine.connect() as conn:
        conn.execute(text(sql))  # Use 'text()' to execute raw SQL
        conn.commit()

    logger.info("SQL script executed successfully")

def seed_sample_data():
    """Seed database with sample data."""
    script_path = os.path.join(os.path.dirname(__file__), 'scripts', 'sample_data.sql')
    execute_sql_script(script_path)
    logger.info("Sample data inserted successfully")

if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else None
    
    if command == "create":
        create_tables()
    elif command == "seed":
        seed_sample_data()
    else:
        print("Available commands: create, seed")
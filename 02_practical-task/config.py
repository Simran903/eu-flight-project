import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection string
DB_CONNECTION_STRING = "postgresql://neondb_owner:npg_drXw7TY6pHyF@ep-hidden-forest-a5ite52n-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"

# API Keys (replace with actual keys in production)
AVIATION_API_KEY = os.getenv('AVIATION_API_KEY', 'your_api_key_here')

# Application settings
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
DELAY_THRESHOLD_MINUTES = int(os.getenv('DELAY_THRESHOLD_MINUTES', '120'))  # 2 hours

# Cache settings
CACHE_EXPIRY = 3600  # Cache expiry in seconds
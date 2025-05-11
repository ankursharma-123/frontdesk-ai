import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_key_for_testing')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///frontdesk.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # LiveKit Configuration
    LIVEKIT_API_KEY = os.getenv('LIVEKIT_API_KEY')
    LIVEKIT_API_SECRET = os.getenv('LIVEKIT_API_SECRET')
    LIVEKIT_URL = os.getenv('LIVEKIT_URL', 'ws://localhost:7880')
    
    # OpenAI Configuration (for AI agent)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Request timeout in minutes
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 30))
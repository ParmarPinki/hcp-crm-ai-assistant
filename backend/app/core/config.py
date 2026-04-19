import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    groq_api_key: str = os.getenv('GROQ_API_KEY', '')
    model_name: str = os.getenv('MODEL_NAME', 'gemma2-9b-it')
    database_url: str = os.getenv('DATABASE_URL', 'mysql+pymysql://root:root@localhost:3306/hcp_crm')
    allow_mock_llm: bool = os.getenv('ALLOW_MOCK_LLM', 'true').lower() == 'true'
    cors_origins: str = os.getenv('CORS_ORIGINS', 'http://localhost:5173')

settings = Settings()

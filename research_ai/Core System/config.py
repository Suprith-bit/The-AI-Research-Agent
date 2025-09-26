import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")

    # LLM Settings
    MODEL_NAME = "gemini-2.5-flash"
    MAX_TOKENS = 1500
    TEMPERATURE = 0.3

    # Search Settings
    MAX_SEARCH_RESULTS = 10
    MAX_SOURCES_PER_QUERY = 5

    # Agent Settings
    MAX_SUB_QUESTIONS = 6
    MIN_SUB_QUESTIONS = 3

    @classmethod
    def validate(cls):
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment")
        if not cls.SERPER_API_KEY:
            raise ValueError("SERPER_API_KEY not found in environment")
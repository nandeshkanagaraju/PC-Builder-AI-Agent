import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/pc_agent_db")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@youragent.com")

    # Add other configurations like scraper settings, API limits etc.
    SCRAPER_TARGET_URLS = {
        "newegg": "https://www.newegg.com/p/{}?cm_mmc=pricompc", # Example, actual scraping logic is more complex
        "amazon": "https://www.amazon.com/dp/{}",
        # Add more retailers
    }
    TRUSTED_RETAILERS = ["newegg.com", "amazon.com", "bestbuy.com"] # Simple list for MVP
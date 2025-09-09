import sys
import os

# Add the project root to the path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import SessionLocal
from services.scraper_service import update_product_prices
from services.notification_service import NotificationService

def run_scheduled_tasks():
    db = SessionLocal()
    try:
        print(f"[{datetime.now()}] Starting scheduled tasks...")
        # 1. Update prices
        update_product_prices(db)

        # 2. Check for price drops and send notifications
        notification_service = NotificationService(db)
        notification_service.check_for_price_drops()

        print(f"[{datetime.now()}] Scheduled tasks completed.")
    except Exception as e:
        print(f"[{datetime.now()}] Error during scheduled tasks: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    from datetime import datetime
    run_scheduled_tasks()
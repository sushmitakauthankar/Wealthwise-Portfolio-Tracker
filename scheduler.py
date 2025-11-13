from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from database import SessionLocal
import crud

def update_prices_job():
    print("Updating prices from mock data...")
    db: Session = SessionLocal()
    try:
        crud.load_prices_from_json_to_db(db)
        print("Prices updated successfully.")
    except Exception as e:
        print(f"Error updating prices: {e}")
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_prices_job, "interval", hours=3)
    scheduler.start()
    print("Background scheduler started (runs every 3 hours).")

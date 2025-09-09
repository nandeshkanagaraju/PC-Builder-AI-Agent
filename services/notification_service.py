import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import Session
from models import SavedBuild, BuildPart, Product, PriceEntry, User
from config import Config
from datetime import datetime, timedelta

class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def send_email(self, to_email: str, subject: str, body: str):
        if not Config.EMAIL_USER or not Config.EMAIL_PASSWORD:
            print("Email credentials not configured. Skipping email send.")
            return

        msg = MIMEMultipart()
        msg['From'] = Config.FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP(Config.EMAIL_HOST, Config.EMAIL_PORT)
            server.starttls()  # Upgrade connection to secure TLS
            server.login(Config.EMAIL_USER, Config.EMAIL_PASSWORD)
            text = msg.as_string()
            server.sendmail(Config.FROM_EMAIL, to_email, text)
            server.quit()
            print(f"Email sent to {to_email} for subject '{subject}'")
            return True
        except Exception as e:
            print(f"Failed to send email to {to_email}: {e}")
            return False

    def check_for_price_drops(self):
        saved_builds = self.db.query(SavedBuild).all()
        notification_sent_count = 0

        for build in saved_builds:
            user = build.user
            if not user or not user.email:
                continue

            price_drops_found = []
            current_build_cost = 0

            # Get the latest price for each part in the saved build
            for build_part in build.parts:
                product = build_part.product
                if not product: continue

                latest_price_entry = self.db.query(PriceEntry) \
                    .filter(PriceEntry.product_id == product.id) \
                    .order_by(PriceEntry.timestamp.desc(), PriceEntry.price.asc()) \
                    .first()

                if latest_price_entry:
                    current_build_cost += latest_price_entry.price
                    # Update build_part with current price
                    build_part.current_price = latest_price_entry.price
                    build_part.lowest_price_retailer = latest_price_entry.retailer_name
                    build_part.lowest_price_url = latest_price_entry.retailer_url
                    self.db.add(build_part) # Mark for update

                    # Check for price drop (e.g., more than 5% or $10 below recommended price)
                    if latest_price_entry.price < build_part.recommended_price and \
                       (build_part.recommended_price - latest_price_entry.price) > build_part.recommended_price * 0.05: # 5% drop
                        price_drops_found.append({
                            "product_name": product.name,
                            "old_price": build_part.recommended_price,
                            "new_price": latest_price_entry.price,
                            "retailer": latest_price_entry.retailer_name,
                            "url": latest_price_entry.retailer_url
                        })
            self.db.commit()

            # If price drops found and not notified recently (e.g., last 24 hours)
            if price_drops_found and (build.notified_at is None or build.notified_at < datetime.now() - timedelta(hours=24)):
                subject = f"Price Drop Alert for Your Saved PC Build!"
                body = (
                    f"Hi {user.name if user.name else 'there'},\n\n"
                    f"Great news! We've found price drops for components in your saved PC build:\n\n"
                )
                for drop in price_drops_found:
                    body += (
                        f"- {drop['product_name']}:\n"
                        f"  - Old Price: ${drop['old_price']:.2f}\n"
                        f"  - New Price: ${drop['new_price']:.2f} (a saving of ${drop['old_price'] - drop['new_price']:.2f}!)\n"
                        f"  - Retailer: {drop['retailer']}\n"
                        f"  - Link: {drop['url']}\n\n"
                    )
                body += (
                    f"Log in to your account or visit our platform to review your updated build.\n\n"
                    f"Happy building,\nYour PC Agent Team"
                )

                if self.send_email(user.email, subject, body):
                    build.notified_at = datetime.now() # Update notification timestamp
                    self.db.add(build)
                    self.db.commit()
                    notification_sent_count += 1
        print(f"Finished checking price drops. Sent {notification_sent_count} notifications.")

if __name__ == "__main__":
    from database import SessionLocal, create_db_and_tables
    create_db_and_tables()
    db = SessionLocal()
    notification_service = NotificationService(db)
    notification_service.check_for_price_drops()
    db.close()
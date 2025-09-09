import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from models import Product, PriceEntry
from config import Config
import time
import random

def scrape_amazon(product_url: str) -> float | None:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(product_url, headers=headers, timeout=10)
        response.raise_for_status() # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.text, 'html.parser')

        # This is a very basic selector, often changes.
        # You'll need to inspect Amazon's current HTML structure.
        price_span = soup.find('span', class_='a-offscreen')
        if price_span:
            price_text = price_span.get_text(strip=True).replace('$', '').replace(',', '')
            return float(price_text)
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error scraping Amazon {product_url}: {e}")
        return None
    except Exception as e:
        print(f"Failed to parse Amazon price for {product_url}: {e}")
        return None

def scrape_newegg(product_url: str) -> float | None:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(product_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Again, highly dependent on Newegg's current HTML
        price_strong = soup.find('li', class_='price-current').find('strong')
        if price_strong:
            price_text = price_strong.get_text(strip=True).replace('$', '').replace(',', '')
            return float(price_text)
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error scraping Newegg {product_url}: {e}")
        return None
    except Exception as e:
        print(f"Failed to parse Newegg price for {product_url}: {e}")
        return None

def get_product_url_for_retailer(product: Product, retailer: str) -> str | None:
    # This function needs to dynamically generate or look up the correct URL for a product
    # on a specific retailer's site. This is often the hardest part.
    # For MVP, you might store these URLs directly in your product data.
    # Or build a mapping for common products.
    # For example, searching by model number on the retailer's site might be needed.

    if retailer == "amazon.com":
        # Placeholder: You'd need a way to get the Amazon ASIN or search for the product
        return f"https://www.amazon.com/s?k={product.name.replace(' ', '+')}"
    elif retailer == "newegg.com":
        # Placeholder: You'd need Newegg item number or search logic
        return f"https://www.newegg.com/p/pl?d={product.name.replace(' ', '+')}"
    return None

def update_product_prices(db: Session):
    products = db.query(Product).all()
    retailers_to_scrape = Config.TRUSTED_RETAILERS # Use your configured list

    for product in products:
        print(f"Scraping prices for {product.name}...")
        for retailer in retailers_to_scrape:
            product_url = get_product_url_for_retailer(product, retailer)
            if not product_url:
                print(f"Could not find URL for {product.name} on {retailer}")
                continue

            current_price = None
            if "amazon.com" in retailer: # Simplified check
                current_price = scrape_amazon(product_url)
            elif "newegg.com" in retailer: # Simplified check
                current_price = scrape_newegg(product_url)
            # Add more scrapers for other retailers

            if current_price is not None:
                new_price_entry = PriceEntry(
                    product_id=product.id,
                    retailer_name=retailer,
                    retailer_url=product_url, # This should ideally be the direct product page URL
                    price=current_price
                )
                db.add(new_price_entry)
                print(f"  -> Found {current_price} on {retailer}")
            time.sleep(random.uniform(1, 3)) # Be polite, avoid getting blocked

    db.commit()
    print("Price update complete.")

if __name__ == "__main__":
    from database import SessionLocal, create_db_and_tables
    # Ensure tables exist
    create_db_and_tables()
    # Add some dummy products if not present for testing
    db = SessionLocal()
    if not db.query(Product).first():
        print("Adding dummy products for scraping test...")
        dummy_cpu = Product(name="AMD Ryzen 5 5600X", category="CPU", brand="AMD", model="5600X", specs={"cores": 6, "threads": 12, "socket": "AM4"})
        dummy_gpu = Product(name="NVIDIA GeForce RTX 3060", category="GPU", brand="NVIDIA", model="RTX 3060", specs={"vram": 12, "memory_type": "GDDR6"})
        db.add(dummy_cpu)
        db.add(dummy_gpu)
        db.commit()
        db.refresh(dummy_cpu)
        db.refresh(dummy_gpu)
        # For testing, you'd manually set up product URLs or use a search logic here
        # For the dummy data, let's just make up some URLs
        db.add(PriceEntry(product_id=dummy_cpu.id, retailer_name="amazon.com", retailer_url="https://www.amazon.com/dp/B08V5Q4K9L", price=299.99))
        db.add(PriceEntry(product_id=dummy_cpu.id, retailer_name="newegg.com", retailer_url="https://www.newegg.com/amd-ryzen-5-5600x/p/N82E16819113666", price=299.99))
        db.commit()

    print("Running price update...")
    update_product_prices(db)
    db.close()
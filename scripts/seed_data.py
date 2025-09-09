# scripts/seed_data.py

import sys
import os
from datetime import datetime
import random
from sqlalchemy.orm import Session
from sqlalchemy import func

# Add the project root to the path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import SessionLocal, create_db_and_tables
from models import Product, PriceEntry, User, SavedBuild, BuildPart # Import all models

def seed_data():
    db: Session = SessionLocal()
    try:
        print("Starting to seed initial product data...")

        # --- IMPORTANT: Clear existing data for a fresh start ---
        # Be careful with this in a real application, as it deletes ALL data!
        db.query(BuildPart).delete()
        db.query(SavedBuild).delete()
        db.query(User).delete()
        db.query(PriceEntry).delete()
        db.query(Product).delete()
        db.commit()
        print("Cleared existing data from tables.")
        # --- End of clear data section ---

        products_to_add = []

        # --- CPUs ---
        # High-end gaming/productivity
        products_to_add.append(Product(name="Intel Core i9-14900K", category="CPU", brand="Intel", model="i9-14900K", specs={"cores": 24, "threads": 32, "socket": "LGA1700", "tdp": 125, "ram_type": "DDR5"}, gaming_score=99, productivity_score=100, aesthetic_tags=""))
        products_to_add.append(Product(name="AMD Ryzen 9 7950X3D", category="CPU", brand="AMD", model="7950X3D", specs={"cores": 16, "threads": 32, "socket": "AM5", "tdp": 120, "ram_type": "DDR5"}, gaming_score=98, productivity_score=98, aesthetic_tags=""))
        # Mid-range gaming/productivity (good for $1500 builds)
        products_to_add.append(Product(name="Intel Core i7-13700K", category="CPU", brand="Intel", model="i7-13700K", specs={"cores": 16, "threads": 24, "socket": "LGA1700", "tdp": 125, "ram_type": "DDR5"}, gaming_score=90, productivity_score=95, aesthetic_tags=""))
        products_to_add.append(Product(name="AMD Ryzen 7 7800X3D", category="CPU", brand="AMD", model="7800X3D", specs={"cores": 8, "threads": 16, "socket": "AM5", "tdp": 120, "ram_type": "DDR5"}, gaming_score=98, productivity_score=85, aesthetic_tags=""))
        products_to_add.append(Product(name="Intel Core i5-14600K", category="CPU", brand="Intel", model="i5-14600K", specs={"cores": 14, "threads": 20, "socket": "LGA1700", "tdp": 125, "ram_type": "DDR5"}, gaming_score=85, productivity_score=88, aesthetic_tags=""))
        # Entry-level / Budget
        products_to_add.append(Product(name="Intel Core i5-12400F", category="CPU", brand="Intel", model="i5-12400F", specs={"cores": 6, "threads": 12, "socket": "LGA1700", "tdp": 65, "ram_type": "DDR4"}, gaming_score=65, productivity_score=70, aesthetic_tags=""))
        products_to_add.append(Product(name="AMD Ryzen 5 5600X", category="CPU", brand="AMD", model="5600X", specs={"cores": 6, "threads": 12, "socket": "AM4", "tdp": 65, "ram_type": "DDR4"}, gaming_score=70, productivity_score=68, aesthetic_tags=""))

        # --- GPUs ---
        # High-end gaming
        products_to_add.append(Product(name="NVIDIA GeForce RTX 4090", category="GPU", brand="NVIDIA", model="RTX 4090", specs={"vram_gb": 24, "memory_type": "GDDR6X", "tdp": 450}, gaming_score=100, productivity_score=99, aesthetic_tags="RGB"))
        products_to_add.append(Product(name="AMD Radeon RX 7900 XTX", category="GPU", brand="AMD", model="RX 7900 XTX", specs={"vram_gb": 24, "memory_type": "GDDR6", "tdp": 355}, gaming_score=95, productivity_score=90, aesthetic_tags=""))
        # Mid-range gaming (good for $1500 builds)
        products_to_add.append(Product(name="NVIDIA GeForce RTX 4070 Super", category="GPU", brand="NVIDIA", model="RTX 4070 Super", specs={"vram_gb": 12, "memory_type": "GDDR6X", "tdp": 220}, gaming_score=88, productivity_score=80, aesthetic_tags="RGB"))
        products_to_add.append(Product(name="AMD Radeon RX 7800 XT", category="GPU", brand="AMD", model="RX 7800 XT", specs={"vram_gb": 16, "memory_type": "GDDR6", "tdp": 263}, gaming_score=85, productivity_score=78, aesthetic_tags=""))
        products_to_add.append(Product(name="NVIDIA GeForce RTX 4060 Ti", category="GPU", brand="NVIDIA", model="RTX 4060 Ti", specs={"vram_gb": 8, "memory_type": "GDDR6", "tdp": 160}, gaming_score=75, productivity_score=70, aesthetic_tags=""))
        # Entry-level / Budget
        products_to_add.append(Product(name="AMD Radeon RX 6600", category="GPU", brand="AMD", model="RX 6600", specs={"vram_gb": 8, "memory_type": "GDDR6", "tdp": 132}, gaming_score=55, productivity_score=50, aesthetic_tags=""))

        # --- Motherboards ---
        # AM5 (DDR5)
        products_to_add.append(Product(name="MSI MAG B650 TOMAHAWK WIFI", category="Motherboard", brand="MSI", model="B650 TOMAHAWK WIFI", specs={"socket": "AM5", "ram_type": "DDR5", "form_factor": "ATX"}, aesthetic_tags="RGB"))
        products_to_add.append(Product(name="Gigabyte B650 AORUS ELITE AX", category="Motherboard", brand="Gigabyte", model="B650 AORUS ELITE AX", specs={"socket": "AM5", "ram_type": "DDR5", "form_factor": "ATX"}, aesthetic_tags=""))
        # LGA1700 (DDR5)
        products_to_add.append(Product(name="ASUS ROG STRIX Z790-E GAMING WIFI II", category="Motherboard", brand="ASUS", model="Z790-E GAMING WIFI II", specs={"socket": "LGA1700", "ram_type": "DDR5", "form_factor": "ATX"}, aesthetic_tags="RGB"))
        products_to_add.append(Product(name="MSI PRO Z790-A WIFI", category="Motherboard", brand="MSI", model="Z790-A WIFI", specs={"socket": "LGA1700", "ram_type": "DDR5", "form_factor": "ATX"}, aesthetic_tags=""))
        # LGA1700 (DDR4)
        products_to_add.append(Product(name="ASRock B660M Pro RS", category="Motherboard", brand="ASRock", model="B660M Pro RS", specs={"socket": "LGA1700", "ram_type": "DDR4", "form_factor": "Micro-ATX"}, aesthetic_tags=""))
        # AM4 (DDR4)
        products_to_add.append(Product(name="MSI B550 GAMING PLUS", category="Motherboard", brand="MSI", model="B550 GAMING PLUS", specs={"socket": "AM4", "ram_type": "DDR4", "form_factor": "ATX"}, aesthetic_tags=""))

        # --- RAM ---
        products_to_add.append(Product(name="G.Skill Trident Z5 RGB 32GB DDR5-6000", category="RAM", brand="G.Skill", model="Trident Z5 RGB 32GB 6000", specs={"capacity_gb": 32, "ram_type": "DDR5", "speed_mt_s": 6000}, aesthetic_tags="RGB"))
        products_to_add.append(Product(name="Corsair Vengeance RGB DDR5 32GB-6000", category="RAM", brand="Corsair", model="Vengeance RGB DDR5 32GB 6000", specs={"capacity_gb": 32, "ram_type": "DDR5", "speed_mt_s": 6000}, aesthetic_tags="RGB"))
        products_to_add.append(Product(name="G.Skill Ripjaws S5 32GB DDR5-5600", category="RAM", brand="G.Skill", model="Ripjaws S5 32GB 5600", specs={"capacity_gb": 32, "ram_type": "DDR5", "speed_mt_s": 5600}, aesthetic_tags="minimalist"))
        products_to_add.append(Product(name="Teamgroup T-Force Vulcan Z 16GB DDR4-3200", category="RAM", brand="Teamgroup", model="Vulcan Z 16GB 3200", specs={"capacity_gb": 16, "ram_type": "DDR4", "speed_mt_s": 3200}, aesthetic_tags=""))

        # --- Storage ---
        products_to_add.append(Product(name="Samsung 990 Pro 2TB NVMe SSD", category="Storage", brand="Samsung", model="990 Pro 2TB", specs={"capacity_gb": 2000, "type": "SSD", "interface": "NVMe PCIe 4.0"}, aesthetic_tags=""))
        products_to_add.append(Product(name="Samsung 970 Evo Plus 1TB NVMe SSD", category="Storage", brand="Samsung", model="970 Evo Plus 1TB", specs={"capacity_gb": 1000, "type": "SSD", "interface": "NVMe PCIe 3.0"}, aesthetic_tags=""))
        products_to_add.append(Product(name="Crucial P5 Plus 1TB NVMe SSD", category="Storage", brand="Crucial", model="P5 Plus 1TB", specs={"capacity_gb": 1000, "type": "SSD", "interface": "NVMe PCIe 4.0"}, aesthetic_tags=""))
        products_to_add.append(Product(name="Western Digital Blue 500GB SSD", category="Storage", brand="WD", model="WD Blue 500GB", specs={"capacity_gb": 500, "type": "SSD", "interface": "SATA"}, aesthetic_tags=""))

        # --- Power Supplies (PSU) ---
        products_to_add.append(Product(name="Corsair RM1000e 1000W 80+ Gold PSU", category="PSU", brand="Corsair", model="RM1000e", specs={"wattage": 1000, "efficiency": "80+ Gold"}, aesthetic_tags=""))
        products_to_add.append(Product(name="Corsair RM850e 850W 80+ Gold PSU", category="PSU", brand="Corsair", model="RM850e", specs={"wattage": 850, "efficiency": "80+ Gold"}, aesthetic_tags=""))
        products_to_add.append(Product(name="EVGA SuperNOVA 750 GT 750W 80+ Gold PSU", category="PSU", brand="EVGA", model="750 GT", specs={"wattage": 750, "efficiency": "80+ Gold"}, aesthetic_tags=""))
        products_to_add.append(Product(name="Cooler Master MWE Gold 650 V2 650W 80+ Gold PSU", category="PSU", brand="Cooler Master", model="MWE Gold 650", specs={"wattage": 650, "efficiency": "80+ Gold"}, aesthetic_tags=""))

        # --- Cases ---
        products_to_add.append(Product(name="NZXT H7 Flow", category="Case", brand="NZXT", model="H7 Flow", specs={"form_factor": "ATX Mid Tower", "color": "black"}, aesthetic_tags="minimalist"))
        products_to_add.append(Product(name="Lian Li O11 Dynamic EVO", category="Case", brand="Lian Li", model="O11 Dynamic EVO", specs={"form_factor": "ATX Mid Tower", "color": "black"}, aesthetic_tags="RGB,aesthetic"))
        products_to_add.append(Product(name="Fractal Design Pop Air", category="Case", brand="Fractal Design", model="Pop Air", specs={"form_factor": "ATX Mid Tower", "color": "white"}, aesthetic_tags="white,RGB"))
        products_to_add.append(Product(name="Cooler Master NR200P Max", category="Case", brand="Cooler Master", model="NR200P Max", specs={"form_factor": "Mini ITX", "color": "black"}, aesthetic_tags="small,minimalist"))

        # --- Monitors ---
        products_to_add.append(Product(name="Samsung Odyssey G7 27\" 1440p 240Hz", category="Monitor", brand="Samsung", model="Odyssey G7 27", specs={"resolution_width": 2560, "resolution_height": 1440, "refresh_rate_hz": 240, "size_inches": 27}, aesthetic_tags="gaming"))
        products_to_add.append(Product(name="Dell S2721DGF 27\" 1440p 165Hz Monitor", category="Monitor", brand="Dell", model="S2721DGF", specs={"resolution_width": 2560, "resolution_height": 1440, "refresh_rate_hz": 165, "size_inches": 27}, aesthetic_tags=""))
        products_to_add.append(Product(name="Acer Nitro XV240Y 24\" 1080p 165Hz Monitor", category="Monitor", brand="Acer", model="Nitro XV240Y", specs={"resolution_width": 1920, "resolution_height": 1080, "refresh_rate_hz": 165, "size_inches": 24}, aesthetic_tags="budget"))

        # --- Keyboards ---
        products_to_add.append(Product(name="Keychron K2 Pro Wireless Mechanical Keyboard", category="Keyboard", brand="Keychron", model="K2 Pro", specs={"type": "mechanical", "wireless": True, "layout": "75%"}, aesthetic_tags="minimalist,white"))
        products_to_add.append(Product(name="Corsair K70 RGB PRO Mechanical Keyboard", category="Keyboard", brand="Corsair", model="K70 RGB PRO", specs={"type": "mechanical", "wireless": False, "layout": "full"}, aesthetic_tags="RGB"))

        # --- Mice ---
        products_to_add.append(Product(name="Logitech G Pro X Superlight Wireless Mouse", category="Mouse", brand="Logitech", model="G Pro X Superlight", specs={"type": "wireless", "dpi": 25600, "weight_g": 63}, aesthetic_tags="minimalist"))
        products_to_add.append(Product(name="Razer DeathAdder V3 Pro Wireless Mouse", category="Mouse", brand="Razer", model="DeathAdder V3 Pro", specs={"type": "wireless", "dpi": 30000, "weight_g": 64}, aesthetic_tags="gaming"))

        db.add_all(products_to_add)
        db.commit() # Commit products first to get IDs
        print(f"Added {len(products_to_add)} products.")

        # --- Add realistic dummy prices for these products ---
        # Get all products from the DB to ensure they have IDs
        all_products = db.query(Product).all()
        price_entries = []
        retailers = ["amazon.com", "newegg.com", "bestbuy.com"]

        for product in all_products:
            # Determine a realistic base price range for each category
            base_price = 0
            if product.category == "CPU":
                if "i9" in product.model or "Ryzen 9" in product.model: base_price = random.uniform(500, 650)
                elif "i7" in product.model or "Ryzen 7" in product.model: base_price = random.uniform(300, 450)
                elif "i5" in product.model or "Ryzen 5" in product.model: base_price = random.uniform(150, 250)
            elif product.category == "GPU":
                if "4090" in product.model or "7900" in product.model: base_price = random.uniform(900, 1800)
                elif "4070" in product.model or "7800" in product.model: base_price = random.uniform(450, 650)
                elif "4060" in product.model or "6600" in product.model: base_price = random.uniform(200, 350)
            elif product.category == "Motherboard":
                if "Z790" in product.model: base_price = random.uniform(250, 400)
                elif "B650" in product.model: base_price = random.uniform(180, 280)
                elif "B660" in product.model or "B550" in product.model: base_price = random.uniform(100, 180)
            elif product.category == "RAM":
                if 32 in product.specs.values(): base_price = random.uniform(80, 150)
                elif 16 in product.specs.values(): base_price = random.uniform(40, 80)
            elif product.category == "Storage":
                if 2000 in product.specs.values(): base_price = random.uniform(120, 200)
                elif 1000 in product.specs.values(): base_price = random.uniform(60, 120)
                elif 500 in product.specs.values(): base_price = random.uniform(30, 60)
            elif product.category == "PSU":
                if 1000 in product.specs.values(): base_price = random.uniform(120, 180)
                elif 850 in product.specs.values(): base_price = random.uniform(90, 140)
                elif 750 in product.specs.values(): base_price = random.uniform(70, 100)
                elif 650 in product.specs.values(): base_price = random.uniform(60, 80)
            elif product.category == "Case": base_price = random.uniform(60, 150)
            elif product.category == "Monitor": base_price = random.uniform(150, 400)
            elif product.category == "Keyboard": base_price = random.uniform(50, 150)
            elif product.category == "Mouse": base_price = random.uniform(30, 100)

            if base_price > 0:
                for retailer in retailers:
                    # Simulate price fluctuation
                    price = round(base_price * random.uniform(0.95, 1.05), 2)
                    # Generic URL placeholder, in real app you'd need actual product page URLs
                    url = f"https://www.{retailer}/{product.name.replace(' ', '-').lower()}"
                    price_entries.append(PriceEntry(
                        product_id=product.id,
                        retailer_name=retailer,
                        retailer_url=url,
                        price=price
                    ))
            else:
                print(f"Warning: No base price defined for {product.name} ({product.category}). Skipping price entry.")

        db.add_all(price_entries)
        db.commit()
        print(f"Added {len(price_entries)} price entries.")

        print("Initial product data seeding complete.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
        # Re-raise the exception to see full traceback for debugging if needed
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_db_and_tables() # Ensure tables exist before trying to seed
    seed_data()
from sqlalchemy.orm import Session
from models import Product, PriceEntry

class RecommendationService:
    def __init__(self, db: Session):
        self.db = db

    def get_lowest_price_for_product(self, product_id: int):
        # Get the latest lowest price for a product
        latest_prices = self.db.query(PriceEntry) \
            .filter(PriceEntry.product_id == product_id) \
            .order_by(PriceEntry.timestamp.desc(), PriceEntry.price.asc()) \
            .first()
        return latest_prices # Returns PriceEntry object or None

    def get_compatible_parts(self, category: str, requirements: dict):
        # Basic filtering logic based on requirements (e.g., CPU socket, RAM type)
        query = self.db.query(Product).filter(Product.category == category)

        if category == "CPU" and requirements.get("socket"):
            query = query.filter(Product.specs["socket"].astext == requirements["socket"])
        if category == "Motherboard" and requirements.get("socket"):
            query = query.filter(Product.specs["socket"].astext == requirements["socket"])
        if category == "RAM" and requirements.get("ram_type"):
            query = query.filter(Product.specs["ram_type"].astext == requirements["ram_type"])

        # Add more compatibility rules as needed

        return query.all()

    def recommend_build(self, user_prefs: dict) -> dict | None:
        budget = user_prefs.get("budget")
        use_case = user_prefs.get("use_case", "general") # gaming, productivity, general
        aesthetic = user_prefs.get("aesthetic")

        if not budget or budget <= 0:
            return None # Cannot recommend without a budget

        recommended_parts = {}
        total_cost = 0

        # --- Simplified Component Selection Logic ---
        # This is where the core logic to pick parts resides.
        # It's a heuristic for MVP.

        # 1. CPU
        cpus = self.db.query(Product).filter(Product.category == "CPU").all()
        selected_cpu = None
        if use_case == "gaming":
            cpus.sort(key=lambda x: x.gaming_score, reverse=True)
        elif use_case == "productivity":
            cpus.sort(key=lambda x: x.productivity_score, reverse=True)
        else:
            cpus.sort(key=lambda x: (x.gaming_score + x.productivity_score), reverse=True)

        for cpu in cpus:
            price_entry = self.get_lowest_price_for_product(cpu.id)
            if price_entry and price_entry.price <= budget * 0.3: # Allocate max 30% of budget for CPU
                selected_cpu = cpu
                recommended_parts["CPU"] = {"product": cpu, "price_entry": price_entry}
                total_cost += price_entry.price
                break
        if not selected_cpu: return None # Can't build without a CPU

        # Update requirements based on selected CPU for compatibility
        compat_reqs = {"socket": selected_cpu.specs.get("socket"), "ram_type": selected_cpu.specs.get("ram_type")}

        # 2. Motherboard
        motherboards = self.get_compatible_parts("Motherboard", compat_reqs)
        motherboards.sort(key=lambda x: (x.gaming_score + x.productivity_score), reverse=True)
        selected_mb = None
        for mb in motherboards:
            price_entry = self.get_lowest_price_for_product(mb.id)
            if price_entry and (total_cost + price_entry.price) <= budget * 0.5: # MB + CPU max 50%
                selected_mb = mb
                recommended_parts["Motherboard"] = {"product": mb, "price_entry": price_entry}
                total_cost += price_entry.price
                break
        if not selected_mb: return None

        # 3. GPU (most important for gaming)
        gpus = self.db.query(Product).filter(Product.category == "GPU").all()
        if use_case == "gaming":
            gpus.sort(key=lambda x: x.gaming_score, reverse=True)
        else: # For other cases, still need a GPU but not top tier
            gpus.sort(key=lambda x: (x.gaming_score + x.productivity_score), reverse=True)
        selected_gpu = None
        for gpu in gpus:
            price_entry = self.get_lowest_price_for_product(gpu.id)
            if price_entry and (total_cost + price_entry.price) <= budget * (0.9 if use_case == "gaming" else 0.7):
                selected_gpu = gpu
                recommended_parts["GPU"] = {"product": gpu, "price_entry": price_entry}
                total_cost += price_entry.price
                break
        if not selected_gpu: return None

        # 4. RAM
        rams = self.get_compatible_parts("RAM", compat_reqs)
        rams.sort(key=lambda x: x.specs.get("capacity_gb", 0), reverse=True) # Prioritize higher capacity
        selected_ram = None
        # Simple logic: aim for 16GB or 32GB based on budget/use case
        target_ram_gb = 16 if budget < 1000 and use_case != "productivity" else 32
        for ram in rams:
            if ram.specs.get("capacity_gb", 0) >= target_ram_gb:
                price_entry = self.get_lowest_price_for_product(ram.id)
                if price_entry and (total_cost + price_entry.price) <= budget * 0.95:
                    selected_ram = ram
                    recommended_parts["RAM"] = {"product": ram, "price_entry": price_entry}
                    total_cost += price_entry.price
                    break
        if not selected_ram: return None


        # 5. Storage (SSD)
        ssds = self.db.query(Product).filter(Product.category == "Storage", Product.specs["type"].astext == "SSD").all()
        ssds.sort(key=lambda x: x.specs.get("capacity_gb", 0), reverse=True)
        selected_ssd = None
        target_ssd_gb = 500 if budget < 800 else 1000 # Aim for 500GB or 1TB
        for ssd in ssds:
            if ssd.specs.get("capacity_gb", 0) >= target_ssd_gb:
                price_entry = self.get_lowest_price_for_product(ssd.id)
                if price_entry and (total_cost + price_entry.price) <= budget * 0.98:
                    selected_ssd = ssd
                    recommended_parts["Storage"] = {"product": ssd, "price_entry": price_entry}
                    total_cost += price_entry.price
                    break
        if not selected_ssd: return None

        # 6. Power Supply (PSU) - simplified selection
        psus = self.db.query(Product).filter(Product.category == "PSU").all()
        psus.sort(key=lambda x: x.specs.get("wattage", 0), reverse=True) # Prioritize higher wattage
        selected_psu = None
        # A more robust calculation would sum up wattage of CPU/GPU + buffer
        required_wattage = 650 # Placeholder for MVP
        if selected_gpu and selected_cpu:
            # Very rough estimate
            cpu_watt = selected_cpu.specs.get("tdp", 65) # TDP of CPU
            gpu_watt = selected_gpu.specs.get("tdp", 150) # TDP of GPU
            required_wattage = (cpu_watt + gpu_watt) * 1.5 # 50% buffer
            required_wattage = max(required_wattage, 450) # Minimum practical PSU

        for psu in psus:
            if psu.specs.get("wattage", 0) >= required_wattage:
                price_entry = self.get_lowest_price_for_product(psu.id)
                if price_entry and (total_cost + price_entry.price) <= budget:
                    selected_psu = psu
                    recommended_parts["PSU"] = {"product": psu, "price_entry": price_entry}
                    total_cost += price_entry.price
                    break
        if not selected_psu: return None

        # 7. Case - just pick one that fits, for MVP
        cases = self.db.query(Product).filter(Product.category == "Case").all()
        # For MVP, just pick the cheapest compatible one or one matching aesthetic tags
        selected_case = None
        for case in cases:
            # More complex compatibility: Motherboard form factor (ATX, Micro-ATX, Mini-ITX)
            # GPU length clearance, CPU cooler height clearance
            # For MVP, just try to find a general purpose one.
            price_entry = self.get_lowest_price_for_product(case.id)
            if price_entry and (total_cost + price_entry.price) <= budget:
                if aesthetic and aesthetic in case.aesthetic_tags: # Simple aesthetic matching
                     selected_case = case
                     recommended_parts["Case"] = {"product": case, "price_entry": price_entry}
                     total_cost += price_entry.price
                     break
        if not selected_case and cases: # If no aesthetic match, just pick first available
            price_entry = self.get_lowest_price_for_product(cases[0].id)
            if price_entry and (total_cost + price_entry.price) <= budget:
                selected_case = cases[0]
                recommended_parts["Case"] = {"product": selected_case, "price_entry": price_entry}
                total_cost += price_entry.price

        if user_prefs.get("monitor"):
            monitors = self.db.query(Product).filter(Product.category == "Monitor").all()
            # Filter by resolution, refresh rate here
            monitors.sort(key=lambda x: (x.specs.get("resolution_width", 0) * x.specs.get("resolution_height", 0) + x.specs.get("refresh_rate_hz", 0)), reverse=True)
            for monitor in monitors:
                price_entry = self.get_lowest_price_for_product(monitor.id)
                if price_entry and (total_cost + price_entry.price) <= budget:
                    recommended_parts["Monitor"] = {"product": monitor, "price_entry": price_entry}
                    total_cost += price_entry.price
                    break


        # Final Check: if total_cost is too high, return None or suggest cutting corners
        if total_cost > budget:
            return None # Or implement logic to reduce price by swapping parts

        return {
            "build": recommended_parts,
            "total_cost": total_cost,
            "user_preferences": user_prefs # Store original preferences for later reference
        }

    # You could add a method for `get_alternatives(product_id, budget_impact)` here
    # Which would find slightly cheaper/more expensive compatible parts.
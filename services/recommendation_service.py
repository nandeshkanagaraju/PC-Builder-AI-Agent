# services/recommendation_service.py

import logging
from sqlalchemy.orm import Session
from sqlalchemy import func # Import func for potential future use (e.g., aggregations)
from models import Product, PriceEntry # Ensure all necessary models are imported
import random # <--- ADDED: Required for random.uniform

# Configure logging for the recommendation service
# Using INFO level by default, you can change to DEBUG for more verbose output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RecommendationService:
    def __init__(self, db: Session):
        self.db = db
        logging.info("RecommendationService initialized.")

    def get_lowest_price_for_product(self, product_id: int):
        """
        Gets the latest lowest price for a specific product from available PriceEntry records.
        """
        latest_price_entry = self.db.query(PriceEntry) \
            .filter(PriceEntry.product_id == product_id) \
            .order_by(PriceEntry.timestamp.desc(), PriceEntry.price.asc()) \
            .first()
        if latest_price_entry:
            logging.debug(f"Found lowest price for product_id {product_id}: ${latest_price_entry.price} at {latest_price_entry.retailer_name}")
        else:
            logging.warning(f"No price entries found for product_id {product_id}.")
        return latest_price_entry # Returns PriceEntry object or None

    def get_compatible_parts(self, category: str, requirements: dict):
        """
        Filters products by category and basic compatibility requirements.
        Removes .astext for MySQL compatibility when querying JSON fields.
        """
        query = self.db.query(Product).filter(Product.category == category)
        logging.debug(f"Filtering {category} with requirements: {requirements}")

        # --- FIX: Removed .astext for MySQL JSON field comparisons ---
        if category == "CPU" and requirements.get("socket"):
            query = query.filter(Product.specs["socket"] == requirements["socket"])
        if category == "Motherboard" and requirements.get("socket"):
            query = query.filter(Product.specs["socket"] == requirements["socket"])
        if category == "RAM" and requirements.get("ram_type"):
            query = query.filter(Product.specs["ram_type"] == requirements["ram_type"])

        # Add more compatibility rules as needed, e.g., Motherboard form factor, Case compatibility with MB/GPU size
        # Example for motherboard form factor matching case:
        if category == "Case" and requirements.get("mb_form_factor"):
            # This would require your case specs to have a list of supported form factors
            # e.g., Product(..., specs={"supported_mb_form_factors": ["ATX", "Micro-ATX"]})
            # For simplicity, for MVP we might only filter by general size if a case supports ATX
            logging.debug(f"Attempting to filter cases by MB form factor {requirements['mb_form_factor']} - (not fully implemented in MVP for cases)")


        compatible_products = query.all()
        logging.debug(f"Found {len(compatible_products)} compatible {category} products.")
        return compatible_products

    def recommend_build(self, user_prefs: dict) -> dict | None:
        """
        Recommends a complete PC build based on user preferences and budget.
        Prioritizes gaming/productivity scores and ensures compatibility.
        """
        budget = user_prefs.get("budget")
        use_case = user_prefs.get("use_case", "general") # gaming, productivity, general
        aesthetic = user_prefs.get("aesthetic")
        include_monitor = user_prefs.get("monitor", False)
        monitor_resolution = user_prefs.get("monitor_resolution") # e.g., "1440p"
        monitor_refresh_rate = user_prefs.get("monitor_refresh_rate") # e.g., 144

        logging.info(f"Starting recommendation for budget=${budget}, use_case='{use_case}', aesthetic='{aesthetic}', monitor={include_monitor}")

        if not budget or budget <= 0:
            logging.warning("Budget not provided or invalid. Cannot recommend build.")
            return None

        recommended_parts = {}
        total_cost = 0

        # --- Component Selection Logic ---
        # This is a heuristic-based selection. For better results,
        # you'd need more sophisticated optimization.

        selected_cpu = None
        selected_mb = None
        selected_gpu = None
        selected_ram = None
        selected_storage = None
        selected_psu = None
        selected_case = None
        selected_monitor = None # For peripheral

        compat_reqs = {} # Will be updated with socket, RAM type etc.

        # 1. CPU Selection (Allocate ~15-30% of budget)
        cpu_budget_max = budget * random.uniform(0.15, 0.30)
        cpus = self.db.query(Product).filter(Product.category == "CPU").all()
        logging.debug(f"Considering {len(cpus)} CPUs for up to ${cpu_budget_max:.2f}")

        if use_case == "gaming":
            cpus.sort(key=lambda x: (x.gaming_score, x.productivity_score), reverse=True)
        elif use_case == "productivity":
            cpus.sort(key=lambda x: (x.productivity_score, x.gaming_score), reverse=True)
        else: # General
            cpus.sort(key=lambda x: (x.gaming_score + x.productivity_score), reverse=True)

        for cpu in cpus:
            price_entry = self.get_lowest_price_for_product(cpu.id)
            if price_entry and price_entry.price <= cpu_budget_max:
                selected_cpu = cpu
                recommended_parts["CPU"] = {"product": cpu, "price_entry": price_entry}
                total_cost += price_entry.price
                # --- MODIFIED: Store CPU socket and RAM type in compat_reqs ---
                compat_reqs["cpu_socket"] = selected_cpu.specs.get("socket")
                compat_reqs["cpu_ram_type"] = selected_cpu.specs.get("ram_type")
                logging.info(f"Selected CPU: {selected_cpu.name} for ${recommended_parts['CPU']['price_entry'].price:.2f}. Running total: ${total_cost:.2f}. CPU Socket: {compat_reqs['cpu_socket']}, CPU RAM Type: {compat_reqs['cpu_ram_type']}")
                break
        if not selected_cpu:
            logging.warning("Failed to select a CPU within budget allocation.")
            return None


        # 2. Motherboard Selection (Allocate ~10-20% of remaining budget)
        mb_budget_max = (budget - total_cost) * random.uniform(0.10, 0.20)
        # Use CPU socket for filtering motherboards
        motherboards = self.get_compatible_parts("Motherboard", {"socket": compat_reqs.get("cpu_socket")})
        motherboards.sort(key=lambda x: (x.gaming_score + x.productivity_score), reverse=True)
        logging.debug(f"Considering {len(motherboards)} Motherboards for up to ${mb_budget_max:.2f} (socket: {compat_reqs.get('cpu_socket')})")

        for mb in motherboards:
            price_entry = self.get_lowest_price_for_product(mb.id)
            if price_entry and price_entry.price <= mb_budget_max:
                selected_mb = mb
                recommended_parts["Motherboard"] = {"product": mb, "price_entry": price_entry}
                total_cost += price_entry.price
                # --- IMPORTANT FIX: Update compat_reqs with MOTHERBOARD'S RAM type ---
                compat_reqs["mb_form_factor"] = selected_mb.specs.get("form_factor")
                compat_reqs["ram_type"] = selected_mb.specs.get("ram_type") # This is what RAM needs to match!
                logging.info(f"Selected MB: {mb.name} for ${price_entry.price:.2f}. Running total: ${total_cost:.2f}. MB RAM Type: {compat_reqs['ram_type']}")
                break
        if not selected_mb:
            logging.warning("Failed to select a Motherboard compatible with CPU and within budget.")
            return None


        # 3. GPU Selection (Allocate ~25-45% of remaining budget, highest priority for gaming)
        gpu_budget_max = (budget - total_cost) * (0.45 if use_case == "gaming" else 0.25)
        gpus = self.db.query(Product).filter(Product.category == "GPU").all()
        logging.debug(f"Considering {len(gpus)} GPUs for up to ${gpu_budget_max:.2f}")

        if use_case == "gaming":
            gpus.sort(key=lambda x: x.gaming_score, reverse=True)
        else:
            gpus.sort(key=lambda x: (x.productivity_score + x.gaming_score), reverse=True)

        for gpu in gpus:
            price_entry = self.get_lowest_price_for_product(gpu.id)
            if price_entry and price_entry.price <= gpu_budget_max:
                selected_gpu = gpu
                recommended_parts["GPU"] = {"product": gpu, "price_entry": price_entry}
                total_cost += price_entry.price
                # Estimate needed PSU wattage
                cpu_tdp = selected_cpu.specs.get("tdp", 65)
                gpu_tdp = selected_gpu.specs.get("tdp", 150)
                compat_reqs["min_psu_wattage"] = (cpu_tdp + gpu_tdp) * 1.5 # 50% buffer
                logging.info(f"Selected GPU: {gpu.name} for ${price_entry.price:.2f}. Running total: ${total_cost:.2f}")
                break
        if not selected_gpu:
            logging.warning("Failed to select a GPU within budget allocation.")
            return None


        # 4. RAM Selection (Allocate ~5-10% of remaining budget)
        ram_budget_max = (budget - total_cost) * random.uniform(0.05, 0.10)
        # Pass the RAM type from the Motherboard
        rams = self.get_compatible_parts("RAM", {"ram_type": compat_reqs.get("ram_type")})
        # Prioritize higher capacity, then speed
        rams.sort(key=lambda x: (x.specs.get("capacity_gb", 0), x.specs.get("speed_mt_s", 0)), reverse=True)
        logging.debug(f"Considering {len(rams)} RAM kits for up to ${ram_budget_max:.2f} (RAM type: {compat_reqs.get('ram_type')})")

        target_ram_gb = 16 if budget < 800 and use_case != "productivity" else 32
        for ram in rams:
            if ram.specs.get("capacity_gb", 0) >= target_ram_gb:
                price_entry = self.get_lowest_price_for_product(ram.id)
                if price_entry and price_entry.price <= ram_budget_max:
                    selected_ram = ram
                    recommended_parts["RAM"] = {"product": ram, "price_entry": price_entry}
                    total_cost += price_entry.price
                    logging.info(f"Selected RAM: {ram.name} for ${price_entry.price:.2f}. Running total: ${total_cost:.2f}")
                    break
        if not selected_ram:
            logging.warning(f"Failed to select a compatible RAM kit ({target_ram_gb}GB target) of type {compat_reqs.get('ram_type')} within budget.")
            return None # Keep this 'return None' as RAM is critical


        # 5. Storage (SSD) Selection (Allocate ~5-10% of remaining budget)
        storage_budget_max = (budget - total_cost) * random.uniform(0.05, 0.10)
        ssds = self.db.query(Product).filter(Product.category == "Storage", Product.specs["type"] == "SSD").all()
        ssds.sort(key=lambda x: x.specs.get("capacity_gb", 0), reverse=True)
        logging.debug(f"Considering {len(ssds)} SSDs for up to ${storage_budget_max:.2f}")

        target_ssd_gb = 500 if budget < 800 else 1000 # Aim for 500GB or 1TB
        for ssd in ssds:
            if ssd.specs.get("capacity_gb", 0) >= target_ssd_gb:
                price_entry = self.get_lowest_price_for_product(ssd.id)
                if price_entry and price_entry.price <= storage_budget_max:
                    selected_storage = ssd
                    recommended_parts["Storage"] = {"product": ssd, "price_entry": price_entry}
                    total_cost += price_entry.price
                    logging.info(f"Selected Storage: {ssd.name} for ${price_entry.price:.2f}. Running total: ${total_cost:.2f}")
                    break
        if not selected_storage:
            logging.warning(f"Failed to select a suitable SSD ({target_ssd_gb}GB target) within budget.")
            return None


        # 6. Power Supply (PSU) Selection (Allocate ~5-8% of remaining budget)
        psu_budget_max = (budget - total_cost) * random.uniform(0.05, 0.08)
        min_psu_wattage = compat_reqs.get("min_psu_wattage", 650) # Default if GPU/CPU TDPs not precise
        psus = self.db.query(Product).filter(Product.category == "PSU").all()
        psus.sort(key=lambda x: x.specs.get("wattage", 0), reverse=True) # Prioritize higher wattage
        logging.debug(f"Considering {len(psus)} PSUs for up to ${psu_budget_max:.2f}, min wattage: {min_psu_wattage}")

        for psu in psus:
            if psu.specs.get("wattage", 0) >= min_psu_wattage:
                price_entry = self.get_lowest_price_for_product(psu.id)
                if price_entry and price_entry.price <= psu_budget_max:
                    selected_psu = psu
                    recommended_parts["PSU"] = {"product": psu, "price_entry": price_entry}
                    total_cost += price_entry.price
                    logging.info(f"Selected PSU: {psu.name} for ${price_entry.price:.2f}. Running total: ${total_cost:.2f}")
                    break
        if not selected_psu:
            logging.warning(f"Failed to select a suitable PSU ({min_psu_wattage}W target) within budget.")
            return None


        # 7. Case Selection (Allocate ~3-7% of remaining budget)
        case_budget_max = (budget - total_cost) * random.uniform(0.03, 0.07)
        cases = self.db.query(Product).filter(Product.category == "Case").all()
        logging.debug(f"Considering {len(cases)} Cases for up to ${case_budget_max:.2f}")

        # Basic case selection: try to match aesthetic, then form factor, then just cheapest
        filtered_cases = []
        for case in cases:
            # Simple form factor match (MB ATX will filter out Mini-ITX cases for now)
            if compat_reqs.get("mb_form_factor") == "ATX" and "Mini ITX" in case.specs.get("form_factor", ""):
                 continue
            filtered_cases.append(case)

        # Prioritize aesthetic, then price
        if aesthetic:
            filtered_cases.sort(key=lambda x: (aesthetic in x.aesthetic_tags, self.get_lowest_price_for_product(x.id).price if self.get_lowest_price_for_product(x.id) else float('inf')), reverse=True)
        else:
            filtered_cases.sort(key=lambda x: self.get_lowest_price_for_product(x.id).price if self.get_lowest_price_for_product(x.id) else float('inf'))

        selected_case = None # Reset selected_case for this logic block
        for case in filtered_cases:
            price_entry = self.get_lowest_price_for_product(case.id)
            if price_entry and price_entry.price <= case_budget_max:
                selected_case = case
                recommended_parts["Case"] = {"product": case, "price_entry": price_entry}
                total_cost += price_entry.price
                logging.info(f"Selected Case: {case.name} for ${price_entry.price:.2f}. Running total: ${total_cost:.2f}")
                break
        if not selected_case:
            logging.warning("Failed to select a Case within budget and basic compatibility.")
            # For MVP, if a case isn't found, we might still try to build without one or just return None
            # For now, let's allow it to proceed if other parts are critical and budget is tight
            pass # Allow to continue for now, but a real build needs a case


        # 8. Peripherals (Monitor, Keyboard, Mouse) - if requested and budget allows
        if include_monitor:
            monitor_budget_max = (budget - total_cost) * random.uniform(0.05, 0.15)
            monitors = self.db.query(Product).filter(Product.category == "Monitor").all()
            logging.debug(f"Considering {len(monitors)} Monitors for up to ${monitor_budget_max:.2f}")

            # Filter/sort monitors based on requested resolution/refresh rate
            if monitor_resolution == "1440p":
                monitors = [m for m in monitors if m.specs.get("resolution_width") == 2560 and m.specs.get("resolution_height") == 1440]
            elif monitor_resolution == "1080p":
                monitors = [m for m in monitors if m.specs.get("resolution_width") == 1920 and m.specs.get("resolution_height") == 1080]
            elif monitor_resolution == "4K":
                monitors = [m for m in monitors if m.specs.get("resolution_width") == 3840 and m.specs.get("resolution_height") == 2160]

            if monitor_refresh_rate:
                 monitors = [m for m in monitors if m.specs.get("refresh_rate_hz", 0) >= monitor_refresh_rate]

            monitors.sort(key=lambda x: (x.specs.get("refresh_rate_hz", 0), x.specs.get("resolution_width", 0)), reverse=True)

            for monitor in monitors:
                price_entry = self.get_lowest_price_for_product(monitor.id)
                if price_entry and price_entry.price <= monitor_budget_max:
                    selected_monitor = monitor
                    recommended_parts["Monitor"] = {"product": monitor, "price_entry": price_entry}
                    total_cost += price_entry.price
                    logging.info(f"Selected Monitor: {monitor.name} for ${price_entry.price:.2f}. Running total: ${total_cost:.2f}")
                    break
            if not selected_monitor:
                logging.warning("Failed to select a Monitor within budget.")


        # Final Check: if total_cost is too high, return None or suggest cutting corners
        if total_cost > budget:
            logging.warning(f"Final build cost (${total_cost:.2f}) exceeds budget (${budget:.2f}). Returning None.")
            return None # Or implement logic to reduce price by swapping parts

        # Ensure a minimal build is complete (CPU, MB, GPU, RAM, Storage, PSU)
        required_categories = {"CPU", "Motherboard", "GPU", "RAM", "Storage", "PSU"}
        if not required_categories.issubset(recommended_parts.keys()):
            logging.warning(f"Required core components not all selected. Missing: {required_categories - recommended_parts.keys()}. Returning None.")
            return None


        logging.info(f"Successfully recommended build with total cost: ${total_cost:.2f}")
        return {
            "build": recommended_parts,
            "total_cost": total_cost,
            "user_preferences": user_prefs # Store original preferences for later reference
        }

    # You could add a method for `get_alternatives(product_id, budget_impact)` here
    # Which would find slightly cheaper/more expensive compatible parts.
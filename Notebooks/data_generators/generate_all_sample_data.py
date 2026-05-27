"""
generate_all_sample_data.py  —  INDIA-CENTRIC EDITION
=====================================================
Sample-data generator for the IntelliBI Sales Lakehouse project.

All entities are India-focused:
  * Regions    = India geographic zones (North / South / East / West / Central / NE) + 1 export zone
  * Cities/    = Major Indian cities with correct states
  * Phones     = +91-XXXXX-XXXXX format
  * Names      = Indian first / last names
  * Currency   = INR (price ranges adjusted accordingly)
  * Brands     = Mix of Indian D2C and global brands sold in India
  * PIN codes  = 6-digit Indian PINs (zip_code column)

Outputs (Small scale ~50K rows):
    - region       :       7 rows
    - product      :    ~500 rows
    - store        :    ~200 rows
    - discount     :     ~40 rows
    - customer     :  ~2,000 rows  (+ 100 SCD2 deltas)
    - sales        : ~50,000 rows
    - invoice      : ~12,000 rows

Run:
    python generate_all_sample_data.py --out ../../sample_data
"""

import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 42
random.seed(SEED)


# ============================================================
#  REGION  (India zones, 7 rows)
# ============================================================
REGIONS = [
    # region_id, region_code, region_name,           country,  sub_region,    manager
    (1, "IN-N",  "INDIA NORTH",       "INDIA", "NORTH",     "Rajesh Kumar"),
    (2, "IN-S",  "INDIA SOUTH",       "INDIA", "SOUTH",     "Priya Iyer"),
    (3, "IN-E",  "INDIA EAST",        "INDIA", "EAST",      "Arijit Banerjee"),
    (4, "IN-W",  "INDIA WEST",        "INDIA", "WEST",      "Neha Shah"),
    (5, "IN-C",  "INDIA CENTRAL",     "INDIA", "CENTRAL",   "Vikram Yadav"),
    (6, "IN-NE", "INDIA NORTH EAST",  "INDIA", "NORTH EAST","Anjali Borah"),
    (7, "IN-EX", "INDIA EXPORTS",     "INDIA", "EXPORTS",   "Karan Mehta"),
]


def write_region(out_dir: Path):
    out = out_dir / "region"
    out.mkdir(parents=True, exist_ok=True)
    path = out / "region_master.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "region_id", "region_code", "region_name",
            "country",   "sub_region",  "regional_manager",
            "created_date",
        ])
        for r in REGIONS:
            w.writerow([*r, "2023-01-01"])
    print(f"  region   -> {path.name:30s} {len(REGIONS):>6} rows")


# ============================================================
#  PRODUCT  (~500 rows)  —  pricing in INR
# ============================================================
CATEGORIES = {
    "ELECTRONICS":      ["LAPTOPS", "MOBILES", "ACCESSORIES", "AUDIO", "WEARABLES"],
    "APPAREL":          ["MENS ETHNIC", "WOMENS ETHNIC", "MENS WESTERN",
                         "WOMENS WESTERN", "KIDS", "FOOTWEAR"],
    "HOME & KITCHEN":   ["FURNITURE", "APPLIANCES", "COOKWARE", "DECOR"],
    "GROCERIES":        ["BEVERAGES", "SNACKS", "ATTA & DAL", "DAIRY", "MASALA"],
    "SPORTS":           ["FITNESS", "OUTDOOR", "CRICKET", "BADMINTON"],
    "BEAUTY":           ["SKINCARE", "MAKEUP", "FRAGRANCE", "AYURVEDA"],
    "BOOKS":            ["FICTION", "NON-FICTION", "EDUCATION", "REGIONAL"],
    "TOYS":             ["AGES 0-3", "AGES 4-8", "AGES 9+"],
}
BRANDS = [
    # Indian / India-grown
    "TATA", "RELIANCE", "BOAT", "MAMAEARTH", "FABINDIA", "BIBA",
    "HALDIRAM", "PARLE", "ASIAN PAINTS", "BAJAJ", "GODREJ",
    # Global sold in India
    "SAMSUNG", "XIAOMI", "ADIDAS", "PUMA", "HP", "DELL",
]
SUPPLIERS = [
    "RELIANCE RETAIL", "FLIPKART WHOLESALE", "METRO CASH & CARRY",
    "BIG BASKET SUPPLY", "TATA DIGITAL", "DMART WHOLESALE",
    "UDAAN DISTRIBUTORS", "AMAZON BUSINESS INDIA",
]


def write_product(out_dir: Path, n: int = 500):
    out = out_dir / "product"
    out.mkdir(parents=True, exist_ok=True)
    path = out / "product_catalog.csv"
    rows = []
    pid = 10001
    for _ in range(n):
        cat = random.choice(list(CATEGORIES.keys()))
        sub = random.choice(CATEGORIES[cat])
        brand = random.choice(BRANDS)
        # Pricing band in INR (₹ rough scale)
        price_band = random.choice(["low", "mid", "high"])
        if price_band == "low":
            unit_cost = round(random.uniform(50, 800), 2)
        elif price_band == "mid":
            unit_cost = round(random.uniform(800, 8_000), 2)
        else:
            unit_cost = round(random.uniform(8_000, 80_000), 2)
        list_price = round(unit_cost * random.uniform(1.25, 2.4), 2)
        launch = date(2020, 1, 1) + timedelta(days=random.randint(0, 365 * 5))
        rows.append([
            pid,
            f"SKU-IN-{pid}",
            f"{brand} {sub.title()} Model {random.randint(100, 999)}",
            cat, sub, brand,
            random.choice(SUPPLIERS),
            unit_cost, list_price,
            launch.isoformat(),
            random.choice(["ACTIVE", "ACTIVE", "ACTIVE", "DISCONTINUED"]),
        ])
        pid += 1
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "product_id", "sku", "product_name", "category", "sub_category",
            "brand", "supplier", "unit_cost", "list_price", "launch_date", "status",
        ])
        w.writerows(rows)
    print(f"  product  -> {path.name:30s} {len(rows):>6} rows")
    return [r[0] for r in rows]


# ============================================================
#  STORE  (~200 rows)  —  Indian cities mapped to correct zones
# ============================================================
#  (city, state, region_id)   — region_id matches REGIONS above
INDIAN_CITIES = [
    # North (region_id = 1)
    ("DELHI",       "DELHI",        1),
    ("NEW DELHI",   "DELHI",        1),
    ("GURUGRAM",    "HARYANA",      1),
    ("NOIDA",       "UTTAR PRADESH",1),
    ("LUCKNOW",     "UTTAR PRADESH",1),
    ("JAIPUR",      "RAJASTHAN",    1),
    ("CHANDIGARH",  "CHANDIGARH",   1),
    ("AMRITSAR",    "PUNJAB",       1),
    ("AGRA",        "UTTAR PRADESH",1),
    ("KANPUR",      "UTTAR PRADESH",1),

    # South (region_id = 2)
    ("BENGALURU",   "KARNATAKA",    2),
    ("CHENNAI",     "TAMIL NADU",   2),
    ("HYDERABAD",   "TELANGANA",    2),
    ("COIMBATORE",  "TAMIL NADU",   2),
    ("KOCHI",       "KERALA",       2),
    ("THIRUVANANTHAPURAM", "KERALA",2),
    ("MYSURU",      "KARNATAKA",    2),
    ("MADURAI",     "TAMIL NADU",   2),
    ("VISAKHAPATNAM","ANDHRA PRADESH",2),
    ("VIJAYAWADA",  "ANDHRA PRADESH",2),

    # East (region_id = 3)
    ("KOLKATA",     "WEST BENGAL",  3),
    ("BHUBANESWAR", "ODISHA",       3),
    ("PATNA",       "BIHAR",        3),
    ("RANCHI",      "JHARKHAND",    3),
    ("CUTTACK",     "ODISHA",       3),
    ("SILIGURI",    "WEST BENGAL",  3),

    # West (region_id = 4)
    ("MUMBAI",      "MAHARASHTRA",  4),
    ("PUNE",        "MAHARASHTRA",  4),
    ("AHMEDABAD",   "GUJARAT",      4),
    ("SURAT",       "GUJARAT",      4),
    ("VADODARA",    "GUJARAT",      4),
    ("NAGPUR",      "MAHARASHTRA",  4),
    ("NASHIK",      "MAHARASHTRA",  4),
    ("RAJKOT",      "GUJARAT",      4),
    ("PANAJI",      "GOA",          4),

    # Central (region_id = 5)
    ("BHOPAL",      "MADHYA PRADESH",5),
    ("INDORE",      "MADHYA PRADESH",5),
    ("RAIPUR",      "CHHATTISGARH", 5),
    ("JABALPUR",    "MADHYA PRADESH",5),

    # North East (region_id = 6)
    ("GUWAHATI",    "ASSAM",        6),
    ("SHILLONG",    "MEGHALAYA",    6),
    ("IMPHAL",      "MANIPUR",      6),
    ("AIZAWL",      "MIZORAM",      6),
    ("ITANAGAR",    "ARUNACHAL PRADESH",6),

    # Exports / metro mix (region_id = 7) — international fulfilment hubs in India
    ("MUMBAI PORT", "MAHARASHTRA",  7),
    ("CHENNAI PORT","TAMIL NADU",   7),
    ("KOCHI PORT",  "KERALA",       7),
]
STORE_TYPES = ["FLAGSHIP", "STANDARD", "OUTLET", "EXPRESS", "POPUP"]
STREET_NAMES = ["MG Road", "Nehru Marg", "Gandhi Road", "Park Street",
                "Sector 17", "Brigade Road", "Linking Road", "Marine Drive",
                "Anna Salai", "FC Road"]


def write_store(out_dir: Path, n: int = 200):
    out = out_dir / "store"
    out.mkdir(parents=True, exist_ok=True)
    path = out / "store_master.csv"
    rows = []
    sid = 5001
    for _ in range(n):
        city, state, region_id = random.choice(INDIAN_CITIES)
        opening = date(2018, 1, 1) + timedelta(days=random.randint(0, 365 * 7))
        rows.append([
            sid,
            f"ST-{sid}",
            f"{city.title()} {random.choice(STORE_TYPES).title()} Store",
            random.choice(STORE_TYPES),
            f"{random.randint(1, 999)}, {random.choice(STREET_NAMES)}",
            city, state, region_id,
            f"Manager {random.randint(1000, 9999)}",
            opening.isoformat(),
            random.randint(800, 18_000),   # sq ft – Indian retail typical
            random.choice(["ACTIVE", "ACTIVE", "ACTIVE", "RENOVATION", "CLOSED"]),
        ])
        sid += 1
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "store_id", "store_code", "store_name", "store_type",
            "address", "city", "state", "region_id", "manager_name",
            "opening_date", "square_feet", "status",
        ])
        w.writerows(rows)
    print(f"  store    -> {path.name:30s} {len(rows):>6} rows")
    return [(r[0], r[5], r[7]) for r in rows]  # (store_id, city, region_id)


# ============================================================
#  DISCOUNT  (~40 rows)  —  INR thresholds, Indian segment names
# ============================================================
DISCOUNT_TYPES = ["PERCENT", "FLAT", "BUY_ONE_GET_ONE"]
SEGMENTS = ["REGULAR", "PRIME", "ELITE", "STUDENT", "SENIOR", "ALL"]
PROMO_PREFIXES = ["DIWALI", "HOLI", "EOSS", "REPUBLIC", "FREEDOM",
                  "RAKHI", "MEGA", "WEEKEND", "FLASH", "PRIME"]


def write_discount(out_dir: Path, n: int = 40):
    out = out_dir / "discount"
    out.mkdir(parents=True, exist_ok=True)
    path = out / "discount_master.csv"
    rows = []
    did = 9001
    used_codes = set()
    for i in range(n):
        dtype = random.choice(DISCOUNT_TYPES)
        if dtype == "PERCENT":
            value = random.choice([5, 10, 15, 20, 25, 30, 40, 50])
        elif dtype == "FLAT":
            # Flat amounts in INR
            value = random.choice([100, 250, 500, 1000, 2500, 5000])
        else:
            value = 1
        seg = random.choice(SEGMENTS)
        cat = random.choice(list(CATEGORIES.keys()) + ["ALL"])
        valid_from = date(2024, 1, 1) + timedelta(days=random.randint(0, 365))
        valid_to   = valid_from + timedelta(days=random.randint(30, 180))
        while True:
            code = f"{random.choice(PROMO_PREFIXES)}{random.randint(100, 999)}"
            if code not in used_codes:
                used_codes.add(code)
                break
        rows.append([
            did, code,
            f"{seg.title()} {dtype.title()} Offer {i+1}",
            dtype, value,
            random.choice([0, 500, 1000, 2500, 5000]),     # min purchase ₹
            random.choice([500, 1000, 2500, 5000, 10000]), # max disc ₹
            valid_from.isoformat(), valid_to.isoformat(),
            seg, cat,
            random.choice([1, 2, 3, 5]),
            random.randint(500, 10000),
            random.choice(["Y", "Y", "Y", "N"]),
            (valid_from - timedelta(days=15)).isoformat(),
        ])
        did += 1
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "discount_id", "discount_code", "discount_name", "discount_type",
            "discount_value", "min_purchase_amount", "max_discount_amount",
            "valid_from", "valid_to", "applicable_segment", "applicable_category",
            "usage_limit_per_customer", "total_usage_limit", "is_active",
            "created_date",
        ])
        w.writerows(rows)
    print(f"  discount -> {path.name:30s} {len(rows):>6} rows")
    return [r[1] for r in rows]


# ============================================================
#  CUSTOMER  (~2,000 rows)  —  Indian names, +91 phones, PIN codes
# ============================================================
FIRST_NAMES = [
    # Male
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh",
    "Krishna", "Ishaan", "Rohan", "Aryan", "Karan", "Kabir", "Rahul",
    "Vikram", "Manish", "Suresh", "Rajesh", "Amit", "Sandeep", "Anil",
    "Raj", "Vijay", "Pranav", "Siddharth", "Yash", "Dhruv", "Devansh",
    # Female
    "Aanya", "Aarohi", "Anaya", "Priya", "Pooja", "Sneha", "Nisha",
    "Riya", "Kavya", "Diya", "Saanvi", "Anika", "Meera", "Ananya",
    "Ishita", "Tara", "Sara", "Aisha", "Lakshmi", "Radha", "Sita",
    "Neha", "Anjali", "Shreya", "Divya", "Ritu",
]
LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Singh", "Kumar", "Patel", "Shah",
    "Mehta", "Joshi", "Iyer", "Reddy", "Nair", "Menon", "Rao", "Naidu",
    "Bose", "Banerjee", "Chatterjee", "Mukherjee", "Das", "Sen",
    "Kapoor", "Khanna", "Chopra", "Bhatia", "Malhotra", "Aggarwal",
    "Jain", "Goyal", "Mishra", "Tiwari", "Pandey", "Saxena", "Yadav",
    "Pillai", "Krishnan", "Subramanian", "Venkatesh", "Borah", "Hazarika",
]


def write_customer(out_dir: Path, n: int = 2000):
    """Initial customer load — India-centric."""
    out = out_dir / "customer"
    out.mkdir(parents=True, exist_ok=True)
    path = out / "customer_initial.csv"
    rows = []
    for cid in range(1001, 1001 + n):
        fn = random.choice(FIRST_NAMES); ln = random.choice(LAST_NAMES)
        city, state, region_id = random.choice(INDIAN_CITIES)
        rows.append([
            cid,
            f"{fn} {ln}",
            f"{fn.lower()}.{ln.lower()}{cid}@example.in",
            # +91 mobile number (Indian format, 10 digits starting 6-9)
            f"+91-{random.choice(['6','7','8','9'])}{random.randint(100,999)}-{random.randint(100000,999999)}",
            f"{random.randint(1, 999)}, {random.choice(STREET_NAMES)}",
            city, state,
            "INDIA",
            # 6-digit Indian PIN code
            f"{random.randint(110000, 855000):06d}",
            random.choice(["REGULAR","REGULAR","PRIME","ELITE","STUDENT"]),
        ])
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "customer_id","customer_name","email","phone","address",
            "city","state","country","zip_code","segment",
        ])
        w.writerows(rows)
    print(f"  customer -> {path.name:30s} {len(rows):>6} rows")

    # SCD2 deltas
    delta_path = out / "customer_updates.csv"
    n_changes = int(n * 0.05)
    changed_ids = random.sample([r[0] for r in rows], n_changes)
    delta_rows = []
    for cid in changed_ids:
        original = next(r for r in rows if r[0] == cid)
        new_row = list(original)
        change_type = random.choice(["segment", "address", "email"])
        if change_type == "segment":
            new_row[9] = random.choice(["PRIME", "ELITE"])
        elif change_type == "address":
            new_row[4] = f"{random.randint(1, 999)}, {random.choice(STREET_NAMES)} (New)"
        else:
            new_row[2] = f"updated.{new_row[2]}"
        delta_rows.append(new_row)
    with open(delta_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "customer_id","customer_name","email","phone","address",
            "city","state","country","zip_code","segment",
        ])
        w.writerows(delta_rows)
    print(f"  customer -> {delta_path.name:30s} {len(delta_rows):>6} rows (SCD2 deltas)")
    return [r[0] for r in rows]


# ============================================================
#  SALES  (~50,000 rows)  —  INR pricing
# ============================================================
PAYMENT_METHODS = ["UPI", "CREDIT_CARD", "DEBIT_CARD", "CASH",
                   "NET_BANKING", "WALLET", "EMI", "COD"]
CHANNELS        = ["IN_STORE", "ONLINE", "MOBILE_APP", "PHONE", "B2B"]


def write_sales(out_dir: Path,
                product_ids,
                store_info,
                customer_ids,
                discount_codes,
                n: int = 50_000):
    out = out_dir / "sales"
    out.mkdir(parents=True, exist_ok=True)
    path = out / "daily_sales_enhanced.csv"
    rows = []
    sale_id = 100001
    start = date(2024, 1, 1)
    days_span = (date(2026, 5, 1) - start).days
    for _ in range(n):
        pid = random.choice(product_ids)
        sid, city, region_id = random.choice(store_info)
        cid = random.choice(customer_ids)
        qty = random.choices([1,2,3,4,5,10], weights=[40,25,15,10,5,5])[0]
        # INR pricing distribution
        band = random.choices(["low","mid","high"], weights=[55,35,10])[0]
        if band == "low":
            unit_price = round(random.uniform(100, 1_500), 2)
        elif band == "mid":
            unit_price = round(random.uniform(1_500, 25_000), 2)
        else:
            unit_price = round(random.uniform(25_000, 150_000), 2)
        gross = round(qty * unit_price, 2)
        if random.random() < 0.3:
            dcode = random.choice(discount_codes)
            disc_amt = round(gross * random.uniform(0.05, 0.25), 2)
        else:
            dcode = ""
            disc_amt = 0.0
        net = round(gross - disc_amt, 2)
        cost = round(unit_price * random.uniform(0.5, 0.8) * qty, 2)
        sale_date = start + timedelta(days=random.randint(0, days_span))
        rows.append([
            sale_id, pid, sid, cid, region_id,
            qty, unit_price, gross, dcode, disc_amt, net, cost,
            sale_date.isoformat(),
            random.choice(PAYMENT_METHODS),
            random.choice(CHANNELS),
        ])
        sale_id += 1
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "sale_id","product_id","store_id","customer_id","region_id",
            "quantity","unit_price","gross_amount","discount_code","discount_amount",
            "net_amount","cost_amount","sale_date","payment_method","channel",
        ])
        w.writerows(rows)
    print(f"  sales    -> {path.name:30s} {len(rows):>6} rows")
    return rows


# ============================================================
#  INVOICE  (~12,000 rows)  —  INR currency, Indian GST tax rate
# ============================================================
PAYMENT_STATUSES = ["PAID", "PENDING", "OVERDUE", "CANCELLED", "REFUNDED"]
INV_PAYMENT_METHODS = ["UPI", "NEFT", "RTGS", "IMPS", "CHEQUE",
                       "CREDIT_CARD", "CASH", "DEMAND_DRAFT"]


def write_invoice(out_dir: Path,
                  customer_ids, store_info, discount_codes,
                  n: int = 12_000):
    out = out_dir / "invoice"
    out.mkdir(parents=True, exist_ok=True)
    path = out / "invoice_aws_export.csv"
    rows = []
    start = date(2024, 1, 1)
    days_span = (date(2026, 5, 1) - start).days
    for i in range(n):
        cid = random.choice(customer_ids)
        sid, city, region_id = random.choice(store_info)
        invoice_date = start + timedelta(days=random.randint(0, days_span))
        due_date     = invoice_date + timedelta(days=random.choice([15, 30, 45, 60]))
        # INR-scaled invoice subtotals
        subtotal = round(random.uniform(500, 250_000), 2)
        if random.random() < 0.25:
            dcode = random.choice(discount_codes)
            disc_amt = round(subtotal * random.uniform(0.05, 0.25), 2)
        else:
            dcode = ""
            disc_amt = 0.0
        # India GST blended rate ~ 18 %
        tax_amt = round((subtotal - disc_amt) * 0.18, 2)
        total = round(subtotal - disc_amt + tax_amt, 2)
        status = random.choices(PAYMENT_STATUSES,
                                weights=[70, 15, 8, 4, 3])[0]
        pay_date = (invoice_date + timedelta(days=random.randint(1, 45))).isoformat() \
                    if status in ("PAID", "REFUNDED") else ""
        region_name = next(r[2] for r in REGIONS if r[0] == region_id)
        rows.append([
            f"INV-{1000000+i}",
            f"NUM-{2000000+i}",
            cid, invoice_date.isoformat(), due_date.isoformat(),
            subtotal, dcode, disc_amt, tax_amt, total,
            status,
            random.choice(INV_PAYMENT_METHODS),
            pay_date,
            "INR",                    # currency
            region_name,
            sid,
            random.choice(CHANNELS),
            "etl_user",
        ])
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "invoice_id","invoice_number","customer_id","invoice_date","due_date",
            "subtotal_amount","discount_code","discount_amount","tax_amount",
            "total_amount","payment_status","payment_method","payment_date",
            "currency","region","store_id","channel","created_by",
        ])
        w.writerows(rows)
    print(f"  invoice  -> {path.name:30s} {len(rows):>6} rows")


# ============================================================
#  MAIN
# ============================================================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="../../sample_data")
    parser.add_argument("--customers", type=int, default=2000)
    parser.add_argument("--products",  type=int, default=500)
    parser.add_argument("--stores",    type=int, default=200)
    parser.add_argument("--discounts", type=int, default=40)
    parser.add_argument("--sales",     type=int, default=50_000)
    parser.add_argument("--invoices",  type=int, default=12_000)
    args = parser.parse_args()

    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nGenerating INDIA-CENTRIC sample data in: {out_dir}\n")

    write_region(out_dir)
    product_ids    = write_product(out_dir, args.products)
    store_info     = write_store(out_dir,  args.stores)
    discount_codes = write_discount(out_dir, args.discounts)
    customer_ids   = write_customer(out_dir, args.customers)
    write_sales  (out_dir, product_ids, store_info, customer_ids,
                  discount_codes, args.sales)
    write_invoice(out_dir, customer_ids, store_info, discount_codes,
                  args.invoices)
    print("\nDone.\n")


if __name__ == "__main__":
    main()
total - disc_amt) * random.uniform(0.05, 0.25), 2)
        else:
            dcode = ""
            disc_amt = 0.0
        # India GST blended rate ~ 18 %
        tax_amt = round((subtotal - disc_amt) * 0.18, 2)
        total = round(subtotal - disc_amt + tax_amt, 2)
        status = random.choices(PAYMENT_STATUSES,
                                weights=[70, 15, 8, 4, 3])[0]
        pay_date = (invoice_date + timedelta(days=random.randint(1, 45))).isoformat() \
                    if status in ("PAID", "REFUNDED") else ""
        region_name = next(r[2] for r in REGIONS if r[0] == region_id)
        rows.append([
            f"INV-{1000000+i}",
            f"NUM-{2000000+i}",
            cid, invoice_date.isoformat(), due_date.isoformat(),
            subtotal, dcode, disc_amt, tax_amt, total,
            status,
            random.choice(INV_PAYMENT_METHODS),
            pay_date,
            "INR",                    # currency
            region_name,
            sid,
            random.choice(CHANNELS),
            "etl_user",
        ])
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "invoice_id","invoice_number","customer_id","invoice_date","due_date",
            "subtotal_amount","discount_code","discount_amount","tax_amount",
            "total_amount","payment_status","payment_method","payment_date",
            "currency","region","store_id","channel","created_by",
        ])
        w.writerows(rows)
    print(f"  invoice  -> {path.name:30s} {len(rows):>6} rows")


# ============================================================
#  MAIN
# ============================================================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="../../sample_data")
    parser.add_argument("--customers", type=int, default=2000)
    parser.add_argument("--products",  type=int, default=500)
    parser.add_argument("--stores",    type=int, default=200)
    parser.add_argument("--discounts", type=int, default=40)
    parser.add_argument("--sales",     type=int, default=50_000)
    parser.add_argument("--invoices",  type=int, default=12_000)
    args = parser.parse_args()

    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nGenerating INDIA-CENTRIC sample data in: {out_dir}\n")

    write_region(out_dir)
    product_ids    = write_product(out_dir, args.products)
    store_info     = write_store(out_dir,  args.stores)
    discount_codes = write_discount(out_dir, args.discounts)
    customer_ids   = write_customer(out_dir, args.customers)
    write_sales  (out_dir, product_ids, store_info, customer_ids,
                  discount_codes, args.sales)
    write_invoice(out_dir, customer_ids, store_info, discount_codes,
                  args.invoices)
    print("\nDone.\n")


if __name__ == "__main__":
    main()

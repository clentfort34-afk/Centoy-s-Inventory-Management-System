import csv
import hashlib
import hmac
import secrets
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(_file_).resolve().parent

USERS_FILE = DATA_DIR / "users.txt"
PRODUCTS_FILE = DATA_DIR / "products.txt"
SUPPLIERS_FILE = DATA_DIR / "suppliers.txt"
MOVEMENTS_FILE = DATA_DIR / "stock_movements.txt"

FIELD_NAMES = {
    USERS_FILE: ["username", "role", "salt", "password_hash"],
    PRODUCTS_FILE: ["product_id", "name", "category", "supplier_id", "quantity", "reorder_level", "unit_cost"],
    SUPPLIERS_FILE: ["supplier_id", "name", "phone", "email"],
    MOVEMENTS_FILE: ["movement_id", "product_id", "change", "reason", "username", "timestamp"],
}

THEMES = {
    "1": {"name": "Classic Green", "header": "\033[96m"},
    "2": {"name": "Amber", "header": "\033[93m"},
}
RESET = "\033[0m"
theme = THEMES["1"]

current_user_is_admin = False

def read_rows(path):
    try:
        with path.open("r", encoding="utf-8", newline="") as file:
            return list(csv.DictReader(file, delimiter="|"))
    except FileNotFoundError:
        return []
    except Exception as error:
        print(f"Error reading {path.name}: {error}")
        return []

def write_rows(path, rows):
    try:
        with path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=FIELD_NAMES[path], delimiter="|")
            writer.writeheader()
            writer.writerows(rows)
        return True
    except Exception as error:
        print(f"Error writing {path.name}: {error}")
        return False

def append_row(path, row):
    try:
        file_exists = path.exists()
        with path.open("a", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=FIELD_NAMES[path], delimiter="|")
            if not file_exists or path.stat().st_size == 0:
                writer.writeheader()
            writer.writerow(row)
        return True
    except Exception as error:
        print(f"Error updating {path.name}: {error}")
        return False
def hash_password(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), 310000).hex()


def create_user(username, role, password):
    salt = secrets.token_bytes(16).hex()
    return {
        "username": username,
        "role": role,
        "salt": salt,
        "password_hash": hash_password(password, salt),
    }


def initialize_storage():
    for path in FIELD_NAMES:
        if not path.exists():
            write_rows(path, [])

    users = read_rows(USERS_FILE)
    if not users:
        users = [
            create_user("admin", "Administrator", "admin123"),
            create_user("staff", "Staff", "staff123"),
        ]
        write_rows(USERS_FILE, users)

    if not read_rows(PRODUCTS_FILE):
        default_products = [
            {"product_id": "P001", "name": "Keyboard", "category": "Accessories", "supplier_id": "S001", "quantity": "25", "reorder_level": "5", "unit_cost": "18.50"},
            {"product_id": "P002", "name": "Mouse", "category": "Accessories", "supplier_id": "S001", "quantity": "10", "reorder_level": "8", "unit_cost": "12.00"},
            {"product_id": "P003", "name": "Monitor", "category": "Displays", "supplier_id": "S002", "quantity": "6", "reorder_level": "2", "unit_cost": "145.99"},
        ]
        write_rows(PRODUCTS_FILE, default_products)

    if not read_rows(SUPPLIES_FILE):
        default_supplier = [
            {"supplier_id": "S001", "name": "Northstar Office Supply", "phone": "555-0101", "email": "orders@northstar.example"},
            {"supplier_id": "S002", "name": "Brightline Electronics", "phone": "555-0102", "email": "sales@brightline.example"},
        ]
        write_rows(SUPPLIERS_FILE, default_suppliers)

    if not read_rows(MOVEMENT_FILE):
        default_movements = [
            {"movement_id": "M001", "product_id": "P001", "change": "25", "reason": "Initial stock", "username": "admin", "timestamp": "2026-01-15T09:00:00"},
            {"movement_id": "M002", "product_id": "P002", "change": "10", "reason": "Initial stock", "username": "admin", "timestamp": "2026-01-15T09:10:00"},
            {"movement_id": "M003", "product_id": "P003", "change": "6", "reason": "Initial stock", "username": "admin", "timestamp": "2026-01-15T09:20:00"},
        ]
        write_rows(MOVEMENTS_FILE, default_movements)


def color_text(text, code):
    return f"{code}{text}{RESET}"


def header(title):
    width = 72
    print(color_text("=" * width, theme["header"]))
    print(color_text(title.center(width), theme["header"]))
    print(color_text("=" * width, theme["header"]))


def pause():
    input("\nPress Enter to continue...")


def get_next_id(rows, prefix):
    numbers = []
    for row in rows:
        value = row.get("product_id") if prefix == "P" else row.get("supplier_id") if prefix == "S" else row.get("movement_id")
        if value and value.startswith(prefix):
            try:
                numbers.append(int(value[1:]))
            except ValueError:
                pass
    return f"{prefix}{max(numbers, default=0) + 1:03d}"


def display_table(title, columns, rows):
    header(title)
    if not rows:
        print("\nNo records found.")
        return

    col_widths = []
    for col in columns:
        max_len = len(str(col))
        for row in rows:
            max_len = max(max_len, len(str(row.get(col, ""))))
        col_widths.append(min(max_len, 24))

    row_header = " | ".join(str(col).ljust(col_widths[i]) for i, col in enumerate(columns))
    print(row_header)
    print("-" * len(row_header))

    for row in rows:
        cells = []
        for i, col in enumerate(columns):
            text = str(row.get(col, ""))
            if len(text) > col_widths[i]:
                text = text[: col_widths[i] - 1] + "…"
            cells.append(text.ljust(col_widths[i]))
        print(" | ".join(cells))


def prompt_nonempty(label):
    while True:
        value = input(label).strip()
        if value:
            return value
        print("Please enter a value.")


def prompt_integer(label, minimum=0):
    while True:
        try:
            value = int(input(label).strip())
            if value >= minimum:
                return value
            print(f"Please enter a number greater than or equal to {minimum}.")
        except ValueError:
            print("Please enter a valid whole number.")


def prompt_float(label):
    while True:
        try:
            value = float(input(label).strip())
            if value >= 0:
                return value
            print("Please enter a positive value.")
        except ValueError:
            print("Please enter a valid number.")


def show_products(products=None):
    rows = read_rows(PRODUCTS_FILE) if products is None else products
    display_table(
        "PRODUCT INVENTORY",
        ["product_id", "name", "category", "supplier_id", "quantity", "reorder_level", "unit_cost"],
        rows,
    )


def show_suppliers(suppliers=None):
    rows = read_rows(SUPPLIERS_FILE) if suppliers is None else suppliers
    display_table("SUPPLIERS", ["supplier_id", "name", "phone", "email"], rows)


def add_product():
    if not current_user_is_admin:
        print("Only an Administrator can add products.")
        return

    suppliers = read_rows(SUPPLIERS_FILE)
    if not suppliers:
        print("Please add a supplier first.")
        return

    show_suppliers(suppliers)
    supplier_id = prompt_nonempty("\nEnter supplier ID: ").strip()
    valid_ids = {s["supplier_id"] for s in suppliers}
    if supplier_id not in valid_ids:
        print("Supplier not found.")
        return

    product = read_rows(PRODUCTS_FILE)
    product = {
        "product_id": get_next_id(products, "P"),
        "name": prompt_nonempty("Product name: "),
        "category": prompt_nonempty("Category: "),
        "supplier_id": supplier_id,
        "quantity": str(prompt_integer("Quantity: ", 0)),
        "reorder_level": str(prompt_integer("Reorder level: ", 0)),
        "unit_cost": f"{prompt_float('Unit cost: '):.2f}",
    }

    if append_row(PRODUCTS_FILE, product):
        print(f"Product {product['product_id']} added successfully.")

def add_supplier():
    if not current_user_is_admin:
        print("Only an Administrator can add suppliers.")
        return

    suppliers = read_rows(SUPPLIERS_FILE)
    supplier = {
        "supplier_id": get_next_id(suppliers, "S"),
        "name": prompt_nonempty("Supplier name: "),
        "phone": input("Phone number: ").strip(),
        "email": input("Email: ").strip(),
    }

    if append_row(SUPPLIERS_FILE, supplier):
        print(f"Supplier {supplier['supplier_id']} added successfully.")


def search_products():
    term = input("Search by product ID, name, or category: ").strip().lower()
    if not term:
        print("Search cannot be empty.")
        return

    matches = [
        p for p in read_rows(PRODUCTS_FILE)
        if term in p.get("product_id", "").lower()
        or term in p.get("name", "").lower()
        or term in p.get("category", "").lower()
    ]
    show_products(matches)

def search_suppliers():
    term = input("Search by supplier ID, name, phone, or email: ").strip().lower()
    if not term:
        print("Search cannot be empty.")
        return

    matches = [
        s for s in read_rows(SUPPLIERS_FILE)
        if term in s.get("supplier_id", "").lower()
        or term in s.get("name", "").lower()
        or term in s.get("phone", "").lower()
        or term in s.get("email", "").lower()
    ]
    show_suppliers(matches)


def adjust_stock(user):
    products = read_rows(PRODUCTS_FILE)
    if not products:
        print("No products available.")
        return

    show_products(products)
    product_id = input("\nEnter product ID to adjust: ").strip().upper()
    product = next((p for p in products if p["product_id"] == product_id), None)
    if not product:
        print("Product not found.")
        return

    try:
        change = int(input("Stock change (positive to add, negative to reduce): ").strip())
    except ValueError:
        print("Please enter a valid integer.")
        return

    new_quantity = int(product["quantity"]) + change
    if new_quantity < 0:
        print("Stock cannot go below zero.")
        return

    product["quantity"] = str(new_quantity)

    for i, p in enumerate(products):
        if p["product_id"] == product_id:
            products[i] = product
            break

    if not write_rows(PRODUCTS_FILE, products):
        return

    reason = prompt_nonempty("Reason for adjustment: ")
    movement_id = get_next_id(read_rows(MOVEMENTS_FILE), "M")
    movement = {
        "movement_id": movement_id,
        "product_id": product_id,
        "change": str(change),
        "reason": reason,
        "username": user["username"],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    append_row(MOVEMENT_FILE, movement)
    print(f"Stock updated. New quantity: {new_quantity}")

def reports():
    products = read_rows(PRODUCTS_FILE)
    movements = read_rows(MOVEMENTS_FILE)

    while True:
        header("REPORTS")
        print("1. Low-stock products")
        print("2. Inventory value summary")
        print("3. Recent stock movements")
        print("0. Return")
        choice = input("\nSelect report: ").strip()

        if choice == "1":
            low_stock = [p for p in products if int(p["quantity"]) <= int(p["reorder_level"])]
            show_products(low_stock)
            print(f"\nLow stock items: {len(low_stock)}")
            pause()

        elif choice == "2":
            total_units = sum(int(p["quantity"]) for p in products)
            total_value = sum(int(p["quantity"]) * float(p["unit_cost"]) for p in products)
            header("INVENTORY VALUE SUMMARY")
            print(f"Products: {len(products)}")
            print(f"Total units in stock: {total_units}")
            print(f"Total inventory value: ${total_value:,.2f}")
            pause()

        elif choice == "3":
            display_table(
                "RECENT STOCK MOVEMENTS",
                ["movement_id", "product_id", "change", "reason", "username", "timestamp"],
                movements[-10:][::-1],
            )
            pause()

        elif choice == "0":
            return

        else:
            print("Invalid selection.")

def settings(user):
    global theme

    while True:
        header("SYSTEM SETTINGS")
        print(f"Current theme: {theme['name']}")
        print("1. Classic Green")
        print("2. Amber")
        print("3. Change my password")
        print("0. Return to dashboard")
        choice = input("\nSelect an option: ").strip()

        if choice in THEMES:
            theme = THEMES[choice]
            print(f"Theme changed to {theme['name']}.")
        elif choice == "3":
            old_password = input("Current password: ")
            users = read_rows(USERS_FILE)
            account = next((u for u in users if u["username"] == user["username"]), None)

            if not account or not hmac.compare_digest(hash_password(old_password, account["salt"]), account["password_hash"]):
                print("Current password is incorrect.")
                continue

            new_password = input("New password (min 8 characters): ")
            if len(new_password) < 8:
                print("Password must be at least 8 characters.")
                continue

            new_salt = secrets.token_bytes(16).hex()
            account["salt"] = new_salt
            account["password_hash"] = hash_password(new_password, new_salt)

            if write_rows(USERS_FILE, users):
                print("Password updated.")

        elif choice == "0":
            return
        else:
            print("Invalid selection.")


def login():
    users = read_rows(USERS_FILE)
    header("INVENTORY MANAGEMENT SYSTEM")
    print("Use the default admin account or staff account.\n")

    username = input("Username: ").strip()
    if username.lower() == "q":
        return None

    password = input("Password: ")
    account = next((u for u in users if u["username"] == username), None)

    if account and hmac.compare_digest(hash_password(password, account["salt"]), account["password_hash"]):
        print(f"\nWelcome, {username}!")
        return account

    print("\nInvalid username or password.")
    return False


def dashboard(user):
    global current_user_is_admin
    current_user_is_admin = user["role"] == "Administrator"

    while True:
        header("INVENTORY MANAGEMENT SYSTEM")
        print(f"User: {user['username']} ({user['role']})")
        print(f"Date/time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Theme: {theme['name']}")
        print("-" * 72)
        print("1. View products")
        print("2. Search products")
        print("3. Adjust stock")
        print("4. View suppliers")
        print("5. Search suppliers")
        if current_user_is_admin:
            print("6. Add product")
            print("7. Add supplier")
        print("8. Reports")
        print("9. Settings")
        print("0. Log out")

        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            show_products()
            pause()
        elif choice == "2":
            search_products()
            pause()
        elif choice == "3":
            adjust_stock(user)
            pause()
        elif choice == "4":
            show_suppliers()
            pause()
        elif choice == "5":
            search_suppliers()
            pause()
        elif choice == "6" and current_user_is_admin:
            add_product()
            pause()
        elif choice == "7" and current_user_is_admin:
            add_supplier()
            pause()
        elif choice == "8":
            reports()
        elif choice == "9":
            settings(user)
        elif choice == "0":
            print("Logged out.")
            return
        else:
            print("Invalid selection or access denied.")

def main():
    initialize_storage()

    while True:
        user = login()
        if user is None:
            print("Goodbye.")
            break
        if user is not False:
            dashboard(user)


if __name__ == "__main__":
    main()

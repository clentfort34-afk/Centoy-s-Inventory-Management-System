import csv
import getpass
import hashlib
import hmac
import os
import secrets
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
USERS_FILE = DATA_DIR / "users.txt"
PRODUCTS_FILE = DATA_DIR / "products.txt"
SUPPLIERS_FILE = DATA_DIR / "suppliers.txt"
MOVEMENTS_FILE = DATA_DIR / "stock_movements.txt"

FIELDS = {
    USERS_FILE: ["username", "role", "salt", "password_hash"],
    PRODUCTS_FILE: [
        "product_id", "name", "category", "supplier_id",
        "quantity", "reorder_level", "unit_cost",
    ],
    SUPPLIERS_FILE: ["supplier_id", "name", "phone", "email"],
    MOVEMENTS_FILE: [
        "movement_id", "product_id", "change", "reason",
        "username", "timestamp",
    ],
}

THEMES = {
    "1": {"name": "Classic Green", "accent": "\033[92m", "heading": "\033[96m"},
    "2": {"name": "Amber", "accent": "\033[93m", "heading": "\033[95m"},
}
RESET = "\033[0m"
theme = THEMES["1"]


def read_rows(path):
    """Read pipe-delimited records from a text file."""
    try:
        with path.open("r", newline="", encoding="utf-8") as file:
            return list(csv.DictReader(file, delimiter="|"))
    except FileNotFoundError:
        return []
    except (OSError, csv.Error) as error:
        print(f"\nCould not read {path.name}: {error}")
        return []

def write_rows(path, rows):
    """Replace a text file with the supplied records."""
    try:
        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file, fieldnames=FIELDS[path], delimiter="|",
                extrasaction="ignore",
            )
            writer.writeheader()
            writer.writerows(rows)
        return True
    except OSError as error:
        print(f"\nCould not write {path.name}: {error}")
        return False


def append_row(path, row):
    """Append one record, writing a header if the file is empty."""
    try:
        needs_header = not path.exists() or path.stat().st_size == 0
        with path.open("a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file, fieldnames=FIELDS[path], delimiter="|",
                extrasaction="ignore",
            )
            if needs_header:
                writer.writeheader()
            writer.writerow(row)
        return True
    except OSError as error:
        print(f"\nCould not update {path.name}: {error}")
        return False

def password_hash(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), 310_000
    ).hex()


def create_user(username, role, password):
    salt = secrets.token_bytes(16).hex()
    return {
        "username": username,
        "role": role,
        "salt": salt,
        "password_hash": password_hash(password, salt),
    }


def initialize_storage():
    """Create missing files and provision example accounts on first run."""
    for path, fields in FIELDS.items():
        if not path.exists():
            write_rows(path, [])

    users = read_rows(USERS_FILE)
    if not users:
        users = [
            create_user("admin", "Administrator", "admin123"),
            create_user("staff", "Staff", "staff123"),
        ]
        write_rows(USERS_FILE, users)


def color(text, code):
    return f"{code}{text}{RESET}"


def header(title):
    width = 72
    print(color("=" * width, theme["heading"]))
    print(color(title.center(width), theme["heading"]))
    print(color("=" * width, theme["heading"]))

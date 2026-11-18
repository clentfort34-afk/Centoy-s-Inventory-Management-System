# Clent-F.-Angeline-M.
Final Project : Python System CSC 204-A

Centoys Invetory Management System

A terminal-based inventory application built with python 3. It stores data in pipe-delimited '.txt' files and 
support administrator and staff roles.

Features

- Login/logout with salted PBKDF2 password hashing
- Product and supplier records
- Stock adjustments with a movement history
- Search products and suppliers
- Low-stock, inventory-value, and stock-movement reports
- Classic Green and Amber terminal themes
- Password changes and input validation
- Persistent data stored in text files

Requirements 

- Python 3.8 or newer
- No third-party dependencies

Run

1. Place `inventory_system.py` and the data files in the same folder.
2. Run:  ```bash python inventory_system.py```
3. On the first run, use one of these starter accounts:

 | Role | Username | Password |
 | Administrator | `admin` | `admin123` |
 | Staff | `staff` | `staff123` |

4. Change the starter password using **Settings - Change my password**.
The application creates missing data files automatically. Keep the `.txt` files
in the same directory as the Python script so records persist across runs.

Screenshots 

Capture terminal screenshots while demonstrating :

1. The login promt
2. The dashboard after login
3. Viewing or adjusting product stock
4. The reports menu and a report
5. Theme Selection in System settings

import sqlite3

conn = sqlite3.connect("store.db")

cursor = conn.cursor()

# ---------------- USERS TABLE ---------------- #

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

# ---------------- PHONES TABLE ---------------- #

cursor.execute("""
CREATE TABLE IF NOT EXISTS phones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price INTEGER NOT NULL,
    image TEXT NOT NULL,
    description TEXT NOT NULL
)
""")

# ---------------- ORDERS TABLE ---------------- #

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    total INTEGER,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")

# ---------------- SAMPLE PHONES ---------------- #

cursor.execute("SELECT COUNT(*) FROM phones")
count = cursor.fetchone()[0]

if count == 0:

    phones = [

        (
            "iPhone 17",
            89999,
            "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9",
            "Apple's latest smartphone with powerful performance and advanced camera system."
        ),

        (
            "Samsung Galaxy S25",
            79999,
            "https://images.unsplash.com/photo-1598327105666-5b89351aff97",
            "Premium Samsung flagship with stunning display and battery life."
        ),

        (
            "OnePlus 14 Pro",
            59999,
            "https://www.dailyinsights.co.in/wp-content/uploads/2025/08/oneplus-14-pro.png",
            "Fast performance, smooth experience and flagship features."
        ),

        (
            "Google Pixel 10",
            74999,
            "https://images.unsplash.com/photo-1512499617640-c74ae3a79d37",
            "Excellent camera and clean Android experience."
        ),

        (
            "Xiaomi 15 Ultra",
            69999,
            "https://images.unsplash.com/photo-1580910051074-3eb694886505",
            "Flagship Xiaomi device with powerful hardware."
        )

    ]

    cursor.executemany("""
    INSERT INTO phones
    (name, price, image, description)
    VALUES (?, ?, ?, ?)
    """, phones)

conn.commit()
conn.close()

print("Database Created Successfully!")
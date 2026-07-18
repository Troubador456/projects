import sqlite3

def init_db():
    conn = sqlite3.connect('medical_system.db')
    cursor = conn.cursor()
    
    # Create Pharmacies Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pharmacies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            address TEXT,
            phone TEXT
        )
    ''')
    
    # Create Blood Pressure History Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blood_pressure (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT,
            systolic INTEGER,
            diastolic INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # EXTENSION: Create Adverse Drug Reactions Tracking Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS adverse_reactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drug_name TEXT,
            symptom TEXT,
            severity TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Seed Sample Data
    pharmacies_data = [
        ("CVS Pharmacy", "123 Main St, Austin, TX", "555-0199"),
        ("Walgreens", "456 Oak Ave, Austin, TX", "555-0244"),
        ("Corner Care Pharmacy", "789 Pine Rd, Leander, TX", "555-0311")
    ]
    
    bp_data = [
        ("PID123", 120, 80),
        ("PID123", 135, 88),
        ("PID456", 140, 95)
    ]
    
    cursor.executemany("INSERT OR IGNORE INTO pharmacies (name, address, phone) VALUES (?, ?, ?)", pharmacies_data)
    cursor.executemany("INSERT OR IGNORE INTO blood_pressure (patient_id, systolic, diastolic) VALUES (?, ?, ?)", bp_data)
    
    conn.commit()
    conn.close()
    print("Database built and seeded successfully!")

if __name__ == "__main__":
    init_db()


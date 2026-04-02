import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection parameters
DB_PARAMS = {
    "host": "localhost",
    "database": "cems",
    "user": "veerapandig",
    "password": "1234"
}

def seed_halls():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        
        # 1. Create 'halls' table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS halls (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                capacity INTEGER,
                description TEXT
            );
        """)
        
        # 2. Add the requested halls (Combining TP 404 & 405 as they are the same class)
        halls_to_seed = [
            ("SRM TP 404 & 405", 120, "Combined large classroom in TP building"),
            ("SRM GANESAN AUDITORIUM", 500, "Large auditorium for main events"),
            ("MEDICAL HALL", 200, "Hall near the medical block"),
            ("BELL LAB 502", 40, "Laboratory/Seminar Room")
        ]
        
        # Cleanup old separate entries if they exist
        cur.execute("DELETE FROM halls WHERE name IN ('SRM TP 404', 'SRM TP 405')")
        
        for name, cap, desc in halls_to_seed:
            cur.execute("""
                INSERT INTO halls (name, capacity, description) 
                VALUES (%s, %s, %s) 
                ON CONFLICT (name) DO UPDATE SET capacity = EXCLUDED.capacity, description = EXCLUDED.description;
            """, (name, cap, desc))
            
        # 3. Modify 'events' table structure if it already exists, or create new
        # We handle this in the backend too, but for cleanliness:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id SERIAL PRIMARY KEY,
                organizer_id INTEGER REFERENCES users(id),
                title VARCHAR(255) NOT NULL,
                description TEXT,
                hall_id INTEGER REFERENCES halls(id),
                team_size INTEGER NOT NULL DEFAULT 1,
                female_mandatory BOOLEAN NOT NULL DEFAULT FALSE,
                reg_amount NUMERIC(10,2) DEFAULT 0,
                poster_url TEXT,
                start_date TIMESTAMP NOT NULL,
                end_date TIMESTAMP NOT NULL,
                reg_deadline TIMESTAMP NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                admin_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        conn.commit()
        print("✅ Successfully initialized Halls table and seeded with data.")
        print("✅ Events table confirmed.")
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")

if __name__ == "__main__":
    seed_halls()

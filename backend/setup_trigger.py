from db import DatabaseConnection

def setup_trigger():
    trigger_sql = """
    -- Function to set club_id automatically
    CREATE OR REPLACE FUNCTION set_event_club_id()
    RETURNS TRIGGER AS $$
    BEGIN
        IF NEW.club_id IS NULL THEN
            SELECT club_id INTO NEW.club_id FROM users WHERE id = NEW.organizer_id;
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    -- Trigger for events table
    DROP TRIGGER IF EXISTS trg_set_event_club_id ON events;
    CREATE TRIGGER trg_set_event_club_id
    BEFORE INSERT ON events
    FOR EACH ROW
    EXECUTE FUNCTION set_event_club_id();
    """
    
    # Also add foreign key constraints if they are not explicitly enforced (though schema shows references)
    # The schema already has REFERENCES, but let's ensure they are there.
    
    try:
        with DatabaseConnection() as conn:
            with conn.cursor() as cur:
                cur.execute(trigger_sql)
                conn.commit()
                print("✅ Trigger created successfully!")
    except Exception as e:
        print(f"❌ Error creating trigger: {e}")

if __name__ == "__main__":
    setup_trigger()

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database connection parameters
DB_PARAMS = {
    "host": "localhost",
    "database": "cems",
    "user": "veerapandig",
    "password": "1234"
}

# Create a connection pool to manage concurrent connections efficiently
try:
    # minconn = 1, maxconn = 10
    connection_pool = psycopg2.pool.ThreadedConnectionPool(1, 10, **DB_PARAMS)
    if connection_pool:
        logger.info("Connection pool created successfully")
except Exception as e:
    logger.error(f"Error creating connection pool: {e}")
    connection_pool = None

def get_connection():
    """Acquire a connection from the pool."""
    if connection_pool is None:
        raise Exception("Connection pool is not initialized.")
    try:
        return connection_pool.getconn()
    except Exception as e:
        logger.error(f"Error getting connection from pool: {e}")
        raise

def release_connection(conn):
    """Release the connection back to the pool."""
    if connection_pool is not None and conn is not None:
        try:
            connection_pool.putconn(conn)
        except Exception as e:
            logger.error(f"Error releasing connection to pool: {e}")

class DatabaseConnection:
    """Context manager for easy and safe database access.
    
    Usage:
        with DatabaseConnection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM users")
                results = cur.fetchall()
    """
    def __enter__(self):
        self.conn = get_connection()
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Rollback if an error occurred
            self.conn.rollback()
        else:
            # Commit if successful
            self.conn.commit()
        release_connection(self.conn)

def execute_query(query, params=None, fetch=True):
    """Utility function to execute a query and fetch results as dictionaries."""
    with DatabaseConnection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            if fetch:
                try:
                    return cur.fetchall()
                except psycopg2.ProgrammingError:
                    # Catch cases where the query doesn't return anything (e.g., INSERT without RETURNING)
                    return []
            return []

if __name__ == "__main__":
    try:
        # Test the connection context manager
        with DatabaseConnection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                db_version = cur.fetchone()[0]
                print(f"✅ Successfully connected to the local PostgreSQL database ('cems')!")
                print(f"📌 PostgreSQL version: {db_version}")
    except Exception as e:
        print(f"❌ Failed to connect to the database. Error: {e}")

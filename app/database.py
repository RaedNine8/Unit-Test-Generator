import os
import psycopg2
from dotenv import load_dotenv
import logging

load_dotenv() # Load environment variables from .env file

logger = logging.getLogger(__name__)

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOSTNAME"),
            port=os.getenv("DB_PORT"),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            dbname=os.getenv("DB_NAME")
        )
        logger.info("Successfully connected to the PostgreSQL database.")
        return conn
    except psycopg2.OperationalError as e:
        logger.error(f"Could not connect to the PostgreSQL database: {e}")
        # Depending on the application's needs, you might want to raise the exception
        # or handle it in a different way.
        raise

def initialize_database():
    """Initializes the database by creating necessary tables if they don't exist."""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            # Example table creation. Adjust this to your needs.
            cur.execute("""
                CREATE TABLE IF NOT EXISTS test_runs (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    source_file VARCHAR(255),
                    tests_generated INTEGER,
                    tests_passed INTEGER
                );
            """)
            conn.commit()
            cur.close()
            conn.close()
            logger.info("Database initialized successfully.")
        except psycopg2.Error as e:
            logger.error(f"Error initializing database: {e}")

def log_test_run(source_file, tests_generated, tests_passed):
    """Log a test run to the database."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO test_runs (source_file, tests_generated, tests_passed)
            VALUES (%s, %s, %s)
            """,
            (source_file, tests_generated, tests_passed)
        )
        conn.commit()
        cur.close()
        conn.close()
        logger.info("Test run logged to database.")
    except Exception as e:
        logger.error(f"Error logging test run: {e}")

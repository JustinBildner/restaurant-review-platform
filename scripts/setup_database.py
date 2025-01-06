import psycopg
import sys
import os

# Add parent directory to path so we can import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

def create_tables():
    # Connection parameters
    conn_params = Config.get_db_config()
    
    # SQL commands to create tables
    create_tables_commands = [
        """
        CREATE TABLE IF NOT EXISTS restaurants (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE,
            address VARCHAR(255) NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS reviews (
            id SERIAL PRIMARY KEY,
            restaurant_id INTEGER REFERENCES restaurants(id),
            review_text TEXT NOT NULL,
            sentiment_score FLOAT NOT NULL
        )
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_restaurant_name 
        ON restaurants(name)
        """
    ]
    
    try:
        # Connect to database
        with psycopg.connect(**conn_params) as conn:
            with conn.cursor() as cur:
                # Execute each command
                for command in create_tables_commands:
                    cur.execute(command)
            # Commit the transaction
            conn.commit()
            print("Tables created successfully")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    create_tables()
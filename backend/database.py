import psycopg
from config import Config

class DatabaseManager:
    def __init__(self):
        self.conn_params = Config.get_db_config()
    
    def add_restaurant(self, name: str, address: str) -> int:
        # Add a new restaurant and return its ID
        query = """
        INSERT INTO restaurants (name, address)
        VALUES (%s, %s)
        RETURNING id;
        """
        with psycopg.connect(**self.conn_params) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (name, address))
                restaurant_id = cur.fetchone()[0]
            conn.commit()
        return restaurant_id
    
    def add_review(self, restaurant_name: str, review_text: str, sentiment_score: float) -> int:
        # Add a new review using restaurant name and return its ID
        query = """
        WITH rest AS (
            SELECT id FROM restaurants WHERE name = %s
        )
        INSERT INTO reviews (restaurant_id, review_text, sentiment_score)
        SELECT rest.id, %s, %s
        FROM rest
        RETURNING id;
        """
        with psycopg.connect(**self.conn_params) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (restaurant_name, review_text, sentiment_score))
                review_id = cur.fetchone()[0]
            conn.commit()
        return review_id

    def get_restaurant_by_name(self, name: str):
        # Get restaurant details by name
        query = """
        SELECT id, name, address
        FROM restaurants
        WHERE name ILIKE %s;
        """
        with psycopg.connect(**self.conn_params) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (f"%{name}%",))
                return cur.fetchall()
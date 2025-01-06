from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

    @staticmethod
    def get_db_config():
        return {
            "dbname": Config.DB_NAME,
            "user": Config.DB_USER,
            "password": Config.DB_PASSWORD,
            "host": Config.DB_HOST
        }
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

def create_database():
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "123456")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    target_db = os.getenv("POSTGRES_DB", "AI_task")

    print(f"\n[INFO] Attempting to create database '{target_db}' on PostgreSQL ({host}:{port})...")
    
    # Connect to the default 'postgres' database with AUTOCOMMIT
    postgres_url = f"postgresql://{user}:{password}@{host}:{port}/postgres"
    
    try:
        engine = create_engine(postgres_url, isolation_level="AUTOCOMMIT")
        with engine.connect() as conn:
            # Check if database already exists
            check_sql = text("SELECT 1 FROM pg_database WHERE datname = :dbname")
            result = conn.execute(check_sql, {"dbname": target_db}).scalar()
            
            if result:
                print(f"[EXISTS] Database '{target_db}' already exists!")
            else:
                conn.execute(text(f'CREATE DATABASE "{target_db}";'))
                print(f"[SUCCESS] Database '{target_db}' created successfully!")
            return True
    except Exception as e:
        print(f"[ERROR] Failed to create database '{target_db}': {e}")
        return False

if __name__ == "__main__":
    success = create_database()
    sys.exit(0 if success else 1)

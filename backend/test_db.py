import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

def test_postgresql():
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "123456")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    target_db = os.getenv("POSTGRES_DB", "AI_task")

    print("\n==========================================")
    print(" [INFO] Testing PostgreSQL Connection")
    print("==========================================")
    print(f" Host: {host}:{port}")
    print(f" User: {user}")
    print(f" Target Database: {target_db}")

    # 1. Attempt connection to target database
    target_url = f"postgresql://{user}:{password}@{host}:{port}/{target_db}"
    try:
        engine = create_engine(target_url, connect_args={"connect_timeout": 5})
        with engine.connect() as conn:
            version = conn.execute(text("SELECT version();")).scalar()
            db_name = conn.execute(text("SELECT current_database();")).scalar()
            print("\n[SUCCESS] PostgreSQL Server is running and target database exists!")
            print(f" Current Database : {db_name}")
            print(f" Server Version   : {version.split(',')[0]}")
            print("==========================================\n")
            return True
    except Exception as err_target:
        err_msg = str(err_target)
        print(f"\n[WARNING] Could not connect directly to '{target_db}'.")

        # 2. Check if server itself is running by connecting to default 'postgres' db
        fallback_url = f"postgresql://{user}:{password}@{host}:{port}/postgres"
        try:
            fallback_engine = create_engine(fallback_url, connect_args={"connect_timeout": 5})
            with fallback_engine.connect() as conn:
                version = conn.execute(text("SELECT version();")).scalar()
                print("\n[PARTIAL SUCCESS] PostgreSQL service IS running on your machine!")
                print(f" Server Version: {version.split(',')[0]}")
                print(f" Issue Found   : Database '{target_db}' does not exist yet.")
                print("\n[ACTION REQUIRED] Create the database by running in psql or pgAdmin:")
                print(f'   CREATE DATABASE "{target_db}";')
                print("==========================================\n")
                return False
        except Exception as err_server:
            print("\n[FAILED] Cannot connect to PostgreSQL server.")
            print(f" Error: {err_msg}")
            print("\n Troubleshooting Tips:")
            print(" 1. Ensure PostgreSQL is installed & running (PowerShell: Get-Service -Name *postgres*)")
            print(" 2. Verify password and credentials in backend/.env")
            print("==========================================\n")
            return False

if __name__ == "__main__":
    success = test_postgresql()
    sys.exit(0 if success else 1)

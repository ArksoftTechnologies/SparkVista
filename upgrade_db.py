from app import create_app, db
from sqlalchemy import text
import sys

# Add the current directory to sys.path to ensure imports work
import os
sys.path.append(os.getcwd())

app = create_app()

with app.app_context():
    print("Attempting to upgrade database...")
    with db.engine.connect() as conn:
        try:
            # Check if column exists (pragmatic way for sqlite)
            # Or just try to search for it, but easiest is just try add and catch error
            conn.execute(text("ALTER TABLE orders ADD COLUMN tracking_id VARCHAR(20)"))
            print("SUCCESS: Added tracking_id column.")
        except Exception as e:
            print(f"INFO: Column addition skipped (might already exist): {e}")
    print("Database upgrade check complete.")

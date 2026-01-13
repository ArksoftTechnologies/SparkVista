from app import create_app, db
from app.models.items import LaundryItem
import sys

app = create_app()

with app.app_context():
    print("Checking database connection...")
    try:
        # Check if table exists
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        if 'laundry_items' not in tables:
            print("ERROR: table 'laundry_items' does not exist!")
            sys.exit(1)
        else:
            print("Table 'laundry_items' exists.")

        # Try to import model
        print("Model imported successfully.")

        # Try to create an item
        print("Attempting to create a test item...")
        try:
            item = LaundryItem(
                name="Test Item Script",
                category="Clothing",
                price_wash=100.0,
                price_dryclean=200.0,
                price_iron=50.0
            )
            db.session.add(item)
            db.session.commit()
            print(f"Successfully created item: {item.to_dict()}")
            
            # Clean up
            db.session.delete(item)
            db.session.commit()
            print("Test item deleted.")
        except Exception as e:
            print(f"ERROR creating item: {e}")
            sys.exit(1)

    except Exception as e:
        print(f"General Error: {e}")
        sys.exit(1)

print("Backend verification passed.")

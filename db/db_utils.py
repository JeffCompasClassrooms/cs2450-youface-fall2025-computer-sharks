import json
import os

# Define the path to your database file
DB_FILE = os.path.join(os.path.dirname(__file__), 'db.json')

def load_db() -> dict:
    """
    Loads the entire database (db.json) file content into a Python dictionary.
    Initializes a basic structure if the file doesn't exist.
    """
    # 1. Check if the file exists
    if not os.path.exists(DB_FILE):
        print(f"Database file not found at {DB_FILE}. Initializing new structure.")
        # Return a basic structure for an empty app
        return {
            "users": [],
            "posts": [],
            "matches": []
        }
    
    # 2. Load the existing data
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {DB_FILE}. Returning empty structure.")
        return {
            "users": [],
            "posts": [],
            "matches": []
        }

def save_db(data: dict):
    """
    Saves the provided dictionary back to the database file (db.json).
    """
    try:
        with open(DB_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        print(f"Error writing to database file: {e}")

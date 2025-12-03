# db/matches.py

# db/matches.py

# Assume you have these helper functions defined elsewhere in your db directory
# that handle reading and writing to your db.json file.
def load_db():
    """Loads the database content from the file (e.g., db.json)."""
    # Placeholder: Implement file reading logic here
    # Example: return json.load(f)
    pass

def save_db(data):
    """Saves the updated database content back to the file (e.g., db.json)."""
    # Placeholder: Implement file writing logic here
    # Example: json.dump(data, f, indent=4)
    pass

# You may need to import the 'datetime' module for timestamps
from datetime import datetime

def save_match(liker: str, target: str, action: str):
    """
    Records a swipe action ('like' or 'dislike') from the liker to the target user.
    """
    db = load_db()
    
    # 1. Ensure the 'matches' list exists
    if 'matches' not in db:
        db['matches'] = []
        
    # 2. Check if this specific action has already been recorded
    # This prevents duplicate entries if a user tries to click the button multiple times
    for match in db['matches']:
        if match['liker'] == liker and \
           match['target'] == target and \
           match['action'] == action:
            print(f"Match/Swipe from {liker} to {target} with action {action} already exists.")
            return

    # 3. Create the new match record
    new_match_record = {
        "liker": liker,
        "target": target,
        "action": action, # 'like' or 'dislike'
        "timestamp": datetime.now().isoformat()
    }
    
    # 4. Add the record to the database and save the file
    db['matches'].append(new_match_record)
    save_db(db)
    print(f"Recorded {liker}'s {action} on {target}.")

# --- You would also need your other functions like check_mutual_like and get_swiped_users here ---
# (As provided in the previous answer)

def check_mutual_like(target_username, current_username):
    """
    Checks if the target_username has previously 'liked' the current_username.
    Returns True if a mutual like exists, False otherwise.
    """
    # **NOTE: This is conceptual database logic. Adjust based on your db.json or SQL structure.**
    
    # Example for JSON/File-based DB:
    db = load_db() 
    
    # Look for a record where the target is the liker and the current user is the target
    # and the action was 'like'.
    for match in db.get('matches', []):
        if match['liker'] == target_username and \
           match['target'] == current_username and \
           match['action'] == 'like':
            return True
    return False

# db/matches.py

# ... (Previous functions like load_db, save_db, save_match, check_mutual_like)

def get_matches_for_user(username: str) -> list:
    """
    Retrieves a list of usernames that have a mutual 'like' with the given user.
    """
    db = load_db()
    
    # 1. Find all users that the current user (username) has liked.
    liked_by_user = {match['target'] for match in db.get('matches', []) 
                     if match['liker'] == username and match['action'] == 'like'}

    mutual_matches = []
    
    # 2. Check if those liked targets have also liked the current user.
    for target in liked_by_user:
        # Reusing the check_mutual_like logic (or implementing it inline)
        if check_mutual_like(target, username):
            mutual_matches.append(target)
            
    return mutual_matches
def get_swiped_users(username):
    """Retrieves a set of users the given username has already swiped on (liked or disliked)."""
    # Again, conceptual logic:
    db = load_db()
    swiped = set()
    for match in db.get('matches', []):
        if match['liker'] == username:
            swiped.add(match['target'])
    return swiped

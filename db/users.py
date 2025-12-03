import tinydb
from werkzeug.security import generate_password_hash, check_password_hash
from .db_utils import load_db

def new_user(db, username, password, email= None, shoe_size=None, is_clown=False, has_clown_horns=False):
    users = db.table('users')
    User = tinydb.Query()
    if users.get(User.username == username):
        return None
    
    hashedPassword = generate_password_hash(password)

    user_record = {
            'username': username,
            'password': hashedPassword,
            'email' : email,
            'friends': [],
            'profile': {
            'shoe_size': shoe_size,
            'is_clown':is_clown,
            'has_clown_horns': has_clown_horns,
            'bio': '',
            'photos': []
            }
            }
    return users.insert(user_record)
def get_all_users():
    db = load_db() 
    
    # 2. FIX: Access the list of users using dictionary key access (db['users'])
    #         instead of the TinyDB method (db.table('users'))
    if 'users' in db:
        all_users = db['users']
    else:
        # Handle case where the 'users' key might be missing
        all_users = [] 

    # 3. If you want to return a list of users, return the list directly
    return all_users
def get_user(db, username, password):
    db = load_db()

    # 1. FIX: Access the list of users directly from the dictionary
    users_list = db.get('users', [])

    # 2. FIX: Find the user dictionary using a simple loop (or list comprehension)
    user = None
    for u in users_list:
        if u.get('username') == username:
            user = u
            break

    # 3. Check if user was found
    if not user:
        return None

    # 4. Check password hash
    # Ensure the key is 'password' and not 'password_hash' depending on your model
    # We use .get() here in case the 'password' field is missing
    hashed_password = user.get('password')

    if hashed_password and check_password_hash(hashed_password, password):
        # Credentials valid, return the user dictionary
        return user

    return None
# db/users.py

# ... (Existing get_all_users function)
from db.matches import get_swiped_users

def get_unseen_candidates(current_username):
    """
    Gets all users, excluding the current user and any users they have already swiped on.
    """
    all_users = get_all_users() # Assuming this returns a list of user objects/dicts
    swiped_users = get_swiped_users(current_username)
    
    candidates = []
    for user in all_users:
        if user['username'] != current_username and user['username'] not in swiped_users:
            candidates.append(user)
    
    # Optional: Shuffle the candidates list before returning
    import random
    random.shuffle(candidates)
    
    return candidates
def get_user_by_name(db, username):
    users = db.table('users')
    User = tinydb.Query()
    return users.get(User.username == username)

def delete_user(db, username, password):
    users = db.table('users')

    user = get_user(db, username, password)
    if user:
        return users.remove(doc_ids=[user.doc_id])
    return False

def add_user_friend(db, user, friend):
    users = db.table('users')
    User = tinydb.Query()
    if friend not in user['friends']:
        if users.get(User.username == friend):
            user['friends'].append(friend)
            users.upsert(user, (User.username == user['username']) &
                    (User.password == user['password']))
            return 'Friend {} added successfully!'.format(friend), 'success'
        return 'User {} does not exist.'.format(friend), 'danger'
    return 'You are already friends with {}.'.format(friend), 'warning'

def remove_user_friend(db, user, friend):
    users = db.table('users')
    User = tinydb.Query()
    if friend in user['friends']:
        user['friends'].remove(friend)
        users.upsert(user, (User.username == user['username']) &
                (User.password == user['password']))
        return 'Friend {} successfully unfriended!'.format(friend), 'success'
    return 'You are not friends with {}.'.format(friend), 'warning'

def get_user_friends(db, user):
    users = db.table('users')
    User = tinydb.Query()
    friends = []
    for friend in user['friends']:
        friends.append(users.get(User.username == friend))
    return friends

def update_user_profile(db, username, bio=None, email=None):
    """Update user's bio and/or email"""
    users = db.table('users')
    User = tinydb.Query()
    user = users.get(User.username == username)

    if not user:
        return False

    if bio is not None:
        user['profile']['bio'] = bio
    if email is not None:
        user['email'] = email

    users.update(user, User.username == username)
    return True

def add_user_photo(db, username, photo_path):
    """Add a photo path to user's profile"""
    users = db.table('users')
    User = tinydb.Query()
    user = users.get(User.username == username)

    if not user:
        return False

    if 'photos' not in user['profile']:
        user['profile']['photos'] = []

    user['profile']['photos'].append(photo_path)
    users.update(user, User.username == username)
    return True





import tinydb
from werkzeug.security import generate_password_hash, check_password_hash

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
def get_all_users(db):
    users = db.table('users')
    return users.all()

def get_user(db, username, password):
    users = db.table('users')
    User = tinydb.Query()
    user =  users.get(User.username == username)

    if not user:
        return None
    if check_password_hash(user['password'], password):
        return user
    return None

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





import time
import tinydb

def add_post(db, user, text, image_path=None):
    """Add a post with optional image"""
    posts = db.table('posts')
    post_data = {
        'user': user['username'],
        'text': text,
        'image': image_path,
        'time': time.time()
    }
    return posts.insert(post_data)

def get_posts(db, user):
    posts = db.table('posts')
    Post = tinydb.Query()
    return posts.search(Post.user==user['username'])

def get_all_posts(db):
    """Get all posts from the database"""
    posts = db.table('posts')
    return posts.all()

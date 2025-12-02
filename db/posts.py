import time
import tinydb

def add_post(db, user, text):
    posts = db.table('posts')
    posts.insert({'user': user['username'], 'text': text, 'time': time.time()})

def get_posts(db, user):
    posts = db.table('posts')
    Post = tinydb.Query()
    return posts.search(Post.user==user['username'])

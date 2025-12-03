# std imports
import time

# installed imports
import flask
import timeago
import tinydb
import os
from db import users
# handlers
from handlers import friends, login, posts, profile, messages
from handlers.swipe import swipe_bp
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import Flask, render_template, request, redirect, url_for, session


from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = flask.Flask(__name__)
app.secret_key = "super-secret-key"

# CSRF Protection
csrf = CSRFProtect(app)

# Rate Limiter
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)


@app.template_filter('convert_time')
def convert_time(ts):
    """A jinja template helper to convert timestamps to timeago."""
    return timeago.format(ts, time.time())
@app.route("/feed")
def feed():
    username = session.get("username")

    if not username:
        return redirect(url_for("login.login_page"))

    all_posts = posts.get_all_posts()  # You already have this in handlers/posts.py

    return render_template(
        "feed.html",
        posts=all_posts,
        user=users.get_user(username)  # From db/users.py
    )
@app.route("/swipe")
def swipe():
    username = session.get("username")

    if not username:
        return redirect(url_for("login.login_page"))

    all_users = users.get_all_users()

    # Remove yourself from swipe options
    all_users = [u for u in all_users if u["username"] != username]

    return render_template("swipe.html", users=all_users)

def timesince(dt):
    now = datetime.utcnow()
    diff = now - dt

    seconds = diff.total_seconds()
    minutes = seconds // 60
    hours = minutes // 60 
    days = diff.days 

    if seconds < 60:
        return f"{int(seconds)} seconds"
    elif minutes < 60:
        return f"{int(minutes)} minutes"
    elif hours < 24:
        return f"{int(hours)} hours"
    else:
        return f"{int(days)} days"
app.jinja_env.filters['timesince'] = timesince

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

app.register_blueprint(friends.blueprint)
app.register_blueprint(login.blueprint)
app.register_blueprint(posts.blueprint)
app.register_blueprint(profile.blueprint)
app.register_blueprint(messages.blueprint)
app.register_blueprint(swipe_bp)
# Apply specific rate limit to the login endpoint
limiter.limit("5 per minute", per_method=True, methods=["POST"])(login.login)

csrf = CSRFProtect(app)
app.secret_key = 'mygroup'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB limit
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} 


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=False, use_reloader=False,threaded=True)

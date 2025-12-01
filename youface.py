# std imports
import time

# installed imports
import flask
import timeago
import tinydb
import os
# handlers
from handlers import friends, login, posts, profile, messages
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
app = flask.Flask(__name__)

@app.template_filter('convert_time')
def convert_time(ts):
    """A jinja template helper to convert timestamps to timeago."""
    return timeago.format(ts, time.time())

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

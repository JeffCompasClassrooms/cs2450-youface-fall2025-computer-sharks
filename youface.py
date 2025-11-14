# std imports
import time

# installed imports
import flask
import timeago
import tinydb
import os
# handlers
from handlers import friends, login, posts, profile
from werkzeug.utils import secure_filename
app = flask.Flask(__name__)

@app.template_filter('convert_time')
def convert_time(ts):
    """A jinja template helper to convert timestamps to timeago."""
    return timeago.format(ts, time.time())

app.register_blueprint(friends.blueprint)
app.register_blueprint(login.blueprint)
app.register_blueprint(posts.blueprint)
app.register_blueprint(profile.blueprint)

app.secret_key = 'mygroup'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB limit
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.run(debug=True, host='0.0.0.0', port=5005) 

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == "__main__":
<<<<<<< HEAD
    app.run(host="0.0.0.0", port=5005, debug=False, use_reloader=False,threaded=True)
=======
    app.run(host="0.0.0.0", port=5005, debug=False, use_reloader=False, threaded=True)
>>>>>>> 21fad2505939bb4dfd2f57af2ef5564b15917ed7

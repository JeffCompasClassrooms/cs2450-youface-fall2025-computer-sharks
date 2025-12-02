import os
import flask
from flask import session
from werkzeug.utils import secure_filename
from db import posts, users, helpers

blueprint = flask.Blueprint("posts", __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@blueprint.route('/post', methods=['POST'])
def post():
    """Creates a new post with optional image."""
    db = helpers.load_db()

    if 'username' not in session:
        flask.flash('Please log in first.', 'warning')
        return flask.redirect(flask.url_for('login.loginscreen'))

    username = session['username']
    user = users.get_user_by_name(db, username)
    if not user:
        flask.flash('Invalid session. Please log in again.', 'danger')
        session.clear()
        return flask.redirect(flask.url_for('login.loginscreen'))

    # Get caption from form
    caption = flask.request.form.get('caption', '').strip()

    # Handle image upload
    image_path = None
    if 'image' in flask.request.files:
        file = flask.request.files['image']
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Create upload directory for posts
            upload_folder = os.path.join("static/uploads/posts", username)
            os.makedirs(upload_folder, exist_ok=True)

            # Add timestamp to filename to avoid conflicts
            import time
            timestamp = str(int(time.time()))
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{timestamp}{ext}"

            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            image_path = f"/static/uploads/posts/{username}/{filename}"

    # Require either caption or image
    if not caption and not image_path:
        flask.flash('Please provide a caption or an image.', 'warning')
        return flask.redirect(flask.url_for('login.index'))

    # Create the post
    posts.add_post(db, user, caption, image_path)
    flask.flash('Post created successfully!', 'success')

    return flask.redirect(flask.url_for('login.index'))

@blueprint.route('/comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    text = request.form.get('comment_text')
    # Save 'text' to database linked to 'post_id'
    return redirect(url_for('feed'))

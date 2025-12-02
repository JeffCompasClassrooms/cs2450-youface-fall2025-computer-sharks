import flask

from flask import session
from db import posts, users, helpers

blueprint = flask.Blueprint("posts", __name__)

@blueprint.route('/post', methods=['POST'])
def post():
    """Creates a new post."""
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

    post = flask.request.form.get('post')
    posts.add_post(db, user, post)

    return flask.redirect(flask.url_for('login.index'))

@blueprint.route('/comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    text = request.form.get('comment_text')
    # Save 'text' to database linked to 'post_id'
    return redirect(url_for('feed'))

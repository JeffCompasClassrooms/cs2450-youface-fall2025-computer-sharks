import flask

from handlers import copy
from db import users, helpers

blueprint = flask.Blueprint("profile", __name__)

@blueprint.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    """Display and handle the edit profile page."""
    db = helpers.load_db()

    # make sure the user is logged in
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')

    if username is None or password is None:
        flask.flash('You need to be logged in to edit your profile.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    user = users.get_user(db, username, password)
    if not user:
        flask.flash('You need to be logged in to edit your profile.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    if flask.request.method == 'POST':
        # Handle profile update here
        # You can add logic to update user information
        flask.flash('Profile updated successfully!', 'success')
        return flask.redirect(flask.url_for('login.index'))

    # GET request - display the edit form
    return flask.render_template('edit_profile.html', title=copy.title,
                                subtitle=copy.subtitle, user=user, username=username)

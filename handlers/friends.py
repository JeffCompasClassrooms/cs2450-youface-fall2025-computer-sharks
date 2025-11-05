import flask

from flask import flash
from handlers import copy
from db import posts, users, helpers

blueprint = flask.Blueprint("friends", __name__)

@blueprint.route('/addfriend', methods=['POST'])
def addfriend():
    """Adds a friend to the user's friends list."""
    db = helpers.load_db()

    # make sure the user is logged in
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')

    if username is None and password is None:
        return flask.redirect(flask.url_for('login.loginscreen'))

    user = users.get_user(db, username, password)
    if not user:
        flash('You need to be logged in to do that.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    # add the friend
    name = flask.request.form.get('name')
    msg, category = users.add_user_friend(db, user, name)

    flask.flash(msg, category)
    return flask.redirect(flask.url_for('login.index'))

@blueprint.route('/searchUser', methods=['POST'])
@blueprint.route('/searchUser', methods=['POST'])
def searchUser():
    """Search users (case-insensitive substring) and render the feed with results."""
    db = helpers.load_db()

    # make sure the user is logged in
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    if username is None and password is None:
        return flask.redirect(flask.url_for('login.loginscreen'))

    user = users.get_user(db, username, password)
    if not user:
        flask.flash('You need to be logged in to do that.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    # read the same form field name you have in the template
    query = flask.request.form.get('searchName', '').strip()
    if not query:
        flask.flash('Please enter a username to search for.', 'warning')
        return flask.redirect(flask.url_for('login.index'))

    # case-insensitive substring search across all users
    all_users = db.table('users').all()
    q_lower = query.lower()
    results = [u for u in all_users if u.get('username') and q_lower in u['username'].lower()]

    # prepare the same context the feed expects
    user_friends = users.get_user_friends(db, user)
    user_posts = posts.get_posts(db, user)[::-1]

    # <-- RENDER feed.html and include search_results -->
    return flask.render_template(
        'feed.html',                # your main feed template
        title=copy.title,
        subtitle=copy.subtitle,
        user=user,
        username=username,
        friends=user_friends,
        posts=user_posts,
        search_results=results
    )

@blueprint.route('/unfriend', methods=['POST'])
def unfriend():
    """Removes a user from the user's friends list."""
    db = helpers.load_db()

    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')

    user = users.get_user(db, username, password)
    if not user:
        flask.flash('You need to be logged in to do that.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    name = flask.request.form.get('name')
    msg, category = users.remove_user_friend(db, user, name)

    flask.flash(msg, category)
    return flask.redirect(flask.url_for('login.index'))

@blueprint.route('/friend/<fname>')
def view_friend(fname):
    """View the page of a given friend."""
    db = helpers.load_db()

    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')

    user = users.get_user(db, username, password)
    if not user:
        flask.flash('You must be logged in to do that.', 'danger')
        return flask.redirect(flask.url_for('login.loginscreen'))

    friend = users.get_user_by_name(db, fname)
    all_posts = posts.get_posts(db, friend)[::-1] # reverse order

    return flask.render_template('friend.html', title=copy.title,
            subtitle=copy.subtitle, user=user, username=username,
            friend=friend['username'],
            friends=users.get_user_friends(db, user), posts=all_posts)

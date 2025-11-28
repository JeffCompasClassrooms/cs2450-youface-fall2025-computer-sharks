import flask

from flask import Blueprint,request,redirect,url_for,flash,make_response, session
from handlers import copy
from db import posts, users, helpers

blueprint = flask.Blueprint("login", __name__)

@blueprint.route('/loginscreen')
def loginscreen():
    """Present a form to the user to enter their username and password."""
    db = helpers.load_db()

    # First check if already logged in
    if 'username' in session:
        username = session['username']
        if users.get_user_by_name(db, username):
            flask.flash('You are already logged in.', 'warning')
            return flask.redirect(flask.url_for('login.index'))

    return flask.render_template('login.html', title=copy.title,
            subtitle=copy.subtitle)

@blueprint.route('/login', methods=['POST'])
def login():
    """Log in the user.

    Using the username and password fields on the form, create, delete, or
    log in a user, based on what button they click.
    """
    db = helpers.load_db()

    #Server-side honeypot check
    if flask.request.form.get('are_you_a_bot'):
        flask.flash('Submission rejected (bot detected).', 'danger')
        return redirect(url_for('login.loginscreen'))

    username = flask.request.form.get('username')
    password = flask.request.form.get('password')
    submit = flask.request.form.get('type')
    resp = make_response(redirect(url_for('profile.edit_profile', username=username)) )

    if submit == 'Create':
        email = flask.request.form.get('email', '')
        shoe_size = flask.request.form.get('shoe_size', 0)
        has_horn = flask.request.form.get('has_horn', 'false').lower() == 'true'

        try:
            shoe_size = int(shoe_size)
        except ValueError:
            shoe_size = 0

        if users.new_user(db, username, password, email=email, shoe_size=shoe_size, has_clown_horns=has_horn) is None:
            flask.flash(f'Username {username} already taken!', 'danger')
            return redirect(url_for('login.loginscreen'))
            
        flask.flash(f'User {username} created successfully!', 'success')

    elif submit == 'Delete':
        if users.delete_user(db, username, password):
            session.clear()
            flask.flash(f'User {username} deleted successfully!', 'success')
            return redirect(url_for('login.loginscreen'))
        else:
            flask.flash('Delete failed: wrong username or password.','danger')
            return redirect(url_for('login.loginscreen'))
        
    user = users.get_user(db, username, password)
    if not user:
        # Invalid credentials → clear session and redirect
        session.clear()
        flash('Incorrect username or password!', 'danger')
        return redirect(url_for('login.loginscreen'))

    session['username'] = username
    flash(f'Logged in as {username}', 'success')
    return redirect(url_for('profile.edit_profile', username=username)) 

@blueprint.route('/logout', methods=['POST'])
def logout():
    """Log out the user."""
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login.loginscreen'))

@blueprint.route('/')
def index():
    """Serves the main feed page for the user."""
    db = helpers.load_db()

    # make sure the user is logged in
    if 'username' not in session:
        flask.flash('Please log in to view the feed.', 'warning')
        return flask.redirect(flask.url_for('login.loginscreen'))

    username = session['username']
    user = users.get_user_by_name(db, username)
    if not user:
        flask.flash('Invalid session. Please log in again.', 'danger')
        session.clear()
        return flask.redirect(flask.url_for('login.loginscreen'))
    
    # get the info for the user's feed
    friends = users.get_user_friends(db, user)
    all_posts = []
    for friend in friends + [user]:
        all_posts += posts.get_posts(db, friend)
    # sort posts
    sorted_posts = sorted(all_posts, key=lambda post: post['time'], reverse=True)

    return flask.render_template('feed.html', title=copy.title,
            subtitle=copy.subtitle, user=user, username=username,
            friends=friends, posts=sorted_posts)

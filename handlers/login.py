import flask

from flask import Blueprint,request,redirect,url_for,flash,make_response
from handlers import copy
from db import posts, users, helpers

blueprint = flask.Blueprint("login", __name__)

@blueprint.route('/loginscreen')
def loginscreen():
    """Present a form to the user to enter their username and password."""
    db = helpers.load_db()

    # First check if already logged in
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')

    if username is not None and password is not None:
        if users.get_user(db, username, password):
            # If they are logged in, redirect them to the feed page
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

    username = flask.request.form.get('username')
    password = flask.request.form.get('password')
    submit = flask.request.form.get('type')
    resp = make_response(redirect(url_for('profile.edit_profile', username=username)))

    if submit == 'Create':
        shoe_size = flask.request.form.get('shoe_size', 0)
        has_horn = flask.request.form.get('has_clown_horns', 'false').lower() == 'true'

        try:
            shoe_size = int(shoe_size)
        except ValueError:
            shoe_size = 0

        if users.new_user(db, username, password) is None:
            resp = make_response(redirect(url_for('login.loginscreen')))
            resp.set_cookie('username', '', expires=0)
            resp.set_cookie('password', '', expires=0)
            flask.flash(f'Username {username} already taken!', 'danger')
            return resp 
            
        flask.flash(f'User {username} created successfully!', 'success')
    elif submit == 'Delete':
        if users.delete_user(db, username, password):
            resp = make_response(redirect(url_for('login.loginscreen')))
            resp.set_cookie('username', '', expires=0)
            resp.set_cookie('password', '', expires=0)
            flask.flash(f'User {username} deleted successfully!', 'success')
            return resp
        else:
            flask.flash('Delete failed: wrong username or password.','danger')
            return redirect(url_for('login.loginscreen'))
    user = users.get_user(db, username, password)
    if not user:
        # Invalid credentials → clear cookies and redirect
        resp = make_response(redirect(url_for('login.loginscreen')))
        resp.set_cookie('username', '', expires=0)
        resp.set_cookie('password', '', expires=0)
        flash('Incorrect username or password!', 'danger')
        return resp

    # ---- SUCCESSFUL LOGIN ----
    # Set cookies for logged-in user
    resp.set_cookie('username', username)
    resp.set_cookie('password', password)
    flash(f'Logged in as {username}', 'success')
    return resp

@blueprint.route('/logout', methods=['POST'])
def logout():
    """Log out the user."""
    db = helpers.load_db()

    resp = flask.make_response(flask.redirect(flask.url_for('login.loginscreen')))
    resp.set_cookie('username', '', expires=0)
    resp.set_cookie('password', '', expires=0)
    return resp

@blueprint.route('/')
def index():
    """Serves the main feed page for the user."""
    db = helpers.load_db()

    # make sure the user is logged in
    username = flask.request.cookies.get('username')
    password = flask.request.cookies.get('password')
    if username is None and password is None:
        return flask.redirect(flask.url_for('login.loginscreen'))
    user = users.get_user(db, username, password)
    if not user:
        flask.flash('Invalid credentials. Please try again.', 'danger')
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

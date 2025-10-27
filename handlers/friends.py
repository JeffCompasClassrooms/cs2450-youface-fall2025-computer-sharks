import flask

from handlers import copy
from db import posts, users, helpers

blueprint = flask.Blueprint("friends", __name__)
#-------NEW ROUTE FOR FINDING AND FILTERING FRIENDS-------
@blueprint.route('/find-friends')
def find_friends():
    db = helpers.load_db()
    username = flask.request.cookies.get('username')
    if not username:
        flask.flash('You need to be logged in to find friends.','warning')
        return flask.redirect(flask.url_for('login.loginscreen'))
    all_users = users.get_all_users(db)
     # Get the filter criteria from the form submission (from the URL)
    min_shoe_size_str = flask.request.args.get('shoe_size')
    is_clown = flask.request.args.get('is_clown')
    has_clown_horns = flask.request.args.get('has_clown_horns')

    # Convert shoe size to an integer for numerical comparison
    min_shoe_size = 0
    if min_shoe_size_str and min_shoe_size_str.isdigit():
        min_shoe_size = int(min_shoe_size_str)

    # Start with an empty list and add users who match all active filters
    filtered_users = []
    for user in all_users:
        # Don't show the currently logged-in user in the results
        if user['username'] == username:
            continue

        # Check "Is a Clown" filter
        # If the filter is on, but the user is not a clown, skip them.
        if is_clown and not user.get('is_clown', False):
            continue

        # Check "Has Clown Horns" filter
        # If the filter is on, but the user doesn't have horns, skip them.
        if has_clown_horns and not user.get('has_clown_horns', False):
            continue

        # Check "Minimum Shoe Size" filter
        user_shoe_size = user.get('shoe_size')
        if min_shoe_size > 0:
            # If shoe size filter is active, skip users with no shoe size or a size that's too small.
            if user_shoe_size is None or user_shoe_size < min_shoe_size:
                continue

        # If the user has passed all the "continue" checks, they are a match.
        filtered_users.append(user)

    # Render the new find_friends.html template with the final list
    return flask.render_template('find_friends.html', users=filtered_users)


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

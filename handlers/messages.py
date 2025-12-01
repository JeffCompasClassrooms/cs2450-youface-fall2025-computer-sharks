import flask
import time
from db import helpers
from tinydb import Query

blueprint = flask.Blueprint("messages", __name__)

@blueprint.route('/message/<username>', methods=['GET', 'POST'])
def message_user(username):
    db = helpers.load_db()
    Messages = db.table('messages')
    User = Query()

    # must be logged in
    if "username" not in flask.session:
        flask.flash("You must be logged in.", "danger")
        return flask.redirect(flask.url_for("login.loginscreen"))

    me = flask.session["username"]

    # POST: sending a message
    if flask.request.method == 'POST':
        text = flask.request.form.get('message_text').strip()

        if text == "":
            flask.flash("Message cannot be empty.", "warning")
        else:
            Messages.insert({
                "sender": me,
                "receiver": username,
                "text": text,
                "timestamp": time.time()
            })
            flask.flash("Message sent!", "success")

        return flask.redirect(f"/message/{username}")

    # GET: load conversation
    conversation = Messages.search(
        ((User.sender == me) & (User.receiver == username)) |
        ((User.sender == username) & (User.receiver == me))
    )

    # Sort by timestamp
    conversation = sorted(conversation, key=lambda x: x["timestamp"])

    return flask.render_template(
        "messages.html",
        username=me,
        friend=username,
        messages=conversation
    )

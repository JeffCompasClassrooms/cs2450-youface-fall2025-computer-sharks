import os
import flask
from flask import Blueprint, request, redirect, url_for, flash, render_template, make_response, current_app
from werkzeug.utils import secure_filename

blueprint = Blueprint('profile', __name__)

# In-memory user profiles
profiles = {}

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------------------------
# Edit Profile Page
# ---------------------------
@blueprint.route('/profile', methods=['GET', 'POST'])
def edit_profile():
    username = request.cookies.get('username')
    if not username:
        flash("Please log in first!", "danger")
        return redirect(url_for("login.loginscreen"))

    # Create profile if it doesn't exist yet
    if username not in profiles:
        profiles[username] = {
            "username": username,
            "bio": "",
            "email": "",
            "photos": []
        }

    user = profiles[username]

    if request.method == 'POST':
        # Update user data
        new_username = request.form.get('username', user['username'])
        user['bio'] = request.form.get('bio', user['bio'])
        user['email'] = request.form.get('email', user['email'])

        # Handle username change
        if new_username != username:
            profiles[new_username] = user
            del profiles[username]
            user['username'] = new_username

            # Update cookie
            resp = make_response(redirect(url_for('profile.edit_profile')))
            resp.set_cookie('username', new_username)
            flash('Profile updated!', 'success')
            return resp

        flash('Profile updated!', 'success')
        return redirect(url_for('profile.edit_profile'))

    return render_template('profile.html', title='Edit Profile', user=user, photos=user['photos'])


# ---------------------------
# Upload Photo
# ---------------------------
@blueprint.route('/upload_photo', methods=['POST'])
def upload_photo():
    username = request.cookies.get('username')

    if not username:
        flash("Please log in first!", "danger")
        return redirect(url_for("login.loginscreen"))

    if username not in profiles:
        flash("User profile not found!", "danger")
        return redirect(url_for("profile.edit_profile"))

    user = profiles[username]

    file = request.files.get('photo')
    if not file or not allowed_file(file.filename):
        flash("Invalid file type!", "danger")
        return redirect(url_for('profile.edit_profile'))

    filename = secure_filename(file.filename)
    upload_folder = os.path.join("static/uploads", username)
    os.makedirs(upload_folder, exist_ok=True)

    path = os.path.join(upload_folder, filename)
    file.save(path)

    # Save to user's photo list
    user["photos"].append(f"/static/uploads/{username}/{filename}")

    flash("Photo uploaded!", "success")
    return redirect(url_for('profile.edit_profile'))


import os
import flask
from flask import Blueprint, request, redirect, url_for, flash, render_template, make_response, current_app, session
from werkzeug.utils import secure_filename
from db.helpers import load_db
from db.users import get_user_by_name, update_user_profile, add_user_photo

blueprint = Blueprint('profile', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------------------------
# Edit Profile Page
# ---------------------------
@blueprint.route('/profile', methods=['GET', 'POST'])
def edit_profile():
    if 'username' not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for("login.loginscreen"))

    username = session['username']
    db = load_db()
    user = get_user_by_name(db, username)

    if not user:
        flash("User not found!", "danger")
        return redirect(url_for("login.loginscreen"))

    if request.method == 'POST':
        # Get form data
        bio = request.form.get('bio', '')
        email = request.form.get('email', '')

        # Update profile in database
        if update_user_profile(db, username, bio=bio, email=email):
            flash('Profile updated!', 'success')
        else:
            flash('Failed to update profile!', 'danger')

        return redirect(url_for('profile.edit_profile'))

    # Prepare user data for template
    user_data = {
        'username': user['username'],
        'email': user.get('email', ''),
        'bio': user.get('profile', {}).get('bio', ''),
        'photos': user.get('profile', {}).get('photos', [])
    }

    return render_template('profile.html', title='Edit Profile', user=user_data, photos=user_data['photos'])


# ---------------------------
# Upload Photo
# ---------------------------
@blueprint.route('/upload_photo', methods=['POST'])
def upload_photo():
    if 'username' not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for("login.loginscreen"))

    username = session['username']
    db = load_db()
    user = get_user_by_name(db, username)

    if not user:
        flash("User profile not found!", "danger")
        return redirect(url_for("profile.edit_profile"))

    file = request.files.get('photo')
    if not file or not allowed_file(file.filename):
        flash("Invalid file type! Please upload PNG, JPG, JPEG, or GIF.", "danger")
        return redirect(url_for('profile.edit_profile'))

    filename = secure_filename(file.filename)
    upload_folder = os.path.join("static/uploads", username)
    os.makedirs(upload_folder, exist_ok=True)

    path = os.path.join(upload_folder, filename)
    file.save(path)

    # Save photo path to database
    photo_path = f"/static/uploads/{username}/{filename}"
    if add_user_photo(db, username, photo_path):
        flash("Photo uploaded successfully!", "success")
    else:
        flash("Failed to save photo!", "danger")

    return redirect(url_for('profile.edit_profile'))

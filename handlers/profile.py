import os
import flask
from flask import Blueprint, request, session, redirect, url_for, flash, render_template, current_app
blueprint = flask.Blueprint('profile', __name__)

# Dummy user data for demonstration; replace with DB logic as needed
user_data = {
    'username': 'testuser',
    'bio': 'This is my bio.',
    'email': 'testuser@example.com'
} 

ALLOWED_EXTENSIONS = {'png','jpg','jpeg','gif'} 

@blueprint.route('/profile', methods=['GET', 'POST'])
def edit_profile():
    if request.method == 'POST':
        # Update user data (replace with DB update logic)
        user_data['username'] = request.form.get('username', user_data['username'])
        user_data['bio'] = request.form.get('bio', user_data['bio'])
        user_data['email'] = request.form.get('email', user_data['email'])
        flash('Profile updated!', 'success')
        return redirect(url_for('profile.edit_profile'))
    return flask.render_template('profile.html', title='Edit Profile', user=user_data, photos=[])

@blueprint.route('/upload_photo', methods=['POST'])
def upload_photo():
    if 'user' not in session:
        flash('Please log in first!')
        return redirect(url_for('loginscreen'))

    user = session['user']
    file = request.files.get('photo')

    if not file or not allowed_file(file.filename):
        flash('Invalid file type!')
        return redirect(url_for('profile.edit_profile', username=user))

    filename = secure_filename(file.filename)
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], user)
    os.makedirs(user_folder, exist_ok=True)
    file.save(os.path.join(user_folder, filename))

    flash('Photo uploaded successfully!')
    return redirect(url_for('profile.edit_profile', username=user))


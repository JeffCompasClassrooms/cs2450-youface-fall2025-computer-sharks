import flask
from flask import request, session, redirect, url_for

blueprint = flask.Blueprint('profile', __name__)

# Dummy user data for demonstration; replace with DB logic as needed
user_data = {
	'username': 'testuser',
	'bio': 'This is my bio.',
	'email': 'testuser@example.com'
}

@blueprint.route('/profile', methods=['GET', 'POST'])
def edit_profile():
	if request.method == 'POST':
		# Update user data (replace with DB update logic)
		user_data['bio'] = request.form.get('bio', user_data['bio'])
		user_data['email'] = request.form.get('email', user_data['email'])
		flask.flash('Profile updated!', 'success')
		return redirect(url_for('profile.edit_profile'))
	return flask.render_template('profile.html', title='Edit Profile', user=user_data)

# Profile Picture Implementation Guide

This guide provides step-by-step instructions for implementing profile pictures in the YouFace application.

## Step-by-Step Instructions for Adding Profile Pictures

### 1. **Create Upload Directory Structure**
```bash
mkdir -p static/uploads/profile_pics
```
- This directory will store uploaded profile pictures
- Add `static/uploads/` to your `.gitignore` file to avoid committing user uploads

### 2. **Update Database Schema (db/users.py)**
Add a function to update user's profile picture path:
```python
def update_user_profile_pic(db, user, pic_path):
    users = db.table('users')
    User = tinydb.Query()
    user['profile_pic'] = pic_path
    users.upsert(user, (User.username == user['username']))
    return 'Profile picture updated!', 'success'

def get_user_profile_pic(db, user):
    return user.get('profile_pic', 'default.jpg')  # default if none set
```

### 3. **Install Required Package**
Add to `requirements.txt`:
```
Werkzeug  # For secure_filename function
Pillow    # For image processing/validation
```
Then run: `pip install Werkzeug Pillow`

### 4. **Update handlers/profile.py**
Modify your edit_profile route to handle file uploads:

```python
import os
from werkzeug.utils import secure_filename
from PIL import Image

# Add these constants at the top
UPLOAD_FOLDER = 'static/uploads/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@blueprint.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    db = helpers.load_db()

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
        # Handle profile picture upload
        if 'profile_pic' in flask.request.files:
            file = flask.request.files['profile_pic']
            if file and file.filename != '' and allowed_file(file.filename):
                # Create secure filename
                filename = secure_filename(f"{username}_{file.filename}")
                filepath = os.path.join(UPLOAD_FOLDER, filename)

                # Save file
                file.save(filepath)

                # Optional: Resize image to standard size
                img = Image.open(filepath)
                img.thumbnail((400, 400))  # Resize to max 400x400
                img.save(filepath)

                # Update database
                pic_url = f"uploads/profile_pics/{filename}"
                users.update_user_profile_pic(db, user, pic_url)
                flask.flash('Profile picture updated successfully!', 'success')
            elif file and file.filename != '':
                flask.flash('Invalid file type. Please upload PNG, JPG, or GIF.', 'danger')

        return flask.redirect(flask.url_for('login.index'))

    # GET request
    current_pic = users.get_user_profile_pic(db, user)
    return flask.render_template('edit_profile.html', title=copy.title,
                                subtitle=copy.subtitle, user=user,
                                username=username, current_pic=current_pic)
```

### 5. **Update templates/edit_profile.html**
Add file upload form:

```html
<form method="post" action="{{ url_for('profile.edit_profile') }}" enctype="multipart/form-data">
  <fieldset>
    <legend>Profile Settings</legend>
    <hr />

    <!-- Profile Picture Section -->
    <div class="form-group">
      <label>Current Profile Picture</label>
      <div class="mb-2">
        <img src="{{ url_for('static', filename=current_pic) }}"
             alt="Profile Picture"
             class="img-thumbnail"
             style="max-width: 200px;">
      </div>
      <label for="profile_pic">Upload New Profile Picture</label>
      <input type="file" class="form-control-file" name="profile_pic" accept="image/*">
      <small class="form-text text-muted">Max size: 5MB. Allowed: PNG, JPG, GIF</small>
    </div>

    <!-- Rest of your form... -->
```

### 6. **Update youface.py**
Add file upload configuration:

```python
app.config['UPLOAD_FOLDER'] = 'static/uploads/profile_pics'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max
```

### 7. **Display Profile Pictures in Templates**

**In templates/feed.html** (show next to posts):
```html
<h4 class="card-title">
  <img src="{{ url_for('static', filename=user.profile_pic if user.profile_pic else 'default.jpg') }}"
       alt="{{ post.user }}"
       class="rounded-circle"
       style="width: 40px; height: 40px; object-fit: cover;">
  {{ post.user }}
</h4>
```

**In templates/profile.html** (navbar or header):
```html
<img src="{{ url_for('static', filename=user.profile_pic if user.profile_pic else 'default.jpg') }}"
     alt="Profile"
     class="rounded-circle"
     style="width: 50px; height: 50px; object-fit: cover;">
```

### 8. **Add Default Profile Picture**
- Download or create a default profile picture image
- Save it as `static/default.jpg`

### 9. **Update Existing Users** (Optional)
Since existing users won't have profile_pic field, you have two options:
- **Option A**: The code handles it with `.get('profile_pic', 'default.jpg')`
- **Option B**: Run a migration script to add the field to all users

### 10. **Security Considerations**
- ✅ File type validation (only images)
- ✅ File size limits (5MB)
- ✅ Secure filenames (prevents directory traversal)
- ✅ Image resizing (prevents huge files)
- Consider adding: File content validation with Pillow

### **Bonus: Display in Friend List**
In `templates/feed.html`, update friend list:
```html
{% for friend in friends %}
  <li>
    <img src="{{ url_for('static', filename=friend.profile_pic if friend.profile_pic else 'default.jpg') }}"
         class="rounded-circle"
         style="width: 30px; height: 30px;">
    <a href="/friend/{{ friend.username }}">{{ friend.username }}</a>
  </li>
{% endfor %}
```

---

## Summary Checklist:
- [ ] Create upload directory
- [ ] Add functions to db/users.py
- [ ] Install Werkzeug and Pillow
- [ ] Update handlers/profile.py with upload logic
- [ ] Update edit_profile.html with file input
- [ ] Configure Flask app for uploads
- [ ] Add default profile picture
- [ ] Display pictures in templates

---

## Notes
- The implementation uses TinyDB (your existing database) to store the file path
- Actual image files are stored in the filesystem under `static/uploads/profile_pics/`
- The `db/users.py` helper functions follow the same pattern as your existing code (posts.py, helpers.py)
- Security features are built-in to prevent common vulnerabilities

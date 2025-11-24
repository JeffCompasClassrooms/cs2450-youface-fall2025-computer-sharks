# Security Fixes Guide for OnlyClowns

This guide will walk you through fixing the major security vulnerabilities in your OnlyClowns application.

---

## Table of Contents
1. [Password Hashing](#1-password-hashing)
2. [Secure Session Management](#2-secure-session-management)
3. [CSRF Protection](#3-csrf-protection)
4. [Additional Security Improvements](#4-additional-security-improvements)

---

## 1. Password Hashing

### Current Problem
Passwords are currently stored in **plaintext** in the database. This means:
- If someone accesses your `db.json` file, they can see everyone's passwords
- If your database is compromised, all user accounts are immediately at risk
- This violates basic security best practices

### Solution: Use `werkzeug.security` for Password Hashing

Werkzeug (already included with Flask) provides secure password hashing using `pbkdf2:sha256`.

### Step 1: Update `db/users.py`

**Import the hashing functions at the top:**
```python
import tinydb
from werkzeug.security import generate_password_hash, check_password_hash
```

**Modify the `new_user()` function** to hash passwords before storing:
```python
def new_user(db, username, password, email=None, shoe_size=None, is_clown=False, has_clown_horns=False):
    users = db.table('users')
    User = tinydb.Query()
    if users.get(User.username == username):
        return None

    # Hash the password before storing
    hashed_password = generate_password_hash(password)

    user_record = {
        'username': username,
        'password': hashed_password,  # Store hashed password
        'email': email,
        'friends': [],
        'profile': {
            'shoe_size': shoe_size,
            'is_clown': is_clown,
            'has_clown_horns': has_clown_horns
        }
    }
    return users.insert(user_record)
```

**Modify the `get_user()` function** to verify hashed passwords:
```python
def get_user(db, username, password):
    users = db.table('users')
    User = tinydb.Query()

    # First, get the user by username only
    user = users.get(User.username == username)

    if not user:
        return None

    # Check if the provided password matches the hashed password
    if check_password_hash(user['password'], password):
        return user

    return None
```

**Modify the `delete_user()` function** similarly:
```python
def delete_user(db, username, password):
    users = db.table('users')
    User = tinydb.Query()

    # Verify the user exists and password is correct before deleting
    user = get_user(db, username, password)
    if user:
        return users.remove(doc_ids=[user.doc_id])

    return False
```

### Step 2: Clear Your Database

After implementing password hashing, you'll need to **delete or reset your `db.json` file** because existing passwords are in plaintext and won't work with the new hashing system.

**Option A: Delete the file**
```bash
rm db.json
```

**Option B: Manually edit `db.json`** and remove all users from the `users` table:
```json
{
  "users": {},
  "posts": {},
  "_default": {}
}
```

### Testing
1. Start your application: `python youface.py`
2. Create a new account
3. Check `db.json` - you should see a hashed password like:
   ```
   "password": "pbkdf2:sha256:600000$randomsalt$hashedpasswordstring"
   ```
4. Log out and log back in - it should work!

---

## 2. Secure Session Management

### Current Problem
Your app stores **username and password** directly in cookies:
```python
resp.set_cookie('username', username)
resp.set_cookie('password', password)
```

This means:
- Anyone who intercepts cookies can see credentials
- Cookies aren't encrypted or signed
- Password is sent with every request

### Solution: Use Flask Sessions

Flask sessions are cryptographically signed and don't expose sensitive data.

### Step 1: Update `handlers/login.py`

**Import `session` from Flask** (add to existing imports):
```python
from flask import Blueprint, request, redirect, url_for, flash, make_response, session
```

**Update the login route** to use sessions instead of cookies:

**In the `login()` function**, replace cookie setting with sessions:

**OLD CODE (lines 77-82):**
```python
# ---- SUCCESSFUL LOGIN ----
# Set cookies for logged-in user
resp.set_cookie('username', username)
resp.set_cookie('password', password)
flash(f'Logged in as {username}', 'success')
return resp
```

**NEW CODE:**
```python
# ---- SUCCESSFUL LOGIN ----
# Store username in session (don't store password!)
session['username'] = username
flash(f'Logged in as {username}', 'success')
return redirect(url_for('profile.edit_profile', username=username))
```

**Update the logout route** to clear sessions:

**OLD CODE (lines 84-92):**
```python
@blueprint.route('/logout', methods=['POST'])
def logout():
    """Log out the user."""
    db = helpers.load_db()

    resp = flask.make_response(flask.redirect(flask.url_for('login.loginscreen')))
    resp.set_cookie('username', '', expires=0)
    resp.set_cookie('password', '', expires=0)
    return resp
```

**NEW CODE:**
```python
@blueprint.route('/logout', methods=['POST'])
def logout():
    """Log out the user."""
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login.loginscreen'))
```

**Update the `loginscreen()` route:**

**OLD CODE (lines 14-22):**
```python
# First check if already logged in
username = flask.request.cookies.get('username')
password = flask.request.cookies.get('password')

if username is not None and password is not None:
    if users.get_user(db, username, password):
        # If they are logged in, redirect them to the feed page
        flask.flash('You are already logged in.', 'warning')
        return flask.redirect(flask.url_for('login.index'))
```

**NEW CODE:**
```python
# First check if already logged in
if 'username' in session:
    username = session['username']
    if users.get_user_by_name(db, username):
        flask.flash('You are already logged in.', 'warning')
        return flask.redirect(flask.url_for('login.index'))
```

**Update the `index()` route (feed page):**

**OLD CODE (lines 100-107):**
```python
# make sure the user is logged in
username = flask.request.cookies.get('username')
password = flask.request.cookies.get('password')
if username is None and password is None:
    return flask.redirect(flask.url_for('login.loginscreen'))
user = users.get_user(db, username, password)
if not user:
    flask.flash('Invalid credentials. Please try again.', 'danger')
    return flask.redirect(flask.url_for('login.loginscreen'))
```

**NEW CODE:**
```python
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
```

**Update Create account section** to remove cookie clearing:

**In `login()` function, when Create fails (lines 51-56):**

**OLD CODE:**
```python
if users.new_user(db, username, password, email=email, shoe_size=shoe_size, has_clown_horns=has_horn) is None:
    resp = make_response(redirect(url_for('login.loginscreen')))
    resp.set_cookie('username', '', expires=0)
    resp.set_cookie('password', '', expires=0)
    flask.flash(f'Username {username} already taken!', 'danger')
    return resp
```

**NEW CODE:**
```python
if users.new_user(db, username, password, email=email, shoe_size=shoe_size, has_clown_horns=has_horn) is None:
    flask.flash(f'Username {username} already taken!', 'danger')
    return redirect(url_for('login.loginscreen'))
```

**In `login()` function, when Delete succeeds (lines 59-64):**

**OLD CODE:**
```python
if users.delete_user(db, username, password):
    resp = make_response(redirect(url_for('login.loginscreen')))
    resp.set_cookie('username', '', expires=0)
    resp.set_cookie('password', '', expires=0)
    flask.flash(f'User {username} deleted successfully!', 'success')
    return resp
```

**NEW CODE:**
```python
if users.delete_user(db, username, password):
    session.clear()
    flask.flash(f'User {username} deleted successfully!', 'success')
    return redirect(url_for('login.loginscreen'))
```

**When login fails (lines 69-75):**

**OLD CODE:**
```python
if not user:
    # Invalid credentials → clear cookies and redirect
    resp = make_response(redirect(url_for('login.loginscreen')))
    resp.set_cookie('username', '', expires=0)
    resp.set_cookie('password', '', expires=0)
    flash('Incorrect username or password!', 'danger')
    return resp
```

**NEW CODE:**
```python
if not user:
    # Invalid credentials → clear session and redirect
    session.clear()
    flash('Incorrect username or password!', 'danger')
    return redirect(url_for('login.loginscreen'))
```

### Step 2: Update Other Handlers

You'll need to update other files that check cookies. Here are the main ones:

#### `handlers/friends.py`

**Find all instances of:**
```python
username = flask.request.cookies.get('username')
password = flask.request.cookies.get('password')
user = users.get_user(db, username, password)
```

**Replace with:**
```python
if 'username' not in flask.session:
    flask.flash('Please log in first.', 'warning')
    return flask.redirect(flask.url_for('login.loginscreen'))

username = flask.session['username']
user = users.get_user_by_name(db, username)
```

#### `handlers/posts.py`

Same replacement as above.

#### `handlers/profile.py`

Same replacement as above.

### Step 3: Ensure Secret Key is Set

Flask sessions require a secret key. In `youface.py`, you already have:
```python
app.secret_key = 'mygroup'
```

**IMPORTANT:** For production, use a secure random key:
```python
import secrets
app.secret_key = secrets.token_hex(32)  # Generates a random 64-character hex string
```

For your class project, `'mygroup'` is fine, but **never use a simple secret key in production!**

---

## 3. CSRF Protection

### Current Problem
Your forms don't have CSRF (Cross-Site Request Forgery) protection. This means:
- Malicious websites could submit forms on behalf of logged-in users
- Attackers could trick users into performing unwanted actions

### Solution: Use Flask-WTF

Flask-WTF provides easy CSRF protection for forms.

### Step 1: Install Flask-WTF

Add to `requirements.txt`:
```
Flask-WTF
```

Then install:
```bash
pip install Flask-WTF
```

### Step 2: Enable CSRF Protection in `youface.py`

**Add imports:**
```python
from flask_wtf.csrf import CSRFProtect
```

**Initialize CSRF protection:**
```python
app = flask.Flask(__name__)
app.secret_key = 'mygroup'

# Enable CSRF protection
csrf = CSRFProtect(app)
```

### Step 3: Add CSRF Tokens to Forms

**In `templates/login.html`**, add CSRF token to both forms:

**After `<form method="post" action="/login">`, add:**
```html
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
```

**Example for login form:**
```html
<form method="post" action="/login">
  <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
  <fieldset>
    <legend>Login</legend>
    <!-- rest of form -->
```

Do this for **EVERY form** in your templates:
- `templates/login.html` (both login and create forms)
- `templates/feed.html` (post creation form)
- `templates/profile.html` (profile edit and photo upload forms)
- `templates/find_friends.html` (add friend forms)
- `templates/friend.html` (unfriend form if any)
- `templates/base.html` (logout form in navigation)

### Step 4: Add CSRF Token to Logout Form

**In `templates/base.html`**, find the logout form and add the token:

**Before:**
```html
<form action="/logout" method="post" class="d-inline">
  <button type="submit" class="btn btn-danger">Logout</button>
</form>
```

**After:**
```html
<form action="/logout" method="post" class="d-inline">
  <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
  <button type="submit" class="btn btn-danger">Logout</button>
</form>
```

---

## 4. Additional Security Improvements

### 4.1 Environment Variables for Secret Key

Instead of hardcoding your secret key, use environment variables.

**In `youface.py`:**
```python
import os

app.secret_key = os.environ.get('SECRET_KEY', 'mygroup')
```

**Set the environment variable:**
```bash
export SECRET_KEY='your-super-secret-key-here'
```

Or create a `.env` file (and add `.env` to `.gitignore`!):
```
SECRET_KEY=your-super-secret-key-here
```

### 4.2 Secure Cookie Configuration

**In `youface.py`, configure secure cookies:**
```python
app.config['SESSION_COOKIE_SECURE'] = True  # Only send cookies over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to cookies
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Prevent CSRF attacks
```

**Note:** `SESSION_COOKIE_SECURE = True` only works with HTTPS. For local development, set it to `False`.

### 4.3 Input Validation

Add validation for user inputs:

**Email validation** - Already done with `type="email"` in HTML, but add server-side check:
```python
import re

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
```

**Username validation** - Prevent special characters:
```python
def is_valid_username(username):
    # Allow only letters, numbers, and underscores, 3-20 characters
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return re.match(pattern, username) is not None
```

**Password strength** - Require minimum length:
```python
def is_strong_password(password):
    # At least 8 characters, one uppercase, one lowercase, one number
    if len(password) < 8:
        return False
    if not any(char.isupper() for char in password):
        return False
    if not any(char.islower() for char in password):
        return False
    if not any(char.isdigit() for char in password):
        return False
    return True
```

Add these checks in `handlers/login.py` before creating users.

### 4.4 Rate Limiting

Prevent brute force attacks by limiting login attempts.

**Install Flask-Limiter:**
```bash
pip install Flask-Limiter
```

**In `youface.py`:**
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

**In `handlers/login.py`, add to login route:**
```python
@blueprint.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # Only 5 login attempts per minute
def login():
    # ... rest of function
```

---

## Testing Your Security Fixes

### Test Password Hashing
1. Create a new user
2. Check `db.json` - password should look like: `pbkdf2:sha256:600000$...`
3. Log out and log back in - should work
4. Try logging in with wrong password - should fail

### Test Session Management
1. Log in
2. Open browser developer tools → Application/Storage → Cookies
3. You should see a `session` cookie (not `username` or `password`)
4. Log out and check that the session cookie is cleared

### Test CSRF Protection
1. Try submitting a form without the CSRF token
2. You should get a `400 Bad Request` or CSRF error
3. With the token, forms should work normally

---

## Summary Checklist

- [ ] Install Werkzeug (already included with Flask)
- [ ] Update `db/users.py` to hash passwords
- [ ] Delete or reset `db.json`
- [ ] Update `handlers/login.py` to use sessions instead of cookies
- [ ] Update `handlers/friends.py`, `handlers/posts.py`, `handlers/profile.py` to use sessions
- [ ] Install Flask-WTF: `pip install Flask-WTF`
- [ ] Enable CSRF protection in `youface.py`
- [ ] Add CSRF tokens to all forms in templates
- [ ] Test everything works!

---

## Need Help?

If you run into issues:
1. Check the Flask error messages carefully
2. Make sure you deleted/reset `db.json` after implementing password hashing
3. Verify all forms have CSRF tokens
4. Check that you're using `session['username']` instead of cookies everywhere

Good luck with your security improvements! 🔒

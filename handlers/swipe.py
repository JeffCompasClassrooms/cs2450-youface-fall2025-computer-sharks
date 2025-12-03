from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for 
# Assume you import necessary db functions:
from db.users import get_unseen_candidates, get_user_by_name
from db.matches import save_match, check_mutual_like, get_matches_for_user

swipe_bp = Blueprint("swipe", __name__)

# handlers/swipe.py

@swipe_bp.route("/swipe")
def swipe():
    # 1. Get the current user from the session
    current_user_data = session.get("user")
    if not current_user_data:
        # Redirect to login if user not logged in
        return redirect(url_for('login.login_page')) 

    current_username = current_user_data["username"]

    # 2. Get a list of candidates the user has NOT yet swiped on (UNSEEN)
    # This function is crucial and needs to be created/updated in db/users.py
    candidates = get_unseen_candidates(current_username)
    FALLBACK_CANDIDATE = {
        "username": "Gus the Ghost",
        "age": "???",
        "bio": "I haunt the swipe deck. Check back later!",
        "profile_pic": url_for('static', filename='images/placeholder_ghost.png')
    }
    
    # Check if we have a candidate to show
    if not candidates:
        # Pass only the first candidate to the template for the top card
        candidates = [FALLBACK_CANDIDATE]

    # We only render the page with ONE candidate at a time for the single-card swipe
    return render_template("swipe.html", user=current_user_data, candidate=next_candidate)


@swipe_bp.route("/swipe", endpoint="swipe_page")
def swipe_action():
    # Use request.json (standard for Flask with application/json data)
    data = request.json
    
    # Validate required data fields
    if not data or 'user_id' not in data or 'action' not in data:
        return jsonify({"status": "error", "message": "Missing action or user_id"}), 400

    liker_username = session["user"]["username"]
    target_username = data["user_id"] # Matches the data-user-id from swipe.js
    action = data["action"] # 'like' or 'dislike'

    is_match = False
    
    # 1. Process the Action
    if action == "like":
        # Save the like action in the database
        save_match(liker_username, target_username, action="like") 
        
        # 2. Check for a Mutual Match (The Core Logic)
        # We check if the target user previously liked the current user (liker)
        if check_mutual_like(target_username, liker_username):
            is_match = True
            # Optional: You might want to save a formal 'MATCH' record here
            # save_match(liker_username, target_username, action="match") 

    elif action == "dislike":
        # Save the dislike action (optional, but good for not reshowing the user)
        save_match(liker_username, target_username, action="dislike")
        
    else:
        return jsonify({"status": "error", "message": "Invalid action"}), 400

    # 3. Return Response to JavaScript
    if is_match:
        # Respond with success and match status
        return jsonify({
            "status": "success",
            "action": action,
            "match": True,
            "match_user_name": target_username 
        })
    else:
        # Respond with success and no match status
        return jsonify({
            "status": "success",
            "action": action,
            "match": False
        })


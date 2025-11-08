from flask import Blueprint, jsonify, g, request, send_from_directory, current_app
from profile.connector import ProfileConnector
from auth.routes import token_required
import os

bp = Blueprint("profile", __name__, url_prefix="/api/profile")
pc = ProfileConnector()

# ------------------------
# Get User Details
# ------------------------
@bp.get("")
@token_required
def user_details():
    """Returns current user's details."""
    try:
        email = g.current_user.get("sub")
        info = pc.get_user_details(email)

        # Convert profile image path to a URL if present
        if info and info.get("ProfileImgPath"):
            info["ProfileImgURL"] = f"/api/profile/images/{os.path.basename(info['ProfileImgPath'])}"
        return jsonify({"info": info}), 200
    except Exception as e:
        print(f"Error in user_details: {e}")
        return jsonify({"error": "Something went wrong"}), 500


# ------------------------
# Update Profile Image
# ------------------------
@bp.post("/update-image")
@token_required
def update_profile_image():
    """Updates the current user's profile image."""
    try:
        email = g.current_user.get("sub")
        if "image" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["image"]

        # Basic validation
        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        # Save the file to your user images folder
        UPLOAD_FOLDER = os.path.join(current_app.root_path, "static/profile_images/")
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        safe_filename = file.filename  # optional: secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, safe_filename)
        file.save(file_path)

        # Update database (store only filename)
        pc.update_profile_image(email, safe_filename)

        file_url = f"/api/profile/images/{safe_filename}"
        return jsonify({"message": "Profile image updated", "url": file_url}), 200

    except Exception as e:
        print(f"Error in update_profile_image: {e}")
        return jsonify({"error": "Something went wrong"}), 500


# ------------------------
# Serve User Images
# ------------------------
@bp.get("/images/<filename>")
def serve_user_image(filename):
    """Serve profile images."""
    try:
        UPLOAD_FOLDER = os.path.join(current_app.root_path, "static/profile_images/")
        print(UPLOAD_FOLDER)
        return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        print(f"Error serving image {filename}: {e}")
        return jsonify({"error": "Image not found"}), 404

#Update User Password
@bp.post("/update-password")
@token_required
def update_password():
    """Updates the current user's password"""
    try:
        email = g.current_user.get("sub")
        data = request.get_json(silent=True) or request.form
        new_password = data.get("new_password")
        old_password = data.get("old_password")

        if not new_password:
            return jsonify({"error": "No new password provided"}), 400
        
        if not old_password:
            return jsonify({"error": "Old password not provided"}), 400

        if pc.update_user_password(email, old_password, new_password) == False:
            return jsonify({"error": "Old password is incorrect"}), 400
        
        return jsonify({"message": "Password updated successfully"}), 200
    except Exception as e:
        print(f"Error in update_password: {e}")
        return jsonify({"error": "Something went wrong"}), 500
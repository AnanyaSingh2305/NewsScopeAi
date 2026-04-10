from flask import Blueprint, request, jsonify, session

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')
    
    if username and password:
        # Mock validation
        session['user'] = username
        return jsonify({"success": True, "token": "mock-jwt-token-12345", "user": username})
        
    return jsonify({"success": False, "message": "Invalid credentials"}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({"success": True, "message": "Logged out successfully"})

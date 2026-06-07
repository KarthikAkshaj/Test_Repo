"""Authentication routes: register and login."""

from flask import Blueprint, request, jsonify, current_app

from ..models.user import User
from ..utils.auth import hash_password, verify_password, generate_token
from ..utils.validators import validate_email, validate_password
from ..utils.db import db, safe_commit

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user account."""
    data = request.get_json(silent=True) or {}

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()

    email_err = validate_email(email)
    if email_err:
        return jsonify({'error': email_err}), 400

    password_err = validate_password(password)
    if password_err:
        return jsonify({'error': password_err}), 400

    if not full_name:
        return jsonify({'error': 'Full name is required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'An account with that email already exists'}), 409

    user = User(
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
    )
    db.session.add(user)
    err = safe_commit()
    if err:
        current_app.logger.error('Register commit failed: %s', err)
        return jsonify({'error': 'Could not create account'}), 500

    token = generate_token(user.id, user.role)
    return jsonify({'token': token, 'user': user.to_dict()}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate a user and return a JWT."""
    data = request.get_json(silent=True) or {}

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email, is_active=True).first()
    if not user or not verify_password(password, user.password_hash):
        return jsonify({'error': 'Invalid email or password'}), 401

    token = generate_token(user.id, user.role)
    return jsonify({'token': token, 'user': user.to_dict()}), 200

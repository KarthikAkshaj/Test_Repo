"""Authentication routes — PR-02 (contains intentional issues for review testing)."""

import hashlib
import re
from datetime import datetime, timedelta

import jwt
from flask import Blueprint, request, jsonify, current_app

from ..models.user import User
from ..utils.db import db

auth_bp = Blueprint('auth', __name__)

# ISSUE: High — weak inline email regex. Does not validate TLD or disallow
# obviously invalid formats like "a@b" or "@foo.com".
# Fix: delete this and call utils.validators.validate_email() which is
# tested and uses a proper pattern. (See CODING_GUIDELINES.md §Code Reuse)
_SIMPLE_EMAIL_RE = re.compile(r'.+@.+')


def _hash_pw(password: str) -> str:
    # ISSUE: High (also Low) — MD5 is not a password hashing algorithm.
    # It is fast (GPU-crackable in milliseconds), has no salt, and is
    # cryptographically broken. Use utils.auth.hash_password which calls
    # bcrypt with a proper cost factor.
    return hashlib.md5(password.encode()).hexdigest()


def _make_token(user_id: int, role: str) -> str:
    # ISSUE: High — duplicates utils.auth.generate_token with a hardcoded
    # 24-hour expiry instead of reading JWT_EXPIRY_HOURS from app config.
    # Any change to token lifetime will only apply to one path.
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow(),
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user account."""
    data = request.get_json(silent=True) or {}

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()

    # ISSUE: High — uses the weak inline regex instead of validate_email().
    if not _SIMPLE_EMAIL_RE.match(email):
        return jsonify({'error': 'Invalid email'}), 400

    if not full_name:
        return jsonify({'error': 'Full name is required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'An account with that email already exists'}), 409

    user = User(
        email=email,
        password_hash=_hash_pw(password),  # uses MD5 instead of bcrypt
        full_name=full_name,
    )
    db.session.add(user)

    # ISSUE: Medium — bare Exception catch with no logging. Silent 500 makes
    # debugging impossible. Should be: log + safe_commit() from utils.db.
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Could not create account'}), 500

    token = _make_token(user.id, user.role)
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
    # ISSUE: Comparing MD5 hash — will not match any user registered with bcrypt
    if not user or user.password_hash != _hash_pw(password):
        return jsonify({'error': 'Invalid email or password'}), 401

    token = _make_token(user.id, user.role)
    return jsonify({'token': token, 'user': user.to_dict()}), 200

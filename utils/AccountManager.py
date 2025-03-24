import json
import os
import hashlib

USERS_FILE = 'users.json'

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_account(username, password):
    users = load_users()
    if username in users:
        return False  # Username already exists
    # Store the user record as a dictionary so that you can add more fields later.
    users[username] = {
        'password': hash_password(password),
        # Later you can add more keys, e.g., a spending dictionary:
        # 'monthly_spend': {},
        # 'training_samples': []
    }
    save_users(users)
    return True

def authenticate(username, password):
    users = load_users()
    hashed = hash_password(password)
    user_record = users.get(username)
    if not user_record:
        return False
    # Now compare the stored password field with the hashed value.
    return user_record.get('password') == hashed

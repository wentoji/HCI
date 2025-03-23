current_user = None

def set_user(username):
    global current_user
    current_user = username

def get_user():
    return current_user

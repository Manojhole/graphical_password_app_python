import os
import json
import sqlite3

USER_DATA_DIR = "user_data"
os.makedirs(USER_DATA_DIR, exist_ok=True)

def save_graphical_password(user_mobile, app_name, image_ids, hint):
    user_file = os.path.join(USER_DATA_DIR, f"{user_mobile}.json")
    
    if os.path.exists(user_file):
        with open(user_file, "r") as f:
            data = json.load(f)
    else:
        data = {}

    # Save both image_ids and hint for the app
    data[app_name] = {
        "image_ids": image_ids,
        "hint": hint
    }

    with open(user_file, "w") as f:
        json.dump(data, f)

def get_password_for_app(user_mobile, app_name):
    user_file = os.path.join(USER_DATA_DIR, f"{user_mobile}.json")
    if os.path.exists(user_file):
        with open(user_file, "r") as f:
            data = json.load(f)
            app_data = data.get(app_name)
            if app_data:
                return app_data.get("image_ids")
    return None

def get_hint_for_app(user_mobile, app_name):
    user_file = os.path.join(USER_DATA_DIR, f"{user_mobile}.json")
    if os.path.exists(user_file):
        with open(user_file, "r") as f:
            data = json.load(f)
            app_data = data.get(app_name)
            if app_data:
                return app_data.get("hint")
    return None

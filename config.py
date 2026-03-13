import os
from dotenv import load_dotenv

# Load environment variables from .env file, overriding any existing ones
load_dotenv(override=True)

# Discord Bot Token
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Authorized Discord User IDs (Comma-separated list in .env)
# Only these users will be allowed to execute commands
AUTHORIZED_USERS = []
auth_users_env = os.getenv("AUTHORIZED_USERS", "")
if auth_users_env:
    for user_id in auth_users_env.split(","):
        user_id = user_id.strip()
        if user_id.isdigit():
            AUTHORIZED_USERS.append(int(user_id))

def is_authorized(user_id):
    """Check if a User ID is authorized to use the bot."""
    # If no users are configured, deny all requests for safety.
    if not AUTHORIZED_USERS:
        print("Warning: No authorized users configured in .env.")
        return False
    return user_id in AUTHORIZED_USERS

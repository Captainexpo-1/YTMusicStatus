import os
from slack_sdk import WebClient
import dotenv
from typing import Dict

dotenv.load_dotenv(override=True)

SLACK_TOKEN = os.environ.get("SLACK_OAUTH")

client = WebClient(token=SLACK_TOKEN)

def set_song(song_data: Dict[str, str]):
    
    song_name = song_data["title"]
    
    PREFIX = "Listening to "
    SUFFIX = f" by {song_data['channel']}"
    if len(PREFIX + song_name + SUFFIX) > 100:
        song_name = song_name[:95 - len(PREFIX + SUFFIX)] + "..."
        
    custom_status = {
        "status_text": PREFIX + song_name + SUFFIX,  # Text of the status
        "status_emoji": os.environ.get("SLACK_EMOJI", ":music:"),  # Emoji to display
        "status_expiration": 0  # Set to 0 for no expiration
    }
    set_status(custom_status)
    
def remove_status():
    custom_emoji, custom_text = os.environ.get("DEFAULT_STATUS", "|").split("|")
    set_status(
        {
            "status_text": custom_text,  # Text of the status
            "status_emoji": custom_emoji,  # Emoji to display
            "status_expiration": 0  # Set to 0 for no expiration
        }
    )    
    
def set_status(status: Dict[str, str|int]):
    try:
        result = client.users_profile_set(
            user=os.environ.get("SLACK_USER_ID"),  # Replace with your Slack user ID
            profile=status
        )

        if result["ok"]:
            print("Slack status updated successfully!")
        else:
            print(f"Error updating status: {result['error']}")

    except Exception as e:
        print(f"An error occurred: {e}")
    
import os
from slack_sdk import WebClient
import dotenv
from typing import Dict

dotenv.load_dotenv(override=True)

SLACK_TOKEN = os.environ.get("SLACK_OAUTH")

client = WebClient(token=SLACK_TOKEN)

def set_song(song_name: str):
    custom_status = {
        "status_text": f"Listening to {song_name}",  # Text of the status
        "status_emoji": ":music:",  # Emoji to display
        "status_expiration": 0  # Set to 0 for no expiration
    }
    set_status(custom_status)
    
def remove_status():
    set_status(
        {
            "status_text": "",  # Text of the status
            "status_emoji": "",  # Emoji to display
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
    
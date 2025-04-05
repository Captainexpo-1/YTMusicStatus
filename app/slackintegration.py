import os
from slack_sdk import WebClient
import dotenv
from typing import Dict
import asyncio
import logging

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
waiting_to_set_status = False
def set_status(status: Dict[str, str|int]):
    global waiting_to_set_status
    try:
        result = client.users_profile_set(
            user=os.environ.get("SLACK_USER_ID"),  # Replace with your Slack user ID
            profile=status
        )

        if result["ok"]:
            logging.info("Status updated successfully")
        else:
            logging.info(f"Error updating status: {result['error']}")

    except Exception as e:
        if "ratelimited" in str(e): 
            if waiting_to_set_status:
                return
            logging.info("Rate limit exceeded. Trying again in 5 seconds...")
            waiting_to_set_status = True
            asyncio.sleep(5)
            waiting_to_set_status = False
            set_status(status)
        else:
            logging.info(f"An unknown error occurred: {e}")
    
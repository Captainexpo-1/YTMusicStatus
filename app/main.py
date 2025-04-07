from pypresence_patch import Presence
import time
import json
import websockets
import asyncio
import dotenv
import os
import slackintegration
import logging

class PresenceStopException(Exception):
    pass

dotenv.load_dotenv(override=True)

ENABLE_SLACK = os.environ.get("ENABLE_SLACK", "0") == "1"
LOG_FILE = os.environ.get("LOG_FILE", "app.log")  # Default log file if not specified
CLIENT_ID = os.environ["CLIENT_ID"]

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    filemode='w',
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

connection_start = time.time()

current_song_url = "" 

current_rpc = None

async def stop_status():
    global current_song_url
    current_song_url = ""
    if ENABLE_SLACK:
        await slackintegration.remove_status()
    await asyncio.to_thread(current_rpc.clear)
    
def connect_rpc():
    global connection_start, current_rpc
    while True:
        try:
            rpc = Presence(CLIENT_ID) 
            rpc.connect()
            current_rpc = rpc
            logging.info("Connected to Discord Rich Presence.")
            connection_start = time.time()
            return rpc
        except Exception as e:
            logging.error("Failed to connect to Discord Rich Presence. Retrying in 5 seconds...")
            logging.exception(e)
            asyncio.run(stop_status())
            time.sleep(5)

rpc = connect_rpc()

def format_time(seconds: int):
    # return formatted time in HH:MM:SS
    
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

do_update = True
async def handler(websocket):
    global current_song_url, do_update
    async for message in websocket:
        data = json.loads(message)
        try:
            match data.get("event", ""):
                case "song":
                    if data.get("paused", False) and do_update:
                        do_update = False
                        await stop_status()
                        logging.info("Paused, skipping update.")
                        continue
                    elif not data.get("paused", False) and not do_update:
                        do_update = True
                    if not do_update:
                        logging.info("Skipping update due to paused status.")
                        continue
                    await asyncio.to_thread(
                        rpc.update,
                        details=f"{data['title']}",
                        state=f"by {data['channel']}",
                        large_image="ytmusic",
                        large_text=f"{format_time(int(data['progress']['total']))} long",  # Duration of the track
                        start=int(time.time()) - int(data['progress']['current']),  # Start time for the track
                        buttons = [
                            {"label": "Play on YouTube Music", "url": data["url"]},
                        ],
                        activity_type=2,
                    )
                    if data.get("url", "") == current_song_url:
                        logging.info("Ignoring duplicate song URL.")
                        continue
                    if ENABLE_SLACK:
                        await slackintegration.set_song(data)
                    current_song_url = data.get("url", "")
                case "close":
                    if rpc:
                        await asyncio.to_thread(rpc.clear)
                        logging.info("Cleared Discord Rich Presence.")
                    else:
                        logging.warning("RPC is not initialized. Skipping clear operation.")
                    await stop_status()
                    raise PresenceStopException()
                case _:
                    logging.warning("Unknown event type.")
        except BrokenPipeError as e:
            await stop_status()
            logging.error("Connection broken, unable to update Discord Rich Presence.")
            logging.exception(e)

async def start_server():
    global connection_start
    while True:
        try:
            async with websockets.serve(handler, "localhost", 54545):
                logging.info("WebSocket server started.")
                connection_start = time.time()
                await asyncio.Future()
        except Exception as e:
            logging.error("WebSocket server encountered an error. Retrying in 5 seconds...")
            logging.exception(e)
            await stop_status()
            await asyncio.sleep(5)
        except PresenceStopException:
            logging.info("Presence stopped by client.")
            connection_start = 0
            await stop_status()
            break

asyncio.run(start_server())

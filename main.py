import pypresence
from pypresence import Presence
import time
import json
import websockets
import asyncio
import dotenv
import os
import slackintegration

class PresenceStopException(Exception):
    pass

print(pypresence.__file__)

dotenv.load_dotenv(override=True)

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]

connection_start = time.time()

current_song_url = "" 

def panic():
    if os.environ.get("ENABLE_SLACK", "0") == "1":
        slackintegration.remove_status()

def connect_rpc():
    global connection_start
    while True:
        try:
            rpc = Presence(CLIENT_ID) 
            rpc.connect()
            print("Connected to Discord Rich Presence.")
            connection_start = time.time()
            return rpc
        except Exception as e:
            print("Failed to connect to Discord Rich Presence. Retrying in 5 seconds...")
            print(e)
            panic()
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

async def handler(websocket):
    global current_song_url
    async for message in websocket:
        data = json.loads(message)
        print("Received:", data)
        if data.get("url", "") == current_song_url:
            print("Ignoring duplicate song URL.")
            continue
        current_song_url = data.get("url", "")
        try:
            if data.get("type", "") == "close":
                if rpc:
                    await asyncio.to_thread(rpc.clear)
                    print("Cleared Discord Rich Presence.")
                else:
                    print("RPC is not initialized. Skipping clear operation.")
                panic()
                raise PresenceStopException()
    
            await asyncio.to_thread(
                rpc.update,
                details=f"{data['title']}",
                state=f"by {data['channel']}",
                large_image="ytmusic",
                large_text=f"{format_time(int(data['progress']['total']))} long",  # Duration of the track
                start=int(time.time()) - int(data["progress"]["current"]),  # Start time for the track
                buttons = [
                    {"label": "Play on YouTube Music", "url": data["url"]},
                ],
                activity_type=2,
            )
            
            if os.environ.get("ENABLE_SLACK", "0") == "1":
                slackintegration.set_song(data['title'])

        except BrokenPipeError as e:
            panic()
            print("Connection broken, unable to update Discord Rich Presence.")
            print(e)

async def start_server():
    global connection_start
    while True:
        try:
            async with websockets.serve(handler, "localhost", 54545):
                print("WebSocket server started.")
                connection_start = time.time()
                await asyncio.Future()
        except Exception as e:
            print("WebSocket server encountered an error. Retrying in 5 seconds...")
            print(e)
            panic()

            await asyncio.sleep(5)
        except PresenceStopException:
            print("Presence stopped by client.")
            connection_start = 0
            panic()
            break
            

asyncio.run(start_server())

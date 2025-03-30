# YT Music Discord & Slack Integration

This repo contains both an extension and a simple script to integrate YT Music with Discord and Slack.

## Installation

1. Clone the repo
2. Install the extension in your browser (currently it only supports Firefox) by going to `about:debugging#/runtime/this-firefox` and clicking on "Load Temporary Add-on". Select the [manifest.json](YTMusicExtension/manifest.json) file.
3. Verify that it works by going to [YT Music](https://music.youtube.com), playing a song, and then clicking on the extension icon. You should see a popup with the current song information.
5. Set up the `.env` file (see [Env Setup](#env-setup)).
4. To use the script, run `python3 ./app/main.py`

### Env Setup

Copy the `.env.example` file to `.env`

```bash
cp .env.example .env
```

Then fill in the required environment variables in the `.env` file. 
You can find the required variables in the `.env.example` file. If you want to disable the slack integration, you can set `ENABLE_SLACK` to `0`.

Besides that, if you want to only use discord, no changes to the `.env` are needed.


## Using the Api

When the extension is active and a YT music tab is open, it starts a websocket server on port 54545. 

There are two possible payloads from the extension:

1. The current song information
```js
{
    "event": "song"
    "title": str, 
    "progress": {
        "current": int, 
        "total": int
    }, 
    "channel": str, 
    "url": str
}
```

2. A close event when YT Music is closed
```js
{
    "event": "close"
}
```

The provided script in `app/main.py` just listens to the websocket and send the current song information to Discord and Slack (if enabled). 

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.


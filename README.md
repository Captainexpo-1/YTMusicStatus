# YT Music Discord & Slack Integration

Easily integrate YT Music with Discord and Slack using this repository, which includes both a browser extension and a Python script.

---

## Features

### Discord Integration
![Discord](https://hc-cdn.hel1.your-objectstorage.com/s/v3/34d69cfa0a29457dcde7bd486a180ea554802e63_image.png)

### Slack Integration
![Slack](https://hc-cdn.hel1.your-objectstorage.com/s/v3/445f26f8463bd792a01fc9e8f0d965b0eebb216d_image.png)

---

## Installation

### 1. Clone the Repository
```bash
git clone "https://github.com/Captainexpo-1/YTMusicDiscordIntegration"
```

### 2. Install the Browser Extension
- Supported Browser: **Firefox**
- Steps:
    1. Navigate to `about:debugging#/runtime/this-firefox` in Firefox.
    2. Click on **"Load Temporary Add-on"**.
    3. Select the [manifest.json](YTMusicExtension/manifest.json) file.

- **Verification**:  
    Open [YT Music](https://music.youtube.com), play a song, and click the extension icon. A popup should display the current song information.

### 3. Set Up the `.env` File
- Copy the example file:
    ```bash
    cp .env.example .env
    ```
- Fill in the required environment variables in `.env`.  
    - To disable Slack integration, set `ENABLE_SLACK=0`.
    - No changes are needed if only Discord integration is required.

### 4. Run the Script
```bash
python3 ./app/main.py
```

---

## Using the API

When the extension is active and a YT Music tab is open, a WebSocket server starts on port `54545`.

### Payloads

1. **Current Song Information**
     ```json
     {
             "event": "song",
             "title": "string",
             "progress": {
                     "current": "int",
                     "total": "int"
             },
             "channel": "string",
             "url": "string"
     }
     ```

2. **Close Event**
     ```json
     {
             "event": "close"
     }
     ```

The script in `app/main.py` listens to the WebSocket and sends the current song information to Discord and Slack (if enabled).

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.


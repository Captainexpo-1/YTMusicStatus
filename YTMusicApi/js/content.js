function parseTime(timeStr) {
    let s = 0;
    timeStr
        .split(":")
        .reverse()
        .forEach((v, i) => (s += parseInt(v) * Math.pow(60, i)));

    return s;
}

function getSongInfo() {
    const title = document.querySelector(
        ".middle-controls>.content-info-wrapper>yt-formatted-string.title",
    );
    let progress = document.querySelector("span.time-info");
    const channel = document.querySelector(
        ".content-info-wrapper>.byline-wrapper>span.subtitle>yt-formatted-string",
    ).childNodes[0];

    if (progress) {
        progress = progress.textContent.replace(/\s+/g, "").split("/");
        if (progress.length != 2) {
            progress = {
                current: 0,
                total: 0,
            };
        } else {
            progress = {
                current: parseTime(progress[0]),
                total: parseTime(progress[1]),
            };
        }
    } else {
        progress = {
            current: 0,
            total: 0,
        };
    }

    return {
        title:
            title && title.textContent.length > 0
                ? title.textContent
                : "<unknown>",
        progress,
        channel: channel ? channel.textContent : "<unknown>",
        url: window.location.href,
    };
}

function sendToBackground(songData) {
    if (!songData) return;
    console.log("sending to background:", songData);
    chrome.runtime.sendMessage({ type: "updateSong", info: songData });
}

function updateSong() {
    const info = getSongInfo();
    if (info.title == "Il Mondo" && info.channel == "Engelbert Humperdinck")
        return;
    sendToBackground(info);
    sendToSocket(info);
}

setInterval(updateSong, 1000);

let socket;

function newSocket() {
    socket = new WebSocket("ws://localhost:54545");

    socket.addEventListener("error", (err) => {
        console.error("WebSocket error:", err);
        setTimeout(newSocket, 5000); // Try to reconnect after 5 seconds
    });

    socket.addEventListener("close", () => {
        console.warn("WebSocket connection closed.");
        setTimeout(newSocket, 5000); // Try to reconnect after 5 seconds
    });
}

function sendToSocket(songData) {
    if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify(songData));
    } else {
        console.warn("WebSocket not open. Retrying connection...");
        newSocket();
    }
}

newSocket();

window.addEventListener("beforeunload", () => {
    if (socket.readyState === WebSocket.OPEN) {
        socket.send('{"type":"close"}');
    }
    socket.close();
});

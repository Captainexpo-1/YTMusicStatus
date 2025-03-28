let latestSongInfo = null;

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.type === "updateSong") {
        latestSongInfo = msg.info;
    } else if (msg.type === "getLatestSong") {
        sendResponse(latestSongInfo);
    }
});

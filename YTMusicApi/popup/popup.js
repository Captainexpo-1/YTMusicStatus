function getCurrentTabInfo() {
    chrome.runtime.sendMessage({ type: "getLatestSong" }, (response) => {
        if (response && response.title) {
            document.getElementById("song").textContent =
                `${response.title} - ${response.channel}`;
        } else {
            document.getElementById("song").textContent =
                "No song data available.";
        }
    });
}

getCurrentTabInfo();

let video = document.getElementById('video');
let isStreaming = false;
let socket;
let frameInterval;

// Open WebSocket connection
function openSocket() {
    socket = new WebSocket('ws://192.168.17.170:8000/ws');

    socket.onopen = () => {
        console.log('WebSocket connecti on established');
        streamFrames(); // Start streaming frames once connected
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);

        // Trim everything after an underscore for each prediction
        const trimmedData = data.map(item => item.split('_')[0]);

        document.getElementById('result-box').innerText = `Prediction: ${trimmedData.join(', ')}`;
        console.log(trimmedData);
    };

    socket.onerror = (error) => {
        console.error('WebSocket Error:', error);
        document.getElementById('result-box').innerText = 'Error with WebSocket connection';
    };

    socket.onclose = () => {
        console.log('WebSocket connection closed');
    };
}

// Start webcam and stream frames
function startWebcam() {
    if (!isStreaming) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => {
                video.srcObject = stream;
                isStreaming = true;
                openSocket();
            })
            .catch(err => console.error('Error accessing webcam:', err));
    }
}

// Stop webcam and streaming
function stopWebcam() {
    if (isStreaming) {
        let stream = video.srcObject;
        let tracks = stream.getTracks();

        tracks.forEach(track => track.stop());
        video.srcObject = null;
        isStreaming = false;

        clearInterval(frameInterval);

        if (socket) {
            socket.close();
        }
    }
}

// Capture video frame and send it as Uint8Array
function captureAndSendFrame() {
    let canvas = document.createElement('canvas');
    let ctx = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(async (blob) => {
        let arrayBuffer = await blob.arrayBuffer();
        let uint8Array = new Uint8Array(arrayBuffer);
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(uint8Array);
        }
    }, 'image/jpeg', 0.8);
}

// Send frames at 30 FPS using WebSocket
function streamFrames() {
    frameInterval = setInterval(() => {
        if (isStreaming) {
            captureAndSendFrame();
        }
    }, 1000 / 30); // 30 FPS
}

// Dark Theme Logic
document.addEventListener("DOMContentLoaded", () => {
    const themeToggle = document.getElementById("theme-toggle");
    if (themeToggle) {
        let darkMode = localStorage.getItem("darkMode") === "true";

        function applyTheme() {
            document.documentElement.setAttribute("data-theme", darkMode ? "dark" : "light");
            themeToggle.textContent = darkMode ? "☀️" : "🌙";
        }

        themeToggle.addEventListener("click", () => {
            darkMode = !darkMode;
            localStorage.setItem("darkMode", darkMode);
            applyTheme();
        });

        applyTheme();
    }
});

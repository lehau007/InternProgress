document.addEventListener('DOMContentLoaded', function() {
    const recordButton = document.getElementById('recordButton');
    const recordingStatus = document.getElementById('recordingStatus');
    const timer = document.getElementById('timer');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const transcriptionResult = document.getElementById('transcriptionResult');
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    let startTime;
    let timerInterval;
    function updateTimer() {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        const minutes = String(Math.floor(elapsed / 60)).padStart(2, '0');
        const seconds = String(elapsed % 60).padStart(2, '0');
        timer.textContent = `${minutes}:${seconds}`;
    }
    function startTimer() {
        startTime = Date.now();
        timerInterval = setInterval(updateTimer, 1000);
        updateTimer();
    }
    function stopTimer() {
        clearInterval(timerInterval);
        timer.textContent = '00:00';
    }
    recordButton.addEventListener('click', async function() {
        if (!isRecording) {
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                alert('Your browser does not support audio recording.');
                return;
            }
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];
                mediaRecorder.ondataavailable = function(e) {
                    audioChunks.push(e.data);
                };
                mediaRecorder.onstop = function() {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                    sendAudio(audioBlob);
                };
                mediaRecorder.start();
                isRecording = true;
                recordButton.classList.add('recording');
                recordButton.querySelector('.btn-text').textContent = 'Stop Recording';
                recordingStatus.textContent = 'Recording...';
                startTimer();
            } catch (err) {
                alert('Could not start recording: ' + err.message);
            }
        } else {
            mediaRecorder.stop();
            isRecording = false;
            recordButton.classList.remove('recording');
            recordButton.querySelector('.btn-text').textContent = 'Start Recording';
            recordingStatus.textContent = 'Not recording';
            stopTimer();
        }
    });
    function sendAudio(audioBlob) {
        loadingIndicator.classList.remove('hidden');
        transcriptionResult.innerHTML = '<p class="placeholder">Processing...</p>';
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');
        fetch('/transcribe/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            loadingIndicator.classList.add('hidden');
            if (data.success) {
                transcriptionResult.innerHTML = `<p>${data.transcription}</p>`;
            } else {
                transcriptionResult.innerHTML = `<p class="placeholder">Error: ${data.error}</p>`;
            }
        })
        .catch(err => {
            loadingIndicator.classList.add('hidden');
            transcriptionResult.innerHTML = `<p class="placeholder">Error: ${err.message}</p>`;
        });
    }
});

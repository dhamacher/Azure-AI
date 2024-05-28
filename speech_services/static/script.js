let mediaRecorder;
  let chunks = [];
  
  document.getElementById('stopButton').addEventListener('click', function() {
      mediaRecorder.stop();
      mediaRecorder.stream.getTracks().forEach(track => track.stop());
  });

  document.getElementById('startButton').addEventListener('click', function() {
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => {
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.start();

        mediaRecorder.ondataavailable = e => {
          chunks.push(e.data);
        };

        mediaRecorder.onstop = e => {
          let blob = new Blob(chunks, { 'type' : 'audio/wav; codecs=0' });
          chunks = [];
          let formData = new FormData();
          formData.append('file', blob);

          fetch('/audio', {
            method: 'POST',
            body: formData
          }).then(response => response.json())
          .then(data => { document.getElementById('recognizedText').innerText = data; });
        };
      });
      
      let progressBar = document.getElementById('progressBar');
      progressBar.value = 0;
      let intervalId = setInterval(function() {
          progressBar.value += 1;
          if (progressBar.value >= 30) {
              clearInterval(intervalId);
          }
      }, 1000);  // Update every second

      // setTimeout(function() {
      //     mediaRecorder.stop();
      // }, 30000);  // Stop recording after 30 seconds
  });
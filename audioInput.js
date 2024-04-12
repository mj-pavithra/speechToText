const { createApp, ref } = Vue;

const app = createApp({
    setup() {
        const audioFile = ref(null);
        const audioUrl = ref('');
        const audioElement = ref(null); // Reference to the audio element
        const transcription = ref('');
        const utterances = ref([]);
        const waiting = ref(false); // Flag to indicate if waiting for response
        const currentTime = ref(0); // Current time of the audio playback
        const highlightedWords = ref([]); // Array to store highlighted words

        function handleAudioUpload(event) {
            const files = event.target.files || event.dataTransfer.files;
            if (files.length > 0) {
                audioFile.value = files[0];
                audioUrl.value = URL.createObjectURL(audioFile.value);
                audioElement.value = new Audio(audioUrl.value);
            } else {
                audioFile.value = null;
                audioUrl.value = '';
                audioElement.value = null; 
            }
        }


        function synchronizeHighlighting(time) {
            highlightedWords.value = utterances.value.filter(utterance => {
                return utterance.end <= time;
            });
        }
        
        function syncHighlighting(event) {
            currentTime.value = event.target.currentTime;
            synchronizeHighlighting(currentTime.value);
        }

        function playAudio() {
            if (audioElement.value) {
                audioElement.value.play(); // Play the audio
            }
        }

        function isHighlighted(utterance) {
            return highlightedWords.value.includes(utterance);
        }

        function handleDragOver(event) {
            event.preventDefault(); // Necessary to allow the drop
        }

        function handleDrop(event) {
            handleAudioUpload(event); // Reuse the audio upload logic for dropped files
        }

        function triggerFileInput() {
            document.getElementById('fileInput').click(); // Programmatically click the hidden file input
        }

        async function submitAudio() {
            console.log('Submitting audio...');
            waiting.value = true; // Set waiting flag to true
            const formData = new FormData();
            formData.append('audio', audioFile.value);

            try {
                const csrfToken = getCookie('csrftoken'); 

                const response = await fetch('http://localhost:8000/getAudio/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken 
                    },
                    body: formData,
                });

                if (response.ok) {
                    const data = await response.json();
                    transcription.value = data.transcription;
                    utterances.value = data.utterances || [];

                    console.log('Transcription:', transcription.value);
                    utterances.value.forEach(utterance => {
                        console.log(`${utterance.word} [${utterance.start}-${utterance.end}] Confidence: ${utterance.confidence}`);
                    });
                } else {
                    console.error('Failed to transcribe audio file');
                    console.log(await response.text());
                }
            } catch (error) {
                console.error('Error transcribing audio file:', error);
            } finally {
                waiting.value = false; // Set waiting flag to false regardless of success or failure
            }
        }

        function getCookie(name) {
            const value = `; ${document.cookie}`;
            const parts = value.split(`; ${name}=`);
            if (parts.length === 2) return parts.pop().split(';').shift();
        }

        return { 
            audioFile, 
            handleAudioUpload, 
            submitAudio, 
            audioUrl, 
            transcription, 
            utterances, 
            handleDragOver, 
            handleDrop, 
            triggerFileInput, 
            waiting, // Add waiting to return object
            highlightedWords ,// Add highlightedWords to return object
            playAudio, // Add playAudio function
            isHighlighted, // Add isHighlighted function
            syncHighlighting // Add syncHighlighting function
        };
    },
});

app.mount('#audio-app');

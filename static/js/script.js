document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const recordBtn = document.getElementById('record-btn');
    const translateBtn = document.getElementById('translate-btn');
    const statusText = document.getElementById('status');
    const originalText = document.getElementById('original-text');
    const translatedText = document.getElementById('translated-text');
    const playOriginalBtn = document.getElementById('play-original');
    const playTranslationBtn = document.getElementById('play-translation');
    const audioPlayer = document.getElementById('audio-player');
    const inputLanguageSelect = document.getElementById('input-language');
    const outputLanguageSelect = document.getElementById('output-language');
    const swapLanguagesBtn = document.getElementById('swap-languages');
    
    // State variables
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    let originalAudioPath = null;
    let translatedAudioPath = null;
    
    // Initialize audio recording
    async function setupRecorder() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            
            mediaRecorder.ondataavailable = (e) => {
                audioChunks.push(e.data);
            };
            
            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                await sendAudioForTranslation(audioBlob);
                audioChunks = [];
            };
            
            return true;
        } catch (err) {
            console.error("Error accessing microphone:", err);
            statusText.textContent = "Error: Cannot access microphone";
            statusText.style.color = "red";
            return false;
        }
    }
    
    // Handle record button click
    recordBtn.addEventListener('click', async function() {
        if (!mediaRecorder) {
            statusText.textContent = "Initializing microphone...";
            const initialized = await setupRecorder();
            if (!initialized) return;
        }
        
        if (!isRecording) {
            // Start recording
            mediaRecorder.start();
            isRecording = true;
            recordBtn.classList.add('recording');
            recordBtn.innerHTML = '<i class="fas fa-stop"></i> Stop Recording';
            statusText.textContent = "Recording... Speak now";
            // Reset text displays
            originalText.value = "Recording...";
            translatedText.value = "Waiting for translation...";
            playOriginalBtn.disabled = true;
            playTranslationBtn.disabled = true;
        } else {
            // Stop recording
            mediaRecorder.stop();
            isRecording = false;
            recordBtn.classList.remove('recording');
            recordBtn.innerHTML = '<i class="fas fa-microphone"></i> Record Speech';
            statusText.textContent = "Processing...";
        }
    });
    
    // Handle text translation button click
    translateBtn.addEventListener('click', async function() {
        const text = originalText.value.trim();
        if (!text) {
            statusText.textContent = "Please enter some text to translate";
            return;
        }
        
        statusText.textContent = "Translating...";
        await translateTextInput(text);
    });
    
    // Send audio to backend for processing
    async function sendAudioForTranslation(audioBlob) {
        const formData = new FormData();
        formData.append('audio', audioBlob);
        formData.append('input_language', inputLanguageSelect.value);
        formData.append('output_language', outputLanguageSelect.value);
        
        try {
            statusText.textContent = "Processing speech...";
            const response = await fetch('/upload_audio', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Unknown error occurred');
            }
            
            const data = await response.json();
            
            // Update UI with recognition and translation results
            originalText.value = data.recognized_text;
            translatedText.value = data.translated_text;
            originalAudioPath = data.original_audio_path;
            translatedAudioPath = data.translated_audio_path;
            
            // Enable play buttons
            playOriginalBtn.disabled = false;
            playTranslationBtn.disabled = false;
            statusText.textContent = "Translation complete";
            
            // Add animation to the translated text
            translatedText.classList.add('fade-in');
            setTimeout(() => {
                translatedText.classList.remove('fade-in');
            }, 500);
            
        } catch (error) {
            console.error("Error during translation:", error);
            statusText.textContent = `Error: ${error.message}`;
            statusText.style.color = "red";
            setTimeout(() => {
                statusText.textContent = "Ready to translate";
                statusText.style.color = "";
            }, 3000);
        }
    }
    
    // Translate text input
    async function translateTextInput(text) {
        try {
            const response = await fetch('/translate_text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: text,
                    input_language: inputLanguageSelect.value,
                    output_language: outputLanguageSelect.value
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Unknown error occurred');
            }
            
            const data = await response.json();
            
            translatedText.value = data.translated_text;
            originalAudioPath = data.original_audio_path;
            translatedAudioPath = data.translated_audio_path;
            
            // Enable play buttons
            playOriginalBtn.disabled = false;
            playTranslationBtn.disabled = false;
            statusText.textContent = "Translation complete";
            
            // Add animation to the translated text
            translatedText.classList.add('fade-in');
            setTimeout(() => {
                translatedText.classList.remove('fade-in');
            }, 500);
            
        } catch (error) {
            console.error("Error during translation:", error);
            statusText.textContent = `Error: ${error.message}`;
            statusText.style.color = "red";
            setTimeout(() => {
                statusText.textContent = "Ready to translate";
                statusText.style.color = "";
            }, 3000);
        }
    }
    
    // Play original audio
    playOriginalBtn.addEventListener('click', function() {
        if (originalAudioPath) {
            playAudio(originalAudioPath, playOriginalBtn);
        }
    });
    
    // Play translation audio
    playTranslationBtn.addEventListener('click', function() {
        if (translatedAudioPath) {
            playAudio(translatedAudioPath, playTranslationBtn);
        }
    });
    
    // Helper function to play audio
    function playAudio(audioPath, button) {
        audioPlayer.src = audioPath;
        audioPlayer.play();
        
        // Visual feedback for playing
        const originalIcon = button.innerHTML;
        button.innerHTML = '<i class="fas fa-volume-up"></i>';
        button.disabled = true;
        
        audioPlayer.onended = () => {
            button.innerHTML = originalIcon;
            button.disabled = false;
        };
    }
    
    // Swap languages
    swapLanguagesBtn.addEventListener('click', function() {
        const inputValue = inputLanguageSelect.value;
        const outputValue = outputLanguageSelect.value;
        
        inputLanguageSelect.value = outputValue;
        outputLanguageSelect.value = inputValue;
        
        // If there's text in the boxes, auto-translate in the new direction
        const originalTextValue = originalText.value.trim();
        if (originalTextValue && originalTextValue !== "Recording...") {
            // First swap the text boxes
            const temp = originalText.value;
            originalText.value = translatedText.value;
            translatedText.value = temp;
            
            // Then translate if needed
            if (originalText.value.trim()) {
                setTimeout(() => {
                    translateTextInput(originalText.value);
                }, 100);
            }
        }
    });
    
    // Auto-translate when input text changes (with debounce)
    let typingTimer;
    originalText.addEventListener('input', function() {
        clearTimeout(typingTimer);
        if (originalText.value.trim()) {
            playOriginalBtn.disabled = true;
            playTranslationBtn.disabled = true;
            typingTimer = setTimeout(() => {
                translateTextInput(originalText.value);
            }, 1000); // 1 second delay
        }
    });
});
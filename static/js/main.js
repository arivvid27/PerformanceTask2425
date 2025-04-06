document.addEventListener('DOMContentLoaded', function() {
    // Tab switching functionality
    const textTabBtn = document.getElementById('textTabBtn');
    const speechTabBtn = document.getElementById('speechTabBtn');
    const textTranslationTab = document.getElementById('textTranslationTab');
    const speechTranslationTab = document.getElementById('speechTranslationTab');
    
    textTabBtn.addEventListener('click', function() {
        textTabBtn.classList.add('active-tab');
        speechTabBtn.classList.remove('active-tab');
        speechTabBtn.classList.add('bg-gray-300', 'text-gray-700');
        speechTabBtn.classList.remove('bg-blue-500', 'text-white');
        
        textTranslationTab.classList.remove('hidden');
        speechTranslationTab.classList.add('hidden');
    });
    
    speechTabBtn.addEventListener('click', function() {
        speechTabBtn.classList.add('active-tab');
        textTabBtn.classList.remove('active-tab');
        textTabBtn.classList.add('bg-gray-300', 'text-gray-700');
        textTabBtn.classList.remove('bg-blue-500', 'text-white');
        
        speechTranslationTab.classList.remove('hidden');
        textTranslationTab.classList.add('hidden');
    });
    
    // Text Translation
    const sourceText = document.getElementById('sourceText');
    const targetText = document.getElementById('targetText');
    const sourceLanguage = document.getElementById('sourceLanguage');
    const targetLanguage = document.getElementById('targetLanguage');
    const translateBtn = document.getElementById('translateBtn');
    const clearSourceBtn = document.getElementById('clearSource');
    const copyTargetBtn = document.getElementById('copyTarget');
    const detectLanguageBtn = document.getElementById('detectLanguage');
    const speakSourceBtn = document.getElementById('speakSource');
    const speakTargetBtn = document.getElementById('speakTarget');
    
    // Translate text function
    translateBtn.addEventListener('click', function() {
        if (!sourceText.value.trim()) {
            alert('Please enter text to translate');
            return;
        }
        
        translateBtn.disabled = true;
        translateBtn.innerHTML = '<div class="spinner"></div> Translating...';
        
        fetch('/api/translate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: sourceText.value,
                source_lang: sourceLanguage.value,
                target_lang: targetLanguage.value
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Translation error: ' + data.error);
            } else {
                targetText.value = data.translated_text;
                
                // If source language was auto-detected, update the dropdown
                if (!sourceLanguage.value && data.source_lang) {
                    for (let option of sourceLanguage.options) {
                        if (option.value === data.source_lang) {
                            option.selected = true;
                            break;
                        }
                    }
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to translate: ' + error.message);
        })
        .finally(() => {
            translateBtn.disabled = false;
            translateBtn.innerHTML = '<i class="fas fa-language mr-2"></i> Translate';
        });
    });
    
    // Clear source text
    clearSourceBtn.addEventListener('click', function() {
        sourceText.value = '';
        sourceText.focus();
    });
    
    // Copy target text
    copyTargetBtn.addEventListener('click', function() {
        if (!targetText.value.trim()) return;
        
        targetText.select();
        document.execCommand('copy');
        
        const originalText = copyTargetBtn.textContent;
        copyTargetBtn.textContent = 'Copied!';
        setTimeout(() => {
            copyTargetBtn.textContent = originalText;
        }, 2000);
    });
    
    // Detect language
    detectLanguageBtn.addEventListener('click', function() {
        if (!sourceText.value.trim()) {
            alert('Please enter text to detect language');
            return;
        }
        
        detectLanguageBtn.textContent = 'Detecting...';
        
        fetch('/api/translate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: sourceText.value,
                target_lang: targetLanguage.value
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.source_lang) {
                for (let option of sourceLanguage.options) {
                    if (option.value === data.source_lang) {
                        option.selected = true;
                        break;
                    }
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
        })
        .finally(() => {
            detectLanguageBtn.textContent = 'Detect Language';
        });
    });
    
    // Speak functions
    speakSourceBtn.addEventListener('click', function() {
        if (!sourceText.value.trim()) return;
        
        const langCode = sourceLanguage.value || 'en';
        textToSpeech(sourceText.value, langCode);
    });
    
    speakTargetBtn.addEventListener('click', function() {
        if (!targetText.value.trim()) return;
        
        textToSpeech(targetText.value, targetLanguage.value);
    });
    
    function textToSpeech(text, language) {
        fetch('/api/text-to-speech', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                language: language
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('TTS error: ' + data.error);
            } else if (data.audio_url) {
                const audio = new Audio(data.audio_url);
                audio.play();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to generate speech: ' + error.message);
        });
    }
    
    // Speech Translation
    const recordAudioBtn = document.getElementById('recordAudioBtn');
    const recordingStatus = document.getElementById('recordingStatus');
    const sourceSpeechLanguage = document.getElementById('sourceSpeechLanguage');
    const targetSpeechLanguage = document.getElementById('targetSpeechLanguage');
    const transcriptionText = document.getElementById('transcriptionText');
    const translatedSpeechText = document.getElementById('translatedSpeechText');
    const translateSpeechBtn = document.getElementById('translateSpeechBtn');
    const speakTranslationBtn = document.getElementById('speakTranslation');
    
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    
    // Record audio
    recordAudioBtn.addEventListener('click', function() {
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    });
    
    function startRecording() {
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.start();
                
                audioChunks = [];
                
                mediaRecorder.addEventListener('dataavailable', event => {
                    audioChunks.push(event.data);
                });
                
                mediaRecorder.addEventListener('stop', () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    processSpeechToText(audioBlob);
                });
                
                isRecording = true;
                recordAudioBtn.classList.add('recording');
                recordingStatus.textContent = 'Recording... Click to stop';
            })
            .catch(error => {
                console.error('Error accessing microphone:', error);
                alert('Failed to access microphone: ' + error.message);
            });
    }
    
    function stopRecording() {
        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
            
            // Stop all audio tracks
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
            
            isRecording = false;
            recordAudioBtn.classList.remove('recording');
            recordingStatus.textContent = 'Processing audio...';
        }
    }
    
    function processSpeechToText(audioBlob) {
        const formData = new FormData();
        formData.append('audio', audioBlob);
        formData.append('language', sourceSpeechLanguage.value);
        
        fetch('/api/speech-to-text', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Speech recognition error: ' + data.error);
            } else {
                transcriptionText.value = data.text;
                recordingStatus.textContent = 'Speech recognized. Ready to translate.';
                
                // Auto-translate if there's text
                if (data.text && !data.text.startsWith('Error') && !data.text.startsWith('Could not')) {
                    translateSpeechBtn.click();
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to process speech: ' + error.message);
            recordingStatus.textContent = 'Click to start recording';
        });
    }
    
    // Translate speech
    translateSpeechBtn.addEventListener('click', function() {
        if (!transcriptionText.value.trim()) {
            alert('No speech to translate. Please record audio first.');
            return;
        }
        
        translateSpeechBtn.disabled = true;
        translateSpeechBtn.innerHTML = '<div class="spinner"></div> Translating...';
        
        fetch('/api/translate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: transcriptionText.value,
                source_lang: sourceSpeechLanguage.value.split('-')[0],
                target_lang: targetSpeechLanguage.value
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Translation error: ' + data.error);
            } else {
                translatedSpeechText.value = data.translated_text;
                speakTranslationBtn.disabled = false;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to translate: ' + error.message);
        })
        .finally(() => {
            translateSpeechBtn.disabled = false;
            translateSpeechBtn.innerHTML = '<i class="fas fa-language mr-2"></i> Translate Speech';
        });
    });
    
    // Speak translation
    speakTranslationBtn.addEventListener('click', function() {
        if (!translatedSpeechText.value.trim()) return;
        
        textToSpeech(translatedSpeechText.value, targetSpeechLanguage.value);
    });
    
    // Initialize the UI
    speakTranslationBtn.disabled = true;
});
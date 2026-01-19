/**
 * Soniox Real-time Transcription Demo
 *
 * Tests Soniox WebSocket API with:
 * - Microphone capture (16kHz, mono, PCM16)
 * - Real-time transcription display
 * - Silence-based detection (5s silence = send)
 * - Stop word detection ("go go go" = send)
 */

// Constants
const SONIOX_WS_URL = 'wss://stt-rt.soniox.com/transcribe-websocket';
const SAMPLE_RATE = 16000;
const CHANNELS = 1;

// State
let websocket = null;
let audioContext = null;
let mediaStream = null;
let processor = null;
let isRecording = false;
let finalTranscript = '';
let interimTranscript = '';

// Detection state
let detectionMode = 'silence'; // 'silence' or 'stopword'
let silenceStartTime = null;
let hasSpeech = false;

// DOM Elements
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const audioLevel = document.getElementById('audioLevel');
const finalText = document.getElementById('finalText');
const interimText = document.getElementById('interimText');
const commandBox = document.getElementById('commandBox');
const commandText = document.getElementById('commandText');
const debugLog = document.getElementById('debug');
const stopwordConfig = document.getElementById('stopwordConfig');
const silenceConfig = document.getElementById('silenceConfig');

// Mode selector
document.querySelectorAll('.mode-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        detectionMode = btn.dataset.mode;

        if (detectionMode === 'stopword') {
            stopwordConfig.classList.add('visible');
            silenceConfig.style.display = 'none';
        } else {
            stopwordConfig.classList.remove('visible');
            silenceConfig.style.display = 'flex';
        }

        log(`Detection mode: ${detectionMode}`);
    });
});

// Logging
function log(message, type = 'info') {
    const line = document.createElement('div');
    line.className = `debug-line ${type}`;
    line.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    debugLog.appendChild(line);
    debugLog.scrollTop = debugLog.scrollHeight;
    console.log(`[${type}] ${message}`);
}

// Update status
function setStatus(text, state = '') {
    statusText.textContent = text;
    statusDot.className = 'status-dot ' + state;
}

// Normalize text for stop word detection
function normalizeText(text) {
    return text.replace(/[^a-zA-Z0-9]/g, '').toLowerCase();
}

// Check for stop word
function checkStopWord(text) {
    const stopWord = document.getElementById('stopWord').value;
    const normalizedStopWord = normalizeText(stopWord);
    const normalizedText = normalizeText(text);

    if (normalizedText.endsWith(normalizedStopWord)) {
        // Strip the stop word from original text
        const regex = new RegExp(stopWord.split('').join('[\\s.,!?]*') + '[\\s.,!?]*$', 'i');
        const cleaned = text.replace(regex, '').trim();
        return { detected: true, command: cleaned };
    }
    return { detected: false, command: text };
}

// Calculate RMS and dB from audio data
function calculateAudioLevel(audioData) {
    let sum = 0;
    for (let i = 0; i < audioData.length; i++) {
        sum += audioData[i] * audioData[i];
    }
    const rms = Math.sqrt(sum / audioData.length);
    const db = 20 * Math.log10(Math.max(rms, 1e-10));
    return { rms, db };
}

// Convert Float32 to Int16 PCM
function float32ToInt16(float32Array) {
    const int16Array = new Int16Array(float32Array.length);
    for (let i = 0; i < float32Array.length; i++) {
        const s = Math.max(-1, Math.min(1, float32Array[i]));
        int16Array[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }
    return int16Array;
}

// Handle command detection
function handleCommandDetected(command) {
    log(`Command detected: "${command}"`, 'success');
    commandBox.style.display = 'block';
    commandText.textContent = command;

    // Reset for next command (in hands-free mode)
    finalTranscript = '';
    interimTranscript = '';
    finalText.textContent = '';
    interimText.textContent = '';
    hasSpeech = false;
    silenceStartTime = null;
}

// Start recording
async function startRecording() {
    const apiKey = document.getElementById('apiKey').value.trim();
    if (!apiKey) {
        alert('Please enter your Soniox API key');
        return;
    }

    const model = document.getElementById('model').value.trim() || 'stt-rt-preview';

    try {
        setStatus('Connecting...', '');
        log('Requesting microphone access...');

        // Get microphone access
        mediaStream = await navigator.mediaDevices.getUserMedia({
            audio: {
                sampleRate: SAMPLE_RATE,
                channelCount: CHANNELS,
                echoCancellation: true,
                noiseSuppression: true,
            }
        });
        log('Microphone access granted', 'success');

        // Create AudioContext
        audioContext = new AudioContext({ sampleRate: SAMPLE_RATE });
        const source = audioContext.createMediaStreamSource(mediaStream);

        // Create ScriptProcessor for audio processing
        processor = audioContext.createScriptProcessor(4096, 1, 1);

        // Connect to Soniox WebSocket
        log(`Connecting to Soniox (model: ${model})...`);
        websocket = new WebSocket(SONIOX_WS_URL);

        websocket.onopen = () => {
            log('WebSocket connected', 'success');

            // Send start request
            const startRequest = {
                api_key: apiKey,
                model: model,
                sample_rate: SAMPLE_RATE,
                num_channels: CHANNELS,
                audio_format: 'pcm_s16le',
            };
            websocket.send(JSON.stringify(startRequest));
            log('Sent start request');

            // Start audio processing
            isRecording = true;
            setStatus('Recording...', 'recording');
            startBtn.disabled = true;
            stopBtn.disabled = false;

            // Reset state
            finalTranscript = '';
            interimTranscript = '';
            finalText.textContent = '';
            interimText.textContent = '';
            commandBox.style.display = 'none';
            hasSpeech = false;
            silenceStartTime = null;
        };

        websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);

            // Check for errors
            if (data.error_message) {
                log(`Error: ${data.error_message}`, 'error');
                stopRecording();
                return;
            }

            // Process tokens
            if (data.tokens) {
                let newFinal = '';
                let newInterim = '';

                for (const token of data.tokens) {
                    const text = token.text || '';
                    if (token.is_final) {
                        newFinal += text;
                    } else {
                        newInterim += text;
                    }
                }

                if (newFinal) {
                    finalTranscript += newFinal;
                    finalText.textContent = finalTranscript;
                    hasSpeech = true;
                    silenceStartTime = null; // Reset silence timer on speech

                    // Check for stop word (if in stop word mode)
                    if (detectionMode === 'stopword') {
                        const result = checkStopWord(finalTranscript);
                        if (result.detected) {
                            handleCommandDetected(result.command);
                        }
                    }
                }

                interimTranscript = newInterim;
                interimText.textContent = interimTranscript;
            }
        };

        websocket.onerror = (error) => {
            log(`WebSocket error: ${error}`, 'error');
        };

        websocket.onclose = () => {
            log('WebSocket closed');
            if (isRecording) {
                stopRecording();
            }
        };

        // Process audio
        processor.onaudioprocess = (e) => {
            if (!isRecording || websocket.readyState !== WebSocket.OPEN) return;

            const inputData = e.inputBuffer.getChannelData(0);

            // Calculate and display audio level
            const { db } = calculateAudioLevel(inputData);
            const normalizedLevel = Math.max(0, Math.min(100, (db + 60) * 2)); // -60dB to 0dB -> 0-100%
            audioLevel.style.width = normalizedLevel + '%';

            // Silence detection (if in silence mode)
            if (detectionMode === 'silence') {
                const silenceThreshold = -40; // dB
                const silenceDuration = parseInt(document.getElementById('silenceDuration').value) || 5000;

                if (db < silenceThreshold) {
                    // Silence detected
                    if (hasSpeech && !silenceStartTime) {
                        silenceStartTime = Date.now();
                    }

                    if (silenceStartTime && (Date.now() - silenceStartTime) >= silenceDuration) {
                        // Silence threshold reached
                        if (finalTranscript.trim()) {
                            handleCommandDetected(finalTranscript.trim());
                        }
                    }
                } else {
                    // Speech detected
                    silenceStartTime = null;
                }
            }

            // Convert and send audio
            const int16Data = float32ToInt16(inputData);
            websocket.send(int16Data.buffer);
        };

        // Connect audio nodes
        source.connect(processor);
        processor.connect(audioContext.destination);

    } catch (error) {
        log(`Error: ${error.message}`, 'error');
        setStatus('Error', '');
        stopRecording();
    }
}

// Stop recording
function stopRecording() {
    isRecording = false;

    if (processor) {
        processor.disconnect();
        processor = null;
    }

    if (audioContext) {
        audioContext.close();
        audioContext = null;
    }

    if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
        mediaStream = null;
    }

    if (websocket) {
        websocket.close();
        websocket = null;
    }

    setStatus('Stopped', '');
    startBtn.disabled = false;
    stopBtn.disabled = true;
    audioLevel.style.width = '0%';
    log('Recording stopped');
}

// Event listeners
startBtn.addEventListener('click', startRecording);
stopBtn.addEventListener('click', stopRecording);

// Load saved API key
const savedApiKey = localStorage.getItem('soniox_api_key');
if (savedApiKey) {
    document.getElementById('apiKey').value = savedApiKey;
}

// Save API key on change
document.getElementById('apiKey').addEventListener('change', (e) => {
    localStorage.setItem('soniox_api_key', e.target.value);
});

log('Demo ready. Enter your API key and click Start.');

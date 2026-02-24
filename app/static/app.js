// Recording Status Tracking
let isRecording = false;
let statusInterval = null;
let recordingStartTime = null;
let currentUser = null;
const API_BASE = '/api';

/**
 * Format seconds to MM:SS format
 */
function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
        return `${hours}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }
    return `${minutes}:${String(secs).padStart(2, '0')}`;
}

/**
 * Show message to user
 */
function showMessage(text, type = 'info') {
    const messageBox = document.getElementById('messageBox');
    const messageText = document.getElementById('messageText');
    
    messageBox.className = `message-box ${type}`;
    messageText.textContent = text;
    messageBox.style.display = 'block';
    
    // Auto-hide after 5 seconds for success messages
    if (type === 'success') {
        setTimeout(() => {
            messageBox.style.display = 'none';
        }, 5000);
    }
}

// ==================== TAB MANAGEMENT ====================

/**
 * Show login tab
 */
function showLoginTab() {
    document.getElementById('loginTab').classList.add('active');
    document.getElementById('registerTab').classList.remove('active');
    document.querySelectorAll('.tab-btn')[0].classList.add('active');
    document.querySelectorAll('.tab-btn')[1].classList.remove('active');
}

/**
 * Show register tab
 */
function showRegisterTab() {
    document.getElementById('registerTab').classList.add('active');
    document.getElementById('loginTab').classList.remove('active');
    document.querySelectorAll('.tab-btn')[1].classList.add('active');
    document.querySelectorAll('.tab-btn')[0].classList.remove('active');
}

// ==================== USER MANAGEMENT ====================

/**
 * Register new user
 */
async function registerUser() {
    const username = document.getElementById('regUsername').value.trim();
    const email = document.getElementById('regEmail').value.trim();
    
    if (!username) {
        showMessage('Please enter a username', 'error');
        return;
    }
    
    if (username.length < 3) {
        showMessage('Username must be at least 3 characters', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/users/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                username: username,
                email: email || null
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(`✅ User registered successfully! You can now login.`, 'success');
            
            // Clear form
            document.getElementById('regUsername').value = '';
            document.getElementById('regEmail').value = '';
            
            // Switch to login tab
            setTimeout(() => {
                showLoginTab();
                document.getElementById('loginUsername').value = username;
            }, 1500);
        } else {
            showMessage(`Error: ${data.error}`, 'error');
        }
    } catch (error) {
        console.error('Error registering user:', error);
        showMessage('Failed to register user', 'error');
    }
}

/**
 * Login user
 */
async function loginUser() {
    const username = document.getElementById('loginUsername').value.trim();
    
    if (!username) {
        showMessage('Please enter your username', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/users/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username: username })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = username;
            showMessage(`✅ Welcome ${username}!`, 'success');
            
            // Update UI
            updateUserUI();
        } else {
            showMessage(`Error: ${data.error}`, 'error');
        }
    } catch (error) {
        console.error('Error logging in:', error);
        showMessage('Failed to login', 'error');
    }
}

/**
 * Logout user
 */
function logoutUser() {
    if (!confirm('Are you sure you want to logout?')) {
        return;
    }
    
    currentUser = null;
    document.getElementById('loginUsername').value = '';
    showMessage('✅ You have been logged out', 'success');
    updateUserUI();
}

/**
 * Update UI based on login state
 */
function updateUserUI() {
    const recordingSection = document.getElementById('recordingSection');
    const currentUserSection = document.getElementById('currentUserSection');
    const authSection = document.getElementById('authSection');
    
    if (currentUser) {
        // User logged in
        authSection.style.display = 'none';
        recordingSection.style.display = 'block';
        currentUserSection.style.display = 'block';
        document.getElementById('currentUsername').textContent = currentUser;
    } else {
        // User not logged in
        authSection.style.display = 'block';
        recordingSection.style.display = 'none';
        currentUserSection.style.display = 'none';
    }
}

// ==================== TIME WINDOW MANAGEMENT ====================

/**
 * Handle custom duration input
 */
function handleTotalDurationChange() {
    const select = document.getElementById('totalDuration');
    const customInput = document.getElementById('customDuration');
    
    if (select.value === 'custom') {
        customInput.style.display = 'block';
        customInput.focus();
    } else {
        customInput.style.display = 'none';
    }
    
    updateExpectedChunks();
}

// Update the select element listener
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('totalDuration').addEventListener('change', handleTotalDurationChange);
});

/**
 * Update expected chunks based on selected durations
 */
function updateExpectedChunks() {
    const totalSelect = document.getElementById('totalDuration');
    const chunkSelect = document.getElementById('chunkDuration');
    const customInput = document.getElementById('customDuration');
    
    let totalDuration;
    
    if (totalSelect.value === 'custom') {
        totalDuration = parseInt(customInput.value) || 0;
    } else {
        totalDuration = parseInt(totalSelect.value);
    }
    
    const chunkDuration = parseInt(chunkSelect.value);
    
    if (totalDuration <= 0) {
        document.getElementById('expectedChunks').textContent = '0';
        document.getElementById('totalTime').textContent = '0';
        return;
    }
    
    const expectedChunks = Math.ceil(totalDuration / chunkDuration);
    const totalMinutes = Math.floor(totalDuration / 60);
    
    document.getElementById('expectedChunks').textContent = expectedChunks;
    document.getElementById('totalTime').textContent = totalMinutes;
    
    // Update status display as well
    document.getElementById('statusTotal').textContent = formatTime(totalDuration);
    document.getElementById('statusExpectedChunks').textContent = expectedChunks;
}

// ==================== RECORDING ====================

/**
 * Get total duration value in seconds
 */
function getTotalDuration() {
    const select = document.getElementById('totalDuration');
    const customInput = document.getElementById('customDuration');
    
    if (select.value === 'custom') {
        return parseInt(customInput.value) || 0;
    }
    return parseInt(select.value);
}

/**
 * Get chunk duration value in seconds
 */
function getChunkDuration() {
    return parseInt(document.getElementById('chunkDuration').value);
}

/**
 * Start recording
 */
async function startRecording() {
    if (!currentUser) {
        showMessage('Please login first', 'error');
        return;
    }
    
    const totalDuration = getTotalDuration();
    const chunkDuration = getChunkDuration();
    
    if (totalDuration <= 0) {
        showMessage('Please enter a valid duration', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/start-recording`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                username: currentUser,
                total_duration_seconds: totalDuration,
                chunk_duration_seconds: chunkDuration
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            isRecording = true;
            recordingStartTime = Date.now();
            
            // Update UI
            document.getElementById('startBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;
            document.getElementById('totalDuration').disabled = true;
            document.getElementById('chunkDuration').disabled = true;
            document.getElementById('customDuration').disabled = true;
            document.getElementById('statusBox').style.display = 'block';
            document.getElementById('statusUser').textContent = currentUser;
            
            showMessage(`✅ Recording started!`, 'success');
            
            // Start status polling
            startStatusPolling();
        } else {
            showMessage(`Error: ${data.error}`, 'error');
        }
    } catch (error) {
        console.error('Error starting recording:', error);
        showMessage('Failed to start recording', 'error');
    }
}

/**
 * Stop recording
 */
async function stopRecording() {
    if (!currentUser) {
        showMessage('No active recording', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/stop-recording`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username: currentUser })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            isRecording = false;
            clearInterval(statusInterval);
            
            // Update UI
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
            document.getElementById('totalDuration').disabled = false;
            document.getElementById('chunkDuration').disabled = false;
            document.getElementById('customDuration').disabled = false;
            document.getElementById('statusBox').style.display = 'none';
            
            showMessage(
                `✅ Recording stopped! Total chunks: ${data.total_chunks}`,
                'success'
            );
        } else {
            showMessage(`Error: ${data.error}`, 'error');
        }
    } catch (error) {
        console.error('Error stopping recording:', error);
        showMessage('Failed to stop recording', 'error');
    }
}

/**
 * Poll recording status
 */
async function startStatusPolling() {
    statusInterval = setInterval(async () => {
        if (!isRecording || !currentUser) {
            clearInterval(statusInterval);
            return;
        }
        
        try {
            const response = await fetch(`${API_BASE}/recording-status/${currentUser}`);
            const data = await response.json();
            
            if (response.ok && data.is_recording) {
                // Update elapsed time
                const elapsed = data.elapsed_seconds;
                document.getElementById('statusElapsed').textContent = formatTime(elapsed);
                
                // Update chunks count
                document.getElementById('statusChunks').textContent = data.total_chunks_so_far;
                
                // Update progress bar
                const progressFill = document.getElementById('progressFill');
                const percentage = (elapsed / data.total_duration_seconds) * 100;
                progressFill.style.width = Math.min(percentage, 100) + '%';
                
                // Check if recording should stop
                if (elapsed >= data.total_duration_seconds) {
                    stopRecording();
                }
            } else if (!data.is_recording) {
                stopRecording();
            }
        } catch (error) {
            console.error('Error polling status:', error);
        }
    }, 1000); // Poll every second
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    updateUserUI();
    updateExpectedChunks();
});


// Dashboard functionality
const API_BASE = '/api';
let allVideos = [];
let allUsers = [];

/**
 * Format date to readable format
 */
function formatDate(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

/**
 * Calculate duration between two timestamps
 */
function calculateDuration(startTime, endTime) {
    const start = new Date(startTime);
    const end = new Date(endTime);
    const diffSeconds = (end - start) / 1000;
    
    const minutes = Math.floor(diffSeconds / 60);
    const seconds = Math.floor(diffSeconds % 60);
    
    return `${minutes}m ${seconds}s`;
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
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        messageBox.style.display = 'none';
    }, 5000);
}

/**
 * Load all videos from the server
 */
async function loadAllVideos() {
    try {
        document.getElementById('videosContainer').innerHTML = '<p class="loading">Loading videos...</p>';
        
        const response = await fetch(`${API_BASE}/videos`);
        const data = await response.json();
        
        if (response.ok) {
            allVideos = data.chunks;
            displayVideos(allVideos);
            updateStatistics(allVideos);
        } else {
            showMessage(`Error: ${data.error}`, 'error');
        }
    } catch (error) {
        console.error('Error loading videos:', error);
        showMessage('Failed to load videos', 'error');
    }
}

/**
 * Load all users from the server
 */
async function loadAllUsers() {
    try {
        const response = await fetch(`${API_BASE}/users`);
        const data = await response.json();
        
        if (response.ok) {
            allUsers = data.users;
            populateUserFilter();
        } else {
            console.error('Error loading users:', data.error);
        }
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

/**
 * Populate user filter dropdown
 */
function populateUserFilter() {
    const filterSelect = document.getElementById('filterUserSelect');
    if (!filterSelect) return;
    
    filterSelect.innerHTML = '<option value="">All Users</option>';
    allUsers.forEach(user => {
        const option = document.createElement('option');
        option.value = user.username;
        option.textContent = user.username;
        filterSelect.appendChild(option);
    });
}

/**
 * Display videos in the container
 */
function displayVideos(videos) {
    const container = document.getElementById('videosContainer');
    
    if (videos.length === 0) {
        container.innerHTML = '<p class="loading">No videos found</p>';
        return;
    }
    
    container.innerHTML = videos.map(video => `
        <div class="video-card">
            <h3>📹 ${video.file_name}</h3>
            <p><span class="label">User:</span> <span class="value">${video.user_name}</span></p>
            <p><span class="label">Duration:</span> <span class="value">${calculateDuration(video.record_start_time, video.record_end_time)}</span></p>
            <p><span class="label">Requested Duration:</span> <span class="value">${video.duration_seconds}s</span></p>
            <p><span class="label">Chunk Size:</span> <span class="value">${video.chunk_duration_seconds}s</span></p>
            <p><span class="label">Start Time:</span> <span class="value">${formatDate(video.record_start_time)}</span></p>
            <p><span class="label">End Time:</span> <span class="value">${formatDate(video.record_end_time)}</span></p>
            <p><span class="label">Recorded:</span> <span class="value">${formatDate(video.created_at)}</span></p>
            
            <div class="video-actions">
                <button class="btn btn-play" onclick="playVideo(${video.id})">▶️ Play</button>
                <button class="btn btn-download" onclick="downloadVideo(${video.id}, '${video.file_name}')">⬇️ Download</button>
                <button class="btn btn-delete" onclick="deleteVideo(${video.id})">🗑️ Delete</button>
            </div>
        </div>
    `).join('');
}

/**
 * Update statistics display
 */
function updateStatistics(videos) {
    if (videos.length === 0) {
        document.getElementById('totalChunks').textContent = '0';
        document.getElementById('totalUsers').textContent = '0';
        document.getElementById('totalDuration').textContent = '0h';
        return;
    }
    
    // Total chunks
    document.getElementById('totalChunks').textContent = videos.length;
    
    // Unique users
    const uniqueUsers = new Set(videos.map(v => v.user_name));
    document.getElementById('totalUsers').textContent = uniqueUsers.size;
    
    // Total duration
    let totalDurationSeconds = 0;
    videos.forEach(video => {
        const start = new Date(video.record_start_time);
        const end = new Date(video.record_end_time);
        totalDurationSeconds += (end - start) / 1000;
    });
    
    const hours = Math.floor(totalDurationSeconds / 3600);
    const minutes = Math.floor((totalDurationSeconds % 3600) / 60);
    document.getElementById('totalDuration').textContent = `${hours}h ${minutes}m`;
}

/**
 * Play video in a modal or new window
 */
function playVideo(videoId) {
    // Open video in a new modal or window
    const video = allVideos.find(v => v.id === videoId);
    if (!video) {
        showMessage('Video not found', 'error');
        return;
    }
    
    // Create a simple modal to play the video
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
    `;
    
    modal.innerHTML = `
        <div style="
            background: white;
            border-radius: 10px;
            padding: 20px;
            max-width: 90%;
            max-height: 90%;
            overflow: auto;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h2 style="margin: 0;">${video.file_name}</h2>
                <button onclick="this.closest('div').parentElement.remove()" style="
                    background: none;
                    border: none;
                    font-size: 1.5rem;
                    cursor: pointer;
                ">✕</button>
            </div>
            <video width="100%" height="auto" controls style="border-radius: 8px; max-height: 70vh;">
                <source src="/api/video/${videoId}/download" type="video/mp4">
                Your browser does not support the video tag.
            </video>
            <p style="margin-top: 15px; color: #666;">
                <strong>User:</strong> ${video.user_name}<br>
                <strong>Duration:</strong> ${calculateDuration(video.record_start_time, video.record_end_time)}<br>
                <strong>Requested Duration:</strong> ${video.duration_seconds}s<br>
                <strong>Chunk Size:</strong> ${video.chunk_duration_seconds}s<br>
                <strong>Recorded:</strong> ${formatDate(video.created_at)}
            </p>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Close modal when clicking outside
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

/**
 * Download video
 */
function downloadVideo(videoId, fileName) {
    const a = document.createElement('a');
    a.href = `/api/video/${videoId}/download`;
    a.download = fileName;
    a.click();
    showMessage(`✅ Downloading ${fileName}...`, 'success');
}

/**
 * Delete video
 */
async function deleteVideo(videoId) {
    if (!confirm('Are you sure you want to delete this video? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/delete-video/${videoId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('✅ Video deleted successfully', 'success');
            // Reload videos
            loadAllVideos();
        } else {
            showMessage(`Error: ${data.error}`, 'error');
        }
    } catch (error) {
        console.error('Error deleting video:', error);
        showMessage('Failed to delete video', 'error');
    }
}

/**
 * Apply filter by user name
 */
function applyFilter() {
    const filterSelect = document.getElementById('filterUserSelect');
    const userName = filterSelect.value.trim();
    
    if (!userName) {
        loadAllVideos();
        showMessage('Filters cleared', 'success');
        return;
    }
    
    const filtered = allVideos.filter(v => v.user_name === userName);
    
    if (filtered.length === 0) {
        showMessage(`No videos found for user "${userName}"`, 'info');
    } else {
        showMessage(`Found ${filtered.length} video(s) for user "${userName}"`, 'success');
    }
    
    displayVideos(filtered);
}

// Load all videos on page load
document.addEventListener('DOMContentLoaded', () => {
    loadAllVideos();
    loadAllUsers();
});

// Refresh videos every 10 seconds
setInterval(loadAllVideos, 10000);


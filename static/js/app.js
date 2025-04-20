// DOM Elements
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const fileInput = document.getElementById('file-input');
const filePreview = document.getElementById('file-preview');
const filePreviewImg = document.getElementById('file-preview-img');
const fileName = document.getElementById('file-name');
const fileType = document.getElementById('file-type');
const removeFileBtn = document.getElementById('remove-file');
const chatMessages = document.getElementById('chat-messages');
const sendBtn = document.getElementById('send-btn');

// State variables
let currentFile = null;
let isProcessingYouTube = false;

// YouTube URL regex pattern
const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+$/;

// Initialize the chat interface
function initChat() {
    // Focus on input field
    chatInput.focus();

    // Set up event listeners
    chatForm.addEventListener('submit', handleSubmit);
    fileInput.addEventListener('change', handleFileSelect);
    removeFileBtn.addEventListener('click', removeFile);

    // Auto-resize textarea as user types
    chatInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
}

// Check if a string is a YouTube URL
function isYouTubeUrl(url) {
    return youtubeRegex.test(url);
}

// Handle form submission
async function handleSubmit(e) {
    e.preventDefault();

    const message = chatInput.value.trim();

    // Don't submit if both message and file are empty
    if (!message && !currentFile) {
        return;
    }

    // Check if the message is a YouTube URL
    const isYouTube = isYouTubeUrl(message);
    if (isYouTube) {
        isProcessingYouTube = true;
    }

    // Add user message to chat
    if (isYouTube) {
        addMessage('user', `Processing YouTube video: ${message}`);
    } else {
        addMessage('user', message);
    }

    // Clear input and reset height
    chatInput.value = '';
    chatInput.style.height = 'auto';

    // Show loading indicator
    showLoadingIndicator();
    if (isYouTube) {
        updateLoadingMessage('Fetching and processing YouTube video... This may take a minute.');
    }

    // Prepare data for submission
    let requestData;
    let requestOptions;

    if (currentFile) {
        // If we have a file, use FormData
        const formData = new FormData();
        formData.append('message', message);
        formData.append('file', currentFile);

        requestData = formData;
        requestOptions = {
            method: 'POST',
            body: formData
        };
    } else {
        // For text-only, use JSON
        requestData = { message };
        requestOptions = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        };
    }

    try {
        console.log('Sending request to server...');
        console.log('Message:', message);
        console.log('File:', currentFile ? currentFile.name : 'none');

        // Send request to server
        const response = await fetch('/chat', requestOptions);

        console.log('Response status:', response.status);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Server error:', errorText);
            throw new Error(`Server error: ${response.status} ${response.statusText}\n${errorText}`);
        }

        const data = await response.json();
        console.log('Response data:', data);

        // Remove loading indicator
        removeLoadingIndicator();
        isProcessingYouTube = false;

        if (data.error) {
            // Show error message
            console.error('API error:', data.error);
            addMessage('ai', `Error: ${data.error}`);
        } else {
            // Show AI response
            addMessage('ai', data.answer);

            // Display similar content if available
            if (data.similar_content && data.similar_content.length > 0) {
                let similarContentHtml = '<div class="similar-content"><h4>Similar Content Found:</h4><ul>';

                data.similar_content.forEach(item => {
                    let itemHtml = `<li><strong>${item.type}</strong>: `;

                    if (item.url) {
                        itemHtml += `<a href="${item.url}" target="_blank">${item.url}</a><br>`;
                    }

                    itemHtml += `<span class="similarity">Similarity: ${Math.round(item.similarity * 100)}%</span><br>`;
                    itemHtml += `<span class="snippet">${item.text}</span></li>`;

                    similarContentHtml += itemHtml;
                });

                similarContentHtml += '</ul></div>';

                // Add similar content as a system message
                addMessage('system', similarContentHtml);
            }
        }
    } catch (error) {
        console.error('Fetch error:', error);

        // Remove loading indicator
        removeLoadingIndicator();

        // Show error message
        addMessage('ai', `Error: ${error.message}`);
    }

    // Reset file after submission
    if (currentFile) {
        removeFile();
    }

    // Scroll to bottom of chat
    scrollToBottom();
}

// Handle file selection
function handleFileSelect(e) {
    const file = e.target.files[0];

    if (!file) {
        return;
    }

    currentFile = file;

    // Show file preview
    filePreview.classList.add('show');
    fileName.textContent = file.name;

    // Determine file type and show appropriate preview
    const fileExtension = file.name.split('.').pop().toLowerCase();
    fileType.textContent = file.type || fileExtension;

    if (file.type.startsWith('image/')) {
        // Show image preview
        const reader = new FileReader();
        reader.onload = function(e) {
            filePreviewImg.src = e.target.result;
            filePreviewImg.style.display = 'block';
        };
        reader.readAsDataURL(file);
    } else {
        // Hide image preview for non-image files
        filePreviewImg.style.display = 'none';
    }
}

// Remove selected file
function removeFile() {
    currentFile = null;
    fileInput.value = '';
    filePreview.classList.remove('show');
    filePreviewImg.src = '';
}

// Add a message to the chat
function addMessage(sender, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;

    const avatarDiv = document.createElement('div');
    avatarDiv.className = `message-avatar ${sender}-avatar`;
    avatarDiv.textContent = sender === 'user' ? 'U' : 'AI';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = formatMessage(content);

    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);

    chatMessages.appendChild(messageDiv);

    // Scroll to the new message
    scrollToBottom();
}

// Format message content (convert URLs to links, etc.)
function formatMessage(content) {
    if (!content) return '';

    // Convert URLs to clickable links
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    content = content.replace(urlRegex, url => `<a href="${url}" target="_blank">${url}</a>`);

    // Convert line breaks to <br>
    content = content.replace(/\n/g, '<br>');

    return content;
}

// Show loading indicator
function showLoadingIndicator() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message ai-message loading-message';
    loadingDiv.id = 'loading-indicator';

    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar ai-avatar';
    avatarDiv.textContent = 'AI';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content loading';
    contentDiv.id = 'loading-content';

    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';
    typingIndicator.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';

    // Add a message element
    const messageElement = document.createElement('div');
    messageElement.className = 'loading-message-text';
    messageElement.textContent = 'Generating response...';
    messageElement.id = 'loading-message-text';

    contentDiv.appendChild(messageElement);
    contentDiv.appendChild(typingIndicator);
    loadingDiv.appendChild(avatarDiv);
    loadingDiv.appendChild(contentDiv);

    chatMessages.appendChild(loadingDiv);

    scrollToBottom();
}

// Update loading message
function updateLoadingMessage(message) {
    const messageElement = document.getElementById('loading-message-text');
    if (messageElement) {
        messageElement.textContent = message;
    }
}

// Remove loading indicator
function removeLoadingIndicator() {
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.remove();
    }
}

// Scroll to bottom of chat
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initChat);

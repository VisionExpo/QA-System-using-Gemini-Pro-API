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

// Handle form submission
async function handleSubmit(e) {
    e.preventDefault();

    const message = chatInput.value.trim();

    // Don't submit if both message and file are empty
    if (!message && !currentFile) {
        return;
    }

    // Add user message to chat
    addMessage('user', message);

    // Clear input and reset height
    chatInput.value = '';
    chatInput.style.height = 'auto';

    // Show loading indicator
    showLoadingIndicator();

    // Prepare form data for submission
    const formData = new FormData();
    formData.append('message', message);

    if (currentFile) {
        formData.append('file', currentFile);
    }

    try {
        console.log('Sending request to server...');
        console.log('Message:', message);
        console.log('File:', currentFile ? currentFile.name : 'none');

        // Send request to server
        const response = await fetch('/chat', {
            method: 'POST',
            body: formData
        });

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

        if (data.error) {
            // Show error message
            console.error('API error:', data.error);
            addMessage('ai', `Error: ${data.error}`);
        } else {
            // Show AI response
            addMessage('ai', data.answer);
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

    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';
    typingIndicator.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';

    contentDiv.appendChild(typingIndicator);
    loadingDiv.appendChild(avatarDiv);
    loadingDiv.appendChild(contentDiv);

    chatMessages.appendChild(loadingDiv);

    scrollToBottom();
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

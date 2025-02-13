let selectedLayout = 'layout_1.html'; // Default layout

function selectLayout(event) {
    document.querySelectorAll('.layout-icon').forEach(icon => {
        icon.classList.remove('selected');
    });
    event.target.classList.add('selected');
    selectedLayout = event.target.getAttribute('data-layout');
}

async function checkBackendStatus() {
    try {
        const response = await fetch('http://localhost:9000/');
        const data = await response.json();
        console.log('Backend status:', data);
        return data.status === 'Running';
    } catch (error) {
        console.error('Backend health check failed:', error);
        return false;
    }
}

async function produceNewspaper() {
    var topics = [];
    for (var i = 1; i <= topicCount; i++) {
        var topic = document.getElementById('topic' + i).value.trim();
        if (topic) {
            topics.push(topic);
        }
    }

    if (topics.length === 0) {
        alert('Please fill in at least one topic.');
        return;
    }

    // Check backend status first
    const isBackendRunning = await checkBackendStatus();
    if (!isBackendRunning) {
        alert('Backend server is not responding. Please try again later.');
        return;
    }

    // Show loading animation
    toggleLoading(true);

    const payload = {
        topics: topics,
        layout: selectedLayout
    };

    console.log('Sending request with payload:', payload);

    try {
        const response = await fetch('http://localhost:9000/generate_newspaper', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        console.log('Response status:', response.status);
        const data = await response.json();
        console.log('Response data:', data);

        if (!response.ok) {
            throw new Error(data.error || 'Failed to generate newspaper');
        }

        toggleLoading(false);
        displayNewspaper(data);
    } catch (error) {
        toggleLoading(false);
        console.error('Error:', error);
        alert('Error generating newspaper: ' + error.message);
    }
}

function toggleLoading(isLoading) {
    const loadingSection = document.getElementById('loading');
    const loadingMessages = document.getElementById('loadingMessages');
    const messages = [
        "Looking for news...", 
        "Curating sources...", 
        "Writing articles...", 
        "Editing content...",
        "Generating podcast...",
        "Finalizing your personalized news experience..."
    ];
    loadingMessages.style.fontFamily = "'Gill Sans', sans-serif";
    if (isLoading) {
        loadingSection.classList.remove('hidden');
        let messageIndex = 0;
        loadingMessages.textContent = messages[messageIndex];
        const interval = setInterval(() => {
            if (messageIndex < messages.length - 1) {
                messageIndex++;
                loadingMessages.textContent = messages[messageIndex];
            } else {
                clearInterval(interval);
            }
        }, 10000);
        loadingSection.dataset.intervalId = interval;
    } else {
        loadingSection.classList.add('hidden');
        clearInterval(loadingSection.dataset.intervalId);
    }
}

let topicCount = 1;

window.addEventListener('DOMContentLoaded', async (event) => {
    document.getElementById('produceNewspaper').addEventListener('click', produceNewspaper);
    document.querySelectorAll('.layout-icon').forEach(icon => {
        icon.addEventListener('click', selectLayout);
    });
    addIconToLastTopic();

    // Check backend status on page load
    const isBackendRunning = await checkBackendStatus();
    if (!isBackendRunning) {
        alert('Warning: Backend server is not responding. Please make sure it is running.');
    }
});

function addIconToLastTopic() {
    // Remove icons from all topics
    document.querySelectorAll('.add-topic, .remove-topic').forEach(icon => {
        icon.remove();
    });

    // Add icons to the last topic only
    const lastTopic = document.getElementById('topicGroup' + topicCount);
    if (lastTopic) {
        const addIcon = document.createElement('span');
        addIcon.className = 'icon add-topic';
        addIcon.textContent = '+';
        addIcon.addEventListener('click', addTopicField);
        lastTopic.appendChild(addIcon);

        if (topicCount > 1) {
            const removeIcon = document.createElement('span');
            removeIcon.className = 'icon remove-topic';
            removeIcon.textContent = '-';
            removeIcon.addEventListener('click', removeTopicField);
            lastTopic.appendChild(removeIcon);
        }
    }
}

function addTopicField() {
    topicCount++;
    const formGroup = document.createElement('div');
    formGroup.className = 'form-group';
    formGroup.id = 'topicGroup' + topicCount;

    const inputElement = document.createElement('input');
    inputElement.type = 'text';
    inputElement.id = 'topic' + topicCount;
    inputElement.name = 'topic' + topicCount;
    inputElement.className = 'inputText';
    inputElement.required = true;

    formGroup.appendChild(inputElement);

    document.getElementById('topicForm').appendChild(formGroup);

    addIconToLastTopic();
}

function removeTopicField(event) {
    const topicGroup = event.target.parentElement;
    if (topicGroup && topicGroup.id !== 'topicGroup1') {
        topicGroup.remove();
        topicCount--;
        addIconToLastTopic();
    }
}

function displayNewspaper(data) {
    if (data.path) {
        window.location.href = data.path;
    } else {
        console.error('Error: Newspaper path not found');
    }
}
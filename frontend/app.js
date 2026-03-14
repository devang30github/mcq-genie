/**
 * Main Application Logic
 * Handles UI interactions and state management
 */

// ==================== STATE MANAGEMENT ====================
const AppState = {
    currentPage: 'landing',
    sessionId: null,
    currentTest: null,
    currentQuestionIndex: 0,
    userAnswers: {},
    testTimer: null,
    timeRemaining: 0
};

// ==================== PAGE NAVIGATION ====================

function showPage(pageName) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });

    // Show requested page
    const page = document.getElementById(`${pageName}-page`);
    if (page) {
        page.classList.add('active');
        AppState.currentPage = pageName;
    }
}

function startApp() {
    showPage('chat');
    initializeChat();
}

function backToChat() {
    showPage('chat');
}

// ==================== CHAT FUNCTIONALITY ====================

async function initializeChat() {
    try {
        const response = await api.createNewSession();
        AppState.sessionId = response.session_id;
        console.log('Chat session created:', AppState.sessionId);
    } catch (error) {
        console.error('Failed to create chat session:', error);
        showError('Failed to initialize chat. Please refresh the page.');
    }
}

async function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();

    if (!message) return;

    // Add user message to chat
    addMessageToChat('user', message);
    input.value = '';
    autoResizeTextarea(input);

    // Hide suggestions
    document.getElementById('suggestions').style.display = 'none';

    // Show typing indicator
    const typingId = addTypingIndicator();

    try {
        const response = await api.sendMessage(message, AppState.sessionId);
        
        // Remove typing indicator
        removeTypingIndicator(typingId);

        // Add assistant message
        addMessageToChat('assistant', response.message);

        // Update session ID if new
        if (response.session_id) {
            AppState.sessionId = response.session_id;
        }

        // Show suggestions if available
        if (response.suggestions && response.suggestions.length > 0) {
            updateSuggestions(response.suggestions);
        }

        // Check if message mentions test/quiz
        if (shouldShowTestModal(message, response.message)) {
            setTimeout(() => openTestModal(message), 500);
        }

    } catch (error) {
        removeTypingIndicator(typingId);
        addMessageToChat('assistant', '❌ Sorry, I encountered an error. Please try again.');
        console.error('Chat error:', error);
    }
}

function addMessageToChat(role, content) {
    const messagesContainer = document.getElementById('chat-messages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? '👤' : '🤖';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    // Convert newlines to paragraphs
    const paragraphs = content.split('\n').filter(p => p.trim());
    paragraphs.forEach(p => {
        const para = document.createElement('p');
        para.textContent = p;
        messageContent.appendChild(para);
    });
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(messageContent);
    messagesContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function addTypingIndicator() {
    const messagesContainer = document.getElementById('chat-messages');
    const typingId = 'typing-' + Date.now();
    
    const typingDiv = document.createElement('div');
    typingDiv.id = typingId;
    typingDiv.className = 'message assistant-message';
    typingDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            <p>Thinking...</p>
        </div>
    `;
    
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    return typingId;
}

function removeTypingIndicator(typingId) {
    const typingDiv = document.getElementById(typingId);
    if (typingDiv) {
        typingDiv.remove();
    }
}

function updateSuggestions(suggestions) {
    const suggestionsContainer = document.getElementById('suggestions');
    suggestionsContainer.innerHTML = '';
    
    suggestions.forEach(suggestion => {
        const chip = document.createElement('button');
        chip.className = 'suggestion-chip';
        chip.textContent = suggestion;
        chip.onclick = () => sendSuggestion(suggestion);
        suggestionsContainer.appendChild(chip);
    });
    
    suggestionsContainer.style.display = 'flex';
}

function sendSuggestion(text) {
    document.getElementById('user-input').value = text;
    sendMessage();
}

function shouldShowTestModal(userMessage, assistantMessage) {
    const testKeywords = ['quiz', 'test', 'mcq', 'questions', 'exam', 'assessment'];
    const combinedText = (userMessage + ' ' + assistantMessage).toLowerCase();
    return testKeywords.some(keyword => combinedText.includes(keyword));
}

function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

// Auto-resize textarea on input
document.addEventListener('DOMContentLoaded', () => {
    const textarea = document.getElementById('user-input');
    if (textarea) {
        textarea.addEventListener('input', () => autoResizeTextarea(textarea));
    }
});

async function newChat() {
    // Clear chat messages except welcome message
    const messagesContainer = document.getElementById('chat-messages');
    messagesContainer.innerHTML = `
        <div class="message assistant-message">
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                <p>Hello! I'm MCQ Genie, your AI learning assistant. 👋</p>
                <p>Ask me anything or request a quiz on any topic!</p>
            </div>
        </div>
    `;
    
    // Create new session
    await initializeChat();
    
    // Show default suggestions
    updateSuggestions([
        'Explain photosynthesis',
        'Quiz me on Python',
        'Teach me about WW2'
    ]);
}

// ==================== TEST MODAL ====================

function openTestModal(suggestedTopic = '') {
    const modal = document.getElementById('test-modal');
    modal.classList.add('active');
    
    // Pre-fill topic if suggested
    if (suggestedTopic) {
        const topicInput = document.getElementById('test-topic');
        topicInput.value = extractTopicFromMessage(suggestedTopic);
    }
}

function closeTestModal() {
    const modal = document.getElementById('test-modal');
    modal.classList.remove('active');
}

function extractTopicFromMessage(message) {
    // Simple extraction - you can make this smarter
    const match = message.match(/(?:about|on|regarding)\s+([^.!?]+)/i);
    return match ? match[1].trim() : '';
}

async function generateTest() {
    const topic = document.getElementById('test-topic').value.trim();
    const numQuestions = parseInt(document.getElementById('num-questions').value);
    const difficulty = document.querySelector('input[name="difficulty"]:checked').value;

    if (!topic) {
        alert('Please enter a topic');
        return;
    }

    // Show loader
    const btnText = document.getElementById('generate-btn-text');
    const btnLoader = document.getElementById('generate-btn-loader');
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline-block';

    try {
        const response = await api.generateTest(topic, numQuestions, difficulty);
        
        // Store test data
        AppState.currentTest = response;
        AppState.currentQuestionIndex = 0;
        AppState.userAnswers = {};

        // Close modal
        closeTestModal();

        // Start test
        startTest();

    } catch (error) {
        alert('Failed to generate test: ' + error.message);
        console.error('Test generation error:', error);
    } finally {
        // Hide loader
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
}

// ==================== EXAM MODE ====================

function startTest() {
    showPage('exam');
    
    const test = AppState.currentTest;
    
    // Set exam header
    document.getElementById('exam-topic').textContent = test.topic;
    
    // Initialize timer
    AppState.timeRemaining = test.time_limit_minutes * 60; // Convert to seconds
    startTimer();
    
    // Create question navigator buttons
    createQuestionNavigator();
    
    // Display first question
    displayQuestion(0);
}

function startTimer() {
    const timerElement = document.getElementById('timer');
    
    AppState.testTimer = setInterval(() => {
        AppState.timeRemaining--;
        
        const minutes = Math.floor(AppState.timeRemaining / 60);
        const seconds = AppState.timeRemaining % 60;
        
        timerElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        
        // Change color when time is low
        if (AppState.timeRemaining <= 300) { // 5 minutes
            timerElement.style.color = 'var(--danger-color)';
        }
        
        // Auto-submit when time runs out
        if (AppState.timeRemaining <= 0) {
            clearInterval(AppState.testTimer);
            alert('Time is up! Submitting your test...');
            submitTest();
        }
    }, 1000);
}

function createQuestionNavigator() {
    const container = document.getElementById('question-nav-buttons');
    container.innerHTML = '';
    
    const test = AppState.currentTest;
    
    test.questions.forEach((q, index) => {
        const btn = document.createElement('button');
        btn.className = 'nav-button';
        btn.textContent = index + 1;
        btn.onclick = () => displayQuestion(index);
        container.appendChild(btn);
    });
}

function displayQuestion(index) {
    const test = AppState.currentTest;
    const question = test.questions[index];
    
    AppState.currentQuestionIndex = index;
    
    // Update progress
    document.getElementById('exam-progress').textContent = 
        `Question ${index + 1} of ${test.total_questions}`;
    document.getElementById('current-question-num').textContent = index + 1;
    
    // Update question
    document.getElementById('question-text').textContent = question.question_text;
    
    // Display options
    const optionsContainer = document.getElementById('options-container');
    optionsContainer.innerHTML = '';
    
    question.options.forEach(option => {
        const optionDiv = document.createElement('div');
        optionDiv.className = 'option';
        optionDiv.onclick = () => selectOption(question.question_id, option.option_id);
        
        // Check if already selected
        if (AppState.userAnswers[question.question_id] === option.option_id) {
            optionDiv.classList.add('selected');
        }
        
        optionDiv.innerHTML = `
            <div class="option-id">${option.option_id}</div>
            <div class="option-text">${option.text}</div>
        `;
        
        optionsContainer.appendChild(optionDiv);
    });
    
    // Update navigation buttons
    updateNavigationButtons();
    updateQuestionNavigator();
}

function selectOption(questionId, optionId) {
    // Save answer
    AppState.userAnswers[questionId] = optionId;
    
    // Update UI
    const options = document.querySelectorAll('.option');
    options.forEach(opt => opt.classList.remove('selected'));
    event.currentTarget.classList.add('selected');
    
    // Update question navigator
    updateQuestionNavigator();
}

function updateNavigationButtons() {
    const index = AppState.currentQuestionIndex;
    const total = AppState.currentTest.total_questions;
    
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const submitBtn = document.getElementById('submit-btn');
    
    // Previous button
    prevBtn.disabled = index === 0;
    
    // Next/Submit button
    if (index === total - 1) {
        nextBtn.style.display = 'none';
        submitBtn.style.display = 'inline-flex';
    } else {
        nextBtn.style.display = 'inline-flex';
        submitBtn.style.display = 'none';
    }
}

function updateQuestionNavigator() {
    const buttons = document.querySelectorAll('.nav-button');
    const test = AppState.currentTest;
    
    buttons.forEach((btn, index) => {
        btn.classList.remove('active', 'answered');
        
        if (index === AppState.currentQuestionIndex) {
            btn.classList.add('active');
        }
        
        const questionId = test.questions[index].question_id;
        if (AppState.userAnswers[questionId]) {
            btn.classList.add('answered');
        }
    });
}

function previousQuestion() {
    if (AppState.currentQuestionIndex > 0) {
        displayQuestion(AppState.currentQuestionIndex - 1);
    }
}

function nextQuestion() {
    if (AppState.currentQuestionIndex < AppState.currentTest.total_questions - 1) {
        displayQuestion(AppState.currentQuestionIndex + 1);
    }
}

async function submitTest() {
    // Stop timer
    clearInterval(AppState.testTimer);
    
    // Confirm submission
    const answeredCount = Object.keys(AppState.userAnswers).length;
    const totalCount = AppState.currentTest.total_questions;
    
    if (answeredCount < totalCount) {
        const confirmSubmit = confirm(
            `You have only answered ${answeredCount} out of ${totalCount} questions. Submit anyway?`
        );
        if (!confirmSubmit) {
            startTimer(); // Resume timer
            return;
        }
    }
    
    // Prepare answers
    const answers = AppState.currentTest.questions.map(q => ({
        question_id: q.question_id,
        selected_answer: AppState.userAnswers[q.question_id] || ''
    }));
    
    try {
        const result = await api.submitTest(AppState.currentTest.test_id, answers);
        displayResults(result);
    } catch (error) {
        alert('Failed to submit test: ' + error.message);
        console.error('Test submission error:', error);
    }
}

// ==================== RESULTS ====================

function displayResults(result) {
    showPage('results');
    
    // Display score
    document.getElementById('score-percentage').textContent = 
        Math.round(result.score_percentage) + '%';
    
    // Display topic
    document.getElementById('results-topic').textContent = result.topic;
    
    // Display stats
    document.getElementById('correct-count').textContent = result.correct_answers;
    document.getElementById('wrong-count').textContent = result.wrong_answers;
    document.getElementById('total-count').textContent = result.total_questions;
    
    // Display detailed results
    const detailedContainer = document.getElementById('detailed-results');
    detailedContainer.innerHTML = '';
    
    result.results.forEach((item, index) => {
        const resultDiv = document.createElement('div');
        resultDiv.className = `result-item ${item.is_correct ? 'correct' : 'wrong'}`;
        
        resultDiv.innerHTML = `
            <div class="result-question">
                <strong>Question ${index + 1}:</strong> ${item.question_text}
            </div>
            <div class="result-answer">
                <span class="answer-label">Your Answer:</span>
                <span class="answer-value ${item.is_correct ? 'correct' : 'wrong'}">
                    ${item.selected_answer}
                </span>
            </div>
            <div class="result-answer">
                <span class="answer-label">Correct Answer:</span>
                <span class="answer-value correct">${item.correct_answer}</span>
            </div>
            ${item.explanation ? `
                <div class="result-explanation">
                    <strong>💡 Explanation:</strong> ${item.explanation}
                </div>
            ` : ''}
        `;
        
        detailedContainer.appendChild(resultDiv);
    });
}

function retakeTest() {
    openTestModal();
    showPage('chat');
}

// ==================== UTILITY FUNCTIONS ====================

function showError(message) {
    alert(message); // You can make this prettier with a custom modal
}

// ==================== INITIALIZATION ====================

document.addEventListener('DOMContentLoaded', () => {
    console.log('MCQ Genie initialized');
    
    // Close modal when clicking outside
    const modal = document.getElementById('test-modal');
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeTestModal();
        }
    });
});
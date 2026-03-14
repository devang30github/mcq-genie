/**
 * API Service
 * Handles all HTTP requests to the backend
 */

class APIService {
    constructor(baseURL) {
        this.baseURL = baseURL;
    }

    /**
     * Generic fetch wrapper with error handling
     */
    async _fetch(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
            ...options
        };

        try {
            const response = await fetch(url, defaultOptions);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || `HTTP error! status: ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    /**
     * Send a chat message
     */
    async sendMessage(message, sessionId = null) {
        return this._fetch(CONFIG.ENDPOINTS.CHAT_MESSAGE, {
            method: 'POST',
            body: JSON.stringify({
                message: message,
                session_id: sessionId
            })
        });
    }

    /**
     * Create a new chat session
     */
    async createNewSession() {
        return this._fetch(CONFIG.ENDPOINTS.CHAT_NEW_SESSION, {
            method: 'POST'
        });
    }

    /**
     * Get chat history
     */
    async getChatHistory(sessionId) {
        return this._fetch(`${CONFIG.ENDPOINTS.CHAT_HISTORY}/${sessionId}`);
    }

    /**
     * Generate a new test
     */
    async generateTest(topic, numQuestions, difficulty) {
        return this._fetch(CONFIG.ENDPOINTS.TEST_GENERATE, {
            method: 'POST',
            body: JSON.stringify({
                topic: topic,
                num_questions: numQuestions,
                difficulty: difficulty
            })
        });
    }

    /**
     * Submit test answers
     */
    async submitTest(testId, answers) {
        return this._fetch(CONFIG.ENDPOINTS.TEST_SUBMIT, {
            method: 'POST',
            body: JSON.stringify({
                test_id: testId,
                answers: answers
            })
        });
    }

    /**
     * Get test details
     */
    async getTest(testId) {
        return this._fetch(`${CONFIG.ENDPOINTS.TEST_GET}/${testId}`);
    }

    /**
     * Get test result
     */
    async getTestResult(testId) {
        return this._fetch(`${CONFIG.ENDPOINTS.TEST_RESULT}/${testId}/result`);
    }
}

// Initialize API service
const api = new APIService(CONFIG.API_BASE_URL);
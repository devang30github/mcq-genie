/**
 * Configuration file for MCQ Genie
 * Contains API endpoints and app settings
 */

const CONFIG = {
    // API Base URL - Update this to match your backend
    API_BASE_URL: 'http://localhost:8000',
    
    // API Endpoints
    ENDPOINTS: {
        CHAT_MESSAGE: '/api/chat/message',
        CHAT_HISTORY: '/api/chat/history',
        CHAT_NEW_SESSION: '/api/chat/session/new',
        TEST_GENERATE: '/api/test/generate',
        TEST_SUBMIT: '/api/test/submit',
        TEST_GET: '/api/test',
        TEST_RESULT: '/api/test'
    },
    
    // App Settings
    SETTINGS: {
        DEFAULT_TEST_QUESTIONS: 10,
        MAX_TEST_QUESTIONS: 50,
        MIN_TEST_QUESTIONS: 5,
        TEST_TIME_LIMIT_MINUTES: 30,
        AUTO_ADVANCE_DELAY: 500 // ms delay after selecting an option
    }
};

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}
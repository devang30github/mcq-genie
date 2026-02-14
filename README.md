# MCQ Genie 🧞‍♂️

An AI-powered chatbot with intelligent MCQ test generation capabilities. Built with FastAPI, OpenRouter, and MongoDB.

## 🎯 Features

- **Interactive Chatbot**: Discuss any topic with AI-powered conversational interface
- **Dynamic MCQ Generation**: Generate multiple-choice questions on any topic using LLM
- **Intelligent Testing**: Take timed tests with instant evaluation
- **Score Analytics**: Get detailed performance feedback with explanations

## 🏗️ Project Structure
```
mcq-genie/
├── backend/
│   ├── app/
│   │   ├── config/          # Configuration and settings
│   │   ├── models/          # Pydantic schemas
│   │   ├── views/           # FastAPI route handlers
│   │   ├── controllers/     # Business logic layer
│   │   ├── services/        # External services (LLM, DB)
│   │   └── utils/           # Helper functions
│   ├── tests/               # Test suite
│   ├── main.py             # Application entry point
│   └── requirements.txt    # Python dependencies
└── frontend/
    ├── pages/              # HTML pages
    ├── css/                # Stylesheets
    ├── js/                 # JavaScript files
    └── assets/             # Static assets
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- MongoDB 4.4+
- OpenRouter API Key

### Backend Setup

1. **Navigate to backend directory**
```bash
   cd backend
```

2. **Create virtual environment**
```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
   pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
   cp .env.example .env
   # Edit .env and add your OpenRouter API key and MongoDB URL
```

5. **Run the application**
```bash
   python main.py
   # or
   uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
```bash
   cd frontend
```

2. **Open index.html in browser**
```bash
   # Simply open pages/index.html in your browser
   # or use a simple HTTP server:
   python -m http.server 3000
```

## 📚 API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔧 Technology Stack

**Backend:**
- FastAPI - Modern async web framework
- Motor - Async MongoDB driver
- OpenAI SDK - LLM integration via OpenRouter
- Pydantic - Data validation

**Frontend:**
- HTML5/CSS3
- Vanilla JavaScript
- Responsive design

**Database:**
- MongoDB - Document database for flexible schema

## 🎓 MVC Architecture

This project follows the Model-View-Controller pattern:

- **Models** (`app/models/`): Pydantic schemas for data validation
- **Views** (`app/views/`): FastAPI routers and endpoints
- **Controllers** (`app/controllers/`): Business logic and orchestration
- **Services** (`app/services/`): External integrations (LLM, Database)

## 🧪 Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## 📝 Environment Variables

Key environment variables (see `.env.example`):

- `OPENROUTER_API_KEY` - Your OpenRouter API key
- `MONGODB_URL` - MongoDB connection string
- `DEFAULT_MODEL` - LLM model to use
- `SECRET_KEY` - Application secret key

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## 📄 License

MIT License

## 🙏 Acknowledgments

- OpenRouter for LLM API access
- FastAPI for excellent async framework
- MongoDB for flexible data storage
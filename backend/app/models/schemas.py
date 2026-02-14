"""
Pydantic models for MCQ Genie application.
These define the data schemas for API requests and responses.
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ================ Enums ================

class DifficultyLevel(str, Enum):
    """MCQ difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class TestStatus(str, Enum):
    """Test session status."""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"


# ================ Chat Models ================

class ChatMessage(BaseModel):
    """Single chat message."""
    role: str = Field(..., description="Message role: user or assistant")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    """Request to send a chat message."""
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response from chat endpoint."""
    message: str
    session_id: str
    suggestions: Optional[List[str]] = None  # Suggested follow-up actions


# ================ MCQ Models ================

class MCQOption(BaseModel):
    """Single MCQ option."""
    option_id: str = Field(..., description="A, B, C, or D")
    text: str = Field(..., description="Option text")


class MCQuestion(BaseModel):
    """Single multiple-choice question."""
    question_id: str = Field(..., description="Unique question identifier")
    question_text: str = Field(..., description="The question")
    options: List[MCQOption] = Field(..., min_items=4, max_items=4)
    correct_answer: str = Field(..., description="Correct option ID (A/B/C/D)")
    explanation: Optional[str] = None
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    
    @validator('correct_answer')
    def validate_correct_answer(cls, v):
        """Ensure correct_answer is valid option."""
        if v not in ['A', 'B', 'C', 'D']:
            raise ValueError('correct_answer must be A, B, C, or D')
        return v


class MCQGenerationRequest(BaseModel):
    """Request to generate MCQs."""
    topic: str = Field(..., min_length=3, max_length=200)
    num_questions: int = Field(default=10, ge=1, le=50)
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    session_id: Optional[str] = None


class MCQGenerationResponse(BaseModel):
    """Response with generated MCQs."""
    test_id: str
    topic: str
    questions: List[MCQuestion]
    total_questions: int
    time_limit_minutes: int
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ================ Test Submission Models ================

class AnswerSubmission(BaseModel):
    """Single answer submission."""
    question_id: str
    selected_answer: str
    
    @validator('selected_answer')
    def validate_selected_answer(cls, v):
        """Ensure selected_answer is valid option."""
        if v not in ['A', 'B', 'C', 'D']:
            raise ValueError('selected_answer must be A, B, C, or D')
        return v


class TestSubmission(BaseModel):
    """Complete test submission."""
    test_id: str
    answers: List[AnswerSubmission]


class QuestionResult(BaseModel):
    """Result for a single question."""
    question_id: str
    question_text: str
    selected_answer: str
    correct_answer: str
    is_correct: bool
    explanation: Optional[str] = None


class TestResult(BaseModel):
    """Complete test evaluation result."""
    test_id: str
    topic: str
    total_questions: int
    correct_answers: int
    wrong_answers: int
    score_percentage: float
    results: List[QuestionResult]
    completed_at: datetime = Field(default_factory=datetime.utcnow)


# ================ Database Models ================

class ChatSessionDB(BaseModel):
    """Chat session stored in database."""
    session_id: str
    messages: List[ChatMessage]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TestSessionDB(BaseModel):
    """Test session stored in database."""
    test_id: str
    topic: str
    questions: List[MCQuestion]
    difficulty: DifficultyLevel
    status: TestStatus = TestStatus.IN_PROGRESS
    time_limit_minutes: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    submitted_at: Optional[datetime] = None
    answers: Optional[List[AnswerSubmission]] = None
    result: Optional[TestResult] = None
"""
Database Service for MongoDB operations.
Handles CRUD operations for chat sessions and test sessions.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models import (
    ChatSessionDB,
    TestSessionDB,
    ChatMessage,
    MCQuestion,
    AnswerSubmission,
    TestResult,
    TestStatus
)
from app.utils import generate_id


class DatabaseService:
    """Service for database operations."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize database service.
        
        Args:
            db: MongoDB database instance
        """
        self.db = db
        self.chat_sessions = db["chat_sessions"]
        self.test_sessions = db["test_sessions"]
    
    # ============= Chat Session Operations =============
    
    async def create_chat_session(self, initial_message: Optional[ChatMessage] = None) -> str:
        """
        Create a new chat session.
        
        Args:
            initial_message: Optional first message
        
        Returns:
            Session ID
        """
        session_id = generate_id("chat_")
        
        session = ChatSessionDB(
            session_id=session_id,
            messages=[initial_message] if initial_message else [],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        await self.chat_sessions.insert_one(session.dict())
        return session_id
    
    async def get_chat_session(self, session_id: str) -> Optional[ChatSessionDB]:
        """
        Get chat session by ID.
        
        Args:
            session_id: Session identifier
        
        Returns:
            ChatSessionDB or None if not found
        """
        session_data = await self.chat_sessions.find_one({"session_id": session_id})
        if session_data:
            return ChatSessionDB(**session_data)
        return None
    
    async def add_message_to_session(
        self,
        session_id: str,
        message: ChatMessage
    ) -> bool:
        """
        Add a message to existing chat session.
        
        Args:
            session_id: Session identifier
            message: Message to add
        
        Returns:
            True if successful, False otherwise
        """
        result = await self.chat_sessions.update_one(
            {"session_id": session_id},
            {
                "$push": {"messages": message.dict()},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        return result.modified_count > 0
    
    async def get_session_messages(self, session_id: str) -> List[ChatMessage]:
        """
        Get all messages from a session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            List of ChatMessage objects
        """
        session = await self.get_chat_session(session_id)
        if session:
            return session.messages
        return []
    
    # ============= Test Session Operations =============
    
    async def create_test_session(
        self,
        topic: str,
        questions: List[MCQuestion],
        difficulty: str,
        time_limit_minutes: int
    ) -> str:
        """
        Create a new test session.
        
        Args:
            topic: Test topic
            questions: List of MCQuestion objects
            difficulty: Difficulty level
            time_limit_minutes: Time limit in minutes
        
        Returns:
            Test ID
        """
        test_id = generate_id("test_")
        
        test_session = TestSessionDB(
            test_id=test_id,
            topic=topic,
            questions=questions,
            difficulty=difficulty,
            status=TestStatus.IN_PROGRESS,
            time_limit_minutes=time_limit_minutes,
            created_at=datetime.utcnow()
        )
        
        await self.test_sessions.insert_one(test_session.dict())
        return test_id
    
    async def get_test_session(self, test_id: str) -> Optional[TestSessionDB]:
        """
        Get test session by ID.
        
        Args:
            test_id: Test identifier
        
        Returns:
            TestSessionDB or None if not found
        """
        test_data = await self.test_sessions.find_one({"test_id": test_id})
        if test_data:
            return TestSessionDB(**test_data)
        return None
    
    async def submit_test_answers(
        self,
        test_id: str,
        answers: List[AnswerSubmission],
        result: TestResult
    ) -> bool:
        """
        Submit answers and result for a test.
        
        Args:
            test_id: Test identifier
            answers: List of answer submissions
            result: Test result
        
        Returns:
            True if successful, False otherwise
        """
        update_result = await self.test_sessions.update_one(
            {"test_id": test_id},
            {
                "$set": {
                    "answers": [answer.dict() for answer in answers],
                    "result": result.dict(),
                    "status": TestStatus.COMPLETED,
                    "submitted_at": datetime.utcnow()
                }
            }
        )
        return update_result.modified_count > 0
    
    async def get_test_questions(self, test_id: str) -> Optional[List[MCQuestion]]:
        """
        Get questions for a test (without answers).
        
        Args:
            test_id: Test identifier
        
        Returns:
            List of MCQuestion objects or None
        """
        test_session = await self.get_test_session(test_id)
        if test_session:
            # Return questions without exposing correct answers
            return test_session.questions
        return None
    
    async def get_test_result(self, test_id: str) -> Optional[TestResult]:
        """
        Get result for a completed test.
        
        Args:
            test_id: Test identifier
        
        Returns:
            TestResult or None
        """
        test_session = await self.get_test_session(test_id)
        if test_session and test_session.result:
            return test_session.result
        return None
    
    async def mark_test_expired(self, test_id: str) -> bool:
        """
        Mark a test as expired.
        
        Args:
            test_id: Test identifier
        
        Returns:
            True if successful, False otherwise
        """
        result = await self.test_sessions.update_one(
            {"test_id": test_id},
            {"$set": {"status": TestStatus.EXPIRED}}
        )
        return result.modified_count > 0
    
    # ============= Query Operations =============
    
    async def get_user_test_history(
        self,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent test history.
        
        Args:
            limit: Maximum number of tests to return
        
        Returns:
            List of test summary dictionaries
        """
        cursor = self.test_sessions.find(
            {},
            {
                "test_id": 1,
                "topic": 1,
                "difficulty": 1,
                "status": 1,
                "created_at": 1,
                "result.score_percentage": 1,
                "result.total_questions": 1
            }
        ).sort("created_at", -1).limit(limit)
        
        tests = await cursor.to_list(length=limit)
        return tests


# Dependency function for FastAPI
def get_db_service(db: AsyncIOMotorDatabase) -> DatabaseService:
    """
    Create DatabaseService instance.
    
    Args:
        db: MongoDB database instance
    
    Returns:
        DatabaseService instance
    """
    return DatabaseService(db)
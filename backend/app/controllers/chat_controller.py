"""
Chat Controller - Business logic for chat operations.
Orchestrates between LLM service and database service.
"""
from typing import List, Dict, Optional
from datetime import datetime

from app.models import ChatMessage, ChatRequest, ChatResponse
from app.services import get_llm_service, DatabaseService
from app.utils import generate_id


class ChatController:
    """Controller for chat-related business logic."""
    
    def __init__(self, db_service: DatabaseService):
        """
        Initialize chat controller.
        
        Args:
            db_service: Database service instance
        """
        self.db_service = db_service
        self.llm_service = get_llm_service()
    
    async def process_chat_message(
        self,
        request: ChatRequest
    ) -> ChatResponse:
        """
        Process a chat message and generate response.
        
        Args:
            request: Chat request with message and optional session_id
        
        Returns:
            ChatResponse with assistant's reply
        """
        # Get or create session
        session_id = request.session_id
        if not session_id:
            session_id = await self.db_service.create_chat_session()
        
        # Verify session exists
        session = await self.db_service.get_chat_session(session_id)
        if not session:
            # Create new session if not found
            session_id = await self.db_service.create_chat_session()
        
        # Create user message
        user_message = ChatMessage(
            role="user",
            content=request.message,
            timestamp=datetime.utcnow()
        )
        
        # Save user message to database
        await self.db_service.add_message_to_session(session_id, user_message)
        
        # Get conversation history
        history = await self.db_service.get_session_messages(session_id)
        
        # Build messages for LLM
        llm_messages = self._build_llm_messages(history)
        
        # Get LLM response
        assistant_content = await self.llm_service.chat_completion(
            messages=llm_messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Create assistant message
        assistant_message = ChatMessage(
            role="assistant",
            content=assistant_content,
            timestamp=datetime.utcnow()
        )
        
        # Save assistant message to database
        await self.db_service.add_message_to_session(session_id, assistant_message)
        
        # Generate suggestions based on conversation
        suggestions = await self._generate_suggestions(request.message, assistant_content)
        
        return ChatResponse(
            message=assistant_content,
            session_id=session_id,
            suggestions=suggestions
        )
    
    async def get_chat_history(self, session_id: str) -> List[ChatMessage]:
        """
        Get chat history for a session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            List of chat messages
        """
        messages = await self.db_service.get_session_messages(session_id)
        return messages
    
    async def create_new_session(self) -> str:
        """
        Create a new chat session.
        
        Returns:
            New session ID
        """
        session_id = await self.db_service.create_chat_session()
        return session_id
    
    def _build_llm_messages(self, history: List[ChatMessage]) -> List[Dict[str, str]]:
        """
        Build messages list for LLM from chat history.
        
        Args:
            history: List of ChatMessage objects
        
        Returns:
            List of message dictionaries for LLM
        """
        # System message for chatbot behavior
        system_message = {
            "role": "system",
            "content": """You are MCQ Genie, a helpful AI assistant specialized in education and learning.

Your capabilities:
1. Answer questions on any topic clearly and accurately
2. Explain complex concepts in simple terms
3. Help users learn through conversation
4. Generate quiz questions when requested

Guidelines:
- Be conversational and friendly
- Provide clear, concise explanations
- Use examples when helpful
- If user wants to test their knowledge, suggest generating a quiz
- Stay on topic and educational

Remember: Your goal is to help users learn effectively."""
        }
        
        # Convert history to LLM format
        llm_messages = [system_message]
        for msg in history:
            llm_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        return llm_messages
    
    async def _generate_suggestions(
        self,
        user_message: str,
        assistant_response: str
    ) -> List[str]:
        """
        Generate smart follow-up suggestions.
        
        Args:
            user_message: User's message
            assistant_response: Assistant's response
        
        Returns:
            List of suggestion strings
        """
        # Check if conversation is about a learnable topic
        keywords = ["explain", "what is", "how does", "tell me about", "learn", "understand"]
        
        if any(keyword in user_message.lower() for keyword in keywords):
            # Generate contextual suggestions
            try:
                suggestions = await self.llm_service.generate_chat_suggestions(user_message)
                return suggestions
            except Exception as e:
                print(f"⚠️ Could not generate suggestions: {str(e)}")
                return self._default_suggestions()
        else:
            return self._default_suggestions()
    
    def _default_suggestions(self) -> List[str]:
        """Get default suggestions."""
        return [
            "Generate a quiz on this topic",
            "Explain in more detail",
            "Give me some examples"
        ]
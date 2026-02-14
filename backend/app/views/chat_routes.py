"""
Chat Routes - API endpoints for chat functionality.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.models import ChatRequest, ChatResponse, ChatMessage
from app.controllers import ChatController
from app.services import get_db_service, DatabaseService
from app.config.database import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase


router = APIRouter()


def get_chat_controller(
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> ChatController:
    """
    Dependency to get ChatController instance.
    
    Args:
        db: Database dependency
    
    Returns:
        ChatController instance
    """
    db_service = get_db_service(db)
    return ChatController(db_service)


@router.post("/message", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def send_message(
    request: ChatRequest,
    controller: ChatController = Depends(get_chat_controller)
):
    """
    Send a message and get AI response.
    
    Args:
        request: Chat request with message and optional session_id
        controller: Chat controller dependency
    
    Returns:
        ChatResponse with assistant's reply and suggestions
    
    Raises:
        HTTPException: If message processing fails
    """
    try:
        response = await controller.process_chat_message(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )


@router.get("/history/{session_id}", response_model=List[ChatMessage])
async def get_chat_history(
    session_id: str,
    controller: ChatController = Depends(get_chat_controller)
):
    """
    Get chat history for a session.
    
    Args:
        session_id: Chat session identifier
        controller: Chat controller dependency
    
    Returns:
        List of chat messages
    
    Raises:
        HTTPException: If session not found
    """
    try:
        messages = await controller.get_chat_history(session_id)
        if not messages:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session not found: {session_id}"
            )
        return messages
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve history: {str(e)}"
        )


@router.post("/session/new", status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    controller: ChatController = Depends(get_chat_controller)
):
    """
    Create a new chat session.
    
    Args:
        controller: Chat controller dependency
    
    Returns:
        Dictionary with new session_id
    
    Raises:
        HTTPException: If session creation fails
    """
    try:
        session_id = await controller.create_new_session()
        return {
            "session_id": session_id,
            "message": "New chat session created"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )


@router.get("/session/{session_id}/exists")
async def check_session_exists(
    session_id: str,
    controller: ChatController = Depends(get_chat_controller)
):
    """
    Check if a chat session exists.
    
    Args:
        session_id: Chat session identifier
        controller: Chat controller dependency
    
    Returns:
        Dictionary with exists boolean
    """
    try:
        messages = await controller.get_chat_history(session_id)
        exists = len(messages) > 0
        return {
            "session_id": session_id,
            "exists": exists,
            "message_count": len(messages)
        }
    except Exception as e:
        return {
            "session_id": session_id,
            "exists": False,
            "message_count": 0
        }
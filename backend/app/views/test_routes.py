"""
Test Routes - API endpoints for MCQ test functionality.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional

from app.models import (
    MCQGenerationRequest,
    MCQGenerationResponse,
    TestSubmission,
    TestResult
)
from app.controllers import TestController
from app.services import get_db_service, DatabaseService
from app.config.database import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase


router = APIRouter()


def get_test_controller(
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> TestController:
    """
    Dependency to get TestController instance.
    
    Args:
        db: Database dependency
    
    Returns:
        TestController instance
    """
    db_service = get_db_service(db)
    return TestController(db_service)


@router.post("/generate", response_model=MCQGenerationResponse, status_code=status.HTTP_201_CREATED)
async def generate_test(
    request: MCQGenerationRequest,
    controller: TestController = Depends(get_test_controller)
):
    """
    Generate a new MCQ test on a given topic.
    
    Args:
        request: Test generation request with topic, num_questions, difficulty
        controller: Test controller dependency
    
    Returns:
        MCQGenerationResponse with test details and questions
    
    Raises:
        HTTPException: If test generation fails
    """
    try:
        response = await controller.generate_test(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate test: {str(e)}"
        )


@router.post("/submit", response_model=TestResult, status_code=status.HTTP_200_OK)
async def submit_test(
    submission: TestSubmission,
    controller: TestController = Depends(get_test_controller)
):
    """
    Submit answers for a test and get results.
    
    Args:
        submission: Test submission with test_id and answers
        controller: Test controller dependency
    
    Returns:
        TestResult with score and detailed feedback
    
    Raises:
        HTTPException: If submission fails or test not found
    """
    try:
        result = await controller.submit_test(submission)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit test: {str(e)}"
        )


@router.get("/{test_id}", response_model=MCQGenerationResponse)
async def get_test(
    test_id: str,
    controller: TestController = Depends(get_test_controller)
):
    """
    Get test details by ID (for taking the test).
    
    Args:
        test_id: Test identifier
        controller: Test controller dependency
    
    Returns:
        Test details with questions (answers hidden)
    
    Raises:
        HTTPException: If test not found
    """
    try:
        test = await controller.get_test_details(test_id)
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test not found: {test_id}"
            )
        return test
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve test: {str(e)}"
        )


@router.get("/{test_id}/result", response_model=TestResult)
async def get_test_result(
    test_id: str,
    controller: TestController = Depends(get_test_controller)
):
    """
    Get result for a completed test.
    
    Args:
        test_id: Test identifier
        controller: Test controller dependency
    
    Returns:
        TestResult with score and feedback
    
    Raises:
        HTTPException: If result not found (test not submitted yet)
    """
    try:
        result = await controller.get_test_result(test_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Result not found for test: {test_id}. Test may not be submitted yet."
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve result: {str(e)}"
        )


@router.get("/{test_id}/status")
async def get_test_status(
    test_id: str,
    controller: TestController = Depends(get_test_controller)
):
    """
    Get test status (in_progress, completed, expired).
    
    Args:
        test_id: Test identifier
        controller: Test controller dependency
    
    Returns:
        Dictionary with test status information
    
    Raises:
        HTTPException: If test not found
    """
    try:
        test_details = await controller.get_test_details(test_id)
        if not test_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test not found: {test_id}"
            )
        
        # Check if result exists
        result = await controller.get_test_result(test_id)
        
        return {
            "test_id": test_id,
            "topic": test_details.topic,
            "status": "completed" if result else "in_progress",
            "total_questions": test_details.total_questions,
            "time_limit_minutes": test_details.time_limit_minutes,
            "created_at": test_details.created_at
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get test status: {str(e)}"
        )
"""
Test Controller - Business logic for MCQ test operations.
Handles test generation, submission, and evaluation.
"""
from typing import List, Optional
from datetime import datetime

from app.models import (
    MCQGenerationRequest,
    MCQGenerationResponse,
    TestSubmission,
    TestResult,
    QuestionResult,
    MCQuestion,
    AnswerSubmission,
    DifficultyLevel,
    TestStatus
)
from app.services import get_llm_service, DatabaseService
from app.config import get_settings
from app.utils import calculate_score_percentage, generate_id


class TestController:
    """Controller for test-related business logic."""
    
    def __init__(self, db_service: DatabaseService):
        """
        Initialize test controller.
        
        Args:
            db_service: Database service instance
        """
        self.db_service = db_service
        self.llm_service = get_llm_service()
        self.settings = get_settings()
    
    async def generate_test(
        self,
        request: MCQGenerationRequest
    ) -> MCQGenerationResponse:
        """
        Generate a new MCQ test.
        
        Args:
            request: Test generation request
        
        Returns:
            MCQGenerationResponse with test details
        """
        # Validate number of questions
        num_questions = min(request.num_questions, self.settings.max_mcq_count)
        
        # Generate MCQs using LLM
        questions = await self.llm_service.generate_mcqs(
            topic=request.topic,
            num_questions=num_questions,
            difficulty=request.difficulty
        )
        
        # Create test session in database
        test_id = await self.db_service.create_test_session(
            topic=request.topic,
            questions=questions,
            difficulty=request.difficulty,
            time_limit_minutes=self.settings.test_time_limit_minutes
        )
        
        # Prepare questions for response (hide correct answers)
        public_questions = self._prepare_public_questions(questions)
        
        return MCQGenerationResponse(
            test_id=test_id,
            topic=request.topic,
            questions=public_questions,
            total_questions=len(questions),
            time_limit_minutes=self.settings.test_time_limit_minutes,
            created_at=datetime.utcnow()
        )
    
    async def submit_test(
        self,
        submission: TestSubmission
    ) -> TestResult:
        """
        Submit and evaluate a test.
        
        Args:
            submission: Test submission with answers
        
        Returns:
            TestResult with score and detailed feedback
        """
        # Get test session
        test_session = await self.db_service.get_test_session(submission.test_id)
        
        if not test_session:
            raise ValueError(f"Test not found: {submission.test_id}")
        
        if test_session.status == TestStatus.COMPLETED:
            raise ValueError("Test already submitted")
        
        if test_session.status == TestStatus.EXPIRED:
            raise ValueError("Test has expired")
        
        # Evaluate answers
        result = self._evaluate_test(
            test_session.questions,
            submission.answers,
            test_session.topic
        )
        
        # Save submission to database
        await self.db_service.submit_test_answers(
            test_id=submission.test_id,
            answers=submission.answers,
            result=result
        )
        
        return result
    
    async def get_test_details(self, test_id: str) -> Optional[MCQGenerationResponse]:
        """
        Get test details (for taking the test).
        
        Args:
            test_id: Test identifier
        
        Returns:
            Test details or None if not found
        """
        test_session = await self.db_service.get_test_session(test_id)
        
        if not test_session:
            return None
        
        # Prepare questions without answers
        public_questions = self._prepare_public_questions(test_session.questions)
        
        return MCQGenerationResponse(
            test_id=test_session.test_id,
            topic=test_session.topic,
            questions=public_questions,
            total_questions=len(test_session.questions),
            time_limit_minutes=test_session.time_limit_minutes,
            created_at=test_session.created_at
        )
    
    async def get_test_result(self, test_id: str) -> Optional[TestResult]:
        """
        Get result for a completed test.
        
        Args:
            test_id: Test identifier
        
        Returns:
            TestResult or None if not found
        """
        result = await self.db_service.get_test_result(test_id)
        return result
    
    def _prepare_public_questions(self, questions: List[MCQuestion]) -> List[MCQuestion]:
        """
        Prepare questions for public viewing (hide correct answers).
        
        Args:
            questions: List of MCQuestion objects
        
        Returns:
            List of questions without correct answers exposed
        """
        public_questions = []
        for q in questions:
            # Create a copy without correct answer in response
            public_q = MCQuestion(
                question_id=q.question_id,
                question_text=q.question_text,
                options=q.options,
                correct_answer="",  # Don't expose correct answer
                explanation=None,    # Don't expose explanation yet
                difficulty=q.difficulty
            )
            public_questions.append(public_q)
        
        return public_questions
    
    def _evaluate_test(
        self,
        questions: List[MCQuestion],
        answers: List[AnswerSubmission],
        topic: str
    ) -> TestResult:
        """
        Evaluate test submission.
        
        Args:
            questions: Original questions with correct answers
            answers: User's answer submissions
            topic: Test topic
        
        Returns:
            TestResult with evaluation
        """
        # Create answer map for quick lookup
        answer_map = {ans.question_id: ans.selected_answer for ans in answers}
        
        # Evaluate each question
        results = []
        correct_count = 0
        
        for question in questions:
            selected = answer_map.get(question.question_id, "")
            is_correct = selected == question.correct_answer
            
            if is_correct:
                correct_count += 1
            
            result = QuestionResult(
                question_id=question.question_id,
                question_text=question.question_text,
                selected_answer=selected if selected else "Not answered",
                correct_answer=question.correct_answer,
                is_correct=is_correct,
                explanation=question.explanation
            )
            results.append(result)
        
        # Calculate score
        total_questions = len(questions)
        wrong_count = total_questions - correct_count
        score = calculate_score_percentage(correct_count, total_questions)
        
        return TestResult(
            test_id=questions[0].question_id.split("_")[0] if questions else "unknown",
            topic=topic,
            total_questions=total_questions,
            correct_answers=correct_count,
            wrong_answers=wrong_count,
            score_percentage=score,
            results=results,
            completed_at=datetime.utcnow()
        )
    
    async def regenerate_question(
        self,
        test_id: str,
        question_id: str
    ) -> Optional[MCQuestion]:
        """
        Regenerate a single question (future feature).
        
        Args:
            test_id: Test identifier
            question_id: Question to regenerate
        
        Returns:
            New MCQuestion or None
        """
        # TODO: Implement question regeneration
        # This could be useful if a user finds a question confusing
        pass
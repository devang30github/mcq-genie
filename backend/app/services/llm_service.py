"""
LLM Service for OpenRouter API integration.
Handles chat completion and structured MCQ generation.
"""
from openai import AsyncOpenAI
from typing import List, Dict, Any, Optional
import json
from app.config import get_settings
from app.models import MCQuestion, MCQOption, DifficultyLevel


class LLMService:
    """Service for interacting with LLM via OpenRouter."""
    
    def __init__(self):
        """Initialize OpenAI client with OpenRouter configuration."""
        settings = get_settings()
        self.client = AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url
        )
        self.default_model = settings.default_model
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Get chat completion from LLM.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (defaults to settings.default_model)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
        
        Returns:
            Assistant's response content
        """
        try:
            response = await self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ LLM Error: {str(e)}")
            raise Exception(f"Failed to get LLM response: {str(e)}")
    
    async def generate_mcqs(
        self,
        topic: str,
        num_questions: int,
        difficulty: DifficultyLevel
    ) -> List[MCQuestion]:
        """
        Generate MCQs on a given topic using structured output.
        
        Args:
            topic: Topic for MCQ generation
            num_questions: Number of questions to generate
            difficulty: Difficulty level (easy/medium/hard)
        
        Returns:
            List of MCQuestion objects
        """
        system_prompt = self._build_mcq_system_prompt(difficulty)
        user_prompt = self._build_mcq_user_prompt(topic, num_questions)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            # Get response from LLM
            response = await self.chat_completion(
                messages=messages,
                temperature=0.8,  # More creative for question generation
                max_tokens=4000   # Larger for multiple questions
            )
            
            # Parse JSON response
            mcqs_data = self._parse_mcq_response(response)
            
            # Convert to MCQuestion objects
            questions = []
            for idx, mcq in enumerate(mcqs_data):
                question = MCQuestion(
                    question_id=f"q_{idx + 1}",
                    question_text=mcq["question"],
                    options=[
                        MCQOption(option_id="A", text=mcq["options"]["A"]),
                        MCQOption(option_id="B", text=mcq["options"]["B"]),
                        MCQOption(option_id="C", text=mcq["options"]["C"]),
                        MCQOption(option_id="D", text=mcq["options"]["D"])
                    ],
                    correct_answer=mcq["correct_answer"],
                    explanation=mcq.get("explanation", ""),
                    difficulty=difficulty
                )
                questions.append(question)
            
            return questions
        
        except Exception as e:
            print(f"❌ MCQ Generation Error: {str(e)}")
            raise Exception(f"Failed to generate MCQs: {str(e)}")
    
    def _build_mcq_system_prompt(self, difficulty: DifficultyLevel) -> str:
        """Build system prompt for MCQ generation."""
        difficulty_guidance = {
            DifficultyLevel.EASY: "Create straightforward questions testing basic knowledge and recall.",
            DifficultyLevel.MEDIUM: "Create questions requiring understanding and application of concepts.",
            DifficultyLevel.HARD: "Create challenging questions requiring analysis, synthesis, and critical thinking."
        }
        
        return f"""You are an expert educational content creator specializing in multiple-choice questions.

**Your Task:** Generate high-quality MCQs that are clear, unambiguous, and educationally valuable.

**Difficulty Level:** {difficulty.value.upper()}
{difficulty_guidance[difficulty]}

**Requirements:**
1. Each question must have exactly 4 options (A, B, C, D)
2. Only ONE option should be correct
3. Distractors (wrong options) should be plausible but clearly incorrect
4. Avoid "All of the above" or "None of the above" options
5. Questions should be clear and unambiguous
6. Provide a brief explanation for the correct answer

**Output Format:** 
Respond with ONLY a valid JSON array. No additional text before or after.

Example format:
[
  {{
    "question": "What is the capital of France?",
    "options": {{
      "A": "London",
      "B": "Paris",
      "C": "Berlin",
      "D": "Madrid"
    }},
    "correct_answer": "B",
    "explanation": "Paris is the capital and largest city of France."
  }}
]"""
    
    def _build_mcq_user_prompt(self, topic: str, num_questions: int) -> str:
        """Build user prompt for MCQ generation."""
        return f"""Generate {num_questions} multiple-choice questions about: {topic}

Remember to respond with ONLY the JSON array, no other text."""
    
    def _parse_mcq_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Parse LLM response to extract MCQ data.
        
        Args:
            response: Raw LLM response
        
        Returns:
            List of MCQ dictionaries
        """
        # Remove markdown code blocks if present
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        
        response = response.strip()
        
        try:
            mcqs = json.loads(response)
            if not isinstance(mcqs, list):
                raise ValueError("Response is not a list")
            return mcqs
        except json.JSONDecodeError as e:
            print(f"❌ JSON Parse Error: {str(e)}")
            print(f"Response was: {response[:200]}...")
            raise Exception("Failed to parse MCQ response as JSON")
    
    async def generate_chat_suggestions(self, topic: str) -> List[str]:
        """
        Generate follow-up suggestions based on chat topic.
        
        Args:
            topic: Current conversation topic
        
        Returns:
            List of suggestion strings
        """
        prompt = f"""Based on the topic "{topic}", suggest 3 brief follow-up actions a user might want to take.

Format as JSON array of strings. Keep each suggestion under 10 words.

Example: ["Take a quiz on this topic", "Learn advanced concepts", "Get practice problems"]

Respond with ONLY the JSON array."""
        
        try:
            response = await self.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )
            
            # Parse suggestions
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            suggestions = json.loads(response)
            return suggestions[:3]  # Return max 3 suggestions
        
        except Exception as e:
            print(f"⚠️ Suggestion generation failed: {str(e)}")
            # Return default suggestions on error
            return [
                "Generate a quiz on this topic",
                "Ask me more questions",
                "Explain in simpler terms"
            ]


# Singleton instance
_llm_service = None


def get_llm_service() -> LLMService:
    """Get or create LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
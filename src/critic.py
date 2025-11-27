"""
Critic Agent for SkillAssessGPT.

This module contains the CriticAgent class that validates the pedagogical
coherence and quality of generated APC assessments using Google Gemini LLM.
"""

import json
import time
from typing import Optional
import google.generativeai as genai

from src.models import AssessmentOutput, ValidationResult


class CriticAgent:
    """
    Critic agent that validates APC assessment quality using Google Gemini LLM.
    
    This agent checks alignment between competency and criteria, verifies
    observability of criteria, and validates coherence between task complexity
    and competency level.
    """
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        """
        Initialize the critic agent.
        
        Args:
            api_key: Google API key
            model: Model name to use (default: "gemini-2.5-flash")
        """
        self.api_key = api_key
        self.model = model
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(model)
        self.max_retries = 3
        self.initial_retry_delay = 1  # seconds
    
    def _build_validation_prompt(self, assessment: AssessmentOutput) -> str:
        """
        Build the validation prompt for the LLM.
        
        Args:
            assessment: The assessment output to validate
            
        Returns:
            Formatted validation prompt string
        """
        # Convert assessment to a readable format for the LLM
        assessment_json = json.dumps(assessment.to_dict(), ensure_ascii=False, indent=2)
        
        prompt = f"""Vous êtes un validateur de qualité pédagogique pour les évaluations par compétences (APC).

Votre tâche est d'analyser l'évaluation suivante et de valider sa qualité selon ces critères :

1. **Alignement** : Les critères d'évaluation sont-ils bien alignés avec la compétence visée ?
2. **Observabilité** : Tous les critères sont-ils observables et mesurables ?
3. **Cohérence** : La complexité de la tâche correspond-elle au niveau de compétence et au niveau éducatif ?

**Évaluation à valider** :
```json
{assessment_json}
```

Analysez cette évaluation et fournissez votre validation au format JSON suivant :

{{
  "is_valid": true/false,
  "alignment_score": "good" / "acceptable" / "poor",
  "observability_issues": [
    "Liste des problèmes d'observabilité identifiés"
  ],
  "coherence_issues": [
    "Liste des problèmes de cohérence identifiés"
  ],
  "feedback": "Feedback détaillé et spécifique sur les problèmes identifiés ou confirmation de la qualité"
}}

**Soyez concis dans votre feedback.** Répondez UNIQUEMENT avec le JSON, sans texte supplémentaire."""
        
        return prompt
    
    def validate_assessment(self, assessment: AssessmentOutput) -> ValidationResult:
        """
        Validate an assessment using the Google Gemini API.
        
        This method calls the LLM with retry logic and parses the validation
        response into a ValidationResult object.
        
        Args:
            assessment: The assessment output to validate
            
        Returns:
            ValidationResult object with validation status and feedback
            
        Raises:
            Exception: If API call fails after all retries or response is invalid
        """
        prompt = self._build_validation_prompt(assessment)
        
        # Retry logic with exponential backoff
        for attempt in range(self.max_retries):
            try:
                response = self._call_api(prompt)
                validation = self._parse_validation_response(response)
                return validation
            except Exception as e:
                if attempt < self.max_retries - 1:
                    delay = self.initial_retry_delay * (2 ** attempt)
                    print(f"Validation API call failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    # If all retries fail, return a "not completed" validation
                    print(f"Validation failed after {self.max_retries} attempts: {str(e)}")
                    return ValidationResult(
                        is_valid=False,
                        alignment_score="",
                        observability_issues=[],
                        coherence_issues=[],
                        feedback=f"Validation could not be completed due to API error: {str(e)}"
                    )
    
    def _call_api(self, prompt: str) -> str:
        """
        Call the Google Gemini API with the given prompt.
        
        Args:
            prompt: The validation prompt to send to the LLM
            
        Returns:
            API response text
            
        Raises:
            Exception: If API call fails
        """
        try:
            response = self.client.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,  # Lower temperature for more consistent validation
                    max_output_tokens=3000,  # Optimized for concise validation
                ),
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                ]
            )
            
            # Check if response was blocked or incomplete
            if not response.candidates:
                raise Exception("Response was blocked or empty")
            
            candidate = response.candidates[0]
            if candidate.finish_reason != 1:  # 1 = STOP (normal completion)
                finish_reasons = {
                    2: "MAX_TOKENS - Response exceeded token limit",
                    3: "SAFETY - Response blocked by safety filters",
                    4: "RECITATION - Response blocked due to recitation",
                    5: "OTHER - Response stopped for other reasons"
                }
                reason = finish_reasons.get(candidate.finish_reason, f"Unknown reason: {candidate.finish_reason}")
                raise Exception(f"Response incomplete: {reason}")
            
            return response.text
        except Exception as e:
            raise Exception(f"Validation API request failed: {str(e)}")
    
    def _parse_validation_response(self, api_response: str) -> ValidationResult:
        """
        Parse the API validation response into a ValidationResult object.
        
        Args:
            api_response: Raw API response text
            
        Returns:
            ValidationResult object
            
        Raises:
            Exception: If response format is invalid or missing required fields
        """
        try:
            # Extract the content from the API response
            content = api_response
            
            if not content:
                raise ValueError("Empty response from validation API")
            
            # Try to extract JSON from the content
            # Sometimes LLMs wrap JSON in markdown code blocks
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            # Parse JSON
            data = json.loads(content)
            
            # Validate required fields
            if "is_valid" not in data:
                raise ValueError("Missing 'is_valid' in validation response")
            
            # Create ValidationResult
            validation = ValidationResult(
                is_valid=data.get("is_valid", False),
                alignment_score=data.get("alignment_score", ""),
                observability_issues=data.get("observability_issues", []),
                coherence_issues=data.get("coherence_issues", []),
                feedback=data.get("feedback", "")
            )
            
            return validation
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse validation JSON response: {str(e)}\nContent: {content[:200]}")
        except ValueError as e:
            raise Exception(f"Invalid validation response format: {str(e)}")
        except Exception as e:
            raise Exception(f"Error parsing validation response: {str(e)}")

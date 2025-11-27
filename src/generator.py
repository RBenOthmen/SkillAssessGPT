"""
Generator Agent for SkillAssessGPT.

This module contains the GeneratorAgent class that uses Google Gemini LLM
to generate APC assessment grids, evaluation situations, and scoring rubrics.
"""

import json
import time
from typing import Optional
import google.generativeai as genai

from src.models import (
    CompetencyInput,
    AssessmentOutput,
    APCGrid,
    Criterion,
    EvaluationSituation,
    ScoringRubric
)


class GeneratorAgent:
    """
    Generator agent that creates APC assessment materials using Google Gemini LLM.
    
    This agent constructs detailed prompts and calls the Gemini API to generate
    structured assessment grids with ND/NI/NA levels, authentic evaluation situations,
    and scoring rubrics.
    """
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        """
        Initialize the generator agent.
        
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
    
    def _build_prompt(self, input_data: CompetencyInput) -> str:
        """
        Build the detailed prompt for the LLM.
        
        Args:
            input_data: Competency input with context parameters
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Vous êtes un expert en ingénierie pédagogique spécialisé dans l'évaluation par compétences (APC).

Générez une grille d'évaluation APC complète et une situation d'évaluation authentique basées sur les informations suivantes :

**Compétence** : {input_data.competency}
"""
        
        if input_data.element:
            prompt += f"**Élément de compétence** : {input_data.element}\n"
        
        prompt += f"""**Niveau** : {input_data.niveau}
**Parcours** : {input_data.parcours}
**Spécialité** : {input_data.specialite}
**Durée** : {input_data.duree}

Votre réponse doit être au format JSON avec la structure suivante :

{{
  "grid": {{
    "nd_criteria": [
      {{
        "description": "Description du critère",
        "indicators": ["Indicateur 1", "Indicateur 2"],
        "points": 2
      }}
    ],
    "ni_criteria": [
      {{
        "description": "Description du critère",
        "indicators": ["Indicateur 1", "Indicateur 2"],
        "points": 3
      }}
    ],
    "na_criteria": [
      {{
        "description": "Description du critère",
        "indicators": ["Indicateur 1", "Indicateur 2"],
        "points": 4
      }}
    ]
  }},
  "situation": {{
    "context": "Description du contexte authentique",
    "task": "Description de la tâche complexe",
    "instructions": "Instructions claires pour les étudiants",
    "duration": "{input_data.duree}"
  }},
  "rubric": {{
    "total_points": 20,
    "nd_range": [0, 6],
    "ni_range": [7, 13],
    "na_range": [14, 20],
    "criteria_points": {{
      "Critère 1": 2,
      "Critère 2": 3
    }}
  }}
}}

**Exigences importantes** :
1. Chaque niveau (ND, NI, NA) doit avoir EXACTEMENT 3 critères (pas plus)
2. Chaque critère doit avoir MAXIMUM 2 indicateurs concis
3. Les descriptions doivent être courtes et précises
4. Le barème doit totaliser exactement 20 points
5. Tous les critères doivent avoir des points > 0

Répondez UNIQUEMENT avec le JSON, sans texte supplémentaire. Soyez concis."""
        
        return prompt

    def generate_assessment(self, input_data: CompetencyInput) -> AssessmentOutput:
        """
        Generate a complete assessment using the Google Gemini API.
        
        This method calls the LLM with retry logic and parses the response
        into a structured AssessmentOutput object.
        
        Args:
            input_data: Competency input with context parameters
            
        Returns:
            AssessmentOutput object with grid, situation, and rubric
            
        Raises:
            Exception: If API call fails after all retries or response is invalid
        """
        prompt = self._build_prompt(input_data)
        
        # Retry logic with exponential backoff
        for attempt in range(self.max_retries):
            try:
                response = self._call_api(prompt)
                assessment = self._parse_response(response, input_data)
                return assessment
            except Exception as e:
                if attempt < self.max_retries - 1:
                    delay = self.initial_retry_delay * (2 ** attempt)
                    print(f"API call failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    raise Exception(f"Failed to generate assessment after {self.max_retries} attempts: {str(e)}")
    
    def _call_api(self, prompt: str) -> str:
        """
        Call the Google Gemini API with the given prompt.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            API response text
            
        Raises:
            Exception: If API call fails
        """
        try:
            response = self.client.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=6000,  # Optimized for concise responses
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
            raise Exception(f"API request failed: {str(e)}")
    
    def _parse_response(self, api_response: str, input_data: CompetencyInput) -> AssessmentOutput:
        """
        Parse the API response into an AssessmentOutput object.
        
        Args:
            api_response: Raw API response text
            input_data: Original competency input
            
        Returns:
            AssessmentOutput object
            
        Raises:
            Exception: If response format is invalid or missing required fields
        """
        try:
            # Extract the content from the API response
            content = api_response
            
            if not content:
                raise ValueError("Empty response from API")
            
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
            if "grid" not in data:
                raise ValueError("Missing 'grid' in response")
            if "situation" not in data:
                raise ValueError("Missing 'situation' in response")
            if "rubric" not in data:
                raise ValueError("Missing 'rubric' in response")
            
            # Parse grid
            grid_data = data["grid"]
            nd_criteria = [Criterion.from_dict(c) for c in grid_data.get("nd_criteria", [])]
            ni_criteria = [Criterion.from_dict(c) for c in grid_data.get("ni_criteria", [])]
            na_criteria = [Criterion.from_dict(c) for c in grid_data.get("na_criteria", [])]
            
            grid = APCGrid(
                nd_criteria=nd_criteria,
                ni_criteria=ni_criteria,
                na_criteria=na_criteria
            )
            
            # Parse situation
            situation_data = data["situation"]
            situation = EvaluationSituation(
                context=situation_data.get("context", ""),
                task=situation_data.get("task", ""),
                instructions=situation_data.get("instructions", ""),
                duration=situation_data.get("duration", input_data.duree)
            )
            
            # Parse rubric
            rubric_data = data["rubric"]
            rubric = ScoringRubric(
                total_points=rubric_data.get("total_points", 20),
                nd_range=tuple(rubric_data.get("nd_range", [0, 0])),
                ni_range=tuple(rubric_data.get("ni_range", [0, 0])),
                na_range=tuple(rubric_data.get("na_range", [0, 0])),
                criteria_points=rubric_data.get("criteria_points", {})
            )
            
            # Create and return AssessmentOutput
            assessment = AssessmentOutput(
                input=input_data,
                grid=grid,
                situation=situation,
                rubric=rubric
            )
            
            return assessment
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON response: {str(e)}\nContent: {content[:200]}")
        except ValueError as e:
            raise Exception(f"Invalid response format: {str(e)}")
        except Exception as e:
            raise Exception(f"Error parsing response: {str(e)}")

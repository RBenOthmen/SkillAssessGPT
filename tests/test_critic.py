"""
Tests for the CriticAgent class.
"""

import pytest
from unittest.mock import Mock, patch
from src.critic import CriticAgent
from src.models import (
    CompetencyInput,
    AssessmentOutput,
    APCGrid,
    Criterion,
    EvaluationSituation,
    ScoringRubric,
    ValidationResult
)


def create_sample_assessment():
    """Create a sample assessment for testing."""
    input_data = CompetencyInput(
        competency="Développer une application web",
        element="Backend API",
        niveau="Licence 2",
        parcours="Informatique",
        specialite="Développement Web",
        duree="2 heures"
    )
    
    grid = APCGrid(
        nd_criteria=[
            Criterion("Critère ND 1", ["Indicateur 1", "Indicateur 2"], 2),
            Criterion("Critère ND 2", ["Indicateur 1", "Indicateur 2"], 2),
            Criterion("Critère ND 3", ["Indicateur 1", "Indicateur 2"], 2)
        ],
        ni_criteria=[
            Criterion("Critère NI 1", ["Indicateur 1", "Indicateur 2"], 3),
            Criterion("Critère NI 2", ["Indicateur 1", "Indicateur 2"], 3),
            Criterion("Critère NI 3", ["Indicateur 1", "Indicateur 2"], 3)
        ],
        na_criteria=[
            Criterion("Critère NA 1", ["Indicateur 1", "Indicateur 2"], 5),
            Criterion("Critère NA 2", ["Indicateur 1", "Indicateur 2"], 5),
            Criterion("Critère NA 3", ["Indicateur 1", "Indicateur 2"], 5)
        ]
    )
    
    situation = EvaluationSituation(
        context="Contexte authentique",
        task="Tâche complexe",
        instructions="Instructions claires",
        duration="2 heures"
    )
    
    rubric = ScoringRubric(
        total_points=20,
        nd_range=(0, 6),
        ni_range=(7, 13),
        na_range=(14, 20),
        criteria_points={"Critère 1": 5, "Critère 2": 5, "Critère 3": 10}
    )
    
    return AssessmentOutput(
        input=input_data,
        grid=grid,
        situation=situation,
        rubric=rubric
    )


class TestCriticAgent:
    """Test suite for CriticAgent."""
    
    def test_init(self):
        """Test CriticAgent initialization."""
        agent = CriticAgent(api_key="test_key", model="test_model")
        assert agent.api_key == "test_key"
        assert agent.model == "test_model"
        assert agent.api_url == "https://api.deepseek.com/v1/chat/completions"
    
    def test_build_validation_prompt(self):
        """Test validation prompt building."""
        agent = CriticAgent(api_key="test_key")
        assessment = create_sample_assessment()
        
        prompt = agent._build_validation_prompt(assessment)
        
        # Check that prompt contains key elements
        assert "validateur de qualité pédagogique" in prompt
        assert "Alignement" in prompt
        assert "Observabilité" in prompt
        assert "Cohérence" in prompt
        assert "is_valid" in prompt
        assert "alignment_score" in prompt
        assert "observability_issues" in prompt
        assert "coherence_issues" in prompt
        assert "feedback" in prompt
    
    @patch('src.critic.requests.post')
    def test_validate_assessment_success(self, mock_post):
        """Test successful validation."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": """{
                        "is_valid": true,
                        "alignment_score": "good",
                        "observability_issues": [],
                        "coherence_issues": [],
                        "feedback": "L'évaluation est de bonne qualité."
                    }"""
                }
            }]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        agent = CriticAgent(api_key="test_key")
        assessment = create_sample_assessment()
        
        result = agent.validate_assessment(assessment)
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert result.alignment_score == "good"
        assert len(result.observability_issues) == 0
        assert len(result.coherence_issues) == 0
        assert result.feedback == "L'évaluation est de bonne qualité."
    
    @patch('src.critic.requests.post')
    def test_validate_assessment_failure(self, mock_post):
        """Test validation with issues identified."""
        # Mock API response with validation failure
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": """{
                        "is_valid": false,
                        "alignment_score": "poor",
                        "observability_issues": ["Critère 1 n'est pas observable"],
                        "coherence_issues": ["La tâche est trop complexe pour le niveau"],
                        "feedback": "Plusieurs problèmes identifiés nécessitant une révision."
                    }"""
                }
            }]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        agent = CriticAgent(api_key="test_key")
        assessment = create_sample_assessment()
        
        result = agent.validate_assessment(assessment)
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is False
        assert result.alignment_score == "poor"
        assert len(result.observability_issues) == 1
        assert len(result.coherence_issues) == 1
        assert "problèmes identifiés" in result.feedback
    
    @patch('src.critic.requests.post')
    def test_validate_assessment_with_markdown_json(self, mock_post):
        """Test parsing JSON wrapped in markdown code blocks."""
        # Mock API response with markdown-wrapped JSON
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": """```json
                    {
                        "is_valid": true,
                        "alignment_score": "acceptable",
                        "observability_issues": [],
                        "coherence_issues": [],
                        "feedback": "Acceptable quality."
                    }
                    ```"""
                }
            }]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        agent = CriticAgent(api_key="test_key")
        assessment = create_sample_assessment()
        
        result = agent.validate_assessment(assessment)
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert result.alignment_score == "acceptable"
    
    @patch('src.critic.requests.post')
    def test_validate_assessment_api_failure_returns_not_completed(self, mock_post):
        """Test that API failures return a 'not completed' validation result."""
        # Mock API failure
        mock_post.side_effect = Exception("API connection failed")
        
        agent = CriticAgent(api_key="test_key")
        assessment = create_sample_assessment()
        
        result = agent.validate_assessment(assessment)
        
        # Should return a ValidationResult indicating validation couldn't be completed
        assert isinstance(result, ValidationResult)
        assert result.is_valid is False
        assert "could not be completed" in result.feedback
        assert "API error" in result.feedback

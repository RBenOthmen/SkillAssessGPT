"""
Tests for the GeneratorAgent class.
"""

import pytest
import json
from unittest.mock import Mock, patch
from src.generator import GeneratorAgent
from src.models import CompetencyInput, AssessmentOutput


class TestGeneratorAgent:
    """Test suite for GeneratorAgent."""
    
    def test_init(self):
        """Test generator initialization."""
        agent = GeneratorAgent(api_key="test_key", model="test_model")
        assert agent.api_key == "test_key"
        assert agent.model == "test_model"
        assert agent.max_retries == 3
    
    def test_build_prompt_basic(self):
        """Test prompt building with basic input."""
        agent = GeneratorAgent(api_key="test_key")
        input_data = CompetencyInput(
            competency="Développer une application web",
            niveau="Licence 2",
            parcours="Informatique",
            specialite="Développement Web",
            duree="2 heures"
        )
        
        prompt = agent._build_prompt(input_data)
        
        # Verify key elements are in the prompt
        assert "Développer une application web" in prompt
        assert "Licence 2" in prompt
        assert "Informatique" in prompt
        assert "Développement Web" in prompt
        assert "2 heures" in prompt
        assert "nd_criteria" in prompt
        assert "ni_criteria" in prompt
        assert "na_criteria" in prompt
    
    def test_build_prompt_with_element(self):
        """Test prompt building with optional element field."""
        agent = GeneratorAgent(api_key="test_key")
        input_data = CompetencyInput(
            competency="Développer une application web",
            element="Créer une interface utilisateur",
            niveau="Licence 2",
            parcours="Informatique",
            specialite="Développement Web",
            duree="2 heures"
        )
        
        prompt = agent._build_prompt(input_data)
        assert "Créer une interface utilisateur" in prompt
    
    @patch('src.generator.requests.post')
    def test_call_api_success(self, mock_post):
        """Test successful API call."""
        agent = GeneratorAgent(api_key="test_key")
        
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "test response"}}]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = agent._call_api("test prompt")
        
        assert result == {"choices": [{"message": {"content": "test response"}}]}
        mock_post.assert_called_once()
    
    @patch('src.generator.requests.post')
    def test_call_api_failure(self, mock_post):
        """Test API call failure."""
        agent = GeneratorAgent(api_key="test_key")
        
        # Mock failed response
        mock_post.side_effect = Exception("Connection error")
        
        with pytest.raises(Exception) as exc_info:
            agent._call_api("test prompt")
        
        assert "API request failed" in str(exc_info.value)
    
    def test_parse_response_valid(self):
        """Test parsing a valid API response."""
        agent = GeneratorAgent(api_key="test_key")
        input_data = CompetencyInput(
            competency="Test competency",
            niveau="Licence 2",
            parcours="Informatique",
            specialite="Dev",
            duree="2h"
        )
        
        api_response = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "grid": {
                            "nd_criteria": [
                                {"description": "ND1", "indicators": ["i1"], "points": 2},
                                {"description": "ND2", "indicators": ["i2"], "points": 2},
                                {"description": "ND3", "indicators": ["i3"], "points": 2}
                            ],
                            "ni_criteria": [
                                {"description": "NI1", "indicators": ["i1"], "points": 3},
                                {"description": "NI2", "indicators": ["i2"], "points": 3},
                                {"description": "NI3", "indicators": ["i3"], "points": 3}
                            ],
                            "na_criteria": [
                                {"description": "NA1", "indicators": ["i1"], "points": 5},
                                {"description": "NA2", "indicators": ["i2"], "points": 5},
                                {"description": "NA3", "indicators": ["i3"], "points": 5}
                            ]
                        },
                        "situation": {
                            "context": "Test context",
                            "task": "Test task",
                            "instructions": "Test instructions",
                            "duration": "2h"
                        },
                        "rubric": {
                            "total_points": 20,
                            "nd_range": [0, 6],
                            "ni_range": [7, 13],
                            "na_range": [14, 20],
                            "criteria_points": {"ND1": 2, "NI1": 3}
                        }
                    })
                }
            }]
        }
        
        result = agent._parse_response(api_response, input_data)
        
        assert isinstance(result, AssessmentOutput)
        assert len(result.grid.nd_criteria) == 3
        assert len(result.grid.ni_criteria) == 3
        assert len(result.grid.na_criteria) == 3
        assert result.situation.instructions == "Test instructions"
        assert result.rubric.total_points == 20
    
    def test_parse_response_with_markdown_wrapper(self):
        """Test parsing response wrapped in markdown code blocks."""
        agent = GeneratorAgent(api_key="test_key")
        input_data = CompetencyInput(
            competency="Test",
            niveau="L2",
            parcours="Info",
            specialite="Dev",
            duree="2h"
        )
        
        json_content = {
            "grid": {
                "nd_criteria": [
                    {"description": "ND1", "indicators": ["i1"], "points": 2},
                    {"description": "ND2", "indicators": ["i2"], "points": 2},
                    {"description": "ND3", "indicators": ["i3"], "points": 2}
                ],
                "ni_criteria": [
                    {"description": "NI1", "indicators": ["i1"], "points": 3},
                    {"description": "NI2", "indicators": ["i2"], "points": 3},
                    {"description": "NI3", "indicators": ["i3"], "points": 3}
                ],
                "na_criteria": [
                    {"description": "NA1", "indicators": ["i1"], "points": 5},
                    {"description": "NA2", "indicators": ["i2"], "points": 5},
                    {"description": "NA3", "indicators": ["i3"], "points": 5}
                ]
            },
            "situation": {
                "context": "ctx",
                "task": "tsk",
                "instructions": "inst",
                "duration": "2h"
            },
            "rubric": {
                "total_points": 20,
                "nd_range": [0, 6],
                "ni_range": [7, 13],
                "na_range": [14, 20],
                "criteria_points": {"ND1": 2}
            }
        }
        
        api_response = {
            "choices": [{
                "message": {
                    "content": f"```json\n{json.dumps(json_content)}\n```"
                }
            }]
        }
        
        result = agent._parse_response(api_response, input_data)
        assert isinstance(result, AssessmentOutput)
    
    def test_parse_response_missing_grid(self):
        """Test parsing response with missing grid."""
        agent = GeneratorAgent(api_key="test_key")
        input_data = CompetencyInput(
            competency="Test",
            niveau="L2",
            parcours="Info",
            specialite="Dev",
            duree="2h"
        )
        
        api_response = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "situation": {},
                        "rubric": {}
                    })
                }
            }]
        }
        
        with pytest.raises(Exception) as exc_info:
            agent._parse_response(api_response, input_data)
        
        assert "Missing 'grid'" in str(exc_info.value)
    
    @patch('src.generator.GeneratorAgent._call_api')
    @patch('src.generator.time.sleep')
    def test_generate_assessment_with_retry(self, mock_sleep, mock_call_api):
        """Test generate_assessment with retry logic."""
        agent = GeneratorAgent(api_key="test_key")
        input_data = CompetencyInput(
            competency="Test",
            niveau="L2",
            parcours="Info",
            specialite="Dev",
            duree="2h"
        )
        
        # First call fails, second succeeds
        valid_response = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "grid": {
                            "nd_criteria": [
                                {"description": "ND1", "indicators": ["i1"], "points": 2},
                                {"description": "ND2", "indicators": ["i2"], "points": 2},
                                {"description": "ND3", "indicators": ["i3"], "points": 2}
                            ],
                            "ni_criteria": [
                                {"description": "NI1", "indicators": ["i1"], "points": 3},
                                {"description": "NI2", "indicators": ["i2"], "points": 3},
                                {"description": "NI3", "indicators": ["i3"], "points": 3}
                            ],
                            "na_criteria": [
                                {"description": "NA1", "indicators": ["i1"], "points": 5},
                                {"description": "NA2", "indicators": ["i2"], "points": 5},
                                {"description": "NA3", "indicators": ["i3"], "points": 5}
                            ]
                        },
                        "situation": {
                            "context": "ctx",
                            "task": "tsk",
                            "instructions": "inst",
                            "duration": "2h"
                        },
                        "rubric": {
                            "total_points": 20,
                            "nd_range": [0, 6],
                            "ni_range": [7, 13],
                            "na_range": [14, 20],
                            "criteria_points": {"ND1": 2}
                        }
                    })
                }
            }]
        }
        
        mock_call_api.side_effect = [Exception("First failure"), valid_response]
        
        result = agent.generate_assessment(input_data)
        
        assert isinstance(result, AssessmentOutput)
        assert mock_call_api.call_count == 2
        assert mock_sleep.call_count == 1

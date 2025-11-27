"""
Tests for the input collector module.
"""

import pytest
from src.input_collector import InputCollector
from src.models import CompetencyInput


class TestInputCollector:
    """Test suite for InputCollector class."""
    
    def test_validate_inputs_with_all_required_fields(self):
        """Test that validation passes when all required fields are provided."""
        collector = InputCollector()
        
        input_data = {
            'competency': 'Développer une application web',
            'element': '',
            'niveau': 'Licence 2',
            'parcours': 'Informatique',
            'specialite': 'Développement Web',
            'duree': '2 heures'
        }
        
        assert collector.validate_inputs(input_data) is True
    
    def test_validate_inputs_with_missing_competency(self):
        """Test that validation fails when competency is missing."""
        collector = InputCollector()
        
        input_data = {
            'competency': '',
            'niveau': 'Licence 2',
            'parcours': 'Informatique',
            'specialite': 'Développement Web',
            'duree': '2 heures'
        }
        
        assert collector.validate_inputs(input_data) is False
    
    def test_validate_inputs_with_missing_niveau(self):
        """Test that validation fails when niveau is missing."""
        collector = InputCollector()
        
        input_data = {
            'competency': 'Développer une application web',
            'niveau': '',
            'parcours': 'Informatique',
            'specialite': 'Développement Web',
            'duree': '2 heures'
        }
        
        assert collector.validate_inputs(input_data) is False
    
    def test_validate_inputs_with_whitespace_only(self):
        """Test that validation fails when fields contain only whitespace."""
        collector = InputCollector()
        
        input_data = {
            'competency': '   ',
            'niveau': 'Licence 2',
            'parcours': 'Informatique',
            'specialite': 'Développement Web',
            'duree': '2 heures'
        }
        
        assert collector.validate_inputs(input_data) is False
    
    def test_validate_inputs_with_french_characters(self):
        """Test that validation works with French characters (accents, etc.)."""
        collector = InputCollector()
        
        input_data = {
            'competency': 'Développer une application sécurisée',
            'niveau': 'Licence 2',
            'parcours': 'Informatique',
            'specialite': 'Sécurité et Réseaux',
            'duree': '2 heures'
        }
        
        assert collector.validate_inputs(input_data) is True
    
    def test_validate_inputs_with_multiple_missing_fields(self):
        """Test that validation fails when multiple fields are missing."""
        collector = InputCollector()
        
        input_data = {
            'competency': 'Développer une application web',
            'niveau': '',
            'parcours': '',
            'specialite': 'Développement Web',
            'duree': ''
        }
        
        assert collector.validate_inputs(input_data) is False

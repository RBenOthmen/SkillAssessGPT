"""
Tests for the ExportModule class.
"""

import pytest
import json
import os
from pathlib import Path
from src.exporter import ExportModule
from src.models import (
    CompetencyInput,
    AssessmentOutput,
    APCGrid,
    Criterion,
    EvaluationSituation,
    ScoringRubric,
    ValidationResult
)


class TestExportModule:
    """Test suite for ExportModule."""
    
    @pytest.fixture
    def sample_assessment(self):
        """Create a sample assessment for testing."""
        input_data = CompetencyInput(
            competency="Développer une application web",
            element="Créer une interface utilisateur",
            niveau="Licence 2",
            parcours="Informatique",
            specialite="Développement Web",
            duree="2 heures"
        )
        
        grid = APCGrid(
            nd_criteria=[
                Criterion("Critère ND1", ["Indicateur 1", "Indicateur 2"], 2),
                Criterion("Critère ND2", ["Indicateur 3"], 2),
                Criterion("Critère ND3", ["Indicateur 4"], 2)
            ],
            ni_criteria=[
                Criterion("Critère NI1", ["Indicateur 5"], 3),
                Criterion("Critère NI2", ["Indicateur 6"], 3),
                Criterion("Critère NI3", ["Indicateur 7"], 3)
            ],
            na_criteria=[
                Criterion("Critère NA1", ["Indicateur 8"], 5),
                Criterion("Critère NA2", ["Indicateur 9"], 5),
                Criterion("Critère NA3", ["Indicateur 10"], 5)
            ]
        )
        
        situation = EvaluationSituation(
            context="Contexte authentique de test",
            task="Tâche complexe à réaliser",
            instructions="Instructions claires pour les étudiants",
            duration="2 heures"
        )
        
        rubric = ScoringRubric(
            total_points=20,
            nd_range=(0, 6),
            ni_range=(7, 13),
            na_range=(14, 20),
            criteria_points={"Critère ND1": 2, "Critère NI1": 3, "Critère NA1": 5}
        )
        
        return AssessmentOutput(
            input=input_data,
            grid=grid,
            situation=situation,
            rubric=rubric
        )
    
    @pytest.fixture
    def sample_validation(self):
        """Create a sample validation result for testing."""
        return ValidationResult(
            is_valid=True,
            alignment_score="good",
            observability_issues=[],
            coherence_issues=[],
            feedback="L'évaluation est de bonne qualité."
        )
    
    @pytest.fixture
    def sample_validation_failed(self):
        """Create a sample failed validation result for testing."""
        return ValidationResult(
            is_valid=False,
            alignment_score="poor",
            observability_issues=["Critère 1 n'est pas observable"],
            coherence_issues=["Tâche trop complexe pour le niveau"],
            feedback="Des améliorations sont nécessaires."
        )
    
    def test_init(self, tmp_path):
        """Test export module initialization."""
        output_dir = str(tmp_path / "test_outputs")
        exporter = ExportModule(output_dir=output_dir)
        
        assert exporter.output_dir == output_dir
        assert Path(output_dir).exists()
    
    def test_export_json_success(self, tmp_path, sample_assessment, sample_validation):
        """Test successful JSON export."""
        output_dir = str(tmp_path / "test_outputs")
        exporter = ExportModule(output_dir=output_dir)
        
        filepath = exporter.export_json(
            sample_assessment,
            sample_validation,
            "test_assessment.json"
        )
        
        # Verify file was created
        assert os.path.exists(filepath)
        assert filepath.endswith('.json')
        
        # Verify JSON content
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert "assessment" in data
        assert "validation" in data
        assert data["assessment"]["input"]["competency"] == "Développer une application web"
        assert data["validation"]["is_valid"] is True
    
    def test_export_markdown_success(self, tmp_path, sample_assessment, sample_validation):
        """Test successful Markdown export."""
        output_dir = str(tmp_path / "test_outputs")
        exporter = ExportModule(output_dir=output_dir)
        
        filepath = exporter.export_markdown(
            sample_assessment,
            sample_validation,
            "test_assessment.md"
        )
        
        # Verify file was created
        assert os.path.exists(filepath)
        assert filepath.endswith('.md')
        
        # Verify Markdown content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "# Grille d'Évaluation APC" in content
        assert "Développer une application web" in content
        assert "Niveau ND (Non Développé)" in content
        assert "Niveau NI (Niveau Intermédiaire)" in content
        assert "Niveau NA (Niveau Attendu)" in content
        assert "Barème de Notation" in content
        assert "✅ Validé" in content
    
    def test_export_markdown_with_failed_validation(self, tmp_path, sample_assessment, sample_validation_failed):
        """Test Markdown export with failed validation."""
        output_dir = str(tmp_path / "test_outputs")
        exporter = ExportModule(output_dir=output_dir)
        
        filepath = exporter.export_markdown(
            sample_assessment,
            sample_validation_failed,
            "test_failed.md"
        )
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "❌ Non validé" in content
        assert "Problèmes d'observabilité" in content
        assert "Problèmes de cohérence" in content
        assert "Des améliorations sont nécessaires" in content
    
    def test_json_export_adds_extension(self, tmp_path, sample_assessment, sample_validation):
        """Test that JSON export adds .json extension if missing."""
        output_dir = str(tmp_path / "test_outputs")
        exporter = ExportModule(output_dir=output_dir)
        
        filepath = exporter.export_json(
            sample_assessment,
            sample_validation,
            "test_no_extension"
        )
        
        assert filepath.endswith('.json')
        assert os.path.exists(filepath)
    
    def test_markdown_export_adds_extension(self, tmp_path, sample_assessment, sample_validation):
        """Test that Markdown export adds .md extension if missing."""
        output_dir = str(tmp_path / "test_outputs")
        exporter = ExportModule(output_dir=output_dir)
        
        filepath = exporter.export_markdown(
            sample_assessment,
            sample_validation,
            "test_no_extension"
        )
        
        assert filepath.endswith('.md')
        assert os.path.exists(filepath)
    
    def test_export_handles_french_characters(self, tmp_path, sample_assessment, sample_validation):
        """Test that exports handle French characters correctly."""
        output_dir = str(tmp_path / "test_outputs")
        exporter = ExportModule(output_dir=output_dir)
        
        # Export JSON
        json_path = exporter.export_json(sample_assessment, sample_validation, "test_french.json")
        with open(json_path, 'r', encoding='utf-8') as f:
            json_content = f.read()
        
        assert "Développer" in json_content
        assert "Créer" in json_content
        
        # Export Markdown
        md_path = exporter.export_markdown(sample_assessment, sample_validation, "test_french.md")
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        assert "Développer" in md_content
        assert "Évaluation" in md_content

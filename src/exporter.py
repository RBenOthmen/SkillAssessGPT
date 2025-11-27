"""
Export Module for SkillAssessGPT.

This module contains the ExportModule class that exports assessment outputs
and validation results to JSON and Markdown formats.
"""

import json
import os
from typing import Optional
from pathlib import Path

from src.models import AssessmentOutput, ValidationResult


class ExportModule:
    """
    Export module that formats and saves assessment outputs.
    
    This module handles exporting assessment grids, evaluation situations,
    scoring rubrics, and validation results to both JSON and Markdown formats.
    """
    
    def __init__(self, output_dir: str = "outputs"):
        """
        Initialize the export module.
        
        Args:
            output_dir: Directory where output files will be saved (default: "outputs")
        """
        self.output_dir = output_dir
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """Create output directory if it doesn't exist."""
        try:
            Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise Exception(f"Failed to create output directory '{self.output_dir}': {str(e)}")
    
    def export_json(
        self,
        assessment: AssessmentOutput,
        validation: ValidationResult,
        filepath: str
    ) -> str:
        """
        Export assessment and validation to JSON format.
        
        Args:
            assessment: The assessment output to export
            validation: The validation result to export
            filepath: Path where the JSON file will be saved
            
        Returns:
            Full path to the created JSON file
            
        Raises:
            Exception: If file writing fails
        """
        try:
            # Combine assessment and validation data
            export_data = {
                "assessment": assessment.to_dict(),
                "validation": validation.to_dict()
            }
            
            # Ensure filepath is in output directory
            if not filepath.startswith(self.output_dir):
                filepath = os.path.join(self.output_dir, filepath)
            
            # Ensure .json extension
            if not filepath.endswith('.json'):
                filepath += '.json'
            
            # Write JSON file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            return filepath
            
        except Exception as e:
            raise Exception(f"Failed to export JSON to '{filepath}': {str(e)}")

    def export_markdown(
        self,
        assessment: AssessmentOutput,
        validation: ValidationResult,
        filepath: str
    ) -> str:
        """
        Export assessment and validation to Markdown format.
        
        Creates a readable Markdown document with formatted tables for the
        APC grid and clear sections for all assessment components.
        
        Args:
            assessment: The assessment output to export
            validation: The validation result to export
            filepath: Path where the Markdown file will be saved
            
        Returns:
            Full path to the created Markdown file
            
        Raises:
            Exception: If file writing fails
        """
        try:
            # Build Markdown content
            md_content = self._build_markdown_content(assessment, validation)
            
            # Ensure filepath is in output directory
            if not filepath.startswith(self.output_dir):
                filepath = os.path.join(self.output_dir, filepath)
            
            # Ensure .md extension
            if not filepath.endswith('.md'):
                filepath += '.md'
            
            # Write Markdown file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            return filepath
            
        except Exception as e:
            raise Exception(f"Failed to export Markdown to '{filepath}': {str(e)}")
    
    def _build_markdown_content(
        self,
        assessment: AssessmentOutput,
        validation: ValidationResult
    ) -> str:
        """
        Build the Markdown content from assessment and validation data.
        
        Args:
            assessment: The assessment output
            validation: The validation result
            
        Returns:
            Formatted Markdown string
        """
        lines = []
        
        # Title and metadata
        lines.append("# Grille d'Évaluation APC")
        lines.append("")
        lines.append(f"**Généré le** : {assessment.generated_at}")
        lines.append(f"**Validé le** : {validation.validated_at}")
        lines.append("")
        
        # Validation status
        status_emoji = "✅" if validation.is_valid else "❌"
        status_text = "Validé" if validation.is_valid else "Non validé"
        lines.append(f"**Statut de validation** : {status_emoji} {status_text}")
        
        if validation.alignment_score:
            lines.append(f"**Score d'alignement** : {validation.alignment_score}")
        
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Competency information
        lines.append("## Compétence")
        lines.append("")
        lines.append(f"**Compétence** : {assessment.input.competency}")
        
        if assessment.input.element:
            lines.append(f"**Élément** : {assessment.input.element}")
        
        lines.append(f"**Niveau** : {assessment.input.niveau}")
        lines.append(f"**Parcours** : {assessment.input.parcours}")
        lines.append(f"**Spécialité** : {assessment.input.specialite}")
        lines.append(f"**Durée** : {assessment.input.duree}")
        lines.append("")
        
        # APC Grid
        lines.append("## Grille APC")
        lines.append("")
        
        # ND Level
        lines.append("### Niveau ND (Non Développé)")
        lines.append("")
        lines.append(self._format_criteria_table(assessment.grid.nd_criteria))
        lines.append("")
        
        # NI Level
        lines.append("### Niveau NI (Niveau Intermédiaire)")
        lines.append("")
        lines.append(self._format_criteria_table(assessment.grid.ni_criteria))
        lines.append("")
        
        # NA Level
        lines.append("### Niveau NA (Niveau Attendu)")
        lines.append("")
        lines.append(self._format_criteria_table(assessment.grid.na_criteria))
        lines.append("")
        
        # Evaluation Situation
        lines.append("## Situation d'Évaluation")
        lines.append("")
        
        if assessment.situation.context:
            lines.append("### Contexte")
            lines.append("")
            lines.append(assessment.situation.context)
            lines.append("")
        
        if assessment.situation.task:
            lines.append("### Tâche")
            lines.append("")
            lines.append(assessment.situation.task)
            lines.append("")
        
        lines.append("### Instructions")
        lines.append("")
        lines.append(assessment.situation.instructions)
        lines.append("")
        
        lines.append(f"**Durée** : {assessment.situation.duration}")
        lines.append("")
        
        # Scoring Rubric
        lines.append("## Barème de Notation")
        lines.append("")
        lines.append(f"**Total de points** : {assessment.rubric.total_points}")
        lines.append("")
        
        lines.append("### Répartition par niveau")
        lines.append("")
        lines.append("| Niveau | Plage de points |")
        lines.append("|--------|----------------|")
        lines.append(f"| ND (Non Développé) | {assessment.rubric.nd_range[0]} - {assessment.rubric.nd_range[1]} |")
        lines.append(f"| NI (Niveau Intermédiaire) | {assessment.rubric.ni_range[0]} - {assessment.rubric.ni_range[1]} |")
        lines.append(f"| NA (Niveau Attendu) | {assessment.rubric.na_range[0]} - {assessment.rubric.na_range[1]} |")
        lines.append("")
        
        if assessment.rubric.criteria_points:
            lines.append("### Points par critère")
            lines.append("")
            lines.append("| Critère | Points |")
            lines.append("|---------|--------|")
            for criterion, points in assessment.rubric.criteria_points.items():
                lines.append(f"| {criterion} | {points} |")
            lines.append("")
        
        # Validation feedback
        lines.append("## Validation")
        lines.append("")
        
        if validation.observability_issues:
            lines.append("### Problèmes d'observabilité")
            lines.append("")
            for issue in validation.observability_issues:
                lines.append(f"- {issue}")
            lines.append("")
        
        if validation.coherence_issues:
            lines.append("### Problèmes de cohérence")
            lines.append("")
            for issue in validation.coherence_issues:
                lines.append(f"- {issue}")
            lines.append("")
        
        if validation.feedback:
            lines.append("### Feedback")
            lines.append("")
            lines.append(validation.feedback)
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_criteria_table(self, criteria: list) -> str:
        """
        Format a list of criteria as a Markdown table.
        
        Args:
            criteria: List of Criterion objects
            
        Returns:
            Formatted Markdown table string
        """
        lines = []
        lines.append("| Critère | Indicateurs | Points |")
        lines.append("|---------|-------------|--------|")
        
        for criterion in criteria:
            # Format indicators as a bulleted list
            indicators_text = "<br>".join([f"• {ind}" for ind in criterion.indicators])
            lines.append(f"| {criterion.description} | {indicators_text} | {criterion.points} |")
        
        return "\n".join(lines)

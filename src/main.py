"""
Main Pipeline for SkillAssessGPT.

This module contains the SkillAssessGPT class that orchestrates the complete
assessment generation pipeline: input collection, generation, validation, and export.
"""

import os
import sys
from typing import Tuple, Optional
from dotenv import load_dotenv

from src.models import AssessmentOutput, ValidationResult
from src.input_collector import InputCollector
from src.generator import GeneratorAgent
from src.critic import CriticAgent
from src.exporter import ExportModule


class SkillAssessGPT:
    """
    Main pipeline orchestrator for SkillAssessGPT.
    
    This class coordinates the entire workflow from input collection through
    generation, validation, and export of APC assessment materials.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the SkillAssessGPT pipeline.
        
        Args:
            api_key: DeepSeek API key (if None, loads from environment)
            
        Raises:
            ValueError: If API key is not provided and not found in environment
        """
        # Load environment variables
        load_dotenv()
        
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "Google API key not found. "
                "Please set GOOGLE_API_KEY environment variable or pass api_key parameter."
            )
        
        # Initialize components
        self.input_collector = InputCollector()
        self.generator = GeneratorAgent(self.api_key)
        self.critic = CriticAgent(self.api_key)
        self.exporter = ExportModule()
    
    def run(self) -> Tuple[AssessmentOutput, ValidationResult]:
        """
        Run the complete assessment generation pipeline.
        
        This method orchestrates all stages:
        1. Collect user inputs
        2. Generate assessment with LLM
        3. Validate assessment quality
        4. Export results to JSON and Markdown
        
        Returns:
            Tuple of (AssessmentOutput, ValidationResult)
            
        Raises:
            Exception: If any stage fails critically
        """
        print("=" * 60)
        print("SkillAssessGPT - Générateur d'Évaluations APC")
        print("=" * 60)
        print()
        
        # Stage 1: Input Collection
        print("📝 Étape 1/4 : Collecte des informations")
        print("-" * 60)
        try:
            input_data = self.input_collector.collect_inputs()
        except Exception as e:
            print(f"\n❌ Erreur lors de la collecte des informations : {str(e)}")
            raise
        
        # Stage 2: Generation
        print("\n🤖 Étape 2/4 : Génération de la grille d'évaluation")
        print("-" * 60)
        print("Appel de l'agent générateur (Google Gemini)...")
        print("Cela peut prendre 10-20 secondes...")
        
        try:
            assessment = self.generator.generate_assessment(input_data)
            print("✅ Grille d'évaluation générée avec succès!")
            print(f"   - {len(assessment.grid.nd_criteria)} critères ND")
            print(f"   - {len(assessment.grid.ni_criteria)} critères NI")
            print(f"   - {len(assessment.grid.na_criteria)} critères NA")
            print(f"   - Barème total : {assessment.rubric.total_points} points")
        except Exception as e:
            print(f"\n❌ Erreur lors de la génération : {str(e)}")
            raise
        
        # Stage 3: Validation
        print("\n🔍 Étape 3/4 : Validation de la qualité pédagogique")
        print("-" * 60)
        print("Appel de l'agent critique (Google Gemini)...")
        print("Cela peut prendre 5-10 secondes...")
        
        try:
            validation = self.critic.validate_assessment(assessment)
            
            if validation.is_valid:
                print("✅ Validation réussie!")
                if validation.alignment_score:
                    print(f"   - Score d'alignement : {validation.alignment_score}")
            else:
                print("⚠️  Validation avec remarques")
                if validation.observability_issues:
                    print(f"   - {len(validation.observability_issues)} problème(s) d'observabilité")
                if validation.coherence_issues:
                    print(f"   - {len(validation.coherence_issues)} problème(s) de cohérence")
        except Exception as e:
            print(f"\n⚠️  Avertissement : Validation incomplète : {str(e)}")
            # Create a fallback validation result
            validation = ValidationResult(
                is_valid=False,
                feedback=f"Validation non complétée : {str(e)}"
            )
        
        # Stage 4: Export
        print("\n💾 Étape 4/4 : Export des résultats")
        print("-" * 60)
        
        try:
            # Generate base filename from competency
            base_filename = self._generate_filename(input_data.competency)
            
            # Export JSON
            json_path = self.exporter.export_json(
                assessment,
                validation,
                f"{base_filename}.json"
            )
            print(f"✅ Export JSON : {json_path}")
            
            # Export Markdown
            md_path = self.exporter.export_markdown(
                assessment,
                validation,
                f"{base_filename}.md"
            )
            print(f"✅ Export Markdown : {md_path}")
            
        except Exception as e:
            print(f"\n❌ Erreur lors de l'export : {str(e)}")
            raise
        
        # Display completion summary
        self._display_summary(assessment, validation, json_path, md_path)
        
        return assessment, validation
    
    def _generate_filename(self, competency: str) -> str:
        """
        Generate a safe filename from the competency description.
        
        Args:
            competency: Competency description text
            
        Returns:
            Safe filename string
        """
        # Take first 50 characters and clean up
        filename = competency[:50].strip()
        
        # Replace spaces and special characters
        filename = filename.replace(" ", "_")
        filename = "".join(c for c in filename if c.isalnum() or c in ("_", "-"))
        
        # Ensure it's not empty
        if not filename:
            filename = "assessment"
        
        return filename.lower()
    
    def _display_summary(
        self,
        assessment: AssessmentOutput,
        validation: ValidationResult,
        json_path: str,
        md_path: str
    ):
        """
        Display completion summary with file paths and key information.
        
        Args:
            assessment: Generated assessment output
            validation: Validation result
            json_path: Path to JSON export file
            md_path: Path to Markdown export file
        """
        print("\n" + "=" * 60)
        print("✨ Génération terminée avec succès!")
        print("=" * 60)
        print()
        print("📊 Résumé :")
        print(f"   Compétence : {assessment.input.competency[:60]}...")
        print(f"   Niveau : {assessment.input.niveau}")
        print(f"   Parcours : {assessment.input.parcours}")
        print(f"   Spécialité : {assessment.input.specialite}")
        print()
        print("📁 Fichiers générés :")
        print(f"   JSON     : {json_path}")
        print(f"   Markdown : {md_path}")
        print()
        
        # Validation status
        if validation.is_valid:
            print("✅ Statut : Validé")
        else:
            print("⚠️  Statut : Validation avec remarques")
            if validation.feedback:
                print(f"\n💬 Feedback : {validation.feedback[:200]}...")
        
        print()
        print("=" * 60)


def main():
    """
    Entry point for command-line execution.
    """
    try:
        pipeline = SkillAssessGPT()
        pipeline.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Opération annulée par l'utilisateur.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erreur fatale : {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

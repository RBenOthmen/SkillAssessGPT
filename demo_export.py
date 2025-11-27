"""
Demo script to showcase the export module functionality.
"""

from src.models import (
    CompetencyInput,
    AssessmentOutput,
    APCGrid,
    Criterion,
    EvaluationSituation,
    ScoringRubric,
    ValidationResult
)
from src.exporter import ExportModule


def main():
    """Demonstrate export functionality."""
    
    # Create sample assessment
    input_data = CompetencyInput(
        competency="Développer une application web responsive",
        element="Créer une interface utilisateur moderne",
        niveau="Licence 2",
        parcours="Informatique",
        specialite="Développement Web",
        duree="2 heures"
    )
    
    grid = APCGrid(
        nd_criteria=[
            Criterion("Utilise HTML de base", ["Balises structurelles présentes", "Syntaxe HTML valide"], 2),
            Criterion("Applique CSS simple", ["Styles de base appliqués", "Couleurs définies"], 2),
            Criterion("Structure de base", ["Page affichable", "Contenu visible"], 2)
        ],
        ni_criteria=[
            Criterion("Utilise HTML sémantique", ["Balises sémantiques appropriées", "Structure logique"], 3),
            Criterion("Applique CSS avancé", ["Flexbox ou Grid utilisé", "Responsive design partiel"], 3),
            Criterion("Interactivité de base", ["Événements JavaScript simples", "Validation de formulaire"], 3)
        ],
        na_criteria=[
            Criterion("Maîtrise HTML5", ["Toutes balises sémantiques", "Accessibilité respectée"], 5),
            Criterion("Maîtrise CSS3", ["Design responsive complet", "Animations fluides"], 5),
            Criterion("JavaScript avancé", ["Manipulation DOM complexe", "Gestion d'état"], 5)
        ]
    )
    
    situation = EvaluationSituation(
        context="Une startup locale souhaite créer un site vitrine pour présenter ses services.",
        task="Développer une page d'accueil responsive avec navigation, section héros, et formulaire de contact.",
        instructions="Créez une page HTML5 complète avec CSS3 et JavaScript. La page doit être responsive (mobile, tablette, desktop) et respecter les bonnes pratiques d'accessibilité.",
        duration="2 heures"
    )
    
    rubric = ScoringRubric(
        total_points=20,
        nd_range=(0, 6),
        ni_range=(7, 13),
        na_range=(14, 20),
        criteria_points={
            "Utilise HTML de base": 2,
            "Applique CSS simple": 2,
            "Structure de base": 2,
            "Utilise HTML sémantique": 3,
            "Applique CSS avancé": 3,
            "Interactivité de base": 3,
            "Maîtrise HTML5": 5
        }
    )
    
    assessment = AssessmentOutput(
        input=input_data,
        grid=grid,
        situation=situation,
        rubric=rubric
    )
    
    # Create validation result
    validation = ValidationResult(
        is_valid=True,
        alignment_score="good",
        observability_issues=[],
        coherence_issues=[],
        feedback="L'évaluation est bien structurée et alignée avec la compétence visée. Les critères sont observables et mesurables."
    )
    
    # Export to both formats
    exporter = ExportModule()
    
    json_path = exporter.export_json(assessment, validation, "demo_assessment")
    print(f"✅ JSON exported to: {json_path}")
    
    md_path = exporter.export_markdown(assessment, validation, "demo_assessment")
    print(f"✅ Markdown exported to: {md_path}")
    
    print("\n📁 Check the 'outputs' directory to see the generated files!")


if __name__ == "__main__":
    main()

import sys
from typing import Optional
from src.models import CompetencyInput


class InputCollector:

    def __init__(self):
        """Initialize the InputCollector."""
        # Ensure UTF-8 encoding for French character support
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8')
        if sys.stdin.encoding != 'utf-8':
            sys.stdin.reconfigure(encoding='utf-8')
    
    def collect_inputs(self) -> CompetencyInput:
        print("=== SkillAssessGPT - Collecte des informations ===\n")
        
        # Collect competency (required)
        competency = self._prompt_required(
            "Compétence à évaluer",
            "Décrivez la compétence principale à évaluer"
        )
        
        # Collect element (optional)
        element = self._prompt_optional(
            "Élément de compétence",
            "Précisez un élément spécifique de la compétence si nécessaire"
        )
        
        # Collect niveau (required)
        niveau = self._prompt_required(
            "Niveau d'études",
            "Ex: Licence 2, Master 1, etc."
        )
        
        # Collect parcours (required)
        parcours = self._prompt_required(
            "Parcours/Filière",
            "Ex: Informatique, Gestion, Sciences, etc."
        )
        
        # Collect specialite (required)
        specialite = self._prompt_required(
            "Spécialité",
            "Ex: Développement Web, Réseaux, Base de données, etc."
        )
        
        # Collect duree (required)
        duree = self._prompt_required(
            "Durée de l'évaluation",
            "Ex: 2 heures, 3h30, 1 heure 30 minutes, etc."
        )
        
        # Create and validate the input object
        try:
            input_data = CompetencyInput(
                competency=competency,
                element=element,
                niveau=niveau,
                parcours=parcours,
                specialite=specialite,
                duree=duree
            )
            
            print("\n✓ Toutes les informations ont été collectées avec succès!\n")
            return input_data
            
        except ValueError as e:
            # This should not happen if _prompt_required works correctly,
            # but we handle it just in case
            raise ValueError(f"Erreur de validation: {str(e)}")
    
    def validate_inputs(self, input_data: dict) -> bool:
        required_fields = {
            'competency': 'Compétence',
            'niveau': 'Niveau d\'études',
            'parcours': 'Parcours/Filière',
            'specialite': 'Spécialité',
            'duree': 'Durée'
        }
        
        missing_fields = []
        
        for field_key, field_name in required_fields.items():
            value = input_data.get(field_key, '')
            if not value or not str(value).strip():
                missing_fields.append(field_name)
        
        if missing_fields:
            print("❌ Erreur: Les champs suivants sont obligatoires et ne peuvent pas être vides:")
            for field in missing_fields:
                print(f"   - {field}")
            return False
        
        return True
    
    def _prompt_required(self, field_name: str, hint: str) -> str:
        while True:
            print(f"\n{field_name} (requis):")
            print(f"  {hint}")
            value = input("> ").strip()
            
            if value:
                return value
            else:
                print(f"❌ Le champ '{field_name}' ne peut pas être vide. Veuillez réessayer.")
    
    def _prompt_optional(self, field_name: str, hint: str) -> str:
        print(f"\n{field_name}:")
        print(f"  {hint}")
        value = input("> ").strip()
        return value

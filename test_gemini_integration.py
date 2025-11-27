"""
Quick test script to verify Google Gemini integration.
"""

import os
from dotenv import load_dotenv
from src.models import CompetencyInput
from src.generator import GeneratorAgent
from src.critic import CriticAgent

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ GOOGLE_API_KEY not found in environment variables")
    print("Please set it in your .env file")
    exit(1)

print("✅ API key loaded successfully")
print(f"   Key: {api_key[:8]}...{api_key[-4:]}")
print()

# Create test input
test_input = CompetencyInput(
    competency="Créer une page web simple avec HTML et CSS",
    element="Structurer le contenu avec HTML",
    niveau="Licence 1",
    parcours="Informatique",
    specialite="Développement Web",
    duree="1 heure"
)

print("📝 Test input created:")
print(f"   Competency: {test_input.competency}")
print()

# Test Generator Agent
print("🤖 Testing Generator Agent...")
try:
    generator = GeneratorAgent(api_key)
    print("✅ Generator Agent initialized successfully")
    
    print("   Generating assessment (this may take 10-20 seconds)...")
    assessment = generator.generate_assessment(test_input)
    
    print("✅ Assessment generated successfully!")
    print(f"   - ND criteria: {len(assessment.grid.nd_criteria)}")
    print(f"   - NI criteria: {len(assessment.grid.ni_criteria)}")
    print(f"   - NA criteria: {len(assessment.grid.na_criteria)}")
    print(f"   - Total points: {assessment.rubric.total_points}")
    print()
    
    # Test Critic Agent
    print("🔍 Testing Critic Agent...")
    critic = CriticAgent(api_key)
    print("✅ Critic Agent initialized successfully")
    
    print("   Validating assessment (this may take 5-10 seconds)...")
    validation = critic.validate_assessment(assessment)
    
    print("✅ Validation completed successfully!")
    print(f"   - Valid: {validation.is_valid}")
    print(f"   - Alignment score: {validation.alignment_score}")
    print()
    
    print("=" * 60)
    print("🎉 All tests passed! Google Gemini integration is working!")
    print("=" * 60)
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

#!/usr/bin/env python
"""
Test script to verify Gemini API integration
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_interview_screener.settings')

# Set the API key directly for testing
os.environ['GEMINI_API_KEY'] = 'AIzaSyDU2KI9vh66W6KVfnX0SHsRyGUEaemBUms'

try:
    django.setup()
    print("✓ Django setup successful")
except Exception as e:
    print(f"✗ Django setup failed: {e}")
    sys.exit(1)

# Test Gemini integration
try:
    from interviews.services import AIService
    print("✓ AIService import successful")
    
    # Test question generation
    ai_service = AIService()
    print("✓ AIService initialization successful")
    
    # Test with a simple job description
    test_jd = "We are looking for a Python Developer with Django experience to build web applications."
    
    print("🧪 Testing question generation...")
    questions = ai_service.generate_questions_from_jd(test_jd, num_questions=3)
    
    if questions and len(questions) > 0:
        print(f"✓ Generated {len(questions)} questions successfully!")
        for i, q in enumerate(questions, 1):
            print(f"  {i}. {q.get('question', 'N/A')}")
            print(f"     Difficulty: {q.get('difficulty', 'N/A')}")
            print(f"     Category: {q.get('category', 'N/A')}")
            print()
    else:
        print("✗ Question generation failed - no questions returned")
        
except Exception as e:
    print(f"✗ Gemini integration test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Test Complete ===")

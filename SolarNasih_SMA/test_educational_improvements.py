#!/usr/bin/env python3
"""
Test script for Educational Agent improvements
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.educational_agent import EducationalAgent

def test_parameter_extraction():
    """Test parameter extraction methods"""
    agent = EducationalAgent()
    
    test_cases = [
        {
            "input": "Crée un quiz de 5 questions sur l'énergie solaire niveau débutant",
            "expected_questions": 5,
            "expected_difficulty": "beginner"
        },
        {
            "input": "Je veux 10 questions difficiles sur l'installation",
            "expected_questions": 10,
            "expected_difficulty": "advanced"
        },
        {
            "input": "Quiz intermédiaire avec 15 questions sur l'économie",
            "expected_questions": 15,
            "expected_difficulty": "intermediate"
        },
        {
            "input": "Test sur les panneaux solaires niveau expert",
            "expected_questions": 10,  # default
            "expected_difficulty": "advanced"
        }
    ]
    
    print("Testing parameter extraction...")
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['input']}")
        
        # Test number extraction
        num_questions = agent._extract_num_questions(test_case['input'])
        print(f"  Extracted questions: {num_questions} (expected: {test_case['expected_questions']})")
        
        # Test difficulty extraction
        difficulty = agent._extract_difficulty(test_case['input'])
        print(f"  Extracted difficulty: {difficulty} (expected: {test_case['expected_difficulty']})")
        
        # Test topic extraction
        topic = agent._extract_topic(test_case['input'])
        print(f"  Extracted topic: {topic}")
        
        # Verify results
        questions_ok = num_questions == test_case['expected_questions']
        difficulty_ok = difficulty == test_case['expected_difficulty']
        
        if questions_ok and difficulty_ok:
            print("  ✅ PASS")
        else:
            print("  ❌ FAIL")

def test_quiz_generation():
    """Test quiz generation with different parameters"""
    agent = EducationalAgent()
    
    print("\nTesting quiz generation...")
    
    test_cases = [
        {"topic": "basics", "difficulty": "beginner", "num_questions": 3},
        {"topic": "installation", "difficulty": "intermediate", "num_questions": 5},
        {"topic": "economics", "difficulty": "advanced", "num_questions": 7},
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['topic']} - {test_case['difficulty']} - {test_case['num_questions']} questions")
        
        try:
            result = agent.create_quiz_tool(
                test_case['topic'], 
                test_case['difficulty'], 
                test_case['num_questions']
            )
            
            if 'error' in result:
                print(f"  ❌ Error: {result['error']}")
            else:
                questions = result.get('questions', [])
                print(f"  Generated {len(questions)} questions")
                print(f"  Topic: {result.get('topic')}")
                print(f"  Difficulty: {result.get('difficulty')}")
                
                if len(questions) == test_case['num_questions']:
                    print("  ✅ PASS - Correct number of questions")
                else:
                    print(f"  ❌ FAIL - Expected {test_case['num_questions']}, got {len(questions)}")
                    
        except Exception as e:
            print(f"  ❌ Exception: {e}")

if __name__ == "__main__":
    print("Educational Agent Improvement Tests")
    print("=" * 40)
    
    test_parameter_extraction()
    test_quiz_generation()
    
    print("\nTests completed!") 
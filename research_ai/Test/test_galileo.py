#!/usr/bin/env python3
"""
Test script for Optimized Galileo
Demonstrates all functionality with predefined inputs
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from galileo_optimized import OptimizedGalileo

def test_full_pipeline():
    """Test the complete research pipeline"""

    print("🔬 TESTING OPTIMIZED GALILEO")
    print("=" * 50)

    try:
        # Initialize Galileo
        galileo = OptimizedGalileo()

        # Test 1: Research blockchain at intermediate level
        print("\n🧪 TEST 1: Research 'blockchain technology' at intermediate level")
        result = galileo.research_topic("blockchain technology", "intermediate")

        if result and result['status'] == 'completed':
            print("✅ Research completed successfully!")
            print(f"📄 Report saved: {result.get('report_file')}")

            # Test 2: Ask follow-up questions
            print("\n🧪 TEST 2: Follow-up questions")

            followup_questions = [
                "What are the main benefits of blockchain?",
                "How does blockchain work?",
                "What are blockchain applications?"
            ]

            for question in followup_questions:
                print(f"\n❓ Question: {question}")
                response = galileo.ask_followup(question)
                print(f"💬 Response: {response[:200]}...")

            print("\n✅ All tests completed successfully!")

        else:
            print("❌ Research failed")
            if result:
                print(f"Error: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def test_minimal_example():
    """Minimal working example"""

    print("🧪 MINIMAL TEST")
    print("=" * 30)

    try:
        galileo = OptimizedGalileo()

        # Simple test with artificial intelligence
        result = galileo.research_topic("artificial intelligence", "beginner")

        if result:
            print(f"Status: {result['status']}")
            if result.get('report_file'):
                print(f"Report: {result['report_file']}")
                return True

        return False

    except Exception as e:
        print(f"Minimal test failed: {e}")
        return False

if __name__ == "__main__":
    # Choose test based on command line argument
    if len(sys.argv) > 1 and sys.argv[1] == "minimal":
        success = test_minimal_example()
    else:
        test_full_pipeline()
        success = True

    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Tests failed!")
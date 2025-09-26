#!/usr/bin/env python3
"""
Test script for enhanced context system (Phase 1)
Tests report-aware follow-up questions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from galileo_optimized import OptimizedGalileo

def test_enhanced_context():
    """Test the enhanced context system with report awareness"""

    print("🧪 TESTING ENHANCED CONTEXT SYSTEM (PHASE 1)")
    print("=" * 60)

    try:
        # Initialize Galileo
        galileo = OptimizedGalileo()

        # Check if we have an existing session with a report
        if galileo.research_context.get('sessions'):
            print("📚 Found existing research sessions:")
            for i, (key, data) in enumerate(galileo.research_context['sessions'].items(), 1):
                status = data.get('status', 'unknown')
                topic = data.get('topic', 'Unknown topic')
                report_file = data.get('report_file', 'No report')
                print(f"   {i}. {topic} ({status}) - {report_file}")

            # Use the first completed session for testing
            completed_sessions = {k: v for k, v in galileo.research_context['sessions'].items()
                                if v.get('status') == 'completed'}

            if completed_sessions:
                # Find session with report file
                session_key = None
                for key, data in completed_sessions.items():
                    if data.get('report_file') and os.path.exists(data.get('report_file')):
                        session_key = key
                        break

                if not session_key:
                    session_key = list(completed_sessions.keys())[0]
                session_data = completed_sessions[session_key]
                galileo.research_context['current_session'] = session_key

                print(f"\n🎯 Testing with session: {session_data['topic']}")
                print(f"📄 Report file: {session_data.get('report_file', 'None')}")

                # Test follow-up questions
                test_questions = [
                    "What are the main applications?",
                    "What are the key benefits?",
                    "What are the growth drivers?",
                    "What industries are impacted?",
                    "What are the future trends?"
                ]

                print(f"\n💬 TESTING FOLLOW-UP QUESTIONS:")
                print("-" * 40)

                for i, question in enumerate(test_questions, 1):
                    print(f"\n❓ Question {i}: {question}")
                    print("🤖 Response:")

                    response = galileo.ask_followup(question)

                    # Show first 300 characters of response
                    preview = response[:300] + "..." if len(response) > 300 else response
                    print(f"{preview}")

                    # Check if it came from report or analysis
                    if "_Source:" in response:
                        print("✅ Response source: REPORT (Enhanced)")
                    else:
                        print("📊 Response source: ANALYSIS (Fallback)")

                    print("-" * 40)

                print(f"\n✅ Enhanced context system test completed!")
                print(f"📈 Chat history entries: {len(galileo.research_context.get('chat_history', []))}")

            else:
                print("❌ No completed research sessions found for testing")
                print("💡 Run a research session first with: python galileo_optimized.py")

        else:
            print("❌ No research sessions found")
            print("💡 Run a research session first with: python galileo_optimized.py")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_context()
#!/usr/bin/env python3
"""
Optimized Project Galileo - AI Research Agent
Streamlined version with context retention and improved performance
"""

import sys
import os
import json
import pickle
from datetime import datetime
from typing import Dict, List, Any

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from agents.planner import QueryPlanner
from agents.scout import WebScout
from agents.analyst import InformationAnalyst
from agents.writer import ReportWriter

class OptimizedGalileo:
    """Optimized Galileo with context retention and streamlined pipeline"""

    def __init__(self):
        # Validate configuration
        Config.validate()

        # Initialize agents
        self.planner = QueryPlanner()
        self.scout = WebScout()
        self.analyst = InformationAnalyst()
        self.writer = ReportWriter()

        # Context storage with persistence
        self.context_file = "galileo_context.pkl"
        self.research_context = self._load_context()

        print("✅ Optimized Galileo initialized with context retention")

    def _load_context(self) -> Dict:
        """Load previous context if exists"""
        if os.path.exists(self.context_file):
            try:
                with open(self.context_file, 'rb') as f:
                    context = pickle.load(f)
                    print("📂 Loaded previous research context")
                    return context
            except:
                pass

        return {
            'sessions': {},
            'current_session': None,
            'last_topic': '',
            'last_depth': '',
            'chat_history': []
        }

    def _save_context(self):
        """Save context to file"""
        try:
            with open(self.context_file, 'wb') as f:
                pickle.dump(self.research_context, f)
        except Exception as e:
            print(f"⚠️  Context save failed: {e}")

    def research_topic(self, topic: str = None, depth: str = None, force_new: bool = False):
        """Main research pipeline with context awareness"""

        # Get user input if not provided
        if not topic:
            topic, depth = self._get_user_input()

        # Check if we already researched this topic
        session_key = f"{topic.lower()}_{depth}"
        if not force_new and session_key in self.research_context.get('sessions', {}):
            print(f"\n📚 Found previous research on '{topic}' at {depth} level")
            choice = input("Use previous research (y) or start fresh (n)? [y/n]: ").lower()
            if choice == 'y':
                self.research_context['current_session'] = session_key
                session_data = self.research_context['sessions'][session_key]
                self._display_research_summary(session_data)
                return session_data

        print("🚀 Starting optimized research pipeline...")

        # Initialize new session
        session_data = {
            'topic': topic,
            'depth': depth,
            'start_time': datetime.now().isoformat(),
            'sub_questions': [],
            'sources_data': {},
            'analysis_results': {},
            'final_report': {},
            'status': 'started'
        }

        try:
            # Stage 1: Planning (Optimized)
            print(f"\n🧠 STAGE 1: PLANNING")
            session_data['sub_questions'] = self.planner.decompose_query(topic, depth)
            session_data['status'] = 'planned'
            print(f"✅ Generated {len(session_data['sub_questions'])} focused questions")

            # Stage 2: Scouting (Optimized)
            print(f"\n🔍 STAGE 2: SCOUTING")
            self.scout.configure_for_depth(depth)
            session_data['sources_data'] = self.scout.search_all_questions(session_data['sub_questions'])
            session_data['status'] = 'scouted'

            total_sources = sum(len(sources) for sources in session_data['sources_data'].values())
            print(f"✅ Collected {total_sources} sources")

            # Stage 3: Analysis (Streamlined)
            print(f"\n🔬 STAGE 3: ANALYSIS")
            session_data['analysis_results'] = self.analyst.analyze_and_synthesize(
                session_data['sources_data'], depth
            )
            session_data['status'] = 'analyzed'
            print("✅ Analysis completed")

            # Stage 4: Writing (Optimized)
            print(f"\n✍️  STAGE 4: WRITING")
            session_data['final_report'] = self.writer.generate_evidence_backed_report(
                {'user_topic': topic, 'user_depth': depth, 'analysis_results': session_data['analysis_results']},
                lambda: self._get_depth_config(depth)
            )
            session_data['status'] = 'completed'

            # Save report
            filename = self.writer.save_report_to_file(session_data['final_report'])
            session_data['report_file'] = filename

            print(f"✅ Report saved: {filename}")

            # Save to context
            self.research_context['sessions'][session_key] = session_data
            self.research_context['current_session'] = session_key
            self.research_context['last_topic'] = topic
            self.research_context['last_depth'] = depth

            self._save_context()

            session_data['end_time'] = datetime.now().isoformat()
            self._display_research_summary(session_data)

            return session_data

        except Exception as e:
            print(f"❌ Pipeline error: {e}")
            session_data['status'] = 'failed'
            session_data['error'] = str(e)
            return session_data

    def ask_followup(self, question: str) -> str:
        """Ask follow-up questions about the current research - Enhanced with report awareness"""

        if not self.research_context.get('current_session'):
            return "No active research session. Please research a topic first."

        session_key = self.research_context['current_session']
        session_data = self.research_context['sessions'][session_key]

        if session_data['status'] != 'completed':
            return "Research not completed yet. Please complete the research first."

        # ENHANCED: Try report-aware search first, then fallback to analysis
        report_response = self._search_report_content(question, session_data)
        if report_response:
            # Add to chat history
            self.research_context['chat_history'].append({
                'timestamp': datetime.now().isoformat(),
                'question': question,
                'response': report_response,
                'session': session_key,
                'source': 'report'
            })
            self._save_context()
            return report_response

        # FALLBACK: Use existing analysis-based approach
        analysis = session_data.get('analysis_results', {})
        sub_answers = analysis.get('sub_question_answers', {})

        # Simple keyword matching for analysis results
        question_lower = question.lower()
        relevant_info = []

        for sub_q, answer_data in sub_answers.items():
            if any(word in sub_q.lower() for word in question_lower.split() if len(word) > 3):
                relevant_info.append({
                    'question': sub_q,
                    'answer': answer_data.get('answer', ''),
                    'sources': answer_data.get('source_urls', [])
                })

        if not relevant_info:
            return "I don't have specific information about that in the current research. Try asking about the main topics covered."

        # Format response from analysis
        response = f"Based on the research analysis for '{session_data['topic']}':\n\n"
        for info in relevant_info[:2]:  # Limit to top 2 relevant answers
            response += f"**{info['question']}**\n{info['answer']}\n"
            if info['sources']:
                response += f"Sources: {', '.join(info['sources'][:2])}\n\n"

        # Add to chat history
        self.research_context['chat_history'].append({
            'timestamp': datetime.now().isoformat(),
            'question': question,
            'response': response,
            'session': session_key,
            'source': 'analysis'
        })

        self._save_context()
        return response

    def _search_report_content(self, question: str, session_data: Dict) -> str:
        """Search within the actual markdown report for relevant content"""
        try:
            # Get the report file path
            report_file = session_data.get('report_file')
            if not report_file or not os.path.exists(report_file):
                return None

            # Read the markdown report
            with open(report_file, 'r', encoding='utf-8') as f:
                report_content = f.read()

            # Find relevant sections based on question keywords
            relevant_sections = self._extract_relevant_sections(question, report_content)

            if relevant_sections:
                response = f"Based on your research report on '{session_data['topic']}':\n\n"
                for section in relevant_sections[:2]:  # Limit to top 2 sections
                    response += f"{section}\n\n"

                response += f"_Source: {report_file}_"
                return response

            return None

        except Exception as e:
            print(f"Debug: Report search error: {e}")
            return None

    def _extract_relevant_sections(self, question: str, report_content: str) -> List[str]:
        """Extract sections from the report that are relevant to the question"""
        try:
            question_words = set(word.lower() for word in question.split() if len(word) > 3)
            relevant_sections = []

            # Enhanced keyword matching with synonyms
            expanded_keywords = question_words.copy()
            keyword_map = {
                'applications': ['uses', 'application', 'applied', 'industry', 'sector'],
                'benefits': ['advantage', 'value', 'benefit', 'improvement'],
                'growth': ['expansion', 'increase', 'development', 'driver'],
                'industries': ['sector', 'industry', 'business', 'field'],
                'trends': ['future', 'trend', 'outlook', 'projection']
            }

            for word in question_words:
                if word in keyword_map:
                    expanded_keywords.update(keyword_map[word])

            # Split report into sections and paragraphs
            sections = report_content.split('\n## ')

            for section in sections:
                if not section.strip() or section.startswith('---'):
                    continue

                # Add back the header marker if it was split
                if not section.startswith('#'):
                    section = '## ' + section

                # Check section relevance
                section_lower = section.lower()
                matches = sum(1 for word in expanded_keywords if word in section_lower)

                # More flexible matching - even 1 good keyword match
                if matches >= 1:
                    # Extract paragraphs from this section
                    paragraphs = [p.strip() for p in section.split('\n\n') if p.strip()]

                    for para in paragraphs:
                        if len(para) < 50:  # Skip very short paragraphs
                            continue

                        para_lower = para.lower()
                        para_matches = sum(1 for word in expanded_keywords if word in para_lower)

                        if para_matches >= 1:
                            # Clean up formatting
                            clean_para = para.replace('→', '').strip()
                            if (clean_para and
                                not clean_para.startswith('---') and
                                not clean_para.startswith('*') and
                                len(clean_para) > 100):

                                relevant_sections.append({
                                    'content': clean_para,
                                    'score': para_matches
                                })

            # Sort by relevance score and return top sections
            relevant_sections.sort(key=lambda x: x['score'], reverse=True)
            return [section['content'] for section in relevant_sections[:3]]

        except Exception as e:
            print(f"Debug: Section extraction error: {e}")
            return []

    def _get_user_input(self) -> tuple:
        """Get optimized user input"""
        print("\n🎯 RESEARCH SETUP")

        # Suggest recent topic if available
        if self.research_context.get('last_topic'):
            print(f"Recent topic: {self.research_context['last_topic']}")

        topic = input("What do you want to research? ").strip()

        while not topic:
            topic = input("Please enter a valid topic: ").strip()

        print(f"\n📊 EXPERIENCE LEVEL")
        print("1. Beginner (simple explanations)")
        print("2. Intermediate (balanced detail)")
        print("3. Expert (technical depth)")

        # Default to previous depth if available
        default_depth = "2"
        if self.research_context.get('last_depth'):
            depth_map = {'beginner': '1', 'intermediate': '2', 'expert': '3'}
            default_depth = depth_map.get(self.research_context['last_depth'], '2')

        choice = input(f"Select level (1-3) [{default_depth}]: ").strip() or default_depth

        depth_map = {'1': 'beginner', '2': 'intermediate', '3': 'expert'}
        depth = depth_map.get(choice, 'intermediate')

        return topic, depth

    def _get_depth_config(self, depth: str) -> Dict:
        """Get depth configuration for writer"""
        configs = {
            'beginner': {
                'explanation_style': 'simple and clear',
                'technical_terms': 'minimal, with definitions',
                'detail_level': 'basic concepts and overview',
                'examples': 'lots of practical examples',
                'structure': 'step-by-step explanations'
            },
            'intermediate': {
                'explanation_style': 'balanced technical and accessible',
                'technical_terms': 'moderate, assume some knowledge',
                'detail_level': 'detailed with some technical depth',
                'examples': 'practical and theoretical examples',
                'structure': 'organized sections with depth'
            },
            'expert': {
                'explanation_style': 'technical and comprehensive',
                'technical_terms': 'full technical vocabulary',
                'detail_level': 'deep analysis and advanced concepts',
                'examples': 'complex real-world applications',
                'structure': 'detailed analysis with citations'
            }
        }

        return {
            'user_depth': depth,
            'depth_config': configs.get(depth, configs['intermediate'])
        }

    def _display_research_summary(self, session_data: Dict):
        """Display research session summary"""
        print(f"\n📊 RESEARCH SUMMARY")
        print(f"Topic: {session_data['topic']}")
        print(f"Level: {session_data['depth']}")
        print(f"Status: {session_data['status']}")
        print(f"Sub-questions: {len(session_data.get('sub_questions', []))}")

        if session_data.get('sources_data'):
            total_sources = sum(len(sources) for sources in session_data['sources_data'].values())
            print(f"Sources: {total_sources}")

        if session_data.get('final_report'):
            metadata = session_data['final_report'].get('metadata', {})
            print(f"Report: {metadata.get('word_count', 0)} words, {metadata.get('citation_count', 0)} citations")

        if session_data.get('report_file'):
            print(f"File: {session_data['report_file']}")

    def show_recent_research(self):
        """Show recent research sessions"""
        sessions = self.research_context.get('sessions', {})
        if not sessions:
            print("No previous research sessions found")
            return

        print("\n📚 RECENT RESEARCH SESSIONS")
        for i, (key, data) in enumerate(list(sessions.items())[-5:], 1):
            print(f"{i}. {data['topic']} ({data['depth']}) - {data['status']}")

    def interactive_mode(self):
        """Interactive mode with context retention"""
        print("🔬 OPTIMIZED GALILEO - INTERACTIVE MODE")
        print("Commands: research, ask, recent, quit")

        while True:
            try:
                command = input("\n> ").strip().lower()

                if command == 'quit' or command == 'exit':
                    print("👋 Goodbye!")
                    break
                elif command == 'research':
                    self.research_topic()
                elif command.startswith('ask '):
                    question = command[4:].strip()
                    if question:
                        response = self.ask_followup(question)
                        print(f"\n💬 {response}")
                    else:
                        print("Please provide a question after 'ask'")
                elif command == 'recent':
                    self.show_recent_research()
                elif command == 'help':
                    print("\nCommands:")
                    print("- research: Start new research")
                    print("- ask [question]: Ask about current research")
                    print("- recent: Show recent sessions")
                    print("- quit: Exit")
                else:
                    print("Unknown command. Type 'help' for commands.")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")

def main():
    """Main entry point"""
    print("🔬 OPTIMIZED PROJECT GALILEO")
    print("=" * 50)

    try:
        galileo = OptimizedGalileo()

        # Check command line arguments
        if len(sys.argv) == 2 and sys.argv[1] == '--interactive':
            galileo.interactive_mode()
        else:
            # Single research mode
            result = galileo.research_topic()
            if result and result['status'] == 'completed':
                print("\n💬 You can now ask follow-up questions!")
                while True:
                    question = input("\nAsk a question (or 'quit'): ").strip()
                    if question.lower() in ['quit', 'exit', '']:
                        break
                    response = galileo.ask_followup(question)
                    print(f"\n{response}")

    except KeyboardInterrupt:
        print("\n👋 Research cancelled")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
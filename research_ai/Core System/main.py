import sys
import os
import json
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from agents.planner import QueryPlanner
from agents.scout import WebScout
from agents.analyst import InformationAnalyst
from agents.writer import ReportWriter

# Import LangChain orchestrator
try:
    from agents.orchestrator import GalileoOrchestrator
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  LangChain not available: {e}")
    LANGCHAIN_AVAILABLE = False

class ProjectGalileo:
    def __init__(self):
        try:
            Config.validate()
            self.planner = QueryPlanner()
            self.scout = WebScout()
            self.analyst = InformationAnalyst()
            self.writer = ReportWriter()

            # Context storage between agents
            self.research_context = {
                'user_topic': '',
                'user_depth': '',
                'sub_questions': [],
                'sources_data': {},
                'analysis_results': {},
                'final_report': {},
                'start_time': datetime.now().isoformat(),
                'session_id': str(id(self))
            }

            print("✅ Project Galileo initialized successfully")
        except Exception as e:
            print(f"❌ Initialization Error: {e}")
            raise

    def run_complete_research_pipeline(self):
        """
        Complete research pipeline: Planner → Scout → Analyst → Writer
        """
        print("=" * 70)
        print("🔬 PROJECT GALILEO - COMPLETE RESEARCH PIPELINE")
        print("=" * 70)

        # Step 1: Get user input (2 questions only)
        self._get_user_input()

        # Step 2: Run Planner
        self._run_planner_stage()

        # Step 3: Run Scout
        self._run_scout_stage()

        # Step 4: Run Analyst
        self._run_analyst_stage()

        # Step 5: Run Writer
        self._run_writer_stage()

        # Step 6: Show final results
        self._show_final_results()

        return self.research_context

    def _get_user_input(self):
        """Get 2 questions from user"""
        print("\n🎯 QUESTION 1:")
        topic = input("What topic do you want to research? ").strip()

        while not topic:
            print("❌ Please enter a valid topic")
            topic = input("What topic do you want to research? ").strip()

        print(f"\n🎚️  QUESTION 2:")
        print("What is your experience level with this topic?")
        print("1. Beginner (simple explanations, basic concepts)")
        print("2. Intermediate (balanced detail, some technical terms)")
        print("3. Expert (advanced analysis, technical depth)")

        while True:
            choice = input("Select your level (1-3): ").strip()

            if choice == "1":
                depth = "beginner"
                break
            elif choice == "2":
                depth = "intermediate"
                break
            elif choice == "3":
                depth = "expert"
                break
            else:
                print("❌ Please enter 1, 2, or 3")

        self.research_context['user_topic'] = topic
        self.research_context['user_depth'] = depth

        print(f"\n✅ Topic: {topic}")
        print(f"✅ Depth: {depth}")

    def _run_planner_stage(self):
        """Run Planner agent"""
        print(f"\n" + "="*50)
        print("🧠 STAGE 1: PLANNER")
        print("="*50)

        try:
            print(f"Planning comprehensive coverage for: {self.research_context['user_topic']}")

            sub_questions = self.planner.decompose_query(
                query=self.research_context['user_topic'],
                user_depth=self.research_context['user_depth']
            )

            self.research_context['sub_questions'] = sub_questions

            print(f"✅ Generated {len(sub_questions)} sub-questions:")
            for i, question in enumerate(sub_questions, 1):
                print(f"   {i}. {question}")

        except Exception as e:
            print(f"❌ Planner error: {e}")
            # Fallback
            self.research_context['sub_questions'] = [
                f"What is {self.research_context['user_topic']}",
                f"How does {self.research_context['user_topic']} work",
                f"Applications of {self.research_context['user_topic']}"
            ]

    def _run_scout_stage(self):
        """Run Scout agent"""
        print(f"\n" + "="*50)
        print("🔍 STAGE 2: SCOUT")
        print("="*50)

        try:
            # Configure scout with depth
            self.scout.configure_for_depth(self.research_context['user_depth'])

            # Search for sources
            print("Starting deep internet search...")
            sources_data = self.scout.search_all_questions(
                self.research_context['sub_questions']
            )

            self.research_context['sources_data'] = sources_data

            total_sources = sum(len(sources) for sources in sources_data.values())
            print(f"✅ Scout collected {total_sources} sources with extracted content")

        except Exception as e:
            print(f"❌ Scout error: {e}")
            self.research_context['sources_data'] = {}

    def _run_analyst_stage(self):
        """Run Analyst agent"""
        print(f"\n" + "="*50)
        print("🔬 STAGE 3: ANALYST")
        print("="*50)

        try:
            if not self.research_context['sources_data']:
                print("⚠️  No sources available for analysis")
                return

            # Analyze and synthesize information
            analysis_results = self.analyst.analyze_and_synthesize(
                sources_data=self.research_context['sources_data'],
                user_depth=self.research_context['user_depth']
            )

            self.research_context['analysis_results'] = analysis_results

            answers_count = len(analysis_results.get('sub_question_answers', {}))
            print(f"✅ Analyst synthesized {answers_count} comprehensive answers")

        except Exception as e:
            print(f"❌ Analyst error: {e}")
            self.research_context['analysis_results'] = {}

    def _run_writer_stage(self):
        """Run Writer agent"""
        print(f"\n" + "="*50)
        print("✍️  STAGE 4: WRITER")
        print("="*50)

        try:
            if not self.research_context.get('analysis_results'):
                print("⚠️  No analysis results available for report generation")
                return

            # Generate evidence-backed report
            print("Generating evidence-backed markdown report...")

            report_result = self.writer.generate_evidence_backed_report(
                research_context=self.research_context,
                get_depth_function=self.get_depth_for_writer
            )

            self.research_context['final_report'] = report_result

            # Save report to file
            filename = self.writer.save_report_to_file(report_result)

            word_count = report_result['metadata']['word_count']
            citation_count = report_result['metadata']['citation_count']

            print(f"✅ Generated {word_count} word report with {citation_count} citations")
            print(f"💾 Saved as: {filename}")

        except Exception as e:
            print(f"❌ Writer error: {e}")
            self.research_context['final_report'] = {}

    def _show_final_results(self):
        """Show final pipeline results"""
        print(f"\n" + "="*70)
        print("🎉 RESEARCH PIPELINE COMPLETED")
        print("="*70)

        # Calculate execution time
        start_time = datetime.fromisoformat(self.research_context['start_time'])
        execution_time = (datetime.now() - start_time).total_seconds()

        print(f"🎯 Topic: {self.research_context['user_topic']}")
        print(f"🎚️  User Level: {self.research_context['user_depth']}")
        print(f"❓ Sub-questions: {len(self.research_context.get('sub_questions', []))}")
        print(f"📚 Sources: {sum(len(s) for s in self.research_context.get('sources_data', {}).values())}")
        print(f"🔬 Analysis: {'✅ Complete' if self.research_context.get('analysis_results') else '❌ Failed'}")
        print(f"📝 Report: {'✅ Generated' if self.research_context.get('final_report') else '❌ Failed'}")
        print(f"⏱️  Total Time: {execution_time:.1f} seconds")

        # Show report summary if available
        if self.research_context.get('final_report'):
            metadata = self.research_context['final_report']['metadata']
            print(f"\n📊 REPORT SUMMARY:")
            print(f"   • Words: {metadata.get('word_count', 0)}")
            print(f"   • Citations: {metadata.get('citation_count', 0)}")
            print(f"   • Sections: {metadata.get('section_count', 0)}")

    def get_depth_for_writer(self):
        """Function that writer agent calls to get user depth"""
        user_depth = self.research_context.get('user_depth', 'intermediate')

        depth_configs = {
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
            'user_depth': user_depth,
            'depth_config': depth_configs.get(user_depth, depth_configs['intermediate'])
        }

def run_langchain_mode():
    """Run with LangChain orchestration"""
    print("🚀 Project Galileo - LangChain Mode")
    print("=" * 50)

    try:
        orchestrator = GalileoOrchestrator()

        # Get user input
        print("\n🎯 QUESTION 1:")
        topic = input("What topic do you want to research? ").strip()

        print("\n🎚️  QUESTION 2:")
        print("What is your experience level?")
        print("1. Beginner   2. Intermediate   3. Expert")

        depth_choice = input("Select (1-3): ").strip()
        depth_map = {'1': 'beginner', '2': 'intermediate', '3': 'expert'}
        user_depth = depth_map.get(depth_choice, 'intermediate')

        # Execute LangChain pipeline
        result = orchestrator.execute_research_pipeline(topic, user_depth)

        if result['success']:
            summary = result['pipeline_summary']
            print(f"\n✅ LangChain research completed!")
            print(f"📊 Summary: {summary}")
        else:
            print(f"❌ Pipeline failed: {result['error']}")

    except Exception as e:
        print(f"❌ LangChain error: {e}")

def main():
    """Main entry point with mode selection"""
    print("🔬 PROJECT GALILEO - AI RESEARCH AGENT")
    print("=" * 60)

    # Check if LangChain is available and offer choice
    if LANGCHAIN_AVAILABLE:
        print("\nSelect execution mode:")
        print("1. Standard Mode (Direct agent execution)")
        print("2. LangChain Mode (Advanced orchestration)")

        mode_choice = input("\nSelect mode (1-2): ").strip()

        if mode_choice == "2":
            run_langchain_mode()
            return

    # Standard mode (original implementation)
    try:
        print("🚀 Starting standard research pipeline...")

        # Initialize and run
        agent = ProjectGalileo()
        result = agent.run_complete_research_pipeline()

        print("\n✅ Research completed successfully!")

    except KeyboardInterrupt:
        print("\n\n👋 Research cancelled by user")
    except Exception as e:
        print(f"❌ Critical Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
from langchain.agents import AgentExecutor, create_react_agent
from langchain.schema import SystemMessage, HumanMessage
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, List, Any
import json
from datetime import datetime

from agents.planner import QueryPlanner
from agents.scout import WebScout
from agents.analyst import InformationAnalyst
from agents.writer import ReportWriter
from config import Config

class GalileoOrchestrator:
    """
    LangChain-based orchestrator for Project Galileo
    Manages the full research pipeline: Planner → Scout → Analyst → Writer
    """

    def __init__(self):
        # Initialize LangChain LLM with Gemini compatibility
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=Config.GEMINI_API_KEY,
            temperature=0.3,
            convert_system_message_to_human=True  # Fix for Gemini compatibility
        )

        # Initialize individual agents
        self.planner = QueryPlanner()
        self.scout = WebScout()
        self.analyst = InformationAnalyst()
        self.writer = ReportWriter()

        # Shared memory across the pipeline
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        # Research context storage
        self.research_context = {
            'pipeline_start_time': datetime.now().isoformat(),
            'user_topic': '',
            'user_depth': '',
            'sub_questions': [],
            'sources_data': {},
            'analysis_results': {},
            'final_report': {},
            'pipeline_status': 'initialized'
        }

        # Create LangChain tools for each agent
        self.tools = self._create_agent_tools()

        # Create the main orchestration agent
        self.orchestration_agent = self._create_orchestration_agent()

        print("🤖 LangChain Galileo Orchestrator initialized")

    def _create_agent_tools(self) -> List[Tool]:
        """Create LangChain tools for each research agent"""

        tools = [
            Tool(
                name="query_planner",
                description="Decomposes research queries into comprehensive sub-questions based on user depth level",
                func=self._planner_tool
            ),
            Tool(
                name="web_scout",
                description="Searches internet deeply for sources and extracts content for research sub-questions",
                func=self._scout_tool
            ),
            Tool(
                name="information_analyst",
                description="Analyzes and synthesizes information from multiple sources with source attribution",
                func=self._analyst_tool
            ),
            Tool(
                name="report_writer",
                description="Generates evidence-backed markdown reports with inline citations",
                func=self._writer_tool
            ),
            Tool(
                name="get_user_depth",
                description="Retrieves user experience level and writing configuration for report generation",
                func=self._get_user_depth_tool
            ),
            Tool(
                name="update_context",
                description="Updates the research context with new information from any agent",
                func=self._update_context_tool
            )
        ]

        return tools

    def _create_orchestration_agent(self):
        """Create the main LangChain orchestration agent"""

        prompt_template = """
        You are the Orchestrator for Project Galileo, an autonomous AI research system.

        Your role is to coordinate a research pipeline with these agents:
        1. PLANNER: Decomposes queries into sub-questions
        2. SCOUT: Searches internet and extracts content
        3. ANALYST: Synthesizes information across sources
        4. WRITER: Creates evidence-backed reports

        RESEARCH PIPELINE:
        1. Call query_planner to decompose the topic
        2. Call web_scout to find and extract sources
        3. Call information_analyst to synthesize findings
        4. Call report_writer for final report

        You have access to the following tools:
        {tools}

        Tool names: {tool_names}

        Use the following format:

        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question

        Question: {input}
        Thought: {agent_scratchpad}
        """

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["input", "agent_scratchpad"],
            partial_variables={
                "tools": "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools]),
                "tool_names": ", ".join([tool.name for tool in self.tools])
            }
        )

        # Create the agent
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

        # Create executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            max_iterations=10,
            handle_parsing_errors=True
        )

        return agent_executor

    def execute_research_pipeline(self, user_topic: str, user_depth: str) -> Dict:
        """
        Execute the complete research pipeline using LangChain orchestration
        """

        print(f"\n🚀 LangChain Pipeline Starting...")
        print(f"🎯 Topic: {user_topic}")
        print(f"🎚️  Depth: {user_depth}")

        # Update initial context
        self.research_context.update({
            'user_topic': user_topic,
            'user_depth': user_depth,
            'pipeline_status': 'running'
        })

        try:
            # Execute the orchestrated research pipeline
            pipeline_instruction = f"""
            Execute complete research pipeline for:
            TOPIC: "{user_topic}"
            USER DEPTH: "{user_depth}"
            
            Follow this sequence:
            1. Use query_planner to decompose the topic into sub-questions
            2. Use web_scout to search and extract content for each sub-question  
            3. Use information_analyst to synthesize the collected information
            4. Use get_user_depth then report_writer to create the final report
            5. Update context after each step
            
            Provide status updates throughout the process.
            """

            result = self.orchestration_agent.invoke({
                "input": pipeline_instruction
            })

            self.research_context['pipeline_status'] = 'completed'
            self.research_context['pipeline_end_time'] = datetime.now().isoformat()

            print(f"\n✅ LangChain Pipeline Completed!")

            return {
                'success': True,
                'research_context': self.research_context,
                'orchestration_result': result,
                'pipeline_summary': self._generate_pipeline_summary()
            }

        except Exception as e:
            print(f"❌ Pipeline execution error: {e}")
            self.research_context['pipeline_status'] = 'failed'
            self.research_context['error'] = str(e)

            return {
                'success': False,
                'error': str(e),
                'research_context': self.research_context
            }

    def _planner_tool(self, query_input: str) -> str:
        """LangChain tool wrapper for Planner agent"""
        try:
            # Parse input if it's JSON
            if query_input.startswith('{'):
                input_data = json.loads(query_input)
                topic = input_data.get('topic', query_input)
                depth = input_data.get('depth', self.research_context.get('user_depth', 'intermediate'))
            else:
                topic = self.research_context.get('user_topic', query_input)
                depth = self.research_context.get('user_depth', 'intermediate')

            print(f"🧠 PLANNER: Processing {topic} at {depth} level...")

            sub_questions = self.planner.decompose_query(topic, depth)
            self.research_context['sub_questions'] = sub_questions

            return f"Generated {len(sub_questions)} sub-questions: {json.dumps(sub_questions)}"

        except Exception as e:
            return f"Planner error: {str(e)}"

    def _scout_tool(self, scout_input: str) -> str:
        """LangChain tool wrapper for Scout agent"""
        try:
            sub_questions = self.research_context.get('sub_questions', [])
            user_depth = self.research_context.get('user_depth', 'intermediate')

            if not sub_questions:
                return "Error: No sub-questions available. Run planner first."

            print(f"🔍 SCOUT: Searching for {len(sub_questions)} queries at {user_depth} depth...")

            self.scout.configure_for_depth(user_depth)
            sources_data = self.scout.search_all_questions(sub_questions)
            self.research_context['sources_data'] = sources_data

            total_sources = sum(len(sources) for sources in sources_data.values())

            return f"Scout collected {total_sources} sources across {len(sub_questions)} queries"

        except Exception as e:
            return f"Scout error: {str(e)}"

    def _analyst_tool(self, analyst_input: str) -> str:
        """LangChain tool wrapper for Analyst agent"""
        try:
            sources_data = self.research_context.get('sources_data', {})
            user_depth = self.research_context.get('user_depth', 'intermediate')

            if not sources_data:
                return "Error: No sources data available. Run scout first."

            print(f"🔬 ANALYST: Analyzing sources at {user_depth} depth...")

            analysis_results = self.analyst.analyze_and_synthesize(sources_data, user_depth)
            self.research_context['analysis_results'] = analysis_results

            answers_count = len(analysis_results.get('sub_question_answers', {}))

            return f"Analyst completed synthesis for {answers_count} sub-questions with full source attribution"

        except Exception as e:
            return f"Analyst error: {str(e)}"

    def _writer_tool(self, writer_input: str) -> str:
        """LangChain tool wrapper for Writer agent"""
        try:
            if not self.research_context.get('analysis_results'):
                return "Error: No analysis results available. Run analyst first."

            print(f"✍️  WRITER: Generating evidence-backed report...")

            # Writer calls the depth function
            report_result = self.writer.generate_evidence_backed_report(
                self.research_context,
                self.get_depth_for_writer
            )

            self.research_context['final_report'] = report_result

            # Save report to file
            filename = self.writer.save_report_to_file(report_result)

            word_count = report_result['metadata']['word_count']
            citation_count = report_result['metadata']['citation_count']

            return f"Generated {word_count} word report with {citation_count} citations. Saved as {filename}"

        except Exception as e:
            return f"Writer error: {str(e)}"

    def _get_user_depth_tool(self, depth_input: str) -> str:
        """LangChain tool to get user depth configuration"""
        try:
            depth_info = self.get_depth_for_writer()
            return f"Retrieved depth configuration: {json.dumps(depth_info)}"
        except Exception as e:
            return f"Depth retrieval error: {str(e)}"

    def _update_context_tool(self, context_input: str) -> str:
        """LangChain tool to update research context"""
        try:
            # Parse context update
            if context_input.startswith('{'):
                update_data = json.loads(context_input)
                self.research_context.update(update_data)
                return f"Context updated with: {list(update_data.keys())}"
            else:
                return f"Context status: {self.research_context['pipeline_status']}"
        except Exception as e:
            return f"Context update error: {str(e)}"

    def get_depth_for_writer(self) -> Dict:
        """Function that writer calls to get user depth configuration"""
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

    def _generate_pipeline_summary(self) -> Dict:
        """Generate summary of the complete pipeline execution"""

        return {
            'topic': self.research_context.get('user_topic'),
            'user_depth': self.research_context.get('user_depth'),
            'sub_questions_count': len(self.research_context.get('sub_questions', [])),
            'sources_collected': sum(
                len(sources) for sources in self.research_context.get('sources_data', {}).values()
            ),
            'analysis_completed': bool(self.research_context.get('analysis_results')),
            'report_generated': bool(self.research_context.get('final_report')),
            'pipeline_status': self.research_context.get('pipeline_status'),
            'execution_time': self._calculate_execution_time()
        }

    def _calculate_execution_time(self) -> str:
        """Calculate total pipeline execution time"""
        try:
            start_time = datetime.fromisoformat(self.research_context['pipeline_start_time'])

            if 'pipeline_end_time' in self.research_context:
                end_time = datetime.fromisoformat(self.research_context['pipeline_end_time'])
                duration = end_time - start_time
                return f"{duration.total_seconds():.1f} seconds"
            else:
                return "Pipeline still running"
        except:
            return "Unknown"

    def get_orchestrator_stats(self) -> Dict:
        """Get orchestrator statistics"""
        return {
            'framework': 'langchain',
            'llm': 'gemini-2.5-flash',
            'agents': ['planner', 'scout', 'analyst', 'writer'],
            'tools_count': len(self.tools),
            'memory_type': 'conversation_buffer',
            'pipeline_status': self.research_context.get('pipeline_status', 'unknown')
        }
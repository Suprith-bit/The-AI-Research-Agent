from langchain.tools import Tool
from typing import List, Dict, Any

class GalileoToolFactory:
    """Factory for creating LangChain tools for Galileo agents"""

    @staticmethod
    def create_research_tools(orchestrator) -> List[Tool]:
        """Create all research tools for LangChain integration"""

        return [
            Tool(
                name="execute_research_pipeline",
                description="Execute complete research pipeline from topic to final report",
                func=lambda x: orchestrator.execute_research_pipeline_tool(x)
            ),
            Tool(
                name="get_pipeline_status",
                description="Get current status of research pipeline execution",
                func=lambda x: orchestrator.get_pipeline_status()
            ),
            Tool(
                name="save_research_context",
                description="Save current research context to file",
                func=lambda x: orchestrator.save_context_to_file()
            )
        ]
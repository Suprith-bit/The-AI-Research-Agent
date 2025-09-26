"""
Project Galileo Agent System
============================

AI research agents for autonomous information gathering and analysis.

Agents:
- QueryPlanner: Decomposes research queries into comprehensive sub-questions
- WebScout: Searches internet and extracts content from multiple sources
- InformationAnalyst: Synthesizes information across sources with attribution
- ReportWriter: Generates evidence-backed markdown reports with citations

Optional LangChain Orchestration:
- GalileoOrchestrator: LangChain-based agent coordination and memory management
"""

from .planner import QueryPlanner
from .scout import WebScout
from .analyst import InformationAnalyst
from .writer import ReportWriter

# Optional LangChain import
try:
    from .orchestrator import GalileoOrchestrator
    __all__ = ['QueryPlanner', 'WebScout', 'InformationAnalyst', 'ReportWriter', 'GalileoOrchestrator']
except ImportError:
    __all__ = ['QueryPlanner', 'WebScout', 'InformationAnalyst', 'ReportWriter']

# Agent metadata
AGENT_INFO = {
    'planner': {
        'description': 'Query decomposition and research planning',
        'model': 'gemini-2.5-flash',
        'features': ['unlimited_coverage', 'depth_aware', 'comprehensive_questions']
    },
    'scout': {
        'description': 'Deep internet search and content extraction',
        'api': 'serper',
        'features': ['8+_sources_per_query', 'content_extraction', 'relevancy_ranking']
    },
    'analyst': {
        'description': 'Information synthesis and source attribution',
        'model': 'gemini-2.5-flash',
        'features': ['cross_source_synthesis', 'contradiction_detection', 'quality_assessment']
    },
    'writer': {
        'description': 'Evidence-backed report generation',
        'model': 'gemini-2.5-flash',
        'features': ['inline_citations', 'markdown_format', 'depth_aware_writing']
    }
}
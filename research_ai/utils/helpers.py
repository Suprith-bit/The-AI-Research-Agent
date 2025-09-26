"""
Utility functions for Project Galileo research pipeline
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any
from urllib.parse import urlparse

def clean_text(text: str) -> str:
    """Clean and normalize text content"""
    if not text:
        return ""

    # Remove extra whitespace
    cleaned = re.sub(r'\s+', ' ', text.strip())

    # Remove common unwanted patterns
    unwanted = [
        r'cookie.*?policy',
        r'privacy.*?policy',
        r'terms.*?service',
        r'subscribe.*?newsletter'
    ]

    for pattern in unwanted:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

    return cleaned.strip()

def extract_domain(url: str) -> str:
    """Extract clean domain name from URL"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        return domain.replace('www.', '')
    except:
        return 'unknown-domain'

def calculate_relevance_score(query: str, content: str) -> float:
    """Calculate basic relevance score between query and content"""
    if not query or not content:
        return 0.0

    query_words = set(word.lower() for word in query.split() if len(word) > 2)
    content_words = set(word.lower() for word in content.split() if len(word) > 2)

    if not query_words:
        return 0.0

    overlap = len(query_words.intersection(content_words))
    return min(overlap / len(query_words), 1.0)

def format_timestamp() -> str:
    """Get formatted timestamp for filenames"""
    return datetime.now().strftime('%Y%m%d_%H%M%S')

def save_json_data(data: Dict, filename: str) -> bool:
    """Save data as JSON file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving JSON: {e}")
        return False

def load_json_data(filename: str) -> Dict:
    """Load data from JSON file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return {}

def validate_url(url: str) -> bool:
    """Validate if URL is properly formatted"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def count_words(text: str) -> int:
    """Count words in text"""
    return len(text.split()) if text else 0

def create_filename_safe_string(text: str, max_length: int = 50) -> str:
    """Create filename-safe string from text"""
    # Remove special characters
    safe = re.sub(r'[^\w\s-]', '', text)
    # Replace spaces with underscores
    safe = re.sub(r'[-\s]+', '_', safe)
    # Limit length
    return safe[:max_length].strip('_')

def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def get_research_summary(research_context: Dict) -> Dict:
    """Generate summary statistics from research context"""

    summary = {
        'topic': research_context.get('user_topic', 'Unknown'),
        'depth': research_context.get('user_depth', 'Unknown'),
        'sub_questions_count': len(research_context.get('sub_questions', [])),
        'total_sources': 0,
        'analysis_complete': bool(research_context.get('analysis_results')),
        'report_generated': bool(research_context.get('final_report'))
    }

    # Count total sources
    sources_data = research_context.get('sources_data', {})
    summary['total_sources'] = sum(len(sources) for sources in sources_data.values())

    # Add report statistics if available
    if research_context.get('final_report'):
        metadata = research_context['final_report'].get('metadata', {})
        summary.update({
            'word_count': metadata.get('word_count', 0),
            'citation_count': metadata.get('citation_count', 0)
        })

    return summary

# Research pipeline status constants
PIPELINE_STATUS = {
    'INITIALIZED': 'initialized',
    'PLANNING': 'planning',
    'SCOUTING': 'scouting',
    'ANALYZING': 'analyzing',
    'WRITING': 'writing',
    'COMPLETED': 'completed',
    'FAILED': 'failed'
}
import google.generativeai as genai
from typing import List, Dict, Any
import json
import re
from datetime import datetime
from config import Config

class ReportWriter:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.5-flash")

        # Writing configuration for high-quality reports
        self.generation_config = genai.types.GenerationConfig(
            temperature=0.3,  # Balanced creativity and consistency
            top_p=0.9,
            top_k=50,
            max_output_tokens=6000,  # Large enough for comprehensive reports
            candidate_count=1
        )

    def generate_evidence_backed_report(self, research_context: Dict,
                                        get_depth_function: callable) -> Dict:
        """
        Generate comprehensive markdown report with inline citations
        Calls user depth function before writing
        """

        print(f"\n✍️  WRITER: Starting evidence-backed report generation...")

        # STEP 1: Get user depth configuration by calling the function
        depth_info = get_depth_function()
        user_depth = depth_info.get('user_depth', 'intermediate')
        depth_config = depth_info.get('depth_config', {})

        print(f"📞 Called depth function - User level: {user_depth}")
        print(f"🎚️  Writing style: {depth_config.get('explanation_style', 'balanced')}")

        # STEP 2: Extract all necessary data from research context
        user_topic = research_context.get('user_topic', 'Research Topic')
        analysis_results = research_context.get('analysis_results', {})
        sub_question_answers = analysis_results.get('sub_question_answers', {})
        synthesized_insights = analysis_results.get('synthesized_insights', {})

        # STEP 3: Build source citation map
        source_citation_map = self._build_source_citation_map(sub_question_answers)

        # STEP 4: Generate the markdown report
        try:
            markdown_report = self._generate_markdown_report(
                user_topic=user_topic,
                sub_question_answers=sub_question_answers,
                synthesized_insights=synthesized_insights,
                user_depth=user_depth,
                depth_config=depth_config,
                analysis_results=analysis_results,
                source_citation_map=source_citation_map
            )

            # STEP 5: Validate citations and format
            validated_report = self._validate_and_format_report(markdown_report, source_citation_map)

            # STEP 6: Generate JSON output
            json_output = self._generate_json_output(
                user_topic, sub_question_answers, synthesized_insights, source_citation_map
            )

            # STEP 7: Generate metadata
            report_metadata = self._generate_report_metadata(
                research_context, user_depth, validated_report
            )

            print(f"✅ Generated {len(validated_report.split())} word report")
            print(f"🔗 Citations included: {report_metadata['citation_count']}")

            return {
                'markdown_report': validated_report,
                'json_output': json_output,
                'metadata': report_metadata,
                'user_depth': user_depth,
                'depth_config': depth_config
            }

        except Exception as e:
            print(f"❌ Report generation error: {e}")
            return self._generate_fallback_report(research_context, user_depth)

    def _generate_markdown_report(self, user_topic: str, sub_question_answers: Dict,
                                  synthesized_insights: Dict, user_depth: str,
                                  depth_config: Dict, analysis_results: Dict,
                                  source_citation_map: Dict) -> str:
        """Generate the main markdown report using AI"""

        report_prompt = f"""
        TASK: Generate a comprehensive, evidence-backed research report in Markdown format.
        
        TOPIC: "{user_topic}"
        USER LEVEL: {user_depth}
        WRITING STYLE: {depth_config.get('explanation_style', 'balanced technical and accessible')}
        TECHNICAL TERMS: {depth_config.get('technical_terms', 'moderate, assume some knowledge')}
        DETAIL LEVEL: {depth_config.get('detail_level', 'detailed with some technical depth')}
        
        RESEARCH DATA TO SYNTHESIZE:
        
        SUB-QUESTION ANSWERS:
        {json.dumps({q: a.get('answer', '') for q, a in sub_question_answers.items()}, indent=2)[:4000]}
        
        OVERALL INSIGHTS:
        {json.dumps(synthesized_insights, indent=2)[:1500]}
        
        SOURCE CITATION MAP:
        {json.dumps(source_citation_map, indent=2)[:2000]}
        
        CRITICAL REQUIREMENTS:
        1. **MANDATORY INLINE CITATIONS**: Every factual statement, statistic, or claim MUST be immediately followed by an inline citation: [Source Title](URL)
        2. **NO NUMBERED CITATIONS**: DO NOT use numbered citations like [1], [2], [3]. ONLY use inline format: [Title](URL)
        3. **Markdown Format**: Use proper markdown headers, lists, emphasis
        4. **{user_depth.title()} Level**: Write for {user_depth} audience with {depth_config.get('explanation_style', 'appropriate')} style
        5. **Comprehensive Coverage**: Address all major aspects found in the research
        6. **Evidence-Backed**: Every key point must have source attribution with FULL URLs
        
        REPORT STRUCTURE:
        
        # {user_topic}
        
        ## Executive Summary
        [Brief overview with key findings - include citations]
        
        ## Introduction
        [Context and scope - include citations for background facts]
        
        ## Key Findings
        [Main discoveries from research - heavily cited]
        
        ## Detailed Analysis
        [In-depth examination of each major aspect - every claim cited]
        
        ## Insights and Implications
        [Cross-cutting insights - cite supporting evidence]
        
        ## Conclusion
        [Summary and key takeaways - cite main sources]
        
        ## Sources
        [List all sources used with full URLs]
        
        CITATION FORMAT EXAMPLES:
        - "BERT uses bidirectional training unlike GPT's unidirectional approach [Understanding BERT Architecture](https://example.com/bert-guide)."
        - "The transformer architecture has 12 layers in the base model [BERT Technical Paper](https://arxiv.org/paper123)."
        - "Performance on GLUE benchmark reached 80.5% accuracy [BERT Performance Analysis](https://research.com/bert-glue)."
        
        WRITING GUIDELINES FOR {user_depth.upper()} LEVEL:
        - Use {depth_config.get('technical_terms', 'appropriate technical language')}
        - Provide {depth_config.get('examples', 'relevant examples')}
        - Structure with {depth_config.get('structure', 'clear organization')}
        - Focus on {depth_config.get('focus', 'comprehensive understanding')}
        
        Generate a complete, professional research report with comprehensive inline citations.
        """

        try:
            response = self.model.generate_content(
                report_prompt,
                generation_config=self.generation_config
            )

            return response.text.strip()

        except Exception as e:
            print(f"AI report generation error: {e}")
            raise

    def _build_source_citation_map(self, sub_question_answers: Dict) -> Dict:
        """Build a map of sources for citation generation"""

        citation_map = {}
        citation_index = 1

        for question, answer_data in sub_question_answers.items():
            source_urls = answer_data.get('source_urls', [])

            for url in source_urls:
                if url not in citation_map:
                    # Try to get source title from the answer data
                    source_title = self._extract_source_title(url, answer_data)

                    citation_map[url] = {
                        'index': citation_index,
                        'title': source_title,
                        'url': url,
                        'question_context': question
                    }
                    citation_index += 1

        return citation_map

    def _extract_source_title(self, url: str, answer_data: Dict) -> str:
        """Extract or generate appropriate source title for citations"""

        # Try to get title from key points that reference this URL
        key_points = answer_data.get('key_points', [])

        for point in key_points:
            supporting_sources = point.get('supporting_sources', [])
            if url in supporting_sources:
                # Generate title based on the content
                return self._generate_source_title_from_url(url)

        return self._generate_source_title_from_url(url)

    def _generate_source_title_from_url(self, url: str) -> str:
        """Generate readable source title from URL"""

        if not url:
            return "Source"

        try:
            # Extract domain for title
            domain = url.split('/')[2].replace('www.', '')

            # Common domain mappings
            domain_titles = {
                'arxiv.org': 'ArXiv Research Paper',
                'github.com': 'GitHub Repository',
                'stackoverflow.com': 'Stack Overflow Discussion',
                'medium.com': 'Medium Article',
                'towardsdatascience.com': 'Towards Data Science',
                'pytorch.org': 'PyTorch Documentation',
                'tensorflow.org': 'TensorFlow Documentation',
                'wikipedia.org': 'Wikipedia',
                'nature.com': 'Nature Journal',
                'sciencedirect.com': 'ScienceDirect Paper'
            }

            # Check if domain has a known mapping
            for known_domain, title in domain_titles.items():
                if known_domain in domain:
                    return title

            # Default: Capitalize domain name
            return domain.replace('.com', '').replace('.org', '').replace('.edu', '').title()

        except:
            return "Source"

    def _generate_json_output(self, user_topic: str, sub_question_answers: Dict,
                            synthesized_insights: Dict, source_citation_map: Dict) -> Dict:
        """Generate structured JSON output from research data"""

        findings = []
        sources = []

        # Extract findings from sub-question answers
        for question, answer_data in sub_question_answers.items():
            key_points = answer_data.get('key_points', [])
            source_urls = answer_data.get('source_urls', [])

            for point in key_points:
                finding = {
                    "category": "Finding",
                    "title": point.get('point', question)[:100],
                    "impact": point.get('impact', 'Medium'),
                    "timeline": "Current",
                    "confidence": "Medium",
                    "evidence": source_urls[:3],  # Max 3 sources per finding
                    "context": question
                }
                findings.append(finding)

        # Extract sources
        for url, data in source_citation_map.items():
            source = {
                "url": url,
                "title": data['title'],
                "reliability_score": 0.8,
                "date_accessed": datetime.now().strftime('%Y-%m-%d')
            }
            sources.append(source)

        # Build complete JSON structure
        json_output = {
            "metadata": {
                "topic": user_topic,
                "generated_at": datetime.now().isoformat(),
                "confidence_level": "medium"
            },
            "executive_summary": {
                "key_points": list(synthesized_insights.get('key_insights', []))[:5],
                "overall_assessment": synthesized_insights.get('conclusion', 'Research completed successfully')
            },
            "findings": findings[:10],  # Max 10 findings
            "sources": sources
        }

        return json_output

    def _fix_numbered_citations(self, report: str, source_citation_map: Dict) -> str:
        """Fix numbered citations like [1], [2] by converting to inline format"""

        if not source_citation_map:
            return report

        # Create a list of sources in order
        sources_list = []
        for url, data in source_citation_map.items():
            sources_list.append((data['index'], data['title'], url))

        # Sort by index
        sources_list.sort(key=lambda x: x[0])

        # Replace numbered citations
        fixed_report = report

        # Find patterns like [1], [2], [1, 3], [7, 9], etc.
        numbered_pattern = r'\[(\d+(?:\s*,\s*\d+)*)\]'

        def replace_numbered_citation(match):
            numbers_str = match.group(1)
            numbers = [int(n.strip()) for n in numbers_str.split(',')]

            # Convert numbers to inline citations
            citations = []
            for num in numbers:
                # Find the source with this index
                for index, title, url in sources_list:
                    if index == num:
                        citations.append(f"[{title}]({url})")
                        break

            if citations:
                return ' '.join(citations)
            else:
                return match.group(0)  # Keep original if no match found

        fixed_report = re.sub(numbered_pattern, replace_numbered_citation, fixed_report)

        # Also clean up any remaining Sources section with numbered format
        # Remove lines like "* [1] Title - URL" from Sources section
        fixed_report = re.sub(r'\n\s*\*\s*\[\d+\][^\n]*', '', fixed_report)

        return fixed_report

    def _validate_and_format_report(self, markdown_report: str, source_citation_map: Dict) -> str:
        """Validate citations and format the report"""

        # First, fix any numbered citations that slipped through
        fixed_report = self._fix_numbered_citations(markdown_report, source_citation_map)

        # Count citations
        citation_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        citations = re.findall(citation_pattern, fixed_report)

        print(f"🔍 Found {len(citations)} citations in report")

        # Validate URLs in citations
        validated_report = self._validate_citation_urls(fixed_report)

        # Ensure proper markdown formatting
        formatted_report = self._ensure_markdown_formatting(validated_report)

        # Add metadata header
        final_report = self._add_report_header(formatted_report)

        return final_report

    def _validate_citation_urls(self, report: str) -> str:
        """Validate that citation URLs are properly formatted"""

        # Find all citations
        citation_pattern = r'\[([^\]]+)\]\(([^)]+)\)'

        def fix_citation(match):
            title = match.group(1).strip()
            url = match.group(2).strip()

            # Ensure URL is properly formatted
            if not url.startswith(('http://', 'https://')):
                if url.startswith('www.'):
                    url = f"https://{url}"
                elif '.' in url:
                    url = f"https://{url}"

            return f"[{title}]({url})"

        validated_report = re.sub(citation_pattern, fix_citation, report)

        return validated_report

    def _ensure_markdown_formatting(self, report: str) -> str:
        """Ensure proper markdown formatting"""

        # Fix common formatting issues
        formatted = report

        # Ensure headers have proper spacing
        formatted = re.sub(r'\n(#{1,6})', r'\n\n\1', formatted)
        formatted = re.sub(r'(#{1,6}.*?)\n([^\n#])', r'\1\n\n\2', formatted)

        # Ensure lists have proper spacing
        formatted = re.sub(r'\n(\s*[-*+])', r'\n\n\1', formatted)

        # Clean up multiple newlines
        formatted = re.sub(r'\n{3,}', '\n\n', formatted)

        return formatted.strip()

    def _add_report_header(self, report: str) -> str:
        """Add metadata header to the report"""

        header = f"""---
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Generator: Project Galileo AI Research Agent
Format: Evidence-Backed Research Report
---

"""

        return header + report

    def _generate_report_metadata(self, research_context: Dict, user_depth: str,
                                  report: str) -> Dict:
        """Generate comprehensive metadata for the report"""

        # Count various elements
        word_count = len(report.split())
        citation_count = len(re.findall(r'\[([^\]]+)\]\(([^)]+)\)', report))
        section_count = len(re.findall(r'^#+', report, re.MULTILINE))

        # Get source statistics
        analysis_results = research_context.get('analysis_results', {})
        total_sources = analysis_results.get('metadata', {}).get('total_sources_analyzed', 0)

        return {
            'generation_timestamp': datetime.now().isoformat(),
            'user_topic': research_context.get('user_topic', ''),
            'user_depth': user_depth,
            'word_count': word_count,
            'citation_count': citation_count,
            'section_count': section_count,
            'sources_analyzed': total_sources,
            'report_quality_score': min(citation_count * 0.1, 1.0),  # Simple quality metric
            'sub_questions_covered': len(analysis_results.get('sub_question_answers', {}))
        }

    def _generate_fallback_report(self, research_context: Dict, user_depth: str) -> Dict:
        """Generate fallback report when main generation fails"""

        user_topic = research_context.get('user_topic', 'Research Topic')

        fallback_report = f"""---
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Generator: Project Galileo AI Research Agent (Fallback Mode)
Format: Basic Research Report
---

# {user_topic}

## Report Generation Notice

This report was generated in fallback mode due to technical issues with the main report generation process.

## Available Research Data

The research process was completed with the following components:

- **Topic**: {user_topic}
- **User Level**: {user_depth}
- **Sub-questions**: {len(research_context.get('analysis_results', {}).get('sub_question_answers', {}))} questions analyzed

## Research Summary

Based on the completed research process, information was gathered from multiple internet sources and analyzed. However, due to processing limitations, the full evidence-backed report could not be generated.

## Recommendations

For a complete analysis, please:

1. Check the saved research context files
2. Review the individual source analyses
3. Re-run the report generation process

## Technical Details

- Generation attempt timestamp: {datetime.now().isoformat()}
- Fallback mode triggered
- Research data available in context files
"""

        return {
            'markdown_report': fallback_report,
            'metadata': {
                'generation_timestamp': datetime.now().isoformat(),
                'user_topic': user_topic,
                'user_depth': user_depth,
                'fallback_mode': True,
                'word_count': len(fallback_report.split()),
                'citation_count': 0
            },
            'user_depth': user_depth,
            'fallback_mode': True
        }

    def save_report_to_file(self, report_data: Dict, filename: str = None) -> str:
        """Save both markdown and JSON reports to files"""

        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            topic_clean = re.sub(r'[^\w\s-]', '', report_data['metadata']['user_topic'])
            topic_clean = re.sub(r'[-\s]+', '_', topic_clean)[:30]
            filename = f"research_report_{topic_clean}_{timestamp}.md"

        # Generate JSON filename
        json_filename = filename.replace('.md', '.json')

        try:
            # Save markdown file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report_data['markdown_report'])

            # Save JSON file if available
            if 'json_output' in report_data:
                import json
                with open(json_filename, 'w', encoding='utf-8') as f:
                    json.dump(report_data['json_output'], f, indent=2, ensure_ascii=False)

            print(f"💾 Report saved to: {filename}")
            print(f"💾 JSON saved to: {json_filename}")
            return filename

        except Exception as e:
            print(f"❌ Failed to save report: {e}")
            return ""

    def get_writer_stats(self) -> Dict:
        """Get writer statistics and capabilities"""
        return {
            'model': 'gemini-2.5-flash',
            'max_output_tokens': 6000,
            'features': [
                'evidence_backed_citations',
                'markdown_formatting',
                'depth_aware_writing',
                'comprehensive_coverage',
                'source_attribution'
            ],
            'citation_formats': ['inline_markdown'],
            'supported_depths': ['beginner', 'intermediate', 'expert']
        }
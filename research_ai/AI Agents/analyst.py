import google.generativeai as genai
from typing import List, Dict, Any, Tuple
import json
import re
from config import Config
from collections import defaultdict
import hashlib

class InformationAnalyst:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.5-flash")

        # Analysis configuration
        self.generation_config = genai.types.GenerationConfig(
            temperature=0.2,  # Lower temperature for more consistent analysis
            top_p=0.8,
            top_k=40,
            max_output_tokens=4000,
            candidate_count=1
        )

        # Quality thresholds
        self.quality_thresholds = {
            'min_content_length': 100,
            'min_relevance_score': 0.3,
            'max_sources_per_answer': 10
        }

    def analyze_and_synthesize(self, sources_data: Dict, user_depth: str) -> Dict:
        """
        Main analysis function: extract information and synthesize from multiple sources
        Returns structured analysis with source attribution for every piece of information
        """

        print(f"\n🔬 ANALYST: Starting information extraction and synthesis...")
        print(f"🎚️  Analysis depth: {user_depth}")

        analysis_results = {
            'sub_question_answers': {},
            'synthesized_insights': {},
            'source_quality_analysis': {},
            'cross_source_validation': {},
            'information_gaps': {},
            'metadata': {
                'user_depth': user_depth,
                'total_sources_analyzed': 0,
                'high_quality_sources': 0,
                'analysis_timestamp': None
            }
        }

        total_sources = 0

        # Process each sub-question
        for sub_question, sources in sources_data.items():
            if not sources:
                continue

            print(f"\n📍 Analyzing: {sub_question[:60]}...")

            try:
                # Step 1: Filter and assess source quality
                quality_sources = self._assess_source_quality(sources, sub_question)

                # Step 2: Extract key information from each source
                source_extractions = self._extract_information_from_sources(
                    quality_sources, sub_question, user_depth
                )

                # Step 3: Synthesize information across sources
                synthesized_answer = self._synthesize_cross_source_information(
                    source_extractions, sub_question, user_depth
                )

                # Step 4: Validate information consistency
                validation_results = self._validate_cross_source_consistency(
                    source_extractions, sub_question
                )

                # Store results with full source attribution
                analysis_results['sub_question_answers'][sub_question] = synthesized_answer
                analysis_results['source_quality_analysis'][sub_question] = {
                    'total_sources': len(sources),
                    'quality_sources': len(quality_sources),
                    'quality_breakdown': self._get_quality_breakdown(quality_sources)
                }
                analysis_results['cross_source_validation'][sub_question] = validation_results

                total_sources += len(sources)

                print(f"   ✅ Extracted from {len(quality_sources)}/{len(sources)} quality sources")
                print(f"   📊 Synthesis confidence: {synthesized_answer.get('confidence_score', 0):.2f}")

            except Exception as e:
                print(f"   ❌ Analysis error: {e}")
                analysis_results['sub_question_answers'][sub_question] = {
                    'answer': f"Analysis failed for this question: {str(e)}",
                    'source_urls': [],
                    'confidence_score': 0.0,
                    'error': str(e)
                }

        # Generate overall insights
        analysis_results['synthesized_insights'] = self._generate_overall_insights(
            analysis_results['sub_question_answers'], user_depth
        )

        # Identify information gaps
        analysis_results['information_gaps'] = self._identify_information_gaps(
            analysis_results['sub_question_answers']
        )

        # Update metadata
        analysis_results['metadata']['total_sources_analyzed'] = total_sources
        analysis_results['metadata']['high_quality_sources'] = sum(
            analysis_results['source_quality_analysis'][q]['quality_sources']
            for q in analysis_results['source_quality_analysis']
        )

        print(f"\n🔬 Analysis completed!")
        print(f"📊 Total sources analyzed: {total_sources}")
        print(f"🎯 High-quality sources: {analysis_results['metadata']['high_quality_sources']}")

        return analysis_results

    def _assess_source_quality(self, sources: List[Dict], sub_question: str) -> List[Dict]:
        """Assess and filter sources based on quality indicators"""

        quality_sources = []

        for source in sources:
            # Quality indicators
            content_length = len(source.get('extracted_content', ''))
            relevance_score = source.get('relevance_score', 0)
            extraction_success = source.get('extraction_success', False)

            # Calculate quality score
            quality_score = 0.0

            # Content length score (0-0.3)
            if content_length >= 800:
                quality_score += 0.3
            elif content_length >= 400:
                quality_score += 0.2
            elif content_length >= self.quality_thresholds['min_content_length']:
                quality_score += 0.1

            # Relevance score (0-0.4)
            quality_score += min(relevance_score * 0.4, 0.4)

            # Extraction success (0-0.2)
            if extraction_success:
                quality_score += 0.2

            # URL quality indicators (0-0.1)
            url = source.get('url', '').lower()
            if any(domain in url for domain in ['edu', 'org', 'gov']):
                quality_score += 0.05
            if 'https' in url:
                quality_score += 0.05

            source['quality_score'] = quality_score

            # Filter based on minimum thresholds
            if (content_length >= self.quality_thresholds['min_content_length'] and
                    relevance_score >= self.quality_thresholds['min_relevance_score']):
                quality_sources.append(source)

        # Sort by quality score and take top sources
        quality_sources.sort(key=lambda x: x['quality_score'], reverse=True)
        return quality_sources[:self.quality_thresholds['max_sources_per_answer']]

    def _extract_information_from_sources(self, sources: List[Dict], sub_question: str,
                                          user_depth: str) -> List[Dict]:
        """Extract key information from each source with source attribution"""

        extractions = []

        for source in sources:
            try:
                content = source.get('extracted_content', '')
                if len(content) < 50:  # Skip very short content
                    continue

                # Extract information using AI
                extraction_result = self._ai_extract_information(
                    content, sub_question, source, user_depth
                )

                if extraction_result and extraction_result.get('key_information'):
                    extractions.append(extraction_result)

            except Exception as e:
                print(f"   ⚠️  Extraction failed for {source.get('url', 'unknown')}: {e}")

        return extractions

    def _ai_extract_information(self, content: str, sub_question: str,
                                source: Dict, user_depth: str) -> Dict:
        """Use AI to extract key information from source content"""

        extraction_prompt = f"""
        TASK: Extract key information from this content to answer the sub-question.
        
        SUB-QUESTION: "{sub_question}"
        USER LEVEL: {user_depth}
        SOURCE URL: {source.get('url', 'unknown')}
        
        CONTENT TO ANALYZE:
        {content[:2000]}  # Limit content length for processing
        
        Extract specific, factual information that directly answers or relates to the sub-question.
        Focus on {user_depth}-level information.
        
        Return as JSON:
        {{
            "key_information": [
                {{
                    "fact": "specific factual statement",
                    "relevance_to_question": "how this fact answers the sub-question",
                    "confidence": 0.9,
                    "context": "brief context around this fact"
                }},
                {{
                    "fact": "another specific factual statement", 
                    "relevance_to_question": "how this relates to the question",
                    "confidence": 0.8,
                    "context": "context for this fact"
                }}
            ],
            "main_points": [
                "key point 1 from this source",
                "key point 2 from this source"
            ],
            "source_authority": {{
                "appears_authoritative": true/false,
                "reasoning": "why this source seems reliable or not",
                "date_indicators": "any date/recency indicators found"
            }}
        }}
        
        Only extract information that is:
        1. Factual and specific
        2. Directly relevant to the sub-question
        3. Appropriate for {user_depth} level understanding
        """

        try:
            response = self.model.generate_content(
                extraction_prompt,
                generation_config=self.generation_config
            )

            cleaned_response = self._clean_json_response(response.text)
            extraction_data = json.loads(cleaned_response)

            # Add source metadata to each extracted fact
            if 'key_information' in extraction_data:
                for fact in extraction_data['key_information']:
                    fact['source_url'] = source.get('url')
                    fact['source_title'] = source.get('title')
                    fact['extraction_timestamp'] = source.get('search_position', 0)

            # Add source metadata
            extraction_data['source_metadata'] = {
                'url': source.get('url'),
                'title': source.get('title'),
                'domain': source.get('url', '').split('/')[2] if source.get('url') else '',
                'quality_score': source.get('quality_score', 0),
                'relevance_score': source.get('relevance_score', 0),
                'content_length': len(source.get('extracted_content', ''))
            }

            return extraction_data

        except Exception as e:
            print(f"AI extraction error: {e}")
            return {}

    def _synthesize_cross_source_information(self, extractions: List[Dict],
                                             sub_question: str, user_depth: str) -> Dict:
        """Synthesize information from multiple sources into a comprehensive answer"""

        if not extractions:
            return {
                'answer': f"No sufficient information found to answer: {sub_question}",
                'source_urls': [],
                'confidence_score': 0.0
            }

        # Prepare synthesis data
        all_facts = []
        all_sources = []

        for extraction in extractions:
            if 'key_information' in extraction:
                all_facts.extend(extraction['key_information'])

            if 'source_metadata' in extraction:
                all_sources.append(extraction['source_metadata'])

        synthesis_prompt = f"""
        TASK: Synthesize information from multiple sources to answer the sub-question comprehensively.
        
        SUB-QUESTION: "{sub_question}"
        USER LEVEL: {user_depth}
        
        EXTRACTED FACTS FROM SOURCES:
        {json.dumps(all_facts, indent=2)[:3000]}  # Limit for processing
        
        SOURCES ANALYZED: {len(all_sources)} sources
        
        Create a comprehensive answer by:
        1. Combining complementary information from different sources
        2. Identifying the most reliable facts (highest confidence)
        3. Resolving any contradictions between sources
        4. Structuring for {user_depth} level understanding
        
        Return as JSON:
        {{
            "synthesized_answer": "comprehensive answer combining multiple sources",
            "key_points": [
                {{
                    "point": "main point 1",
                    "supporting_sources": ["url1", "url2"],
                    "confidence": 0.9
                }},
                {{
                    "point": "main point 2", 
                    "supporting_sources": ["url2", "url3"],
                    "confidence": 0.8
                }}
            ],
            "source_consensus": {{
                "high_agreement": ["fact most sources agree on"],
                "some_disagreement": ["fact with mixed evidence"],
                "unique_insights": ["fact from only one high-quality source"]
            }},
            "overall_confidence": 0.85,
            "information_completeness": 0.8
        }}
        """

        try:
            response = self.model.generate_content(
                synthesis_prompt,
                generation_config=self.generation_config
            )

            cleaned_response = self._clean_json_response(response.text)
            synthesis_result = json.loads(cleaned_response)

            # Add source URLs to the result
            source_urls = [source['url'] for source in all_sources if source.get('url')]

            return {
                'answer': synthesis_result.get('synthesized_answer', ''),
                'key_points': synthesis_result.get('key_points', []),
                'source_consensus': synthesis_result.get('source_consensus', {}),
                'source_urls': source_urls,
                'confidence_score': synthesis_result.get('overall_confidence', 0.0),
                'completeness_score': synthesis_result.get('information_completeness', 0.0),
                'sources_count': len(all_sources)
            }

        except Exception as e:
            print(f"Synthesis error: {e}")
            # Fallback synthesis
            return self._fallback_synthesis(all_facts, all_sources, sub_question)

    def _validate_cross_source_consistency(self, extractions: List[Dict],
                                           sub_question: str) -> Dict:
        """Validate consistency of information across sources"""

        if len(extractions) < 2:
            return {'validation': 'insufficient_sources', 'consistency_score': 0.5}

        # Group similar facts
        fact_groups = self._group_similar_facts(extractions)

        validation_result = {
            'consistency_score': 0.0,
            'contradictions': [],
            'consensus_facts': [],
            'unique_facts': []
        }

        total_fact_groups = len(fact_groups)
        consistent_groups = 0

        for group in fact_groups:
            if len(group) > 1:  # Multiple sources support this fact
                consistent_groups += 1
                validation_result['consensus_facts'].append({
                    'fact': group[0]['fact'],
                    'source_count': len(group),
                    'average_confidence': sum(f['confidence'] for f in group) / len(group)
                })
            else:  # Only one source for this fact
                validation_result['unique_facts'].append(group[0])

        # Calculate consistency score
        if total_fact_groups > 0:
            validation_result['consistency_score'] = consistent_groups / total_fact_groups

        return validation_result

    def _group_similar_facts(self, extractions: List[Dict]) -> List[List[Dict]]:
        """Group similar facts from different sources"""

        all_facts = []
        for extraction in extractions:
            if isinstance(extraction, dict) and 'key_information' in extraction:
                key_info = extraction['key_information']
                if isinstance(key_info, list):
                    all_facts.extend(key_info)

        # Simple similarity grouping based on keywords
        fact_groups = []
        used_facts = set()

        for i, fact in enumerate(all_facts):
            if i in used_facts:
                continue

            similar_group = [fact]
            fact_keywords = set(fact['fact'].lower().split())

            for j, other_fact in enumerate(all_facts[i+1:], i+1):
                if j in used_facts:
                    continue

                other_keywords = set(other_fact['fact'].lower().split())
                overlap = len(fact_keywords.intersection(other_keywords))

                if overlap >= min(3, len(fact_keywords) * 0.4):  # Similarity threshold
                    similar_group.append(other_fact)
                    used_facts.add(j)

            fact_groups.append(similar_group)
            used_facts.add(i)

        return fact_groups

    def _generate_overall_insights(self, sub_question_answers: Dict, user_depth: str) -> Dict:
        """Generate overall insights by connecting information across sub-questions"""

        insights_prompt = f"""
        TASK: Generate overall insights by connecting information across all sub-questions.
        
        USER LEVEL: {user_depth}
        
        SUB-QUESTION ANSWERS:
        {json.dumps({q: a.get('answer', '') for q, a in sub_question_answers.items()}, indent=2)[:3000]}
        
        Identify:
        1. Common themes across sub-questions
        2. Connections between different aspects
        3. Overarching insights for {user_depth} level
        
        Return as JSON:
        {{
            "key_insights": [
                "insight 1 connecting multiple sub-questions",
                "insight 2 about overall patterns"
            ],
            "thematic_connections": {{
                "theme_1": ["sub-question 1", "sub-question 3"],
                "theme_2": ["sub-question 2", "sub-question 4"]
            }},
            "knowledge_synthesis": "high-level synthesis for {user_depth} audience"
        }}
        """

        try:
            response = self.model.generate_content(insights_prompt, generation_config=self.generation_config)
            cleaned_response = self._clean_json_response(response.text)
            return json.loads(cleaned_response)
        except:
            return {"key_insights": ["Analysis completed across multiple sources"], "knowledge_synthesis": "Information synthesized from multiple sources"}

    def _identify_information_gaps(self, sub_question_answers: Dict) -> Dict:
        """Identify gaps in information coverage"""

        gaps = {
            'low_confidence_areas': [],
            'incomplete_answers': [],
            'missing_perspectives': []
        }

        for question, answer_data in sub_question_answers.items():
            confidence = answer_data.get('confidence_score', 0)
            completeness = answer_data.get('completeness_score', 0)

            if confidence < 0.6:
                gaps['low_confidence_areas'].append(question)

            if completeness < 0.7:
                gaps['incomplete_answers'].append(question)

        return gaps

    def _get_quality_breakdown(self, sources: List[Dict]) -> Dict:
        """Get breakdown of source quality"""

        if not sources:
            return {}

        quality_scores = [s.get('quality_score', 0) for s in sources]

        return {
            'average_quality': sum(quality_scores) / len(quality_scores),
            'high_quality_count': len([s for s in quality_scores if s >= 0.7]),
            'medium_quality_count': len([s for s in quality_scores if 0.4 <= s < 0.7]),
            'low_quality_count': len([s for s in quality_scores if s < 0.4])
        }

    def _fallback_synthesis(self, all_facts: List[Dict], all_sources: List[Dict],
                            sub_question: str) -> Dict:
        """Fallback synthesis when AI fails"""

        if not all_facts:
            return {
                'answer': f"Unable to find sufficient information for: {sub_question}",
                'source_urls': [],
                'confidence_score': 0.0
            }

        # Simple concatenation of high-confidence facts
        high_conf_facts = [f for f in all_facts if f.get('confidence', 0) >= 0.7]

        if high_conf_facts:
            answer = ". ".join([f['fact'] for f in high_conf_facts[:3]])
        else:
            answer = ". ".join([f['fact'] for f in all_facts[:3]])

        source_urls = [s['url'] for s in all_sources if s.get('url')]

        return {
            'answer': answer,
            'source_urls': source_urls,
            'confidence_score': 0.6,
            'sources_count': len(all_sources)
        }

    def _clean_json_response(self, response_text: str) -> str:
        """Clean JSON response from Gemini"""
        try:
            cleaned = re.sub(r'```json\s*', '', response_text)
            cleaned = re.sub(r'```\s*$', '', cleaned)

            json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if json_match:
                return json_match.group(0)

            return cleaned.strip()
        except:
            return response_text

    def get_analyst_stats(self) -> Dict:
        """Get analyst statistics"""
        return {
            'model': 'gemini-2.5-flash',
            'quality_thresholds': self.quality_thresholds,
            'features': [
                'cross_source_synthesis',
                'source_attribution',
                'quality_assessment',
                'consistency_validation',
                'gap_identification'
            ]
        }
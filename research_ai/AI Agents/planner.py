import google.generativeai as genai
from typing import List, Dict, Any
import json
import re
from config import Config

class QueryPlanner:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)

        # Updated for Gemini 2.5 Flash
        self.model = genai.GenerativeModel("gemini-2.5-flash")

        # Generation configuration for unlimited coverage
        self.generation_config = genai.types.GenerationConfig(
            temperature=0.4,
            top_p=0.9,
            top_k=50,
            max_output_tokens=4000,  # Increased for more sub-questions
            candidate_count=1
        )

        # Depth-based question limits (no upper limit for complete coverage)
        self.depth_configs = {
            'beginner': {
                'min_questions': 3,
                'target_questions': 4,
                'max_questions': 5,
                'focus': 'basic understanding and fundamentals'
            },
            'intermediate': {
                'min_questions': 4,
                'target_questions': 6,
                'max_questions': 8,
                'focus': 'detailed analysis and practical applications'
            },
            'expert': {
                'min_questions': 6,
                'target_questions': 8,
                'max_questions': 10,  # No real limit for complete coverage
                'focus': 'comprehensive deep-dive with technical depth'
            }
        }

    def decompose_query(self, query: str, user_depth: str) -> List[str]:
        """
        Decompose query into focused, web-searchable sub-questions
        Optimized for speed and search quality
        """

        print(f"🧠 Planner analyzing for {user_depth} level coverage...")

        # Get depth configuration
        depth_config = self.depth_configs.get(user_depth, self.depth_configs['intermediate'])

        try:
            # Generate focused sub-questions directly
            sub_questions = self._generate_focused_questions(query, user_depth, depth_config)

            # Quick validation and cleanup
            final_questions = self._validate_and_finalize_questions(sub_questions, depth_config)

            print(f"✅ Generated {len(final_questions)} focused sub-questions for {user_depth} level")

            return final_questions

        except Exception as e:
            print(f"❌ Planner error: {e}")
            return self._fallback_focused_decomposition(query, user_depth)

    def _generate_focused_questions(self, query: str, user_depth: str, depth_config: Dict) -> List[str]:
        """Generate focused, web-searchable sub-questions"""

        focused_prompt = f"""
        QUERY: "{query}"
        USER LEVEL: {user_depth}
        TARGET: {depth_config['target_questions']} focused questions

        Create {depth_config['target_questions']} FOCUSED, web-searchable sub-questions that cover the most important aspects of "{query}".

        Requirements:
        - Each question should be SHORT and SPECIFIC for web search
        - Questions should be complete sentences that can be searched directly
        - Cover key aspects: definition, how it works, applications, benefits, challenges
        - Appropriate for {user_depth} level

        Examples of GOOD questions:
        - "What is machine learning definition and types"
        - "How does machine learning work step by step"
        - "Machine learning applications in business 2024"
        - "Benefits and advantages of machine learning"
        - "Challenges and limitations of machine learning"

        Examples of BAD questions (too long/vague):
        - "Machine learning comprehensive analysis including all technical implementation details and business use cases across industries with future trends"

        Return ONLY a JSON array of questions:
        [
            "focused question 1",
            "focused question 2",
            "focused question 3"
        ]
        """

        try:
            response = self.model.generate_content(
                focused_prompt,
                generation_config=self.generation_config
            )

            cleaned_response = self._clean_json_response(response.text)
            # Try to parse as array first
            if cleaned_response.strip().startswith('['):
                return json.loads(cleaned_response)
            else:
                # Parse as object and extract sub_questions
                result = json.loads(cleaned_response)
                return result.get("sub_questions", result.get("questions", []))

        except Exception as e:
            print(f"Focused generation error: {e}")
            raise

    def _analyze_coverage_completeness(self, query: str, sub_questions: List[str], user_depth: str) -> Dict:
        """Analyze if sub-questions provide complete coverage"""

        coverage_prompt = f"""
        ORIGINAL QUERY: "{query}"
        USER LEVEL: {user_depth}
        GENERATED SUB-QUESTIONS: {json.dumps(sub_questions, indent=2)}
        
        Analyze if these sub-questions provide COMPLETE coverage for a {user_depth} level understanding.
        
        Check coverage of:
        1. Core concepts and definitions
        2. Technical mechanisms  
        3. Applications and use cases
        4. Advantages and limitations
        5. Comparisons and alternatives
        6. Current developments
        7. Implementation aspects
        8. Industry significance
        
        Return as JSON:
        {{
            "is_complete": true/false,
            "coverage_score": 0.85,
            "covered_aspects": [
                "aspect 1 well covered",
                "aspect 2 covered"
            ],
            "missing_aspects": [
                "missing aspect 1",
                "missing aspect 2"
            ],
            "recommendations": [
                "add questions about X",
                "need more coverage of Y"
            ]
        }}
        """

        try:
            response = self.model.generate_content(
                coverage_prompt,
                generation_config=self.generation_config
            )

            cleaned_response = self._clean_json_response(response.text)
            return json.loads(cleaned_response)

        except Exception as e:
            print(f"Coverage analysis error: {e}")
            # Assume incomplete coverage to be safe
            return {
                "is_complete": False,
                "coverage_score": 0.5,
                "missing_aspects": ["technical details", "applications", "comparisons"]
            }

    def _generate_missing_coverage_questions(self, query: str, existing_questions: List[str],
                                             missing_aspects: List[str], user_depth: str) -> List[str]:
        """Generate additional questions to cover missing aspects"""

        missing_prompt = f"""
        ORIGINAL QUERY: "{query}"
        USER LEVEL: {user_depth}
        EXISTING QUESTIONS: {json.dumps(existing_questions, indent=2)}
        MISSING COVERAGE: {json.dumps(missing_aspects, indent=2)}
        
        Generate additional specific, searchable sub-questions to cover the missing aspects.
        Focus only on the gaps in coverage.
        
        Return as JSON:
        {{
            "additional_questions": [
                "specific question for missing aspect 1",
                "specific question for missing aspect 2",
                "..."
            ]
        }}
        """

        try:
            response = self.model.generate_content(
                missing_prompt,
                generation_config=self.generation_config
            )

            cleaned_response = self._clean_json_response(response.text)
            result = json.loads(cleaned_response)

            return result.get("additional_questions", [])

        except Exception as e:
            print(f"Missing coverage generation error: {e}")
            return []

    def _validate_and_finalize_questions(self, sub_questions: List[str], depth_config: Dict) -> List[str]:
        """Validate and finalize the sub-questions list"""

        # Remove duplicates while preserving order
        unique_questions = []
        seen = set()

        for question in sub_questions:
            question_clean = question.lower().strip()
            if question_clean not in seen and len(question.strip()) > 10:
                seen.add(question_clean)
                unique_questions.append(question.strip())

        # Ensure minimum questions met
        if len(unique_questions) < depth_config['min_questions']:
            print(f"⚠️  Only {len(unique_questions)} questions generated, minimum is {depth_config['min_questions']}")

        # Log if we exceed target (which is fine for complete coverage)
        if len(unique_questions) > depth_config['target_questions']:
            print(f"📈 Generated {len(unique_questions)} questions (target: {depth_config['target_questions']}) for complete coverage")

        return unique_questions

    def _clean_json_response(self, response_text: str) -> str:
        """Clean and extract JSON from Gemini 2.5 Flash response"""
        try:
            # Remove markdown code blocks
            cleaned = re.sub(r'```json\s*', '', response_text)
            cleaned = re.sub(r'```\s*$', '', cleaned)

            # Find JSON content
            json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if json_match:
                return json_match.group(0)

            # If no braces found, try to extract from text
            lines = cleaned.split('\n')
            json_lines = []
            in_json = False

            for line in lines:
                if '{' in line:
                    in_json = True
                if in_json:
                    json_lines.append(line)
                if '}' in line and in_json:
                    break

            return '\n'.join(json_lines) if json_lines else cleaned.strip()

        except Exception as e:
            print(f"JSON cleaning error: {e}")
            return response_text

    def _fallback_focused_decomposition(self, query: str, user_depth: str) -> List[str]:
        """Fallback focused decomposition when AI fails"""

        depth_config = self.depth_configs.get(user_depth, self.depth_configs['intermediate'])

        # Simple focused questions
        base_questions = [
            f"What is {query} definition and overview",
            f"How does {query} work",
            f"{query} applications and examples",
            f"Benefits and advantages of {query}",
            f"Challenges and limitations of {query}"
        ]

        # Add depth-specific questions
        if user_depth == 'expert':
            base_questions.extend([
                f"{query} technical implementation details",
                f"{query} research and latest developments"
            ])
        elif user_depth == 'intermediate':
            base_questions.extend([
                f"{query} best practices and guidelines"
            ])

        # Return appropriate number based on depth
        target_count = depth_config['target_questions']
        return base_questions[:target_count]

    def get_planner_stats(self) -> Dict:
        """Get planner statistics"""
        return {
            'model': 'gemini-2.5-flash',
            'depth_configs': self.depth_configs,
            'max_output_tokens': 4000,
            'supports_unlimited_coverage': True
        }
import requests
import json
from typing import List, Dict, Any
import time
import urllib.parse
from bs4 import BeautifulSoup
import concurrent.futures
from threading import Lock
import re

class WebScout:
    def __init__(self):
        # Updated Serper API configuration
        self.serper_api_key = "a0b5bb733c99102003d1cb2a7e0c8e1eea9a766c"
        self.serper_url = "https://google.serper.dev/search"

        # Optimized sources per sub-query for speed
        self.min_sources_per_query = 5
        self.target_sources_per_query = 7
        self.max_search_results = 10

        # Optimized depth configurations for faster processing
        self.depth_configs = {
            'beginner': {
                'sources_per_query': 5,
                'content_length': 600,  # Shorter content for speed
                'focus': 'basic explanations and simple examples'
            },
            'intermediate': {
                'sources_per_query': 6,
                'content_length': 800,  # Medium content length
                'focus': 'detailed explanations with examples'
            },
            'expert': {
                'sources_per_query': 7,
                'content_length': 1000,  # Reasonable content length
                'focus': 'comprehensive technical content'
            }
        }

        self.current_depth = 'intermediate'
        self.rate_limit_lock = Lock()

        # Headers for web scraping
        self.scraping_headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def configure_for_depth(self, user_depth: str):
        """Configure scout based on user depth level"""
        self.current_depth = user_depth
        depth_config = self.depth_configs.get(user_depth, self.depth_configs['intermediate'])

        print(f"🎚️  Scout configured for {user_depth} level:")
        print(f"   📊 Target sources per query: {depth_config['sources_per_query']}")
        print(f"   📝 Content extraction length: {depth_config['content_length']} chars")

    def search_all_questions(self, sub_questions: List[str]) -> Dict:
        """Search internet deeply for all sub-questions with 8+ sites each"""

        print(f"\n🌐 Starting DEEP internet extraction for {len(sub_questions)} queries")
        print(f"🎯 Minimum {self.min_sources_per_query} sites per query with content extraction")

        all_sources_data = {}

        for i, question in enumerate(sub_questions, 1):
            print(f"\n📍 [{i}/{len(sub_questions)}] Deep extracting: {question[:60]}...")

            try:
                # Deep search with multiple strategies
                question_sources = self._deep_search_with_extraction(question)

                # Ensure minimum sources requirement
                if len(question_sources) < self.min_sources_per_query:
                    print(f"⚠️  Only {len(question_sources)} sources found, searching deeper...")
                    additional_sources = self._search_deeper(question, len(question_sources))
                    question_sources.extend(additional_sources)

                # Rank by relevancy and take top sources
                depth_config = self.depth_configs[self.current_depth]
                target_count = depth_config['sources_per_query']

                ranked_sources = self._rank_by_pure_relevancy(question, question_sources)
                final_sources = ranked_sources[:target_count]

                all_sources_data[question] = final_sources

                print(f"   ✅ Extracted {len(final_sources)} sites with content")

                # Show top results
                for j, source in enumerate(final_sources[:3], 1):
                    title = source.get('title', 'No title')[:40]
                    score = source.get('relevance_score', 0)
                    content_length = len(source.get('extracted_content', ''))
                    print(f"   {j}. {title}... (⭐{score:.3f}, 📝{content_length}chars)")

                # Rate limiting
                time.sleep(2)

            except Exception as e:
                print(f"   ❌ Error extracting for query: {e}")
                all_sources_data[question] = []

        total_sites = sum(len(sources) for sources in all_sources_data.values())
        print(f"\n🌐 Deep extraction completed: {total_sites} sites with content extracted")

        return all_sources_data

    def _deep_search_with_extraction(self, query: str) -> List[Dict]:
        """Optimized search with immediate content extraction"""

        # Strategy 1: Direct search (main strategy)
        direct_results = self._serper_search(query)

        # Strategy 2: Only add one expanded search if needed
        if len(direct_results) < self.target_sources_per_query:
            expanded_results = self._serper_search(f"{query} guide tutorial")
            direct_results.extend(expanded_results)

        # Remove duplicates
        unique_results = self._remove_url_duplicates(direct_results)

        # Extract content from all unique URLs
        results_with_content = self._extract_content_from_urls(unique_results)

        print(f"   🔍 Found {len(results_with_content)} unique sites with extracted content")

        return results_with_content

    def _serper_search(self, query: str) -> List[Dict]:
        """Search using Serper API"""
        if len(query.split()) > 15:  # If query is too long
        # Take first 10 words
            query = ' '.join(query.split()[:10])

    # Remove complex punctuation that might confuse search
        query = query.replace('"', '').replace('(', '').replace(')', '')

        headers = {
            'X-API-KEY': self.serper_api_key,
            'Content-Type': 'application/json'
        }

        payload = {
            'q': query,
            'num': self.max_search_results,
            'gl': 'us',
            'hl': 'en'
        }

        try:
            with self.rate_limit_lock:
                response = requests.post(
                    self.serper_url,
                    headers=headers,
                    data=json.dumps(payload),
                    timeout=15
                )
                response.raise_for_status()

            data = response.json()
            results = []

            if 'organic' in data:
                for item in data['organic']:
                    result = {
                        'title': item.get('title', 'No title'),
                        'url': item.get('link', ''),
                        'snippet': item.get('snippet', 'No snippet'),
                        'query': query,
                        'source': 'serper_direct',
                        'search_position': len(results) + 1
                    }
                    results.append(result)

            return results

        except Exception as e:
            print(f"   Serper search error: {e}")
            return []

    def _expanded_search(self, query: str) -> List[Dict]:
        """Expanded search with contextual terms"""

        expansion_terms = [
            f'"{query}"',  # Exact phrase
            f'{query} tutorial guide',
            f'{query} explanation how',
            f'{query} examples applications'
        ]

        expanded_results = []

        for term in expansion_terms[:2]:  # Limit to save API calls
            try:
                results = self._serper_search(term)
                for result in results:
                    result['source'] = 'serper_expanded'
                expanded_results.extend(results)
                time.sleep(1)
            except:
                continue

        return expanded_results

    def _alternative_search(self, query: str) -> List[Dict]:
        """Alternative phrasing search"""

        alternatives = [
            f"what is {query}",
            f"{query} definition overview",
            f"understanding {query}"
        ]

        alternative_results = []

        for alt in alternatives[:1]:  # Limited alternatives
            try:
                results = self._serper_search(alt)
                for result in results:
                    result['source'] = 'serper_alternative'
                alternative_results.extend(results)
                time.sleep(1)
            except:
                continue

        return alternative_results

    def _search_deeper(self, query: str, current_count: int) -> List[Dict]:
        """Search deeper when not enough sources found"""

        needed = self.min_sources_per_query - current_count
        print(f"   🔍 Searching deeper for {needed} more sources...")

        deeper_terms = [
            f"{query} comprehensive guide",
            f"{query} detailed analysis",
            f"{query} research study",
            f"{query} implementation examples"
        ]

        deeper_results = []

        for term in deeper_terms:
            if len(deeper_results) >= needed:
                break

            try:
                results = self._serper_search(term)
                for result in results[:3]:  # Take top 3 per term
                    result['source'] = 'serper_deeper'
                deeper_results.extend(results)
                time.sleep(1)
            except:
                continue

        return deeper_results[:needed]

    def _remove_url_duplicates(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate URLs while preserving order"""

        seen_urls = set()
        unique_results = []

        for result in results:
            url = result.get('url', '').lower()
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)

        return unique_results

    def _extract_content_from_urls(self, results: List[Dict]) -> List[Dict]:
        """Extract content from all URLs with parallel processing"""

        depth_config = self.depth_configs[self.current_depth]
        max_content_length = depth_config['content_length']

        def extract_single_url(result):
            try:
                url = result.get('url', '')
                if not url:
                    return None

                # Scrape content
                response = requests.get(url, headers=self.scraping_headers, timeout=10)
                response.raise_for_status()

                # Parse content
                soup = BeautifulSoup(response.content, 'html.parser')

                # Remove unwanted elements
                for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                    element.decompose()

                # Extract text content
                content = soup.get_text(separator=' ', strip=True)

                # Clean and limit content
                cleaned_content = self._clean_extracted_content(content)
                limited_content = cleaned_content[:max_content_length]

                # Add extraction metadata
                result.update({
                    'extracted_content': limited_content,
                    'content_length': len(limited_content),
                    'extraction_success': True,
                    'source_url': url
                })

                return result

            except Exception as e:
                result.update({
                    'extracted_content': result.get('snippet', ''),
                    'content_length': len(result.get('snippet', '')),
                    'extraction_success': False,
                    'extraction_error': str(e),
                    'source_url': result.get('url', '')
                })
                return result

        # Parallel content extraction
        results_with_content = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_result = {
                executor.submit(extract_single_url, result): result
                for result in results
            }

            for future in concurrent.futures.as_completed(future_to_result):
                try:
                    result_with_content = future.result(timeout=15)
                    if result_with_content:
                        results_with_content.append(result_with_content)
                except Exception as e:
                    print(f"   Content extraction failed: {e}")

        return results_with_content

    def _clean_extracted_content(self, content: str) -> str:
        """Clean extracted content"""

        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)

        # Remove common navigation text
        unwanted_patterns = [
            r'cookie.*?policy',
            r'privacy.*?policy',
            r'terms.*?service',
            r'sign.*?up',
            r'log.*?in',
            r'subscribe',
            r'newsletter'
        ]

        for pattern in unwanted_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)

        return content.strip()

    def _rank_by_pure_relevancy(self, query: str, sources: List[Dict]) -> List[Dict]:
        """Rank sources by pure relevancy to query"""

        for source in sources:
            # Calculate relevancy score
            relevancy = self._calculate_deep_relevancy(query, source)
            source['relevance_score'] = relevancy

        # Sort by relevancy (highest first)
        ranked_sources = sorted(sources, key=lambda x: x['relevance_score'], reverse=True)

        return ranked_sources

    def _calculate_deep_relevancy(self, query: str, source: Dict) -> float:
        """Calculate deep relevancy score using multiple content sources"""

        # Get all text content
        title = source.get('title', '').lower()
        snippet = source.get('snippet', '').lower()
        extracted_content = source.get('extracted_content', '').lower()
        url = source.get('url', '').lower()

        query_lower = query.lower()
        query_words = set(word.strip() for word in query_lower.split() if len(word.strip()) > 2)

        if not query_words:
            return 0.0

        # Factor 1: Title relevancy (35% weight)
        title_words = set(word.strip() for word in title.split() if len(word.strip()) > 2)
        title_overlap = len(query_words.intersection(title_words))
        title_score = (title_overlap / len(query_words)) * 0.35

        # Factor 2: Content relevancy (40% weight) - Most important
        content_words = set(word.strip() for word in extracted_content.split() if len(word.strip()) > 2)
        content_overlap = len(query_words.intersection(content_words))
        content_score = (content_overlap / len(query_words)) * 0.40

        # Factor 3: Snippet relevancy (15% weight)
        snippet_words = set(word.strip() for word in snippet.split() if len(word.strip()) > 2)
        snippet_overlap = len(query_words.intersection(snippet_words))
        snippet_score = (snippet_overlap / len(query_words)) * 0.15

        # Factor 4: Exact phrase matching (10% weight)
        phrase_bonus = 0.0
        if query_lower in title:
            phrase_bonus += 0.05
        if query_lower in extracted_content:
            phrase_bonus += 0.05
        phrase_bonus = min(phrase_bonus, 0.10)

        # Factor 5: Content quality indicators (based on extraction success)
        quality_bonus = 0.0
        if source.get('extraction_success', False):
            content_length = source.get('content_length', 0)
            if content_length > 500:  # Good content length
                quality_bonus = 0.05

        total_score = title_score + content_score + snippet_score + phrase_bonus + quality_bonus

        return min(total_score, 1.0)

    def get_scout_stats(self) -> Dict:
        """Get scout statistics"""
        return {
            'api': 'serper',
            'min_sources_per_query': self.min_sources_per_query,
            'current_depth': self.current_depth,
            'depth_config': self.depth_configs[self.current_depth],
            'content_extraction': True,
            'parallel_processing': True
        }
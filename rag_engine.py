# rag_engine.py - QUERY UNDERSTANDING
from groq_handler import GroqHandler
from college.college_handler import CollegeHandler
from typing import List, Dict
import json

class IntelligentRAG:
    """
    Advanced RAG with LLM-powered query understanding.
    Uses Groq to understand intent and rewrite queries intelligently.
    """
    
    def __init__(self, groq_handler: GroqHandler, college_handler: CollegeHandler):
        self.groq = groq_handler
        self.college = college_handler
        print("Intelligent RAG with LLM query understanding initialized!")
    
    def understand_and_rewrite_query(self, query: str) -> Dict:
        """
        Use Groq LLM to deeply understand the query and rewrite it
        into precise search terms that will match the database.
        
        This is the KEY to true intelligence!
        """
        
        understanding_prompt = f"""You are a college database query expert. Analyze this student question and help retrieve the right information.

Student's question: "{query}"

Task: Understand what the student is REALLY asking for, then generate precise search queries that will find the information in a college database.

Examples:
- "head of CS" → means "HOD Computer Science" or "CSE department head"
- "accommodation facilities" → means "hostel", "boys hostel", "girls hostel"  
- "where can I eat" → means "canteen", "food court", "dining"
- "CS department location" → means "Computer Science department" (location)

Respond with ONLY this JSON format:
{{
    "understanding": "brief explanation of what student wants",
    "search_queries": ["query1", "query2", "query3"],
    "query_type": "person" or "location" or "timing" or "facility" or "general"
}}

Think step by step:
1. What is the student asking about? (person, place, time, facility, info)
2. What synonyms or related terms should we search for?
3. Generate 1-3 precise search queries

JSON:"""

        try:
            response = self.groq.client.chat.completions.create(
                model=self.groq.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert at understanding student questions about colleges. Always respond with valid JSON only."
                    },
                    {
                        "role": "user", 
                        "content": understanding_prompt
                    }
                ],
                temperature=0.2,  # Low temp for consistent parsing
                max_tokens=300
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Clean up response
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            understanding = json.loads(response_text)
            
            print(f"\n LLM Understanding:")
            print(f"   What student wants: {understanding['understanding']}")
            print(f"   Query type: {understanding['query_type']}")
            print(f"   Search terms: {understanding['search_queries']}")
            
            return understanding
            
        except Exception as e:
            print(f" Query understanding failed: {e}")
            # Fallback: use original query
            return {
                'understanding': 'Using original query',
                'search_queries': [query],
                'query_type': 'general'
            }
    
    def smart_multi_search(self, search_queries: List[str], query_type: str) -> List[Dict]:
        """
        Search database with multiple intelligent queries.
        Returns best matches across all searches.
        """
        all_results = {}  # Use dict to deduplicate
        
        for search_query in search_queries:
            context, score, title = self.college.get_match_with_score(
                search_query,
                threshold=0.20  # Lower threshold since queries are now precise
            )
            
            if context and title not in all_results:
                all_results[title] = {
                    'query': search_query,
                    'context': context,
                    'score': score,
                    'title': title
                }
        
        # Sort by score descending
        results = sorted(all_results.values(), key=lambda x: x['score'], reverse=True)
        
        # Take top 3 results
        return results[:3]
    
    def smart_answer(self, query: str) -> str:
        """
        Main intelligent RAG pipeline:
        1. LLM understands query deeply
        2. Rewrites into precise search terms  
        3. Searches local database (fast)
        4. LLM synthesizes natural answer
        """
        
        print(f"\n{'='*70}")
        print(f" INTELLIGENT RAG PROCESSING")
        print(f"{'='*70}")
        
        # STEP 1: LLM understands and rewrites query
        understanding = self.understand_and_rewrite_query(query)
        
        # STEP 2: Smart multi-search with rewritten queries
        results = self.smart_multi_search(
            understanding['search_queries'],
            understanding['query_type']
        )
        
        if not results:
            print(" No relevant information found")
            
            # Use LLM to generate helpful response
            no_match_prompt = f"""The student asked: "{query}"

We couldn't find information about this in our college database.

Provide a helpful response that:
1. Politely says we don't have that info
2. Suggests related topics they could ask about (departments, facilities, faculty, timings, locations)
3. Mentions they can visit the main office for more help

Be brief (2 sentences)."""

            return self.groq.answer_question(no_match_prompt)
        
        # STEP 3: Combine contexts
        print(f" Found {len(results)} relevant sources:")
        for r in results:
            print(f"   - {r['title']} (confidence: {r['score']:.3f})")
        
        combined_context = "\n\n".join([
            f"[Source: {r['title']}]\n{r['context']}" 
            for r in results
        ])
        
        # STEP 4: LLM synthesizes intelligent answer
        synthesis_prompt = f"""You are a helpful college assistant. Answer the student's question using the information provided.

Student's question: "{query}"

What the student wants: {understanding['understanding']}

Information from college database:
{combined_context}

Instructions:
- Answer naturally and conversationally
- Use ONLY information provided above
- If multiple sources, combine them intelligently
- Be clear and concise (2-4 sentences)
- If info is incomplete, mention "visit main office for more details"

Answer:"""

        answer = self.groq.client.chat.completions.create(
            model=self.groq.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful college assistant. Answer clearly based on provided information only."
                },
                {
                    "role": "user",
                    "content": synthesis_prompt
                }
            ],
            temperature=0.3,
            max_tokens=200
        ).choices[0].message.content.strip()
        
        print(f"\n Generated answer: {answer[:100]}...")
        print(f"{'='*70}\n")
        
        return answer



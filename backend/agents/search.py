from openai import OpenAI
import os
import json
import logging
from langchain_community.adapters.openai import convert_openai_messages
from langchain_openai import ChatOpenAI
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class SearchAgent:
    def __init__(self):
        self.perplexity_client = OpenAI(
            api_key=os.getenv("PERPLEXITY_API_KEY"),
            base_url="https://api.perplexity.ai"
        )
        logger.info("SearchAgent initialized")

    def extract_json_from_response(self, content: str):
        """Use GPT-4 mini to extract JSON from the response"""
        prompt = [{
            "role": "system",
            "content": "You are a JSON extractor. Your task is to find and extract only the JSON object from the given text. "
                      "The JSON should contain a 'results' array with objects having 'url', 'title', 'snippet', and 'date' fields. "
                      "Return only the valid JSON object, nothing else."
        }, {
            "role": "user",
            "content": f"Extract only the JSON object from this text:\n\n{content}"
        }]

        try:
            lc_messages = convert_openai_messages(prompt)
            optional_params = {
                "response_format": {"type": "json_object"}
            }
            response = ChatOpenAI(model='gpt-4o-mini', max_retries=1, model_kwargs=optional_params).invoke(lc_messages).content
            extracted = json.loads(response)
            
            # Validate the structure
            if 'results' not in extracted or not isinstance(extracted['results'], list):
                logger.error("Invalid JSON structure: missing 'results' array")
                return {'results': []}
                
            # Validate each result
            valid_results = []
            for result in extracted['results']:
                if all(k in result for k in ['url', 'title', 'snippet']):
                    # Ensure there's a date, even if approximate
                    if 'date' not in result:
                        result['date'] = datetime.now().strftime('%Y-%m-%d')
                    valid_results.append(result)
                else:
                    logger.warning(f"Skipping invalid result: {result}")
            
            return {'results': valid_results}
        except Exception as e:
            logger.error(f"Error extracting JSON: {str(e)}")
            return {'results': []}

    def search_perplexity(self, query: str):
        logger.info(f"Starting search for query: {query}")
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a news search assistant. Search for the latest news, blog posts, "
                    "and social media content (including X.com/Twitter) about the given topic. "
                    "Return only factual, recent information from reliable sources. "
                    "Format your response as a JSON object with a 'results' array containing objects with "
                    "'url', 'title', 'snippet', and 'date' fields. The date should be in YYYY-MM-DD format. "
                    "Each result must have all fields. Return at least 20 results if available."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Search for the latest news and discussions about: {query}\n"
                    "Include only content from the past month. "
                    "Focus on news articles, blog posts, and relevant social media discussions. "
                    "Return at least 20 results if available. "
                    "Make sure each result has a url, title, snippet, and publication date in YYYY-MM-DD format."
                )
            }
        ]

        try:
            logger.info("Making API request to Perplexity")
            response = self.perplexity_client.chat.completions.create(
                model="sonar-reasoning-pro",  
                messages=messages
            )
            
            try:
                if not hasattr(response, 'choices') or not response.choices:
                    logger.error("No choices in Perplexity response")
                    return [], "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=1000"
                
                content = response.choices[0].message.content
                logger.debug(f"Raw Perplexity response: {content}")
                
                if not content:
                    logger.error("Empty content from Perplexity")
                    return [], "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=1000"
                
                results = self.extract_json_from_response(content)
                sources = results.get('results', [])
                
                if not sources:
                    logger.warning("No valid sources found in Perplexity response")
                else:
                    logger.info(f"Retrieved {len(sources)} valid results from Perplexity")
                    logger.debug(f"First few results: {sources[:3]}")
                
                # Use a default image if no specific image is available
                image = "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=1000"
                
                return sources, image
                
            except Exception as e:
                logger.error(f"Failed to extract JSON: {str(e)}")
                logger.debug(f"Raw response content: {content if 'content' in locals() else 'No content available'}")
                return [], "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=1000"
                
        except Exception as e:
            logger.error(f"Error in Perplexity search: {str(e)}")
            return [], "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=1000"

    def run(self, article: dict):
        logger.info(f"SearchAgent running for topic: {article['query']}")
        res = self.search_perplexity(article["query"])
        article["sources"] = res[0]
        article["image"] = res[1]
        logger.info(f"SearchAgent completed. Found {len(article['sources'])} sources")
        return article

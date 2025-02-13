from datetime import datetime
from langchain_community.adapters.openai import convert_openai_messages
from langchain_openai import ChatOpenAI
from openai import OpenAI
import os
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)

class CuratorAgent:
    def __init__(self):
        self.client = OpenAI()
        logger.info("CuratorAgent initialized")

    def curate_sources(self, query: str, sources: list):
        """
        Curate relevant sources for a query
        :param query: The search query
        :param sources: List of source articles
        :return: Filtered list of sources
        """
        if not sources:
            logger.warning("No sources provided for curation")
            return []

        logger.info(f"Curating {len(sources)} sources for query: {query}")
        
        # Sort sources by date before curation
        try:
            sources = sorted(sources, key=lambda x: x.get('date', '1970-01-01'), reverse=True)
        except Exception as e:
            logger.warning(f"Error sorting sources by date: {str(e)}")
        
        prompt = [{
            "role": "system",
            "content": "You are a personal newspaper editor. Your task is to select the most relevant and diverse articles "
                      "from a list of sources. Choose articles that provide comprehensive coverage of different aspects "
                      "of the topic, prioritizing recent articles. Return at least 10 articles if available, or all articles if less than 10."
        }, {
            "role": "user",
            "content": f"Today's date is {datetime.now().strftime('%d/%m/%Y')}\n"
                      f"Topic or Query: {query}\n"
                      f"Your task is to return the most relevant articles for the topic.\n"
                      f"Here is a list of articles:\n"
                      f"{json.dumps(sources, indent=2)}\n"
                      f"Please return a JSON array of URLs for the selected articles. Include at least 10 articles if available."
        }]

        try:
            lc_messages = convert_openai_messages(prompt)
            response = ChatOpenAI(model='gpt-4o-mini', max_retries=1).invoke(lc_messages).content
            
            # Parse the response and extract URLs
            try:
                chosen_urls = json.loads(response)
                logger.info(f"Selected {len(chosen_urls)} sources from {len(sources)} available")
                
                # Filter sources while maintaining order
                filtered_sources = [s for s in sources if s["url"] in chosen_urls]
                logger.info(f"Final number of curated sources: {len(filtered_sources)}")
                return filtered_sources
            except json.JSONDecodeError:
                logger.error("Failed to parse curator response as JSON")
                return sources[:10]  # Return first 10 sources as fallback
        except Exception as e:
            logger.error(f"Error in source curation: {str(e)}")
            return sources[:10]  # Return first 10 sources as fallback

    def curate_content(self, article: dict):
        logger.info(f"Starting content curation for topic: {article['query']}")
        logger.info(f"Processing {len(article['sources'])} sources")

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a news curator and writer. Your task is to analyze the provided sources "
                    "and create a comprehensive news article that synthesizes the information. "
                    "Focus on recent developments, trends, and significant insights. "
                    "Write in a professional journalistic style. "
                    "Make sure to incorporate information from multiple sources to provide a well-rounded perspective. "
                    "Include publication dates when referencing sources."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Create a news article about {article['query']} using these sources:\n\n" +
                    json.dumps(article['sources'], indent=2) +
                    "\n\nFormat the response as a JSON object with 'title' and 'content' fields. " +
                    "The content should be properly formatted with HTML paragraphs and include citations with dates where appropriate. "
                    "When citing sources, include the publication date in the format (Source Name, YYYY-MM-DD)."
                )
            }
        ]

        try:
            logger.info("Making API request to OpenAI for content curation")
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"Content curation completed. Generated title: {result.get('title', 'No title')}")
            logger.debug("Content preview: " + result.get('content', '')[:200] + "...")
            
            return result
        except Exception as e:
            logger.error(f"Error in content curation: {str(e)}")
            return {"title": "Error", "content": "<p>Failed to generate content.</p>"}

    def run(self, article: dict):
        logger.info("CuratorAgent running")
        if article.get("sources"):
            article["sources"] = self.curate_sources(article["query"], article["sources"])
        result = self.curate_content(article)
        article["title"] = result["title"]
        article["content"] = result["content"]
        logger.info("CuratorAgent completed")
        return article

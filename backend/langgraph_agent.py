import os
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import TypedDict, List, Optional, Dict, Any
from langgraph.graph import StateGraph

# Import agent classes
from .agents import SearchAgent, CuratorAgent, WriterAgent, DesignerAgent, EditorAgent, PublisherAgent, CritiqueAgent, PodcastAgent

# Configure logging
logger = logging.getLogger(__name__)

# Define state schema
class AgentState(TypedDict):
    query: str
    sources: Optional[List[Dict[str, Any]]]
    image: Optional[str]
    title: Optional[str]
    date: Optional[str]
    paragraphs: Optional[List[str]]
    summary: Optional[str]
    critique_result: Optional[str]
    message: Optional[str]
    path: Optional[str]
    podcast: Optional[Dict[str, str]]

class MasterAgent:
    def __init__(self):
        logger.info("Initializing MasterAgent")
        self.output_dir = f"outputs/run_{int(time.time())}"
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"Created output directory: {self.output_dir}")

    def run(self, queries: list, layout: str):
        logger.info(f"Starting newspaper generation for queries: {queries}")
        logger.info(f"Using layout: {layout}")

        # Initialize agents
        logger.info("Initializing agents...")
        search_agent = SearchAgent()
        curator_agent = CuratorAgent()
        writer_agent = WriterAgent()
        critique_agent = CritiqueAgent()
        designer_agent = DesignerAgent(self.output_dir)
        editor_agent = EditorAgent(layout)
        publisher_agent = PublisherAgent(self.output_dir)
        podcast_agent = PodcastAgent(self.output_dir)
        logger.info("All agents initialized successfully")

        # Define a Langchain graph
        logger.info("Setting up workflow graph")
        workflow = StateGraph(AgentState)

        # Add nodes for each agent
        workflow.add_node("search_step", search_agent.run)
        workflow.add_node("curate_step", curator_agent.run)
        workflow.add_node("write_step", writer_agent.run)
        workflow.add_node("critique_step", critique_agent.run)
        workflow.add_node("design_step", designer_agent.run)

        # Set up edges
        workflow.add_edge('search_step', 'curate_step')
        workflow.add_edge('curate_step', 'write_step')
        workflow.add_edge('write_step', 'critique_step')

        # Define the conditional logic
        def decide_next_step(state: AgentState) -> str:
            result = "accept" if state.get('critique_result') is None else "revise"
            logger.info(f"Critique decision: {result}")
            return result

        # Add conditional edges with the new syntax
        workflow.add_conditional_edges(
            "critique_step",
            decide_next_step,
            {
                "accept": "design_step",
                "revise": "write_step"
            }
        )

        # set up start and end nodes
        workflow.set_entry_point("search_step")
        workflow.set_finish_point("design_step")

        # compile the graph
        logger.info("Compiling workflow graph")
        chain = workflow.compile()

        # Execute the graph for each query in parallel
        logger.info("Starting parallel processing of topics")
        with ThreadPoolExecutor() as executor:
            parallel_results = list(executor.map(
                lambda q: chain.invoke({
                    "query": q, 
                    "sources": None, 
                    "image": None, 
                    "title": None, 
                    "date": None, 
                    "paragraphs": None, 
                    "summary": None, 
                    "critique_result": None, 
                    "message": None, 
                    "path": None,
                    "podcast": None
                }), 
                queries
            ))
        logger.info("Completed parallel processing of topics")

        # Compile the final newspaper
        logger.info("Compiling final newspaper")
        newspaper_html = editor_agent.run(parallel_results)
        newspaper_path = publisher_agent.run(newspaper_html)

        # Generate podcast from the articles
        logger.info("Generating podcast from articles")
        podcast_result = podcast_agent.run(parallel_results)
        if podcast_result:
            # Update the newspaper HTML to include the audio player
            newspaper_html = self.add_audio_player_to_html(newspaper_html, podcast_result["podcast_path"])
            newspaper_path = publisher_agent.run(newspaper_html)
            logger.info(f"Newspaper with podcast published at: {newspaper_path}")
        else:
            logger.error("Failed to generate podcast")

        return newspaper_path

    def add_audio_player_to_html(self, html: str, audio_path: str) -> str:
        """Add an audio player to the HTML content"""
        # Get the relative path from the newspaper file to the audio file
        relative_audio_path = os.path.relpath(audio_path, self.output_dir)
        
        # Create the audio player HTML
        audio_player = f"""
        <div class="podcast-section" style="margin: 20px 0; padding: 20px; background: #f5f5f5; border-radius: 8px;">
            <h2 style="color: #333; margin-bottom: 15px;">📻 Listen to the News Podcast</h2>
            <audio controls style="width: 100%;">
                <source src="{relative_audio_path}" type="audio/mpeg">
                Your browser does not support the audio element.
            </audio>
        </div>
        """
        
        # Insert the audio player before the closing body tag
        html = html.replace('</body>', f'{audio_player}</body>')
        return html

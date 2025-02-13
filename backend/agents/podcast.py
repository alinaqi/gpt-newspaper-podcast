from openai import OpenAI
import os
import logging
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class PodcastAgent:
    def __init__(self, output_dir):
        self.client = OpenAI()
        self.output_dir = output_dir
        logger.info("PodcastAgent initialized")

    def generate_podcast_script(self, articles):
        """Generate an engaging podcast script from the articles"""
        logger.info("Generating podcast script")
        
        prompt = [{
            "role": "system",
            "content": "You are writing a script for 'GPT Podcast'. The show has three hosts: Alex (male), Lia (female), and Ray (male). "
                      "Create a natural, engaging conversation between these hosts as they discuss the news. "
                      "Format the script with clear speaker labels (ALEX:, LIA:, RAY:). Start with a welcome to GPT Podcast. "
                      "Make the conversation dynamic with hosts building on each other's points."
        }, {
            "role": "user",
            "content": f"Create a podcast script discussing these articles: {str(articles)}\n"
                      f"Start with 'ALEX: Welcome to GPT Podcast!' and maintain a natural conversation flow between the three hosts. "
                      f"Make sure each host contributes roughly equally to the discussion."
        }]

        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=prompt,
                temperature=0.7
            )
            script = response.choices[0].message.content
            logger.info("Podcast script generated successfully")
            return script
        except Exception as e:
            logger.error(f"Error generating podcast script: {str(e)}")
            return None

    def create_audio(self, script):
        """Convert the script to audio using OpenAI's TTS"""
        logger.info("Converting script to audio")
        
        try:
            # Create audio file path
            audio_file_path = Path(self.output_dir) / "podcast.mp3"
            
            # Generate speech using OpenAI's TTS
            response = self.client.audio.speech.create(
                model="tts-1-hd",  # Using HD model for better quality
                voice="nova",      # Using Nova voice for a natural, engaging tone
                input=script
            )
            
            # Save the audio file
            response.stream_to_file(str(audio_file_path))
            
            logger.info(f"Audio generated and saved to {audio_file_path}")
            return str(audio_file_path)
        except Exception as e:
            logger.error(f"Error creating audio: {str(e)}")
            return None

    def run(self, articles):
        """Main function to generate podcast from articles"""
        logger.info("PodcastAgent running")
        
        try:
            # Generate podcast script
            script = self.generate_podcast_script(articles)
            if not script:
                logger.error("Failed to generate podcast script")
                return None

            # Create audio from script
            audio_path = self.create_audio(script)
            if not audio_path:
                logger.error("Failed to create audio")
                return None

            logger.info("PodcastAgent completed successfully")
            return {
                "podcast_path": audio_path,
                "script": script
            }
        except Exception as e:
            logger.error(f"Error in PodcastAgent: {str(e)}")
            return None 
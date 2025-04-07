"""
Story foundation module that handles generating the initial story structure,
including setting, plot outline, and chapter summaries with genre integration.
python_file: foundation.py
"""

import json
import os
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from utils.prompt_templates import (
    STORY_FOUNDATION_PROMPT,
    CHAPTER_OUTLINE_PROMPT
)

class StoryFoundation:
    """Handles the generation of the story's foundation elements with genre considerations."""
    
    def __init__(self, llm):
        """Initialize the StoryFoundation class with a language model."""
        self.llm = llm
        
        # Define the schema for structured output parsing
        self.story_schema = [
            ResponseSchema(name="title", description="The title of the story"),
            ResponseSchema(name="theme", description="The main theme or themes of the story"),
            ResponseSchema(name="setting", description="Detailed description of the setting including location, social context, and cultural elements"),
            ResponseSchema(name="synopsis", description="A brief synopsis of the overall story"),
            ResponseSchema(name="narrative_arc", description="Description of the main narrative arc with beginning, middle, and end"),
            ResponseSchema(name="genre_elements", description="Description of how the selected genres are incorporated into the story"),
            ResponseSchema(name="narrative_tone", description="The overall tone and mood of the narrative"),
            ResponseSchema(name="social_context", description="Broader social and cultural context of the story"),
        ]
        
        self.chapter_schema = [
            ResponseSchema(name="chapter_number", description="The chapter number"),
            ResponseSchema(name="title", description="The title of the chapter"),
            ResponseSchema(name="summary", description="A summary of the main events in the chapter"),
            ResponseSchema(name="key_points", description="An array of key plot points in bullet form"),
            ResponseSchema(name="characters_involved", description="An array of characters involved in this chapter"),
            ResponseSchema(name="setting_details", description="Specific details about the setting for this chapter"),
            ResponseSchema(name="cultural_elements", description="Indian cultural elements to incorporate in this chapter"),
            ResponseSchema(name="genre_elements", description="Specific genre elements to incorporate in this chapter"),
            ResponseSchema(name="narrative_progression", description="How this chapter moves the story forward"),
        ]
    
    def generate_story_outline(self, plot_concept, region, narrative_tone, narrative_pacing, num_chapters, genres):
        """
        Generate the overall story outline including setting, themes, and narrative arc with genre integration.
        
        Args:
            plot_concept (str): Brief description of the story concept
            region (str): Region of India to set the story in
            narrative_tone (str): The overall tone of the narrative
            narrative_pacing (str): The narrative's pacing style
            num_chapters (int): Number of chapters in the story
            genres (list): List of genres to incorporate into the story
            
        Returns:
            dict: Story outline with structure, themes, and chapter outlines
        """
        # Create a parser for the structured output
        parser = StructuredOutputParser.from_response_schemas(self.story_schema)
        format_instructions = parser.get_format_instructions()
        
        # Format the genres as a comma-separated string
        genres_str = ", ".join(genres)
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_template(STORY_FOUNDATION_PROMPT)
        
        # Generate the story foundation
        chain = prompt | self.llm
        response = chain.invoke({
            "plot_concept": plot_concept,
            "region": region,
            "narrative_tone": narrative_tone,
            "narrative_pacing": narrative_pacing,
            "genres": genres_str,
            "format_instructions": format_instructions
        })
        
        # Parse the response
        try:
            story_outline = parser.parse(response.content)
        except Exception as e:
            print(f"Error parsing story outline: {e}")
            # Fallback to using the raw response
            story_outline = {
                "title": "Untitled Story",
                "theme": "Undefined",
                "setting": f"Set in {region}",
                "synopsis": plot_concept,
                "narrative_arc": "Beginning, middle, and end structure",
                "genre_elements": f"A blend of {genres_str}",
                "narrative_tone": narrative_tone,
                "social_context": "Contemporary Indian context"
            }
        
        # Generate chapter outlines
        chapter_outlines = self._generate_chapter_outlines(
            plot_concept=plot_concept,
            story_outline=story_outline,
            region=region,
            narrative_tone=narrative_tone,
            narrative_pacing=narrative_pacing,
            num_chapters=num_chapters,
            genres=genres
        )
        
        # Add chapters to the story outline
        story_outline["chapters"] = chapter_outlines
        
        # Store the genres in the story outline
        story_outline["genres"] = genres
        
        return story_outline
    
    def _generate_chapter_outlines(self, plot_concept, story_outline, region, narrative_tone, narrative_pacing, num_chapters, genres):
        """
        Generate outlines for each chapter in the story with genre integration.
        
        Args:
            plot_concept (str): Brief description of the story concept
            story_outline (dict): The overall story outline
            region (str): Region of India to set the story in
            narrative_tone (str): The overall tone of the narrative
            narrative_pacing (str): The narrative's pacing style
            num_chapters (int): Number of chapters to generate
            genres (list): List of genres to incorporate into the story
            
        Returns:
            list: List of chapter outlines
        """
        chapter_outlines = []
        parser = StructuredOutputParser.from_response_schemas([
            ResponseSchema(name="chapters", description="Array of chapter outlines")
        ])
        format_instructions = parser.get_format_instructions()
        
        # Format the genres as a comma-separated string
        genres_str = ", ".join(genres)
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_template(CHAPTER_OUTLINE_PROMPT)
        
        # Generate all chapter outlines at once
        chain = prompt | self.llm
        response = chain.invoke({
            "plot_concept": plot_concept,
            "story_outline": json.dumps(story_outline),
            "region": region,
            "narrative_tone": narrative_tone,
            "narrative_pacing": narrative_pacing,
            "genres": genres_str,
            "num_chapters": num_chapters,
            "format_instructions": format_instructions
        })
        
        # Parse the response
        try:
            result = parser.parse(response.content)
            chapter_outlines = result.get("chapters", [])
            
            # Ensure we have the correct number of chapters
            if len(chapter_outlines) < num_chapters:
                # Pad with empty chapters if necessary
                for i in range(len(chapter_outlines), num_chapters):
                    chapter_outlines.append({
                        "chapter_number": i + 1,
                        "title": f"Chapter {i + 1}",
                        "summary": "To be determined",
                        "key_points": [],
                        "characters_involved": [],
                        "setting_details": "",
                        "cultural_elements": [],
                        "genre_elements": f"Incorporating elements of {genres_str}",
                        "narrative_progression": f"Moving forward with {narrative_pacing} pace"
                    })
            elif len(chapter_outlines) > num_chapters:
                # Truncate if we have too many
                chapter_outlines = chapter_outlines[:num_chapters]
                
            # Ensure each chapter has genre_elements and narrative_progression
            for chapter in chapter_outlines:
                if "genre_elements" not in chapter:
                    chapter["genre_elements"] = f"Incorporating elements of {genres_str}"
                if "narrative_progression" not in chapter:
                    chapter["narrative_progression"] = f"Moving forward with {narrative_pacing} pace"
                    
        except Exception as e:
            print(f"Error parsing chapter outlines: {e}")
            # Generate basic chapter outlines as fallback
            for i in range(num_chapters):
                chapter_outlines.append({
                    "chapter_number": i + 1,
                    "title": f"Chapter {i + 1}",
                    "summary": "To be determined",
                    "key_points": [],
                    "characters_involved": [],
                    "setting_details": "",
                    "cultural_elements": [],
                    "genre_elements": f"Incorporating elements of {genres_str}",
                    "narrative_progression": f"Moving forward with {narrative_pacing} pace"
                })
        
        return chapter_outlines
        
    def blend_genres(self, genres):
        """
        Analyze how to blend multiple genres effectively.
        
        Args:
            genres (list): List of genres to blend
            
        Returns:
            dict: Guidelines for blending the genres
        """
        if len(genres) <= 1:
            return {"primary_genre": genres[0] if genres else "Drama"}
            
        # Create a prompt for genre blending guidance
        prompt = ChatPromptTemplate.from_template(
            "You are an expert storyteller specializing in Indian literature. "
            "Analyze how to effectively blend the following genres in a story: {genres}. "
            "Identify which elements from each genre should be highlighted and how they can "
            "complement each other. Consider Indian cultural contexts in your analysis."
        )
        
        # Generate genre blending guidance
        chain = prompt | self.llm
        response = chain.invoke({"genres": ", ".join(genres)})
        
        # Parse into a simple structure
        blend_guidance = {
            "primary_genre": genres[0],
            "secondary_genres": genres[1:] if len(genres) > 1 else [],
            "blending_strategy": response.content
        }
        
        return blend_guidance
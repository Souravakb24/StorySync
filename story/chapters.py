"""
Chapter generation module that handles creating individual chapters
with proper context management between chapters and genre integration.
python_file: chapters.py
"""

import json
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from utils.prompt_templates import CHAPTER_GENERATION_PROMPT

class ChapterGenerator:
    """Handles the generation of individual story chapters with genre awareness."""
    
    def __init__(self, llm, story_outline, main_characters, supporting_characters, context_manager, region, narrative_tone, narrative_pacing, genres):
        """
        Initialize the ChapterGenerator class.
        
        Args:
            llm: The language model to use
            story_outline (dict): The overall story outline
            main_characters (list): List of main character profiles
            supporting_characters (list): List of supporting character profiles
            context_manager: Context manager for tracking story state
            region (str): Region of India to set the story in
            narrative_tone (str): Tone of the narrative (e.g., Dramatic, Humorous)
            narrative_pacing (str): Pacing of the narrative (e.g., Slow-burning, Fast-paced)
            genres (list): List of genres to incorporate into the story
        """
        self.llm = llm
        self.story_outline = story_outline
        self.main_characters = main_characters
        self.supporting_characters = supporting_characters
        self.context_manager = context_manager
        self.region = region
        self.narrative_tone = narrative_tone
        self.narrative_pacing = narrative_pacing
        self.genres = genres
        
        # Define the schema for chapter output parsing
        self.chapter_schema = [
            ResponseSchema(name="title", description="The title of the chapter"),
            ResponseSchema(name="content", description="The full content of the chapter"),
            ResponseSchema(name="summary", description="A brief summary of what happened in the chapter"),
            ResponseSchema(name="key_events", description="List of important events that happened in the chapter"),
            ResponseSchema(name="character_development", description="How characters developed or changed in this chapter"),
            ResponseSchema(name="cultural_elements_used", description="Indian cultural elements that were incorporated"),
            ResponseSchema(name="genre_elements_used", description="How elements from the selected genres were incorporated in this chapter"),
            ResponseSchema(name="next_chapter_hooks", description="Story hooks or open questions for the next chapter")
        ]
        
        # Initialize genre arc tracking
        self.genre_arcs = self._initialize_genre_arcs()
    
    def _initialize_genre_arcs(self):
        """
        Initialize genre-specific story arcs and elements to track throughout the chapters.
        
        Returns:
            dict: Genre arc tracking information
        """
        genre_arcs = {}
        
        # Define standard elements to track for various genres
        for genre in self.genres:
            genre_lower = genre.lower()
            
            if "romance" in genre_lower:
                genre_arcs[genre] = {
                    "relationship_stages": ["Initial meeting", "Attraction", "Obstacles", "Growth", "Resolution"],
                    "current_stage": 0,
                    "emotional_beats": [],
                    "key_moments": []
                }
            elif "mystery" in genre_lower:
                genre_arcs[genre] = {
                    "mystery_elements": ["Initial problem", "Clues", "Red herrings", "Revelations", "Solution"],
                    "current_element": 0,
                    "revelations": [],
                    "open_questions": []
                }
            elif "adventure" in genre_lower:
                genre_arcs[genre] = {
                    "journey_stages": ["Call to adventure", "Challenges", "Trials", "Climactic challenge", "Return"],
                    "current_stage": 0,
                    "locations": [],
                    "achievements": []
                }
            elif "historical" in genre_lower or "period" in genre_lower:
                genre_arcs[genre] = {
                    "historical_elements": ["Setting establishment", "Period tensions", "Historical events", "Character adaptation", "Resolution"],
                    "current_element": 0,
                    "historical_references": [],
                    "period_authentic_elements": []
                }
            elif "fantasy" in genre_lower or "mytholog" in genre_lower:
                genre_arcs[genre] = {
                    "magical_elements": ["World rules", "Magic introduction", "Powers development", "Magical conflict", "Magical resolution"],
                    "current_element": 0,
                    "magical_components": [],
                    "mythological_references": []
                }
            else:
                # Generic tracking for other genres
                genre_arcs[genre] = {
                    "arc_stages": ["Introduction", "Development", "Complication", "Climax", "Resolution"],
                    "current_stage": 0,
                    "key_elements": [],
                    "genre_markers": []
                }
                
        return genre_arcs
    
    def generate_chapter(self, chapter_num):
        """
        Generate a single chapter of the story with appropriate genre elements.
        
        Args:
            chapter_num (int): The chapter number to generate
            
        Returns:
            dict: Complete chapter with content and metadata
        """
        # Get chapter outline from story outline
        chapter_outline = self._get_chapter_outline(chapter_num)
        
        # Get relevant context from previous chapters
        previous_context = self.context_manager.get_context_for_chapter(chapter_num)
        
        # Determine which genre elements to emphasize in this chapter
        genre_guidance = self._determine_genre_emphasis(chapter_num)
        
        # Create a parser for the structured output
        parser = StructuredOutputParser.from_response_schemas(self.chapter_schema)
        format_instructions = parser.get_format_instructions()
        
        # Format the genres as a comma-separated string
        genres_str = ", ".join(self.genres)
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_template(CHAPTER_GENERATION_PROMPT)
        
        # Generate the chapter
        chain = prompt | self.llm
        response = chain.invoke({
            "chapter_num": chapter_num,
            "chapter_outline": json.dumps(chapter_outline),
            "story_outline": json.dumps(self.story_outline),
            "main_characters": json.dumps(self.main_characters),
            "supporting_characters": json.dumps(self.supporting_characters),
            "previous_context": json.dumps(previous_context),
            "region": self.region,
            "narrative_tone": self.narrative_tone,
            "narrative_pacing": self.narrative_pacing,
            "genres": genres_str,
            "genre_guidance": json.dumps(genre_guidance),
            "format_instructions": format_instructions
        })
        
        # Parse the response
        try:
            chapter = parser.parse(response.content)
            # Add the chapter number
            chapter["chapter_number"] = chapter_num
            
            # Validate and ensure correct types for list fields
            chapter = self._validate_chapter_fields(chapter)
            
            # Update genre arcs based on this chapter
            self._update_genre_arcs(chapter, chapter_num)
            
            # Add genre trajectory to next chapter hooks if not present
            if "next_chapter_hooks" not in chapter or not chapter["next_chapter_hooks"]:
                chapter["next_chapter_hooks"] = []
            if "genre_trajectory" not in chapter.get("next_chapter_hooks", []):
                chapter["next_chapter_hooks"].append(self._get_genre_trajectory(chapter_num + 1))
                
        except Exception as e:
            print(f"Error parsing chapter content: {e}")
            # Create basic chapter as fallback
            chapter = {
                "chapter_number": chapter_num,
                "title": chapter_outline.get("title", f"Chapter {chapter_num}"),
                "content": "Error generating chapter content.",
                "summary": chapter_outline.get("summary", "Summary not available."),
                "key_events": [],
                "character_development": "No character development tracked.",
                "cultural_elements_used": [],
                "genre_elements_used": self._get_default_genre_elements(chapter_num),
                "next_chapter_hooks": []
            }
        
        return chapter
    
    def _validate_chapter_fields(self, chapter):
        """
        Validate chapter fields and ensure they have the correct types.
        
        Args:
            chapter (dict): The chapter data to validate
            
        Returns:
            dict: The validated chapter data with correct types
        """
        # Ensure key_events is a list
        if "key_events" in chapter:
            if isinstance(chapter["key_events"], str):
                chapter["key_events"] = [chapter["key_events"]] if chapter["key_events"] else []
            elif chapter["key_events"] is None:
                chapter["key_events"] = []
        else:
            chapter["key_events"] = []
            
        # Ensure next_chapter_hooks is a list
        if "next_chapter_hooks" in chapter:
            if isinstance(chapter["next_chapter_hooks"], str):
                chapter["next_chapter_hooks"] = [chapter["next_chapter_hooks"]] if chapter["next_chapter_hooks"] else []
            elif chapter["next_chapter_hooks"] is None:
                chapter["next_chapter_hooks"] = []
        else:
            chapter["next_chapter_hooks"] = []
            
        # Ensure cultural_elements_used is a list
        if "cultural_elements_used" in chapter:
            if isinstance(chapter["cultural_elements_used"], str):
                chapter["cultural_elements_used"] = [chapter["cultural_elements_used"]] if chapter["cultural_elements_used"] else []
            elif chapter["cultural_elements_used"] is None:
                chapter["cultural_elements_used"] = []
        else:
            chapter["cultural_elements_used"] = []
            
        # Ensure genre_elements_used is a list
        if "genre_elements_used" in chapter:
            if isinstance(chapter["genre_elements_used"], str):
                chapter["genre_elements_used"] = [chapter["genre_elements_used"]] if chapter["genre_elements_used"] else []
            elif chapter["genre_elements_used"] is None:
                chapter["genre_elements_used"] = []
        else:
            chapter["genre_elements_used"] = []
            
        # character_development can be either string or list, so we don't need to convert it
            
        return chapter
    
    def _get_chapter_outline(self, chapter_num):
        """
        Get the outline for a specific chapter from the story outline.
        
        Args:
            chapter_num (int): The chapter number
            
        Returns:
            dict: The chapter outline
        """
        chapters = self.story_outline.get("chapters", [])
        
        # Find the chapter with the matching chapter number
        for chapter in chapters:
            if chapter.get("chapter_number") == chapter_num:
                return chapter
        
        # If not found, return a default chapter outline
        return {
            "chapter_number": chapter_num,
            "title": f"Chapter {chapter_num}",
            "summary": "No summary available.",
            "key_points": [],
            "characters_involved": [],
            "setting_details": "",
            "cultural_elements": [],
            "genre_elements": []
        }
    
    def _determine_genre_emphasis(self, chapter_num):
        """
        Determine which genre elements to emphasize in the current chapter.
        
        Args:
            chapter_num (int): The chapter number to generate
            
        Returns:
            dict: Guidance on which genre elements to emphasize
        """
        total_chapters = len(self.story_outline.get("chapters", []))
        chapter_position = chapter_num / total_chapters  # 0.0 to 1.0 representing position in story
        
        # For beginning chapters (first quarter)
        if chapter_position <= 0.25:
            focus = "establishing"
            phase = "introduction"
        # For middle chapters (second and third quarters)
        elif chapter_position <= 0.75:
            focus = "developing"
            phase = "complication"
        # For ending chapters (last quarter)
        else:
            focus = "resolving"
            phase = "resolution"
        
        # Determine primary and secondary genres for this chapter
        # Create a cycle of emphasis so each genre gets highlighted
        primary_index = (chapter_num - 1) % len(self.genres)
        secondary_index = (primary_index + 1) % len(self.genres)
        
        primary_genre = self.genres[primary_index]
        secondary_genre = self.genres[secondary_index]
        
        # Get genre-specific stage based on chapter position
        genre_stages = {}
        for genre, arc_data in self.genre_arcs.items():
            # Calculate which stage of this genre's arc we should be in
            if "arc_stages" in arc_data:
                stage_index = min(int(chapter_position * len(arc_data["arc_stages"])), len(arc_data["arc_stages"]) - 1)
                genre_stages[genre] = {
                    "current_stage": arc_data["arc_stages"][stage_index],
                    "emphasis": "primary" if genre == primary_genre else "secondary" if genre == secondary_genre else "background"
                }
            elif "relationship_stages" in arc_data:  # Romance
                stage_index = min(int(chapter_position * len(arc_data["relationship_stages"])), len(arc_data["relationship_stages"]) - 1)
                genre_stages[genre] = {
                    "current_stage": arc_data["relationship_stages"][stage_index],
                    "emphasis": "primary" if genre == primary_genre else "secondary" if genre == secondary_genre else "background"
                }
            elif "mystery_elements" in arc_data:  # Mystery
                stage_index = min(int(chapter_position * len(arc_data["mystery_elements"])), len(arc_data["mystery_elements"]) - 1)
                genre_stages[genre] = {
                    "current_stage": arc_data["mystery_elements"][stage_index],
                    "emphasis": "primary" if genre == primary_genre else "secondary" if genre == secondary_genre else "background"
                }
            # Add other genre-specific logic as needed
        
        guidance = {
            "chapter_position": f"{chapter_num}/{total_chapters}",
            "narrative_phase": phase,
            "focus": focus,
            "primary_genre": primary_genre,
            "secondary_genre": secondary_genre,
            "genre_stages": genre_stages,
            "blend_recommendation": f"This chapter should primarily emphasize {primary_genre} elements while incorporating supporting elements from {secondary_genre}."
        }
        
        return guidance
    
    def _update_genre_arcs(self, chapter, chapter_num):
        """
        Update the genre arc tracking based on the generated chapter.
        
        Args:
            chapter (dict): The generated chapter
            chapter_num (int): The chapter number
        """
        # Extract genre elements used in the chapter
        genre_elements = chapter.get("genre_elements_used", [])
        
        # If it's a string, convert to list
        if isinstance(genre_elements, str):
            genre_elements = [genre_elements]
            
        # Process each genre element
        for element in genre_elements:
            element_lower = element.lower()
            
            # Update appropriate genre arcs based on content
            for genre, arc_data in self.genre_arcs.items():
                genre_lower = genre.lower()
                
                if "romance" in genre_lower and ("relationship" in element_lower or "romantic" in element_lower):
                    arc_data["key_moments"].append(element)
                    if "emotional" in element_lower:
                        arc_data["emotional_beats"].append(element)
                        
                elif "mystery" in genre_lower and ("clue" in element_lower or "reveal" in element_lower or "mystery" in element_lower):
                    if "reveal" in element_lower or "solution" in element_lower:
                        arc_data["revelations"].append(element)
                    else:
                        arc_data["open_questions"].append(element)
                        
                elif "adventure" in genre_lower and ("journey" in element_lower or "challenge" in element_lower or "quest" in element_lower):
                    if "location" in element_lower or "place" in element_lower:
                        arc_data["locations"].append(element)
                    if "achieve" in element_lower or "overcome" in element_lower:
                        arc_data["achievements"].append(element)
                        
                # Add more genre-specific tracking as needed
                
                # Generic tracking for any genre
                if genre_lower in element_lower:
                    arc_data["key_elements"].append(element)
                    arc_data["genre_markers"].append(element)
        
        # Update the current stage for each genre based on chapter position
        total_chapters = len(self.story_outline.get("chapters", []))
        chapter_position = chapter_num / total_chapters
        
        for genre, arc_data in self.genre_arcs.items():
            # Determine which stage we should be in based on chapter position
            for stage_list_key in ["arc_stages", "relationship_stages", "mystery_elements", "journey_stages", 
                                "historical_elements", "magical_elements"]:
                if stage_list_key in arc_data:
                    stages = arc_data[stage_list_key]
                    stage_index = min(int(chapter_position * len(stages)), len(stages) - 1)
                    arc_data["current_stage"] = stage_index
                    break
    
    def _get_genre_trajectory(self, next_chapter_num):
        """
        Get the genre trajectory for the next chapter.
        
        Args:
            next_chapter_num (int): The next chapter number
            
        Returns:
            str: Genre trajectory guidance
        """
        total_chapters = len(self.story_outline.get("chapters", []))
        
        # If we're at the end of the story
        if next_chapter_num > total_chapters:
            return "This is the conclusion - all genre elements should be resolved."
            
        # Determine which genres to focus on next
        primary_index = (next_chapter_num - 1) % len(self.genres)
        primary_genre = self.genres[primary_index]
        
        # Get the next stage for the primary genre
        next_stage = "development"
        for genre, arc_data in self.genre_arcs.items():
            if genre == primary_genre:
                # Find the relevant stage list
                for stage_list_key in ["arc_stages", "relationship_stages", "mystery_elements", "journey_stages", 
                                    "historical_elements", "magical_elements"]:
                    if stage_list_key in arc_data:
                        stages = arc_data[stage_list_key]
                        current_stage = arc_data.get("current_stage", 0)
                        next_stage_index = min(current_stage + 1, len(stages) - 1)
                        next_stage = stages[next_stage_index]
                        break
                break
                
        return f"Next chapter should advance the {primary_genre} elements toward {next_stage}."
    
    def _get_default_genre_elements(self, chapter_num):
        """
        Get default genre elements when chapter generation fails.
        
        Args:
            chapter_num (int): The chapter number
            
        Returns:
            list: Default genre elements
        """
        total_chapters = len(self.story_outline.get("chapters", []))
        chapter_position = chapter_num / total_chapters
        
        # Determine phase based on position
        if chapter_position <= 0.25:
            phase = "introduction"
        elif chapter_position <= 0.75:
            phase = "development"
        else:
            phase = "resolution"
            
        # Generate default elements for each genre based on phase
        default_elements = []
        
        for genre in self.genres:
            genre_lower = genre.lower()
            
            if "romance" in genre_lower:
                if phase == "introduction":
                    default_elements.append(f"Initial attraction between characters (Romance)")
                elif phase == "development":
                    default_elements.append(f"Relationship complications and growth (Romance)")
                else:
                    default_elements.append(f"Romantic resolution or commitment (Romance)")
                    
            elif "mystery" in genre_lower:
                if phase == "introduction":
                    default_elements.append(f"Mystery setup and initial clues (Mystery)")
                elif phase == "development":
                    default_elements.append(f"Investigation progress and red herrings (Mystery)")
                else:
                    default_elements.append(f"Mystery revelation and resolution (Mystery)")
                    
            elif "adventure" in genre_lower:
                if phase == "introduction":
                    default_elements.append(f"Journey beginning and initial challenges (Adventure)")
                elif phase == "development":
                    default_elements.append(f"Overcoming obstacles and character growth (Adventure)")
                else:
                    default_elements.append(f"Final challenge and triumphant return (Adventure)")
            
            # Add more genre-specific defaults as needed
            else:
                default_elements.append(f"{genre} elements appropriate for the {phase} phase")
                
        return default_elements
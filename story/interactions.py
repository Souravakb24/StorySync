"""
Interactive elements module for handling decision points and branching
narratives in the story with multi-genre integration.
python_file: interactions.py
"""

import json
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from utils.prompt_templates import (
    DECISION_POINTS_PROMPT, 
    BRANCH_GENERATION_PROMPT
)

class InteractiveElements:
    """Handles interactive elements and decision points in the story with genre awareness."""
    
    def __init__(self, llm, story_outline, main_characters, supporting_characters, region, narrative_tone, narrative_pacing, genres):
        """
        Initialize the InteractiveElements class.
        
        Args:
            llm: The language model to use
            story_outline (dict): The overall story outline
            main_characters (list): List of main character profiles
            supporting_characters (list): List of supporting character profiles
            region (str): Region of India to set the story in
            narrative_tone (str): The overall tone of the narrative
            narrative_pacing (str): The narrative's pacing style
            genres (list): List of genres to incorporate into the story
        """
        self.llm = llm
        self.story_outline = story_outline
        self.main_characters = main_characters
        self.supporting_characters = supporting_characters
        self.region = region
        self.narrative_tone = narrative_tone
        self.narrative_pacing = narrative_pacing
        self.genres = genres
        
        # Define schemas for output parsing
        self.decision_point_schema = [
            ResponseSchema(name="decision_points", description="Array of decision points")
        ]
        
        self.branch_schema = [
            ResponseSchema(name="title", description="Title of this branch"),
            ResponseSchema(name="content", description="Content for this branch of the story"),
            ResponseSchema(name="consequences", description="Consequences of this choice on the story and characters"),
            ResponseSchema(name="follow_up_hooks", description="Hooks for continuing the story from this branch"),
            ResponseSchema(name="character_impacts", description="How this choice impacts character development"),
            ResponseSchema(name="cultural_elements", description="Cultural elements incorporated in this branch"),
            ResponseSchema(name="genre_elements", description="Genre elements incorporated or emphasized in this branch"),
            ResponseSchema(name="genre_shift", description="How this choice shifts genre emphasis or balance if applicable"),
            ResponseSchema(name="narrative_tone_progression", description="How the narrative tone evolves with this branch")
        ]
        
        # Track genre progression through decision branches
        self.genre_decision_history = {}  # Maps decision point IDs to genre impacts
    
    def generate_decision_points(self, chapter_content, chapter_num, num_decisions=1):
        """
        Generate potential decision points for a chapter with genre considerations.
        
        Args:
            chapter_content (dict): The content of the chapter
            chapter_num (int): The chapter number
            num_decisions (int): Number of decision points to generate
            
        Returns:
            list: List of decision points with choices
        """
        # Create a parser for the structured output
        parser = StructuredOutputParser.from_response_schemas(self.decision_point_schema)
        format_instructions = parser.get_format_instructions()
        
        # Format the genres as a comma-separated string
        genres_str = ", ".join(self.genres)
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_template(DECISION_POINTS_PROMPT)
        
        # Generate the decision points
        chain = prompt | self.llm
        response = chain.invoke({
            "chapter_content": json.dumps(chapter_content),
            "chapter_num": chapter_num,
            "story_outline": json.dumps(self.story_outline),
            "main_characters": json.dumps(self.main_characters),
            "num_decisions": num_decisions,
            "region": self.region,
            "narrative_tone": self.narrative_tone,
            "narrative_pacing": self.narrative_pacing,
            "genres": genres_str,
            "format_instructions": format_instructions
        })
        
        # Parse the response
        try:
            result = parser.parse(response.content)
            decision_points = result.get("decision_points", [])
            
            # Ensure each decision point has genre impact information
            for dp in decision_points:
                if "genre_impacts" not in dp:
                    dp["genre_impacts"] = self._generate_default_genre_impacts(dp, chapter_num)
                
                # Ensure each choice has genre emphasis
                for choice in dp.get("choices", []):
                    if "genre_emphasis" not in choice:
                        choice["genre_emphasis"] = self._suggest_genre_emphasis(choice, dp, chapter_num)
                        
        except Exception as e:
            print(f"Error parsing decision points: {e}")
            # Create a default decision point as fallback
            decision_points = [{
                "point_id": f"dp_{chapter_num}_1",
                "description": "A decision point based on the chapter events",
                "context": "At a critical moment in the story",
                "choices": [
                    {
                        "choice_id": f"c_{chapter_num}_1_1",
                        "description": "First option",
                        "immediate_outcome": "The story continues with this choice",
                        "genre_emphasis": self._default_genre_emphasis(1, chapter_num)
                    },
                    {
                        "choice_id": f"c_{chapter_num}_1_2",
                        "description": "Second option",
                        "immediate_outcome": "The story takes a different path",
                        "genre_emphasis": self._default_genre_emphasis(2, chapter_num)
                    }
                ],
                "genre_impacts": self._generate_default_genre_impacts(None, chapter_num)
            }]
        
        return decision_points
    
    def generate_branch(self, chapter_content, decision_point, choice_id):
        """
        Generate a story branch based on a specific choice with genre awareness.
        
        Args:
            chapter_content (dict): The content of the chapter
            decision_point (dict): The decision point data
            choice_id (str): The ID of the chosen option
            
        Returns:
            dict: Story branch based on the chosen option
        """
        # Find the selected choice
        selected_choice = None
        for choice in decision_point.get("choices", []):
            if choice.get("choice_id") == choice_id:
                selected_choice = choice
                break
        
        if not selected_choice:
            print(f"Error: Choice ID {choice_id} not found in decision point")
            return None
        
        # Create a parser for the structured output
        parser = StructuredOutputParser.from_response_schemas(self.branch_schema)
        format_instructions = parser.get_format_instructions()
        
        # Format the genres as a comma-separated string
        genres_str = ", ".join(self.genres)
        
        # Get genre emphasis from the choice if available
        genre_emphasis = selected_choice.get("genre_emphasis", genres_str)
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_template(BRANCH_GENERATION_PROMPT)
        
        # Generate the branch
        chain = prompt | self.llm
        response = chain.invoke({
            "chapter_content": json.dumps(chapter_content),
            "decision_point": json.dumps(decision_point),
            "selected_choice": json.dumps(selected_choice),
            "story_outline": json.dumps(self.story_outline),
            "main_characters": json.dumps(self.main_characters),
            "region": self.region,
            "narrative_tone": self.narrative_tone,
            "narrative_pacing": self.narrative_pacing,
            "genres": genres_str,
            "genre_emphasis": genre_emphasis,
            "format_instructions": format_instructions
        })
        
        # Parse the response
        try:
            branch = parser.parse(response.content)
            # Add the choice ID to the branch
            branch["choice_id"] = choice_id
            branch["decision_point_id"] = decision_point.get("point_id")
            
            # Track genre impact of this decision
            self.genre_decision_history[decision_point.get("point_id")] = {
                "choice_id": choice_id,
                "genre_emphasis": genre_emphasis,
                "genre_shift": branch.get("genre_shift", "No significant genre shift")
            }
            
            # Ensure genre elements are included
            if "genre_elements" not in branch:
                branch["genre_elements"] = self._derive_genre_elements(selected_choice, branch)
                
        except Exception as e:
            print(f"Error parsing branch content: {e}")
            # Create a basic branch as fallback
            branch = {
                "title": f"Branch from choice {choice_id}",
                "content": f"The story continues based on choice {choice_id}.",
                "consequences": "The story continues with consequences of this choice.",
                "follow_up_hooks": ["The story continues..."],
                "character_impacts": "Characters are affected by this choice.",
                "cultural_elements": [],
                "genre_elements": self._default_genre_elements(selected_choice, decision_point),
                "genre_shift": self._default_genre_shift(selected_choice, decision_point),
                "narrative_tone_progression": f"Maintaining {self.narrative_tone} tone",
                "choice_id": choice_id,
                "decision_point_id": decision_point.get("point_id")
            }
            
            # Track genre impact even for fallback
            self.genre_decision_history[decision_point.get("point_id")] = {
                "choice_id": choice_id,
                "genre_emphasis": selected_choice.get("genre_emphasis", self.genres[0] if self.genres else "Drama"),
                "genre_shift": branch["genre_shift"]
            }
        
        return branch
        
    def _generate_default_genre_impacts(self, decision_point, chapter_num):
        """Generate default genre impact information for a decision point."""
        if not self.genres:
            return "This decision point will impact the story's direction."
            
        genre_impacts = []
        
        # Calculate which genres might be emphasized at this point in the story
        total_chapters = len(self.story_outline.get("chapters", []))
        chapter_position = chapter_num / total_chapters if total_chapters > 0 else 0.5
        
        # Determine appropriate genres based on narrative position
        if chapter_position < 0.3:  # Early in story
            for genre in self.genres:
                if "romance" in genre.lower():
                    genre_impacts.append(f"This decision could establish the romantic dynamics")
                elif "mystery" in genre.lower():
                    genre_impacts.append(f"This decision could introduce key mystery elements")
                elif "adventure" in genre.lower():
                    genre_impacts.append(f"This decision could set the journey's direction")
                else:
                    genre_impacts.append(f"This decision impacts {genre} elements")
        elif chapter_position < 0.7:  # Middle of story
            for genre in self.genres:
                if "romance" in genre.lower():
                    genre_impacts.append(f"This decision could complicate or deepen relationships")
                elif "mystery" in genre.lower():
                    genre_impacts.append(f"This decision could reveal important clues or create misdirection")
                elif "adventure" in genre.lower():
                    genre_impacts.append(f"This decision could present a significant challenge or discovery")
                else:
                    genre_impacts.append(f"This decision advances {genre} elements")
        else:  # Late in story
            for genre in self.genres:
                if "romance" in genre.lower():
                    genre_impacts.append(f"This decision could lead toward romantic resolution")
                elif "mystery" in genre.lower():
                    genre_impacts.append(f"This decision could lead toward solving the mystery")
                elif "adventure" in genre.lower():
                    genre_impacts.append(f"This decision could lead toward the journey's conclusion")
                else:
                    genre_impacts.append(f"This decision resolves {genre} elements")
                    
        return "; ".join(genre_impacts[:3])  # Limit to top 3 impacts
        
    def _suggest_genre_emphasis(self, choice, decision_point, chapter_num):
        """Suggest which genre(s) a particular choice might emphasize."""
        if not self.genres:
            return "No specific genre emphasis"
            
        choice_desc = choice.get("description", "").lower()
        choice_outcome = choice.get("immediate_outcome", "").lower()
        
        # Figure out which genre(s) this choice might emphasize based on content
        emphasized_genres = []
        
        for genre in self.genres:
            genre_lower = genre.lower()
            
            # Check for genre keywords in the choice description and outcome
            if "romance" in genre_lower:
                romance_keywords = ["love", "relationship", "emotion", "heart", "feeling", "together", "romantic"]
                if any(keyword in choice_desc or keyword in choice_outcome for keyword in romance_keywords):
                    emphasized_genres.append(genre)
                    
            elif "mystery" in genre_lower:
                mystery_keywords = ["secret", "clue", "investigate", "discover", "reveal", "solve", "truth", "suspicion"]
                if any(keyword in choice_desc or keyword in choice_outcome for keyword in mystery_keywords):
                    emphasized_genres.append(genre)
                    
            elif "adventure" in genre_lower:
                adventure_keywords = ["journey", "quest", "challenge", "danger", "explore", "risk", "brave", "venture"]
                if any(keyword in choice_desc or keyword in choice_outcome for keyword in adventure_keywords):
                    emphasized_genres.append(genre)
                    
            elif "historical" in genre_lower:
                historical_keywords = ["tradition", "heritage", "past", "ancestry", "legacy", "history", "era"]
                if any(keyword in choice_desc or keyword in choice_outcome for keyword in historical_keywords):
                    emphasized_genres.append(genre)
                    
            elif "drama" in genre_lower:
                drama_keywords = ["conflict", "emotion", "tense", "family", "struggle", "pain", "overcome"]
                if any(keyword in choice_desc or keyword in choice_outcome for keyword in drama_keywords):
                    emphasized_genres.append(genre)
                    
            # Add more genre keyword checks as needed
                    
        # If we couldn't detect any specific genres, use positional logic
        if not emphasized_genres:
            # Use chapter position to select genre emphasis
            total_chapters = len(self.story_outline.get("chapters", []))
            chapter_position = chapter_num / total_chapters if total_chapters > 0 else 0.5
            
            # Rotate through genres based on choice number and chapter position
            choice_id_num = int(choice.get("choice_id", "0").split("_")[-1])
            index = (chapter_num + choice_id_num) % len(self.genres)
            emphasized_genres.append(self.genres[index])
            
        return ", ".join(emphasized_genres[:2])  # Limit to top 2 genres
    
    def _default_genre_emphasis(self, choice_num, chapter_num):
        """Create default genre emphasis for fallback scenarios."""
        if not self.genres:
            return "Drama"
            
        # For first choice, emphasize first genre; for second choice, emphasize second genre, etc.
        index = (choice_num - 1) % len(self.genres)
        return self.genres[index]
        
    def _derive_genre_elements(self, choice, branch):
        """Derive genre elements from choice and branch content."""
        if not self.genres:
            return ["Generic story elements"]
            
        genre_elements = []
        content = branch.get("content", "")
        consequences = branch.get("consequences", "")
        
        # Extract genre emphasis from choice
        genre_emphasis = choice.get("genre_emphasis", "")
        if not genre_emphasis:
            genre_emphasis = self.genres[0] if self.genres else "Drama"
            
        # Create genre elements based on the emphasized genres
        emphasized_genres = [g.strip() for g in genre_emphasis.split(",")]
        
        for genre in emphasized_genres:
            genre_lower = genre.lower()
            
            if "romance" in genre_lower:
                genre_elements.append(f"Romantic development between characters ({genre})")
            elif "mystery" in genre_lower:
                genre_elements.append(f"Mystery progression with new revelations ({genre})")
            elif "adventure" in genre_lower:
                genre_elements.append(f"Adventure elements with challenges and exploration ({genre})")
            elif "historical" in genre_lower:
                genre_elements.append(f"Historical elements highlighting period authenticity ({genre})")
            elif "drama" in genre_lower:
                genre_elements.append(f"Dramatic elements focusing on emotional conflicts ({genre})")
            else:
                genre_elements.append(f"{genre} elements appropriate to the story")
                
        return genre_elements
    
    def _default_genre_elements(self, choice, decision_point):
        """Create default genre elements for fallback scenarios."""
        if not self.genres:
            return ["Generic story elements"]
            
        genre_elements = []
        
        # Extract genre emphasis from choice if available
        genre_emphasis = choice.get("genre_emphasis", "") if choice else ""
        if not genre_emphasis and self.genres:
            genre_emphasis = self.genres[0]
            
        # Create default elements based on emphasized genre
        if "romance" in genre_emphasis.lower():
            genre_elements.append("Development of romantic relationships")
            genre_elements.append("Emotional connection between characters")
        elif "mystery" in genre_emphasis.lower():
            genre_elements.append("Clues related to the central mystery")
            genre_elements.append("Increasing suspense and questions")
        elif "adventure" in genre_emphasis.lower():
            genre_elements.append("Journey progression and challenges")
            genre_elements.append("Exploration of new environments")
        elif "historical" in genre_emphasis.lower():
            genre_elements.append("Period-authentic scenarios and challenges")
            genre_elements.append("Cultural and historical context integration")
        else:
            for genre in self.genres[:2]:  # Use first two genres
                genre_elements.append(f"{genre} elements appropriate to the story")
                
        return genre_elements
        
    def _default_genre_shift(self, choice, decision_point):
        """Create default genre shift information for fallback scenarios."""
        if not self.genres or len(self.genres) <= 1:
            return "No significant genre shift"
            
        # Get genre emphasis from choice
        genre_emphasis = choice.get("genre_emphasis", "") if choice else ""
        if not genre_emphasis and self.genres:
            genre_emphasis = self.genres[0]
            
        # Create default genre shift description
        emphasized_genres = [g.strip() for g in genre_emphasis.split(",")]
        primary_genre = emphasized_genres[0] if emphasized_genres else self.genres[0]
        
        # Find a different genre to shift toward
        other_genres = [g for g in self.genres if g.lower() != primary_genre.lower()]
        if other_genres:
            secondary_genre = other_genres[0]
            return f"This choice shifts the narrative toward {primary_genre} with elements of {secondary_genre}"
        else:
            return f"This choice maintains focus on {primary_genre} elements"
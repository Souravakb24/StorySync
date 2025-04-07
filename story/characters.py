"""
Character generator module that creates main and supporting characters
with culturally authentic traits, backgrounds, and motivations,
reflecting multiple genre influences.
python_file: characters.py
"""

import json
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from utils.prompt_templates import (
    MAIN_CHARACTERS_PROMPT,
    SUPPORTING_CHARACTERS_PROMPT
)

class CharacterGenerator:
    """Handles the generation of main and supporting characters with genre awareness."""
    
    def __init__(self, llm):
        """Initialize the CharacterGenerator class with a language model."""
        self.llm = llm
        
        # Define the schema for character output parsing
        self.character_schema = [
            ResponseSchema(name="name", description="Full name of the character"),
            ResponseSchema(name="age", description="Age of the character"),
            ResponseSchema(name="gender", description="Gender of the character"),
            ResponseSchema(name="background", description="Detailed background of the character including birthplace, family, and cultural context"),
            ResponseSchema(name="appearance", description="Physical appearance description"),
            ResponseSchema(name="personality", description="Personality traits and characteristics"),
            ResponseSchema(name="motivations", description="Primary motivations and desires"),
            ResponseSchema(name="goals", description="Personal and narrative goals"),
            ResponseSchema(name="conflicts", description="Internal and external conflicts"),
            ResponseSchema(name="character_arc", description="How the character changes throughout the story"),
            ResponseSchema(name="cultural_traits", description="Specific cultural traits relevant to their Indian background"),
            ResponseSchema(name="speech_pattern", description="Distinctive way of speaking, including use of Indian expressions or language patterns"),
            ResponseSchema(name="relationships", description="Relationships with other characters"),
            ResponseSchema(name="genre_archetypes", description="Character archetypes from the selected genres that this character embodies"),
            ResponseSchema(name="genre_traits", description="Specific traits or qualities that reflect the story's genres"),
            ResponseSchema(name="socio_economic_context", description="Character's social and economic background within the Indian context"),
            ResponseSchema(name="professional_background", description="Character's career, profession, or primary occupation"),
            ResponseSchema(name="narrative_role", description="Character's role in the story's narrative structure"),
            ResponseSchema(name="emotional_landscape", description="Character's emotional depth and psychological complexity")
        ]
    
    def generate_main_characters(self, plot_concept, story_outline, region, narrative_tone, narrative_pacing, genres, num_characters=3):
        """
        Generate the main characters for the story with genre considerations.
        
        Args:
            plot_concept (str): Brief description of the story concept
            story_outline (dict): The overall story outline
            region (str): Region of India to set the story in
            narrative_tone (str): The overall tone of the narrative
            narrative_pacing (str): The pacing style of the narrative
            genres (list): List of genres to incorporate into character creation
            num_characters (int): Number of main characters to generate
            
        Returns:
            list: List of main character profiles
        """
        # Create a parser for the structured output
        parser = StructuredOutputParser.from_response_schemas([
            ResponseSchema(name="characters", description="Array of character profiles")
        ])
        format_instructions = parser.get_format_instructions()
        
        # Format the genres as a comma-separated string
        genres_str = ", ".join(genres)
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_template(MAIN_CHARACTERS_PROMPT)
        
        # Generate the main characters
        chain = prompt | self.llm
        response = chain.invoke({
            "plot_concept": plot_concept,
            "story_outline": json.dumps(story_outline),
            "region": region,
            "narrative_tone": narrative_tone,
            "narrative_pacing": narrative_pacing,
            "genres": genres_str,
            "num_characters": num_characters,
            "format_instructions": format_instructions
        })
        
        # Parse the response
        try:
            result = parser.parse(response.content)
            main_characters = result.get("characters", [])
            
            # Ensure each character has genre-related fields
            for character in main_characters:
                if "genre_archetypes" not in character:
                    character["genre_archetypes"] = self._generate_genre_archetypes(character, genres)
                if "genre_traits" not in character:
                    character["genre_traits"] = self._generate_genre_traits(character, genres)
                
                # Add narrative-specific context
                character["narrative_role"] = self._determine_narrative_role(character, genres, 0)
                character["emotional_landscape"] = self._analyze_emotional_complexity(character, narrative_tone)
                    
        except Exception as e:
            print(f"Error parsing main characters: {e}")
            # Generate basic character profiles as fallback
            main_characters = []
            for i in range(num_characters):
                main_characters.append({
                    "name": f"Character {i+1}",
                    "age": "Unknown",
                    "gender": "Unknown",
                    "background": f"From {region}",
                    "appearance": "To be determined",
                    "personality": "To be determined",
                    "motivations": "To be determined",
                    "goals": "To be determined",
                    "conflicts": "To be determined",
                    "character_arc": "To be determined",
                    "cultural_traits": f"Typical of {region}",
                    "speech_pattern": "Standard",
                    "relationships": "To be determined",
                    "genre_archetypes": self._default_genre_archetypes(genres, i),
                    "genre_traits": self._default_genre_traits(genres, i),
                    "socio_economic_context": "To be determined",
                    "professional_background": "To be determined",
                    "narrative_role": self._determine_narrative_role({}, genres, i),
                    "emotional_landscape": self._analyze_emotional_complexity({}, narrative_tone)
                })
        
        return main_characters
    
    def generate_supporting_characters(self, plot_concept, main_characters, story_outline, region, narrative_tone, narrative_pacing, genres, num_characters=5):
        """
        Generate supporting characters for the story based on main characters, plot, and genres.
        
        Args:
            plot_concept (str): Brief description of the story concept
            main_characters (list): List of main character profiles
            story_outline (dict): The overall story outline
            region (str): Region of India to set the story in
            narrative_tone (str): The overall tone of the narrative
            narrative_pacing (str): The pacing style of the narrative
            genres (list): List of genres to incorporate into character creation
            num_characters (int): Number of supporting characters to generate
            
        Returns:
            list: List of supporting character profiles
        """
        # Create a parser for the structured output
        parser = StructuredOutputParser.from_response_schemas([
            ResponseSchema(name="supporting_characters", description="Array of supporting character profiles")
        ])
        format_instructions = parser.get_format_instructions()
        
        # Format the genres as a comma-separated string
        genres_str = ", ".join(genres)
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_template(SUPPORTING_CHARACTERS_PROMPT)
        
        # Generate the supporting characters
        chain = prompt | self.llm
        response = chain.invoke({
            "plot_concept": plot_concept,
            "main_characters": json.dumps(main_characters),
            "story_outline": json.dumps(story_outline),
            "region": region,
            "narrative_tone": narrative_tone,
            "narrative_pacing": narrative_pacing,
            "genres": genres_str,
            "num_characters": num_characters,
            "format_instructions": format_instructions
        })
        
        # Parse the response
        try:
            result = parser.parse(response.content)
            supporting_characters = result.get("supporting_characters", [])
            
            # Ensure each supporting character has genre-related fields
            for character in supporting_characters:
                if "genre_role" not in character:
                    character["genre_role"] = self._generate_supporting_genre_role(character, genres)
                if "genre_purpose" not in character:
                    character["genre_purpose"] = self._generate_supporting_genre_purpose(character, genres, story_outline)
                
                # Add narrative-specific context
                character["narrative_role"] = self._determine_narrative_role(character, genres, 1)
                character["emotional_landscape"] = self._analyze_emotional_complexity(character, narrative_tone)
                    
        except Exception as e:
            print(f"Error parsing supporting characters: {e}")
            # Generate basic character profiles as fallback
            supporting_characters = []
            for i in range(num_characters):
                supporting_characters.append({
                    "name": f"Supporting Character {i+1}",
                    "role": "Minor character",
                    "relationship_to_main_characters": "Acquaintance",
                    "brief_description": "To be determined",
                    "cultural_background": f"From {region}",
                    "genre_role": self._default_supporting_genre_role(genres, i),
                    "genre_purpose": self._default_supporting_genre_purpose(genres, i),
                    "socio_economic_context": "To be determined",
                    "professional_background": "To be determined",
                    "narrative_role": self._determine_narrative_role({}, genres, i),
                    "emotional_landscape": self._analyze_emotional_complexity({}, narrative_tone)
                })
        
        return supporting_characters

    def _determine_narrative_role(self, character, genres, index):
        """
        Determine the narrative role of a character based on genres and character traits.
        
        Args:
            character (dict): Character profile
            genres (list): Story genres
            index (int): Character index for default role assignment
        
        Returns:
            str: Narrative role description
        """
        if not genres:
            return "Undefined narrative role"
        
        primary_genre = genres[0].lower()
        personality = character.get("personality", "").lower()
        
        # Role mapping based on genre and personality
        genre_role_map = {
            "romance": {
                "passionate": "Romantic Lead",
                "reserved": "Love Interest",
                "default": "Romantic Catalyst"
            },
            "mystery": {
                "curious": "Detective/Investigator",
                "secretive": "Key Suspect",
                "default": "Mystery Participant"
            },
            "adventure": {
                "brave": "Hero/Protagonist",
                "wise": "Mentor/Guide",
                "default": "Journey Companion"
            },
            "drama": {
                "emotional": "Emotional Anchor",
                "conflicted": "Internal Conflict Driver",
                "default": "Story Catalyst"
            }
        }
        
        # Try to match personality to a specific role
        for genre, role_map in genre_role_map.items():
            if genre in primary_genre:
                for trait, role in role_map.items():
                    if trait in personality:
                        return role
                return role_map["default"]
        
        # Fallback default roles based on index
        default_roles = [
            "Primary Narrative Driver",
            "Supporting Narrative Element",
            "Contextual Character",
            "Thematic Representation",
            "Narrative Catalyst"
        ]
        
        return default_roles[index % len(default_roles)]
    
    def _analyze_emotional_complexity(self, character, narrative_tone):
        """
        Analyze the emotional depth of a character based on narrative tone.
        
        Args:
            character (dict): Character profile
            narrative_tone (str): The overall tone of the narrative
        
        Returns:
            str: Description of emotional landscape
        """
        tone_emotional_map = {
            "Dramatic": "Deeply layered emotional landscape with intense internal conflicts",
            "Humorous": "Emotionally lighthearted with comedic undertones",
            "Suspenseful": "Emotionally tense with underlying anxiety and anticipation",
            "Inspirational": "Emotionally resilient with hope and personal growth",
            "Mysterious": "Emotionally guarded with hidden depths",
            "Emotional": "Rich, nuanced emotional experiences",
            "Philosophical": "Emotionally contemplative with intellectual depth",
            "Introspective": "Deeply self-aware with complex inner world"
        }
        
        # Analyze character's inherent emotional traits
        personality = character.get("personality", "").lower()
        conflicts = character.get("conflicts", "").lower()
        
        emotional_indicators = {
            "passionate": "Intense emotional experiences",
            "reserved": "Subtle, restrained emotional expression",
            "conflicted": "Internal emotional turmoil",
            "resilient": "Emotionally strong and adaptive"
        }
        
        # Default to narrative tone if no specific character traits
        base_description = tone_emotional_map.get(narrative_tone, "Balanced emotional landscape")
        
        # Enhance description with character-specific emotional indicators
        for trait, description in emotional_indicators.items():
            if trait in personality or trait in conflicts:
                base_description += f" with {description}"
                break
        
        return base_description
        
    def _generate_genre_archetypes(self, character, genres):
        """Generate genre-specific archetypes for a character based on their traits and the story genres."""
        if not genres:
            return "Standard character archetype"
            
        # This would typically involve a more complex analysis of the character in relation to genre conventions
        # For simplicity, we're providing a basic implementation
        archetypes = []
        personality = character.get("personality", "").lower()
        motivations = character.get("motivations", "").lower()
        conflicts = character.get("conflicts", "").lower()
        
        for genre in genres:
            genre = genre.lower()
            if "romance" in genre:
                if "passionate" in personality or "love" in motivations:
                    archetypes.append("Romantic Lead")
                elif "jealous" in personality or "rival" in conflicts:
                    archetypes.append("Romantic Rival")
            elif "adventure" in genre:
                if "brave" in personality or "explore" in motivations:
                    archetypes.append("Hero/Adventurer")
                elif "wise" in personality or "guide" in motivations:
                    archetypes.append("Mentor")
            elif "mystery" in genre:
                if "curious" in personality or "truth" in motivations:
                    archetypes.append("Detective/Truth Seeker")
                elif "secretive" in personality or "hidden" in motivations:
                    archetypes.append("Mysterious Figure")
            # Add more genre-specific archetype mappings as needed
                
        if not archetypes:
            # Default archetype based on primary genre
            primary_genre = genres[0].lower()
            if "romance" in primary_genre:
                archetypes.append("Romantic Character")
            elif "adventure" in primary_genre:
                archetypes.append("Adventurous Soul")
            elif "mystery" in primary_genre:
                archetypes.append("Enigmatic Individual")
            elif "historical" in primary_genre:
                archetypes.append("Historical Figure")
            elif "fantasy" in primary_genre:
                archetypes.append("Magical Character")
            else:
                archetypes.append("Cultural Archetype")
                
        return ", ".join(archetypes)
    
    def _generate_genre_traits(self, character, genres):
        """Generate genre-specific traits for a character based on the story genres."""
        if not genres:
            return "Standard character traits"
            
        # Combine multiple genre traits
        traits = []
        for genre in genres:
            genre = genre.lower()
            if "romance" in genre:
                traits.append("Emotionally complex")
            elif "adventure" in genre:
                traits.append("Resourceful and brave")
            elif "mystery" in genre:
                traits.append("Observant and analytical")
            elif "historical" in genre:
                traits.append("Connected to cultural traditions")
            elif "fantasy" in genre:
                traits.append("Believes in the supernatural")
            elif "comedy" in genre:
                traits.append("Has a keen sense of humor")
            elif "thriller" in genre:
                traits.append("Alert to danger")
            elif "drama" in genre:
                traits.append("Emotionally expressive")
            # Add more genre-specific trait mappings as needed
                
        if not traits:
            traits.append("Culturally authentic traits")
            
        return ", ".join(traits)
        
    def _default_genre_archetypes(self, genres, index):
        """Generate default genre archetypes when character generation fails."""
        if not genres:
            return "Standard character archetype"
            
        primary_genre = genres[0].lower() if genres else "drama"
        
        if index == 0:  # Protagonist
            if "romance" in primary_genre:
                return "Romantic Protagonist"
            elif "adventure" in primary_genre:
                return "Hero's Journey Archetype"
            else:
                return f"{primary_genre.title()} Protagonist"
        elif index == 1:  # Deuteragonist/Ally
            return f"Supporting {primary_genre.title()} Character"
        else:  # Other main characters
            if "romance" in primary_genre:
                return "Love Interest or Confidant"
            elif "mystery" in primary_genre:
                return "Suspect or Helper"
            else:
                return f"Important {primary_genre.title()} Character"
                
    def _default_genre_traits(self, genres, index):
        """Generate default genre traits when character generation fails."""
        if not genres:
            return "Standard character traits"
            
        traits = []
        for genre in genres[:2]:  # Use at most two genres for defaults
            genre = genre.lower()
            if "romance" in genre:
                traits.append("Romantically inclined")
            elif "adventure" in genre:
                traits.append("Seeks excitement")
            elif "mystery" in genre:
                traits.append("Curious and questioning")
            elif "historical" in genre:
                traits.append("Historically authentic")
            elif "fantasy" in genre:
                traits.append("Magical or mythical qualities")
            elif "drama" in genre:
                traits.append("Emotionally driven")
            else:
                traits.append(f"{genre.title()} characteristics")
                
        if not traits:
            traits.append("Culturally relevant traits")
            
        return ", ".join(traits)
        
    def _generate_supporting_genre_role(self, character, genres):
        """Generate genre-specific role for a supporting character."""
        if not genres:
            return "Standard supporting role"
            
        role = character.get("role", "").lower()
        description = character.get("brief_description", "").lower()
        
        # Determine role based on character description and genres
        if "mentor" in role or "guide" in role or "teach" in description:
            return "Mentor/Guide"
        elif "friend" in role or "ally" in role or "help" in description:
            return "Ally/Helper"
        elif "oppos" in role or "enemy" in role or "antagonist" in role:
            return "Antagonist/Obstacle"
        elif "family" in role or "relative" in role or "parent" in description:
            return "Family Member"
        
        # Default to genre-specific roles
        primary_genre = genres[0].lower() if genres else "drama"
        if "romance" in primary_genre:
            return "Romantic Facilitator or Obstacle"
        elif "mystery" in primary_genre:
            return "Information Provider or Red Herring"
        elif "adventure" in primary_genre:
            return "Quest Companion or Challenger"
        else:
            return f"{primary_genre.title()} Supporting Character"
    
    def _default_supporting_genre_role(self, genres, index):
        """Generate default genre role for supporting characters when generation fails."""
        if not genres:
            return "Minor character"
            
        primary_genre = genres[0].lower() if genres else "drama"
        
        if index % 5 == 0:
            return "Mentor or Guide"
        elif index % 5 == 1:
            return "Ally or Helper"
        elif index % 5 == 2:
            return "Comic Relief or Emotional Support"
        elif index % 5 == 3:
            return "Minor Antagonist or Obstacle"
        else:
            return "Background Character with Cultural Significance"
            
    def _generate_supporting_genre_purpose(self, character, genres, story_outline):
        """Generate genre-specific narrative purpose for a supporting character."""
        if not genres:
            return "Standard narrative purpose"
            
        # This would typically involve analyzing the character in relation to the story outline
        # For simplicity, we're providing a basic implementation
        role = character.get("role", "").lower()
        relationship = character.get("relationship_to_main_characters", "").lower()
        
        purposes = []
        for genre in genres:
            genre = genre.lower()
            if "romance" in genre:
                if "friend" in role or "confidant" in relationship:
                    purposes.append("Provides emotional support or romantic advice")
                elif "rival" in role or "compet" in relationship:
                    purposes.append("Creates romantic tension or obstacles")
            elif "mystery" in genre:
                if "witness" in role or "inform" in relationship:
                    purposes.append("Provides clues or information")
                elif "suspect" in role:
                    purposes.append("Misdirects the investigation")
            elif "adventure" in genre:
                if "ally" in role or "companion" in relationship:
                    purposes.append("Assists in the quest or journey")
                elif "expert" in role or "know" in relationship:
                    purposes.append("Provides specialized knowledge")
            # Add more genre-specific purpose mappings as needed
                
        if not purposes:
            narrative_themes = story_outline.get("theme", "").lower()
            if "family" in narrative_themes:
                purposes.append("Strengthens family themes")
            elif "tradition" in narrative_themes:
                purposes.append("Represents cultural traditions")
            elif "change" in narrative_themes:
                purposes.append("Highlights societal changes")
            else:
                purposes.append("Enhances cultural authenticity")
                
        return "; ".join(purposes)
        
    def _default_supporting_genre_purpose(self, genres, index):
        """Generate default genre purpose for supporting characters when generation fails."""
        if not genres:
            return "Minor role in the narrative"
            
        purposes = []
        for genre in genres[:2]:  # Use at most two genres for defaults
            genre = genre.lower()
            if "romance" in genre:
                purposes.append("Influences the romantic storyline")
            elif "mystery" in genre:
                purposes.append("Connects to the central mystery")
            elif "adventure" in genre:
                purposes.append("Assists or challenges during the journey")
            elif "historical" in genre:
                purposes.append("Provides historical context")
            elif "fantasy" in genre:
                purposes.append("Connects to magical or mythical elements")
            else:
                purposes.append(f"Serves typical {genre} narrative functions")
                
        if not purposes:
            purposes.append("Adds cultural depth to the story")
            
        return "; ".join(purposes)
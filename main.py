"""
Main entry point for the interactive story generator.
This script orchestrates the entire story generation process for audiobooks.
python_file: main.py
"""

import os
import json
from langchain.chat_models import ChatOpenAI
from config.settings import OPENAI_API_KEY, DEFAULT_MODEL, TEMPERATURE, DEFAULT_CHAPTERS
from story.foundation import StoryFoundation
from story.characters import CharacterGenerator
from story.chapters import ChapterGenerator
from utils.storage import StoryStorage
from utils.context_manager import ContextManager

# Define available genres for story generation
AVAILABLE_GENRES = [
    "Drama", "Romance", "Adventure", "Mystery", "Historical Fiction", 
    "Fantasy", "Mythology", "Folklore", "Family Saga", "Coming of Age",
    "Social Commentary", "Political", "Comedy", "Thriller", "Magical Realism",
    "Epic", "Devotional", "Philosophical", "Satire", "Fable", 
    "Horror", "Supernatural", "Science Fiction", "Dystopian", "Utopian",
    "Action", "War", "Inspirational", "Biographical", "Psychological",
    "Crime", "Spiritual", "Travelogue", "Epistolary", "Poetic Narrative",
    "Rural", "Urban", "Diaspora", "Revolutionary", "Postcolonial"
]

# Define narrative tones
NARRATIVE_TONES = [
    "Dramatic", 
    "Humorous", 
    "Suspenseful", 
    "Inspirational", 
    "Mysterious", 
    "Emotional", 
    "Philosophical", 
    "Introspective"
]

# Define narrative pacing options
NARRATIVE_PACING = [
    "Slow-burning", 
    "Fast-paced", 
    "Episodic", 
    "Continuous", 
    "Non-linear", 
    "Cyclical"
]

def create_story_directory(title):
    """Create a directory for the story based on its title"""
    sanitized_title = "".join(c if c.isalnum() or c.isspace() else "_" for c in title).strip()
    sanitized_title = sanitized_title.replace(" ", "_")
    directory = f"output/{sanitized_title}"
    
    if not os.path.exists(directory):
        os.makedirs(directory)
        os.makedirs(f"{directory}/chapters")
    
    return directory

def display_available_genres():
    """Display all available genres in a formatted manner"""
    print("\nAvailable Genres:")
    # Display genres in multiple columns for better readability
    cols = 3
    rows = (len(AVAILABLE_GENRES) + cols - 1) // cols
    
    for row in range(rows):
        line = ""
        for col in range(cols):
            idx = row + col * rows
            if idx < len(AVAILABLE_GENRES):
                # Format: "1. Drama          16. Epic          31. Crime"
                genre_num = f"{idx + 1}. {AVAILABLE_GENRES[idx]}"
                line += f"{genre_num:<20}"
        print(line)

def suggest_story_elements(plot_concept, llm):
    """
    Suggest multiple options for genres, narrative tone, and narrative pacing based on the plot concept
    
    Args:
        plot_concept (str): The user's plot or concept for the story
        llm: Language model instance
        
    Returns:
        dict: Multiple suggested options for genres, narrative tone, and narrative pacing
    """
    print("\nAnalyzing your plot concept to suggest suitable elements...")
    
    # If the plot is too short or empty, use defaults
    if len(plot_concept.strip()) < 10:
        print("Plot concept is too short for meaningful analysis. Using default suggestions.")
        return {
            "suggested_genres": [
                {"name": "Drama", "reason": "A versatile genre that works well for most stories."},
                {"name": "Family Saga", "reason": "Explores relationships and dynamics within families."},
                {"name": "Social Commentary", "reason": "Examines societal issues and human experiences."}
            ],
            "suggested_tones": [
                {"name": "Dramatic", "reason": "Creates emotional impact and depth."},
                {"name": "Emotional", "reason": "Connects with audiences through feelings and experiences."},
                {"name": "Philosophical", "reason": "Explores deeper meanings and questions."}
            ],
            "suggested_pacing": [
                {"name": "Slow-burning", "reason": "Allows for character development and building tension."},
                {"name": "Episodic", "reason": "Presents story in distinct segments or chapters."},
                {"name": "Continuous", "reason": "Maintains a steady flow of narrative events."}
            ]
        }
    
    # Create prompt for LLM to analyze the plot concept
    prompt = f"""
    Based on the following plot concept for an Indian story, suggest multiple options for:
    1. The 5 most suitable genres from this list: {', '.join(AVAILABLE_GENRES)}
    2. The 3 most suitable narrative tones from this list: {', '.join(NARRATIVE_TONES)}
    3. The 3 most suitable narrative pacing styles from this list: {', '.join(NARRATIVE_PACING)}
    
    For each suggestion, provide a brief reason (1-2 sentences) why it would work well with this plot concept.
    
    Plot concept: "{plot_concept}"
    
    You must respond with a valid JSON object and nothing else. The format should be exactly:
    {{
        "suggested_genres": [
            {{"name": "Genre1", "reason": "Brief reason this fits"}},
            {{"name": "Genre2", "reason": "Brief reason this fits"}},
            ...
        ],
        "suggested_tones": [
            {{"name": "Tone1", "reason": "Brief reason this fits"}},
            {{"name": "Tone2", "reason": "Brief reason this fits"}},
            ...
        ],
        "suggested_pacing": [
            {{"name": "Pacing1", "reason": "Brief reason this fits"}},
            {{"name": "Pacing2", "reason": "Brief reason this fits"}},
            ...
        ]
    }}
    
    Ensure each genre, tone, and pacing matches exactly one of the options provided in the lists above.
    """
    
    # Get suggestion from LLM using the up-to-date invoke method
    try:
        # Instead of using the deprecated predict method, use invoke
        response = llm.invoke(prompt)
        
        # The response might be in different formats depending on the LLM version
        if hasattr(response, 'content'):
            # For newer LangChain versions
            response_text = response.content
        else:
            # Fallback for older versions or different response formats
            response_text = str(response)
        
        # Parse the JSON response
        suggestions = json.loads(response_text)
        
        # Extract and validate suggested genres
        valid_genres = []
        if "suggested_genres" in suggestions:
            for genre_obj in suggestions["suggested_genres"]:
                if isinstance(genre_obj, dict) and "name" in genre_obj:
                    genre_name = genre_obj["name"]
                    if genre_name in AVAILABLE_GENRES:
                        valid_genres.append({
                            "name": genre_name,
                            "reason": genre_obj.get("reason", "Good match for your story concept.")
                        })
        
        # Extract and validate suggested tones
        valid_tones = []
        if "suggested_tones" in suggestions:
            for tone_obj in suggestions["suggested_tones"]:
                if isinstance(tone_obj, dict) and "name" in tone_obj:
                    tone_name = tone_obj["name"]
                    if tone_name in NARRATIVE_TONES:
                        valid_tones.append({
                            "name": tone_name,
                            "reason": tone_obj.get("reason", "Good match for your story concept.")
                        })
        
        # Extract and validate suggested pacing
        valid_pacing = []
        if "suggested_pacing" in suggestions:
            for pace_obj in suggestions["suggested_pacing"]:
                if isinstance(pace_obj, dict) and "name" in pace_obj:
                    pace_name = pace_obj["name"]
                    if pace_name in NARRATIVE_PACING:
                        valid_pacing.append({
                            "name": pace_name,
                            "reason": pace_obj.get("reason", "Good match for your story concept.")
                        })
        
        # Add default options if no valid options were found
        if not valid_genres:
            valid_genres = [{"name": AVAILABLE_GENRES[0], "reason": "Default option."}]
        if not valid_tones:
            valid_tones = [{"name": NARRATIVE_TONES[0], "reason": "Default option."}]
        if not valid_pacing:
            valid_pacing = [{"name": NARRATIVE_PACING[0], "reason": "Default option."}]
        
        return {
            "suggested_genres": valid_genres,
            "suggested_tones": valid_tones,
            "suggested_pacing": valid_pacing
        }
    except (json.JSONDecodeError, KeyError) as e:
        # Fallback to defaults if there's an error
        print(f"Error processing suggestions: {e}")
        return {
            "suggested_genres": [
                {"name": "Drama", "reason": "A versatile genre that works well for most stories."},
                {"name": "Family Saga", "reason": "Explores relationships and dynamics within families."},
                {"name": "Social Commentary", "reason": "Examines societal issues and human experiences."}
            ],
            "suggested_tones": [
                {"name": "Dramatic", "reason": "Creates emotional impact and depth."},
                {"name": "Emotional", "reason": "Connects with audiences through feelings and experiences."},
                {"name": "Philosophical", "reason": "Explores deeper meanings and questions."}
            ],
            "suggested_pacing": [
                {"name": "Slow-burning", "reason": "Allows for character development and building tension."},
                {"name": "Episodic", "reason": "Presents story in distinct segments or chapters."},
                {"name": "Continuous", "reason": "Maintains a steady flow of narrative events."}
            ]
        }
    except Exception as e:
        # Catch any other unexpected errors
        print(f"Unexpected error generating suggestions: {e}")
        return {
            "suggested_genres": [
                {"name": "Drama", "reason": "A versatile genre that works well for most stories."},
                {"name": "Family Saga", "reason": "Explores relationships and dynamics within families."},
                {"name": "Social Commentary", "reason": "Examines societal issues and human experiences."}
            ],
            "suggested_tones": [
                {"name": "Dramatic", "reason": "Creates emotional impact and depth."},
                {"name": "Emotional", "reason": "Connects with audiences through feelings and experiences."},
                {"name": "Philosophical", "reason": "Explores deeper meanings and questions."}
            ],
            "suggested_pacing": [
                {"name": "Slow-burning", "reason": "Allows for character development and building tension."},
                {"name": "Episodic", "reason": "Presents story in distinct segments or chapters."},
                {"name": "Continuous", "reason": "Maintains a steady flow of narrative events."}
            ]
        }

def main():
    """Main function to run the interactive story generator for audiobooks"""
    print("=" * 50)
    print("INTERACTIVE AUDIOBOOK STORY GENERATOR")
    print("=" * 50)
    
    # Initialize the language model
    llm = ChatOpenAI(
        api_key=OPENAI_API_KEY,
        model_name=DEFAULT_MODEL,
        temperature=TEMPERATURE
    )
    
    # Get initial story concept from user
    print("\nEnter a brief plot or concept for your story (1-2 lines):")
    plot_concept = input("> ")
    
    # Get suggestions based on the plot concept
    suggestions = suggest_story_elements(plot_concept, llm)
    
    # Display suggestions to the user
    print("\n--- SUGGESTED STORY ELEMENTS BASED ON YOUR PLOT ---")
    
    # Display suggested genres with reasons
    print("\nSUGGESTED GENRES:")
    for i, genre_obj in enumerate(suggestions['suggested_genres'], 1):
        print(f"{i}. {genre_obj['name']}: {genre_obj['reason']}")
    
    # Display suggested tones with reasons
    print("\nSUGGESTED NARRATIVE TONES:")
    for i, tone_obj in enumerate(suggestions['suggested_tones'], 1):
        print(f"{i}. {tone_obj['name']}: {tone_obj['reason']}")
    
    # Display suggested pacing with reasons
    print("\nSUGGESTED NARRATIVE PACING:")
    for i, pace_obj in enumerate(suggestions['suggested_pacing'], 1):
        print(f"{i}. {pace_obj['name']}: {pace_obj['reason']}")
    
    print("\n---------------------------------------------------")
    
    # Select multiple genres
    display_available_genres()
    print("\nSelect one or more genres (enter numbers or names separated by commas):")
    print("Example: '1, 5, 15' or 'Drama, Mystery, Fantasy'")
    print(f"Suggested: {', '.join([g['name'] for g in suggestions['suggested_genres']])}")
    genre_input = input("> ").strip()
    
    # If user just presses enter, use all the suggested genres
    if not genre_input:
        selected_genres = [genre_obj['name'] for genre_obj in suggestions['suggested_genres']]
        print(f"Using suggested genres: {', '.join(selected_genres)}")
    else:
        # Process genre selections
        selected_genres = []
        
        # Split input by commas
        genre_inputs = [g.strip() for g in genre_input.split(',')]
        
        for input_item in genre_inputs:
            try:
                # Check if input is a number referencing the suggested genres
                sugg_idx = int(input_item) - 1
                if 0 <= sugg_idx < len(suggestions['suggested_genres']):
                    selected_genres.append(suggestions['suggested_genres'][sugg_idx]['name'])
                else:
                    # Try to match with the full genre list
                    genre_idx = int(input_item) - 1
                    if 0 <= genre_idx < len(AVAILABLE_GENRES):
                        selected_genres.append(AVAILABLE_GENRES[genre_idx])
                    else:
                        print(f"Invalid selection number: {input_item}")
            except ValueError:
                # Input was not a number, try to match it with available genres
                input_item = input_item.title()
                if input_item in AVAILABLE_GENRES:
                    selected_genres.append(input_item)
                else:
                    print(f"Genre not found: {input_item}")
        
        # If no valid genres were selected, use the suggested genres
        if not selected_genres:
            selected_genres = [genre_obj['name'] for genre_obj in suggestions['suggested_genres']]
            print(f"No valid genres selected. Using suggested genres: {', '.join(selected_genres)}")
    
    # Remove duplicates while preserving order
    selected_genres = list(dict.fromkeys(selected_genres))
    
    print(f"Selected genres: {', '.join(selected_genres)}")
    
    print("\nEnter desired setting region in India (North, South, East, West, Central):")
    region = input("> ").strip().capitalize() + " India"
    if region not in ["North India", "South India", "East India", "West India", "Central India"]:
        region = "North India"  # Default
        print(f"Using default region: {region}")
    
    # Narrative Tone Selection
    print("\nSelect narrative tone (choose one):")
    
    # Display narrative tones
    for i, tone in enumerate(NARRATIVE_TONES, 1):
        print(f"{i}. {tone}")
    
    print(f"Suggested: Enter a number 1-{len(suggestions['suggested_tones'])} to choose from the suggestions, or any other valid option")
    narrative_tone_input = input("> ").strip()
    
    # If user just presses enter, use the first suggested tone
    if not narrative_tone_input:
        narrative_tone = suggestions['suggested_tones'][0]['name']
        print(f"Using suggested tone: {narrative_tone}")
    else:
        try:
            # First check if it's one of the suggested tones
            sugg_idx = int(narrative_tone_input) - 1
            if 0 <= sugg_idx < len(suggestions['suggested_tones']):
                narrative_tone = suggestions['suggested_tones'][sugg_idx]['name']
            else:
                # Try to match with the full tone list
                tone_index = int(narrative_tone_input) - 1
                if 0 <= tone_index < len(NARRATIVE_TONES):
                    narrative_tone = NARRATIVE_TONES[tone_index]
                else:
                    narrative_tone = suggestions['suggested_tones'][0]['name']
                    print(f"Invalid selection. Using suggested tone: {narrative_tone}")
        except ValueError:
            # If input is not a number, try to match with available tones
            narrative_tone_input = narrative_tone_input.capitalize()
            if narrative_tone_input in NARRATIVE_TONES:
                narrative_tone = narrative_tone_input
            else:
                narrative_tone = suggestions['suggested_tones'][0]['name']
                print(f"Tone not found. Using suggested tone: {narrative_tone}")
    
    # Narrative Pacing Selection
    print("\nSelect narrative pacing:")
    
    # Display narrative pacing options
    for i, pace in enumerate(NARRATIVE_PACING, 1):
        print(f"{i}. {pace}")
    
    print(f"Suggested: Enter a number 1-{len(suggestions['suggested_pacing'])} to choose from the suggestions, or any other valid option")
    pacing_input = input("> ").strip()
    
    # If user just presses enter, use the first suggested pacing
    if not pacing_input:
        selected_pacing = suggestions['suggested_pacing'][0]['name']
        print(f"Using suggested pacing: {selected_pacing}")
    else:
        try:
            # First check if it's one of the suggested pacing options
            sugg_idx = int(pacing_input) - 1
            if 0 <= sugg_idx < len(suggestions['suggested_pacing']):
                selected_pacing = suggestions['suggested_pacing'][sugg_idx]['name']
            else:
                # Try to match with the full pacing list
                pace_index = int(pacing_input) - 1
                if 0 <= pace_index < len(NARRATIVE_PACING):
                    selected_pacing = NARRATIVE_PACING[pace_index]
                else:
                    selected_pacing = suggestions['suggested_pacing'][0]['name']
                    print(f"Invalid selection. Using suggested pacing: {selected_pacing}")
        except ValueError:
            # If input is not a number, try to match with available pacing
            pacing_input = pacing_input.capitalize()
            if pacing_input in NARRATIVE_PACING:
                selected_pacing = pacing_input
            else:
                selected_pacing = suggestions['suggested_pacing'][0]['name']
                print(f"Pacing not found. Using suggested pacing: {selected_pacing}")
    
    print("\nEnter number of chapters (default: 10):")
    try:
        num_chapters = int(input("> ").strip())
    except (ValueError, TypeError):
        num_chapters = DEFAULT_CHAPTERS
        print(f"Using default number of chapters: {num_chapters}")
    
    # Initialize story components
    story_foundation = StoryFoundation(llm)
    character_generator = CharacterGenerator(llm)
    context_manager = ContextManager()
    language = 'hindi'
    
    # Generate story foundation
    print("\nGenerating story foundation...")
    story_outline = story_foundation.generate_story_outline(
        plot_concept=plot_concept,
        region=region,
        narrative_tone=narrative_tone,
        narrative_pacing=selected_pacing,
        num_chapters=num_chapters,
        genres=selected_genres
    )
    
    # Generate main characters
    print("\nGenerating main characters...")
    main_characters = character_generator.generate_main_characters(
        plot_concept=plot_concept,
        story_outline=story_outline,
        region=region,
        narrative_tone=narrative_tone,
        narrative_pacing=selected_pacing,
        genres=selected_genres
    )
    
    # Generate supporting characters
    print("\nGenerating supporting characters...")
    supporting_characters = character_generator.generate_supporting_characters(
        plot_concept=plot_concept,
        main_characters=main_characters,
        story_outline=story_outline,
        region=region,
        narrative_tone=narrative_tone,
        narrative_pacing=selected_pacing,
        genres=selected_genres
    )
    
    # Create storage directory
    story_title = story_outline.get("title", "Untitled_Story")
    story_dir = create_story_directory(story_title)
    
    # Initialize story storage
    storage = StoryStorage(story_dir)
    
    # Save story foundation and characters
    storage.save_story_outline(story_outline)
    storage.save_characters({
        "main_characters": main_characters,
        "supporting_characters": supporting_characters
    })
    
    # Save genres and narrative information
    metadata = {
        "genres": selected_genres,
        "region": region,
        "narrative_tone": narrative_tone,
        "narrative_pacing": selected_pacing,
        "language": language
    }
    storage.save_metadata(metadata)
    
    # Initialize chapter generator
    chapter_generator = ChapterGenerator(
        llm=llm,
        story_outline=story_outline,
        main_characters=main_characters,
        supporting_characters=supporting_characters,
        context_manager=context_manager,
        region=region,
        narrative_tone=narrative_tone,
        narrative_pacing=selected_pacing,
        genres=selected_genres
    )
    
    # Generate chapters
    for chapter_num in range(1, num_chapters + 1):
        print(f"\nGenerating Chapter {chapter_num}...")
        chapter = chapter_generator.generate_chapter(chapter_num)
        storage.save_chapter(chapter, chapter_num)
        
        # Update context for next chapter
        context_manager.update_with_chapter(chapter, chapter_num)
        
        # Display chapter info
        print(f"Chapter {chapter_num}: {chapter.get('title', 'Untitled')}")
        print(f"Word count: {len(chapter.get('content', '').split())}")
    
    print("\n" + "=" * 50)
    print(f"Story generation complete! Files saved to {story_dir}")
    print(f"Genres: {', '.join(selected_genres)}")
    print(f"Region: {region}")
    print(f"Narrative Tone: {narrative_tone}")
    print(f"Narrative Pacing: {selected_pacing}")
    print("=" * 50)

if __name__ == "__main__":
    main()
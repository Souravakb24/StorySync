import os
import json
import gradio as gr
import tempfile
import zipfile
import shutil
from langchain_openai import ChatOpenAI  # Updated import
from config.settings import OPENAI_API_KEY, DEFAULT_MODEL, TEMPERATURE, DEFAULT_CHAPTERS
from story.foundation import StoryFoundation
from story.characters import CharacterGenerator
from story.chapters import ChapterGenerator
from utils.storage import StoryStorage
from utils.context_manager import ContextManager

# Import constants from main.py
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

NARRATIVE_PACING = [
    "Slow-burning", 
    "Fast-paced", 
    "Episodic", 
    "Continuous", 
    "Non-linear", 
    "Cyclical"
]

# Regions in India
REGIONS = ["North India", "South India", "East India", "West India", "Central India"]

# Languages
LANGUAGES = ["Hindi", "English", "Tamil", "Bengali", "Telugu", "Marathi", "Gujarati", "Kannada", "Malayalam", "Punjabi"]

def suggest_story_elements(plot_concept, progress=gr.Progress()):
    """
    Suggest multiple options for genres, narrative tone, and narrative pacing based on the plot concept
    
    Args:
        plot_concept (str): The user's plot or concept for the story
        progress (gr.Progress): Gradio progress indicator
        
    Returns:
        dict: Multiple suggested options for genres, narrative tone, and narrative pacing
    """
    try:
        progress(0.1, "Analyzing your plot concept")
    except Exception:
        # Handle cases where progress tracker might not be functioning
        pass
    
    # Initialize the language model
    llm = ChatOpenAI(
        api_key=OPENAI_API_KEY,
        model_name=DEFAULT_MODEL,
        temperature=TEMPERATURE
    )
    
    # If the plot is too short or empty, use defaults
    if len(plot_concept.strip()) < 10:
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
    
    try:
        progress(0.2, "Getting suggestions from AI")
    except Exception:
        pass
    
    # Get suggestion from LLM using the invoke method
    try:
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
        
        # Process and validate the suggestions (similar to your existing code)
        # ...
        
        try:
            progress(0.3, "Processing suggestions")
        except Exception:
            pass
        
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
        
        try:
            progress(0.4, "Suggestions ready")
        except Exception:
            pass
        
        return {
            "suggested_genres": valid_genres,
            "suggested_tones": valid_tones,
            "suggested_pacing": valid_pacing
        }
    except Exception as e:
        # Fallback to defaults if there's an error
        try:
            progress(0.4, f"Error processing suggestions: {str(e)}. Using defaults.")
        except Exception:
            pass
        
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

def format_suggestions_for_display(suggestions):
    """
    Format the suggestions to display in the UI
    
    Args:
        suggestions (dict): Suggestions from the AI
        
    Returns:
        str: Formatted HTML to display the suggestions
    """
    html = "<div style='text-align: left;'>"
    
    # Genres section
    html += "<h3>🎭 Suggested Genres</h3>"
    html += "<ul>"
    for genre in suggestions["suggested_genres"]:
        html += f"<li><strong>{genre['name']}</strong>: {genre['reason']}</li>"
    html += "</ul>"
    
    # Tones section
    html += "<h3>🎭 Suggested Narrative Tones</h3>"
    html += "<ul>"
    for tone in suggestions["suggested_tones"]:
        html += f"<li><strong>{tone['name']}</strong>: {tone['reason']}</li>"
    html += "</ul>"
    
    # Pacing section
    html += "<h3>⏱️ Suggested Narrative Pacing</h3>"
    html += "<ul>"
    for pace in suggestions["suggested_pacing"]:
        html += f"<li><strong>{pace['name']}</strong>: {pace['reason']}</li>"
    html += "</ul>"
    
    html += "</div>"
    return html

def create_story_directory(title):
    """Create a directory for the story based on its title"""
    sanitized_title = "".join(c if c.isalnum() or c.isspace() else "_" for c in title).strip()
    sanitized_title = sanitized_title.replace(" ", "_")
    directory = f"output/{sanitized_title}"
    
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        os.makedirs(f"{directory}/chapters", exist_ok=True)
    
    return directory

def generate_full_story(
    plot_concept, 
    title, 
    genres, 
    region, 
    narrative_tone, 
    narrative_pacing, 
    num_chapters,
    language,
    progress=gr.Progress()
):
    """
    Generate the full story based on user inputs
    
    Args:
        plot_concept (str): The plot concept
        title (str): Story title
        genres (list): Selected genres
        region (str): Selected region
        narrative_tone (str): Selected narrative tone
        narrative_pacing (str): Selected narrative pacing
        num_chapters (int): Number of chapters
        language (str): Selected language
        progress (gr.Progress): Gradio progress indicator
        
    Returns:
        dict: Complete story data including outline, characters, and chapters
    """
    try:
        progress(0.1, "Initializing story generation")
    except Exception:
        pass
    
    # Initialize the language model
    llm = ChatOpenAI(
        api_key=OPENAI_API_KEY,
        model_name=DEFAULT_MODEL,
        temperature=TEMPERATURE
    )
    
    # Initialize story components
    story_foundation = StoryFoundation(llm)
    character_generator = CharacterGenerator(llm)
    context_manager = ContextManager()
    
    try:
        progress(0.2, "Generating story foundation")
    except Exception:
        pass
    
    # Generate story foundation
    story_outline = story_foundation.generate_story_outline(
        plot_concept=plot_concept,
        region=region,
        narrative_tone=narrative_tone,
        narrative_pacing=narrative_pacing,
        num_chapters=num_chapters,
        genres=genres
    )
    
    # Override title if provided
    if title and title.strip():
        story_outline["title"] = title
    else:
        title = story_outline.get("title", "Untitled_Story")
    
    try:
        progress(0.3, "Generating main characters")
    except Exception:
        pass
    
    # Generate main characters
    main_characters = character_generator.generate_main_characters(
        plot_concept=plot_concept,
        story_outline=story_outline,
        region=region,
        narrative_tone=narrative_tone,
        narrative_pacing=narrative_pacing,
        genres=genres
    )
    
    try:
        progress(0.4, "Generating supporting characters")
    except Exception:
        pass
    
    # Generate supporting characters
    supporting_characters = character_generator.generate_supporting_characters(
        plot_concept=plot_concept,
        main_characters=main_characters,
        story_outline=story_outline,
        region=region,
        narrative_tone=narrative_tone,
        narrative_pacing=narrative_pacing,
        genres=genres
    )
    
    # Create storage directory
    story_dir = create_story_directory(title)
    
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
        "genres": genres,
        "region": region,
        "narrative_tone": narrative_tone,
        "narrative_pacing": narrative_pacing,
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
        narrative_pacing=narrative_pacing,
        genres=genres
    )
    
    # Generate chapters
    chapters = []
    chapter_progress_start = 0.5
    chapter_progress_per_chapter = 0.5 / num_chapters
    
    for chapter_num in range(1, num_chapters + 1):
        try:
            progress(
                chapter_progress_start + (chapter_num - 1) * chapter_progress_per_chapter,
                f"Generating Chapter {chapter_num} of {num_chapters}"
            )
        except Exception:
            pass
        
        chapter = chapter_generator.generate_chapter(chapter_num)
        storage.save_chapter(chapter, chapter_num)
        
        # Update context for next chapter
        context_manager.update_with_chapter(chapter, chapter_num)
        
        # Add to chapters list
        chapters.append(chapter)
    
    try:
        progress(1.0, "Story generation complete")
    except Exception:
        pass
    
    # Return complete story data
    return {
        "title": title,
        "directory": story_dir,
        "outline": story_outline,
        "main_characters": main_characters,
        "supporting_characters": supporting_characters,
        "chapters": chapters,
        "metadata": metadata
    }

def create_story_zip(story_data):
    """
    Create a ZIP file of the story for download
    
    Args:
        story_data (dict): The complete story data
        
    Returns:
        str: Path to the created ZIP file
    """
    # Create a temporary directory to hold all files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save story outline
        with open(os.path.join(temp_dir, "story_outline.json"), "w") as f:
            json.dump(story_data["outline"], f, indent=2)
        
        with open(os.path.join(temp_dir, "story_outline.txt"), "w") as f:
            f.write(f"# {story_data['title']}\n\n")
            f.write(f"## Synopsis\n{story_data['outline'].get('synopsis', '')}\n\n")
            f.write(f"## Themes\n{story_data['outline'].get('themes', '')}\n\n")
            f.write(f"## Setting\n{story_data['outline'].get('setting', '')}\n\n")
        
        # Save characters
        with open(os.path.join(temp_dir, "characters.json"), "w") as f:
            json.dump({
                "main_characters": story_data["main_characters"],
                "supporting_characters": story_data["supporting_characters"]
            }, f, indent=2)
        
        with open(os.path.join(temp_dir, "characters.txt"), "w") as f:
            f.write("# Characters\n\n")
            f.write("## Main Characters\n\n")
            for char in story_data["main_characters"]:
                f.write(f"### {char.get('name', 'Unnamed')}\n")
                f.write(f"* Age: {char.get('age', 'Unknown')}\n")
                f.write(f"* Background: {char.get('background', 'Unknown')}\n")
                f.write(f"* Personality: {char.get('personality', 'Unknown')}\n")
                f.write(f"* Goals: {char.get('goals', 'Unknown')}\n\n")
            
            f.write("## Supporting Characters\n\n")
            for char in story_data["supporting_characters"]:
                f.write(f"### {char.get('name', 'Unnamed')}\n")
                f.write(f"* Role: {char.get('role', 'Unknown')}\n")
                f.write(f"* Description: {char.get('description', 'Unknown')}\n\n")
        
        # Save metadata
        with open(os.path.join(temp_dir, "metadata.json"), "w") as f:
            json.dump(story_data["metadata"], f, indent=2)
        
        # Create chapters directory
        chapters_dir = os.path.join(temp_dir, "chapters")
        os.makedirs(chapters_dir, exist_ok=True)
        
        # Save chapters as individual files
        for i, chapter in enumerate(story_data["chapters"], 1):
            # JSON format
            with open(os.path.join(chapters_dir, f"chapter_{i}.json"), "w") as f:
                json.dump(chapter, f, indent=2)
            
            # Text format
            with open(os.path.join(chapters_dir, f"chapter_{i}.txt"), "w") as f:
                f.write(f"# Chapter {i}: {chapter.get('title', 'Untitled')}\n\n")
                f.write(chapter.get('content', ''))
        
        # Create a complete story text file
        with open(os.path.join(temp_dir, "complete_story.txt"), "w") as f:
            f.write(f"# {story_data['title']}\n\n")
            f.write(f"## Synopsis\n{story_data['outline'].get('synopsis', '')}\n\n")
            
            for i, chapter in enumerate(story_data["chapters"], 1):
                f.write(f"\n\n## Chapter {i}: {chapter.get('title', 'Untitled')}\n\n")
                f.write(chapter.get('content', ''))
        
        # Create a ZIP file
        zip_path = os.path.join(tempfile.gettempdir(), f"{story_data['title'].replace(' ', '_')}.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
    
    return zip_path

def format_story_preview(story_data):
    """
    Format the story data for preview in the UI
    
    Args:
        story_data (dict): The complete story data
        
    Returns:
        str: Formatted HTML to display the story preview
    """
    html = f"<div style='text-align: left;'>"
    
    # Story title and metadata
    html += f"<h1>{story_data['title']}</h1>"
    html += f"<p><strong>Genres:</strong> {', '.join(story_data['metadata']['genres'])}</p>"
    html += f"<p><strong>Region:</strong> {story_data['metadata']['region']}</p>"
    html += f"<p><strong>Tone:</strong> {story_data['metadata']['narrative_tone']}</p>"
    html += f"<p><strong>Pacing:</strong> {story_data['metadata']['narrative_pacing']}</p>"
    html += f"<p><strong>Language:</strong> {story_data['metadata']['language']}</p>"
    
    # Synopsis
    html += f"<h2>Synopsis</h2>"
    html += f"<p>{story_data['outline'].get('synopsis', '')}</p>"
    
    # Themes
    if 'themes' in story_data['outline']:
        html += f"<h2>Themes</h2>"
        html += f"<p>{story_data['outline']['themes']}</p>"
    
    # Setting
    if 'setting' in story_data['outline']:
        html += f"<h2>Setting</h2>"
        html += f"<p>{story_data['outline']['setting']}</p>"
    
    # Characters
    html += f"<h2>Main Characters</h2>"
    html += "<div style='display: flex; flex-wrap: wrap;'>"
    
    for char in story_data["main_characters"]:
        html += "<div style='width: 45%; margin: 10px; padding: 10px; border: 1px solid #ccc; border-radius: 5px;'>"
        html += f"<h3>{char.get('name', 'Unnamed')}</h3>"
        html += f"<p><strong>Age:</strong> {char.get('age', 'Unknown')}</p>"
        html += f"<p><strong>Background:</strong> {char.get('background', 'Unknown')}</p>"
        html += f"<p><strong>Personality:</strong> {char.get('personality', 'Unknown')}</p>"
        html += "</div>"
    
    html += "</div>"
    
    # Supporting Characters (collapsed)
    html += f"<h2>Supporting Characters</h2>"
    html += "<details>"
    html += "<summary>Click to expand/collapse</summary>"
    html += "<div style='display: flex; flex-wrap: wrap;'>"
    
    for char in story_data["supporting_characters"]:
        html += "<div style='width: 45%; margin: 10px; padding: 10px; border: 1px solid #ccc; border-radius: 5px;'>"
        html += f"<h3>{char.get('name', 'Unnamed')}</h3>"
        html += f"<p><strong>Role:</strong> {char.get('role', 'Unknown')}</p>"
        html += f"<p><strong>Description:</strong> {char.get('description', 'Unknown')}</p>"
        html += "</div>"
    
    html += "</div>"
    html += "</details>"
    
    # Chapters (each in a collapsible section)
    html += f"<h2>Chapters</h2>"
    
    for i, chapter in enumerate(story_data["chapters"], 1):
        html += "<details>"
        html += f"<summary>Chapter {i}: {chapter.get('title', 'Untitled')}</summary>"
        html += f"<div style='white-space: pre-wrap;'>{chapter.get('content', '')}</div>"
        html += "</details>"
    
    html += "</div>"
    return html

def get_suggestions(plot_concept):
    """
    Get story element suggestions based on plot concept
    
    Args:
        plot_concept (str): The plot concept
        
    Returns:
        tuple: (HTML formatted suggestions, suggested genres list, suggested tone, suggested pacing)
    """
    progress = gr.Progress()
    suggestions = suggest_story_elements(plot_concept, progress)
    
    # Format suggestions for display
    formatted_suggestions = format_suggestions_for_display(suggestions)
    
    # Extract suggested genres, tone, and pacing for the next steps
    suggested_genres = [genre["name"] for genre in suggestions["suggested_genres"]]
    suggested_tone = suggestions["suggested_tones"][0]["name"] if suggestions["suggested_tones"] else NARRATIVE_TONES[0]
    suggested_pacing = suggestions["suggested_pacing"][0]["name"] if suggestions["suggested_pacing"] else NARRATIVE_PACING[0]
    
    # Return values directly without using gr.update
    return formatted_suggestions, suggested_genres, suggested_tone, suggested_pacing

def generate_and_preview(plot_concept, title, genres, region, narrative_tone, narrative_pacing, num_chapters, language):
    """
    Generate the story and format it for preview
    
    Args:
        plot_concept (str): The plot concept
        title (str): The story title
        genres (list): Selected genres
        region (str): Selected region
        narrative_tone (str): Selected narrative tone
        narrative_pacing (str): Selected narrative pacing
        num_chapters (int): Number of chapters
        language (str): Selected language
        
    Returns:
        tuple: (HTML formatted story preview, download file path)
    """
    progress = gr.Progress()
    story_data = generate_full_story(
        plot_concept, 
        title, 
        genres, 
        region, 
        narrative_tone, 
        narrative_pacing, 
        num_chapters,
        language,
        progress
    )
    
    # Create a ZIP file for download
    zip_path = create_story_zip(story_data)
    
    # Format the story data for preview
    formatted_preview = format_story_preview(story_data)
    
    return formatted_preview, zip_path

# Create the Gradio interface
with gr.Blocks(title="Interactive Audiobook Story Generator") as app:
    gr.Markdown("# 📚 Interactive Audiobook Story Generator")
    gr.Markdown("Create rich, culturally authentic Indian stories with AI assistance")
    
    with gr.Tab("Step 1: Story Concept"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Enter your story concept")
                plot_concept = gr.Textbox(
                    label="Plot Concept", 
                    placeholder="Enter a brief plot or concept for your story (1-2 lines)",
                    lines=3
                )
                analyze_btn = gr.Button("✨ Analyze & Suggest Elements", variant="primary")
            
            with gr.Column():
                suggestions_display = gr.HTML(label="AI Suggestions")
        
        # Store suggestions for the next step
        suggested_genres_store = gr.State([])
        suggested_tone_store = gr.State("")
        suggested_pacing_store = gr.State("")
    
    with gr.Tab("Step 2: Story Configuration"):
        with gr.Row():
            with gr.Column():
                title = gr.Textbox(
                    label="Story Title", 
                    placeholder="Enter a title for your story (optional, AI will generate one if empty)"
                )
                
                genres = gr.CheckboxGroup(
                    label="Select Genres (Multiple)", 
                    choices=AVAILABLE_GENRES
                )
                
                region = gr.Dropdown(
                    label="Setting Region", 
                    choices=REGIONS,
                    value="North India"
                )
            
            with gr.Column():
                narrative_tone = gr.Dropdown(
                    label="Narrative Tone", 
                    choices=NARRATIVE_TONES,
                    value="Dramatic"
                )
                
                narrative_pacing = gr.Dropdown(
                    label="Narrative Pacing", 
                    choices=NARRATIVE_PACING,
                    value="Slow-burning"
                )
                
                language = gr.Dropdown(
                    label="Language", 
                    choices=LANGUAGES,
                    value="Hindi"
                )
                
                num_chapters = gr.Slider(
                    label="Number of Chapters", 
                    minimum=1, 
                    maximum=20, 
                    value=10, 
                    step=1
                )
        
        generate_btn = gr.Button("🎮 Generate Story", variant="primary")
    
    with gr.Tab("Step 3: Preview & Export"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Story Preview")
                story_preview = gr.HTML()
            
        with gr.Row():
            download_btn = gr.Button("📥 Download Story", variant="secondary")
            download_file = gr.File(label="Download Complete Story")
    
    # Connect functions to buttons
    analyze_btn.click(
        fn=get_suggestions,
        inputs=[plot_concept],
        outputs=[suggestions_display, genres, narrative_tone, narrative_pacing]
    )
    
    generate_btn.click(
        fn=generate_and_preview,
        inputs=[
            plot_concept, 
            title, 
            genres, 
            region, 
            narrative_tone, 
            narrative_pacing, 
            num_chapters,
            language
        ],
        outputs=[story_preview, download_file]
    )
    
    download_btn.click(
        fn=lambda x: x,
        inputs=[download_file],
        outputs=[download_file]
    )

# Launch the app
if __name__ == "__main__":
    app.launch(share=True)  # Added share=True to create a public link
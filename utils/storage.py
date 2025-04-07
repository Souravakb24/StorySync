"""
Storage module for saving and loading story components.
python_file: storage.py
"""

import os
import json
import time

class StoryStorage:
    """Handles saving and loading story components to and from files."""
    
    def __init__(self, story_dir):
        """
        Initialize the StoryStorage class.
        
        Args:
            story_dir (str): Directory to store story files
        """
        self.story_dir = story_dir
        
        # Create directories if they don't exist
        if not os.path.exists(story_dir):
            os.makedirs(story_dir)
        
        if not os.path.exists(f"{story_dir}/chapters"):
            os.makedirs(f"{story_dir}/chapters")
        
        if not os.path.exists(f"{story_dir}/branches"):
            os.makedirs(f"{story_dir}/branches")
        
        # Create a timestamp for versioning
        self.timestamp = int(time.time())
    
    def save_story_outline(self, story_outline):
        """
        Save the story outline to a file.
        
        Args:
            story_outline (dict): The story outline to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(f"{self.story_dir}/story_outline.json", "w", encoding="utf-8") as f:
                json.dump(story_outline, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving story outline: {e}")
            return False
    
    def save_characters(self, characters):
        """
        Save character data to a file.
        
        Args:
            characters (dict): Dict with main_characters and supporting_characters lists
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(f"{self.story_dir}/characters.json", "w", encoding="utf-8") as f:
                json.dump(characters, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving characters: {e}")
            return False
    
    def save_metadata(self, metadata):
        """
        Save metadata to a file.
        
        Args:
            metadata (dict): Metadata information including genres, region, narrative_tone, etc.
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(f"{self.story_dir}/metadata.json", "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving metadata: {e}")
            return False
    
    def save_chapter(self, chapter, chapter_num):
        """
        Save a chapter to a file.
        
        Args:
            chapter (dict): The chapter data
            chapter_num (int): The chapter number
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Save as JSON
            with open(f"{self.story_dir}/chapters/chapter_{chapter_num}.json", "w", encoding="utf-8") as f:
                json.dump(chapter, f, indent=2, ensure_ascii=False)
            
            # Also save as Markdown for easy reading
            with open(f"{self.story_dir}/chapters/chapter_{chapter_num}.md", "w", encoding="utf-8") as f:
                f.write(f"# {chapter.get('title', f'Chapter {chapter_num}')}\n\n")
                f.write(chapter.get('content', 'Content not available.'))
            
            return True
        except Exception as e:
            print(f"Error saving chapter {chapter_num}: {e}")
            return False
    
    def save_branch(self, branch, decision_point_id, choice_id):
        """
        Save a story branch to a file.
        
        Args:
            branch (dict): The branch data
            decision_point_id (str): ID of the decision point
            choice_id (str): ID of the choice
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create branches directory if it doesn't exist
            branch_dir = f"{self.story_dir}/branches/{decision_point_id}"
            if not os.path.exists(branch_dir):
                os.makedirs(branch_dir)
            
            # Save as JSON
            with open(f"{branch_dir}/{choice_id}.json", "w", encoding="utf-8") as f:
                json.dump(branch, f, indent=2, ensure_ascii=False)
            
            # Also save as Markdown for easy reading
            with open(f"{branch_dir}/{choice_id}.md", "w", encoding="utf-8") as f:
                f.write(f"# {branch.get('title', f'Branch for {choice_id}')}\n\n")
                f.write(branch.get('content', 'Content not available.'))
            
            return True
        except Exception as e:
            print(f"Error saving branch for choice {choice_id}: {e}")
            return False
    
    def load_story_outline(self):
        """
        Load the story outline from a file.
        
        Returns:
            dict: The story outline, or None if not found
        """
        try:
            with open(f"{self.story_dir}/story_outline.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading story outline: {e}")
            return None
    
    def load_characters(self):
        """
        Load character data from a file.
        
        Returns:
            dict: Dict with main_characters and supporting_characters lists, or None if not found
        """
        try:
            with open(f"{self.story_dir}/characters.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading characters: {e}")
            return None
    
    def load_metadata(self):
        """
        Load metadata from a file.
        
        Returns:
            dict: Metadata information, or None if not found
        """
        try:
            with open(f"{self.story_dir}/metadata.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading metadata: {e}")
            return None
    
    def load_chapter(self, chapter_num):
        """
        Load a chapter from a file.
        
        Args:
            chapter_num (int): The chapter number
            
        Returns:
            dict: The chapter data, or None if not found
        """
        try:
            with open(f"{self.story_dir}/chapters/chapter_{chapter_num}.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading chapter {chapter_num}: {e}")
            return None
    
    def load_branch(self, decision_point_id, choice_id):
        """
        Load a story branch from a file.
        
        Args:
            decision_point_id (str): ID of the decision point
            choice_id (str): ID of the choice
            
        Returns:
            dict: The branch data, or None if not found
        """
        try:
            with open(f"{self.story_dir}/branches/{decision_point_id}/{choice_id}.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading branch for choice {choice_id}: {e}")
            return None
    
    def export_full_story(self, interactive=False):
        """
        Export the entire story as a single markdown file.
        
        Args:
            interactive (bool): Whether to include interactivity notes
            
        Returns:
            str: Path to the exported file, or None if failed
        """
        try:
            story_outline = self.load_story_outline()
            if not story_outline:
                return None
            
            title = story_outline.get("title", "Untitled Story")
            export_path = f"{self.story_dir}/{title.replace(' ', '_')}_full.md"
            
            with open(export_path, "w", encoding="utf-8") as f:
                # Write title and metadata
                f.write(f"# {title}\n\n")
                f.write(f"*{story_outline.get('setting', '')}*\n\n")
                f.write(f"**Theme**: {story_outline.get('theme', '')}\n\n")
                
                # Add genre and narrative information if available
                metadata = self.load_metadata()
                if metadata:
                    # Genres
                    if "genres" in metadata:
                        genres_str = ", ".join(metadata.get("genres", []))
                        f.write(f"**Genres**: {genres_str}\n\n")
                    
                    # Narrative details
                    narrative_details = []
                    if "narrative_tone" in metadata:
                        narrative_details.append(f"Tone: {metadata['narrative_tone']}")
                    if "narrative_pacing" in metadata:
                        narrative_details.append(f"Pacing: {metadata['narrative_pacing']}")
                    
                    if narrative_details:
                        f.write(f"**Narrative Style**: {', '.join(narrative_details)}\n\n")
                
                f.write(f"{story_outline.get('synopsis', '')}\n\n")
                f.write("---\n\n")
                
                # Write each chapter
                chapter_files = sorted([c for c in os.listdir(f"{self.story_dir}/chapters") if c.endswith(".json")])
                
                for chapter_file in chapter_files:
                    chapter_num = int(chapter_file.split("_")[1].split(".")[0])
                    chapter = self.load_chapter(chapter_num)
                    
                    if chapter:
                        f.write(f"## Chapter {chapter_num}: {chapter.get('title', '')}\n\n")
                        f.write(f"{chapter.get('content', '')}\n\n")
                        
                        if interactive:
                            f.write("\n*Decision points would appear here in the interactive version.*\n\n")
                    
                    f.write("---\n\n")
            
            return export_path
        except Exception as e:
            print(f"Error exporting full story: {e}")
            return None
            
    def export_audiobook_script(self):
        """
        Export the story in a format optimized for audiobook narration.
        
        Returns:
            str: Path to the exported script file, or None if failed
        """
        try:
            story_outline = self.load_story_outline()
            if not story_outline:
                return None
                
            title = story_outline.get("title", "Untitled Story")
            export_path = f"{self.story_dir}/{title.replace(' ', '_')}_audiobook.txt"
            
            # Load metadata to get additional story information
            metadata = self.load_metadata()
            genres = metadata.get("genres", []) if metadata else []
            
            with open(export_path, "w", encoding="utf-8") as f:
                # Write audiobook header
                f.write(f"AUDIOBOOK SCRIPT: {title}\n")
                f.write(f"{'=' * 50}\n\n")
                
                # Write narration notes
                f.write("NARRATION NOTES:\n")
                f.write("- This story combines elements of " + ", ".join(genres) + "\n")
                
                # Add narrative context from metadata
                if metadata:
                    # Region
                    f.write(f"- Set in {metadata.get('region', 'India')}\n")
                    
                    # Narrative tone and pacing
                    if "narrative_tone" in metadata:
                        f.write(f"- Narrative Tone: {metadata['narrative_tone']}\n")
                    if "narrative_pacing" in metadata:
                        f.write(f"- Narrative Pacing: {metadata['narrative_pacing']}\n")
                
                f.write("- Pronunciation guide included with character names\n\n")
                f.write(f"{'=' * 50}\n\n")
                
                # Write introduction
                f.write("INTRODUCTION:\n")
                f.write(f"[NARRATOR, CALM VOICE] {title}.\n\n")
                f.write(f"[PAUSE 2s]\n\n")
                f.write(f"[NARRATOR] {story_outline.get('synopsis', '')}\n\n")
                f.write(f"{'=' * 50}\n\n")
                
                # Load character information for pronunciation guide
                characters_data = self.load_characters()
                if characters_data:
                    f.write("CHARACTER PRONUNCIATION GUIDE:\n")
                    if "main_characters" in characters_data:
                        for char in characters_data["main_characters"]:
                            f.write(f"- {char.get('name', 'Unknown')}: [Standard pronunciation]\n")
                    f.write("\n")
                
                # Write each chapter
                chapter_files = sorted([c for c in os.listdir(f"{self.story_dir}/chapters") if c.endswith(".json")])
                
                for chapter_file in chapter_files:
                    chapter_num = int(chapter_file.split("_")[1].split(".")[0])
                    chapter = self.load_chapter(chapter_num)
                    
                    if chapter:
                        # Format chapter header for audio
                        f.write(f"CHAPTER {chapter_num}: {chapter.get('title', '')}\n")
                        f.write(f"{'=' * 50}\n\n")
                        
                        # Chapter introduction
                        f.write(f"[NARRATOR] Chapter {chapter_num}. {chapter.get('title', '')}\n\n")
                        f.write(f"[PAUSE 1s]\n\n")
                        
                        # Process content for better audio narration
                        content = chapter.get('content', '')
                        
                        # Split into paragraphs
                        paragraphs = content.split('\n\n')
                        
                        for para in paragraphs:
                            if para.strip():
                                # Check if paragraph is dialogue
                                if '"' in para or '"' in para:
                                    # Format dialogue with speaker cues
                                    f.write(f"[DIALOGUE] {para}\n\n")
                                else:
                                    # Format narration
                                    f.write(f"[NARRATOR] {para}\n\n")
                        
                        f.write(f"[PAUSE 2s]\n\n")
                        f.write(f"{'=' * 50}\n\n")
            
            return export_path
        except Exception as e:
            print(f"Error exporting audiobook script: {e}")
            return None
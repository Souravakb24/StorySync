"""
Context management module for maintaining story state and providing
relevant context between chapters.
python_file: context_manager.py
"""

from config.settings import MAX_CONTEXT_ITEMS, CRITICAL_CONTEXT_WEIGHT

class ContextManager:
    """Manages context window and summarization for story generation."""
    
    def __init__(self):
        """Initialize the ContextManager class."""
        self.context_points = []  # List of context points with metadata
        self.chapter_summaries = {}  # Dictionary of chapter summaries keyed by chapter number
    
    def update_with_chapter(self, chapter, chapter_num):
        """
        Update the context manager with information from a newly generated chapter.
        
        Args:
            chapter (dict): The chapter data including content and metadata
            chapter_num (int): The chapter number
        """
        # Store the chapter summary
        self.chapter_summaries[chapter_num] = {
            "title": chapter.get("title", f"Chapter {chapter_num}"),
            "summary": chapter.get("summary", "No summary available."),
            "key_events": chapter.get("key_events", [])
        }
        
        # Extract key events as context points
        key_events = chapter.get("key_events", [])
        # Handle if key_events is returned as a string instead of a list
        if isinstance(key_events, str):
            key_events = [key_events] if key_events else []
            
        for event in key_events:
            self.add_context_point(
                content=event,
                chapter=chapter_num,
                importance="high" if "critical" in event.lower() or "important" in event.lower() else "medium",
                context_type="event"
            )
        
        # Extract character development as context points
        character_dev = chapter.get("character_development", "")
        if isinstance(character_dev, str) and character_dev:
            self.add_context_point(
                content=character_dev,
                chapter=chapter_num,
                importance="high",
                context_type="character_development"
            )
        elif isinstance(character_dev, list):
            for dev in character_dev:
                self.add_context_point(
                    content=dev,
                    chapter=chapter_num,
                    importance="high",
                    context_type="character_development"
                )
        
        # Extract next chapter hooks as context points
        next_chapter_hooks = chapter.get("next_chapter_hooks", [])
        # Handle if next_chapter_hooks is returned as a string instead of a list
        if isinstance(next_chapter_hooks, str):
            next_chapter_hooks = [next_chapter_hooks] if next_chapter_hooks else []
            
        for hook in next_chapter_hooks:
            self.add_context_point(
                content=hook,
                chapter=chapter_num,
                importance="high",
                context_type="hook"
            )
        
        # Prune context if needed
        self._prune_context()
    
    def add_context_point(self, content, chapter, importance="medium", context_type="general"):
        """
        Add a context point to the manager.
        
        Args:
            content (str): The content of the context point
            chapter (int): The chapter number this context point is from
            importance (str): Importance level (low, medium, high, critical)
            context_type (str): Type of context (event, character_development, hook, etc.)
        """
        # Calculate weight based on importance
        weight_map = {
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": CRITICAL_CONTEXT_WEIGHT
        }
        weight = weight_map.get(importance.lower(), 2)
        
        # Add context point
        self.context_points.append({
            "content": content,
            "chapter": chapter,
            "importance": importance,
            "type": context_type,
            "weight": weight
        })
    
    def get_context_for_chapter(self, chapter_num):
        """
        Get relevant context for generating a specific chapter.
        
        Args:
            chapter_num (int): The chapter number to get context for
            
        Returns:
            dict: Organized context for chapter generation
        """
        # If this is the first chapter, return empty context
        if chapter_num == 1:
            return {
                "previous_chapters": [],
                "key_events": [],
                "character_developments": [],
                "open_hooks": []
            }
        
        # Get previous chapter summaries
        previous_chapters = []
        for i in range(1, chapter_num):
            if i in self.chapter_summaries:
                previous_chapters.append(self.chapter_summaries[i])
        
        # Filter and sort context points
        relevant_points = [point for point in self.context_points if point["chapter"] < chapter_num]
        
        # Sort by weight (most important first)
        relevant_points.sort(key=lambda x: (x["weight"], x["chapter"]), reverse=True)
        
        # Organize context by type
        key_events = [point["content"] for point in relevant_points if point["type"] == "event"]
        character_developments = [point["content"] for point in relevant_points if point["type"] == "character_development"]
        open_hooks = [point["content"] for point in relevant_points if point["type"] == "hook"]
        
        # Limit to most important items
        key_events = key_events[:MAX_CONTEXT_ITEMS]
        character_developments = character_developments[:MAX_CONTEXT_ITEMS]
        open_hooks = open_hooks[:MAX_CONTEXT_ITEMS]
        
        return {
            "previous_chapters": previous_chapters,
            "key_events": key_events,
            "character_developments": character_developments,
            "open_hooks": open_hooks
        }
    
    def _prune_context(self):
        """
        Prune the context points if there are too many, keeping the most important ones.
        """
        if len(self.context_points) > MAX_CONTEXT_ITEMS * 3:
            # Sort by weight (most important first)
            self.context_points.sort(key=lambda x: (x["weight"], x["chapter"]), reverse=True)
            
            # Keep only the top items
            self.context_points = self.context_points[:MAX_CONTEXT_ITEMS * 2]
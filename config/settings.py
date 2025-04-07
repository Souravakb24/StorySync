"""
Configuration settings for the interactive story generator.
python: settings.py
"""

# OpenAI API Configuration
OPENAI_API_KEY = "your_openaiapi_key"  # Replace with your actual API key
DEFAULT_MODEL = "gpt-4o"
TEMPERATURE = 0.7
MAX_TOKENS = 4000

# LangChain Configuration
VERBOSE = True

# Story Configuration
DEFAULT_CHAPTERS = 10
MAX_CHOICES_PER_DECISION = 3
DEFAULT_LANGUAGE = "English"

# Cultural Context Configuration
DEFAULT_REGION = "North India"  # Options: North India, South India, East India, West India, Central India
CULTURAL_DEPTH = "Deep"  # Options: Light, Moderate, Deep

# Context Management
MAX_CONTEXT_ITEMS = 15  # Maximum number of outline points to retain
CRITICAL_CONTEXT_WEIGHT = 3  # Weight multiplier for critical context points

# Paths
DATA_DIR = "data"
OUTPUT_DIR = "output"
TEMPLATES_DIR = f"{DATA_DIR}/story_templates"
CULTURAL_DIR = f"{DATA_DIR}/cultural_elements"

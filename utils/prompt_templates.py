"""
Prompt templates for story generation with an Indian cultural perspective and multi-genre integration.
Optimized for 15-20 minute reading time per chapter.
Supports response generation in Hindi language for authentic Hindi stories.
"""

# Story Foundation Prompt
STORY_FOUNDATION_PROMPT = """
You are a master storyteller specializing in creating narratives with authentic Indian cultural elements and genre expertise.

Goal:
Generate a comprehensive story outline based on the following concept:
"{plot_concept}"

The story should be set in {region}
The story will have a {narrative_tone} tone and {narrative_pacing} pacing
The story should blend elements from these genres: {genres}
Each chapter should provide 15-20 minutes of reading content (approximately 2,500-3,500 words)

Context dump:
Your outline should highlight authentic Indian cultural elements, traditions, values, and perspectives while incorporating the selected genres. Consider the following aspects:
- Regional customs, traditions, and festivals specific to {region}
- Social structures and family dynamics in Indian society
- Cultural values and philosophies that inform character motivations
- Local language expressions and communication styles
- Narrative tone and pacing implications on story structure
- Connection to Indian mythology, folklore, or religious traditions where appropriate
- Authentic representation of Indian settings, food, clothing, and daily life
- Genre conventions, tropes, and narrative structures appropriate to {genres}
- How to effectively blend multiple genres when applicable
- Ways to make genre elements culturally authentic to the Indian context

For each genre, consider these elements through the lens of the {narrative_tone} tone and {narrative_pacing} pacing:
- Romance: Relationship dynamics influenced by Indian family structures, cultural expectations around love and marriage
- Mystery: Investigation methods reflecting Indian social hierarchies, cultural secrets, historical mysteries
- Adventure: Journeys through diverse Indian landscapes, cultural quests, historical expeditions
- Historical Fiction: Accurate portrayal of historical events, social movements, cultural transitions
- Fantasy/Mythology: Integration of Indian mythological elements, regional folklore, magical systems based on cultural beliefs
- Drama: Family dynamics, social conflicts, cultural tensions specific to Indian society
- Comedy: Humor reflecting Indian sensibilities, cultural misunderstandings, societal quirks
- Thriller: Tensions arising from cultural conflicts, contemporary Indian settings

Return Format:
{format_instructions}

Language:
hindi

Warnings:
Ensure cultural authenticity and avoid stereotypical representations.
Balance genre elements with cultural authenticity.
Outline should support 15-20 minute reading time per chapter.
If language is set to "hindi", respond entirely in Hindi using Devanagari script.
"""

# Chapter Outline Prompt
CHAPTER_OUTLINE_PROMPT = """
You are a master storyteller specializing in creating narratives with authentic Indian cultural elements and genre expertise.

Goal:
Create a detailed chapter-by-chapter outline for a {num_chapters}-chapter story set in {region} 
The story will have a {narrative_tone} tone and {narrative_pacing} pacing
The story should blend elements from these genres: {genres}
Each chapter should provide 15-20 minutes of reading content (approximately 2,500-3,500 words)

Context dump:
Using the following story outline:
```
{story_outline}
```

For each chapter, provide:
1. A chapter title reflecting the {narrative_tone} tone
2. A summary of the main events aligned with {narrative_pacing} progression
3. Key plot points in bullet form (minimum 5-7 substantial plot points per chapter)
4. Characters involved in this chapter
5. Setting details specific to this chapter
6. Indian cultural elements to incorporate
7. Genre elements to incorporate from {genres}
8. Estimated word count (aim for 2,500-3,500 words)
9. Key dialogue moments or exchanges to include
10. Sensory details to emphasize for immersion

Ensure the chapter outline builds a coherent narrative arc with rising action, climax, and resolution. Each chapter should advance the plot while incorporating authentic Indian cultural elements and genre conventions in a balanced way.

Keep in mind the {narrative_tone} tone and {narrative_pacing} pacing in:
- Regional customs, traditions, and festivals specific to {region}
- Cultural values and philosophies that inform character motivations and decisions
- Local language expressions and communication styles
- Connection to Indian mythology, folklore, or religious traditions where appropriate
- Authentic representation of Indian settings, food, clothing, and daily life
- Genre-specific narrative patterns and elements from {genres}
- How to balance multiple genres within each chapter when applicable
- Strategic progression of genre elements throughout the story arc

For multi-genre stories, consider:
- How to introduce and develop each genre element throughout the narrative
- Which chapters should emphasize which genres
- How genre elements can complement Indian cultural elements
- Creating a balanced pace reflecting the {narrative_pacing} style
- Strategic placement of genre-specific milestones (romance scenes, mystery reveals, adventure challenges)

Return Format:
{format_instructions}

Language:
hindi

Warnings:
Maintain consistency with the story outline and ensure cultural authenticity.
Balance genre elements with {narrative_tone} tone and {narrative_pacing} pacing.
Plan for 15-20 minutes of reading time per chapter.
If language is set to "hindi", respond entirely in Hindi using Devanagari script.
"""

# Main Characters Prompt
MAIN_CHARACTERS_PROMPT = """
You are a master storyteller specializing in creating authentic Indian characters with depth and cultural authenticity, suited to specific genres.

Goal:
Create {num_characters} main characters for a story set in {region} 
The story has a {narrative_tone} tone with {narrative_pacing} pacing
The story blends elements from these genres: {genres}
Each chapter will provide 15-20 minutes of reading content

Context dump:
Based on the following story outline:
```
{story_outline}
```

For each character, provide:
1. Name (authentic to the region and narrative context)
2. Age
3. Gender
4. Detailed background (birthplace, family, cultural context)
5. Physical appearance description
6. Personality traits aligned with {narrative_tone} tone
7. Primary motivations and desires
8. Personal and narrative goals
9. Internal and external conflicts
10. Character arc throughout the story
11. Specific cultural traits relevant to their Indian background
12. Speech patterns including use of Indian expressions
13. Relationships with other characters
14. Genre archetype(s) the character represents
15. How the character embodies elements from the selected genres
16. Unique quirks or habits that can be referenced throughout the story
17. Voice characteristics and verbal tics to maintain consistency

Ensure the characters:
- Reflect authentic Indian cultural values specific to {region}
- Have names appropriate to their background
- Demonstrate cultural authenticity in their motivations
- Embody the diversity of Indian society
- Connect to Indian traditions in meaningful ways
- Show realistic cultural traits
- Fulfill or subvert genre archetypes authentically
- Align with the {narrative_tone} tone and {narrative_pacing} pacing
- Have sufficient depth to sustain 15-20 minute chapters

For multi-genre stories, consider:
- How each character might bridge multiple genres
- Which genre archetype each character primarily represents
- How Indian cultural elements influence genre character types
- Creating a balanced cast that serves all story genres

Return Format:
{format_instructions}

Language:
hindi

Warnings:
Avoid stereotypical characterizations.
Balance genre archetypes with cultural authenticity.
Develop characters with sufficient complexity for 15-20 minute chapters.
If language is set to "hindi", respond entirely in Hindi using Devanagari script.
"""

# Supporting Characters Prompt
SUPPORTING_CHARACTERS_PROMPT = """
You are a master storyteller specializing in creating authentic Indian characters with depth and cultural authenticity, suited to specific genres.

Goal:
Create {num_characters} supporting characters for a story set in {region}
The story has a {narrative_tone} tone with {narrative_pacing} pacing
The story blends elements from these genres: {genres}
Each chapter will provide 15-20 minutes of reading content

Context dump:
Based on the following story outline and main characters:
```
Story Outline: {story_outline}

Main Characters: {main_characters}
```

These supporting characters should complement the main characters and serve specific roles in the narrative. Consider including:
- Family members
- Friends and allies
- Rivals or antagonists
- Mentors or guides
- Community members
- Authority figures
- Genre-specific supporting roles

For each supporting character, provide:
1. Name (authentic to the region)
2. Role in the story
3. Relationship to main characters
4. Brief background and personality
5. Cultural background specific to {region}
6. How they influence the plot
7. Genre-specific function they serve
8. How they contribute to the story's genre elements
9. Distinct speech patterns or expressions
10. Chapter(s) in which they appear prominently
11. Key scenes or interactions they participate in

Ensure the characters:
- Reflect authentic Indian cultural values specific to {region}
- Have names appropriate to their background
- Represent the diversity of Indian society
- Embody authentic cultural traits
- Fulfill genre-specific supporting roles
- Align with the {narrative_tone} tone and {narrative_pacing} pacing
- Have sufficient depth for their role in 15-20 minute chapters

For multi-genre stories, consider:
- Supporting characters who bridge multiple genres
- How to balance the supporting cast to serve all genres
- Characters who might subvert genre expectations
- How characters fit into the {narrative_tone} narrative tone

Return Format:
{format_instructions}

Language:
hindi

Warnings:
Ensure supporting characters have meaningful roles.
Maintain cultural authenticity.
Develop characters with appropriate complexity for 15-20 minute chapters.
If language is set to "hindi", respond entirely in Hindi using Devanagari script.
"""

# Chapter Generation Prompt
CHAPTER_GENERATION_PROMPT = """
You are a master storyteller specializing in creating narratives with authentic Indian cultural elements and genre expertise.

Goal:
Generate Chapter {chapter_num} of a story based on the provided outline and context.
Produce 3,500-4,500 words (30-35 minutes reading time).

Context dump:
The story is set in {region}
Narrative Tone: {narrative_tone}
Narrative Pacing: {narrative_pacing}
Genres: {genres}

Chapter Outline:
```
{chapter_outline}
```

Story Outline:
```
{story_outline}
```

Characters:
```
Main Characters: {main_characters}
Supporting Characters: {supporting_characters}
```

Previous Chapter Context:
```
{previous_context}
```

Your chapter should:
1. Follow the outlined plot points
2. Develop characters through dialogue and actions
3. Incorporate authentic Indian cultural elements
4. Use narrative tone and pacing strategically
5. Include rich sensory details of settings
6. Use natural dialogue reflecting Indian speech patterns
7. Reference appropriate customs and traditions
8. Maintain narrative consistency
9. Advance character arcs and plot development
10. Incorporate genre elements from {genres}
11. Include 5-7 substantial scenes
12. Feature at least 3-4 meaningful dialogue exchanges
13. Incorporate 2-3 cultural references or practices authentically
14. Provide descriptive immersion through all five senses
15. Create natural chapter breaks and transitions

Cultural and Narrative Considerations:
- Reflect {narrative_tone} tone throughout the chapter
- Maintain {narrative_pacing} narrative progression
- Highlight regional characteristics of {region}
- Balance multiple genre elements
- Create authentic cultural interactions
- Develop enough content for 15-20 minutes of reading

Return Format:
{format_instructions}

Language:
hindi

Warnings:
Maintain consistency with previous chapters.
Balance genre conventions with cultural authenticity.
Ensure 15-20 minutes reading length (3,500-4,500 words).
If language is set to "hindi", respond entirely in Hindi using Devanagari script.
"""

# Decision Points Prompt
DECISION_POINTS_PROMPT = """
You are a master storyteller creating interactive narratives with authentic Indian cultural elements.

Goal:
Create {num_decisions} meaningful decision points for the chapter.
Each decision point should support potential branches of 15-20 minutes reading time.

Context:
Chapter Content: {chapter_content}
Region: {region}
Narrative Tone: {narrative_tone}
Narrative Pacing: {narrative_pacing}
Genres: {genres}

For each decision point:
1. Identify a meaningful choice moment
2. Describe the context in detail
3. Provide 2-3 distinct choices
4. Describe immediate consequences
5. Indicate which genre(s) each choice advances
6. Explain how each choice aligns with or challenges Indian cultural norms
7. Suggest how each choice could sustain a 15-20 minute branch

Decision Guidelines:
- Rooted in Indian cultural contexts
- Reflect realistic choices in {region}
- Consider cultural values and social expectations
- Advance genre elements meaningfully
- Align with {narrative_tone} tone
- Consistent with {narrative_pacing} progression
- Substantial enough to generate 15-20 minutes of content

Narrative Considerations:
- How choices reflect cultural nuances
- Potential genre pivots
- Impact on character development
- Maintaining story coherence
- Sufficient complexity for extended reading time

Return Format:
{format_instructions}

Language:
hindi

Warnings:
Ensure decisions are meaningful and culturally authentic.
Design decision points that can support 15-20 minute branches.
If language is set to "hindi", respond entirely in Hindi using Devanagari script.
"""

# Branch Generation Prompt
BRANCH_GENERATION_PROMPT = """
You are a master storyteller creating narrative branches with cultural authenticity.

Goal:
Generate a story branch based on a specific decision point.
Produce 3,500-4,500 words (15-20 minutes reading time).

Context:
Chapter Content: {chapter_content}
Decision Point: {decision_point}
Selected Choice: {selected_choice}
Region: {region}
Narrative Tone: {narrative_tone}
Narrative Pacing: {narrative_pacing}
Genres: {genres}

Story Context:
```
Story Outline: {story_outline}
Main Characters: {main_characters}
```

Branch Requirements:
1. Continue narrative from decision point
2. Show realistic cultural consequences
3. Impact character relationships
4. Incorporate {region} cultural elements
5. Include culturally appropriate reactions
6. Establish story continuation hooks
7. Develop genre elements
8. Potentially shift genre emphasis
9. Include 4-6 substantial scenes
10. Feature at least 3 meaningful dialogue exchanges
11. Incorporate 2-3 cultural references or practices
12. Provide descriptive immersion through all five senses

Cultural Considerations:
- Social structure implications
- Cultural values and expectations
- Societal perspectives on the choice
- Regional customs and traditions relevant to the branch

Genre Considerations:
- Alignment with genre expectations
- Emphasized genre elements
- Cultural transformation of genre developments
- Maintaining genre coherence

Return Format:
{format_instructions}

Language:
hindi

Warnings:
Maintain branch consistency and cultural authenticity.
Balance genre development with cultural context.
Ensure 15-20 minutes reading length (3,500-4,500 words).
If language is set to "hindi", respond entirely in Hindi using Devanagari script.
"""

# Export the prompts for use in other modules
__all__ = [
    'STORY_FOUNDATION_PROMPT',
    'CHAPTER_OUTLINE_PROMPT',
    'MAIN_CHARACTERS_PROMPT',
    'SUPPORTING_CHARACTERS_PROMPT',
    'CHAPTER_GENERATION_PROMPT',
    'DECISION_POINTS_PROMPT',
    'BRANCH_GENERATION_PROMPT'
]
# Writer Text Editor

A specialized text editor library designed for fiction writers with focus on distraction-free writing and narrative management.

## Features

- **Focus Mode**: Isolate and highlight the current paragraph or sentence while visually de-emphasizing surrounding content.
- **Writing Statistics Tracking**: Track word count, reading level metrics, and writing pace over time.
- **Character and Plot Element Tracking**: Identify and track character names and key terms across chapters or sections.
- **Non-linear Document Navigation**: Organize document by narrative elements rather than simple linear text.
- **Revision Marking with Draft Comparison**: Maintain multiple drafts of the same document with the ability to compare and selectively merge changes.

## Installation

```bash
pip install writer-text-editor
```

## Usage

```python
from writer_text_editor import Document

# Create a new document
doc = Document("My Novel")

# Add content to the document
doc.add_content("Chapter 1: The Beginning\n\nOnce upon a time...")

# Use focus mode
focus = doc.enter_focus_mode(position=15)  # Focus on the paragraph at position 15
focus.edit("Once upon a time in a land far away...")  # Edit the focused paragraph

# Get writing statistics
stats = doc.get_statistics()
print(f"Word count: {stats.word_count}")
print(f"Reading level: {stats.reading_level}")

# Track characters
characters = doc.track_elements()
print(f"Characters found: {', '.join(characters.names)}")

# Use non-linear navigation
navigation = doc.get_navigation()
chapter_2 = navigation.get_section("Chapter 2")
scene_3 = navigation.get_element("Scene 3")

# Manage revisions
doc.create_revision("Added more description")
new_draft = doc.get_revision("Added more description")
diff = doc.compare_revisions("Original", "Added more description")
```

## License

MIT
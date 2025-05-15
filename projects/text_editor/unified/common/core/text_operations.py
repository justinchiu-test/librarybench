"""
Text operations module for text analysis and manipulation.

This module provides utility functions for text processing, analysis,
and manipulation that are common across different text editor implementations.
"""

import re
from typing import Dict, List, Optional, Tuple, Set, Any


def count_words(text: str) -> int:
    """
    Count the number of words in a text.

    Args:
        text: The text to analyze

    Returns:
        The number of words
    """
    return len(re.findall(r"\b\w+\b", text))


def count_lines(text: str) -> int:
    """
    Count the number of lines in a text.

    Args:
        text: The text to analyze

    Returns:
        The number of lines
    """
    return text.count("\n") + 1


def count_characters(text: str, include_whitespace: bool = True) -> int:
    """
    Count the number of characters in a text.

    Args:
        text: The text to analyze
        include_whitespace: Whether to include whitespace characters in the count

    Returns:
        The number of characters
    """
    if include_whitespace:
        return len(text)
    else:
        return len(re.sub(r"\s", "", text))


def extract_sentences(text: str) -> List[str]:
    """
    Extract sentences from a text.

    Args:
        text: The text to analyze

    Returns:
        A list of sentences
    """
    # This is a simplified implementation and may not handle all edge cases
    return re.split(r"(?<=[.!?])\s+", text)


def calculate_reading_time(text: str, words_per_minute: int = 200) -> float:
    """
    Calculate the estimated reading time for a text.

    Args:
        text: The text to analyze
        words_per_minute: The average reading speed in words per minute

    Returns:
        The estimated reading time in minutes
    """
    word_count = count_words(text)
    return word_count / words_per_minute


def calculate_reading_level(text: str) -> Dict[str, float]:
    """
    Calculate various readability metrics for a text.

    Args:
        text: The text to analyze

    Returns:
        A dictionary with readability metrics
    """
    # Calculate basic statistics
    sentences = extract_sentences(text)
    sentence_count = len(sentences)
    word_count = count_words(text)
    character_count = count_characters(text, include_whitespace=False)

    if sentence_count == 0 or word_count == 0:
        return {
            "flesch_reading_ease": 0.0,
            "flesch_kincaid_grade": 0.0,
            "avg_words_per_sentence": 0.0,
            "avg_characters_per_word": 0.0,
        }

    # Calculate averages
    avg_words_per_sentence = word_count / sentence_count
    avg_characters_per_word = character_count / word_count

    # Flesch Reading Ease score
    flesch_reading_ease = (
        206.835
        - (1.015 * avg_words_per_sentence)
        - (84.6 * avg_characters_per_word / 5)
    )
    flesch_reading_ease = max(0, min(100, flesch_reading_ease))  # Clamp to 0-100

    # Flesch-Kincaid Grade Level
    flesch_kincaid_grade = (
        (0.39 * avg_words_per_sentence) + (11.8 * avg_characters_per_word / 5) - 15.59
    )
    flesch_kincaid_grade = max(0, flesch_kincaid_grade)  # Ensure non-negative

    return {
        "flesch_reading_ease": flesch_reading_ease,
        "flesch_kincaid_grade": flesch_kincaid_grade,
        "avg_words_per_sentence": avg_words_per_sentence,
        "avg_characters_per_word": avg_characters_per_word,
    }


def find_repeated_words(text: str) -> Dict[str, int]:
    """
    Find repeated words in a text.

    Args:
        text: The text to analyze

    Returns:
        A dictionary with words and their frequency
    """
    words = re.findall(r"\b\w+\b", text.lower())
    word_count = {}

    for word in words:
        if len(word) > 3:  # Skip short words
            word_count[word] = word_count.get(word, 0) + 1

    # Return only words that appear more than once
    return {word: count for word, count in word_count.items() if count > 1}


def extract_potential_entities(text: str) -> Dict[str, List[int]]:
    """
    Extract potential named entities from a text with their positions.

    Args:
        text: The text to analyze

    Returns:
        A dictionary with entity names and lists of their positions
    """
    # Find capitalized words that are likely names or entities
    # This is a simplified approach and would be more sophisticated in practice
    entity_matches = re.finditer(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", text)

    entities = {}
    for match in entity_matches:
        entity = match.group(0)
        position = match.start()

        if entity not in entities:
            entities[entity] = []

        entities[entity].append(position)

    return entities


def indent_text(text: str, spaces: int = 4) -> str:
    """
    Indent each line of a text by a specified number of spaces.

    Args:
        text: The text to indent
        spaces: The number of spaces to indent by

    Returns:
        The indented text
    """
    indent = " " * spaces
    return indent + text.replace("\n", "\n" + indent)


def format_text_as_code(text: str, language: str = "python") -> str:
    """
    Format text as code for a specific language.

    This is a simple implementation that just adds appropriate
    indentation and spacing. A more sophisticated implementation
    would use a language-specific formatter.

    Args:
        text: The text to format
        language: The programming language

    Returns:
        The formatted text
    """
    # This is a very simplified implementation
    if language in ("python", "ruby"):
        # These languages use 4-space indentation by convention
        lines = text.split("\n")
        current_indent = 0
        result = []

        for line in lines:
            stripped = line.strip()

            # Adjust indentation based on content
            if stripped.endswith(":"):
                result.append(" " * (4 * current_indent) + stripped)
                current_indent += 1
            elif stripped in (
                "end",
                "endif",
                "endfor",
                "endwhile",
                "else:",
                "elif:",
                "except:",
                "finally:",
            ):
                current_indent = max(0, current_indent - 1)
                result.append(" " * (4 * current_indent) + stripped)
                if not stripped.endswith(":"):
                    current_indent = max(0, current_indent - 1)
            else:
                result.append(" " * (4 * current_indent) + stripped)

        return "\n".join(result)

    # For other languages, just return the text with normalized spacing
    return "\n".join(line.strip() for line in text.split("\n"))


def wrap_text(text: str, width: int = 80) -> str:
    """
    Wrap text to a specified width.

    Args:
        text: The text to wrap
        width: The maximum width of each line

    Returns:
        The wrapped text
    """
    # Split text into paragraphs
    paragraphs = text.split("\n\n")
    wrapped_paragraphs = []

    for paragraph in paragraphs:
        if not paragraph.strip():
            wrapped_paragraphs.append("")
            continue

        # Handle already indented text or lists
        if paragraph.startswith((" ", "\t", "* ", "- ", "1. ")):
            wrapped_paragraphs.append(paragraph)
            continue

        words = paragraph.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            if current_length + len(word) + len(current_line) <= width:
                current_line.append(word)
                current_length += len(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)

        if current_line:
            lines.append(" ".join(current_line))

        wrapped_paragraphs.append("\n".join(lines))

    return "\n\n".join(wrapped_paragraphs)

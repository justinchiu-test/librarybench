"""Text processing utilities for query language interpreters."""

import re
import unicodedata
from typing import Dict, List, Optional, Set


def normalize_text(
    text: str,
    lowercase: bool = True,
    remove_punctuation: bool = False,
    remove_whitespace: bool = False,
    remove_accents: bool = False,
) -> str:
    """Normalize text for processing.

    Args:
        text: Text to normalize
        lowercase: Whether to convert to lowercase
        remove_punctuation: Whether to remove punctuation
        remove_whitespace: Whether to remove whitespace
        remove_accents: Whether to remove accents

    Returns:
        str: Normalized text
    """
    if not text:
        return ""
    
    # Lowercase
    if lowercase:
        text = text.lower()
    
    # Remove accents
    if remove_accents:
        text = ''.join(
            c for c in unicodedata.normalize('NFKD', text)
            if not unicodedata.combining(c)
        )
    
    # Remove punctuation
    if remove_punctuation:
        text = re.sub(r'[^\w\s]', '', text)
    
    # Remove whitespace
    if remove_whitespace:
        text = re.sub(r'\s+', '', text)
    
    return text


def tokenize(
    text: str,
    lowercase: bool = True,
    keep_punctuation: bool = False,
) -> List[str]:
    """Split text into tokens.

    Args:
        text: Text to tokenize
        lowercase: Whether to convert to lowercase
        keep_punctuation: Whether to keep punctuation as separate tokens

    Returns:
        List[str]: List of tokens
    """
    if not text:
        return []
    
    # Lowercase
    if lowercase:
        text = text.lower()
    
    # Split on whitespace and punctuation
    if keep_punctuation:
        # Add spaces around punctuation
        text = re.sub(r'([^\w\s])', r' \1 ', text)
        # Split on whitespace
        tokens = text.split()
    else:
        # Split on non-word characters
        tokens = re.findall(r'\w+', text)
    
    return tokens


def find_keywords(
    text: str,
    keywords: Set[str],
    case_sensitive: bool = False,
    whole_word: bool = True,
) -> Dict[str, List[int]]:
    """Find keywords in text.

    Args:
        text: Text to search
        keywords: Keywords to find
        case_sensitive: Whether to match case
        whole_word: Whether to match whole words only

    Returns:
        Dict[str, List[int]]: Dictionary mapping keywords to positions
    """
    results = {}
    
    if not text or not keywords:
        return results
    
    # Prepare text for search
    search_text = text if case_sensitive else text.lower()
    
    for keyword in keywords:
        # Prepare keyword for search
        search_keyword = keyword if case_sensitive else keyword.lower()
        
        # Find positions
        positions = []
        
        if whole_word:
            # Match whole words only
            pattern = r'\b' + re.escape(search_keyword) + r'\b'
            for match in re.finditer(pattern, search_text):
                positions.append(match.start())
        else:
            # Match anywhere
            pos = -1
            while True:
                pos = search_text.find(search_keyword, pos + 1)
                if pos == -1:
                    break
                positions.append(pos)
        
        if positions:
            results[keyword] = positions
    
    return results


def text_distance(text1: str, text2: str) -> float:
    """Calculate normalized Levenshtein distance between two texts.

    Args:
        text1: First text
        text2: Second text

    Returns:
        float: Normalized distance (0.0 to 1.0)
    """
    if text1 == text2:
        return 0.0
    
    if not text1 or not text2:
        return 1.0
    
    # Levenshtein distance calculation
    len1, len2 = len(text1), len(text2)
    
    # Initialize distance matrix
    dp = [[0 for _ in range(len2 + 1)] for _ in range(len1 + 1)]
    
    # Fill first row and column
    for i in range(len1 + 1):
        dp[i][0] = i
    for j in range(len2 + 1):
        dp[0][j] = j
    
    # Fill the rest of the matrix
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            cost = 0 if text1[i-1] == text2[j-1] else 1
            dp[i][j] = min(
                dp[i-1][j] + 1,      # Deletion
                dp[i][j-1] + 1,      # Insertion
                dp[i-1][j-1] + cost  # Substitution
            )
    
    # Normalize distance
    max_len = max(len1, len2)
    return dp[len1][len2] / max_len if max_len > 0 else 0.0
"""
Internationalization for operations engineer CLI tools.
"""

import re
from typing import Dict, Optional


def load_translations(po_file: str) -> Dict[str, str]:
    """
    Load translations from a PO file.
    
    Args:
        po_file (str): Path to PO file.
        
    Returns:
        Dict[str, str]: Dictionary mapping message IDs to translations.
        
    Raises:
        FileNotFoundError: If the PO file does not exist.
    """
    translations = {}
    current_msgid = None
    current_msgstr = None
    
    with open(po_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Parse msgid
            if line.startswith('msgid '):
                if current_msgid is not None and current_msgstr is not None:
                    translations[current_msgid] = current_msgstr
                
                current_msgid = line[6:].strip('"')
                current_msgstr = None
            
            # Parse msgstr
            elif line.startswith('msgstr '):
                current_msgstr = line[7:].strip('"')
            
            # Skip comments and empty lines
            elif line.startswith('#') or not line:
                continue
    
    # Add the last translation
    if current_msgid is not None and current_msgstr is not None:
        translations[current_msgid] = current_msgstr
    
    return translations
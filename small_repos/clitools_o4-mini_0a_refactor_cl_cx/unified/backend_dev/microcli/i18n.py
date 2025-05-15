import os
import re

def load_translations(po_file_path):
    """
    Load translations from a PO file
    
    Args:
        po_file_path: Path to the PO file
        
    Returns:
        dict: Dictionary of msgid -> msgstr mappings
        
    Raises:
        FileNotFoundError: If the PO file doesn't exist
    """
    if not os.path.exists(po_file_path):
        raise FileNotFoundError(f"Translation file not found: {po_file_path}")
    
    translations = {}
    
    # Basic PO file parser - handles simple cases
    with open(po_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Find pairs of msgid and msgstr
    pattern = r'msgid\s+"(.+?)"\s+msgstr\s+"(.+?)"'
    matches = re.findall(pattern, content)
    
    for msgid, msgstr in matches:
        translations[msgid] = msgstr
        
    return translations

def translate(key, translations):
    """
    Translate a key using the translations dictionary
    
    Args:
        key: The key to translate
        translations: Dictionary of translations
        
    Returns:
        str: Translated text or the key itself if not found
    """
    return translations.get(key, key)
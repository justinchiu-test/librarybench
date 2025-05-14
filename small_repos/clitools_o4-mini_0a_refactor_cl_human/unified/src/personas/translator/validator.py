"""
Translation validator module.
Validates translation files and checks for common issues.
"""

import os
import re
from typing import Dict, List, Optional, Set, Tuple


class TranslationValidator:
    """
    Validates translation files and content.
    Checks for consistency, completeness, and formatting issues.
    """
    
    def __init__(self):
        """Initialize a new translation validator."""
        pass
    
    def validate_po_file(self, file_path: str) -> List[Dict[str, any]]:
        """
        Validate a PO translation file.
        
        Args:
            file_path: Path to the PO file
            
        Returns:
            List of issues found
        """
        issues = []
        
        # Check if file exists
        if not os.path.exists(file_path):
            issues.append({
                "type": "error",
                "message": f"File not found: {file_path}"
            })
            return issues
        
        try:
            # Parse PO file
            entries = self._parse_po_file(file_path)
            
            # Validate entries
            for entry in entries:
                # Check for missing translations
                if not entry.get("msgstr"):
                    issues.append({
                        "type": "warning",
                        "message": f"Missing translation for: {entry.get('msgid', '')}",
                        "line": entry.get("line_number")
                    })
                
                # Check for format string consistency
                msgid = entry.get("msgid", "")
                msgstr = entry.get("msgstr", "")
                
                if msgid and msgstr:
                    format_issues = self._check_format_strings(msgid, msgstr)
                    for issue in format_issues:
                        issues.append({
                            "type": "error",
                            "message": issue,
                            "line": entry.get("line_number")
                        })
                    
                    # Check for HTML tag consistency
                    html_issues = self._check_html_tags(msgid, msgstr)
                    for issue in html_issues:
                        issues.append({
                            "type": "error",
                            "message": issue,
                            "line": entry.get("line_number")
                        })
            
            return issues
            
        except Exception as e:
            issues.append({
                "type": "error",
                "message": f"Error parsing PO file: {str(e)}"
            })
            return issues
    
    def validate_translations(self, 
                            source_text: str, 
                            translated_text: str) -> List[str]:
        """
        Validate a translation against its source.
        
        Args:
            source_text: Source text
            translated_text: Translated text
            
        Returns:
            List of issues found
        """
        issues = []
        
        # Check for format string consistency
        format_issues = self._check_format_strings(source_text, translated_text)
        issues.extend(format_issues)
        
        # Check for HTML tag consistency
        html_issues = self._check_html_tags(source_text, translated_text)
        issues.extend(html_issues)
        
        # Check for suspicious translations
        if self._is_suspicious_translation(source_text, translated_text):
            issues.append("Translation appears to be suspicious or incorrect")
        
        return issues
    
    def check_completeness(self, 
                          file_path: str, 
                          reference_file: Optional[str] = None) -> Dict[str, any]:
        """
        Check translation completeness.
        
        Args:
            file_path: Path to the translation file
            reference_file: Path to the reference file (e.g., template)
            
        Returns:
            Completeness statistics
        """
        # Default result
        result = {
            "total": 0,
            "translated": 0,
            "untranslated": 0,
            "fuzzy": 0,
            "percent_complete": 0.0
        }
        
        try:
            # Parse PO file
            entries = self._parse_po_file(file_path)
            
            # Count entries
            result["total"] = len(entries)
            
            for entry in entries:
                if entry.get("fuzzy"):
                    result["fuzzy"] += 1
                elif entry.get("msgstr"):
                    result["translated"] += 1
                else:
                    result["untranslated"] += 1
            
            # Calculate percentage
            if result["total"] > 0:
                result["percent_complete"] = (result["translated"] / result["total"]) * 100
            
            # Check against reference if provided
            if reference_file and os.path.exists(reference_file):
                reference_entries = self._parse_po_file(reference_file)
                reference_ids = {e.get("msgid") for e in reference_entries if e.get("msgid")}
                current_ids = {e.get("msgid") for e in entries if e.get("msgid")}
                
                missing_ids = reference_ids - current_ids
                extra_ids = current_ids - reference_ids
                
                result["missing_entries"] = len(missing_ids)
                result["extra_entries"] = len(extra_ids)
            
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "total": 0,
                "translated": 0,
                "untranslated": 0,
                "fuzzy": 0,
                "percent_complete": 0.0
            }
    
    def _parse_po_file(self, file_path: str) -> List[Dict[str, any]]:
        """
        Parse a PO file into structured entries.
        
        Args:
            file_path: Path to the PO file
            
        Returns:
            List of parsed entries
        """
        entries = []
        current_entry = None
        line_number = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line_number += 1
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                
                # Skip comments
                if line.startswith('#'):
                    # Check for fuzzy flag
                    if current_entry and line == "#, fuzzy":
                        current_entry["fuzzy"] = True
                    continue
                
                # New msgid
                if line.startswith('msgid '):
                    # Save previous entry if it exists
                    if current_entry:
                        entries.append(current_entry)
                    
                    # Start new entry
                    current_entry = {
                        "msgid": line[6:].strip('"'),
                        "msgstr": "",
                        "fuzzy": False,
                        "line_number": line_number
                    }
                
                # msgstr
                elif line.startswith('msgstr ') and current_entry:
                    current_entry["msgstr"] = line[7:].strip('"')
                
                # Continuation of msgid or msgstr
                elif line.startswith('"') and current_entry:
                    # Determine if this is a msgid or msgstr continuation
                    if "msgstr_processing" in current_entry:
                        current_entry["msgstr"] += line.strip('"')
                    else:
                        current_entry["msgid"] += line.strip('"')
                
                # Start of msgstr processing
                elif line.startswith('msgstr') and current_entry:
                    current_entry["msgstr_processing"] = True
            
            # Add last entry
            if current_entry:
                entries.append(current_entry)
        
        return entries
    
    def _check_format_strings(self, source: str, translation: str) -> List[str]:
        """
        Check for format string consistency between source and translation.
        
        Args:
            source: Source text
            translation: Translated text
            
        Returns:
            List of issues found
        """
        issues = []
        
        # Check Python format strings
        python_formats_source = set(re.findall(r'%(?:\([^)]+\))?[diouxXeEfFgGcrs]', source))
        python_formats_translation = set(re.findall(r'%(?:\([^)]+\))?[diouxXeEfFgGcrs]', translation))
        
        if python_formats_source != python_formats_translation:
            missing = python_formats_source - python_formats_translation
            extra = python_formats_translation - python_formats_source
            
            if missing:
                issues.append(f"Missing Python format specifiers in translation: {', '.join(missing)}")
            if extra:
                issues.append(f"Extra Python format specifiers in translation: {', '.join(extra)}")
        
        # Check brace format strings
        brace_formats_source = set(re.findall(r'\{[^}]*\}', source))
        brace_formats_translation = set(re.findall(r'\{[^}]*\}', translation))
        
        if brace_formats_source != brace_formats_translation:
            missing = brace_formats_source - brace_formats_translation
            extra = brace_formats_translation - brace_formats_source
            
            if missing:
                issues.append(f"Missing brace format specifiers in translation: {', '.join(missing)}")
            if extra:
                issues.append(f"Extra brace format specifiers in translation: {', '.join(extra)}")
        
        return issues
    
    def _check_html_tags(self, source: str, translation: str) -> List[str]:
        """
        Check for HTML tag consistency between source and translation.
        
        Args:
            source: Source text
            translation: Translated text
            
        Returns:
            List of issues found
        """
        issues = []
        
        # Extract HTML tags
        source_tags = re.findall(r'<[^>]+>', source)
        translation_tags = re.findall(r'<[^>]+>', translation)
        
        # Simple check for tag count
        if len(source_tags) != len(translation_tags):
            issues.append(f"HTML tag count mismatch: {len(source_tags)} in source vs {len(translation_tags)} in translation")
        
        # Check for missing specific tags
        source_tags_set = set(source_tags)
        translation_tags_set = set(translation_tags)
        
        missing_tags = source_tags_set - translation_tags_set
        if missing_tags:
            issues.append(f"Missing HTML tags in translation: {', '.join(missing_tags)}")
        
        # Check for extra tags
        extra_tags = translation_tags_set - source_tags_set
        if extra_tags:
            issues.append(f"Extra HTML tags in translation: {', '.join(extra_tags)}")
        
        return issues
    
    def _is_suspicious_translation(self, source: str, translation: str) -> bool:
        """
        Check if a translation appears to be suspicious or incorrect.
        
        Args:
            source: Source text
            translation: Translated text
            
        Returns:
            True if the translation appears suspicious
        """
        # If translation is identical to source, it might be untranslated
        if source == translation and len(source) > 10:
            return True
        
        # If length ratio is very different, it might be suspicious
        source_len = len(source)
        translation_len = len(translation)
        
        if source_len > 10 and translation_len > 0:
            ratio = source_len / translation_len
            
            # Usually translations shouldn't be more than 3x longer or shorter
            if ratio > 3 or ratio < 0.33:
                return True
        
        return False


# Create a global validator for convenience
_global_validator = TranslationValidator()

def validate_po_file(file_path: str) -> List[Dict[str, any]]:
    """Validate a PO file using the global validator."""
    return _global_validator.validate_po_file(file_path)

def validate_translations(source_text: str, translated_text: str) -> List[str]:
    """Validate translations using the global validator."""
    return _global_validator.validate_translations(source_text, translated_text)

def check_completeness(file_path: str, reference_file: Optional[str] = None) -> Dict[str, any]:
    """Check translation completeness using the global validator."""
    return _global_validator.check_completeness(file_path, reference_file)
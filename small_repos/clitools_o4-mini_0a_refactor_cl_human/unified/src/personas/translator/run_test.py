"""
Translation testing module.
Runs tests on translations to ensure quality and correctness.
"""

import os
import re
import json
from typing import Any, Dict, List, Optional, Tuple, Union

from .validator import TranslationValidator


class TranslationTester:
    """
    Tests translations for quality and correctness.
    Provides automated checks for common translation issues.
    """
    
    def __init__(self):
        """Initialize a new translation tester."""
        self.validator = TranslationValidator()
    
    def run_tests(self, 
                 file_path: str, 
                 reference_file: Optional[str] = None,
                 output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Run a comprehensive test suite on a translation file.
        
        Args:
            file_path: Path to the translation file
            reference_file: Path to the reference file
            output_file: Path to save test results
            
        Returns:
            Test results
        """
        results = {
            "file": file_path,
            "reference": reference_file,
            "tests": {},
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0
            }
        }
        
        # Check if file exists
        if not os.path.exists(file_path):
            results["tests"]["file_exists"] = {
                "result": "fail",
                "message": f"File does not exist: {file_path}"
            }
            results["summary"]["total_tests"] = 1
            results["summary"]["failed"] = 1
            return results
        
        # Run validation tests
        validation_results = self._run_validation_test(file_path)
        results["tests"]["validation"] = validation_results
        
        # Run completeness test
        completeness_results = self._run_completeness_test(file_path, reference_file)
        results["tests"]["completeness"] = completeness_results
        
        # Run format tests
        format_results = self._run_format_test(file_path)
        results["tests"]["format"] = format_results
        
        # Calculate summary
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        warnings = 0
        
        for test_category, test_result in results["tests"].items():
            total_tests += 1
            if test_result["result"] == "pass":
                passed_tests += 1
            elif test_result["result"] == "fail":
                failed_tests += 1
            elif test_result["result"] == "warning":
                warnings += 1
        
        results["summary"]["total_tests"] = total_tests
        results["summary"]["passed"] = passed_tests
        results["summary"]["failed"] = failed_tests
        results["summary"]["warnings"] = warnings
        
        # Save results if requested
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    json.dump(results, f, indent=2)
            except Exception as e:
                print(f"Error saving test results: {e}")
        
        return results
    
    def check_translation(self, 
                         source: str, 
                         translation: str) -> Dict[str, Any]:
        """
        Check a single translation.
        
        Args:
            source: Source text
            translation: Translated text
            
        Returns:
            Check results
        """
        results = {
            "result": "pass",
            "issues": []
        }
        
        # Validate translation
        issues = self.validator.validate_translations(source, translation)
        
        # Check for empty translation
        if not translation:
            issues.append("Translation is empty")
        
        # Check for suspiciously similar translation
        if source == translation and len(source) > 5:
            issues.append("Translation is identical to source")
        
        # If issues found, mark as failed
        if issues:
            results["result"] = "fail"
            results["issues"] = issues
        
        return results
    
    def _run_validation_test(self, file_path: str) -> Dict[str, Any]:
        """
        Run validation test on a translation file.
        
        Args:
            file_path: Path to the translation file
            
        Returns:
            Test results
        """
        results = {
            "result": "pass",
            "issues": []
        }
        
        # Skip non-PO files for now
        if not file_path.endswith('.po'):
            results["result"] = "skipped"
            results["message"] = "Only PO files are supported for validation testing"
            return results
        
        # Validate PO file
        issues = self.validator.validate_po_file(file_path)
        
        # Count error types
        errors = [i for i in issues if i["type"] == "error"]
        warnings = [i for i in issues if i["type"] == "warning"]
        
        # Determine result
        if errors:
            results["result"] = "fail"
            results["issues"] = issues
            results["message"] = f"Found {len(errors)} errors and {len(warnings)} warnings"
        elif warnings:
            results["result"] = "warning"
            results["issues"] = issues
            results["message"] = f"Found {len(warnings)} warnings"
        else:
            results["message"] = "No issues found"
        
        return results
    
    def _run_completeness_test(self, 
                              file_path: str, 
                              reference_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Run completeness test on a translation file.
        
        Args:
            file_path: Path to the translation file
            reference_file: Path to the reference file
            
        Returns:
            Test results
        """
        results = {
            "result": "pass",
            "issues": []
        }
        
        # Skip non-PO files for now
        if not file_path.endswith('.po'):
            results["result"] = "skipped"
            results["message"] = "Only PO files are supported for completeness testing"
            return results
        
        # Check completeness
        stats = self.validator.check_completeness(file_path, reference_file)
        
        # Add stats to results
        results["stats"] = stats
        
        # Determine result
        if "error" in stats:
            results["result"] = "fail"
            results["message"] = f"Error checking completeness: {stats['error']}"
        elif stats["untranslated"] > 0 or stats["fuzzy"] > 0:
            results["result"] = "warning"
            results["message"] = f"Translation is {stats['percent_complete']:.1f}% complete ({stats['translated']}/{stats['total']})"
            
            if stats["untranslated"] > 0:
                results["issues"].append(f"{stats['untranslated']} untranslated strings")
            
            if stats["fuzzy"] > 0:
                results["issues"].append(f"{stats['fuzzy']} fuzzy strings")
            
            if reference_file and "missing_entries" in stats and stats["missing_entries"] > 0:
                results["issues"].append(f"{stats['missing_entries']} missing entries compared to reference")
        else:
            results["message"] = f"Translation is 100% complete ({stats['translated']}/{stats['total']})"
        
        return results
    
    def _run_format_test(self, file_path: str) -> Dict[str, Any]:
        """
        Run format test on a translation file.
        
        Args:
            file_path: Path to the translation file
            
        Returns:
            Test results
        """
        results = {
            "result": "pass",
            "issues": []
        }
        
        # Skip non-PO files for now
        if not file_path.endswith('.po'):
            results["result"] = "skipped"
            results["message"] = "Only PO files are supported for format testing"
            return results
        
        try:
            # Read file and check for common format issues
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for BOM
            if content.startswith('\ufeff'):
                results["issues"].append("File contains BOM (Byte Order Mark)")
            
            # Check for incorrect line endings
            if '\r\n' in content and '\n' in content.replace('\r\n', ''):
                results["issues"].append("File contains mixed line endings")
            
            # Check for trailing whitespace
            lines_with_trailing = []
            for i, line in enumerate(content.splitlines(), 1):
                if line.rstrip() != line and line.strip():
                    lines_with_trailing.append(i)
            
            if lines_with_trailing:
                results["issues"].append(f"File contains trailing whitespace on lines: " + 
                                       ", ".join(map(str, lines_with_trailing[:5])) + 
                                       ("..." if len(lines_with_trailing) > 5 else ""))
            
            # Check for non-ASCII characters in msgids
            non_ascii_msgids = []
            for match in re.finditer(r'msgid "(.*?)"', content):
                msgid = match.group(1)
                if any(ord(c) > 127 for c in msgid):
                    non_ascii_msgids.append(msgid)
            
            if non_ascii_msgids:
                results["issues"].append(f"File contains non-ASCII characters in msgids: " + 
                                       ", ".join(non_ascii_msgids[:3]) + 
                                       ("..." if len(non_ascii_msgids) > 3 else ""))
            
            # Determine result
            if results["issues"]:
                results["result"] = "warning"
                results["message"] = f"Found {len(results['issues'])} format issues"
            else:
                results["message"] = "No format issues found"
                
        except Exception as e:
            results["result"] = "fail"
            results["message"] = f"Error checking format: {str(e)}"
        
        return results


# Create a global tester for convenience
_global_tester = TranslationTester()

def run_tests(file_path: str, 
             reference_file: Optional[str] = None,
             output_file: Optional[str] = None) -> Dict[str, Any]:
    """Run tests on a translation file using the global tester."""
    return _global_tester.run_tests(file_path, reference_file, output_file)

def check_translation(source: str, translation: str) -> Dict[str, Any]:
    """Check a single translation using the global tester."""
    return _global_tester.check_translation(source, translation)
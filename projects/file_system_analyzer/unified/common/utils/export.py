"""Export utilities for file system analysis results.

This module provides utilities for exporting analysis results to various formats
including JSON, CSV, HTML, and more.
"""

import os
import json
import csv
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from pathlib import Path
from datetime import datetime

# Try to import optional dependencies
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from jinja2 import Template
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False


logger = logging.getLogger(__name__)


class ExportError(Exception):
    """Exception raised for errors during export operations."""
    pass


def ensure_directory_exists(file_path: Union[str, Path]) -> None:
    """
    Ensure the directory for a file path exists.
    
    Args:
        file_path: Path to a file
    """
    path = Path(file_path)
    directory = path.parent
    
    if not directory.exists():
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ExportError(f"Failed to create directory {directory}: {e}")


def dict_to_json(data: Dict[str, Any], pretty: bool = True) -> str:
    """
    Convert a dictionary to a JSON string.
    
    Args:
        data: Dictionary to convert
        pretty: Whether to pretty-print the JSON
        
    Returns:
        JSON string representation of the dictionary
    """
    try:
        if pretty:
            return json.dumps(data, indent=2, default=str, sort_keys=True)
        else:
            return json.dumps(data, default=str)
    except Exception as e:
        raise ExportError(f"Failed to convert data to JSON: {e}")


def export_to_json(
    data: Dict[str, Any], 
    file_path: Union[str, Path],
    pretty: bool = True
) -> str:
    """
    Export data to a JSON file.
    
    Args:
        data: Data to export
        file_path: Path to export to
        pretty: Whether to pretty-print the JSON
        
    Returns:
        Path to the exported file
    """
    path = Path(file_path)
    ensure_directory_exists(path)
    
    try:
        with open(path, 'w') as f:
            json.dump(data, f, indent=2 if pretty else None, default=str, sort_keys=True)
        return str(path.absolute())
    except Exception as e:
        raise ExportError(f"Failed to export to JSON file {file_path}: {e}")


def export_to_csv(
    data: List[Dict[str, Any]], 
    file_path: Union[str, Path],
    headers: Optional[List[str]] = None,
    dialect: str = 'excel'
) -> str:
    """
    Export list of dictionaries to a CSV file.
    
    Args:
        data: List of dictionaries to export
        file_path: Path to export to
        headers: Optional list of column headers (if None, uses keys from first dictionary)
        dialect: CSV dialect to use
        
    Returns:
        Path to the exported file
    """
    path = Path(file_path)
    ensure_directory_exists(path)
    
    if not data:
        # Create an empty file with headers if provided
        try:
            with open(path, 'w', newline='') as f:
                writer = csv.writer(f, dialect=dialect)
                if headers:
                    writer.writerow(headers)
            return str(path.absolute())
        except Exception as e:
            raise ExportError(f"Failed to export empty data to CSV file {file_path}: {e}")
    
    # If no headers provided, use keys from first item
    if headers is None:
        headers = list(data[0].keys())
    
    try:
        with open(path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers, dialect=dialect, 
                                   extrasaction='ignore')
            writer.writeheader()
            
            # Convert values to strings for CSV compatibility
            for row in data:
                # Create a new dict with string values
                str_row = {}
                for key, value in row.items():
                    if key in headers:
                        str_row[key] = str(value) if value is not None else ""
                writer.writerow(str_row)
                
        return str(path.absolute())
    except Exception as e:
        raise ExportError(f"Failed to export to CSV file {file_path}: {e}")


def export_to_html(
    data: Dict[str, Any], 
    file_path: Union[str, Path],
    template_string: Optional[str] = None,
    template_file: Optional[Union[str, Path]] = None,
    title: str = "Export Report"
) -> str:
    """
    Export data to an HTML file using a template.
    
    Args:
        data: Data to export
        file_path: Path to export to
        template_string: Optional template string
        template_file: Optional path to template file
        title: Title for the HTML document (if using default template)
        
    Returns:
        Path to the exported file
    """
    path = Path(file_path)
    ensure_directory_exists(path)
    
    if not JINJA2_AVAILABLE:
        raise ExportError("Jinja2 is required for HTML export but is not installed")
    
    try:
        # Determine template to use
        template_content = None
        
        if template_string:
            template_content = template_string
        elif template_file:
            with open(template_file, 'r') as f:
                template_content = f.read()
        else:
            # Use default template
            template_content = """<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        tr:hover { background-color: #f5f5f5; }
        .critical { background-color: #ffdddd; }
        .high { background-color: #ffeecc; }
        .medium { background-color: #ffffcc; }
        .low { background-color: #e6f2ff; }
        .info { background-color: #e6ffe6; }
        .timestamp { color: #666; font-size: 0.8em; }
        .footer { margin-top: 30px; border-top: 1px solid #ddd; padding-top: 10px; font-size: 0.8em; color: #666; }
    </style>
</head>
<body>
    <h1>{{ title }}</h1>
    <p class="timestamp">Generated: {{ timestamp }}</p>
    
    {% if summary %}
    <h2>Summary</h2>
    <table>
        <tr>
            <th>Metric</th>
            <th>Value</th>
        </tr>
        {% for key, value in summary.items() %}
        <tr>
            <td>{{ key }}</td>
            <td>{{ value }}</td>
        </tr>
        {% endfor %}
    </table>
    {% endif %}
    
    {% if findings %}
    <h2>Findings</h2>
    <table>
        <tr>
            <th>File</th>
            <th>Type</th>
            <th>Priority</th>
            <th>Description</th>
        </tr>
        {% for finding in findings %}
        <tr class="{{ finding.priority | lower if finding.priority else '' }}">
            <td>{{ finding.file_path }}</td>
            <td>{{ finding.pattern_name }}</td>
            <td>{{ finding.priority }}</td>
            <td>{{ finding.description }}</td>
        </tr>
        {% endfor %}
    </table>
    {% endif %}
    
    {% if recommendations %}
    <h2>Recommendations</h2>
    <ul>
        {% for recommendation in recommendations %}
        <li><strong>{{ recommendation.title }}</strong>: {{ recommendation.description }}</li>
        {% endfor %}
    </ul>
    {% endif %}
    
    <div class="footer">
        Generated by File System Analyzer
    </div>
</body>
</html>
"""
        
        # Create template and render
        template = Template(template_content)
        
        # Add timestamp if not in data
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
        # Add title if not in data
        if 'title' not in data:
            data['title'] = title
            
        # Render template
        html_content = template.render(**data)
        
        # Write to file
        with open(path, 'w') as f:
            f.write(html_content)
            
        return str(path.absolute())
    except Exception as e:
        raise ExportError(f"Failed to export to HTML file {file_path}: {e}")


def export_to_excel(
    data: Dict[str, List[Dict[str, Any]]], 
    file_path: Union[str, Path]
) -> str:
    """
    Export data to an Excel file with multiple sheets.
    
    Args:
        data: Dictionary mapping sheet names to lists of dictionaries
        file_path: Path to export to
        
    Returns:
        Path to the exported file
    """
    path = Path(file_path)
    ensure_directory_exists(path)
    
    if not PANDAS_AVAILABLE:
        raise ExportError("Pandas is required for Excel export but is not installed")
    
    try:
        with pd.ExcelWriter(path) as writer:
            for sheet_name, sheet_data in data.items():
                if not sheet_data:
                    # Create empty dataframe for empty sheets
                    df = pd.DataFrame()
                else:
                    df = pd.DataFrame(sheet_data)
                
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
        return str(path.absolute())
    except Exception as e:
        raise ExportError(f"Failed to export to Excel file {file_path}: {e}")


def export_results(
    data: Dict[str, Any],
    file_path: Union[str, Path],
    format: str = "json"
) -> str:
    """
    Export results to a file in the specified format.
    
    Args:
        data: Data to export
        file_path: Path to export to
        format: Format to export to (json, csv, html, excel)
        
    Returns:
        Path to the exported file
    """
    path = Path(file_path)
    
    # Ensure file has the correct extension for the format
    if format.lower() == "json" and not str(path).endswith(".json"):
        path = path.with_suffix(".json")
    elif format.lower() == "csv" and not str(path).endswith(".csv"):
        path = path.with_suffix(".csv")
    elif format.lower() == "html" and not str(path).endswith(".html"):
        path = path.with_suffix(".html")
    elif format.lower() == "excel" and not str(path).endswith((".xlsx", ".xls")):
        path = path.with_suffix(".xlsx")
        
    logger.info(f"Exporting results to {path} in {format} format")
    
    # Export based on format
    if format.lower() == "json":
        return export_to_json(data, path)
    elif format.lower() == "csv":
        # For CSV, we need a list of dictionaries
        if "findings" in data and isinstance(data["findings"], list):
            return export_to_csv(data["findings"], path)
        elif isinstance(data, list):
            return export_to_csv(data, path)
        else:
            # Convert flat dict to a list with one item
            flat_data = []
            for key, value in data.items():
                if not isinstance(value, (dict, list)):
                    flat_data.append({key: value})
            return export_to_csv(flat_data, path)
    elif format.lower() == "html":
        return export_to_html(data, path)
    elif format.lower() == "excel":
        # For Excel, we need a dict mapping sheet names to lists of dictionaries
        if all(isinstance(v, list) for v in data.values()):
            return export_to_excel(data, path)
        else:
            # Convert data to expected format
            excel_data = {}
            
            for key, value in data.items():
                if isinstance(value, list):
                    excel_data[key] = value
                elif isinstance(value, dict):
                    # Create a sheet with a single row
                    excel_data[key] = [value]
                else:
                    # Create a summary sheet for scalar values
                    if "Summary" not in excel_data:
                        excel_data["Summary"] = []
                    excel_data["Summary"].append({"Metric": key, "Value": value})
                    
            return export_to_excel(excel_data, path)
    else:
        raise ExportError(f"Unsupported export format: {format}")
import os
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Set, Union, Any
from uuid import UUID

import pybtex.database
from pybtex.database.input import bibtex

from .models import Author, AuthorType, Reference, ReferenceType
from .service import BibliographyService


def import_bibtex(bibtex_str: str, service: BibliographyService) -> List[UUID]:
    """
    Import references from a BibTeX string.
    
    Args:
        bibtex_str: BibTeX content as a string
        service: The bibliography service to store the imported references
        
    Returns:
        List[UUID]: List of imported reference IDs
    """
    parser = bibtex.Parser()
    bib_data = parser.parse_string(bibtex_str)
    
    imported_ids = []
    
    for entry_key, entry in bib_data.entries.items():
        # Map entry type to ReferenceType
        ref_type = _map_bibtex_type(entry.type)
        
        # Extract authors
        authors = []
        if "author" in entry.persons:
            for person in entry.persons["author"]:
                first = " ".join(person.first_names + person.middle_names)
                last = " ".join(person.last_names)
                
                if first or last:
                    authors.append(f"{last}, {first}" if last else first)
        
        # Extract fields
        fields = entry.fields
        title = fields.get("title", "").replace("{", "").replace("}", "")
        year = int(fields.get("year", "0")) if fields.get("year", "").isdigit() else None
        
        # Create reference based on type
        if ref_type == ReferenceType.JOURNAL_ARTICLE:
            reference = service.create_reference(
                title=title,
                type=ref_type,
                authors=authors,
                year=year,
                journal_name=fields.get("journal", ""),
                volume=fields.get("volume", ""),
                issue=fields.get("number", ""),
                pages=fields.get("pages", ""),
                doi=fields.get("doi", ""),
                url=fields.get("url", ""),
                abstract=fields.get("abstract", ""),
            )
        
        elif ref_type == ReferenceType.BOOK:
            reference = service.create_reference(
                title=title,
                type=ref_type,
                authors=authors,
                year=year,
                publisher=fields.get("publisher", ""),
                isbn=fields.get("isbn", ""),
                edition=fields.get("edition", ""),
                abstract=fields.get("abstract", ""),
            )
        
        elif ref_type == ReferenceType.CONFERENCE_PAPER:
            reference = service.create_reference(
                title=title,
                type=ref_type,
                authors=authors,
                year=year,
                conference_name=fields.get("booktitle", ""),
                conference_location=fields.get("address", ""),
                pages=fields.get("pages", ""),
                doi=fields.get("doi", ""),
                url=fields.get("url", ""),
                abstract=fields.get("abstract", ""),
            )
        
        else:
            # Generic import for other types
            reference = service.create_reference(
                title=title,
                type=ref_type,
                authors=authors,
                year=year,
                doi=fields.get("doi", ""),
                url=fields.get("url", ""),
                abstract=fields.get("abstract", ""),
            )
        
        # Add keywords if available
        if "keywords" in fields:
            keywords = fields["keywords"].split(",")
            for keyword in keywords:
                keyword = keyword.strip()
                if keyword:
                    service.add_keyword_to_reference(reference.id, keyword)
        
        imported_ids.append(reference.id)
    
    return imported_ids


def _map_bibtex_type(bibtex_type: str) -> ReferenceType:
    """
    Map BibTeX entry type to ReferenceType.
    
    Args:
        bibtex_type: BibTeX entry type
        
    Returns:
        ReferenceType: Corresponding ReferenceType
    """
    type_map = {
        "article": ReferenceType.JOURNAL_ARTICLE,
        "book": ReferenceType.BOOK,
        "booklet": ReferenceType.BOOK,
        "inbook": ReferenceType.BOOK_CHAPTER,
        "incollection": ReferenceType.BOOK_CHAPTER,
        "inproceedings": ReferenceType.CONFERENCE_PAPER,
        "conference": ReferenceType.CONFERENCE_PAPER,
        "manual": ReferenceType.REPORT,
        "mastersthesis": ReferenceType.THESIS,
        "phdthesis": ReferenceType.THESIS,
        "proceedings": ReferenceType.REPORT,
        "techreport": ReferenceType.REPORT,
        "unpublished": ReferenceType.PREPRINT,
        "misc": ReferenceType.OTHER,
    }
    
    return type_map.get(bibtex_type.lower(), ReferenceType.OTHER)


def import_json(json_str: str, service: BibliographyService) -> List[UUID]:
    """
    Import references from a JSON string.
    
    Args:
        json_str: JSON content as a string
        service: The bibliography service to store the imported references
        
    Returns:
        List[UUID]: List of imported reference IDs
    """
    data = json.loads(json_str)
    
    if not isinstance(data, list):
        # Handle single reference
        if isinstance(data, dict):
            data = [data]
        else:
            raise ValueError("Invalid JSON format: Expected a list or dict of references")
    
    imported_ids = []
    
    for ref_data in data:
        # Map JSON type to ReferenceType
        ref_type = _map_json_type(ref_data.get("type", ""))
        
        # Extract authors
        authors = []
        if "authors" in ref_data:
            for author in ref_data["authors"]:
                if isinstance(author, str):
                    authors.append(author)
                elif isinstance(author, dict):
                    if "name" in author:
                        authors.append(author["name"])
                    elif "firstName" in author or "lastName" in author:
                        first = author.get("firstName", "")
                        last = author.get("lastName", "")
                        if first or last:
                            authors.append(f"{last}, {first}" if last else first)
        
        # Create reference
        reference = service.create_reference(
            title=ref_data.get("title", "Unknown Title"),
            type=ref_type,
            authors=authors,
            year=int(ref_data["year"]) if "year" in ref_data and str(ref_data["year"]).isdigit() else None,
            journal_name=ref_data.get("journal", ref_data.get("journalName", "")),
            volume=ref_data.get("volume", ""),
            issue=ref_data.get("issue", ref_data.get("number", "")),
            pages=ref_data.get("pages", ""),
            doi=ref_data.get("doi", ""),
            url=ref_data.get("url", ""),
            publisher=ref_data.get("publisher", ""),
            isbn=ref_data.get("isbn", ""),
            abstract=ref_data.get("abstract", ""),
        )
        
        # Add keywords if available
        if "keywords" in ref_data:
            keywords = ref_data["keywords"]
            if isinstance(keywords, str):
                keywords = keywords.split(",")
            
            for keyword in keywords:
                if isinstance(keyword, str):
                    keyword = keyword.strip()
                    if keyword:
                        service.add_keyword_to_reference(reference.id, keyword)
        
        imported_ids.append(reference.id)
    
    return imported_ids


def _map_json_type(json_type: str) -> ReferenceType:
    """
    Map JSON reference type to ReferenceType.
    
    Args:
        json_type: JSON reference type
        
    Returns:
        ReferenceType: Corresponding ReferenceType
    """
    type_map = {
        "article": ReferenceType.JOURNAL_ARTICLE,
        "journal-article": ReferenceType.JOURNAL_ARTICLE,
        "journal_article": ReferenceType.JOURNAL_ARTICLE,
        "journalarticle": ReferenceType.JOURNAL_ARTICLE,
        "book": ReferenceType.BOOK,
        "book-chapter": ReferenceType.BOOK_CHAPTER,
        "book_chapter": ReferenceType.BOOK_CHAPTER,
        "bookchapter": ReferenceType.BOOK_CHAPTER,
        "chapter": ReferenceType.BOOK_CHAPTER,
        "conference": ReferenceType.CONFERENCE_PAPER,
        "conference-paper": ReferenceType.CONFERENCE_PAPER,
        "conference_paper": ReferenceType.CONFERENCE_PAPER,
        "conferencepaper": ReferenceType.CONFERENCE_PAPER,
        "proceedings": ReferenceType.CONFERENCE_PAPER,
        "thesis": ReferenceType.THESIS,
        "dissertation": ReferenceType.THESIS,
        "report": ReferenceType.REPORT,
        "technical-report": ReferenceType.REPORT,
        "technical_report": ReferenceType.REPORT,
        "technicalreport": ReferenceType.REPORT,
        "website": ReferenceType.WEBSITE,
        "web": ReferenceType.WEBSITE,
        "preprint": ReferenceType.PREPRINT,
        "dataset": ReferenceType.DATASET,
        "software": ReferenceType.SOFTWARE,
    }
    
    return type_map.get(json_type.lower(), ReferenceType.OTHER)


def import_endnote_xml(xml_str: str, service: BibliographyService) -> List[UUID]:
    """
    Import references from an EndNote XML string.
    
    Note: This is a simplified implementation that handles common EndNote XML
    patterns, but may not support all variations of EndNote XML formats.
    
    Args:
        xml_str: EndNote XML content as a string
        service: The bibliography service to store the imported references
        
    Returns:
        List[UUID]: List of imported reference IDs
    """
    # Extract records using simple regex patterns
    # This is a simplified approach - in real implementation, use XML parsing
    record_pattern = r"<record>.*?</record>"
    records = re.findall(record_pattern, xml_str, re.DOTALL)
    
    imported_ids = []
    
    for record in records:
        # Extract reference type
        ref_type_match = re.search(r"<ref-type.*?>(.*?)</ref-type>", record, re.DOTALL)
        ref_type_str = ref_type_match.group(1) if ref_type_match else "Journal Article"
        ref_type = _map_endnote_type(ref_type_str)
        
        # Extract title
        title_match = re.search(r"<titles>.*?<title.*?>(.*?)</title>", record, re.DOTALL)
        title = title_match.group(1) if title_match else "Unknown Title"
        
        # Extract authors
        authors = []
        author_pattern = r"<contributors>.*?<authors>.*?<author.*?>(.*?)</author>.*?</authors>.*?</contributors>"
        authors_section = re.search(author_pattern, record, re.DOTALL)
        
        if authors_section:
            author_names = re.findall(r"<author.*?>(.*?)</author>", authors_section.group(0), re.DOTALL)
            authors = [name.strip() for name in author_names if name.strip()]
        
        # Extract year
        year_match = re.search(r"<dates>.*?<year.*?>(.*?)</year>", record, re.DOTALL)
        year = int(year_match.group(1)) if year_match and year_match.group(1).isdigit() else None
        
        # Extract journal
        journal_match = re.search(r"<periodical>.*?<full-title.*?>(.*?)</full-title>", record, re.DOTALL)
        journal = journal_match.group(1) if journal_match else ""
        
        # Extract volume
        volume_match = re.search(r"<volume.*?>(.*?)</volume>", record, re.DOTALL)
        volume = volume_match.group(1) if volume_match else ""
        
        # Extract issue
        issue_match = re.search(r"<number.*?>(.*?)</number>", record, re.DOTALL)
        issue = issue_match.group(1) if issue_match else ""
        
        # Extract pages
        pages_match = re.search(r"<pages.*?>(.*?)</pages>", record, re.DOTALL)
        pages = pages_match.group(1) if pages_match else ""
        
        # Extract DOI
        doi_match = re.search(r"<electronic-resource-num.*?>(.*?)</electronic-resource-num>", record, re.DOTALL)
        doi = doi_match.group(1) if doi_match else ""
        
        # Extract abstract
        abstract_match = re.search(r"<abstract.*?>(.*?)</abstract>", record, re.DOTALL)
        abstract = abstract_match.group(1) if abstract_match else ""
        
        # Extract URL
        url_match = re.search(r"<url.*?>(.*?)</url>", record, re.DOTALL)
        url = url_match.group(1) if url_match else ""
        
        # Extract publisher
        publisher_match = re.search(r"<publisher.*?>(.*?)</publisher>", record, re.DOTALL)
        publisher = publisher_match.group(1) if publisher_match else ""
        
        # Extract keywords
        keywords = []
        keywords_pattern = r"<keywords>.*?<keyword.*?>(.*?)</keyword>.*?</keywords>"
        keywords_section = re.search(keywords_pattern, record, re.DOTALL)
        
        if keywords_section:
            keywords = re.findall(r"<keyword.*?>(.*?)</keyword>", keywords_section.group(0), re.DOTALL)
            keywords = [k.strip() for k in keywords if k.strip()]
        
        # Create reference
        reference = service.create_reference(
            title=title,
            type=ref_type,
            authors=authors,
            year=year,
            journal_name=journal,
            volume=volume,
            issue=issue,
            pages=pages,
            doi=doi,
            url=url,
            publisher=publisher,
            abstract=abstract,
        )
        
        # Add keywords
        for keyword in keywords:
            service.add_keyword_to_reference(reference.id, keyword)
        
        imported_ids.append(reference.id)
    
    return imported_ids


def _map_endnote_type(endnote_type: str) -> ReferenceType:
    """
    Map EndNote reference type to ReferenceType.
    
    Args:
        endnote_type: EndNote reference type
        
    Returns:
        ReferenceType: Corresponding ReferenceType
    """
    type_map = {
        "journal article": ReferenceType.JOURNAL_ARTICLE,
        "book": ReferenceType.BOOK,
        "book section": ReferenceType.BOOK_CHAPTER,
        "conference proceedings": ReferenceType.CONFERENCE_PAPER,
        "conference paper": ReferenceType.CONFERENCE_PAPER,
        "thesis": ReferenceType.THESIS,
        "report": ReferenceType.REPORT,
        "web page": ReferenceType.WEBSITE,
        "electronic article": ReferenceType.PREPRINT,
        "dataset": ReferenceType.DATASET,
        "computer program": ReferenceType.SOFTWARE,
    }
    
    return type_map.get(endnote_type.lower(), ReferenceType.OTHER)
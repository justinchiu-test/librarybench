"""Tests for edge cases in citation parsers."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import pypdf

from researchbrain.citations.parsers import (
    parse_bibtex_file, parse_ris_file,
    extract_doi_from_pdf, extract_pdf_metadata
)


class TestCitationParserEdgeCases:
    """Test edge cases for citation parsers."""
    
    def test_parse_bibtex_string_minimal(self):
        """Test parsing a minimal BibTeX string."""
        bibtex = """
        @article{minimal,
          title={Minimal BibTeX Entry},
          author={Test Author},
          year={2023}
        }
        """
        
        result = parse_bibtex_string(bibtex)
        assert result is not None
        assert len(result) == 1
        entry = result[0]
        assert entry["title"] == "Minimal BibTeX Entry"
        assert entry["author"] == ["Test Author"]
        assert entry["year"] == 2023
    
    def test_parse_bibtex_string_multiple_entries(self):
        """Test parsing a BibTeX string with multiple entries."""
        bibtex = """
        @article{first,
          title={First Entry},
          author={First Author},
          year={2021}
        }
        
        @book{second,
          title={Second Entry},
          author={Second Author},
          year={2022}
        }
        
        @inproceedings{third,
          title={Third Entry},
          author={Third Author},
          year={2023}
        }
        """
        
        result = parse_bibtex_string(bibtex)
        assert result is not None
        assert len(result) == 3
        assert result[0]["title"] == "First Entry"
        assert result[1]["title"] == "Second Entry"
        assert result[2]["title"] == "Third Entry"
    
    def test_parse_bibtex_string_with_special_characters(self):
        """Test parsing a BibTeX string with special characters."""
        bibtex = r"""
        @article{special,
          title={Special \& Characters in {BibTeX}: A Test},
          author={Test Author and Another Author and {Organization Name}},
          year={2023},
          journal={Test \& Journal}
        }
        """
        
        result = parse_bibtex_string(bibtex)
        assert result is not None
        assert len(result) == 1
        entry = result[0]
        assert "Special" in entry["title"]
        assert "Characters" in entry["title"]
        assert len(entry["author"]) == 3
    
    def test_parse_bibtex_string_with_multiline_fields(self):
        """Test parsing a BibTeX string with multiline fields."""
        bibtex = """
        @article{multiline,
          title={Multiline
                 Title},
          author={Test
                 Author},
          abstract={This is a
                   multiline
                   abstract},
          year={2023}
        }
        """
        
        result = parse_bibtex_string(bibtex)
        assert result is not None
        assert len(result) == 1
        entry = result[0]
        assert "Multiline Title" in entry["title"]
        assert "This is a multiline abstract" in entry["abstract"]
    
    def test_parse_bibtex_file(self):
        """Test parsing a BibTeX file."""
        # Create a temporary BibTeX file
        with tempfile.NamedTemporaryFile(suffix=".bib", delete=False) as temp_file:
            temp_file.write(b"""
            @article{test,
              title={Test BibTeX File},
              author={File Author},
              year={2023}
            }
            """)
            temp_path = temp_file.name
        
        try:
            result = parse_bibtex_file(temp_path)
            assert result is not None
            assert len(result) == 1
            entry = result[0]
            assert entry["title"] == "Test BibTeX File"
            assert entry["author"] == ["File Author"]
            assert entry["year"] == 2023
        finally:
            os.unlink(temp_path)
    
    def test_parse_bibtex_file_nonexistent(self):
        """Test parsing a nonexistent BibTeX file."""
        result = parse_bibtex_file("/nonexistent/file.bib")
        assert result == []
    
    def test_parse_ris_string_minimal(self):
        """Test parsing a minimal RIS string."""
        ris = """
        TY  - JOUR
        TI  - Minimal RIS Entry
        AU  - Test Author
        PY  - 2023
        ER  - 
        """
        
        result = parse_ris_string(ris)
        assert result is not None
        assert len(result) == 1
        entry = result[0]
        assert entry["title"] == "Minimal RIS Entry"
        assert entry["author"] == ["Test Author"]
        assert entry["year"] == 2023
    
    def test_parse_ris_string_multiple_entries(self):
        """Test parsing a RIS string with multiple entries."""
        ris = """
        TY  - JOUR
        TI  - First RIS Entry
        AU  - First Author
        PY  - 2021
        ER  - 
        
        TY  - BOOK
        TI  - Second RIS Entry
        AU  - Second Author
        PY  - 2022
        ER  - 
        
        TY  - CONF
        TI  - Third RIS Entry
        AU  - Third Author
        PY  - 2023
        ER  - 
        """
        
        result = parse_ris_string(ris)
        assert result is not None
        assert len(result) == 3
        assert result[0]["title"] == "First RIS Entry"
        assert result[1]["title"] == "Second RIS Entry"
        assert result[2]["title"] == "Third RIS Entry"
    
    def test_parse_ris_string_with_multiple_authors(self):
        """Test parsing a RIS string with multiple authors."""
        ris = """
        TY  - JOUR
        TI  - Multiple Authors
        AU  - First Author
        AU  - Second Author
        AU  - Third Author
        PY  - 2023
        ER  - 
        """
        
        result = parse_ris_string(ris)
        assert result is not None
        assert len(result) == 1
        entry = result[0]
        assert entry["author"] == ["First Author", "Second Author", "Third Author"]
    
    def test_parse_ris_file(self):
        """Test parsing a RIS file."""
        # Create a temporary RIS file
        with tempfile.NamedTemporaryFile(suffix=".ris", delete=False) as temp_file:
            temp_file.write(b"""
            TY  - JOUR
            TI  - Test RIS File
            AU  - File Author
            PY  - 2023
            ER  - 
            """)
            temp_path = temp_file.name
        
        try:
            result = parse_ris_file(temp_path)
            assert result is not None
            assert len(result) == 1
            entry = result[0]
            assert entry["title"] == "Test RIS File"
            assert entry["author"] == ["File Author"]
            assert entry["year"] == 2023
        finally:
            os.unlink(temp_path)
    
    def test_parse_ris_file_nonexistent(self):
        """Test parsing a nonexistent RIS file."""
        result = parse_ris_file("/nonexistent/file.ris")
        assert result == []
    
    @patch('researchbrain.citations.parsers.PyPDF2')
    def test_extract_doi_from_pdf(self, mock_pypdf2):
        """Test extracting DOI from a PDF file."""
        # Mock PyPDF2 to return text with a DOI
        mock_reader = MagicMock()
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "This is a test PDF with DOI: 10.1234/test.2023 in the text."
        mock_pdf.pages = [mock_page]
        mock_reader.return_value = mock_pdf
        mock_pypdf2.PdfReader = mock_reader
        
        result = extract_doi_from_pdf("/test/file.pdf")
        assert result == "10.1234/test.2023"
    
    @patch('researchbrain.citations.parsers.PyPDF2')
    def test_extract_doi_from_pdf_not_found(self, mock_pypdf2):
        """Test extracting DOI from a PDF file with no DOI."""
        # Mock PyPDF2 to return text without a DOI
        mock_reader = MagicMock()
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "This is a test PDF with no DOI in the text."
        mock_pdf.pages = [mock_page]
        mock_reader.return_value = mock_pdf
        mock_pypdf2.PdfReader = mock_reader
        
        result = extract_doi_from_pdf("/test/file.pdf")
        assert result is None
    
    @patch('researchbrain.citations.parsers.PyPDF2')
    def test_extract_pdf_metadata(self, mock_pypdf2):
        """Test extracting metadata from a PDF file."""
        # Mock PyPDF2 to return metadata
        mock_reader = MagicMock()
        mock_pdf = MagicMock()
        mock_pdf.metadata = {
            "/Title": "Test PDF",
            "/Author": "Test Author",
            "/Subject": "Test Subject",
            "/Keywords": "test, metadata, pdf",
            "/CreationDate": "D:20230101000000",
        }
        mock_reader.return_value = mock_pdf
        mock_pypdf2.PdfReader = mock_reader
        
        result = extract_pdf_metadata("/test/file.pdf")
        assert result is not None
        assert result["title"] == "Test PDF"
        assert result["author"] == "Test Author"
        assert "keywords" in result
    
    @patch('researchbrain.citations.parsers.extract_doi_from_pdf')
    @patch('researchbrain.citations.parsers.extract_pdf_metadata')
    @patch('researchbrain.citations.parsers.parse_bibtex_file')
    @patch('researchbrain.citations.parsers.parse_ris_file')
    def test_parse_citation_file_pdf(self, mock_ris, mock_bibtex, mock_metadata, mock_doi):
        """Test parsing a PDF citation file."""
        # Mock return values
        mock_doi.return_value = "10.1234/test.2023"
        mock_metadata.return_value = {
            "title": "Test PDF",
            "author": "Test Author",
            "year": "2023"
        }
        
        # Test parsing a PDF file
        result = parse_citation_file("/test/file.pdf")
        assert result is not None
        assert result["title"] == "Test PDF"
        assert "doi" in result
        assert result["doi"] == "10.1234/test.2023"
        
        # Verify the right functions were called
        mock_doi.assert_called_once()
        mock_metadata.assert_called_once()
        mock_bibtex.assert_not_called()
        mock_ris.assert_not_called()
    
    @patch('researchbrain.citations.parsers.parse_bibtex_file')
    def test_parse_citation_file_bibtex(self, mock_bibtex):
        """Test parsing a BibTeX citation file."""
        # Mock return value
        mock_bibtex.return_value = [{
            "title": "Test BibTeX",
            "author": ["Test Author"],
            "year": 2023,
            "journal": "Test Journal"
        }]
        
        # Test parsing a BibTeX file
        result = parse_citation_file("/test/file.bib")
        assert result is not None
        assert result["title"] == "Test BibTeX"
        assert result["author"] == ["Test Author"]
        
        # Verify the right function was called
        mock_bibtex.assert_called_once()
    
    @patch('researchbrain.citations.parsers.parse_ris_file')
    def test_parse_citation_file_ris(self, mock_ris):
        """Test parsing a RIS citation file."""
        # Mock return value
        mock_ris.return_value = [{
            "title": "Test RIS",
            "author": ["Test Author"],
            "year": 2023,
            "journal": "Test Journal"
        }]
        
        # Test parsing a RIS file
        result = parse_citation_file("/test/file.ris")
        assert result is not None
        assert result["title"] == "Test RIS"
        assert result["author"] == ["Test Author"]
        
        # Verify the right function was called
        mock_ris.assert_called_once()
    
    def test_parse_citation_file_unsupported(self):
        """Test parsing an unsupported file type."""
        with pytest.raises(ValueError):
            parse_citation_file("/test/file.txt")
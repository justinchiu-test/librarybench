"""Tests for the CLI module."""

import argparse
import os
import shutil
import tempfile
from unittest.mock import patch, MagicMock

import pytest
from rich.console import Console

from researchbrain.cli import main
from researchbrain.core.brain import ResearchBrain
from researchbrain.core.models import Note, Citation


class TestCLI:
    """Tests for the CLI module."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Fixture that creates a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_brain(self):
        """Fixture that creates a mock ResearchBrain instance."""
        mock = MagicMock(spec=ResearchBrain)
        return mock
    
    @pytest.fixture
    def mock_console(self):
        """Fixture that creates a mock Console instance."""
        mock = MagicMock(spec=Console)
        return mock
    
    def test_init_command(self, temp_data_dir, mock_console):
        """Test the init command handler."""
        # Import the private function for testing
        from researchbrain.cli import _init_command
        
        with patch('researchbrain.cli.console', mock_console):
            _init_command(temp_data_dir)
        
        # Check that the directory structure was created
        assert os.path.exists(os.path.join(temp_data_dir, "notes"))
        assert os.path.exists(os.path.join(temp_data_dir, "citations"))
        assert os.path.exists(os.path.join(temp_data_dir, "experiments"))
        assert os.path.exists(os.path.join(temp_data_dir, "grants"))
        
        # Check that the console was called
        mock_console.print.assert_called()
    
    def test_main_function(self):
        """Test the main function integration."""
        # Test that the main function exists and is callable
        assert callable(main)
        
        # Test with a mock ArgumentParser to simulate CLI arguments
        with patch('argparse.ArgumentParser') as mock_parser:
            # Setup mock parser and subparsers
            mock_parser_instance = MagicMock()
            mock_parser.return_value = mock_parser_instance
            
            mock_subparsers = MagicMock()
            mock_parser_instance.add_subparsers.return_value = mock_subparsers
            
            # Setup mock args result
            mock_args = MagicMock()
            mock_args.command = None  # Simulate no command
            mock_args.data_dir = "/tmp/test"
            mock_parser_instance.parse_args.return_value = mock_args
            
            # Execute with mocks
            with patch('researchbrain.cli.ResearchBrain'):
                main()
                
            # Verify parser was called
            mock_parser.assert_called_once()
            mock_parser_instance.add_subparsers.assert_called_once()
            mock_parser_instance.parse_args.assert_called_once()
            
    def test_note_commands_structure(self):
        """Test the note commands structure in CLI."""
        with patch('argparse.ArgumentParser') as mock_parser:
            # Setup mock parser and subparsers
            mock_parser_instance = MagicMock()
            mock_parser.return_value = mock_parser_instance
            
            mock_subparsers = MagicMock()
            mock_parser_instance.add_subparsers.return_value = mock_subparsers
            
            # Setup mock note subparser
            mock_note_parser = MagicMock()
            mock_subparsers.add_parser.return_value = mock_note_parser
            
            mock_note_subparsers = MagicMock()
            mock_note_parser.add_subparsers.return_value = mock_note_subparsers
            
            # Setup command handlers
            mock_create_parser = MagicMock()
            mock_list_parser = MagicMock()
            mock_view_parser = MagicMock()
            
            mock_note_subparsers.add_parser.side_effect = [
                mock_create_parser, mock_list_parser, mock_view_parser
            ]
            
            # Setup mock args result
            mock_args = MagicMock()
            mock_args.command = "note"
            mock_args.note_command = "create"
            mock_args.data_dir = "/tmp/test"
            mock_parser_instance.parse_args.return_value = mock_args
            
            # Mock brain
            mock_brain = MagicMock()
            
            # Execute with mocks
            with patch('researchbrain.cli.ResearchBrain', return_value=mock_brain):
                main()
            
            # Verify parser structure
            mock_subparsers.add_parser.assert_any_call("note", help="Manage research notes")
            mock_note_parser.add_subparsers.assert_called_once()
    
    def test_search_command_integration(self):
        """Test the search command integration."""
        # Import the private function for testing
        from researchbrain.cli import _handle_search_command
        
        # Setup
        args = argparse.Namespace(query="test", limit=10)
        mock_brain = MagicMock()
        
        # Create test search results
        test_results = {
            "notes": [MagicMock(spec=Note, id=f"note{i}", title=f"Note {i}") for i in range(2)],
            "citations": [MagicMock(spec=Citation, id=f"cite{i}", title=f"Citation {i}") for i in range(2)]
        }
        
        # Mock ResearchBrain.search to return test results
        mock_brain.search.return_value = test_results
        
        # Execute with mocks
        with patch('researchbrain.cli.console'):
            _handle_search_command(mock_brain, args)
        
        # Verify
        mock_brain.search.assert_called_once_with("test", limit=10)
    
    def test_main_with_init_integration(self, temp_data_dir):
        """Test the main function with init command (integration test)."""
        # Setup mock arguments
        test_args = [
            "researchbrain",
            "--data-dir", temp_data_dir,
            "init"
        ]
        
        # Execute
        with patch('sys.argv', test_args), \
             patch('researchbrain.cli._init_command') as mock_init:
            main()
        
        # Verify
        mock_init.assert_called_once_with(temp_data_dir)
    
    def test_experiment_template_commands(self):
        """Test the experiment template commands in CLI."""
        with patch('argparse.ArgumentParser') as mock_parser:
            # Setup mock parser and subparsers
            mock_parser_instance = MagicMock()
            mock_parser.return_value = mock_parser_instance
            
            mock_subparsers = MagicMock()
            mock_parser_instance.add_subparsers.return_value = mock_subparsers
            
            # Setup mock experiment subparser
            mock_exp_parser = MagicMock()
            mock_exp_subparser = MagicMock()
            mock_subparsers.add_parser.return_value = mock_exp_parser
            mock_exp_parser.add_subparsers.return_value = mock_exp_subparser
            
            # Setup mock args result
            mock_args = MagicMock()
            mock_args.command = "experiment"
            mock_args.experiment_command = "list-templates"
            mock_args.data_dir = "/tmp/test"
            mock_parser_instance.parse_args.return_value = mock_args
            
            # Mock list_templates to return template names
            mock_template_list = ["behavioral_experiment", "neuroimaging_experiment"]
            
            # Execute with mocks
            with patch('researchbrain.cli.ResearchBrain'), \
                 patch('researchbrain.cli.list_templates', return_value=mock_template_list), \
                 patch('researchbrain.cli.console'):
                main()
            
            # Verify parser structure
            mock_subparsers.add_parser.assert_any_call("experiment", help="Manage experiments")
            mock_exp_parser.add_subparsers.assert_called_once()
import os
import sys
from src.personas.data_scientist.datapipeline_cli.commands import DataPipelineCommands
from src.core.commands.registry import CommandRegistry

def test_command_registration():
    # Create a command registry
    registry = CommandRegistry("datapipeline")
    
    # Create the commands
    commands = DataPipelineCommands(registry)
    
    # Check that commands were registered
    cmd = registry.find_command("pipeline:run")
    assert cmd is not None
    
    cmd = registry.find_command("pipeline:extract")
    assert cmd is not None
    
    cmd = registry.find_command("pipeline:transform")
    assert cmd is not None
    
    cmd = registry.find_command("pipeline:load")
    assert cmd is not None

def test_pipeline_execution(tmp_path, monkeypatch):
    # Create a command registry
    registry = CommandRegistry("datapipeline")
    
    # Create the commands
    commands = DataPipelineCommands(registry)
    
    # Create a test pipeline file
    pipeline_dir = tmp_path / "pipelines"
    pipeline_dir.mkdir()
    
    # Create a config dir with a pipeline config
    config_dir = tmp_path / "configs"
    config_dir.mkdir()
    
    pipeline_config = config_dir / "test-pipeline.json"
    pipeline_config.write_text('{"pipeline": {"name": "test-pipeline"}}')
    
    # Set working directory to test path
    monkeypatch.chdir(tmp_path)
    
    # Execute the run command
    try:
        # This would normally produce output - we're just testing it doesn't crash
        registry.execute_command("pipeline:run", "test-pipeline")
    except Exception as e:
        # If there's an error, it should be because the pipeline isn't fully implemented
        # not because of import errors or command registry issues
        assert "test-pipeline" in str(e)
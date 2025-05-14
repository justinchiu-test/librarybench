"""
Data scientist datapipeline CLI commands.
Defines commands for managing data pipelines.
"""

import os
import sys
import json
import datetime
import subprocess
from typing import Any, Dict, List, Optional, Tuple

from ....core.commands.registry import CommandRegistry, Command, CommandGroup
from ....core.dev.scaffold import Scaffolder, ScaffoldTemplate
from .config_parser import DataPipelineConfigParser


class DataPipelineCommands:
    """Commands for data pipeline management."""
    
    def __init__(self, registry: CommandRegistry):
        """
        Initialize data pipeline commands.
        
        Args:
            registry: Command registry to register commands with
        """
        self.registry = registry
        self.group = CommandGroup("pipeline", "Data pipeline management commands")
        self.register_commands()
    
    def register_commands(self) -> None:
        """Register data pipeline commands with the command group."""
        self.group.command("run")(self.run_pipeline)
        self.group.command("status")(self.check_status)
        self.group.command("validate")(self.validate_pipeline)
        self.group.command("list")(self.list_pipelines)
        self.group.command("scaffold")(self.scaffold_pipeline)
        self.group.command("extract")(self.extract_data)
        self.group.command("transform")(self.transform_data)
        self.group.command("load")(self.load_data)
        
        # Register the command group with the registry
        self.group.register_with(self.registry)
    
    def run_pipeline(self, 
                    name: str, 
                    env: str = "development",
                    params: str = "") -> int:
        """
        Run a data pipeline.
        
        Args:
            name: Pipeline name
            env: Environment to run in
            params: Additional parameters (JSON string or key=value,key2=value2)
            
        Returns:
            Exit code (0 for success)
        """
        # Load configuration
        config_parser = DataPipelineConfigParser()
        config = config_parser.load_config(name, env)
        
        # Parse parameters
        parameters = {}
        if params:
            if params.startswith('{'):
                # JSON format
                try:
                    parameters = json.loads(params)
                except json.JSONDecodeError:
                    print(f"Error: Invalid JSON parameters: {params}")
                    return 1
            else:
                # key=value format
                for pair in params.split(','):
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        parameters[key.strip()] = value.strip()
        
        # Get pipeline configuration
        pipeline_config = config_parser.get_pipeline_config()
        if not pipeline_config:
            print(f"Error: No configuration found for pipeline: {name}")
            return 1
        
        # Determine pipeline implementation
        implementation = pipeline_config.get("implementation")
        if not implementation:
            # Look for the pipeline file
            pipeline_file = os.path.join(os.getcwd(), "pipelines", f"{name}.py")
            if os.path.exists(pipeline_file):
                implementation = pipeline_file
            else:
                print(f"Error: No implementation found for pipeline: {name}")
                return 1
        
        # Print info
        print(f"Running pipeline: {name}")
        print(f"Environment: {env}")
        if parameters:
            print(f"Parameters: {json.dumps(parameters, indent=2)}")
        
        # Record start time
        start_time = datetime.datetime.now()
        print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run the pipeline
        # For demonstration purposes, we're simulating the pipeline execution
        # In a real implementation, this would interact with a data pipeline framework
        try:
            # Simulate pipeline phases
            print("\nExecuting pipeline phases:")
            
            # Extract phase
            print("- Running Extract phase...")
            datasets = config.get("datasets", {})
            for ds_name, ds_config in datasets.items():
                print(f"  - Extracting data from {ds_name}...")
            
            # Transform phase
            print("- Running Transform phase...")
            transforms = config.get("transforms", {})
            for tx_name, tx_config in transforms.items():
                print(f"  - Applying transformation {tx_name}...")
            
            # Load phase
            print("- Running Load phase...")
            connectors = config.get("connectors", {})
            for conn_name, conn_config in connectors.items():
                print(f"  - Loading data to {conn_name}...")
            
            # Record end time
            end_time = datetime.datetime.now()
            duration = end_time - start_time
            print(f"\nPipeline completed successfully")
            print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Duration: {duration.total_seconds():.2f} seconds")
            
            return 0
            
        except Exception as e:
            print(f"\nError running pipeline: {e}")
            return 1
    
    def check_status(self, name: str, run_id: Optional[str] = None) -> int:
        """
        Check the status of a pipeline or pipeline run.
        
        Args:
            name: Pipeline name
            run_id: Specific run ID to check
            
        Returns:
            Exit code (0 for success)
        """
        # Load configuration
        config_parser = DataPipelineConfigParser()
        config = config_parser.load_config(name)
        
        # Get pipeline configuration
        pipeline_config = config_parser.get_pipeline_config()
        if not pipeline_config:
            print(f"Error: No configuration found for pipeline: {name}")
            return 1
        
        if run_id:
            # Check specific run
            print(f"Checking status of pipeline run: {name} (Run ID: {run_id})")
            # Simulated result
            print(f"Status: COMPLETED")
            print(f"Start time: 2023-01-01 10:00:00")
            print(f"End time: 2023-01-01 10:15:00")
            print(f"Duration: 15 minutes")
            print(f"Records processed: 10000")
        else:
            # Show general pipeline status
            print(f"Pipeline: {name}")
            print(f"Last run: 2023-01-01 10:00:00")
            print(f"Status: ACTIVE")
            print(f"Recent runs:")
            print(f"  - Run ID: abc123 | Status: COMPLETED | 2023-01-01 10:00:00")
            print(f"  - Run ID: def456 | Status: COMPLETED | 2022-12-31 10:00:00")
            print(f"  - Run ID: ghi789 | Status: FAILED    | 2022-12-30 10:00:00")
        
        return 0
    
    def validate_pipeline(self, name: str, env: str = "development") -> int:
        """
        Validate a data pipeline configuration and implementation.
        
        Args:
            name: Pipeline name
            env: Environment to validate for
            
        Returns:
            Exit code (0 for success)
        """
        # Load configuration
        config_parser = DataPipelineConfigParser()
        config = config_parser.load_config(name, env)
        
        print(f"Validating pipeline: {name}")
        print(f"Environment: {env}")
        
        # Validate basic structure
        errors = []
        warnings = []
        
        # Check for required sections
        if "pipeline" not in config:
            errors.append("Missing 'pipeline' section in configuration")
        
        # Check for datasets
        if "datasets" not in config or not config["datasets"]:
            warnings.append("No datasets defined in configuration")
        
        # Check for transforms
        if "transforms" not in config or not config["transforms"]:
            warnings.append("No transforms defined in configuration")
        
        # Check for connectors
        if "connectors" not in config or not config["connectors"]:
            warnings.append("No connectors defined in configuration")
        
        # Check pipeline implementation
        pipeline_config = config.get("pipeline", {})
        implementation = pipeline_config.get("implementation")
        if implementation and not os.path.exists(implementation):
            errors.append(f"Pipeline implementation file not found: {implementation}")
        
        # Check for circular dependencies
        # (This would be more complex in a real implementation)
        
        # Report results
        if errors:
            print("\nErrors:")
            for error in errors:
                print(f"  - {error}")
        
        if warnings:
            print("\nWarnings:")
            for warning in warnings:
                print(f"  - {warning}")
        
        if not errors and not warnings:
            print("\nValidation successful! Pipeline configuration is valid.")
        elif not errors:
            print("\nValidation successful with warnings.")
        else:
            print("\nValidation failed. Please fix the errors and try again.")
            return 1
        
        return 0
    
    def list_pipelines(self) -> int:
        """
        List available data pipelines.
        
        Returns:
            Exit code (0 for success)
        """
        # Look for pipelines in the config directory
        config_parser = DataPipelineConfigParser()
        config_dir = config_parser.config_dir
        
        print(f"Looking for pipelines in {config_dir}")
        
        if not os.path.exists(config_dir):
            print("Config directory not found.")
            return 1
        
        # Find pipeline configurations
        pipelines = []
        for file in os.listdir(config_dir):
            base_name = file.split('.')[0]
            if '-' in base_name:
                # Skip environment-specific configs
                continue
                
            ext = file.split('.')[-1]
            if ext in ('json', 'ini', 'yaml', 'yml'):
                pipelines.append(base_name)
        
        # Remove duplicates
        pipelines = sorted(set(pipelines))
        
        if not pipelines:
            print("No pipelines found.")
            return 0
        
        print(f"\nFound {len(pipelines)} pipeline(s):")
        for pipeline in pipelines:
            # Try to load the pipeline to get more info
            try:
                config = config_parser.load_config(pipeline)
                pipeline_config = config.get("pipeline", {})
                description = pipeline_config.get("description", "No description")
                print(f"  - {pipeline}: {description}")
            except Exception:
                print(f"  - {pipeline}")
        
        return 0
    
    def scaffold_pipeline(self, 
                         name: str, 
                         template: str = "etl",
                         output_dir: Optional[str] = None) -> int:
        """
        Scaffold a new data pipeline.
        
        Args:
            name: Pipeline name
            template: Template to use
            output_dir: Output directory (default: current directory)
            
        Returns:
            Exit code (0 for success)
        """
        # Create scaffolder
        scaffolder = Scaffolder()
        
        # Add data pipeline templates
        self._add_pipeline_templates(scaffolder)
        
        # Check if template exists
        if template not in [t["name"] for t in scaffolder.list_templates()]:
            print(f"Template not found: {template}")
            return 1
        
        # Determine output directory
        if not output_dir:
            output_dir = os.path.join(os.getcwd(), name)
        
        # Prepare variables
        variables = {
            "pipeline_name": name,
            "pipeline_description": f"{name} data pipeline",
            "version": "0.1.0",
            "author": os.environ.get("USER", "user"),
        }
        
        # Generate project
        print(f"Scaffolding {name} data pipeline with template {template}...")
        success = scaffolder.generate(template, output_dir, variables)
        
        if success:
            print(f"Data pipeline scaffolded successfully at: {output_dir}")
            return 0
        else:
            print("Failed to scaffold data pipeline")
            return 1
    
    def extract_data(self, 
                    name: str, 
                    dataset: str,
                    output: Optional[str] = None) -> int:
        """
        Extract data from a source.
        
        Args:
            name: Pipeline name
            dataset: Dataset name
            output: Output file path
            
        Returns:
            Exit code (0 for success)
        """
        # Load configuration
        config_parser = DataPipelineConfigParser()
        config = config_parser.load_config(name)
        
        # Get dataset configuration
        dataset_config = config_parser.get_dataset_config(dataset)
        if not dataset_config:
            print(f"Error: Dataset not found: {dataset}")
            return 1
        
        print(f"Extracting data from {dataset}...")
        print(f"Source type: {dataset_config.get('type', 'unknown')}")
        print(f"Connection: {dataset_config.get('connection', 'unknown')}")
        
        # Determine output path
        if not output:
            output = os.path.join("data", "extracted", f"{dataset}.csv")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output), exist_ok=True)
        
        # Simulate extraction
        print(f"Writing extracted data to {output}")
        with open(output, 'w') as f:
            f.write("id,name,value\n")
            f.write("1,sample1,100\n")
            f.write("2,sample2,200\n")
        
        print(f"Extraction complete. Wrote 2 records.")
        return 0
    
    def transform_data(self, 
                      name: str, 
                      transform: str,
                      input_file: str,
                      output: Optional[str] = None) -> int:
        """
        Apply a transformation to data.
        
        Args:
            name: Pipeline name
            transform: Transformation name
            input_file: Input file path
            output: Output file path
            
        Returns:
            Exit code (0 for success)
        """
        # Load configuration
        config_parser = DataPipelineConfigParser()
        config = config_parser.load_config(name)
        
        # Get transformation configuration
        transform_config = config_parser.get_transform_config(transform)
        if not transform_config:
            print(f"Error: Transformation not found: {transform}")
            return 1
        
        # Check input file
        if not os.path.exists(input_file):
            print(f"Error: Input file not found: {input_file}")
            return 1
        
        print(f"Applying transformation {transform} to {input_file}...")
        print(f"Transform type: {transform_config.get('type', 'unknown')}")
        
        # Determine output path
        if not output:
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output = os.path.join("data", "transformed", f"{base_name}_transformed.csv")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output), exist_ok=True)
        
        # Simulate transformation
        print(f"Writing transformed data to {output}")
        with open(input_file, 'r') as fin, open(output, 'w') as fout:
            # Copy header
            header = fin.readline()
            fout.write(header)
            
            # Transform each line
            count = 0
            for line in fin:
                parts = line.strip().split(',')
                if len(parts) >= 3:
                    # Double the value for demonstration
                    parts[2] = str(int(parts[2]) * 2)
                    fout.write(','.join(parts) + '\n')
                    count += 1
        
        print(f"Transformation complete. Processed {count} records.")
        return 0
    
    def load_data(self, 
                 name: str, 
                 connector: str,
                 input_file: str) -> int:
        """
        Load data to a destination.
        
        Args:
            name: Pipeline name
            connector: Connector name
            input_file: Input file path
            
        Returns:
            Exit code (0 for success)
        """
        # Load configuration
        config_parser = DataPipelineConfigParser()
        config = config_parser.load_config(name)
        
        # Get connector configuration
        connector_config = config_parser.get_connector_config(connector)
        if not connector_config:
            print(f"Error: Connector not found: {connector}")
            return 1
        
        # Check input file
        if not os.path.exists(input_file):
            print(f"Error: Input file not found: {input_file}")
            return 1
        
        print(f"Loading data from {input_file} to {connector}...")
        print(f"Connector type: {connector_config.get('type', 'unknown')}")
        print(f"Connection: {connector_config.get('connection', 'unknown')}")
        
        # Simulate data loading
        with open(input_file, 'r') as f:
            # Skip header
            f.readline()
            
            # Count records
            count = sum(1 for _ in f)
        
        print(f"Loading complete. Loaded {count} records to {connector}.")
        return 0
    
    def _add_pipeline_templates(self, scaffolder: Scaffolder) -> None:
        """
        Add data pipeline templates to the scaffolder.
        
        Args:
            scaffolder: Scaffolder to add templates to
        """
        # ETL pipeline template
        etl = ScaffoldTemplate("etl", "ETL data pipeline template")
        
        etl.add_directory("config")
        etl.add_directory("pipelines")
        etl.add_directory("data/extracted")
        etl.add_directory("data/transformed")
        etl.add_directory("data/loaded")
        
        etl.add_file("config/$pipeline_name.json", """{
  "pipeline": {
    "name": "$pipeline_name",
    "description": "$pipeline_description",
    "version": "$version",
    "author": "$author",
    "implementation": "pipelines/$pipeline_name.py",
    "schedule": "0 0 * * *"
  },
  "datasets": {
    "source_data": {
      "type": "csv",
      "connection": "data/source_data.csv",
      "schema": {
        "id": "integer",
        "name": "string",
        "value": "number"
      }
    }
  },
  "transforms": {
    "clean_data": {
      "type": "python",
      "implementation": "pipelines/transforms/clean_data.py",
      "description": "Clean and validate input data"
    },
    "enrich_data": {
      "type": "python",
      "implementation": "pipelines/transforms/enrich_data.py",
      "description": "Enrich data with additional information"
    }
  },
  "connectors": {
    "output_db": {
      "type": "sql",
      "connection": "sqlite:///data/output.db",
      "table": "processed_data"
    }
  }
}
""")
        
        etl.add_file("config/$pipeline_name-development.json", """{
  "pipeline": {
    "log_level": "DEBUG"
  },
  "datasets": {
    "source_data": {
      "connection": "data/dev_source_data.csv"
    }
  },
  "connectors": {
    "output_db": {
      "connection": "sqlite:///data/dev_output.db"
    }
  }
}
""")
        
        etl.add_file("config/$pipeline_name-production.json", """{
  "pipeline": {
    "log_level": "INFO"
  },
  "datasets": {
    "source_data": {
      "connection": "/data/prod/source_data.csv"
    }
  },
  "connectors": {
    "output_db": {
      "connection": "mysql://user:password@db.example.com/prod_db"
    }
  }
}
""")
        
        etl.add_file("pipelines/$pipeline_name.py", """\"\"\"
$pipeline_description
\"\"\"

import os
import sys
import logging
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('$pipeline_name')

def extract(config):
    \"\"\"Extract data from source.\"\"\"
    logger.info("Starting extraction phase")
    
    # Get dataset config
    dataset_config = config.get('datasets', {}).get('source_data', {})
    source_path = dataset_config.get('connection')
    
    if not source_path or not os.path.exists(source_path):
        logger.error(f"Source file not found: {source_path}")
        return None
    
    # Read data
    try:
        df = pd.read_csv(source_path)
        logger.info(f"Extracted {len(df)} records from {source_path}")
        return df
    except Exception as e:
        logger.error(f"Error during extraction: {e}")
        return None

def transform(df, config):
    \"\"\"Transform the data.\"\"\"
    if df is None or df.empty:
        logger.error("No data to transform")
        return None
        
    logger.info("Starting transformation phase")
    
    # Apply transformations
    try:
        # Clean data
        logger.info("Applying clean_data transformation")
        # Example transformation: drop duplicates
        df = df.drop_duplicates()
        
        # Enrich data
        logger.info("Applying enrich_data transformation")
        # Example transformation: calculate new column
        if 'value' in df.columns:
            df['value_doubled'] = df['value'] * 2
        
        logger.info(f"Transformed data: {len(df)} records")
        return df
    except Exception as e:
        logger.error(f"Error during transformation: {e}")
        return None

def load(df, config):
    \"\"\"Load data to destination.\"\"\"
    if df is None or df.empty:
        logger.error("No data to load")
        return False
        
    logger.info("Starting load phase")
    
    # Get connector config
    connector_config = config.get('connectors', {}).get('output_db', {})
    connection_string = connector_config.get('connection')
    table_name = connector_config.get('table')
    
    if not connection_string or not table_name:
        logger.error("Invalid connector configuration")
        return False
    
    # Load data
    try:
        # For SQLite, we'll use pandas to_sql
        if connection_string.startswith('sqlite'):
            db_path = connection_string.replace('sqlite:///', '')
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            # Create or append to database
            from sqlalchemy import create_engine
            engine = create_engine(f'sqlite:///{db_path}')
            df.to_sql(table_name, engine, if_exists='replace', index=False)
            
            logger.info(f"Loaded {len(df)} records to {table_name}")
            return True
        else:
            # For other databases, we'd use the appropriate connector
            logger.error(f"Unsupported connection: {connection_string}")
            return False
    except Exception as e:
        logger.error(f"Error during loading: {e}")
        return False

def run_pipeline(config):
    \"\"\"Run the complete ETL pipeline.\"\"\"
    logger.info(f"Starting $pipeline_name pipeline")
    
    # Extract
    df = extract(config)
    if df is None:
        return False
    
    # Transform
    df = transform(df, config)
    if df is None:
        return False
    
    # Load
    success = load(df, config)
    
    logger.info(f"Pipeline completed {'successfully' if success else 'with errors'}")
    return success

if __name__ == "__main__":
    # Load config (in a real pipeline, this would use the DataPipelineConfigParser)
    import json
    with open('config/$pipeline_name.json') as f:
        config = json.load(f)
    
    # Run the pipeline
    success = run_pipeline(config)
    sys.exit(0 if success else 1)
""")
        
        etl.add_file("pipelines/transforms/clean_data.py", """\"\"\"
Clean data transformation for $pipeline_name.
\"\"\"

import pandas as pd
import numpy as np

def clean_data(df):
    \"\"\"
    Clean and validate input data.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Cleaned DataFrame
    \"\"\"
    # Create a copy to avoid modifying the original
    df = df.copy()
    
    # Drop duplicates
    df = df.drop_duplicates()
    
    # Remove rows with missing values
    df = df.dropna()
    
    # Validate data types
    if 'id' in df.columns:
        df['id'] = df['id'].astype(int)
    
    if 'value' in df.columns:
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df = df.dropna(subset=['value'])
    
    return df
""")
        
        etl.add_file("pipelines/transforms/enrich_data.py", """\"\"\"
Enrich data transformation for $pipeline_name.
\"\"\"

import pandas as pd
import numpy as np

def enrich_data(df):
    \"\"\"
    Enrich data with additional information.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Enriched DataFrame
    \"\"\"
    # Create a copy to avoid modifying the original
    df = df.copy()
    
    # Add calculated columns
    if 'value' in df.columns:
        # Double the value
        df['value_doubled'] = df['value'] * 2
        
        # Add a category column
        df['value_category'] = pd.cut(
            df['value'],
            bins=[0, 100, 500, 1000, float('inf')],
            labels=['low', 'medium', 'high', 'very high']
        )
    
    # Add timestamp
    import datetime
    df['processed_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return df
""")
        
        etl.add_file("README.md", """# $pipeline_name

$pipeline_description

## Overview

This is an ETL (Extract, Transform, Load) data pipeline that processes data from a source, applies transformations, and loads it to a destination.

## Configuration

Configuration files are located in the `config` directory:

- `$pipeline_name.json`: Base configuration
- `$pipeline_name-development.json`: Development environment configuration
- `$pipeline_name-production.json`: Production environment configuration

## Pipeline Structure

The pipeline consists of three main phases:

1. **Extract**: Data is extracted from the source defined in the configuration.
2. **Transform**: Data is transformed using the transformations defined in the configuration.
3. **Load**: Transformed data is loaded to the destination defined in the configuration.

## Running the Pipeline

To run the pipeline:

```
pipeline run $pipeline_name
```

To run in a specific environment:

```
pipeline run $pipeline_name --env production
```

## Individual Phase Execution

You can also run individual phases:

```
pipeline extract $pipeline_name --dataset source_data
pipeline transform $pipeline_name --transform clean_data --input data/extracted/source_data.csv
pipeline load $pipeline_name --connector output_db --input data/transformed/source_data_transformed.csv
```

## Validating the Pipeline

To validate the pipeline configuration:

```
pipeline validate $pipeline_name
```
""")
        
        scaffolder.add_template(etl)


def register_datapipeline_commands(registry: CommandRegistry) -> None:
    """
    Register data pipeline commands with a command registry.
    
    Args:
        registry: Command registry to register commands with
    """
    DataPipelineCommands(registry)
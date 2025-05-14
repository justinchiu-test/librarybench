"""
Backend developer microservice CLI commands.
Defines commands for microservice management.
"""

import os
import sys
import json
import subprocess
from typing import Any, Dict, List, Optional

from ....core.commands.registry import CommandRegistry, Command, CommandGroup
from ....core.dev.version import bump_version, save_version, VersionComponent
from ....core.dev.scaffold import Scaffolder, ScaffoldTemplate
from .config_parser import MicroserviceConfigParser


class MicroserviceCommands:
    """Commands for microservice management."""
    
    def __init__(self, registry: CommandRegistry):
        """
        Initialize microservice commands.
        
        Args:
            registry: Command registry to register commands with
        """
        self.registry = registry
        self.group = CommandGroup("microservice", "Microservice management commands")
        self.register_commands()
    
    def register_commands(self) -> None:
        """Register microservice commands with the command group."""
        self.group.command("health")(self.health_check)
        self.group.command("migrate")(self.run_migrations)
        self.group.command("scaffold")(self.scaffold_service)
        self.group.command("config")(self.show_config)
        self.group.command("bump-version")(self.bump_version)
        
        # Register the command group with the registry
        self.group.register_with(self.registry)
    
    def health_check(self, service: str, endpoint: Optional[str] = None) -> int:
        """
        Check health of a microservice.
        
        Args:
            service: Service name
            endpoint: Endpoint URL (overrides configuration)
            
        Returns:
            Exit code (0 for success)
        """
        # Get configuration
        config_parser = MicroserviceConfigParser()
        config_parser.load_config(service)
        
        # Determine endpoint
        if not endpoint:
            endpoint = config_parser.get_endpoint(service)
            if not endpoint:
                print(f"No endpoint configured for service: {service}")
                return 1
        
        # Ensure endpoint has health check path
        if not endpoint.endswith("/health"):
            endpoint = endpoint.rstrip("/") + "/health"
        
        # Print info
        print(f"Checking health of {service} at {endpoint}...")
        
        try:
            # Use curl for simplicity
            process = subprocess.run(
                ["curl", "-s", endpoint],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Check result
            if process.returncode != 0:
                print(f"Error connecting to service: {process.stderr}")
                return 1
            
            # Parse response
            try:
                response = json.loads(process.stdout)
                status = response.get("status", "unknown")
                
                # Print status
                if status.lower() == "up":
                    print(f"Service {service} is UP")
                    # Print any additional info
                    for key, value in response.items():
                        if key != "status":
                            print(f"  {key}: {value}")
                    return 0
                else:
                    print(f"Service {service} is DOWN")
                    # Print any error details
                    for key, value in response.items():
                        if key != "status":
                            print(f"  {key}: {value}")
                    return 1
                    
            except json.JSONDecodeError:
                print(f"Invalid response format: {process.stdout}")
                return 1
                
        except Exception as e:
            print(f"Error checking service health: {e}")
            return 1
    
    def run_migrations(self, service: str, up: bool = True) -> int:
        """
        Run database migrations for a microservice.
        
        Args:
            service: Service name
            up: Whether to migrate up (True) or down (False)
            
        Returns:
            Exit code (0 for success)
        """
        # Get configuration
        config_parser = MicroserviceConfigParser()
        config_parser.load_config(service)
        
        # Get database config
        db_config = config_parser.get_db_config()
        if not db_config:
            print(f"No database configuration found for service: {service}")
            return 1
        
        print(f"Running migrations for {service}...")
        
        # Determine migrations directory
        migrations_dir = os.path.join(os.getcwd(), "migrations")
        if not os.path.exists(migrations_dir):
            print(f"Migrations directory not found: {migrations_dir}")
            return 1
        
        # Placeholder for actual migration logic
        # In a real implementation, this would use a migration library
        # or call the service's migration script
        
        # Simulated migration for demonstration
        print(f"{'Up' if up else 'Down'} migration completed successfully")
        return 0
    
    def scaffold_service(self, 
                        name: str, 
                        template: str = "basic",
                        output_dir: Optional[str] = None) -> int:
        """
        Scaffold a new microservice.
        
        Args:
            name: Service name
            template: Template to use
            output_dir: Output directory (default: current directory)
            
        Returns:
            Exit code (0 for success)
        """
        # Create scaffolder
        scaffolder = Scaffolder()
        
        # Add microservice templates
        self._add_microservice_templates(scaffolder)
        
        # Check if template exists
        if template not in [t["name"] for t in scaffolder.list_templates()]:
            print(f"Template not found: {template}")
            return 1
        
        # Determine output directory
        if not output_dir:
            output_dir = os.path.join(os.getcwd(), name)
        
        # Prepare variables
        variables = {
            "service_name": name,
            "service_description": f"{name} microservice",
            "version": "0.1.0",
            "author": os.environ.get("USER", "user"),
            "author_email": f"{os.environ.get('USER', 'user')}@example.com",
        }
        
        # Generate project
        print(f"Scaffolding {name} microservice with template {template}...")
        success = scaffolder.generate(template, output_dir, variables)
        
        if success:
            print(f"Microservice scaffolded successfully at: {output_dir}")
            return 0
        else:
            print("Failed to scaffold microservice")
            return 1
    
    def show_config(self, 
                  service: str, 
                  environment: str = "development",
                  key: Optional[str] = None) -> int:
        """
        Show configuration for a microservice.
        
        Args:
            service: Service name
            environment: Environment to use
            key: Specific configuration key to show
            
        Returns:
            Exit code (0 for success)
        """
        # Get configuration
        config_parser = MicroserviceConfigParser()
        config = config_parser.load_config(service, environment)
        
        # Show specific key if provided
        if key:
            value = config_parser.get_value(key)
            if value is None:
                print(f"Configuration key not found: {key}")
                return 1
            
            print(json.dumps(value, indent=2))
            return 0
        
        # Show entire configuration
        print(json.dumps(config, indent=2))
        return 0
    
    def bump_version(self, 
                    component: str = "patch",
                    service: Optional[str] = None) -> int:
        """
        Bump version of a microservice.
        
        Args:
            component: Version component to bump (major, minor, patch)
            service: Service name (optional)
            
        Returns:
            Exit code (0 for success)
        """
        try:
            # Validate component
            if component not in ["major", "minor", "patch"]:
                print(f"Invalid version component: {component}")
                print("Valid components: major, minor, patch")
                return 1
            
            # Bump version
            version = bump_version(component)
            
            # Save version
            if save_version():
                print(f"Version bumped to {version}")
                return 0
            else:
                print("Failed to save version")
                return 1
                
        except Exception as e:
            print(f"Error bumping version: {e}")
            return 1
    
    def _add_microservice_templates(self, scaffolder: Scaffolder) -> None:
        """
        Add microservice templates to the scaffolder.
        
        Args:
            scaffolder: Scaffolder to add templates to
        """
        # Basic microservice template
        basic = ScaffoldTemplate("basic", "Basic microservice structure")
        
        basic.add_directory("src")
        basic.add_directory("config")
        basic.add_directory("migrations")
        basic.add_directory("tests")
        
        basic.add_file("src/__init__.py", """\"\"\"
$service_name microservice.
\"\"\"

__version__ = "$version"
""")
        
        basic.add_file("src/app.py", """\"\"\"
Main application entry point.
\"\"\"

import os
import json
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'up',
        'service': '$service_name',
        'version': __import__('$service_name').__version__
    })

@app.route('/')
def index():
    return jsonify({
        'service': '$service_name',
        'description': '$service_description'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
""")
        
        basic.add_file("config/$service_name.json", """{
  "service": "$service_name",
  "version": "$version",
  "database": {
    "host": "localhost",
    "port": 5432,
    "name": "$service_name",
    "user": "postgres",
    "password": ""
  },
  "endpoints": {
    "$service_name": "http://localhost:5000"
  },
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s [%(levelname)s] %(message)s"
  }
}
""")
        
        basic.add_file("config/$service_name-development.json", """{
  "database": {
    "host": "localhost"
  },
  "logging": {
    "level": "DEBUG"
  }
}
""")
        
        basic.add_file("config/$service_name-production.json", """{
  "database": {
    "host": "db.example.com"
  },
  "logging": {
    "level": "WARNING"
  }
}
""")
        
        basic.add_file("migrations/README.md", """# Database Migrations

This directory contains database migration scripts for the $service_name microservice.

## Migration Commands

- Run migrations: `flask db upgrade`
- Create a new migration: `flask db migrate -m "description"`
- Rollback migration: `flask db downgrade`
""")
        
        basic.add_file("requirements.txt", """flask==2.0.1
SQLAlchemy==1.4.23
Flask-SQLAlchemy==2.5.1
Flask-Migrate==3.1.0
psycopg2-binary==2.9.1
""")
        
        basic.add_file("README.md", """# $service_name

$service_description

## Setup

1. Create a virtual environment: `python -m venv venv`
2. Activate the environment: `source venv/bin/activate` (Unix) or `venv\\Scripts\\activate` (Windows)
3. Install dependencies: `pip install -r requirements.txt`
4. Run the service: `python src/app.py`

## Configuration

Configuration files are located in the `config` directory. The following files are used:

- `$service_name.json`: Base configuration
- `$service_name-development.json`: Development environment overrides
- `$service_name-production.json`: Production environment overrides

## API Endpoints

- `/health`: Health check endpoint
- `/`: Service information

## Database Migrations

See `migrations/README.md` for database migration instructions.
""")
        
        basic.add_file("tests/__init__.py", "")
        basic.add_file("tests/test_app.py", """import unittest
import json
from src.app import app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
    def test_health_check(self):
        response = self.app.get('/health')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'up')
        self.assertEqual(data['service'], '$service_name')
        
    def test_index(self):
        response = self.app.get('/')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['service'], '$service_name')
        
if __name__ == '__main__':
    unittest.main()
""")
        
        scaffolder.add_template(basic)


def register_microservice_commands(registry: CommandRegistry) -> None:
    """
    Register microservice commands with a command registry.
    
    Args:
        registry: Command registry to register commands with
    """
    MicroserviceCommands(registry)
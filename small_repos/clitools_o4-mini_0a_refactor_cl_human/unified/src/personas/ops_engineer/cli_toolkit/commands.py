"""
Ops engineer CLI commands.
Defines commands for infrastructure automation.
"""

import os
import sys
import json
import datetime
import subprocess
from typing import Any, Dict, List, Optional, Tuple

from ....core.commands.registry import CommandRegistry, Command, CommandGroup
from ....core.dev.scaffold import Scaffolder, ScaffoldTemplate
from .config_parser import InfraConfigParser


class InfraCommands:
    """Commands for infrastructure automation."""
    
    def __init__(self, registry: CommandRegistry):
        """
        Initialize infrastructure commands.
        
        Args:
            registry: Command registry to register commands with
        """
        self.registry = registry
        self.group = CommandGroup("infra", "Infrastructure automation commands")
        self.register_commands()
    
    def register_commands(self) -> None:
        """Register infrastructure commands with the command group."""
        self.group.command("deploy")(self.deploy_infrastructure)
        self.group.command("status")(self.check_status)
        self.group.command("destroy")(self.destroy_infrastructure)
        self.group.command("validate")(self.validate_infrastructure)
        self.group.command("scaffold")(self.scaffold_project)
        self.group.command("plan")(self.plan_changes)
        self.group.command("diff")(self.diff_infrastructure)
        
        # Register the command group with the registry
        self.group.register_with(self.registry)
    
    def deploy_infrastructure(self, 
                             project: str,
                             env: str = "development",
                             resource: Optional[str] = None) -> int:
        """
        Deploy infrastructure resources.
        
        Args:
            project: Project name
            env: Environment to deploy to
            resource: Specific resource to deploy (None for all)
            
        Returns:
            Exit code (0 for success)
        """
        # Load configuration
        config_parser = InfraConfigParser()
        config = config_parser.load_config(project, env)
        
        print(f"Deploying {project} infrastructure to {env} environment")
        if resource:
            print(f"Deploying specific resource: {resource}")
        
        # Get provider configuration
        providers = config.get("providers", {})
        if not providers:
            print("Error: No providers configured")
            return 1
        
        # Default provider
        default_provider = next(iter(providers.keys()))
        
        # Simulate deployment
        print(f"Using provider: {default_provider}")
        
        # If deploying a specific resource
        if resource:
            resource_type, resource_name = self._parse_resource_identifier(resource)
            
            if not resource_type or not resource_name:
                print(f"Error: Invalid resource identifier: {resource}")
                print("Format should be: type:name (e.g., server:web-server)")
                return 1
                
            # Get resource configuration
            resource_config = config_parser.get_resource_config(resource_type, resource_name)
            if not resource_config:
                print(f"Error: Resource not found: {resource}")
                return 1
                
            print(f"Deploying {resource_type}: {resource_name}")
            
            # Simulate deployment steps
            print("- Preparing resources...")
            print("- Creating infrastructure...")
            print("- Configuring resources...")
            print("- Running post-deploy hooks...")
            
            print(f"Resource {resource} deployed successfully")
            
        else:
            # Deploy entire infrastructure
            
            # Simulate deployment steps
            print("- Validating configuration...")
            print("- Planning deployment...")
            print("- Creating infrastructure...")
            print("- Configuring resources...")
            print("- Running post-deploy hooks...")
            
            # Show a summary of deployed resources
            resources = self._count_resources(config)
            print("\nDeployment summary:")
            for res_type, count in resources.items():
                print(f"- {res_type}: {count} resources")
                
            print(f"\nInfrastructure deployed successfully to {env} environment")
        
        return 0
    
    def check_status(self, 
                    project: str,
                    env: str = "development",
                    resource: Optional[str] = None) -> int:
        """
        Check status of deployed infrastructure.
        
        Args:
            project: Project name
            env: Environment to check
            resource: Specific resource to check (None for all)
            
        Returns:
            Exit code (0 for success)
        """
        # Load configuration
        config_parser = InfraConfigParser()
        config = config_parser.load_config(project, env)
        
        print(f"Checking status of {project} infrastructure in {env} environment")
        
        # Simulate status check
        if resource:
            resource_type, resource_name = self._parse_resource_identifier(resource)
            
            if not resource_type or not resource_name:
                print(f"Error: Invalid resource identifier: {resource}")
                print("Format should be: type:name (e.g., server:web-server)")
                return 1
                
            # Get resource configuration
            resource_config = config_parser.get_resource_config(resource_type, resource_name)
            if not resource_config:
                print(f"Error: Resource not found: {resource}")
                return 1
                
            print(f"Status of {resource_type}: {resource_name}")
            print(f"- State: RUNNING")
            print(f"- Created: 2023-04-15 10:30:00")
            print(f"- Last updated: 2023-04-16 14:22:15")
            
            # Show resource-specific details
            if resource_type == "servers":
                print(f"- IP Address: 10.0.0.1")
                print(f"- CPU: 2 cores, Memory: 4GB")
                print(f"- Uptime: 13 days, 2 hours")
            elif resource_type == "databases":
                print(f"- Engine: MySQL 8.0")
                print(f"- Size: 10GB")
                print(f"- Connections: 5 active")
            elif resource_type == "storage":
                print(f"- Type: S3 Compatible")
                print(f"- Size: 50GB")
                print(f"- Objects: 1237")
        else:
            # Show status of all resources
            print("\nResources summary:")
            
            # Servers
            servers = config.get("servers", {})
            print(f"\nServers:")
            for name in servers.keys():
                print(f"- {name}: RUNNING")
                
            # Databases
            databases = config.get("databases", {})
            print(f"\nDatabases:")
            for name in databases.keys():
                print(f"- {name}: RUNNING")
                
            # Storage
            storage = config.get("storage", {})
            print(f"\nStorage:")
            for name in storage.keys():
                print(f"- {name}: AVAILABLE")
                
            # Networking
            networking = config.get("networking", {})
            print(f"\nNetworking:")
            for name in networking.keys():
                print(f"- {name}: CONFIGURED")
                
            print(f"\nAll infrastructure is running properly in {env} environment")
        
        return 0
    
    def destroy_infrastructure(self, 
                              project: str,
                              env: str = "development",
                              resource: Optional[str] = None,
                              force: bool = False) -> int:
        """
        Destroy deployed infrastructure.
        
        Args:
            project: Project name
            env: Environment to destroy
            resource: Specific resource to destroy (None for all)
            force: Whether to force destruction without confirmation
            
        Returns:
            Exit code (0 for success)
        """
        # Load configuration
        config_parser = InfraConfigParser()
        config = config_parser.load_config(project, env)
        
        if resource:
            target = f"resource {resource} in {env} environment"
        else:
            target = f"ALL resources in {env} environment"
            
        print(f"WARNING: About to destroy {target}")
        
        # Ask for confirmation if not forced
        if not force:
            confirmation = input(f"Are you sure you want to destroy {target}? This action cannot be undone. [y/N]: ")
            if confirmation.lower() != 'y':
                print("Destruction cancelled")
                return 0
        
        print(f"Destroying {target}...")
        
        # Simulate destruction
        if resource:
            resource_type, resource_name = self._parse_resource_identifier(resource)
            
            if not resource_type or not resource_name:
                print(f"Error: Invalid resource identifier: {resource}")
                print("Format should be: type:name (e.g., server:web-server)")
                return 1
                
            # Get resource configuration
            resource_config = config_parser.get_resource_config(resource_type, resource_name)
            if not resource_config:
                print(f"Error: Resource not found: {resource}")
                return 1
                
            print(f"- Removing {resource_type}: {resource_name}...")
            print(f"Resource {resource} destroyed successfully")
            
        else:
            # Destroy entire infrastructure
            
            # Simulate destruction steps in reverse order
            print("- Running pre-destroy hooks...")
            print("- Destroying resources...")
            print("- Cleaning up configurations...")
            
            # Show a summary of destroyed resources
            resources = self._count_resources(config)
            print("\nDestruction summary:")
            for res_type, count in resources.items():
                print(f"- {res_type}: {count} resources destroyed")
                
            print(f"\nAll infrastructure in {env} environment has been destroyed")
        
        return 0
    
    def validate_infrastructure(self, 
                              project: str,
                              env: str = "development") -> int:
        """
        Validate infrastructure configuration.
        
        Args:
            project: Project name
            env: Environment to validate
            
        Returns:
            Exit code (0 for success)
        """
        # Load configuration
        config_parser = InfraConfigParser()
        config = config_parser.load_config(project, env)
        
        print(f"Validating {project} infrastructure configuration for {env} environment")
        
        # Validate configuration
        errors = []
        warnings = []
        
        # Check for required sections
        required_sections = ["providers"]
        for section in required_sections:
            if section not in config or not config[section]:
                errors.append(f"Missing required section: {section}")
        
        # Check provider configuration
        providers = config.get("providers", {})
        for provider_name, provider_config in providers.items():
            if "type" not in provider_config:
                errors.append(f"Missing 'type' in provider: {provider_name}")
            if "credentials" not in provider_config:
                warnings.append(f"No credentials specified for provider: {provider_name}")
        
        # Check resource dependencies
        # (This would be more complex in a real implementation)
        
        # Check for security issues
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
            print("\nValidation successful! Infrastructure configuration is valid.")
        elif not errors:
            print("\nValidation successful with warnings.")
        else:
            print("\nValidation failed. Please fix the errors and try again.")
            return 1
        
        print(f"\nResources to be managed:")
        resources = self._count_resources(config)
        for res_type, count in resources.items():
            print(f"- {res_type}: {count} resources")
            
        return 0
    
    def scaffold_project(self, 
                        name: str, 
                        template: str = "terraform",
                        provider: str = "aws",
                        output_dir: Optional[str] = None) -> int:
        """
        Scaffold a new infrastructure project.
        
        Args:
            name: Project name
            template: Template to use
            provider: Cloud provider to use
            output_dir: Output directory (default: current directory)
            
        Returns:
            Exit code (0 for success)
        """
        # Create scaffolder
        scaffolder = Scaffolder()
        
        # Add infrastructure templates
        self._add_infra_templates(scaffolder)
        
        # Check if template exists
        if template not in [t["name"] for t in scaffolder.list_templates()]:
            print(f"Template not found: {template}")
            print("Available templates:")
            for tmpl in scaffolder.list_templates():
                print(f"- {tmpl['name']}: {tmpl['description']}")
            return 1
        
        # Determine output directory
        if not output_dir:
            output_dir = os.path.join(os.getcwd(), name)
        
        # Prepare variables
        variables = {
            "project_name": name,
            "project_description": f"{name} infrastructure",
            "provider": provider,
            "author": os.environ.get("USER", "user"),
        }
        
        # Generate project
        print(f"Scaffolding {name} infrastructure project with template {template}...")
        success = scaffolder.generate(template, output_dir, variables)
        
        if success:
            print(f"Infrastructure project scaffolded successfully at: {output_dir}")
            print(f"\nNext steps:")
            print(f"1. cd {output_dir}")
            print(f"2. Review configuration in config/{name}.yaml")
            print(f"3. Run: infra validate {name}")
            print(f"4. Run: infra deploy {name}")
            return 0
        else:
            print("Failed to scaffold infrastructure project")
            return 1
    
    def plan_changes(self, 
                    project: str,
                    env: str = "development",
                    resource: Optional[str] = None) -> int:
        """
        Plan infrastructure changes without applying them.
        
        Args:
            project: Project name
            env: Environment to plan for
            resource: Specific resource to plan (None for all)
            
        Returns:
            Exit code (0 for success)
        """
        # Load configuration
        config_parser = InfraConfigParser()
        config = config_parser.load_config(project, env)
        
        print(f"Planning changes for {project} infrastructure in {env} environment")
        if resource:
            print(f"Planning changes for specific resource: {resource}")
        
        # Simulate planning
        if resource:
            resource_type, resource_name = self._parse_resource_identifier(resource)
            
            if not resource_type or not resource_name:
                print(f"Error: Invalid resource identifier: {resource}")
                print("Format should be: type:name (e.g., server:web-server)")
                return 1
                
            # Get resource configuration
            resource_config = config_parser.get_resource_config(resource_type, resource_name)
            if not resource_config:
                print(f"Error: Resource not found: {resource}")
                return 1
                
            print(f"\nPlanned changes for {resource_type}: {resource_name}")
            print(f"+ Create or update resource with the following configuration:")
            for key, value in resource_config.items():
                print(f"  - {key}: {value}")
        else:
            # Plan changes for all resources
            print("\nPlanned changes:")
            
            # Simulate changes for different resource types
            servers = config.get("servers", {})
            if servers:
                print("\nServers:")
                for name, server_config in servers.items():
                    print(f"+ Create or update server: {name}")
                    print(f"  - type: {server_config.get('type', 'unknown')}")
                    print(f"  - size: {server_config.get('size', 'unknown')}")
                    
            databases = config.get("databases", {})
            if databases:
                print("\nDatabases:")
                for name, db_config in databases.items():
                    print(f"+ Create or update database: {name}")
                    print(f"  - engine: {db_config.get('engine', 'unknown')}")
                    print(f"  - size: {db_config.get('size', 'unknown')}")
                    
            storage = config.get("storage", {})
            if storage:
                print("\nStorage:")
                for name, storage_config in storage.items():
                    print(f"+ Create or update storage: {name}")
                    print(f"  - type: {storage_config.get('type', 'unknown')}")
                    print(f"  - size: {storage_config.get('size', 'unknown')}")
                    
            networking = config.get("networking", {})
            if networking:
                print("\nNetworking:")
                for name, net_config in networking.items():
                    print(f"+ Create or update networking: {name}")
                    print(f"  - type: {net_config.get('type', 'unknown')}")
                
            print("\nPlan completed. Above changes will be applied during deployment.")
        
        return 0
    
    def diff_infrastructure(self, 
                          project: str,
                          env: str = "development",
                          resource: Optional[str] = None) -> int:
        """
        Show difference between configuration and deployed infrastructure.
        
        Args:
            project: Project name
            env: Environment to check
            resource: Specific resource to check (None for all)
            
        Returns:
            Exit code (0 for success)
        """
        # Load configuration
        config_parser = InfraConfigParser()
        config = config_parser.load_config(project, env)
        
        print(f"Comparing {project} infrastructure configuration with deployed state in {env} environment")
        
        # Simulate diff calculation
        if resource:
            resource_type, resource_name = self._parse_resource_identifier(resource)
            
            if not resource_type or not resource_name:
                print(f"Error: Invalid resource identifier: {resource}")
                print("Format should be: type:name (e.g., server:web-server)")
                return 1
                
            # Get resource configuration
            resource_config = config_parser.get_resource_config(resource_type, resource_name)
            if not resource_config:
                print(f"Error: Resource not found: {resource}")
                return 1
                
            print(f"\nDifferences for {resource_type}: {resource_name}")
            print(f"  ~ size: 'small' => 'medium'")
            print(f"  + new_property: 'value'")
            print(f"  - old_property: 'value'")
            
        else:
            # Show diffs for all resources
            print("\nDifferences:")
            
            # Server example
            print("\nservers.web-server:")
            print(f"  ~ size: 'small' => 'medium'")
            print(f"  + monitoring: 'enabled'")
            
            # Database example
            print("\ndatabases.main-db:")
            print(f"  ~ engine_version: '8.0' => '8.0.25'")
            print(f"  ~ backup_retention: 7 => 14")
            
            # Storage example
            print("\nstorage.app-data:")
            print(f"  ~ size: '50GB' => '100GB'")
            
            print("\nNo other differences found.")
        
        return 0
    
    def _parse_resource_identifier(self, resource_id: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse a resource identifier in the format type:name.
        
        Args:
            resource_id: Resource identifier string
            
        Returns:
            Tuple of (resource_type, resource_name) or (None, None) if invalid
        """
        if ':' not in resource_id:
            return None, None
            
        parts = resource_id.split(':', 1)
        return parts[0], parts[1]
    
    def _count_resources(self, config: Dict[str, Any]) -> Dict[str, int]:
        """
        Count resources in a configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dictionary of resource type to count
        """
        resource_types = ["servers", "databases", "storage", "networking"]
        counts = {}
        
        for resource_type in resource_types:
            resources = config.get(resource_type, {})
            if resources:
                counts[resource_type] = len(resources)
        
        return counts
    
    def _add_infra_templates(self, scaffolder: Scaffolder) -> None:
        """
        Add infrastructure templates to the scaffolder.
        
        Args:
            scaffolder: Scaffolder to add templates to
        """
        # Terraform template
        terraform = ScaffoldTemplate("terraform", "Terraform infrastructure project template")
        
        terraform.add_directory("config")
        terraform.add_directory("terraform")
        terraform.add_directory("terraform/modules")
        terraform.add_directory("terraform/environments/development")
        terraform.add_directory("terraform/environments/production")
        
        terraform.add_file("config/$project_name.yaml", """# $project_name infrastructure configuration

providers:
  $provider:
    type: "$provider"
    region: "us-west-2"
    credentials:
      method: "env"

# Infrastructure resources
servers:
  web-server:
    type: "t3.micro"
    count: 2
    image: "ami-12345678"
    tags:
      Name: "web-server"
      Environment: "$${environment}"
    
databases:
  main-db:
    engine: "mysql"
    version: "8.0"
    size: "db.t3.small"
    storage: 20
    
storage:
  app-data:
    type: "s3"
    versioning: true
    
networking:
  main-vpc:
    cidr: "10.0.0.0/16"
    subnets:
      public:
        - "10.0.1.0/24"
        - "10.0.2.0/24"
      private:
        - "10.0.3.0/24"
        - "10.0.4.0/24"
""")
        
        terraform.add_file("config/$project_name-development.yaml", """# Development environment configuration

providers:
  $provider:
    region: "us-west-2"

servers:
  web-server:
    type: "t3.micro"
    count: 1
    
databases:
  main-db:
    size: "db.t3.small"
    
storage:
  app-data:
    lifecycle_rules:
      - expiration: 30
""")
        
        terraform.add_file("config/$project_name-production.yaml", """# Production environment configuration

providers:
  $provider:
    region: "us-east-1"

servers:
  web-server:
    type: "t3.medium"
    count: 3
    
databases:
  main-db:
    size: "db.t3.medium"
    backup_retention: 14
    
storage:
  app-data:
    lifecycle_rules:
      - expiration: 365
""")
        
        terraform.add_file("terraform/main.tf", """# Main Terraform configuration for $project_name

terraform {
  required_version = ">= 1.0.0"
  
  required_providers {
    $provider = {
      source  = "hashicorp/$provider"
      version = "~> 4.0"
    }
  }
  
  backend "s3" {
    bucket = "${var.project_name}-terraform-state"
    key    = "${var.environment}/terraform.tfstate"
    region = "us-west-2"
  }
}

provider "$provider" {
  region = var.region
}

# Import modules
module "network" {
  source      = "./modules/network"
  environment = var.environment
  vpc_cidr    = var.vpc_cidr
  subnets     = var.subnets
}

module "compute" {
  source        = "./modules/compute"
  environment   = var.environment
  instance_type = var.instance_type
  instance_count = var.instance_count
  vpc_id        = module.network.vpc_id
  subnet_ids    = module.network.public_subnet_ids
}

module "database" {
  source      = "./modules/database"
  environment = var.environment
  engine      = var.db_engine
  version     = var.db_version
  instance    = var.db_instance
  storage     = var.db_storage
  vpc_id      = module.network.vpc_id
  subnet_ids  = module.network.private_subnet_ids
}

module "storage" {
  source      = "./modules/storage"
  environment = var.environment
  versioning  = var.storage_versioning
}
""")
        
        terraform.add_file("terraform/variables.tf", """# Variables for $project_name infrastructure

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "$project_name"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "development"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

# Network variables
variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "subnets" {
  description = "Subnet configuration"
  type        = object({
    public  = list(string)
    private = list(string)
  })
  default     = {
    public  = ["10.0.1.0/24", "10.0.2.0/24"]
    private = ["10.0.3.0/24", "10.0.4.0/24"]
  }
}

# Compute variables
variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "instance_count" {
  description = "Number of instances to launch"
  type        = number
  default     = 2
}

# Database variables
variable "db_engine" {
  description = "Database engine"
  type        = string
  default     = "mysql"
}

variable "db_version" {
  description = "Database engine version"
  type        = string
  default     = "8.0"
}

variable "db_instance" {
  description = "Database instance type"
  type        = string
  default     = "db.t3.small"
}

variable "db_storage" {
  description = "Database storage in GB"
  type        = number
  default     = 20
}

# Storage variables
variable "storage_versioning" {
  description = "Enable versioning for S3 buckets"
  type        = bool
  default     = true
}
""")
        
        terraform.add_file("terraform/outputs.tf", """# Outputs for $project_name infrastructure

output "vpc_id" {
  description = "ID of the VPC"
  value       = module.network.vpc_id
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = module.network.public_subnet_ids
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = module.network.private_subnet_ids
}

output "instance_ids" {
  description = "IDs of the EC2 instances"
  value       = module.compute.instance_ids
}

output "instance_public_ips" {
  description = "Public IPs of the EC2 instances"
  value       = module.compute.public_ips
}

output "database_endpoint" {
  description = "Endpoint of the database"
  value       = module.database.endpoint
}

output "bucket_name" {
  description = "Name of the S3 bucket"
  value       = module.storage.bucket_name
}
""")
        
        terraform.add_file("terraform/modules/network/main.tf", """# Network module for $project_name

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  
  tags = {
    Name        = "${var.project_name}-vpc-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_subnet" "public" {
  count             = length(var.subnets.public)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.subnets.public[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = {
    Name        = "${var.project_name}-public-subnet-${count.index}-${var.environment}"
    Environment = var.environment
  }
}

resource "aws_subnet" "private" {
  count             = length(var.subnets.private)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.subnets.private[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = {
    Name        = "${var.project_name}-private-subnet-${count.index}-${var.environment}"
    Environment = var.environment
  }
}

# Internet Gateway for public subnets
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  
  tags = {
    Name        = "${var.project_name}-igw-${var.environment}"
    Environment = var.environment
  }
}

# Route table for public subnets
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  
  tags = {
    Name        = "${var.project_name}-public-rt-${var.environment}"
    Environment = var.environment
  }
}

# Route table associations for public subnets
resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Data source for availability zones
data "aws_availability_zones" "available" {}
""")
        
        terraform.add_file("terraform/modules/network/variables.tf", """# Variables for network module

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "$project_name"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
}

variable "subnets" {
  description = "Subnet configuration"
  type        = object({
    public  = list(string)
    private = list(string)
  })
}
""")
        
        terraform.add_file("terraform/modules/network/outputs.tf", """# Outputs for network module

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = aws_subnet.private[*].id
}
""")
        
        terraform.add_file("terraform/environments/development/terraform.tfvars", """# Development environment configuration

environment    = "development"
region         = "us-west-2"
instance_type  = "t3.micro"
instance_count = 1
db_instance    = "db.t3.small"
""")
        
        terraform.add_file("terraform/environments/production/terraform.tfvars", """# Production environment configuration

environment    = "production"
region         = "us-east-1"
instance_type  = "t3.medium"
instance_count = 3
db_instance    = "db.t3.medium"
""")
        
        terraform.add_file("README.md", """# $project_name Infrastructure

$project_description

## Overview

This repository contains the infrastructure configuration for the $project_name project.

## Prerequisites

- Terraform >= 1.0.0
- AWS CLI configured with appropriate credentials
- Python 3.8+ (for configuration processing)

## Quick Start

1. Clone this repository
2. Review and modify the configuration in `config/$project_name.yaml`
3. Initialize Terraform:

```
cd terraform
terraform init -backend-config="environments/development/backend.tfvars"
```

4. Plan and apply the infrastructure:

```
terraform plan -var-file="environments/development/terraform.tfvars"
terraform apply -var-file="environments/development/terraform.tfvars"
```

## Using the Infra CLI

This project includes a CLI for managing infrastructure:

```
# Validate configuration
infra validate $project_name

# Plan changes
infra plan $project_name

# Deploy infrastructure
infra deploy $project_name

# Check status
infra status $project_name

# Destroy infrastructure
infra destroy $project_name
```

## Configuration

The infrastructure configuration is defined in YAML files in the `config` directory:

- `$project_name.yaml`: Base configuration
- `$project_name-development.yaml`: Development environment configuration
- `$project_name-production.yaml`: Production environment configuration

## Environments

The following environments are supported:

- `development`: For development and testing
- `production`: For production deployments

## Components

- **Network**: VPC, subnets, security groups
- **Compute**: EC2 instances
- **Database**: RDS database
- **Storage**: S3 buckets
""")
        
        scaffolder.add_template(terraform)


def register_infra_commands(registry: CommandRegistry) -> None:
    """
    Register infrastructure commands with a command registry.
    
    Args:
        registry: Command registry to register commands with
    """
    InfraCommands(registry)
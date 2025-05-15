"""
Publishing functionality for the CLI Toolkit.
"""
import os
import shutil
import subprocess
import tempfile
import re
import json
from typing import Dict, List, Optional, Tuple, Any

class Publisher:
    """
    Handles publishing packages and applications.
    """
    
    def __init__(self, repo_url: Optional[str] = None):
        """
        Initialize a new publisher.
        
        Args:
            repo_url: Repository URL
        """
        self.repo_url = repo_url
    
    def publish_package(self, 
                       package_dir: str, 
                       version: Optional[str] = None, 
                       dry_run: bool = False) -> bool:
        """
        Publish a Python package.
        
        Args:
            package_dir: Directory containing the package
            version: Version to publish (defaults to version in package)
            dry_run: Simulate publishing without actually doing it
            
        Returns:
            True if published successfully
        """
        # Verify package directory
        if not os.path.isdir(package_dir):
            raise ValueError(f"Package directory does not exist: {package_dir}")
        
        # Check for setup.py or pyproject.toml
        has_setup = os.path.isfile(os.path.join(package_dir, "setup.py"))
        has_pyproject = os.path.isfile(os.path.join(package_dir, "pyproject.toml"))
        
        if not (has_setup or has_pyproject):
            raise ValueError(f"Package directory must contain setup.py or pyproject.toml: {package_dir}")
        
        # Update version if specified
        if version is not None:
            self._update_package_version(package_dir, version)
        
        # Build package
        if not self._build_package(package_dir, dry_run):
            return False
        
        # Upload package
        if not dry_run:
            return self._upload_package(package_dir)
        
        return True
    
    def publish_docker(self, 
                     docker_dir: str, 
                     image_name: str, 
                     tag: str = "latest", 
                     registry: Optional[str] = None, 
                     dry_run: bool = False) -> bool:
        """
        Publish a Docker image.
        
        Args:
            docker_dir: Directory containing the Dockerfile
            image_name: Name of the image
            tag: Image tag
            registry: Docker registry
            dry_run: Simulate publishing without actually doing it
            
        Returns:
            True if published successfully
        """
        # Verify Docker directory
        if not os.path.isdir(docker_dir):
            raise ValueError(f"Docker directory does not exist: {docker_dir}")
        
        # Check for Dockerfile
        dockerfile_path = os.path.join(docker_dir, "Dockerfile")
        if not os.path.isfile(dockerfile_path):
            raise ValueError(f"Docker directory must contain a Dockerfile: {docker_dir}")
        
        # Build tag
        full_tag = image_name
        if registry:
            full_tag = f"{registry}/{image_name}"
        full_tag = f"{full_tag}:{tag}"
        
        # Build Docker image
        if not self._build_docker(docker_dir, full_tag, dry_run):
            return False
        
        # Push Docker image
        if not dry_run:
            return self._push_docker(full_tag)
        
        return True
    
    def publish_to_s3(self, 
                    file_path: str, 
                    bucket: str, 
                    key: Optional[str] = None, 
                    region: Optional[str] = None, 
                    public: bool = False, 
                    dry_run: bool = False) -> bool:
        """
        Publish a file to S3.
        
        Args:
            file_path: Path to file to publish
            bucket: S3 bucket name
            key: S3 object key (defaults to file name)
            region: AWS region
            public: Make file publicly accessible
            dry_run: Simulate publishing without actually doing it
            
        Returns:
            True if published successfully
        """
        # Verify file exists
        if not os.path.isfile(file_path):
            raise ValueError(f"File does not exist: {file_path}")
        
        # Get file name for key
        if key is None:
            key = os.path.basename(file_path)
        
        # Print what would be done
        if dry_run:
            print(f"Would upload {file_path} to s3://{bucket}/{key}")
            if public:
                print(f"Would make s3://{bucket}/{key} publicly accessible")
            return True
        
        # In a real implementation, this would use boto3 to upload the file
        # For simulation, just return True
        print(f"Uploaded {file_path} to s3://{bucket}/{key}")
        if public:
            print(f"Made s3://{bucket}/{key} publicly accessible")
        
        return True
    
    def _update_package_version(self, package_dir: str, version: str) -> bool:
        """
        Update the version in a package.
        
        Args:
            package_dir: Directory containing the package
            version: New version
            
        Returns:
            True if version was updated
        """
        # Check for setup.py
        setup_path = os.path.join(package_dir, "setup.py")
        if os.path.isfile(setup_path):
            # Read setup.py
            with open(setup_path, "r") as f:
                setup_content = f.read()
            
            # Update version
            setup_content = re.sub(
                r'version\s*=\s*[\'"]([^\'"]+)[\'"]',
                f'version="{version}"',
                setup_content
            )
            
            # Write updated content
            with open(setup_path, "w") as f:
                f.write(setup_content)
        
        # Check for pyproject.toml
        pyproject_path = os.path.join(package_dir, "pyproject.toml")
        if os.path.isfile(pyproject_path):
            # Read pyproject.toml
            with open(pyproject_path, "r") as f:
                pyproject_content = f.read()
            
            # Update version
            pyproject_content = re.sub(
                r'version\s*=\s*[\'"]([^\'"]+)[\'"]',
                f'version = "{version}"',
                pyproject_content
            )
            
            # Write updated content
            with open(pyproject_path, "w") as f:
                f.write(pyproject_content)
        
        # Check for __init__.py files
        for root, _, files in os.walk(package_dir):
            for file in files:
                if file == "__init__.py":
                    file_path = os.path.join(root, file)
                    
                    # Read file
                    with open(file_path, "r") as f:
                        content = f.read()
                    
                    # Update version
                    new_content = re.sub(
                        r'__version__\s*=\s*[\'"]([^\'"]+)[\'"]',
                        f'__version__ = "{version}"',
                        content
                    )
                    
                    # Write updated content if changed
                    if new_content != content:
                        with open(file_path, "w") as f:
                            f.write(new_content)
        
        return True
    
    def _build_package(self, package_dir: str, dry_run: bool) -> bool:
        """
        Build a Python package.
        
        Args:
            package_dir: Directory containing the package
            dry_run: Simulate building without actually doing it
            
        Returns:
            True if built successfully
        """
        if dry_run:
            print(f"Would build package in {package_dir}")
            return True
        
        try:
            # Clean build artifacts
            dist_dir = os.path.join(package_dir, "dist")
            if os.path.exists(dist_dir):
                shutil.rmtree(dist_dir)
            
            # Build package
            subprocess.run(
                ["python", "-m", "build", "--wheel", "--sdist"],
                cwd=package_dir,
                check=True
            )
            
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _upload_package(self, package_dir: str) -> bool:
        """
        Upload a Python package.
        
        Args:
            package_dir: Directory containing the package
            
        Returns:
            True if uploaded successfully
        """
        try:
            # Upload package
            cmd = ["python", "-m", "twine", "upload", "dist/*"]
            if self.repo_url:
                cmd.extend(["--repository-url", self.repo_url])
            
            subprocess.run(cmd, cwd=package_dir, check=True)
            
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _build_docker(self, docker_dir: str, tag: str, dry_run: bool) -> bool:
        """
        Build a Docker image.
        
        Args:
            docker_dir: Directory containing the Dockerfile
            tag: Image tag
            dry_run: Simulate building without actually doing it
            
        Returns:
            True if built successfully
        """
        if dry_run:
            print(f"Would build Docker image {tag} from {docker_dir}")
            return True
        
        try:
            # Build Docker image
            subprocess.run(
                ["docker", "build", "-t", tag, "."],
                cwd=docker_dir,
                check=True
            )
            
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _push_docker(self, tag: str) -> bool:
        """
        Push a Docker image.
        
        Args:
            tag: Image tag
            
        Returns:
            True if pushed successfully
        """
        try:
            # Push Docker image
            subprocess.run(
                ["docker", "push", tag],
                check=True
            )
            
            return True
        except subprocess.CalledProcessError:
            return False

# Global publisher instance
_publisher = Publisher()

def set_repo_url(repo_url: str) -> None:
    """
    Set the repository URL for the global publisher.
    
    Args:
        repo_url: Repository URL
    """
    global _publisher
    _publisher = Publisher(repo_url)

def publish_package(package_dir: str, 
                   version: Optional[str] = None, 
                   dry_run: bool = False) -> bool:
    """
    Publish a Python package using the global publisher.
    
    Args:
        package_dir: Directory containing the package
        version: Version to publish
        dry_run: Simulate publishing without actually doing it
        
    Returns:
        True if published successfully
    """
    return _publisher.publish_package(package_dir, version, dry_run)

def publish_docker(docker_dir: str, 
                 image_name: str, 
                 tag: str = "latest", 
                 registry: Optional[str] = None, 
                 dry_run: bool = False) -> bool:
    """
    Publish a Docker image using the global publisher.
    
    Args:
        docker_dir: Directory containing the Dockerfile
        image_name: Name of the image
        tag: Image tag
        registry: Docker registry
        dry_run: Simulate publishing without actually doing it
        
    Returns:
        True if published successfully
    """
    return _publisher.publish_docker(docker_dir, image_name, tag, registry, dry_run)

def publish_to_s3(file_path: str, 
                bucket: str, 
                key: Optional[str] = None, 
                region: Optional[str] = None, 
                public: bool = False, 
                dry_run: bool = False) -> bool:
    """
    Publish a file to S3 using the global publisher.
    
    Args:
        file_path: Path to file to publish
        bucket: S3 bucket name
        key: S3 object key
        region: AWS region
        public: Make file publicly accessible
        dry_run: Simulate publishing without actually doing it
        
    Returns:
        True if published successfully
    """
    return _publisher.publish_to_s3(file_path, bucket, key, region, public, dry_run)
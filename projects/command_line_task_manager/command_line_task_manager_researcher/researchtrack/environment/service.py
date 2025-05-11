import os
import platform
import sys
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Set, Union, Any
from uuid import UUID, uuid4
try:
    from importlib.metadata import distributions
except ImportError:
    # Fallback for Python < 3.8
    try:
        from importlib_metadata import distributions
    except ImportError:
        distributions = None

from .models import (
    EnvironmentSnapshot, 
    EnvironmentType, 
    PackageInfo, 
    PackageManagerType,
    ComputeResource,
    ComputeResourceType,
    OperatingSystemType,
    TaskEnvironmentLink
)
from .storage import EnvironmentStorageInterface


class EnvironmentService:
    """Service for managing computational environment snapshots."""
    
    def __init__(self, storage: EnvironmentStorageInterface):
        """
        Initialize the environment service.
        
        Args:
            storage: The storage implementation to use
        """
        self._storage = storage
    
    # Environment snapshot operations
    
    def create_snapshot(
        self,
        name: str,
        description: Optional[str] = None,
        type: Union[EnvironmentType, str] = EnvironmentType.LOCAL,
        python_version: Optional[str] = None,
        os_type: Optional[Union[OperatingSystemType, str]] = None,
        os_version: Optional[str] = None,
        architecture: Optional[str] = None,
        kernel_version: Optional[str] = None,
        environment_variables: Optional[Dict[str, str]] = None,
        packages: Optional[List[PackageInfo]] = None,
        compute_resources: Optional[List[ComputeResource]] = None,
        config_files: Optional[Dict[str, str]] = None,
        container_image: Optional[str] = None,
        container_tag: Optional[str] = None,
        container_digest: Optional[str] = None,
        cloud_provider: Optional[str] = None,
        cloud_region: Optional[str] = None,
        instance_type: Optional[str] = None,
        git_commit: Optional[str] = None,
        git_repository: Optional[str] = None,
        git_branch: Optional[str] = None,
        tags: Optional[Set[str]] = None,
    ) -> EnvironmentSnapshot:
        """
        Create a new environment snapshot.
        
        Args:
            name: Snapshot name
            description: Snapshot description
            type: Environment type
            python_version: Python version
            os_type: Operating system type
            os_version: Operating system version
            architecture: CPU architecture
            kernel_version: Kernel version
            environment_variables: Environment variables dictionary
            packages: List of package information
            compute_resources: List of compute resources
            config_files: Dictionary of configuration files (path -> content)
            container_image: Container image name
            container_tag: Container tag
            container_digest: Container digest
            cloud_provider: Cloud provider
            cloud_region: Cloud region
            instance_type: Instance type
            git_commit: Git commit hash
            git_repository: Git repository URL
            git_branch: Git branch name
            tags: Tags for categorization
            
        Returns:
            EnvironmentSnapshot: The created snapshot
        """
        # Convert string enums to enum values if needed
        if isinstance(type, str):
            type = EnvironmentType(type)
        
        if isinstance(os_type, str) and os_type:
            os_type = OperatingSystemType(os_type)
        
        # Create the snapshot
        snapshot = EnvironmentSnapshot(
            name=name,
            description=description,
            type=type,
            python_version=python_version,
            os_type=os_type,
            os_version=os_version,
            architecture=architecture,
            kernel_version=kernel_version,
            environment_variables=environment_variables or {},
            packages=packages or [],
            compute_resources=compute_resources or [],
            config_files=config_files or {},
            container_image=container_image,
            container_tag=container_tag,
            container_digest=container_digest,
            cloud_provider=cloud_provider,
            cloud_region=cloud_region,
            instance_type=instance_type,
            git_commit=git_commit,
            git_repository=git_repository,
            git_branch=git_branch,
            tags=tags or set(),
        )
        
        # Save the snapshot
        self._storage.create_snapshot(snapshot)
        
        return snapshot
    
    def get_snapshot(self, snapshot_id: UUID) -> Optional[EnvironmentSnapshot]:
        """
        Retrieve a snapshot by ID.
        
        Args:
            snapshot_id: The ID of the snapshot to retrieve
            
        Returns:
            Optional[EnvironmentSnapshot]: The snapshot if found, None otherwise
        """
        return self._storage.get_snapshot(snapshot_id)
    
    def update_snapshot(
        self,
        snapshot_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        python_version: Optional[str] = None,
        os_type: Optional[Union[OperatingSystemType, str]] = None,
        os_version: Optional[str] = None,
        architecture: Optional[str] = None,
        kernel_version: Optional[str] = None,
        container_image: Optional[str] = None,
        container_tag: Optional[str] = None,
        container_digest: Optional[str] = None,
        cloud_provider: Optional[str] = None,
        cloud_region: Optional[str] = None,
        instance_type: Optional[str] = None,
        git_commit: Optional[str] = None,
        git_repository: Optional[str] = None,
        git_branch: Optional[str] = None,
    ) -> bool:
        """
        Update an existing environment snapshot.
        
        Args:
            snapshot_id: The ID of the snapshot to update
            name: New snapshot name
            description: New snapshot description
            python_version: New Python version
            os_type: New operating system type
            os_version: New operating system version
            architecture: New CPU architecture
            kernel_version: New kernel version
            container_image: New container image name
            container_tag: New container tag
            container_digest: New container digest
            cloud_provider: New cloud provider
            cloud_region: New cloud region
            instance_type: New instance type
            git_commit: New Git commit hash
            git_repository: New Git repository URL
            git_branch: New Git branch name
            
        Returns:
            bool: True if update successful, False otherwise
            
        Raises:
            ValueError: If snapshot doesn't exist
        """
        snapshot = self._storage.get_snapshot(snapshot_id)
        if not snapshot:
            raise ValueError(f"Environment snapshot with ID {snapshot_id} does not exist")
        
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if python_version is not None:
            update_data["python_version"] = python_version
        if os_type is not None:
            if isinstance(os_type, str):
                os_type = OperatingSystemType(os_type)
            update_data["os_type"] = os_type
        if os_version is not None:
            update_data["os_version"] = os_version
        if architecture is not None:
            update_data["architecture"] = architecture
        if kernel_version is not None:
            update_data["kernel_version"] = kernel_version
        if container_image is not None:
            update_data["container_image"] = container_image
        if container_tag is not None:
            update_data["container_tag"] = container_tag
        if container_digest is not None:
            update_data["container_digest"] = container_digest
        if cloud_provider is not None:
            update_data["cloud_provider"] = cloud_provider
        if cloud_region is not None:
            update_data["cloud_region"] = cloud_region
        if instance_type is not None:
            update_data["instance_type"] = instance_type
        if git_commit is not None:
            update_data["git_commit"] = git_commit
        if git_repository is not None:
            update_data["git_repository"] = git_repository
        if git_branch is not None:
            update_data["git_branch"] = git_branch
        
        snapshot.update(**update_data)
        return self._storage.update_snapshot(snapshot)
    
    def delete_snapshot(self, snapshot_id: UUID) -> bool:
        """
        Delete an environment snapshot.
        
        Args:
            snapshot_id: The ID of the snapshot to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        return self._storage.delete_snapshot(snapshot_id)
    
    def list_snapshots(
        self, environment_type: Optional[Union[EnvironmentType, str]] = None, tags: Optional[Set[str]] = None
    ) -> List[EnvironmentSnapshot]:
        """
        List environment snapshots with optional filtering.
        
        Args:
            environment_type: Filter by environment type
            tags: Filter by tags (snapshots must have all specified tags)
            
        Returns:
            List[EnvironmentSnapshot]: List of snapshots matching the criteria
        """
        if isinstance(environment_type, EnvironmentType):
            environment_type = environment_type.value
            
        return self._storage.list_snapshots(environment_type, tags)
    
    def capture_current_environment(
        self, 
        name: str, 
        description: Optional[str] = None,
        include_system_info: bool = True,
        include_env_vars: bool = True,
        include_packages: bool = True,
        include_git_info: bool = True,
        redact_sensitive_env_vars: bool = True,
        tags: Optional[Set[str]] = None,
    ) -> EnvironmentSnapshot:
        """
        Capture the current Python environment into a snapshot.
        
        Args:
            name: Name for the snapshot
            description: Description for the snapshot
            include_system_info: Whether to include system information
            include_env_vars: Whether to include environment variables
            include_packages: Whether to include installed packages
            include_git_info: Whether to include Git information
            redact_sensitive_env_vars: Whether to redact sensitive environment variables
            tags: Tags for the snapshot
            
        Returns:
            EnvironmentSnapshot: The created snapshot
        """
        # Initialize data
        python_version = None
        os_type = None
        os_version = None
        architecture = None
        kernel_version = None
        packages = []
        environment_variables = {}
        git_commit = None
        git_repository = None
        git_branch = None
        
        # System information
        if include_system_info:
            # Python version
            python_version = sys.version.split()[0]
            
            # OS information
            os_name = platform.system().lower()
            if os_name == "darwin":
                os_type = OperatingSystemType.MACOS
            elif os_name == "linux":
                os_type = OperatingSystemType.LINUX
            elif os_name == "windows":
                os_type = OperatingSystemType.WINDOWS
            else:
                os_type = OperatingSystemType.OTHER
            
            os_version = platform.version()
            architecture = platform.machine()
            
            try:
                if os_type == OperatingSystemType.LINUX:
                    kernel_version = platform.release()
                elif os_type == OperatingSystemType.MACOS:
                    kernel_version = subprocess.check_output(["uname", "-r"]).decode("utf-8").strip()
                elif os_type == OperatingSystemType.WINDOWS:
                    kernel_version = platform.release()
            except:
                kernel_version = "Unknown"
        
        # Environment variables
        if include_env_vars:
            for key, value in os.environ.items():
                # Redact sensitive environment variables
                if redact_sensitive_env_vars and (
                    "token" in key.lower() or 
                    "key" in key.lower() or 
                    "secret" in key.lower() or 
                    "password" in key.lower() or
                    "credential" in key.lower()
                ):
                    environment_variables[key] = "REDACTED"
                else:
                    environment_variables[key] = value
        
        # Installed packages
        if include_packages and distributions:
            for dist in distributions():
                package = PackageInfo(
                    name=dist.metadata['Name'] if 'Name' in dist.metadata else dist.name,
                    version=dist.version,
                    manager=PackageManagerType.PIP,
                )
                packages.append(package)
        
        # Git information
        if include_git_info:
            try:
                # Try to get git information
                git_repository = subprocess.check_output(
                    ["git", "config", "--get", "remote.origin.url"],
                    stderr=subprocess.DEVNULL
                ).decode("utf-8").strip()
                
                git_branch = subprocess.check_output(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    stderr=subprocess.DEVNULL
                ).decode("utf-8").strip()
                
                git_commit = subprocess.check_output(
                    ["git", "rev-parse", "HEAD"],
                    stderr=subprocess.DEVNULL
                ).decode("utf-8").strip()
            except:
                # If git commands fail, ignore and continue
                pass
        
        # Create the snapshot
        snapshot = self.create_snapshot(
            name=name,
            description=description,
            type=EnvironmentType.LOCAL,
            python_version=python_version,
            os_type=os_type,
            os_version=os_version,
            architecture=architecture,
            kernel_version=kernel_version,
            environment_variables=environment_variables,
            packages=packages,
            git_commit=git_commit,
            git_repository=git_repository,
            git_branch=git_branch,
            tags=tags,
        )
        
        return snapshot
    
    def add_package(
        self, 
        env_id: UUID, 
        name: str, 
        version: str, 
        manager: Union[PackageManagerType, str] = PackageManagerType.PIP,
        channel: Optional[str] = None,
        extras: Optional[List[str]] = None,
    ) -> bool:
        """
        Add a package to an environment snapshot.
        
        Args:
            env_id: The ID of the environment snapshot
            name: Package name
            version: Package version
            manager: Package manager
            channel: Channel (for conda packages)
            extras: Extras (for pip packages with extras)
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If environment doesn't exist
        """
        snapshot = self._storage.get_snapshot(env_id)
        if not snapshot:
            raise ValueError(f"Environment snapshot with ID {env_id} does not exist")
        
        # Convert string enum to enum value if needed
        if isinstance(manager, str):
            manager = PackageManagerType(manager)
        
        # Create package
        package = PackageInfo(
            name=name,
            version=version,
            manager=manager,
            channel=channel,
            extras=extras,
        )
        
        snapshot.add_package(package)
        return self._storage.update_snapshot(snapshot)
    
    def remove_package(
        self, env_id: UUID, package_name: str, manager: Union[PackageManagerType, str] = PackageManagerType.PIP
    ) -> bool:
        """
        Remove a package from an environment snapshot.
        
        Args:
            env_id: The ID of the environment snapshot
            package_name: Package name
            manager: Package manager
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If environment doesn't exist
        """
        snapshot = self._storage.get_snapshot(env_id)
        if not snapshot:
            raise ValueError(f"Environment snapshot with ID {env_id} does not exist")
        
        # Convert string enum to enum value if needed
        if isinstance(manager, str):
            manager = PackageManagerType(manager)
        
        result = snapshot.remove_package(package_name, manager)
        if result:
            return self._storage.update_snapshot(snapshot)
        return False
    
    def add_compute_resource(
        self, 
        env_id: UUID, 
        type: Union[ComputeResourceType, str], 
        count: int, 
        model: Optional[str] = None,
        memory_gb: Optional[float] = None,
    ) -> bool:
        """
        Add a compute resource to an environment snapshot.
        
        Args:
            env_id: The ID of the environment snapshot
            type: Type of compute resource
            count: Number of resources
            model: Model name/identifier
            memory_gb: Memory in gigabytes
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If environment doesn't exist
        """
        snapshot = self._storage.get_snapshot(env_id)
        if not snapshot:
            raise ValueError(f"Environment snapshot with ID {env_id} does not exist")
        
        # Convert string enum to enum value if needed
        if isinstance(type, str):
            type = ComputeResourceType(type)
        
        # Create resource
        resource = ComputeResource(
            type=type,
            count=count,
            model=model,
            memory_gb=memory_gb,
        )
        
        snapshot.add_compute_resource(resource)
        return self._storage.update_snapshot(snapshot)
    
    def remove_compute_resource(self, env_id: UUID, resource_index: int) -> bool:
        """
        Remove a compute resource from an environment snapshot.
        
        Args:
            env_id: The ID of the environment snapshot
            resource_index: Index of the resource to remove
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If environment doesn't exist
            IndexError: If resource index is invalid
        """
        snapshot = self._storage.get_snapshot(env_id)
        if not snapshot:
            raise ValueError(f"Environment snapshot with ID {env_id} does not exist")
        
        if resource_index < 0 or resource_index >= len(snapshot.compute_resources):
            raise IndexError(f"Invalid resource index: {resource_index}")
        
        result = snapshot.remove_compute_resource(resource_index)
        if result:
            return self._storage.update_snapshot(snapshot)
        return False
    
    def add_environment_variable(self, env_id: UUID, key: str, value: str) -> bool:
        """
        Add an environment variable to a snapshot.
        
        Args:
            env_id: The ID of the environment snapshot
            key: Variable name
            value: Variable value
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If environment doesn't exist
        """
        snapshot = self._storage.get_snapshot(env_id)
        if not snapshot:
            raise ValueError(f"Environment snapshot with ID {env_id} does not exist")
        
        snapshot.add_environment_variable(key, value)
        return self._storage.update_snapshot(snapshot)
    
    def remove_environment_variable(self, env_id: UUID, key: str) -> bool:
        """
        Remove an environment variable from a snapshot.
        
        Args:
            env_id: The ID of the environment snapshot
            key: Variable name
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If environment doesn't exist
        """
        snapshot = self._storage.get_snapshot(env_id)
        if not snapshot:
            raise ValueError(f"Environment snapshot with ID {env_id} does not exist")
        
        result = snapshot.remove_environment_variable(key)
        if result:
            return self._storage.update_snapshot(snapshot)
        return False
    
    def add_config_file(self, env_id: UUID, file_path: str, content: str) -> bool:
        """
        Add a configuration file to a snapshot.
        
        Args:
            env_id: The ID of the environment snapshot
            file_path: Path of the configuration file
            content: Content of the file
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If environment doesn't exist
        """
        snapshot = self._storage.get_snapshot(env_id)
        if not snapshot:
            raise ValueError(f"Environment snapshot with ID {env_id} does not exist")
        
        snapshot.add_config_file(file_path, content)
        return self._storage.update_snapshot(snapshot)
    
    def remove_config_file(self, env_id: UUID, file_path: str) -> bool:
        """
        Remove a configuration file from a snapshot.
        
        Args:
            env_id: The ID of the environment snapshot
            file_path: Path of the configuration file
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If environment doesn't exist
        """
        snapshot = self._storage.get_snapshot(env_id)
        if not snapshot:
            raise ValueError(f"Environment snapshot with ID {env_id} does not exist")
        
        result = snapshot.remove_config_file(file_path)
        if result:
            return self._storage.update_snapshot(snapshot)
        return False
    
    def add_tag(self, env_id: UUID, tag: str) -> bool:
        """
        Add a tag to an environment snapshot.
        
        Args:
            env_id: The ID of the environment snapshot
            tag: The tag to add
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If environment doesn't exist
        """
        snapshot = self._storage.get_snapshot(env_id)
        if not snapshot:
            raise ValueError(f"Environment snapshot with ID {env_id} does not exist")
        
        snapshot.add_tag(tag)
        return self._storage.update_snapshot(snapshot)
    
    def remove_tag(self, env_id: UUID, tag: str) -> bool:
        """
        Remove a tag from an environment snapshot.
        
        Args:
            env_id: The ID of the environment snapshot
            tag: The tag to remove
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If environment doesn't exist
        """
        snapshot = self._storage.get_snapshot(env_id)
        if not snapshot:
            raise ValueError(f"Environment snapshot with ID {env_id} does not exist")
        
        result = snapshot.remove_tag(tag)
        if result:
            return self._storage.update_snapshot(snapshot)
        return False
    
    def update_custom_metadata(
        self, env_id: UUID, key: str, value: Union[str, int, float, bool, list, dict]
    ) -> bool:
        """
        Update a custom metadata field for an environment snapshot.
        
        Args:
            env_id: The ID of the environment snapshot
            key: The metadata key
            value: The metadata value
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If environment doesn't exist
        """
        snapshot = self._storage.get_snapshot(env_id)
        if not snapshot:
            raise ValueError(f"Environment snapshot with ID {env_id} does not exist")
        
        snapshot.update_custom_metadata(key, value)
        return self._storage.update_snapshot(snapshot)
    
    def remove_custom_metadata(self, env_id: UUID, key: str) -> bool:
        """
        Remove a custom metadata field from an environment snapshot.
        
        Args:
            env_id: The ID of the environment snapshot
            key: The metadata key
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If environment doesn't exist
        """
        snapshot = self._storage.get_snapshot(env_id)
        if not snapshot:
            raise ValueError(f"Environment snapshot with ID {env_id} does not exist")
        
        result = snapshot.remove_custom_metadata(key)
        if result:
            return self._storage.update_snapshot(snapshot)
        return False
    
    # Task-Environment link operations
    
    def link_task_to_environment(
        self,
        task_id: UUID,
        env_id: UUID,
        description: Optional[str] = None,
        actual_execution_time: Optional[float] = None,
    ) -> UUID:
        """
        Link a task to an environment snapshot.
        
        Args:
            task_id: The ID of the task
            env_id: The ID of the environment snapshot
            description: Description of the relationship
            actual_execution_time: Runtime in seconds, if applicable
            
        Returns:
            UUID: The ID of the created link
            
        Raises:
            ValueError: If environment doesn't exist
        """
        snapshot = self._storage.get_snapshot(env_id)
        if not snapshot:
            raise ValueError(f"Environment snapshot with ID {env_id} does not exist")
        
        # Check if link already exists
        existing_snapshots = self._storage.get_snapshots_for_task(task_id)
        for s in existing_snapshots:
            if s.id == env_id:
                # Link already exists
                return UUID('00000000-0000-0000-0000-000000000000')
        
        # Create the link
        link = TaskEnvironmentLink(
            task_id=task_id,
            environment_id=env_id,
            description=description,
            actual_execution_time=actual_execution_time,
        )
        
        return self._storage.create_task_environment_link(link)
    
    def unlink_task_from_environment(self, task_id: UUID, env_id: UUID) -> bool:
        """
        Remove a link between a task and an environment snapshot.
        
        Args:
            task_id: The ID of the task
            env_id: The ID of the environment snapshot
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Find the link
        links = [
            link_id for link_id, link in self._storage._task_environment_links.items()
            if link.task_id == task_id and link.environment_id == env_id
        ]
        
        if not links:
            return False
        
        # Delete the link
        return self._storage.delete_task_environment_link(links[0])
    
    def get_snapshots_for_task(self, task_id: UUID) -> List[EnvironmentSnapshot]:
        """
        Get all environment snapshots associated with a task.
        
        Args:
            task_id: The ID of the task
            
        Returns:
            List[EnvironmentSnapshot]: List of associated snapshots
        """
        return self._storage.get_snapshots_for_task(task_id)
    
    def get_tasks_for_snapshot(self, env_id: UUID) -> List[UUID]:
        """
        Get all task IDs associated with an environment snapshot.
        
        Args:
            env_id: The ID of the environment snapshot
            
        Returns:
            List[UUID]: List of associated task IDs
        """
        return self._storage.get_tasks_for_snapshot(env_id)
    
    def add_note_to_link(self, task_id: UUID, env_id: UUID, note: str) -> bool:
        """
        Add a note to the link between a task and an environment snapshot.
        
        Args:
            task_id: The ID of the task
            env_id: The ID of the environment snapshot
            note: The note to add
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Find the link
        links = [
            link for link_id, link in self._storage._task_environment_links.items()
            if link.task_id == task_id and link.environment_id == env_id
        ]
        
        if not links:
            return False
        
        link = links[0]
        link.add_note(note)
        return self._storage.update_task_environment_link(link)
    
    def compare_snapshots(self, snapshot_id1: UUID, snapshot_id2: UUID) -> Dict[str, Any]:
        """
        Compare two environment snapshots to find differences.
        
        Args:
            snapshot_id1: The ID of the first snapshot
            snapshot_id2: The ID of the second snapshot
            
        Returns:
            Dict[str, Any]: Dictionary of differences
            
        Raises:
            ValueError: If snapshots don't exist
        """
        snapshot1 = self._storage.get_snapshot(snapshot_id1)
        if not snapshot1:
            raise ValueError(f"Environment snapshot with ID {snapshot_id1} does not exist")
        
        snapshot2 = self._storage.get_snapshot(snapshot_id2)
        if not snapshot2:
            raise ValueError(f"Environment snapshot with ID {snapshot_id2} does not exist")
        
        # Compare snapshots
        differences = {}
        
        # Compare Python version
        if snapshot1.python_version != snapshot2.python_version:
            differences["python_version"] = {
                "snapshot1": snapshot1.python_version,
                "snapshot2": snapshot2.python_version,
            }
        
        # Compare OS information
        if snapshot1.os_type != snapshot2.os_type:
            differences["os_type"] = {
                "snapshot1": snapshot1.os_type,
                "snapshot2": snapshot2.os_type,
            }
        
        if snapshot1.os_version != snapshot2.os_version:
            differences["os_version"] = {
                "snapshot1": snapshot1.os_version,
                "snapshot2": snapshot2.os_version,
            }
        
        # Compare packages
        packages1 = {(p.name, p.manager): p for p in snapshot1.packages}
        packages2 = {(p.name, p.manager): p for p in snapshot2.packages}
        
        # Packages in snapshot1 but not in snapshot2
        packages_only_in_1 = [
            {"name": p.name, "version": p.version, "manager": p.manager}
            for (name, manager), p in packages1.items()
            if (name, manager) not in packages2
        ]
        
        # Packages in snapshot2 but not in snapshot1
        packages_only_in_2 = [
            {"name": p.name, "version": p.version, "manager": p.manager}
            for (name, manager), p in packages2.items()
            if (name, manager) not in packages1
        ]
        
        # Packages with different versions
        packages_diff_version = [
            {
                "name": name,
                "manager": manager,
                "version1": packages1[(name, manager)].version,
                "version2": packages2[(name, manager)].version,
            }
            for (name, manager) in packages1.keys() & packages2.keys()
            if packages1[(name, manager)].version != packages2[(name, manager)].version
        ]
        
        if packages_only_in_1 or packages_only_in_2 or packages_diff_version:
            differences["packages"] = {
                "only_in_snapshot1": packages_only_in_1,
                "only_in_snapshot2": packages_only_in_2,
                "different_versions": packages_diff_version,
            }
        
        # Compare environment variables
        env_vars1 = set(snapshot1.environment_variables.keys())
        env_vars2 = set(snapshot2.environment_variables.keys())
        
        if env_vars1 != env_vars2:
            differences["environment_variables"] = {
                "only_in_snapshot1": list(env_vars1 - env_vars2),
                "only_in_snapshot2": list(env_vars2 - env_vars1),
            }
        
        return differences
"""
Experiment management service for the Academic Knowledge Vault system.

This module provides functionality for creating and managing experiments, protocols, and results.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union, Any

from academic_knowledge_vault.models.base import KnowledgeItemType, Person, Reference
from academic_knowledge_vault.models.experiment import (
    Experiment,
    ExperimentCollection,
    ExperimentProtocol,
    ExperimentResult,
    ExperimentStatus,
    ParameterType,
    ProtocolParameter,
)
from academic_knowledge_vault.storage.experiment_storage import (
    ExperimentStorage,
    ExperimentProtocolStorage,
    ExperimentCollectionStorage,
)


class ExperimentService:
    """Service for managing experiments, protocols, and results."""
    
    def __init__(self,
                experiment_storage: ExperimentStorage,
                protocol_storage: ExperimentProtocolStorage,
                collection_storage: ExperimentCollectionStorage):
        """
        Initialize the experiment service.
        
        Args:
            experiment_storage: Storage for experiments
            protocol_storage: Storage for protocols
            collection_storage: Storage for experiment collections
        """
        self.experiment_storage = experiment_storage
        self.protocol_storage = protocol_storage
        self.collection_storage = collection_storage
    
    def create_protocol(self,
                       name: str,
                       description: str,
                       steps: List[str],
                       parameters: Optional[List[Dict[str, Any]]] = None,
                       materials: Optional[List[str]] = None,
                       equipment: Optional[List[str]] = None,
                       tags: Optional[List[str]] = None,
                       author_id: Optional[str] = None) -> str:
        """
        Create a new experiment protocol.
        
        Args:
            name: Protocol name
            description: Protocol description
            steps: Protocol steps
            parameters: List of parameter dictionaries
            materials: List of required materials
            equipment: List of required equipment
            tags: Tags for the protocol
            author_id: ID of the protocol author
            
        Returns:
            ID of the created protocol
        """
        # Convert parameter dictionaries to objects
        parameter_objects = []
        if parameters:
            for param_dict in parameters:
                parameter_type = param_dict.get("parameter_type", "text")
                if isinstance(parameter_type, str):
                    parameter_type = ParameterType(parameter_type)
                
                parameter = ProtocolParameter(
                    name=param_dict["name"],
                    description=param_dict.get("description", ""),
                    parameter_type=parameter_type,
                    required=param_dict.get("required", True),
                    default_value=param_dict.get("default_value"),
                    units=param_dict.get("units"),
                    options=param_dict.get("options"),
                    min_value=param_dict.get("min_value"),
                    max_value=param_dict.get("max_value"),
                    validation_rules=param_dict.get("validation_rules")
                )
                parameter_objects.append(parameter)
        
        # Create the protocol
        protocol = ExperimentProtocol(
            name=name,
            description=description,
            steps=steps,
            parameters=parameter_objects,
            materials=materials or [],
            equipment=equipment or [],
            tags=set(tags or []),
            author_id=author_id
        )
        
        # Save the protocol
        protocol_id = self.protocol_storage.save(protocol)
        
        return protocol_id
    
    def update_protocol(self,
                       protocol_id: str,
                       description: Optional[str] = None,
                       steps: Optional[List[str]] = None,
                       materials: Optional[List[str]] = None,
                       equipment: Optional[List[str]] = None,
                       tags: Optional[List[str]] = None,
                       add_tags: Optional[List[str]] = None,
                       remove_tags: Optional[List[str]] = None) -> None:
        """
        Update an existing protocol.
        
        Args:
            protocol_id: ID of the protocol to update
            description: New description (if None, keep existing)
            steps: New steps (if None, keep existing)
            materials: New materials (if None, keep existing)
            equipment: New equipment (if None, keep existing)
            tags: Complete replacement of tags (if None, keep existing)
            add_tags: Tags to add to existing set
            remove_tags: Tags to remove from existing set
            
        Raises:
            ValueError: If the protocol doesn't exist
        """
        if not self.protocol_storage.exists(protocol_id):
            raise ValueError(f"Protocol with ID {protocol_id} does not exist")
        
        protocol = self.protocol_storage.get(protocol_id)
        
        # Update description if provided
        if description is not None:
            protocol.description = description
        
        # Update steps if provided
        if steps is not None:
            protocol.steps = steps
        
        # Update materials if provided
        if materials is not None:
            protocol.materials = materials
        
        # Update equipment if provided
        if equipment is not None:
            protocol.equipment = equipment
        
        # Update tags if provided
        if tags is not None:
            protocol.tags = set(tags)
        
        # Add tags if provided
        if add_tags:
            protocol.tags.update(add_tags)
        
        # Remove tags if provided
        if remove_tags:
            protocol.tags.difference_update(remove_tags)
        
        # Update timestamp
        protocol.updated_at = datetime.now()
        
        # Save the updated protocol
        self.protocol_storage.save(protocol)
    
    def add_parameter_to_protocol(self, protocol_id: str, parameter: Dict[str, Any]) -> None:
        """
        Add a parameter to an existing protocol.
        
        Args:
            protocol_id: ID of the protocol
            parameter: Parameter dictionary
            
        Raises:
            ValueError: If the protocol doesn't exist
        """
        if not self.protocol_storage.exists(protocol_id):
            raise ValueError(f"Protocol with ID {protocol_id} does not exist")
        
        protocol = self.protocol_storage.get(protocol_id)
        
        parameter_type = parameter.get("parameter_type", "text")
        if isinstance(parameter_type, str):
            parameter_type = ParameterType(parameter_type)
        
        protocol_param = ProtocolParameter(
            name=parameter["name"],
            description=parameter.get("description", ""),
            parameter_type=parameter_type,
            required=parameter.get("required", True),
            default_value=parameter.get("default_value"),
            units=parameter.get("units"),
            options=parameter.get("options"),
            min_value=parameter.get("min_value"),
            max_value=parameter.get("max_value"),
            validation_rules=parameter.get("validation_rules")
        )
        
        protocol.add_parameter(protocol_param)
        self.protocol_storage.save(protocol)
    
    def add_step_to_protocol(self, protocol_id: str, step_description: str) -> None:
        """
        Add a step to an existing protocol.
        
        Args:
            protocol_id: ID of the protocol
            step_description: Description of the step
            
        Raises:
            ValueError: If the protocol doesn't exist
        """
        if not self.protocol_storage.exists(protocol_id):
            raise ValueError(f"Protocol with ID {protocol_id} does not exist")
        
        protocol = self.protocol_storage.get(protocol_id)
        protocol.add_step(step_description)
        self.protocol_storage.save(protocol)
    
    def create_new_protocol_version(self, protocol_id: str) -> str:
        """
        Create a new version of an existing protocol.
        
        Args:
            protocol_id: ID of the existing protocol
            
        Returns:
            ID of the new protocol version
            
        Raises:
            ValueError: If the protocol doesn't exist
        """
        if not self.protocol_storage.exists(protocol_id):
            raise ValueError(f"Protocol with ID {protocol_id} does not exist")
        
        protocol = self.protocol_storage.get(protocol_id)
        new_protocol = protocol.create_new_version()
        
        # Save the new protocol version
        new_protocol_id = self.protocol_storage.save(new_protocol)
        
        return new_protocol_id
    
    def delete_protocol(self, protocol_id: str) -> bool:
        """
        Delete a protocol.
        
        Args:
            protocol_id: ID of the protocol to delete
            
        Returns:
            True if the protocol was deleted, False if it didn't exist
        """
        return self.protocol_storage.delete(protocol_id)
    
    def get_protocol(self, protocol_id: str) -> ExperimentProtocol:
        """
        Get a protocol by ID.
        
        Args:
            protocol_id: ID of the protocol to retrieve
            
        Returns:
            The requested protocol
            
        Raises:
            ValueError: If the protocol doesn't exist
        """
        if not self.protocol_storage.exists(protocol_id):
            raise ValueError(f"Protocol with ID {protocol_id} does not exist")
        
        return self.protocol_storage.get(protocol_id)
    
    def get_latest_protocol_version(self, protocol_name: str) -> Optional[ExperimentProtocol]:
        """
        Get the latest version of a protocol by name.
        
        Args:
            protocol_name: Name of the protocol
            
        Returns:
            Latest version of the protocol, or None if not found
        """
        return self.protocol_storage.get_latest_version(protocol_name)
    
    def create_experiment(self,
                         title: str,
                         protocol_id: Optional[str] = None,
                         status: Union[str, ExperimentStatus] = ExperimentStatus.PLANNED,
                         research_question_id: Optional[str] = None,
                         hypothesis_ids: Optional[List[str]] = None,
                         parameters: Optional[Dict[str, Any]] = None,
                         researchers: Optional[List[Dict[str, str]]] = None,
                         tags: Optional[List[str]] = None) -> str:
        """
        Create a new experiment.
        
        Args:
            title: Experiment title
            protocol_id: ID of the protocol to use
            status: Initial status of the experiment
            research_question_id: ID of the related research question
            hypothesis_ids: IDs of related hypotheses
            parameters: Parameter values for the experiment
            researchers: List of researcher dictionaries with 'name', optional 'email' and 'affiliation'
            tags: Tags for the experiment
            
        Returns:
            ID of the created experiment
            
        Raises:
            ValueError: If the protocol doesn't exist or has invalid parameters
        """
        # Validate protocol if provided
        protocol_version = None
        if protocol_id:
            if not self.protocol_storage.exists(protocol_id):
                raise ValueError(f"Protocol with ID {protocol_id} does not exist")
            
            protocol = self.protocol_storage.get(protocol_id)
            protocol_version = protocol.version
            
            # Validate parameters against protocol
            if parameters:
                errors = []
                for param in protocol.parameters:
                    if param.name in parameters:
                        value = parameters[param.name]
                        if not param.validate_value(value):
                            errors.append(f"Invalid value for parameter {param.name}: {value}")
                    elif param.required:
                        errors.append(f"Missing required parameter: {param.name}")
                
                if errors:
                    raise ValueError(f"Invalid parameters: {', '.join(errors)}")
        
        # Convert researcher dictionaries to objects
        researcher_objects = []
        if researchers:
            for researcher_dict in researchers:
                person = Person(
                    name=researcher_dict["name"],
                    email=researcher_dict.get("email"),
                    affiliation=researcher_dict.get("affiliation"),
                    role=researcher_dict.get("role", "researcher")
                )
                researcher_objects.append(person)
        
        # Handle string status
        if isinstance(status, str):
            status = ExperimentStatus(status)
        
        # Create the experiment
        experiment = Experiment(
            title=title,
            status=status,
            protocol_id=protocol_id,
            protocol_version=protocol_version,
            research_question_id=research_question_id,
            hypothesis_ids=hypothesis_ids or [],
            parameters=parameters or {},
            researchers=researcher_objects,
            tags=set(tags or [])
        )
        
        # Save the experiment
        experiment_id = self.experiment_storage.save(experiment)
        
        return experiment_id
    
    def update_experiment(self,
                         experiment_id: str,
                         title: Optional[str] = None,
                         status: Optional[Union[str, ExperimentStatus]] = None,
                         tags: Optional[List[str]] = None,
                         add_tags: Optional[List[str]] = None,
                         remove_tags: Optional[List[str]] = None) -> None:
        """
        Update an existing experiment.
        
        Args:
            experiment_id: ID of the experiment to update
            title: New title (if None, keep existing)
            status: New status (if None, keep existing)
            tags: Complete replacement of tags (if None, keep existing)
            add_tags: Tags to add to existing set
            remove_tags: Tags to remove from existing set
            
        Raises:
            ValueError: If the experiment doesn't exist
        """
        if not self.experiment_storage.exists(experiment_id):
            raise ValueError(f"Experiment with ID {experiment_id} does not exist")
        
        experiment = self.experiment_storage.get(experiment_id)
        
        # Update title if provided
        if title is not None:
            experiment.title = title
        
        # Update status if provided
        if status is not None:
            if isinstance(status, str):
                status = ExperimentStatus(status)
            experiment.update_status(status)
        
        # Update tags if provided
        if tags is not None:
            experiment.tags = set(tags)
        
        # Add tags if provided
        if add_tags:
            experiment.tags.update(add_tags)
        
        # Remove tags if provided
        if remove_tags:
            experiment.tags.difference_update(remove_tags)
        
        # Save the updated experiment
        self.experiment_storage.save(experiment)
    
    def set_parameter(self, experiment_id: str, name: str, value: Any) -> None:
        """
        Set a parameter value for an experiment.
        
        Args:
            experiment_id: ID of the experiment
            name: Parameter name
            value: Parameter value
            
        Raises:
            ValueError: If the experiment doesn't exist or parameter is invalid
        """
        if not self.experiment_storage.exists(experiment_id):
            raise ValueError(f"Experiment with ID {experiment_id} does not exist")
        
        experiment = self.experiment_storage.get(experiment_id)
        
        # Validate parameter against protocol if possible
        if experiment.protocol_id:
            try:
                protocol = self.protocol_storage.get(experiment.protocol_id)
                
                for param in protocol.parameters:
                    if param.name == name:
                        if not param.validate_value(value):
                            raise ValueError(f"Invalid value for parameter {name}: {value}")
                        break
            except Exception:
                # Skip validation if protocol can't be loaded
                pass
        
        experiment.set_parameter(name, value)
        self.experiment_storage.save(experiment)
    
    def add_researcher(self,
                      experiment_id: str,
                      name: str,
                      email: Optional[str] = None,
                      affiliation: Optional[str] = None,
                      role: Optional[str] = None) -> None:
        """
        Add a researcher to an experiment.
        
        Args:
            experiment_id: ID of the experiment
            name: Researcher name
            email: Researcher email
            affiliation: Researcher affiliation
            role: Researcher role
            
        Raises:
            ValueError: If the experiment doesn't exist
        """
        if not self.experiment_storage.exists(experiment_id):
            raise ValueError(f"Experiment with ID {experiment_id} does not exist")
        
        experiment = self.experiment_storage.get(experiment_id)
        
        researcher = Person(
            name=name,
            email=email,
            affiliation=affiliation,
            role=role or "researcher"
        )
        
        experiment.add_researcher(researcher)
        self.experiment_storage.save(experiment)
    
    def start_experiment(self, experiment_id: str) -> None:
        """
        Mark an experiment as started.
        
        Args:
            experiment_id: ID of the experiment
            
        Raises:
            ValueError: If the experiment doesn't exist
        """
        if not self.experiment_storage.exists(experiment_id):
            raise ValueError(f"Experiment with ID {experiment_id} does not exist")
        
        experiment = self.experiment_storage.get(experiment_id)
        experiment.start_experiment()
        self.experiment_storage.save(experiment)
    
    def complete_experiment(self, experiment_id: str) -> None:
        """
        Mark an experiment as completed.
        
        Args:
            experiment_id: ID of the experiment
            
        Raises:
            ValueError: If the experiment doesn't exist
        """
        if not self.experiment_storage.exists(experiment_id):
            raise ValueError(f"Experiment with ID {experiment_id} does not exist")
        
        experiment = self.experiment_storage.get(experiment_id)
        experiment.complete_experiment()
        self.experiment_storage.save(experiment)
    
    def add_result(self,
                  experiment_id: str,
                  name: str,
                  description: Optional[str] = None,
                  data_values: Optional[Dict[str, Any]] = None,
                  data_files: Optional[List[str]] = None,
                  success: bool = True,
                  notes: Optional[str] = None) -> str:
        """
        Add a result to an experiment.
        
        Args:
            experiment_id: ID of the experiment
            name: Result name
            description: Result description
            data_values: Dictionary of data values
            data_files: List of data file paths
            success: Whether the result is successful
            notes: Additional notes
            
        Returns:
            ID of the created result
            
        Raises:
            ValueError: If the experiment doesn't exist
        """
        if not self.experiment_storage.exists(experiment_id):
            raise ValueError(f"Experiment with ID {experiment_id} does not exist")
        
        experiment = self.experiment_storage.get(experiment_id)
        
        # Create the result
        result = ExperimentResult(
            name=name,
            description=description,
            data_values=data_values or {},
            data_files=data_files or [],
            success=success,
            notes=notes
        )
        
        # Generate summary statistics if possible
        result.generate_summary_statistics()
        
        # Add the result to the experiment
        experiment.add_result(result)
        self.experiment_storage.save(experiment)
        
        return result.id
    
    def delete_experiment(self, experiment_id: str) -> bool:
        """
        Delete an experiment.
        
        Args:
            experiment_id: ID of the experiment to delete
            
        Returns:
            True if the experiment was deleted, False if it didn't exist
        """
        return self.experiment_storage.delete(experiment_id)
    
    def get_experiment(self, experiment_id: str) -> Experiment:
        """
        Get an experiment by ID.
        
        Args:
            experiment_id: ID of the experiment to retrieve
            
        Returns:
            The requested experiment
            
        Raises:
            ValueError: If the experiment doesn't exist
        """
        if not self.experiment_storage.exists(experiment_id):
            raise ValueError(f"Experiment with ID {experiment_id} does not exist")
        
        return self.experiment_storage.get(experiment_id)
    
    def create_collection(self,
                         name: str,
                         description: Optional[str] = None,
                         experiment_ids: Optional[List[str]] = None,
                         tags: Optional[List[str]] = None) -> str:
        """
        Create an experiment collection.
        
        Args:
            name: Collection name
            description: Collection description
            experiment_ids: IDs of experiments to include
            tags: Tags for the collection
            
        Returns:
            ID of the created collection
            
        Raises:
            ValueError: If any of the specified experiments don't exist
        """
        # Validate experiment IDs if provided
        if experiment_ids:
            for experiment_id in experiment_ids:
                if not self.experiment_storage.exists(experiment_id):
                    raise ValueError(f"Experiment with ID {experiment_id} does not exist")
        
        # Create the collection
        collection = ExperimentCollection(
            name=name,
            description=description,
            experiment_ids=set(experiment_ids or []),
            tags=set(tags or [])
        )
        
        # Save the collection
        collection_id = self.collection_storage.save(collection)
        
        return collection_id
    
    def add_experiment_to_collection(self, collection_id: str, experiment_id: str) -> None:
        """
        Add an experiment to a collection.
        
        Args:
            collection_id: ID of the collection
            experiment_id: ID of the experiment to add
            
        Raises:
            ValueError: If the collection or experiment doesn't exist
        """
        if not self.collection_storage.exists(collection_id):
            raise ValueError(f"Collection with ID {collection_id} does not exist")
        
        if not self.experiment_storage.exists(experiment_id):
            raise ValueError(f"Experiment with ID {experiment_id} does not exist")
        
        collection = self.collection_storage.get(collection_id)
        collection.add_experiment(experiment_id)
        self.collection_storage.save(collection)
    
    def remove_experiment_from_collection(self, collection_id: str, experiment_id: str) -> None:
        """
        Remove an experiment from a collection.
        
        Args:
            collection_id: ID of the collection
            experiment_id: ID of the experiment to remove
            
        Raises:
            ValueError: If the collection doesn't exist
        """
        if not self.collection_storage.exists(collection_id):
            raise ValueError(f"Collection with ID {collection_id} does not exist")
        
        collection = self.collection_storage.get(collection_id)
        collection.remove_experiment(experiment_id)
        self.collection_storage.save(collection)
    
    def get_collection(self, collection_id: str) -> ExperimentCollection:
        """
        Get a collection by ID.
        
        Args:
            collection_id: ID of the collection to retrieve
            
        Returns:
            The requested collection
            
        Raises:
            ValueError: If the collection doesn't exist
        """
        if not self.collection_storage.exists(collection_id):
            raise ValueError(f"Collection with ID {collection_id} does not exist")
        
        return self.collection_storage.get(collection_id)
    
    def delete_collection(self, collection_id: str) -> bool:
        """
        Delete a collection.
        
        Args:
            collection_id: ID of the collection to delete
            
        Returns:
            True if the collection was deleted, False if it didn't exist
        """
        return self.collection_storage.delete(collection_id)
    
    def search_experiments(self,
                          status: Optional[Union[str, ExperimentStatus]] = None,
                          research_question_id: Optional[str] = None,
                          hypothesis_id: Optional[str] = None,
                          protocol_id: Optional[str] = None,
                          researcher: Optional[str] = None,
                          tags: Optional[List[str]] = None,
                          start_date_after: Optional[datetime] = None,
                          start_date_before: Optional[datetime] = None,
                          end_date_after: Optional[datetime] = None,
                          end_date_before: Optional[datetime] = None) -> List[str]:
        """
        Search for experiments based on various criteria.
        
        Args:
            status: Status to filter by
            research_question_id: Research question ID to filter by
            hypothesis_id: Hypothesis ID to filter by
            protocol_id: Protocol ID to filter by
            researcher: Researcher name to filter by
            tags: Tags to filter by
            start_date_after: Only include experiments started after this date
            start_date_before: Only include experiments started before this date
            end_date_after: Only include experiments ended after this date
            end_date_before: Only include experiments ended before this date
            
        Returns:
            List of matching experiment IDs
        """
        # Start with all experiments
        result_ids = set(self.experiment_storage.list_ids())
        
        # Filter by status if specified
        if status:
            if isinstance(status, str):
                status = ExperimentStatus(status)
            
            status_results = set(self.experiment_storage.get_by_status(status))
            result_ids.intersection_update(status_results)
        
        # Filter by research question if specified
        if research_question_id:
            question_results = set(self.experiment_storage.get_by_research_question(research_question_id))
            result_ids.intersection_update(question_results)
        
        # Filter by hypothesis if specified
        if hypothesis_id:
            hypothesis_results = set(self.experiment_storage.get_by_hypothesis(hypothesis_id))
            result_ids.intersection_update(hypothesis_results)
        
        # Filter by protocol if specified
        if protocol_id:
            protocol_results = set(self.experiment_storage.get_by_protocol(protocol_id))
            result_ids.intersection_update(protocol_results)
        
        # Filter by researcher if specified
        if researcher:
            researcher_results = set(self.experiment_storage.get_by_researcher(researcher))
            result_ids.intersection_update(researcher_results)
        
        # Filter by tags if specified
        if tags:
            tag_results = set(self.experiment_storage.search_by_tags(tags))
            result_ids.intersection_update(tag_results)
        
        # Filter by start date if specified
        if start_date_after or start_date_before:
            start_date_results = set(self.experiment_storage.get_by_date_range(
                start_date=start_date_after,
                end_date=start_date_before,
                use_start_date=True
            ))
            result_ids.intersection_update(start_date_results)
        
        # Filter by end date if specified
        if end_date_after or end_date_before:
            end_date_results = set(self.experiment_storage.get_by_date_range(
                start_date=end_date_after,
                end_date=end_date_before,
                use_start_date=False
            ))
            result_ids.intersection_update(end_date_results)
        
        return list(result_ids)
    
    def search_protocols(self,
                        text: Optional[str] = None,
                        tags: Optional[List[str]] = None,
                        author_id: Optional[str] = None) -> List[str]:
        """
        Search for protocols based on various criteria.
        
        Args:
            text: Text to search for in protocol name and description
            tags: Tags to filter by
            author_id: Author ID to filter by
            
        Returns:
            List of matching protocol IDs
        """
        # Start with all protocols
        result_ids = set(self.protocol_storage.list_ids())
        
        # Filter by text if specified
        if text:
            text_results = set()
            text_lower = text.lower()
            
            for protocol_id in result_ids:
                try:
                    protocol = self.protocol_storage.get(protocol_id)
                    
                    if (text_lower in protocol.name.lower() or 
                        text_lower in protocol.description.lower()):
                        text_results.add(protocol_id)
                        
                except Exception:
                    continue
            
            result_ids.intersection_update(text_results)
        
        # Filter by tags if specified
        if tags:
            tag_results = set(self.protocol_storage.search_by_tags(tags))
            result_ids.intersection_update(tag_results)
        
        # Filter by author if specified
        if author_id:
            author_results = set(self.protocol_storage.search_by_author(author_id))
            result_ids.intersection_update(author_results)
        
        return list(result_ids)
"""
Grant Proposal service for the Academic Knowledge Vault system.

This module provides functionality for creating and managing grant proposals and workspaces.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union, Any

from academic_knowledge_vault.models.base import KnowledgeItemType, Person, Reference
from academic_knowledge_vault.models.grant_proposal import (
    BudgetItem,
    FundingAgencyType,
    FundingStatus,
    GrantProposal,
    GrantProposalWorkspace,
    ProposalSection,
)
from academic_knowledge_vault.storage.grant_proposal_storage import (
    GrantProposalStorage,
    GrantProposalWorkspaceStorage,
)


class GrantProposalService:
    """Service for managing grant proposals and workspaces."""
    
    def __init__(self,
                proposal_storage: GrantProposalStorage,
                workspace_storage: GrantProposalWorkspaceStorage):
        """
        Initialize the grant proposal service.
        
        Args:
            proposal_storage: Storage for grant proposals
            workspace_storage: Storage for proposal workspaces
        """
        self.proposal_storage = proposal_storage
        self.workspace_storage = workspace_storage
    
    def create_proposal(self,
                       title: str,
                       funding_agency: str,
                       agency_type: Union[str, FundingAgencyType] = FundingAgencyType.GOVERNMENT,
                       abstract: Optional[str] = None,
                       status: Union[str, FundingStatus] = FundingStatus.DRAFTING,
                       program_name: Optional[str] = None,
                       requested_amount: Optional[float] = None,
                       submission_deadline: Optional[datetime] = None,
                       investigators: Optional[List[Dict[str, str]]] = None,
                       tags: Optional[List[str]] = None) -> str:
        """
        Create a new grant proposal.
        
        Args:
            title: Proposal title
            funding_agency: Funding agency name
            agency_type: Type of funding agency
            abstract: Proposal abstract
            status: Current status of the proposal
            program_name: Name of the funding program
            requested_amount: Amount of funding requested
            submission_deadline: Deadline for submission
            investigators: List of investigator dictionaries with 'name', optional 'email' and 'affiliation'
            tags: Tags for the proposal
            
        Returns:
            ID of the created proposal
        """
        # Handle string agency type
        if isinstance(agency_type, str):
            agency_type = FundingAgencyType(agency_type)
        
        # Handle string status
        if isinstance(status, str):
            status = FundingStatus(status)
        
        # Create investigator objects
        investigator_objects = []
        if investigators:
            for investigator_dict in investigators:
                person = Person(
                    name=investigator_dict["name"],
                    email=investigator_dict.get("email"),
                    affiliation=investigator_dict.get("affiliation"),
                    role=investigator_dict.get("role", "investigator")
                )
                investigator_objects.append(person)
        
        # Create the proposal
        proposal = GrantProposal(
            title=title,
            funding_agency=funding_agency,
            agency_type=agency_type,
            abstract=abstract,
            status=status,
            program_name=program_name,
            requested_amount=requested_amount,
            submission_deadline=submission_deadline,
            investigators=investigator_objects,
            tags=set(tags or [])
        )
        
        # Add some default sections
        proposal.sections["introduction"] = ProposalSection(
            title="Introduction",
            content="",
        )
        
        proposal.sections["background"] = ProposalSection(
            title="Background and Significance",
            content="",
        )
        
        proposal.sections["specific_aims"] = ProposalSection(
            title="Specific Aims",
            content="",
        )
        
        proposal.sections["methods"] = ProposalSection(
            title="Research Methods",
            content="",
        )
        
        proposal.sections["timeline"] = ProposalSection(
            title="Project Timeline",
            content="",
        )
        
        proposal.sections["budget_justification"] = ProposalSection(
            title="Budget Justification",
            content="",
        )
        
        # Save the proposal
        proposal_id = self.proposal_storage.save(proposal)
        
        return proposal_id
    
    def update_proposal(self,
                       proposal_id: str,
                       title: Optional[str] = None,
                       abstract: Optional[str] = None,
                       status: Optional[Union[str, FundingStatus]] = None,
                       program_name: Optional[str] = None,
                       requested_amount: Optional[float] = None,
                       submission_deadline: Optional[datetime] = None,
                       tags: Optional[List[str]] = None,
                       add_tags: Optional[List[str]] = None,
                       remove_tags: Optional[List[str]] = None) -> None:
        """
        Update an existing proposal.
        
        Args:
            proposal_id: ID of the proposal to update
            title: New title (if None, keep existing)
            abstract: New abstract (if None, keep existing)
            status: New status (if None, keep existing)
            program_name: New program name (if None, keep existing)
            requested_amount: New requested amount (if None, keep existing)
            submission_deadline: New submission deadline (if None, keep existing)
            tags: Complete replacement of tags (if None, keep existing)
            add_tags: Tags to add to existing set
            remove_tags: Tags to remove from existing set
            
        Raises:
            ValueError: If the proposal doesn't exist
        """
        if not self.proposal_storage.exists(proposal_id):
            raise ValueError(f"Proposal with ID {proposal_id} does not exist")
        
        proposal = self.proposal_storage.get(proposal_id)
        
        # Update title if provided
        if title is not None:
            proposal.title = title
        
        # Update abstract if provided
        if abstract is not None:
            proposal.abstract = abstract
        
        # Update status if provided
        if status is not None:
            if isinstance(status, str):
                status = FundingStatus(status)
            proposal.update_status(status)
        
        # Update program name if provided
        if program_name is not None:
            proposal.program_name = program_name
        
        # Update requested amount if provided
        if requested_amount is not None:
            proposal.requested_amount = requested_amount
        
        # Update submission deadline if provided
        if submission_deadline is not None:
            proposal.submission_deadline = submission_deadline
        
        # Update tags if provided
        if tags is not None:
            proposal.tags = set(tags)
        
        # Add tags if provided
        if add_tags:
            proposal.tags.update(add_tags)
        
        # Remove tags if provided
        if remove_tags:
            proposal.tags.difference_update(remove_tags)
        
        # Save the updated proposal
        self.proposal_storage.save(proposal)
    
    def delete_proposal(self, proposal_id: str) -> bool:
        """
        Delete a proposal.
        
        Args:
            proposal_id: ID of the proposal to delete
            
        Returns:
            True if the proposal was deleted, False if it didn't exist
        """
        return self.proposal_storage.delete(proposal_id)
    
    def get_proposal(self, proposal_id: str) -> GrantProposal:
        """
        Get a proposal by ID.
        
        Args:
            proposal_id: ID of the proposal to retrieve
            
        Returns:
            The requested proposal
            
        Raises:
            ValueError: If the proposal doesn't exist
        """
        if not self.proposal_storage.exists(proposal_id):
            raise ValueError(f"Proposal with ID {proposal_id} does not exist")
        
        return self.proposal_storage.get(proposal_id)
    
    def add_section(self,
                   proposal_id: str,
                   section_name: str,
                   title: str,
                   content: str = "") -> None:
        """
        Add a section to a proposal.
        
        Args:
            proposal_id: ID of the proposal
            section_name: Name/key for the section
            title: Title of the section
            content: Initial content for the section
            
        Raises:
            ValueError: If the proposal doesn't exist or section already exists
        """
        if not self.proposal_storage.exists(proposal_id):
            raise ValueError(f"Proposal with ID {proposal_id} does not exist")
        
        proposal = self.proposal_storage.get(proposal_id)
        
        if section_name in proposal.sections:
            raise ValueError(f"Section '{section_name}' already exists in the proposal")
        
        section = ProposalSection(
            title=title,
            content=content
        )
        
        proposal.add_section(section_name, section)
        self.proposal_storage.save(proposal)
    
    def update_section(self,
                      proposal_id: str,
                      section_name: str,
                      content: str) -> None:
        """
        Update the content of a proposal section.
        
        Args:
            proposal_id: ID of the proposal
            section_name: Name/key of the section to update
            content: New content for the section
            
        Raises:
            ValueError: If the proposal or section doesn't exist
        """
        if not self.proposal_storage.exists(proposal_id):
            raise ValueError(f"Proposal with ID {proposal_id} does not exist")
        
        proposal = self.proposal_storage.get(proposal_id)
        
        if section_name not in proposal.sections:
            raise ValueError(f"Section '{section_name}' does not exist in the proposal")
        
        proposal.update_section(section_name, content)
        self.proposal_storage.save(proposal)
    
    def add_budget_item(self,
                       proposal_id: str,
                       category: str,
                       item_name: str,
                       amount: float,
                       justification: str,
                       year: Optional[int] = None) -> None:
        """
        Add a budget item to a proposal.
        
        Args:
            proposal_id: ID of the proposal
            category: Budget category
            item_name: Name of the budget item
            amount: Amount requested
            justification: Justification for the item
            year: Budget year
            
        Raises:
            ValueError: If the proposal doesn't exist
        """
        if not self.proposal_storage.exists(proposal_id):
            raise ValueError(f"Proposal with ID {proposal_id} does not exist")
        
        proposal = self.proposal_storage.get(proposal_id)
        
        budget_item = BudgetItem(
            category=category,
            item_name=item_name,
            amount=amount,
            justification=justification,
            year=year
        )
        
        proposal.add_budget_item(budget_item)
        self.proposal_storage.save(proposal)
    
    def add_investigator(self,
                        proposal_id: str,
                        name: str,
                        email: Optional[str] = None,
                        affiliation: Optional[str] = None,
                        role: Optional[str] = None) -> None:
        """
        Add an investigator to a proposal.
        
        Args:
            proposal_id: ID of the proposal
            name: Investigator name
            email: Investigator email
            affiliation: Investigator affiliation
            role: Investigator role
            
        Raises:
            ValueError: If the proposal doesn't exist
        """
        if not self.proposal_storage.exists(proposal_id):
            raise ValueError(f"Proposal with ID {proposal_id} does not exist")
        
        proposal = self.proposal_storage.get(proposal_id)
        
        investigator = Person(
            name=name,
            email=email,
            affiliation=affiliation,
            role=role or "investigator"
        )
        
        proposal.add_investigator(investigator)
        self.proposal_storage.save(proposal)
    
    def add_research_question(self, proposal_id: str, question_id: str) -> None:
        """
        Add a research question to a proposal.
        
        Args:
            proposal_id: ID of the proposal
            question_id: ID of the research question
            
        Raises:
            ValueError: If the proposal doesn't exist
        """
        if not self.proposal_storage.exists(proposal_id):
            raise ValueError(f"Proposal with ID {proposal_id} does not exist")
        
        proposal = self.proposal_storage.get(proposal_id)
        
        question_ref = Reference(
            item_id=question_id,
            item_type=KnowledgeItemType.RESEARCH_QUESTION
        )
        
        proposal.add_research_question(question_ref)
        self.proposal_storage.save(proposal)
    
    def add_key_citation(self, proposal_id: str, citation_id: str) -> None:
        """
        Add a key citation to a proposal.
        
        Args:
            proposal_id: ID of the proposal
            citation_id: ID of the citation
            
        Raises:
            ValueError: If the proposal doesn't exist
        """
        if not self.proposal_storage.exists(proposal_id):
            raise ValueError(f"Proposal with ID {proposal_id} does not exist")
        
        proposal = self.proposal_storage.get(proposal_id)
        
        citation_ref = Reference(
            item_id=citation_id,
            item_type=KnowledgeItemType.CITATION
        )
        
        proposal.add_key_citation(citation_ref)
        self.proposal_storage.save(proposal)
    
    def create_workspace(self,
                        name: str,
                        description: Optional[str] = None,
                        proposal_id: Optional[str] = None,
                        deadline: Optional[datetime] = None,
                        tags: Optional[List[str]] = None) -> str:
        """
        Create a grant proposal workspace.
        
        Args:
            name: Workspace name
            description: Workspace description
            proposal_id: ID of the associated proposal (if any)
            deadline: Deadline for the workspace
            tags: Tags for the workspace
            
        Returns:
            ID of the created workspace
            
        Raises:
            ValueError: If the proposal doesn't exist
        """
        # Validate proposal if provided
        if proposal_id and not self.proposal_storage.exists(proposal_id):
            raise ValueError(f"Proposal with ID {proposal_id} does not exist")
        
        # Create the workspace
        workspace = GrantProposalWorkspace(
            name=name,
            description=description,
            proposal_id=proposal_id,
            deadline=deadline,
            tags=set(tags or [])
        )
        
        # Save the workspace
        workspace_id = self.workspace_storage.save(workspace)
        
        return workspace_id
    
    def update_workspace(self,
                        workspace_id: str,
                        name: Optional[str] = None,
                        description: Optional[str] = None,
                        status: Optional[str] = None,
                        deadline: Optional[datetime] = None,
                        tags: Optional[List[str]] = None,
                        add_tags: Optional[List[str]] = None,
                        remove_tags: Optional[List[str]] = None) -> None:
        """
        Update an existing workspace.
        
        Args:
            workspace_id: ID of the workspace to update
            name: New name (if None, keep existing)
            description: New description (if None, keep existing)
            status: New status (if None, keep existing)
            deadline: New deadline (if None, keep existing)
            tags: Complete replacement of tags (if None, keep existing)
            add_tags: Tags to add to existing set
            remove_tags: Tags to remove from existing set
            
        Raises:
            ValueError: If the workspace doesn't exist
        """
        if not self.workspace_storage.exists(workspace_id):
            raise ValueError(f"Workspace with ID {workspace_id} does not exist")
        
        workspace = self.workspace_storage.get(workspace_id)
        
        # Update name if provided
        if name is not None:
            workspace.name = name
        
        # Update description if provided
        if description is not None:
            workspace.description = description
        
        # Update status if provided
        if status is not None:
            workspace.status = status
        
        # Update deadline if provided
        if deadline is not None:
            workspace.deadline = deadline
        
        # Update tags if provided
        if tags is not None:
            workspace.tags = set(tags)
        
        # Add tags if provided
        if add_tags:
            workspace.tags.update(add_tags)
        
        # Remove tags if provided
        if remove_tags:
            workspace.tags.difference_update(remove_tags)
        
        # Update timestamp
        workspace.updated_at = datetime.now()
        
        # Save the updated workspace
        self.workspace_storage.save(workspace)
    
    def delete_workspace(self, workspace_id: str) -> bool:
        """
        Delete a workspace.
        
        Args:
            workspace_id: ID of the workspace to delete
            
        Returns:
            True if the workspace was deleted, False if it didn't exist
        """
        return self.workspace_storage.delete(workspace_id)
    
    def get_workspace(self, workspace_id: str) -> GrantProposalWorkspace:
        """
        Get a workspace by ID.
        
        Args:
            workspace_id: ID of the workspace to retrieve
            
        Returns:
            The requested workspace
            
        Raises:
            ValueError: If the workspace doesn't exist
        """
        if not self.workspace_storage.exists(workspace_id):
            raise ValueError(f"Workspace with ID {workspace_id} does not exist")
        
        return self.workspace_storage.get(workspace_id)
    
    def add_note_to_workspace(self, workspace_id: str, note_id: str) -> None:
        """
        Add a note to a workspace.
        
        Args:
            workspace_id: ID of the workspace
            note_id: ID of the note to add
            
        Raises:
            ValueError: If the workspace doesn't exist
        """
        if not self.workspace_storage.exists(workspace_id):
            raise ValueError(f"Workspace with ID {workspace_id} does not exist")
        
        workspace = self.workspace_storage.get(workspace_id)
        workspace.add_note(note_id)
        self.workspace_storage.save(workspace)
    
    def add_citation_to_workspace(self, workspace_id: str, citation_id: str) -> None:
        """
        Add a citation to a workspace.
        
        Args:
            workspace_id: ID of the workspace
            citation_id: ID of the citation to add
            
        Raises:
            ValueError: If the workspace doesn't exist
        """
        if not self.workspace_storage.exists(workspace_id):
            raise ValueError(f"Workspace with ID {workspace_id} does not exist")
        
        workspace = self.workspace_storage.get(workspace_id)
        workspace.add_citation(citation_id)
        self.workspace_storage.save(workspace)
    
    def add_question_to_workspace(self, workspace_id: str, question_id: str) -> None:
        """
        Add a research question to a workspace.
        
        Args:
            workspace_id: ID of the workspace
            question_id: ID of the research question to add
            
        Raises:
            ValueError: If the workspace doesn't exist
        """
        if not self.workspace_storage.exists(workspace_id):
            raise ValueError(f"Workspace with ID {workspace_id} does not exist")
        
        workspace = self.workspace_storage.get(workspace_id)
        workspace.add_question(question_id)
        self.workspace_storage.save(workspace)
    
    def add_experiment_to_workspace(self, workspace_id: str, experiment_id: str) -> None:
        """
        Add an experiment to a workspace.
        
        Args:
            workspace_id: ID of the workspace
            experiment_id: ID of the experiment to add
            
        Raises:
            ValueError: If the workspace doesn't exist
        """
        if not self.workspace_storage.exists(workspace_id):
            raise ValueError(f"Workspace with ID {workspace_id} does not exist")
        
        workspace = self.workspace_storage.get(workspace_id)
        workspace.add_experiment(experiment_id)
        self.workspace_storage.save(workspace)
    
    def link_workspace_to_proposal(self, workspace_id: str, proposal_id: str) -> None:
        """
        Link a workspace to a proposal.
        
        Args:
            workspace_id: ID of the workspace
            proposal_id: ID of the proposal
            
        Raises:
            ValueError: If the workspace or proposal doesn't exist
        """
        if not self.workspace_storage.exists(workspace_id):
            raise ValueError(f"Workspace with ID {workspace_id} does not exist")
        
        if not self.proposal_storage.exists(proposal_id):
            raise ValueError(f"Proposal with ID {proposal_id} does not exist")
        
        workspace = self.workspace_storage.get(workspace_id)
        workspace.proposal_id = proposal_id
        workspace.updated_at = datetime.now()
        self.workspace_storage.save(workspace)
    
    def search_proposals(self,
                        text: Optional[str] = None,
                        funding_agency: Optional[str] = None,
                        status: Optional[Union[str, FundingStatus]] = None,
                        investigator: Optional[str] = None,
                        active_only: bool = False,
                        tags: Optional[List[str]] = None,
                        before_deadline: Optional[datetime] = None,
                        after_deadline: Optional[datetime] = None) -> List[str]:
        """
        Search for proposals based on various criteria.
        
        Args:
            text: Text to search for in title, abstract, and content
            funding_agency: Funding agency to filter by
            status: Status to filter by
            investigator: Investigator name to filter by
            active_only: If True, only return active proposals
            tags: Tags to filter by
            before_deadline: Only include proposals due before this date
            after_deadline: Only include proposals due after this date
            
        Returns:
            List of matching proposal IDs
        """
        # Start with all proposals
        result_ids = set(self.proposal_storage.list_ids())
        
        # Filter by text if specified
        if text:
            text_results = set(self.proposal_storage.search_by_content(text))
            result_ids.intersection_update(text_results)
        
        # Filter by funding agency if specified
        if funding_agency:
            agency_results = set(self.proposal_storage.get_by_funding_agency(funding_agency))
            result_ids.intersection_update(agency_results)
        
        # Filter by status if specified
        if status:
            if isinstance(status, str):
                status = FundingStatus(status)
            
            status_results = set(self.proposal_storage.get_by_status(status))
            result_ids.intersection_update(status_results)
        
        # Filter by active only if specified
        if active_only:
            active_results = set(self.proposal_storage.get_active_proposals())
            result_ids.intersection_update(active_results)
        
        # Filter by investigator if specified
        if investigator:
            investigator_results = set(self.proposal_storage.search_by_investigator(investigator))
            result_ids.intersection_update(investigator_results)
        
        # Filter by tags if specified
        if tags:
            tag_results = set(self.proposal_storage.search_by_tags(tags))
            result_ids.intersection_update(tag_results)
        
        # Filter by deadline if specified
        if before_deadline or after_deadline:
            deadline_results = set(self.proposal_storage.get_by_deadline(
                before_date=before_deadline,
                after_date=after_deadline
            ))
            result_ids.intersection_update(deadline_results)
        
        return list(result_ids)
    
    def search_workspaces(self,
                         text: Optional[str] = None,
                         status: Optional[str] = None,
                         active_only: bool = False,
                         tags: Optional[List[str]] = None,
                         before_deadline: Optional[datetime] = None,
                         after_deadline: Optional[datetime] = None,
                         contains_note_id: Optional[str] = None,
                         contains_citation_id: Optional[str] = None,
                         contains_question_id: Optional[str] = None) -> List[str]:
        """
        Search for workspaces based on various criteria.
        
        Args:
            text: Text to search for in name and description
            status: Status to filter by
            active_only: If True, only return active workspaces
            tags: Tags to filter by
            before_deadline: Only include workspaces due before this date
            after_deadline: Only include workspaces due after this date
            contains_note_id: Only include workspaces containing this note
            contains_citation_id: Only include workspaces containing this citation
            contains_question_id: Only include workspaces containing this question
            
        Returns:
            List of matching workspace IDs
        """
        # Start with all workspaces
        result_ids = set(self.workspace_storage.list_ids())
        
        # Filter by text if specified
        if text:
            text_results = set(self.workspace_storage.search_by_name(text))
            result_ids.intersection_update(text_results)
        
        # Filter by status if specified
        if status:
            status_results = set()
            for workspace_id in result_ids:
                try:
                    workspace = self.workspace_storage.get(workspace_id)
                    if workspace.status == status:
                        status_results.add(workspace_id)
                except Exception:
                    continue
            
            result_ids.intersection_update(status_results)
        
        # Filter by active only if specified
        if active_only:
            active_results = set(self.workspace_storage.get_active_workspaces())
            result_ids.intersection_update(active_results)
        
        # Filter by tags if specified
        if tags:
            tag_results = set(self.workspace_storage.search_by_tags(tags))
            result_ids.intersection_update(tag_results)
        
        # Filter by deadline if specified
        if before_deadline or after_deadline:
            deadline_results = set(self.workspace_storage.get_by_deadline(
                before_date=before_deadline,
                after_date=after_deadline
            ))
            result_ids.intersection_update(deadline_results)
        
        # Filter by note if specified
        if contains_note_id:
            note_results = set(self.workspace_storage.get_workspaces_containing_note(contains_note_id))
            result_ids.intersection_update(note_results)
        
        # Filter by citation if specified
        if contains_citation_id:
            citation_results = set(self.workspace_storage.get_workspaces_containing_citation(contains_citation_id))
            result_ids.intersection_update(citation_results)
        
        # Filter by question if specified
        if contains_question_id:
            question_results = set(self.workspace_storage.get_workspaces_containing_question(contains_question_id))
            result_ids.intersection_update(question_results)
        
        return list(result_ids)
"""
Grant Proposal storage functionality for the Academic Knowledge Vault system.

This module defines storage implementations for grant proposals and workspaces.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Any

from academic_knowledge_vault.models.grant_proposal import (
    GrantProposal,
    GrantProposalWorkspace,
    FundingStatus,
)
from academic_knowledge_vault.storage.base import JsonFileStorage


class GrantProposalStorage(JsonFileStorage[GrantProposal]):
    """Storage for grant proposals."""
    
    def __init__(self, base_dir: Union[str, Path], create_dir: bool = True):
        """
        Initialize grant proposal storage.
        
        Args:
            base_dir: Base directory for proposal storage
            create_dir: Whether to create the directory if it doesn't exist
        """
        super().__init__(base_dir, GrantProposal, create_dir)
    
    def get_by_status(self, status: Union[str, FundingStatus]) -> List[str]:
        """
        Get proposals with a specific status.
        
        Args:
            status: Status to filter by
            
        Returns:
            List of proposal IDs with the specified status
        """
        if isinstance(status, str):
            status = FundingStatus(status)
        
        result_ids = []
        
        for proposal_id in self.list_ids():
            try:
                proposal = self.get(proposal_id)
                
                if proposal.status == status:
                    result_ids.append(proposal_id)
                    
            except Exception:
                # Skip problematic proposals
                continue
        
        return result_ids
    
    def get_by_funding_agency(self, agency: str) -> List[str]:
        """
        Get proposals for a specific funding agency.
        
        Args:
            agency: Agency name (partial match)
            
        Returns:
            List of proposal IDs for the agency
        """
        agency = agency.lower()
        result_ids = []
        
        for proposal_id in self.list_ids():
            try:
                proposal = self.get(proposal_id)
                
                if proposal.funding_agency and agency in proposal.funding_agency.lower():
                    result_ids.append(proposal_id)
                    
            except Exception:
                # Skip problematic proposals
                continue
        
        return result_ids
    
    def get_active_proposals(self) -> List[str]:
        """
        Get all active proposals (not completed, rejected, or abandoned).
        
        Returns:
            List of active proposal IDs
        """
        inactive_statuses = [FundingStatus.COMPLETED, FundingStatus.REJECTED]
        result_ids = []
        
        for proposal_id in self.list_ids():
            try:
                proposal = self.get(proposal_id)
                
                if proposal.status not in inactive_statuses:
                    result_ids.append(proposal_id)
                    
            except Exception:
                # Skip problematic proposals
                continue
        
        return result_ids
    
    def get_by_deadline(self, before_date: Optional[datetime] = None, after_date: Optional[datetime] = None) -> List[str]:
        """
        Get proposals with deadlines in a specific range.
        
        Args:
            before_date: Get proposals due before this date
            after_date: Get proposals due after this date
            
        Returns:
            List of proposal IDs with deadlines in the range
        """
        result_ids = []
        
        for proposal_id in self.list_ids():
            try:
                proposal = self.get(proposal_id)
                
                if not proposal.submission_deadline:
                    continue
                
                include = True
                
                if before_date and proposal.submission_deadline > before_date:
                    include = False
                
                if after_date and proposal.submission_deadline < after_date:
                    include = False
                
                if include:
                    result_ids.append(proposal_id)
                    
            except Exception:
                # Skip problematic proposals
                continue
        
        return result_ids
    
    def search_by_title(self, title_text: str) -> List[str]:
        """
        Search proposals by title.
        
        Args:
            title_text: Text to search for in titles
            
        Returns:
            List of proposal IDs with matching titles
        """
        title_text = title_text.lower()
        result_ids = []
        
        for proposal_id in self.list_ids():
            try:
                proposal = self.get(proposal_id)
                
                if title_text in proposal.title.lower():
                    result_ids.append(proposal_id)
                    
            except Exception:
                # Skip problematic proposals
                continue
        
        return result_ids
    
    def search_by_abstract(self, abstract_text: str) -> List[str]:
        """
        Search proposals by abstract.
        
        Args:
            abstract_text: Text to search for in abstracts
            
        Returns:
            List of proposal IDs with matching abstracts
        """
        abstract_text = abstract_text.lower()
        result_ids = []
        
        for proposal_id in self.list_ids():
            try:
                proposal = self.get(proposal_id)
                
                if proposal.abstract and abstract_text in proposal.abstract.lower():
                    result_ids.append(proposal_id)
                    
            except Exception:
                # Skip problematic proposals
                continue
        
        return result_ids
    
    def search_by_investigator(self, investigator_name: str) -> List[str]:
        """
        Search proposals by investigator name.
        
        Args:
            investigator_name: Investigator name to search for
            
        Returns:
            List of proposal IDs with matching investigators
        """
        investigator_name = investigator_name.lower()
        result_ids = []
        
        for proposal_id in self.list_ids():
            try:
                proposal = self.get(proposal_id)
                
                for investigator in proposal.investigators:
                    if investigator_name in investigator.name.lower():
                        result_ids.append(proposal_id)
                        break
                    
            except Exception:
                # Skip problematic proposals
                continue
        
        return result_ids
    
    def get_proposals_by_grant_number(self, grant_number: str) -> List[str]:
        """
        Get proposals with a specific grant number.
        
        Args:
            grant_number: Grant number to search for
            
        Returns:
            List of proposal IDs with the matching grant number
        """
        grant_number = grant_number.lower()
        result_ids = []
        
        for proposal_id in self.list_ids():
            try:
                proposal = self.get(proposal_id)
                
                if proposal.grant_number and grant_number in proposal.grant_number.lower():
                    result_ids.append(proposal_id)
                    
            except Exception:
                # Skip problematic proposals
                continue
        
        return result_ids
    
    def search_by_content(self, text: str) -> List[str]:
        """
        Search proposals by content in any section.
        
        Args:
            text: Text to search for in the content
            
        Returns:
            List of proposal IDs with matching content
        """
        text = text.lower()
        result_ids = []
        
        for proposal_id in self.list_ids():
            try:
                proposal = self.get(proposal_id)
                
                # Check title and abstract
                if text in proposal.title.lower():
                    result_ids.append(proposal_id)
                    continue
                
                if proposal.abstract and text in proposal.abstract.lower():
                    result_ids.append(proposal_id)
                    continue
                
                # Check sections
                for section in proposal.sections.values():
                    if text in section.content.lower():
                        result_ids.append(proposal_id)
                        break
                    
            except Exception:
                # Skip problematic proposals
                continue
        
        return result_ids
    
    def search_by_tags(self, tags: List[str], match_all: bool = True) -> List[str]:
        """
        Search for proposals with specific tags.
        
        Args:
            tags: Tags to search for
            match_all: If True, proposals must have all tags; if False, any tag is sufficient
            
        Returns:
            List of proposal IDs matching the tag criteria
        """
        if not tags:
            return self.list_ids()
        
        result_ids = []
        
        for proposal_id in self.list_ids():
            try:
                proposal = self.get(proposal_id)
                
                if match_all:
                    # All tags must match
                    if all(tag in proposal.tags for tag in tags):
                        result_ids.append(proposal_id)
                else:
                    # Any tag match is sufficient
                    if any(tag in proposal.tags for tag in tags):
                        result_ids.append(proposal_id)
                    
            except Exception:
                # Skip problematic proposals
                continue
        
        return result_ids


class GrantProposalWorkspaceStorage(JsonFileStorage[GrantProposalWorkspace]):
    """Storage for grant proposal workspaces."""
    
    def __init__(self, base_dir: Union[str, Path], create_dir: bool = True):
        """
        Initialize workspace storage.
        
        Args:
            base_dir: Base directory for workspace storage
            create_dir: Whether to create the directory if it doesn't exist
        """
        super().__init__(base_dir, GrantProposalWorkspace, create_dir)
    
    def get_by_proposal(self, proposal_id: str) -> Optional[str]:
        """
        Get the workspace for a specific proposal.
        
        Args:
            proposal_id: ID of the proposal
            
        Returns:
            Workspace ID if found, None otherwise
        """
        for workspace_id in self.list_ids():
            try:
                workspace = self.get(workspace_id)
                
                if workspace.proposal_id == proposal_id:
                    return workspace_id
                    
            except Exception:
                # Skip problematic workspaces
                continue
        
        return None
    
    def get_active_workspaces(self) -> List[str]:
        """
        Get all active workspaces.
        
        Returns:
            List of active workspace IDs
        """
        result_ids = []
        
        for workspace_id in self.list_ids():
            try:
                workspace = self.get(workspace_id)
                
                if workspace.status == "active":
                    result_ids.append(workspace_id)
                    
            except Exception:
                # Skip problematic workspaces
                continue
        
        return result_ids
    
    def get_by_deadline(self, before_date: Optional[datetime] = None, after_date: Optional[datetime] = None) -> List[str]:
        """
        Get workspaces with deadlines in a specific range.
        
        Args:
            before_date: Get workspaces due before this date
            after_date: Get workspaces due after this date
            
        Returns:
            List of workspace IDs with deadlines in the range
        """
        result_ids = []
        
        for workspace_id in self.list_ids():
            try:
                workspace = self.get(workspace_id)
                
                if not workspace.deadline:
                    continue
                
                include = True
                
                if before_date and workspace.deadline > before_date:
                    include = False
                
                if after_date and workspace.deadline < after_date:
                    include = False
                
                if include:
                    result_ids.append(workspace_id)
                    
            except Exception:
                # Skip problematic workspaces
                continue
        
        return result_ids
    
    def search_by_name(self, name_text: str) -> List[str]:
        """
        Search workspaces by name.
        
        Args:
            name_text: Text to search for in names
            
        Returns:
            List of workspace IDs with matching names
        """
        name_text = name_text.lower()
        result_ids = []
        
        for workspace_id in self.list_ids():
            try:
                workspace = self.get(workspace_id)
                
                if name_text in workspace.name.lower():
                    result_ids.append(workspace_id)
                    
            except Exception:
                # Skip problematic workspaces
                continue
        
        return result_ids
    
    def search_by_tags(self, tags: List[str], match_all: bool = True) -> List[str]:
        """
        Search for workspaces with specific tags.
        
        Args:
            tags: Tags to search for
            match_all: If True, workspaces must have all tags; if False, any tag is sufficient
            
        Returns:
            List of workspace IDs matching the tag criteria
        """
        if not tags:
            return self.list_ids()
        
        result_ids = []
        
        for workspace_id in self.list_ids():
            try:
                workspace = self.get(workspace_id)
                
                if match_all:
                    # All tags must match
                    if all(tag in workspace.tags for tag in tags):
                        result_ids.append(workspace_id)
                else:
                    # Any tag match is sufficient
                    if any(tag in workspace.tags for tag in tags):
                        result_ids.append(workspace_id)
                    
            except Exception:
                # Skip problematic workspaces
                continue
        
        return result_ids
    
    def get_workspaces_containing_note(self, note_id: str) -> List[str]:
        """
        Find workspaces that contain a specific note.
        
        Args:
            note_id: ID of the note
            
        Returns:
            List of workspace IDs containing the note
        """
        result_ids = []
        
        for workspace_id in self.list_ids():
            try:
                workspace = self.get(workspace_id)
                
                if note_id in workspace.note_ids:
                    result_ids.append(workspace_id)
                    
            except Exception:
                # Skip problematic workspaces
                continue
        
        return result_ids
    
    def get_workspaces_containing_citation(self, citation_id: str) -> List[str]:
        """
        Find workspaces that contain a specific citation.
        
        Args:
            citation_id: ID of the citation
            
        Returns:
            List of workspace IDs containing the citation
        """
        result_ids = []
        
        for workspace_id in self.list_ids():
            try:
                workspace = self.get(workspace_id)
                
                if citation_id in workspace.citation_ids:
                    result_ids.append(workspace_id)
                    
            except Exception:
                # Skip problematic workspaces
                continue
        
        return result_ids
    
    def get_workspaces_containing_question(self, question_id: str) -> List[str]:
        """
        Find workspaces that contain a specific research question.
        
        Args:
            question_id: ID of the research question
            
        Returns:
            List of workspace IDs containing the question
        """
        result_ids = []
        
        for workspace_id in self.list_ids():
            try:
                workspace = self.get(workspace_id)
                
                if question_id in workspace.question_ids:
                    result_ids.append(workspace_id)
                    
            except Exception:
                # Skip problematic workspaces
                continue
        
        return result_ids
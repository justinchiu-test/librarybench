"""Suppression management for false positives."""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from .models import Vulnerability, SuppressionRule


class SuppressionManager:
    """Manages suppression rules for false positives."""
    
    def __init__(self, suppression_file: Optional[Path] = None):
        self.rules: List[SuppressionRule] = []
        self.audit_log: List[Dict[str, Any]] = []
        
        if suppression_file and suppression_file.exists():
            self.load_rules(suppression_file)
    
    def load_rules(self, file_path: Path) -> None:
        """Load suppression rules from file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                self.rules = [SuppressionRule(**rule) for rule in data.get('rules', [])]
        except Exception as e:
            # Log error but continue
            self.audit_log.append({
                "action": "load_rules_error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    def save_rules(self, file_path: Path) -> None:
        """Save suppression rules to file."""
        data = {
            "rules": [rule.model_dump() for rule in self.rules],
            "audit_log": self.audit_log
        }
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def add_rule(self, rule: SuppressionRule) -> None:
        """Add a new suppression rule."""
        self.rules.append(rule)
        self.audit_log.append({
            "action": "add_rule",
            "rule_id": rule.id,
            "created_by": rule.created_by,
            "timestamp": datetime.now().isoformat()
        })
    
    def should_suppress(self, vulnerability: Vulnerability) -> bool:
        """Check if vulnerability should be suppressed."""
        for rule in self.rules:
            if not rule.active:
                continue
            
            # Check expiration
            if rule.expires_at and datetime.now() > rule.expires_at:
                rule.active = False
                continue
            
            # Check pattern match
            if self._matches_rule(vulnerability, rule):
                self.audit_log.append({
                    "action": "suppress_vulnerability",
                    "vulnerability_id": vulnerability.id,
                    "rule_id": rule.id,
                    "timestamp": datetime.now().isoformat()
                })
                return True
        
        return False
    
    def _matches_rule(self, vulnerability: Vulnerability, rule: SuppressionRule) -> bool:
        """Check if vulnerability matches suppression rule."""
        # Match by vulnerability ID pattern
        if re.match(rule.pattern, vulnerability.id):
            return True
        
        # Match by file path pattern
        if re.search(rule.pattern, str(vulnerability.location.file_path)):
            return True
        
        # Match by vulnerability type
        if rule.pattern == vulnerability.type.value:
            return True
        
        # Match by specific location
        location_pattern = f"{vulnerability.location.file_path}:{vulnerability.location.line_start}"
        if rule.pattern == location_pattern:
            return True
        
        return False
    
    def get_suppression_reason(self, vulnerability: Vulnerability) -> str:
        """Get reason for suppressing a vulnerability."""
        for rule in self.rules:
            if rule.active and self._matches_rule(vulnerability, rule):
                return rule.reason
        return "Unknown suppression reason"
    
    def create_rule_from_vulnerability(self, vulnerability: Vulnerability, 
                                     reason: str, created_by: str,
                                     expires_days: Optional[int] = None) -> SuppressionRule:
        """Create a suppression rule from a vulnerability."""
        expires_at = None
        if expires_days:
            from datetime import timedelta
            expires_at = datetime.now() + timedelta(days=expires_days)
        
        rule = SuppressionRule(
            id=f"suppress-{vulnerability.id}",
            pattern=f"{vulnerability.location.file_path}:{vulnerability.location.line_start}",
            reason=reason,
            created_at=datetime.now(),
            expires_at=expires_at,
            created_by=created_by,
            active=True
        )
        
        return rule
    
    def get_active_rules(self) -> List[SuppressionRule]:
        """Get all active suppression rules."""
        return [rule for rule in self.rules if rule.active]
    
    def get_audit_trail(self, start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get audit trail for suppression actions."""
        trail = self.audit_log
        
        if start_date:
            trail = [
                entry for entry in trail
                if datetime.fromisoformat(entry['timestamp']) >= start_date
            ]
        
        if end_date:
            trail = [
                entry for entry in trail
                if datetime.fromisoformat(entry['timestamp']) <= end_date
            ]
        
        return trail
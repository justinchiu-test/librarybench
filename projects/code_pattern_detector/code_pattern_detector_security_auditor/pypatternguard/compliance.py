"""Compliance mapping for regulatory frameworks."""

import uuid
from datetime import datetime
from typing import Dict, List, Any

from .models import (
    ScanResult,
    ComplianceReport,
    ComplianceRequirement,
    ComplianceFramework,
    VulnerabilityType,
    SeverityLevel,
)


class ComplianceMapper:
    """Maps vulnerabilities to compliance requirements."""
    
    # PCI-DSS requirement mappings
    PCI_DSS_MAPPINGS = {
        VulnerabilityType.INJECTION: ["6.5.1"],
        VulnerabilityType.BROKEN_AUTH: ["6.5.10", "8.2"],
        VulnerabilityType.SENSITIVE_DATA_EXPOSURE: ["3.4", "4.1"],
        VulnerabilityType.BROKEN_ACCESS_CONTROL: ["6.5.8", "7.1"],
        VulnerabilityType.SECURITY_MISCONFIGURATION: ["2.2", "2.3"],
        VulnerabilityType.XSS: ["6.5.7"],
        VulnerabilityType.INSECURE_DESERIALIZATION: ["6.5.8"],
        VulnerabilityType.COMPONENTS_VULNERABILITIES: ["6.2"],
        VulnerabilityType.INSUFFICIENT_LOGGING: ["10.1", "10.2"],
        VulnerabilityType.CRYPTO_FAILURE: ["3.4", "4.1"],
        VulnerabilityType.HARDCODED_SECRET: ["2.3", "8.2.1"],
        VulnerabilityType.INPUT_VALIDATION: ["6.5.1", "6.5.8"],
    }
    
    # SOC2 control mappings
    SOC2_MAPPINGS = {
        VulnerabilityType.INJECTION: ["CC6.1", "CC6.7"],
        VulnerabilityType.BROKEN_AUTH: ["CC6.1", "CC6.2"],
        VulnerabilityType.SENSITIVE_DATA_EXPOSURE: ["CC6.1", "CC6.7"],
        VulnerabilityType.BROKEN_ACCESS_CONTROL: ["CC6.3"],
        VulnerabilityType.SECURITY_MISCONFIGURATION: ["CC7.1", "CC7.2"],
        VulnerabilityType.XSS: ["CC6.1"],
        VulnerabilityType.INSECURE_DESERIALIZATION: ["CC6.1"],
        VulnerabilityType.COMPONENTS_VULNERABILITIES: ["CC7.1"],
        VulnerabilityType.INSUFFICIENT_LOGGING: ["CC7.2", "CC7.3"],
        VulnerabilityType.CRYPTO_FAILURE: ["CC6.1"],
        VulnerabilityType.HARDCODED_SECRET: ["CC6.1", "CC6.7"],
        VulnerabilityType.INPUT_VALIDATION: ["CC6.1"],
    }
    
    # Requirement descriptions
    PCI_DSS_REQUIREMENTS = {
        "2.2": "Develop configuration standards for all system components",
        "2.3": "Encrypt all non-console administrative access",
        "3.4": "Render PAN unreadable anywhere it is stored",
        "4.1": "Use strong cryptography and security protocols",
        "6.2": "Ensure all system components are protected from known vulnerabilities",
        "6.5.1": "Injection flaws, particularly SQL injection",
        "6.5.7": "Cross-site scripting (XSS)",
        "6.5.8": "Improper access control",
        "6.5.10": "Broken authentication and session management",
        "7.1": "Limit access to system components and cardholder data",
        "8.2": "Ensure proper user authentication management",
        "8.2.1": "Using strong cryptography, render all authentication credentials unreadable",
        "10.1": "Implement audit trails",
        "10.2": "Implement automated audit trails for all system components",
    }
    
    SOC2_REQUIREMENTS = {
        "CC6.1": "Logical and physical access controls",
        "CC6.2": "Prior to issuing system credentials",
        "CC6.3": "Role-based access control",
        "CC6.7": "Transmission and disclosure of information",
        "CC7.1": "System operations",
        "CC7.2": "System monitoring",
        "CC7.3": "Evaluating security events",
    }
    
    def generate_report(self, scan_result: ScanResult) -> ComplianceReport:
        """Generate compliance report from scan results."""
        report_id = str(uuid.uuid4())
        
        # Get active vulnerabilities
        active_vulns = [v for v in scan_result.vulnerabilities if not v.suppressed]
        
        # Generate requirements for each framework
        pci_requirements = self._generate_framework_requirements(
            ComplianceFramework.PCI_DSS,
            active_vulns,
            self.PCI_DSS_MAPPINGS,
            self.PCI_DSS_REQUIREMENTS
        )
        
        soc2_requirements = self._generate_framework_requirements(
            ComplianceFramework.SOC2,
            active_vulns,
            self.SOC2_MAPPINGS,
            self.SOC2_REQUIREMENTS
        )
        
        all_requirements = pci_requirements + soc2_requirements
        
        # Calculate compliance scores
        compliance_scores = {
            ComplianceFramework.PCI_DSS: self._calculate_compliance_score(pci_requirements),
            ComplianceFramework.SOC2: self._calculate_compliance_score(soc2_requirements),
        }
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            active_vulns, compliance_scores
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(active_vulns, all_requirements)
        
        return ComplianceReport(
            report_id=report_id,
            timestamp=datetime.now(),
            scan_result_id=scan_result.scan_id,
            frameworks=[ComplianceFramework.PCI_DSS, ComplianceFramework.SOC2],
            requirements=all_requirements,
            executive_summary=executive_summary,
            compliance_scores=compliance_scores,
            recommendations=recommendations,
            metadata={
                "total_vulnerabilities": len(active_vulns),
                "critical_count": len([v for v in active_vulns if v.severity == SeverityLevel.CRITICAL]),
                "high_count": len([v for v in active_vulns if v.severity == SeverityLevel.HIGH]),
            }
        )
    
    def _generate_framework_requirements(
        self,
        framework: ComplianceFramework,
        vulnerabilities: List[Any],
        mappings: Dict[VulnerabilityType, List[str]],
        descriptions: Dict[str, str]
    ) -> List[ComplianceRequirement]:
        """Generate requirements for a specific framework."""
        requirements_map = {}
        
        # Group vulnerabilities by requirement
        for vuln in vulnerabilities:
            requirement_ids = mappings.get(vuln.type, [])
            for req_id in requirement_ids:
                if req_id not in requirements_map:
                    requirements_map[req_id] = []
                requirements_map[req_id].append(vuln.id)
        
        # Create requirement objects
        requirements = []
        for req_id, vuln_ids in requirements_map.items():
            status = "not_compliant" if vuln_ids else "compliant"
            
            requirement = ComplianceRequirement(
                framework=framework,
                requirement_id=req_id,
                description=descriptions.get(req_id, f"Requirement {req_id}"),
                vulnerabilities=vuln_ids,
                status=status,
                evidence=[{
                    "vulnerability_count": len(vuln_ids),
                    "requirement": req_id,
                    "framework": framework.value
                }]
            )
            requirements.append(requirement)
        
        # Add compliant requirements
        for req_id, description in descriptions.items():
            if req_id not in requirements_map:
                requirement = ComplianceRequirement(
                    framework=framework,
                    requirement_id=req_id,
                    description=description,
                    vulnerabilities=[],
                    status="compliant",
                    evidence=[{
                        "requirement": req_id,
                        "framework": framework.value,
                        "notes": "No vulnerabilities found for this requirement"
                    }]
                )
                requirements.append(requirement)
        
        return requirements
    
    def _calculate_compliance_score(self, requirements: List[ComplianceRequirement]) -> float:
        """Calculate compliance score as percentage."""
        if not requirements:
            return 100.0
        
        compliant_count = len([r for r in requirements if r.status == "compliant"])
        total_count = len(requirements)
        
        return (compliant_count / total_count) * 100.0
    
    def _generate_executive_summary(
        self,
        vulnerabilities: List[Any],
        compliance_scores: Dict[ComplianceFramework, float]
    ) -> str:
        """Generate executive summary for the report."""
        critical_count = len([v for v in vulnerabilities if v.severity == SeverityLevel.CRITICAL])
        high_count = len([v for v in vulnerabilities if v.severity == SeverityLevel.HIGH])
        
        summary = f"Security scan identified {len(vulnerabilities)} active vulnerabilities:\n"
        summary += f"- Critical: {critical_count}\n"
        summary += f"- High: {high_count}\n\n"
        
        summary += "Compliance Status:\n"
        for framework, score in compliance_scores.items():
            status = "PASS" if score >= 80 else "FAIL"
            summary += f"- {framework.value}: {score:.1f}% ({status})\n"
        
        if critical_count > 0:
            summary += "\nIMMEDIATE ACTION REQUIRED: Critical vulnerabilities detected "
            summary += "that could lead to data breach or system compromise."
        
        return summary
    
    def _generate_recommendations(
        self,
        vulnerabilities: List[Any],
        requirements: List[ComplianceRequirement]
    ) -> List[str]:
        """Generate recommendations based on findings."""
        recommendations = []
        
        # Priority recommendations based on severity
        critical_vulns = [v for v in vulnerabilities if v.severity == SeverityLevel.CRITICAL]
        if critical_vulns:
            recommendations.append(
                f"CRITICAL: Address {len(critical_vulns)} critical vulnerabilities immediately. "
                "These pose immediate risk to system security and compliance."
            )
        
        # Crypto recommendations
        crypto_vulns = [v for v in vulnerabilities if v.type == VulnerabilityType.CRYPTO_FAILURE]
        if crypto_vulns:
            recommendations.append(
                "Upgrade cryptographic implementations to use strong algorithms "
                "(AES-256, SHA-256 or better) and proper key management."
            )
        
        # Input validation recommendations
        input_vulns = [v for v in vulnerabilities if v.type in [
            VulnerabilityType.INJECTION,
            VulnerabilityType.XSS,
            VulnerabilityType.INPUT_VALIDATION
        ]]
        if input_vulns:
            recommendations.append(
                "Implement comprehensive input validation and sanitization "
                "for all user inputs. Use parameterized queries and output encoding."
            )
        
        # Secret management recommendations
        secret_vulns = [v for v in vulnerabilities if v.type == VulnerabilityType.HARDCODED_SECRET]
        if secret_vulns:
            recommendations.append(
                "Remove all hardcoded secrets and implement proper secret management "
                "using environment variables or dedicated secret management systems."
            )
        
        # Compliance-specific recommendations
        non_compliant = [r for r in requirements if r.status != "compliant"]
        if non_compliant:
            frameworks = list(set(r.framework.value for r in non_compliant))
            recommendations.append(
                f"Review and remediate all findings to achieve compliance with: {', '.join(frameworks)}"
            )
        
        # General recommendations
        recommendations.extend([
            "Implement automated security scanning in CI/CD pipeline",
            "Conduct regular security training for development team",
            "Establish a vulnerability management process with defined SLAs",
            "Perform periodic manual security assessments",
        ])
        
        return recommendations
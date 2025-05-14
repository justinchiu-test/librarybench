"""
Medical-specific validation rules for the CLI Form Library.
"""
import re
import typing as t


def validate_patient_id(patient_id: str) -> t.Tuple[bool, t.Optional[str]]:
    """
    Validate a patient ID.
    
    Args:
        patient_id: Patient ID to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not patient_id:
        return False, "Patient ID is required"
        
    if not re.match(r'^[A-Z0-9]{5,10}$', patient_id):
        return False, "Patient ID must be 5-10 uppercase letters or numbers"
        
    return True, None
    
    
def validate_medical_record_number(mrn: str) -> t.Tuple[bool, t.Optional[str]]:
    """
    Validate a medical record number.
    
    Args:
        mrn: Medical record number to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not mrn:
        return False, "Medical record number is required"
        
    if not re.match(r'^MRN-\d{8}$', mrn):
        return False, "Medical record number must be in format MRN-NNNNNNNN"
        
    return True, None
    
    
def validate_diagnosis_code(code: str) -> t.Tuple[bool, t.Optional[str]]:
    """
    Validate an ICD-10 diagnosis code.
    
    Args:
        code: Diagnosis code to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not code:
        return True, None  # Optional field
        
    if not re.match(r'^[A-Z]\d{2}(\.\d{1,2})?$', code):
        return False, "Invalid ICD-10 diagnosis code format"
        
    return True, None
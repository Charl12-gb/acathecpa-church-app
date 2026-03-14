from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

# Base Pydantic model for common attributes
class CertificateBase(BaseModel):
    course_id: int
    user_id: int
    issue_date: datetime
    certificate_url: Optional[str] = None # URL to a PDF or a verification page
    verification_code: Optional[str] = None # Unique code for verification

# Schema for creating a certificate (input)
class CertificateCreate(CertificateBase):
    pass

# Schema for updating a certificate (input) - if needed
class CertificateUpdate(BaseModel):
    certificate_url: Optional[str] = None
    verification_code: Optional[str] = None

# Schema for displaying a certificate (output)
class Certificate(CertificateBase):
    id: int

    # Pydantic V2Orm_mode / from_attributes
    model_config = ConfigDict(from_attributes=True)

# Schema for display within User or Course schemas (lighter version)
class CertificateDisplay(BaseModel):
    id: int
    course_id: int
    # course_title: str # Consider adding if frequently needed and easily joined
    issue_date: datetime
    certificate_url: Optional[str] = None
    verification_code: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

from pydantic import BaseModel
from typing import List, Optional


class MedicalReport(BaseModel):

    patient_name: Optional[str]

    hemoglobin: Optional[float]

    wbc: Optional[float]

    rbc: Optional[float]

    platelets: Optional[float]

    abnormal_findings: List[str]

    summary: str

    validation_findings: List[str]
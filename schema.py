from pydantic import BaseModel
from typing import Literal, Optional

class JobInfo(BaseModel):
    skills: list[str]
    seniority: Literal["intern", "junior", "mid", "senior", "lead", "unknown"]
    work_mode: Literal["remote", "hybrid", "onsite", "unknown"]
    salary_min: Optional[float]
    salary_max: Optional[float]
    salary_currency: Optional[str]
    salary_period: Optional[Literal["hour", "month", "year"]]
    years_experience: Optional[float]
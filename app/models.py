from pydantic import BaseModel
from typing import Optional


class ClientCreate(BaseModel):
    name: str
    goal: Optional[str] = None
    start_weight: Optional[float] = None
    date_of_birth: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    notes: Optional[str] = None


class EntryCreate(BaseModel):
    week_number: int
    date: Optional[str] = None
    phase: Optional[str] = None
    calories: Optional[int] = None
    cardio: Optional[str] = None
    steps: Optional[int] = None
    training_specifics: Optional[str] = None
    goals_expectations: Optional[str] = None
    notes: Optional[str] = None


PHASES = [
    "Dieting Phase",
    "Diet Break",
    "Maintenance",
    "Reverse Diet",
    "Bulk",
    "Competition Prep",
    "Peak Week",
    "Off Season",
]

PHASE_COLOURS = {
    "Dieting Phase":    "#E8730C",
    "Diet Break":       "#F5A623",
    "Maintenance":      "#4A6FA5",
    "Reverse Diet":     "#2A9D8F",
    "Bulk":             "#2D6A4F",
    "Competition Prep": "#C1121F",
    "Peak Week":        "#7B2D8B",
    "Off Season":       "#6C757D",
}

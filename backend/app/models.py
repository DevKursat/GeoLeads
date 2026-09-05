"""
Data models and Enums for GeoLeads.
"""
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime


class CRMStage(str, Enum):
    NEW = "NEW"                  # Newly discovered lead
    ENRICHED = "ENRICHED"        # Audited, contacts and gaps identified
    CONTACTED = "CONTACTED"      # Email or WhatsApp outreach sent
    IN_DISCUSSION = "IN_DISCUSSION" # Active conversation / sales meeting
    WON = "WON"                  # Client signed / Closed deal
    LOST = "LOST"                # Rejected / Not interested


class OpportunitySeverity(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class SalesGap:
    code: str                     # e.g., 'MISSING_WEBSITE', 'LOW_RATING', 'NO_SSL', 'NO_SOCIAL', 'NO_WHATSAPP'
    title: str                    # Human-friendly title
    description: str              # Impact explanation
    severity: OpportunitySeverity
    pitch_angle: str              # Recommended sales hook
    suggested_solution: str       # What service to sell

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "pitch_angle": self.pitch_angle,
            "suggested_solution": self.suggested_solution
        }


@dataclass
class Lead:
    id: Optional[int] = None
    place_id: str = ""
    name: str = ""
    category: str = ""
    city: str = ""
    address: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: str = ""
    website: str = ""
    rating: Optional[float] = None
    review_count: int = 0
    google_maps_url: str = ""

    # Contact Enrichment
    emails: List[str] = field(default_factory=list)
    phones: List[str] = field(default_factory=list)
    whatsapp: str = ""
    instagram: str = ""
    facebook: str = ""
    linkedin: str = ""
    twitter: str = ""
    youtube: str = ""

    # Technical & SEO Audit
    has_website: bool = False
    has_ssl: bool = False
    meta_title: str = ""
    meta_description: str = ""

    # Sales Opportunity
    opportunity_score: int = 0  # 0 to 100
    gaps: List[SalesGap] = field(default_factory=list)
    primary_gap: str = ""

    # CRM Pipeline
    crm_stage: CRMStage = CRMStage.NEW
    notes: str = ""
    last_contacted_at: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["crm_stage"] = self.crm_stage.value if isinstance(self.crm_stage, CRMStage) else self.crm_stage
        d["gaps"] = [g.to_dict() if isinstance(g, SalesGap) else g for g in self.gaps]
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Lead":
        gaps_data = data.get("gaps", [])
        gaps: List[SalesGap] = []
        for g in gaps_data:
            if isinstance(g, dict):
                gaps.append(SalesGap(
                    code=g.get("code", ""),
                    title=g.get("title", ""),
                    description=g.get("description", ""),
                    severity=OpportunitySeverity(g.get("severity", "MEDIUM")),
                    pitch_angle=g.get("pitch_angle", ""),
                    suggested_solution=g.get("suggested_solution", "")
                ))
            elif isinstance(g, SalesGap):
                gaps.append(g)

        stage_str = data.get("crm_stage", CRMStage.NEW.value)
        try:
            stage = CRMStage(stage_str)
        except ValueError:
            stage = CRMStage.NEW

        return cls(
            id=data.get("id"),
            place_id=data.get("place_id", ""),
            name=data.get("name", ""),
            category=data.get("category", ""),
            city=data.get("city", ""),
            address=data.get("address", ""),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            phone=data.get("phone", ""),
            website=data.get("website", ""),
            rating=data.get("rating"),
            review_count=data.get("review_count", 0),
            google_maps_url=data.get("google_maps_url", ""),
            emails=data.get("emails", []) or [],
            phones=data.get("phones", []) or [],
            whatsapp=data.get("whatsapp", ""),
            instagram=data.get("instagram", ""),
            facebook=data.get("facebook", ""),
            linkedin=data.get("linkedin", ""),
            twitter=data.get("twitter", ""),
            youtube=data.get("youtube", ""),
            has_website=bool(data.get("has_website", False)),
            has_ssl=bool(data.get("has_ssl", False)),
            meta_title=data.get("meta_title", ""),
            meta_description=data.get("meta_description", ""),
            opportunity_score=data.get("opportunity_score", 0),
            gaps=gaps,
            primary_gap=data.get("primary_gap", ""),
            crm_stage=stage,
            notes=data.get("notes", ""),
            last_contacted_at=data.get("last_contacted_at"),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            updated_at=data.get("updated_at", datetime.utcnow().isoformat())
        )

from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

class ContactInfo(BaseModel):
    email: Optional[str] = None
    github: Optional[str] = None
    linkedin: Optional[str] = None
    telegram: Optional[str] = None

class ProfileInfo(BaseModel):
    name: str
    title: str
    bio: str
    contacts: ContactInfo

class AchievementMetric(BaseModel):
    metric_type: str
    before: Optional[str] = None
    after: Optional[str] = None
    unit: str
    improvement_percent: Optional[float] = None

class Achievement(BaseModel):
    id: Optional[str] = None
    description: str
    metrics: List[AchievementMetric] = Field(default_factory=list)

class ArchitectureInfo(BaseModel):
    pattern: Optional[str] = None
    diagram_mermaid: Optional[str] = None

class ContentItem(BaseModel):
    """
    Универсальная единица контента единой ленты (Case study, Architecture Decision, Article/Dictated Note)
    """
    id: str
    type: Literal["case", "decision", "article"]
    title: str
    summary: str
    content: str
    tags: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    role: Optional[str] = None
    date: Optional[str] = None
    repository_url: Optional[str] = None
    diagram_path: Optional[str] = None
    architecture: Optional[ArchitectureInfo] = None
    achievements: List[Achievement] = Field(default_factory=list)
    media: List[str] = Field(default_factory=list)

class PortfolioMeta(BaseModel):
    title: str
    description: str
    theme: Literal["dark", "light", "glassmorphism"] = "dark"

class SkillCategory(BaseModel):
    category: str
    items: List[str] = Field(default_factory=list)

class PortfolioFeed(BaseModel):
    meta: PortfolioMeta
    profile: ProfileInfo
    skills: List[SkillCategory] = Field(default_factory=list)
    items: List[ContentItem] = Field(default_factory=list)

class ReviewIssue(BaseModel):
    severity: Literal["low", "medium", "high", "critical"]
    field: str
    issue_type: Literal["hallucination", "schema_mismatch", "missing_fact", "style"]
    description: str
    suggestion: str

class ReviewReport(BaseModel):
    is_approved: bool
    score: float = Field(ge=0.0, le=1.0)
    issues: List[ReviewIssue] = Field(default_factory=list)
    summary: str

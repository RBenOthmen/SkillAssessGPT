"""
Data models for SkillAssessGPT system.

This module contains all dataclasses representing the core data structures
used throughout the assessment generation pipeline.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Any, Optional
from datetime import datetime


@dataclass
class CompetencyInput:
    competency: str
    element: str = ""
    niveau: str = ""
    parcours: str = ""
    specialite: str = ""
    duree: str = ""
    
    def __post_init__(self):
        """Validate that required fields are not empty."""
        if not self.competency or not self.competency.strip():
            raise ValueError("Competency field cannot be empty")
        if not self.niveau or not self.niveau.strip():
            raise ValueError("Niveau field cannot be empty")
        if not self.parcours or not self.parcours.strip():
            raise ValueError("Parcours field cannot be empty")
        if not self.specialite or not self.specialite.strip():
            raise ValueError("Specialite field cannot be empty")
        if not self.duree or not self.duree.strip():
            raise ValueError("Duree field cannot be empty")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "competency": self.competency,
            "element": self.element,
            "niveau": self.niveau,
            "parcours": self.parcours,
            "specialite": self.specialite,
            "duree": self.duree
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompetencyInput':
        """Create instance from dictionary."""
        return cls(
            competency=data.get("competency", ""),
            element=data.get("element", ""),
            niveau=data.get("niveau", ""),
            parcours=data.get("parcours", ""),
            specialite=data.get("specialite", ""),
            duree=data.get("duree", "")
        )


@dataclass
class Criterion:
    description: str
    indicators: List[str] = field(default_factory=list)
    points: int = 0
    
    def __post_init__(self):
        """Validate criterion data."""
        if not self.description or not self.description.strip():
            raise ValueError("Criterion description cannot be empty")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "description": self.description,
            "indicators": self.indicators,
            "points": self.points
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Criterion':
        """Create instance from dictionary."""
        return cls(
            description=data.get("description", ""),
            indicators=data.get("indicators", []),
            points=data.get("points", 0)
        )


@dataclass
class APCGrid:
    nd_criteria: List[Criterion] = field(default_factory=list)
    ni_criteria: List[Criterion] = field(default_factory=list)
    na_criteria: List[Criterion] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate that each level has at least 3 criteria."""
        if len(self.nd_criteria) < 3:
            raise ValueError("ND level must have at least 3 criteria")
        if len(self.ni_criteria) < 3:
            raise ValueError("NI level must have at least 3 criteria")
        if len(self.na_criteria) < 3:
            raise ValueError("NA level must have at least 3 criteria")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "nd_criteria": [c.to_dict() for c in self.nd_criteria],
            "ni_criteria": [c.to_dict() for c in self.ni_criteria],
            "na_criteria": [c.to_dict() for c in self.na_criteria]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'APCGrid':
        """Create instance from dictionary."""
        return cls(
            nd_criteria=[Criterion.from_dict(c) for c in data.get("nd_criteria", [])],
            ni_criteria=[Criterion.from_dict(c) for c in data.get("ni_criteria", [])],
            na_criteria=[Criterion.from_dict(c) for c in data.get("na_criteria", [])]
        )


@dataclass
class EvaluationSituation:
    context: str = ""
    task: str = ""
    instructions: str = ""
    duration: str = ""
    
    def __post_init__(self):
        """Validate that required fields are not empty."""
        if not self.instructions or not self.instructions.strip():
            raise ValueError("Instructions field cannot be empty")
        if not self.duration or not self.duration.strip():
            raise ValueError("Duration field cannot be empty")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "context": self.context,
            "task": self.task,
            "instructions": self.instructions,
            "duration": self.duration
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EvaluationSituation':
        """Create instance from dictionary."""
        return cls(
            context=data.get("context", ""),
            task=data.get("task", ""),
            instructions=data.get("instructions", ""),
            duration=data.get("duration", "")
        )


@dataclass
class ScoringRubric:
    total_points: int = 0
    nd_range: Tuple[int, int] = (0, 0)
    ni_range: Tuple[int, int] = (0, 0)
    na_range: Tuple[int, int] = (0, 0)
    criteria_points: Dict[str, int] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate scoring rubric."""
        if self.total_points not in [20, 100]:
            raise ValueError("Total points must be either 20 or 100")
        
        # Validate that all criteria have points > 0
        for criterion, points in self.criteria_points.items():
            if points <= 0:
                raise ValueError(f"Criterion '{criterion}' must have points > 0")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "total_points": self.total_points,
            "nd_range": list(self.nd_range),
            "ni_range": list(self.ni_range),
            "na_range": list(self.na_range),
            "criteria_points": self.criteria_points
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScoringRubric':
        """Create instance from dictionary."""
        return cls(
            total_points=data.get("total_points", 0),
            nd_range=tuple(data.get("nd_range", [0, 0])),
            ni_range=tuple(data.get("ni_range", [0, 0])),
            na_range=tuple(data.get("na_range", [0, 0])),
            criteria_points=data.get("criteria_points", {})
        )


@dataclass
class AssessmentOutput:
    input: CompetencyInput
    grid: APCGrid
    situation: EvaluationSituation
    rubric: ScoringRubric
    generated_at: str = ""
    
    def __post_init__(self):
        """Set generation timestamp if not provided."""
        if not self.generated_at:
            self.generated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "input": self.input.to_dict(),
            "grid": self.grid.to_dict(),
            "situation": self.situation.to_dict(),
            "rubric": self.rubric.to_dict(),
            "generated_at": self.generated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AssessmentOutput':
        """Create instance from dictionary."""
        return cls(
            input=CompetencyInput.from_dict(data.get("input", {})),
            grid=APCGrid.from_dict(data.get("grid", {})),
            situation=EvaluationSituation.from_dict(data.get("situation", {})),
            rubric=ScoringRubric.from_dict(data.get("rubric", {})),
            generated_at=data.get("generated_at", "")
        )


@dataclass
class ValidationResult:
    is_valid: bool = False
    alignment_score: str = ""
    observability_issues: List[str] = field(default_factory=list)
    coherence_issues: List[str] = field(default_factory=list)
    feedback: str = ""
    validated_at: str = ""
    
    def __post_init__(self):
        """Set validation timestamp and validate feedback for failures."""
        if not self.validated_at:
            self.validated_at = datetime.now().isoformat()
        
        # If validation failed, feedback must be provided
        if not self.is_valid and (not self.feedback or not self.feedback.strip()):
            raise ValueError("Feedback must be provided when validation fails")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "is_valid": self.is_valid,
            "alignment_score": self.alignment_score,
            "observability_issues": self.observability_issues,
            "coherence_issues": self.coherence_issues,
            "feedback": self.feedback,
            "validated_at": self.validated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ValidationResult':
        """Create instance from dictionary."""
        return cls(
            is_valid=data.get("is_valid", False),
            alignment_score=data.get("alignment_score", ""),
            observability_issues=data.get("observability_issues", []),
            coherence_issues=data.get("coherence_issues", []),
            feedback=data.get("feedback", ""),
            validated_at=data.get("validated_at", "")
        )

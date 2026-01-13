"""
Student Profile Model - Based on AGORA Variables
INPUT: Diagnostico y perfil del estudiante
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from enum import Enum
import numpy as np
import json


class EducationStage(Enum):
    ESO = "ESO"  # Educacion Secundaria Obligatoria
    BACHILLERATO = "Bachillerato"
    FP_BASICA = "FP Basica"
    FP_MEDIO = "FP Grado Medio"


class Gender(Enum):
    FEMALE = "Mujer"
    MALE = "Hombre"
    NON_BINARY = "No binario"
    OTHER = "Otro"


class LearningStyle(Enum):
    # Felder-Silverman dimensions
    ACTIVE = "Activo"
    REFLECTIVE = "Reflexivo"
    SENSORY = "Sensorial"
    INTUITIVE = "Intuitivo"
    VISUAL = "Visual"
    VERBAL = "Verbal"
    SEQUENTIAL = "Secuencial"
    GLOBAL = "Global"


class KolbStyle(Enum):
    DIVERGENT = "Divergente"
    ASSIMILATOR = "Asimilador"
    CONVERGENT = "Convergente"
    ACCOMMODATOR = "Acomodador"


@dataclass
class DemographicVariables:
    """V1-V4: Variables demograficas"""
    age: int  # V1
    education_stage: EducationStage  # V2
    gender: Gender  # V3
    digital_competence_score: float  # V4 (0-100, based on DigComp 2.2)


@dataclass
class EmotionalFactors:
    """V5-V6: Factores emocionales"""
    intrinsic_motivation: float  # V5 (0-100)
    self_efficacy: float  # V6 (0-100)


@dataclass
class CognitiveFactors:
    """V7-V12: Factores cognitivos"""
    learning_preferences: Dict[str, str]  # V7 (Felder-Silverman profile)
    kolb_style: KolbStyle  # V8
    prior_knowledge: Dict[str, float]  # V9 (per skill area, 0-100)
    conceptual_mastery: float  # V10 (0-100)
    reasoning_logic: float  # V11 (0-100)
    metacognitive_accuracy: float  # V12 (discrepancy index)


@dataclass
class StudentProfile:
    """Complete student profile based on AGORA INPUT variables"""
    id: str
    name: str
    demographics: DemographicVariables
    emotional: EmotionalFactors
    cognitive: CognitiveFactors

    # Current state in learning path
    current_node_id: Optional[str] = None
    completed_nodes: List[str] = field(default_factory=list)

    # Performance metrics
    performance_history: List[Dict] = field(default_factory=list)

    def to_vector(self) -> np.ndarray:
        """Convert profile to numerical vector for RL agent"""
        vector = [
            self.demographics.age / 25.0,  # Normalized
            list(EducationStage).index(self.demographics.education_stage) / 4.0,
            self.demographics.digital_competence_score / 100.0,
            self.emotional.intrinsic_motivation / 100.0,
            self.emotional.self_efficacy / 100.0,
            self.cognitive.conceptual_mastery / 100.0,
            self.cognitive.reasoning_logic / 100.0,
            self.cognitive.metacognitive_accuracy,
            list(KolbStyle).index(self.cognitive.kolb_style) / 4.0,
        ]
        # Add prior knowledge scores for each skill
        for skill in ['literacy', 'numeracy', 'digital', 'citizenship']:
            vector.append(self.cognitive.prior_knowledge.get(skill, 0.5))

        return np.array(vector, dtype=np.float32)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'demographics': {
                'age': self.demographics.age,
                'education_stage': self.demographics.education_stage.value,
                'gender': self.demographics.gender.value,
                'digital_competence_score': self.demographics.digital_competence_score
            },
            'emotional': {
                'intrinsic_motivation': self.emotional.intrinsic_motivation,
                'self_efficacy': self.emotional.self_efficacy
            },
            'cognitive': {
                'learning_preferences': self.cognitive.learning_preferences,
                'kolb_style': self.cognitive.kolb_style.value,
                'prior_knowledge': self.cognitive.prior_knowledge,
                'conceptual_mastery': self.cognitive.conceptual_mastery,
                'reasoning_logic': self.cognitive.reasoning_logic,
                'metacognitive_accuracy': self.cognitive.metacognitive_accuracy
            },
            'current_node_id': self.current_node_id,
            'completed_nodes': self.completed_nodes,
            'performance_history': self.performance_history
        }


class StudentFactory:
    """Factory to create student profiles, including virtual clones for simulation"""

    @staticmethod
    def create_virtual_clone(base_profile: StudentProfile, variation: float = 0.1) -> StudentProfile:
        """Create a virtual clone with slight variations for RL simulation"""
        import uuid

        def vary(value: float, max_val: float = 100.0) -> float:
            """Add random variation to a value"""
            delta = np.random.normal(0, variation * max_val)
            return max(0, min(max_val, value + delta))

        clone_id = f"clone_{base_profile.id}_{uuid.uuid4().hex[:8]}"

        # Create varied demographics
        demographics = DemographicVariables(
            age=base_profile.demographics.age,
            education_stage=base_profile.demographics.education_stage,
            gender=base_profile.demographics.gender,
            digital_competence_score=vary(base_profile.demographics.digital_competence_score)
        )

        # Create varied emotional factors
        emotional = EmotionalFactors(
            intrinsic_motivation=vary(base_profile.emotional.intrinsic_motivation),
            self_efficacy=vary(base_profile.emotional.self_efficacy)
        )

        # Create varied cognitive factors
        prior_knowledge = {
            skill: vary(score)
            for skill, score in base_profile.cognitive.prior_knowledge.items()
        }

        cognitive = CognitiveFactors(
            learning_preferences=base_profile.cognitive.learning_preferences.copy(),
            kolb_style=base_profile.cognitive.kolb_style,
            prior_knowledge=prior_knowledge,
            conceptual_mastery=vary(base_profile.cognitive.conceptual_mastery),
            reasoning_logic=vary(base_profile.cognitive.reasoning_logic),
            metacognitive_accuracy=vary(base_profile.cognitive.metacognitive_accuracy, 1.0)
        )

        return StudentProfile(
            id=clone_id,
            name=f"Clone of {base_profile.name}",
            demographics=demographics,
            emotional=emotional,
            cognitive=cognitive
        )

    @staticmethod
    def create_sample_profile(profile_type: str = "average") -> StudentProfile:
        """Create sample profiles for testing"""
        import uuid

        profiles = {
            "high_performer": {
                "demographics": DemographicVariables(16, EducationStage.ESO, Gender.FEMALE, 85.0),
                "emotional": EmotionalFactors(90.0, 85.0),
                "cognitive": CognitiveFactors(
                    {"processing": "Reflexivo", "perception": "Intuitivo",
                     "input": "Visual", "comprehension": "Global"},
                    KolbStyle.ASSIMILATOR,
                    {"literacy": 80.0, "numeracy": 85.0, "digital": 90.0, "citizenship": 75.0},
                    85.0, 88.0, 0.1
                )
            },
            "struggling": {
                "demographics": DemographicVariables(15, EducationStage.ESO, Gender.MALE, 45.0),
                "emotional": EmotionalFactors(40.0, 35.0),
                "cognitive": CognitiveFactors(
                    {"processing": "Activo", "perception": "Sensorial",
                     "input": "Visual", "comprehension": "Secuencial"},
                    KolbStyle.ACCOMMODATOR,
                    {"literacy": 35.0, "numeracy": 30.0, "digital": 50.0, "citizenship": 40.0},
                    40.0, 35.0, 0.4
                )
            },
            "average": {
                "demographics": DemographicVariables(16, EducationStage.BACHILLERATO, Gender.NON_BINARY, 65.0),
                "emotional": EmotionalFactors(60.0, 55.0),
                "cognitive": CognitiveFactors(
                    {"processing": "Activo", "perception": "Sensorial",
                     "input": "Verbal", "comprehension": "Secuencial"},
                    KolbStyle.CONVERGENT,
                    {"literacy": 55.0, "numeracy": 50.0, "digital": 70.0, "citizenship": 60.0},
                    58.0, 55.0, 0.25
                )
            }
        }

        config = profiles.get(profile_type, profiles["average"])

        return StudentProfile(
            id=uuid.uuid4().hex[:12],
            name=f"Sample Student ({profile_type})",
            demographics=config["demographics"],
            emotional=config["emotional"],
            cognitive=config["cognitive"]
        )

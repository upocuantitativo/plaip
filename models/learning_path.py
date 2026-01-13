"""
Learning Path Model - Personalized Learning Pathways (PLPs)
Defines the structure of learning itineraries for Basic Skills
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid
import json


class BasicSkill(Enum):
    """Basic Skills according to EU definition"""
    LITERACY = "literacy"
    NUMERACY = "numeracy"
    DIGITAL = "digital"
    CITIZENSHIP = "citizenship"


class HighImpactStrategy(Enum):
    """V13: Estrategias de Alto Impacto (EAI)"""
    FEEDBACK = "Retroalimentacion de alto impacto"
    FORMATIVE_ASSESSMENT = "Evaluacion formativa"
    GOAL_CLARITY = "Claridad de metas y criterios"
    SELF_REGULATION = "Autorregulacion del aprendizaje"
    PRIOR_KNOWLEDGE = "Identificacion del conocimiento previo"
    DISTRIBUTED_PRACTICE = "Practica distribuida"
    RETRIEVAL_PRACTICE = "Practica de recuperacion"
    SCAFFOLDING = "Andamiaje"
    DIRECT_INSTRUCTION = "Ensenanza directa"
    PROBLEM_BASED = "Aprendizaje basado en problemas"
    SELF_EFFICACY = "Fomento de autoeficacia"
    INTRINSIC_MOTIVATION = "Motivacion intrinseca"


class TeachingMethodology(Enum):
    """V14: Metodologias de ensenanza"""
    PROJECT_BASED = "Aprendizaje Basado en Proyectos"
    PROBLEM_BASED = "Aprendizaje Basado en Problemas"
    INQUIRY_BASED = "Aprendizaje basado en indagacion"
    GAMIFICATION = "Gamificacion"
    ADAPTIVE_TUTORIAL = "Tutorial adaptativo"


class NodeDifficulty(Enum):
    BEGINNER = 1
    ELEMENTARY = 2
    INTERMEDIATE = 3
    ADVANCED = 4


@dataclass
class PerformanceIndicators:
    """Performance metrics for a learning node"""
    completion_rate: float = 0.0  # 0-100%
    average_score: float = 0.0  # 0-100
    time_spent_minutes: float = 0.0
    attempts: int = 0
    retention_rate: float = 0.0  # V19: Long-term retention
    error_patterns: List[str] = field(default_factory=list)  # V18

    def to_dict(self) -> Dict:
        return {
            'completion_rate': self.completion_rate,
            'average_score': self.average_score,
            'time_spent_minutes': self.time_spent_minutes,
            'attempts': self.attempts,
            'retention_rate': self.retention_rate,
            'error_patterns': self.error_patterns
        }


@dataclass
class LearningNode:
    """A single node in the learning path tree"""
    id: str
    title: str
    description: str
    skill: BasicSkill
    difficulty: NodeDifficulty

    # Content and pedagogy
    learning_objectives: List[str] = field(default_factory=list)
    recommended_strategies: List[HighImpactStrategy] = field(default_factory=list)
    methodology: TeachingMethodology = TeachingMethodology.ADAPTIVE_TUTORIAL

    # Prerequisites and connections
    prerequisites: List[str] = field(default_factory=list)  # Node IDs
    next_nodes: List[str] = field(default_factory=list)  # Possible next nodes

    # Estimated duration in minutes
    estimated_duration: int = 30

    # Aggregated performance from all students
    performance: PerformanceIndicators = field(default_factory=PerformanceIndicators)

    # Student-specific performance (student_id -> indicators)
    student_performance: Dict[str, PerformanceIndicators] = field(default_factory=dict)

    def get_reward_value(self, student_id: str) -> float:
        """Calculate reward value for RL based on student performance"""
        if student_id in self.student_performance:
            perf = self.student_performance[student_id]
            # Weighted combination of metrics
            reward = (
                0.4 * (perf.average_score / 100.0) +
                0.3 * (perf.completion_rate / 100.0) +
                0.2 * (perf.retention_rate / 100.0) +
                0.1 * max(0, 1 - perf.time_spent_minutes / (self.estimated_duration * 2))
            )
            return reward
        return 0.0

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'skill': self.skill.value,
            'difficulty': self.difficulty.value,
            'learning_objectives': self.learning_objectives,
            'recommended_strategies': [s.value for s in self.recommended_strategies],
            'methodology': self.methodology.value,
            'prerequisites': self.prerequisites,
            'next_nodes': self.next_nodes,
            'estimated_duration': self.estimated_duration,
            'performance': self.performance.to_dict()
        }


@dataclass
class LearningPath:
    """Complete learning path structure (tree of nodes)"""
    id: str
    name: str
    description: str
    target_skills: List[BasicSkill]

    # All nodes in this path
    nodes: Dict[str, LearningNode] = field(default_factory=dict)

    # Root nodes (entry points)
    root_nodes: List[str] = field(default_factory=list)

    # Metadata
    created_at: str = ""
    updated_at: str = ""
    version: str = "1.0"

    def add_node(self, node: LearningNode) -> None:
        """Add a node to the path"""
        self.nodes[node.id] = node

    def get_node(self, node_id: str) -> Optional[LearningNode]:
        """Get a node by ID"""
        return self.nodes.get(node_id)

    def get_available_next_nodes(self, current_node_id: str,
                                  completed_nodes: List[str]) -> List[LearningNode]:
        """Get available next nodes based on completed prerequisites"""
        current = self.nodes.get(current_node_id)
        if not current:
            return [self.nodes[nid] for nid in self.root_nodes]

        available = []
        for next_id in current.next_nodes:
            next_node = self.nodes.get(next_id)
            if next_node and all(prereq in completed_nodes for prereq in next_node.prerequisites):
                available.append(next_node)

        return available

    def to_tree_structure(self) -> Dict:
        """Convert to tree structure for D3.js visualization"""
        def build_subtree(node_id: str, visited: set) -> Dict:
            if node_id in visited:
                return None
            visited.add(node_id)

            node = self.nodes.get(node_id)
            if not node:
                return None

            children = []
            for next_id in node.next_nodes:
                child = build_subtree(next_id, visited.copy())
                if child:
                    children.append(child)

            return {
                'id': node.id,
                'name': node.title,
                'skill': node.skill.value,
                'difficulty': node.difficulty.value,
                'performance': node.performance.to_dict(),
                'children': children if children else None
            }

        # Build from root nodes
        roots = []
        for root_id in self.root_nodes:
            tree = build_subtree(root_id, set())
            if tree:
                roots.append(tree)

        return {
            'name': self.name,
            'children': roots
        }

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'target_skills': [s.value for s in self.target_skills],
            'nodes': {nid: n.to_dict() for nid, n in self.nodes.items()},
            'root_nodes': self.root_nodes,
            'version': self.version
        }


class LearningPathBuilder:
    """Builder for creating sample learning paths"""

    @staticmethod
    def create_basic_skills_path() -> LearningPath:
        """Create a comprehensive basic skills learning path"""
        path = LearningPath(
            id=uuid.uuid4().hex[:12],
            name="Itinerario de Competencias Basicas",
            description="Itinerario personalizado para el desarrollo de basic skills: "
                       "digital skills y citizenship skills como eje central, "
                       "apoyadas por literacy y numeracy.",
            target_skills=[BasicSkill.DIGITAL, BasicSkill.CITIZENSHIP,
                          BasicSkill.LITERACY, BasicSkill.NUMERACY]
        )

        # FOUNDATIONAL SKILLS - Literacy
        lit_1 = LearningNode(
            id="lit_1", title="Comprension Lectora Basica",
            description="Desarrollo de habilidades de lectura comprensiva",
            skill=BasicSkill.LITERACY, difficulty=NodeDifficulty.BEGINNER,
            learning_objectives=["Identificar ideas principales", "Reconocer estructura textual"],
            recommended_strategies=[HighImpactStrategy.DIRECT_INSTRUCTION,
                                   HighImpactStrategy.FORMATIVE_ASSESSMENT],
            next_nodes=["lit_2", "dig_1"]
        )

        lit_2 = LearningNode(
            id="lit_2", title="Analisis Critico de Textos",
            description="Evaluacion y analisis critico de diferentes tipos de textos",
            skill=BasicSkill.LITERACY, difficulty=NodeDifficulty.INTERMEDIATE,
            learning_objectives=["Evaluar argumentos", "Detectar sesgos"],
            recommended_strategies=[HighImpactStrategy.PROBLEM_BASED,
                                   HighImpactStrategy.RETRIEVAL_PRACTICE],
            prerequisites=["lit_1"],
            next_nodes=["cit_1", "dig_2"]
        )

        # FOUNDATIONAL SKILLS - Numeracy
        num_1 = LearningNode(
            id="num_1", title="Razonamiento Numerico Basico",
            description="Fundamentos de calculo y razonamiento matematico",
            skill=BasicSkill.NUMERACY, difficulty=NodeDifficulty.BEGINNER,
            learning_objectives=["Operaciones basicas", "Resolucion de problemas simples"],
            recommended_strategies=[HighImpactStrategy.SCAFFOLDING,
                                   HighImpactStrategy.DISTRIBUTED_PRACTICE],
            next_nodes=["num_2", "dig_1"]
        )

        num_2 = LearningNode(
            id="num_2", title="Interpretacion de Datos",
            description="Lectura e interpretacion de graficos y estadisticas",
            skill=BasicSkill.NUMERACY, difficulty=NodeDifficulty.INTERMEDIATE,
            learning_objectives=["Leer graficos", "Calcular estadisticos basicos"],
            recommended_strategies=[HighImpactStrategy.PROBLEM_BASED,
                                   HighImpactStrategy.FEEDBACK],
            prerequisites=["num_1"],
            next_nodes=["dig_2", "cit_2"]
        )

        # CENTRAL AXIS - Digital Skills
        dig_1 = LearningNode(
            id="dig_1", title="Alfabetizacion Digital",
            description="Uso basico de herramientas digitales y navegacion segura",
            skill=BasicSkill.DIGITAL, difficulty=NodeDifficulty.BEGINNER,
            learning_objectives=["Navegar internet seguro", "Usar herramientas basicas"],
            recommended_strategies=[HighImpactStrategy.DIRECT_INSTRUCTION,
                                   HighImpactStrategy.SELF_EFFICACY],
            methodology=TeachingMethodology.ADAPTIVE_TUTORIAL,
            next_nodes=["dig_2", "cit_1"]
        )

        dig_2 = LearningNode(
            id="dig_2", title="Comunicacion y Colaboracion Digital",
            description="Herramientas de comunicacion y trabajo colaborativo online",
            skill=BasicSkill.DIGITAL, difficulty=NodeDifficulty.INTERMEDIATE,
            learning_objectives=["Comunicacion efectiva online", "Colaboracion en equipos virtuales"],
            recommended_strategies=[HighImpactStrategy.PROBLEM_BASED,
                                   HighImpactStrategy.INTRINSIC_MOTIVATION],
            methodology=TeachingMethodology.PROJECT_BASED,
            prerequisites=["dig_1"],
            next_nodes=["dig_3", "cit_2"]
        )

        dig_3 = LearningNode(
            id="dig_3", title="Creacion de Contenido Digital",
            description="Produccion de contenido digital de calidad",
            skill=BasicSkill.DIGITAL, difficulty=NodeDifficulty.ADVANCED,
            learning_objectives=["Crear contenido multimedia", "Respetar derechos de autor"],
            recommended_strategies=[HighImpactStrategy.PROBLEM_BASED,
                                   HighImpactStrategy.SELF_REGULATION],
            methodology=TeachingMethodology.PROJECT_BASED,
            prerequisites=["dig_2"],
            next_nodes=["final"]
        )

        # CENTRAL AXIS - Citizenship Skills
        cit_1 = LearningNode(
            id="cit_1", title="Ciudadania y Valores Democraticos",
            description="Comprension de derechos, deberes y participacion ciudadana",
            skill=BasicSkill.CITIZENSHIP, difficulty=NodeDifficulty.BEGINNER,
            learning_objectives=["Conocer derechos fundamentales", "Entender participacion civica"],
            recommended_strategies=[HighImpactStrategy.INQUIRY_BASED,
                                   HighImpactStrategy.GOAL_CLARITY],
            methodology=TeachingMethodology.INQUIRY_BASED,
            next_nodes=["cit_2"]
        )

        cit_2 = LearningNode(
            id="cit_2", title="Pensamiento Critico y Media Literacy",
            description="Evaluacion critica de informacion y medios de comunicacion",
            skill=BasicSkill.CITIZENSHIP, difficulty=NodeDifficulty.INTERMEDIATE,
            learning_objectives=["Detectar desinformacion", "Evaluar fuentes"],
            recommended_strategies=[HighImpactStrategy.PROBLEM_BASED,
                                   HighImpactStrategy.RETRIEVAL_PRACTICE],
            methodology=TeachingMethodology.PROBLEM_BASED,
            prerequisites=["cit_1"],
            next_nodes=["cit_3", "dig_3"]
        )

        cit_3 = LearningNode(
            id="cit_3", title="Participacion Ciudadana Digital",
            description="Uso responsable de plataformas para participacion civica",
            skill=BasicSkill.CITIZENSHIP, difficulty=NodeDifficulty.ADVANCED,
            learning_objectives=["Participacion civica online", "Activismo digital responsable"],
            recommended_strategies=[HighImpactStrategy.PROBLEM_BASED,
                                   HighImpactStrategy.SELF_REGULATION],
            methodology=TeachingMethodology.PROJECT_BASED,
            prerequisites=["cit_2", "dig_2"],
            next_nodes=["final"]
        )

        # Final integration node
        final = LearningNode(
            id="final", title="Proyecto Integrador",
            description="Proyecto final que integra todas las competencias basicas",
            skill=BasicSkill.DIGITAL, difficulty=NodeDifficulty.ADVANCED,
            learning_objectives=["Integrar competencias", "Demostrar dominio"],
            recommended_strategies=[HighImpactStrategy.PROBLEM_BASED,
                                   HighImpactStrategy.SELF_REGULATION],
            methodology=TeachingMethodology.PROJECT_BASED,
            prerequisites=["dig_3", "cit_3"]
        )

        # Add all nodes
        for node in [lit_1, lit_2, num_1, num_2, dig_1, dig_2, dig_3,
                     cit_1, cit_2, cit_3, final]:
            path.add_node(node)

        # Set root nodes (entry points)
        path.root_nodes = ["lit_1", "num_1", "dig_1", "cit_1"]

        return path

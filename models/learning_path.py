"""
Learning Path Model - Personalized Learning Pathways (PLPs)
Based on EU Key Competences for Lifelong Learning (2018/C 189/01)
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid
import json


class BasicSkill(Enum):
    """Basic Skills according to EU Key Competences Framework"""
    LITERACY = "literacy"
    NUMERACY = "numeracy"
    DIGITAL = "digital"
    CITIZENSHIP = "citizenship"


class HighImpactStrategy(Enum):
    """V13: Estrategias de Alto Impacto (EAI)"""
    FEEDBACK = "Retroalimentacion formativa"
    FORMATIVE_ASSESSMENT = "Evaluacion formativa"
    GOAL_CLARITY = "Claridad de metas"
    SELF_REGULATION = "Autorregulacion"
    PRIOR_KNOWLEDGE = "Activacion conocimiento previo"
    DISTRIBUTED_PRACTICE = "Practica distribuida"
    RETRIEVAL_PRACTICE = "Recuperacion activa"
    SCAFFOLDING = "Andamiaje adaptativo"
    DIRECT_INSTRUCTION = "Instruccion directa"
    PROBLEM_BASED = "ABP"
    SELF_EFFICACY = "Autoeficacia"
    INTRINSIC_MOTIVATION = "Motivacion intrinseca"
    INQUIRY_BASED = "Indagacion"


class TeachingMethodology(Enum):
    """V14: Metodologias de ensenanza"""
    PROJECT_BASED = "Aprendizaje por Proyectos"
    PROBLEM_BASED = "Aprendizaje por Problemas"
    INQUIRY_BASED = "Aprendizaje por Indagacion"
    GAMIFICATION = "Gamificacion"
    ADAPTIVE_TUTORIAL = "Tutorial Adaptativo"


class NodeDifficulty(Enum):
    BEGINNER = 1
    ELEMENTARY = 2
    INTERMEDIATE = 3
    ADVANCED = 4


@dataclass
class PerformanceIndicators:
    """Performance metrics for a learning node"""
    completion_rate: float = 0.0
    average_score: float = 0.0
    time_spent_minutes: float = 0.0
    attempts: int = 0
    retention_rate: float = 0.0
    error_patterns: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            'completionRate': self.completion_rate,
            'averageScore': self.average_score,
            'timeSpent': self.time_spent_minutes,
            'attempts': self.attempts,
            'retentionRate': self.retention_rate,
            'errorPatterns': self.error_patterns
        }


@dataclass
class LearningNode:
    """A single node in the learning path tree"""
    id: str
    title: str
    description: str
    skill: BasicSkill
    difficulty: NodeDifficulty
    learning_objectives: List[str] = field(default_factory=list)
    recommended_strategies: List[HighImpactStrategy] = field(default_factory=list)
    methodology: TeachingMethodology = TeachingMethodology.ADAPTIVE_TUTORIAL
    prerequisites: List[str] = field(default_factory=list)
    next_nodes: List[str] = field(default_factory=list)
    estimated_duration: int = 30
    performance: PerformanceIndicators = field(default_factory=PerformanceIndicators)
    student_performance: Dict[str, PerformanceIndicators] = field(default_factory=dict)
    # Content specific to profiles
    activities: Dict[str, List[str]] = field(default_factory=dict)
    resources: List[str] = field(default_factory=list)

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
            'performance': self.performance.to_dict(),
            'activities': self.activities,
            'resources': self.resources
        }


@dataclass
class LearningPath:
    """Complete learning path structure"""
    id: str
    name: str
    description: str
    target_skills: List[BasicSkill]
    nodes: Dict[str, LearningNode] = field(default_factory=dict)
    root_nodes: List[str] = field(default_factory=list)
    version: str = "1.0"

    def add_node(self, node: LearningNode) -> None:
        self.nodes[node.id] = node

    def get_node(self, node_id: str) -> Optional[LearningNode]:
        return self.nodes.get(node_id)

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
    """Builder for creating learning paths based on EU Key Competences"""

    @staticmethod
    def create_basic_skills_path() -> LearningPath:
        """Create a comprehensive basic skills learning path based on EU framework"""
        path = LearningPath(
            id=uuid.uuid4().hex[:12],
            name="Itinerario Competencias Clave UE",
            description="Itinerario personalizado basado en el Marco Europeo de Competencias Clave para el Aprendizaje Permanente (2018/C 189/01)",
            target_skills=[BasicSkill.LITERACY, BasicSkill.NUMERACY,
                          BasicSkill.DIGITAL, BasicSkill.CITIZENSHIP]
        )

        # =====================================================================
        # LITERACY COMPETENCE - Based on EU Framework
        # =====================================================================

        lit_1 = LearningNode(
            id="LIT01",
            title="Vocabulario y Gramatica",
            description="Conocimiento del vocabulario, gramatica funcional y funciones del lenguaje",
            skill=BasicSkill.LITERACY,
            difficulty=NodeDifficulty.BEGINNER,
            learning_objectives=[
                "Conocer vocabulario basico en contexto",
                "Comprender gramatica funcional",
                "Identificar funciones del lenguaje"
            ],
            recommended_strategies=[
                HighImpactStrategy.DIRECT_INSTRUCTION,
                HighImpactStrategy.RETRIEVAL_PRACTICE
            ],
            methodology=TeachingMethodology.ADAPTIVE_TUTORIAL,
            estimated_duration=45,
            activities={
                "high_performer": ["Analisis etimologico", "Creacion de glosarios tematicos"],
                "average": ["Ejercicios de vocabulario contextual", "Juegos de palabras"],
                "struggling": ["Flashcards interactivas", "Asociacion imagen-palabra"]
            },
            resources=["Diccionario visual", "Ejercicios interactivos"],
            next_nodes=["LIT02", "LIT03"]
        )

        lit_2 = LearningNode(
            id="LIT02",
            title="Comprension de Textos",
            description="Capacidad para identificar, comprender e interpretar textos escritos",
            skill=BasicSkill.LITERACY,
            difficulty=NodeDifficulty.ELEMENTARY,
            learning_objectives=[
                "Identificar ideas principales y secundarias",
                "Distinguir tipos de textos (literarios/no literarios)",
                "Reconocer estilos y registros linguisticos"
            ],
            recommended_strategies=[
                HighImpactStrategy.FORMATIVE_ASSESSMENT,
                HighImpactStrategy.SCAFFOLDING
            ],
            methodology=TeachingMethodology.INQUIRY_BASED,
            estimated_duration=50,
            prerequisites=["LIT01"],
            activities={
                "high_performer": ["Analisis comparativo de textos", "Sintesis critica"],
                "average": ["Subrayado y esquemas", "Resumenes guiados"],
                "struggling": ["Lectura fragmentada", "Preguntas de comprension paso a paso"]
            },
            resources=["Banco de textos graduados", "Guias de lectura"],
            next_nodes=["LIT04"]
        )

        lit_3 = LearningNode(
            id="LIT03",
            title="Expresion Oral y Escrita",
            description="Habilidades para comunicar oral y escrito en diversas situaciones",
            skill=BasicSkill.LITERACY,
            difficulty=NodeDifficulty.ELEMENTARY,
            learning_objectives=[
                "Comunicar oralmente de forma clara",
                "Redactar textos coherentes",
                "Adaptar comunicacion al contexto"
            ],
            recommended_strategies=[
                HighImpactStrategy.FEEDBACK,
                HighImpactStrategy.PROBLEM_BASED
            ],
            methodology=TeachingMethodology.PROJECT_BASED,
            estimated_duration=55,
            prerequisites=["LIT01"],
            activities={
                "high_performer": ["Debates estructurados", "Ensayos argumentativos"],
                "average": ["Presentaciones orales", "Redaccion de textos guiados"],
                "struggling": ["Descripciones simples", "Dialogos cortos"]
            },
            resources=["Rubricas de evaluacion", "Modelos de textos"],
            next_nodes=["LIT04"]
        )

        lit_4 = LearningNode(
            id="LIT04",
            title="Pensamiento Critico Textual",
            description="Evaluar informacion, formular argumentos y usar fuentes",
            skill=BasicSkill.LITERACY,
            difficulty=NodeDifficulty.INTERMEDIATE,
            learning_objectives=[
                "Evaluar validez de argumentos",
                "Distinguir hecho de opinion",
                "Usar multiples fuentes"
            ],
            recommended_strategies=[
                HighImpactStrategy.INQUIRY_BASED,
                HighImpactStrategy.SELF_REGULATION
            ],
            methodology=TeachingMethodology.PROBLEM_BASED,
            estimated_duration=60,
            prerequisites=["LIT02", "LIT03"],
            activities={
                "high_performer": ["Analisis de fake news", "Investigacion autonoma"],
                "average": ["Verificacion de fuentes guiada", "Debates moderados"],
                "struggling": ["Identificacion de sesgos con apoyo", "Ejercicios de verificacion simple"]
            },
            resources=["Checklist de verificacion", "Ejemplos de falacias"],
            next_nodes=["CIT01"]
        )

        # =====================================================================
        # NUMERACY COMPETENCE - Mathematical competence
        # =====================================================================

        num_1 = LearningNode(
            id="NUM01",
            title="Numeros y Operaciones",
            description="Conocimiento solido de numeros, medidas, estructuras y operaciones basicas",
            skill=BasicSkill.NUMERACY,
            difficulty=NodeDifficulty.BEGINNER,
            learning_objectives=[
                "Dominar operaciones aritmeticas basicas",
                "Comprender el sistema numerico",
                "Realizar calculos mentales"
            ],
            recommended_strategies=[
                HighImpactStrategy.DISTRIBUTED_PRACTICE,
                HighImpactStrategy.DIRECT_INSTRUCTION
            ],
            methodology=TeachingMethodology.ADAPTIVE_TUTORIAL,
            estimated_duration=40,
            activities={
                "high_performer": ["Problemas de logica numerica", "Patrones y secuencias"],
                "average": ["Ejercicios de calculo progresivo", "Aplicaciones cotidianas"],
                "struggling": ["Manipulativos virtuales", "Calculos con apoyo visual"]
            },
            resources=["Calculadora pedagogica", "Ejercicios graduados"],
            next_nodes=["NUM02", "NUM03"]
        )

        num_2 = LearningNode(
            id="NUM02",
            title="Razonamiento Matematico",
            description="Seguir y evaluar cadenas de argumentos, razonar matematicamente",
            skill=BasicSkill.NUMERACY,
            difficulty=NodeDifficulty.ELEMENTARY,
            learning_objectives=[
                "Seguir razonamientos logicos",
                "Justificar procedimientos",
                "Resolver problemas estructurados"
            ],
            recommended_strategies=[
                HighImpactStrategy.PROBLEM_BASED,
                HighImpactStrategy.SCAFFOLDING
            ],
            methodology=TeachingMethodology.PROBLEM_BASED,
            estimated_duration=50,
            prerequisites=["NUM01"],
            activities={
                "high_performer": ["Demostraciones matematicas", "Problemas abiertos"],
                "average": ["Problemas paso a paso", "Justificacion de soluciones"],
                "struggling": ["Problemas con pistas", "Razonamiento guiado"]
            },
            resources=["Banco de problemas", "Estrategias de resolucion"],
            next_nodes=["NUM04"]
        )

        num_3 = LearningNode(
            id="NUM03",
            title="Datos y Estadistica",
            description="Uso de datos estadisticos y graficos para la toma de decisiones",
            skill=BasicSkill.NUMERACY,
            difficulty=NodeDifficulty.ELEMENTARY,
            learning_objectives=[
                "Leer e interpretar graficos",
                "Calcular estadisticos basicos",
                "Comunicar con datos"
            ],
            recommended_strategies=[
                HighImpactStrategy.FORMATIVE_ASSESSMENT,
                HighImpactStrategy.FEEDBACK
            ],
            methodology=TeachingMethodology.PROJECT_BASED,
            estimated_duration=45,
            prerequisites=["NUM01"],
            activities={
                "high_performer": ["Analisis de datasets reales", "Visualizacion de datos"],
                "average": ["Interpretacion de graficos", "Creacion de tablas"],
                "struggling": ["Lectura de graficos simples", "Conteo y frecuencias"]
            },
            resources=["Herramientas de graficacion", "Datasets educativos"],
            next_nodes=["NUM04", "DIG02"]
        )

        num_4 = LearningNode(
            id="NUM04",
            title="Matematicas Aplicadas",
            description="Aplicar principios matematicos en contextos cotidianos (finanzas, medidas)",
            skill=BasicSkill.NUMERACY,
            difficulty=NodeDifficulty.INTERMEDIATE,
            learning_objectives=[
                "Aplicar matematicas a finanzas personales",
                "Resolver problemas de medicion",
                "Tomar decisiones basadas en datos"
            ],
            recommended_strategies=[
                HighImpactStrategy.PROBLEM_BASED,
                HighImpactStrategy.SELF_REGULATION
            ],
            methodology=TeachingMethodology.PROJECT_BASED,
            estimated_duration=55,
            prerequisites=["NUM02", "NUM03"],
            activities={
                "high_performer": ["Proyecto de presupuesto familiar", "Analisis de inversiones"],
                "average": ["Calculo de descuentos e intereses", "Planificacion de gastos"],
                "struggling": ["Ejercicios de compra simulada", "Presupuesto guiado"]
            },
            resources=["Simulador financiero", "Casos practicos"],
            next_nodes=["DIG03"]
        )

        # =====================================================================
        # DIGITAL COMPETENCE - Based on DigComp Framework
        # =====================================================================

        dig_1 = LearningNode(
            id="DIG01",
            title="Alfabetizacion Digital",
            description="Comprender tecnologias digitales, sus funciones y limitaciones",
            skill=BasicSkill.DIGITAL,
            difficulty=NodeDifficulty.BEGINNER,
            learning_objectives=[
                "Conocer dispositivos y software basicos",
                "Entender principios de internet y redes",
                "Identificar oportunidades y riesgos digitales"
            ],
            recommended_strategies=[
                HighImpactStrategy.DIRECT_INSTRUCTION,
                HighImpactStrategy.SELF_EFFICACY
            ],
            methodology=TeachingMethodology.ADAPTIVE_TUTORIAL,
            estimated_duration=40,
            activities={
                "high_performer": ["Exploracion de nuevas tecnologias", "Investigacion de IA"],
                "average": ["Navegacion guiada", "Configuracion de dispositivos"],
                "struggling": ["Tutoriales paso a paso", "Practica supervisada"]
            },
            resources=["Guias de dispositivos", "Videos tutoriales"],
            next_nodes=["DIG02", "DIG03"]
        )

        dig_2 = LearningNode(
            id="DIG02",
            title="Informacion y Datos",
            description="Buscar, filtrar, evaluar y gestionar informacion digital",
            skill=BasicSkill.DIGITAL,
            difficulty=NodeDifficulty.ELEMENTARY,
            learning_objectives=[
                "Buscar informacion de forma efectiva",
                "Evaluar fiabilidad de fuentes digitales",
                "Gestionar y organizar datos"
            ],
            recommended_strategies=[
                HighImpactStrategy.INQUIRY_BASED,
                HighImpactStrategy.FORMATIVE_ASSESSMENT
            ],
            methodology=TeachingMethodology.INQUIRY_BASED,
            estimated_duration=45,
            prerequisites=["DIG01"],
            activities={
                "high_performer": ["Busqueda avanzada y operadores", "Curaduria de contenidos"],
                "average": ["Evaluacion de sitios web", "Organizacion de favoritos"],
                "struggling": ["Busquedas guiadas", "Checklist de fiabilidad"]
            },
            resources=["Criterios CRAAP", "Herramientas de organizacion"],
            next_nodes=["DIG04", "CIT02"]
        )

        dig_3 = LearningNode(
            id="DIG03",
            title="Comunicacion y Colaboracion",
            description="Usar tecnologias para comunicacion, colaboracion y ciudadania activa",
            skill=BasicSkill.DIGITAL,
            difficulty=NodeDifficulty.ELEMENTARY,
            learning_objectives=[
                "Comunicar efectivamente en entornos digitales",
                "Colaborar usando herramientas online",
                "Participar en comunidades digitales"
            ],
            recommended_strategies=[
                HighImpactStrategy.PROBLEM_BASED,
                HighImpactStrategy.INTRINSIC_MOTIVATION
            ],
            methodology=TeachingMethodology.PROJECT_BASED,
            estimated_duration=50,
            prerequisites=["DIG01"],
            activities={
                "high_performer": ["Proyecto colaborativo internacional", "Liderazgo de equipo virtual"],
                "average": ["Trabajo en equipo con herramientas cloud", "Foros de discusion"],
                "struggling": ["Comunicacion en chat grupal", "Colaboracion en documento compartido"]
            },
            resources=["Suite colaborativa", "Netiqueta"],
            next_nodes=["DIG04", "CIT02"]
        )

        dig_4 = LearningNode(
            id="DIG04",
            title="Creacion de Contenido Digital",
            description="Crear, editar y programar contenido digital respetando derechos",
            skill=BasicSkill.DIGITAL,
            difficulty=NodeDifficulty.INTERMEDIATE,
            learning_objectives=[
                "Crear contenido multimedia basico",
                "Entender nociones de programacion",
                "Respetar propiedad intelectual"
            ],
            recommended_strategies=[
                HighImpactStrategy.PROBLEM_BASED,
                HighImpactStrategy.SELF_REGULATION
            ],
            methodology=TeachingMethodology.PROJECT_BASED,
            estimated_duration=60,
            prerequisites=["DIG02", "DIG03"],
            activities={
                "high_performer": ["Desarrollo de app simple", "Produccion de video"],
                "average": ["Presentaciones multimedia", "Blog o web basica"],
                "struggling": ["Edicion de imagenes", "Presentacion con plantilla"]
            },
            resources=["Herramientas de creacion", "Licencias Creative Commons"],
            next_nodes=["DIG05"]
        )

        dig_5 = LearningNode(
            id="DIG05",
            title="Seguridad y Bienestar Digital",
            description="Proteger dispositivos, datos, identidad digital y bienestar",
            skill=BasicSkill.DIGITAL,
            difficulty=NodeDifficulty.ADVANCED,
            learning_objectives=[
                "Proteger datos e identidad digital",
                "Reconocer amenazas de ciberseguridad",
                "Gestionar tiempo de pantalla"
            ],
            recommended_strategies=[
                HighImpactStrategy.PROBLEM_BASED,
                HighImpactStrategy.SELF_REGULATION
            ],
            methodology=TeachingMethodology.PROBLEM_BASED,
            estimated_duration=55,
            prerequisites=["DIG04"],
            activities={
                "high_performer": ["Auditoria de privacidad", "Plan de ciberseguridad personal"],
                "average": ["Configuracion de privacidad", "Deteccion de phishing"],
                "struggling": ["Creacion de contrasenas seguras", "Identificacion de riesgos basicos"]
            },
            resources=["Guia de ciberseguridad", "Test de phishing"],
            next_nodes=["FINAL"]
        )

        # =====================================================================
        # CITIZENSHIP COMPETENCE
        # =====================================================================

        cit_1 = LearningNode(
            id="CIT01",
            title="Valores Democraticos",
            description="Comprender valores europeos, derechos humanos y principios democraticos",
            skill=BasicSkill.CITIZENSHIP,
            difficulty=NodeDifficulty.BEGINNER,
            learning_objectives=[
                "Conocer derechos fundamentales de la UE",
                "Comprender el sistema democratico",
                "Valorar diversidad cultural"
            ],
            recommended_strategies=[
                HighImpactStrategy.INQUIRY_BASED,
                HighImpactStrategy.GOAL_CLARITY
            ],
            methodology=TeachingMethodology.INQUIRY_BASED,
            estimated_duration=45,
            activities={
                "high_performer": ["Analisis comparativo de sistemas politicos", "Debate sobre derechos"],
                "average": ["Estudio de casos de derechos", "Reflexion sobre valores"],
                "struggling": ["Identificacion de derechos basicos", "Ejemplos cotidianos de democracia"]
            },
            resources=["Carta de Derechos Fundamentales", "Videos educativos"],
            next_nodes=["CIT02", "CIT03"]
        )

        cit_2 = LearningNode(
            id="CIT02",
            title="Media Literacy",
            description="Acceder, comprender e interactuar criticamente con los medios",
            skill=BasicSkill.CITIZENSHIP,
            difficulty=NodeDifficulty.ELEMENTARY,
            learning_objectives=[
                "Entender rol de medios en democracia",
                "Analizar mensajes mediaticos",
                "Detectar desinformacion"
            ],
            recommended_strategies=[
                HighImpactStrategy.PROBLEM_BASED,
                HighImpactStrategy.RETRIEVAL_PRACTICE
            ],
            methodology=TeachingMethodology.PROBLEM_BASED,
            estimated_duration=50,
            prerequisites=["CIT01"],
            activities={
                "high_performer": ["Analisis de campanas mediaticas", "Investigacion de desinformacion"],
                "average": ["Comparacion de fuentes de noticias", "Verificacion de hechos"],
                "struggling": ["Identificacion de publicidad vs informacion", "Checklist anti-fake news"]
            },
            resources=["Herramientas de fact-checking", "Ejemplos de desinformacion"],
            next_nodes=["CIT04"]
        )

        cit_3 = LearningNode(
            id="CIT03",
            title="Sostenibilidad y Medio Ambiente",
            description="Comprender cambio climatico, sostenibilidad y responsabilidad ambiental",
            skill=BasicSkill.CITIZENSHIP,
            difficulty=NodeDifficulty.ELEMENTARY,
            learning_objectives=[
                "Conocer causas del cambio climatico",
                "Entender desarrollo sostenible (ODS)",
                "Adoptar comportamientos responsables"
            ],
            recommended_strategies=[
                HighImpactStrategy.INQUIRY_BASED,
                HighImpactStrategy.PROBLEM_BASED
            ],
            methodology=TeachingMethodology.PROJECT_BASED,
            estimated_duration=50,
            prerequisites=["CIT01"],
            activities={
                "high_performer": ["Proyecto de huella de carbono", "Plan de accion climatica"],
                "average": ["Calculo de huella ecologica", "Propuestas de mejora local"],
                "struggling": ["Identificacion de acciones sostenibles", "Diario ecologico"]
            },
            resources=["Calculadora de huella", "ODS interactivos"],
            next_nodes=["CIT04"]
        )

        cit_4 = LearningNode(
            id="CIT04",
            title="Participacion Ciudadana",
            description="Participar efectivamente en actividades civicas y toma de decisiones",
            skill=BasicSkill.CITIZENSHIP,
            difficulty=NodeDifficulty.INTERMEDIATE,
            learning_objectives=[
                "Desarrollar argumentos constructivos",
                "Participar en decisiones comunitarias",
                "Promover justicia social"
            ],
            recommended_strategies=[
                HighImpactStrategy.PROBLEM_BASED,
                HighImpactStrategy.SELF_REGULATION
            ],
            methodology=TeachingMethodology.PROJECT_BASED,
            estimated_duration=55,
            prerequisites=["CIT02", "CIT03"],
            activities={
                "high_performer": ["Proyecto de mejora comunitaria", "Campana de sensibilizacion"],
                "average": ["Propuesta a gobierno escolar", "Voluntariado planificado"],
                "struggling": ["Participacion en actividad civica", "Reflexion sobre contribucion"]
            },
            resources=["Guia de participacion", "Ejemplos de proyectos civicos"],
            next_nodes=["FINAL"]
        )

        # =====================================================================
        # FINAL INTEGRATION NODE
        # =====================================================================

        final = LearningNode(
            id="FINAL",
            title="Proyecto Integrador",
            description="Proyecto final que integra las cuatro competencias clave",
            skill=BasicSkill.DIGITAL,
            difficulty=NodeDifficulty.ADVANCED,
            learning_objectives=[
                "Integrar competencias clave",
                "Demostrar dominio transversal",
                "Crear producto final significativo"
            ],
            recommended_strategies=[
                HighImpactStrategy.PROBLEM_BASED,
                HighImpactStrategy.SELF_REGULATION
            ],
            methodology=TeachingMethodology.PROJECT_BASED,
            estimated_duration=90,
            prerequisites=["DIG05", "CIT04"],
            activities={
                "high_performer": ["Proyecto de impacto social con tecnologia"],
                "average": ["Campana digital sobre tema ciudadano"],
                "struggling": ["Presentacion multimedia sobre ODS local"]
            },
            resources=["Rubrica de evaluacion integral", "Ejemplos de proyectos"]
        )

        # Add all nodes to path
        all_nodes = [
            lit_1, lit_2, lit_3, lit_4,
            num_1, num_2, num_3, num_4,
            dig_1, dig_2, dig_3, dig_4, dig_5,
            cit_1, cit_2, cit_3, cit_4,
            final
        ]

        for node in all_nodes:
            path.add_node(node)

        # Set root nodes (entry points for each competence)
        path.root_nodes = ["LIT01", "NUM01", "DIG01", "CIT01"]

        return path

# PLAIP - Personalized Learning's Artificial Intelligence Paths

Sistema de itinerarios personalizados de aprendizaje basado en **Aprendizaje por Refuerzo** para el desarrollo de **Basic Skills** (competencias basicas).

## Proyecto ERASMUS-EDU-2026-POL-EXP-T03

Este proyecto forma parte de una accion de Policy Experimentation de la Comision Europea, orientada a la definicion y testeo de modelos de itinerarios personalizados de aprendizaje (PLPs) para apoyar la adquisicion de basic skills en educacion secundaria y FP (EQF 2-4).

### Enfoque Estrategico

- **Eje Central**: Digital Skills + Citizenship Skills
- **Fundamento**: Literacy + Numeracy (foundational skills)

## Caracteristicas

- **Itinerarios Personalizados**: Definicion de rutas de aprendizaje adaptadas al perfil del estudiante
- **Aprendizaje por Refuerzo**: Simulacion de escenarios mediante Q-Learning para optimizar itinerarios
- **Clonacion de Perfiles**: Creacion de perfiles virtuales de estudiantes para simulaciones
- **Visualizacion de Arbol**: Representacion grafica del itinerario con indicadores de rendimiento
- **Variables AGORA**: Integracion de variables de diagnostico y evaluacion basadas en el modelo AGORA

## Estructura del Proyecto

```
PLAIP/
├── app.py                 # Aplicacion Flask principal
├── models/
│   ├── student_profile.py # Perfil del estudiante (Variables INPUT)
│   ├── learning_path.py   # Itinerarios de aprendizaje
│   └── database.py        # Modelos de base de datos
├── rl/
│   ├── environment.py     # Entorno Gymnasium para RL
│   └── agent.py           # Agente Q-Learning
├── visualization/
│   └── tree.py            # Generacion de datos para D3.js
├── templates/             # Templates HTML (Jinja2)
├── static/
│   ├── css/style.css      # Estilos personalizados
│   └── js/main.js         # JavaScript principal
└── requirements.txt       # Dependencias Python
```

## Variables del Modelo (basadas en AGORA)

### INPUT: Diagnostico y Perfil del Estudiante
- V1-V4: Variables demograficas (edad, etapa educativa, genero, competencia digital)
- V5-V6: Factores emocionales (motivacion intrinseca, autoeficacia)
- V7-V12: Factores cognitivos (preferencias, estilo Kolb, conocimiento previo, etc.)

### PROCESO: Intervencion y Adaptacion
- V13: Estrategias de Alto Impacto (EAI)
- V14: Metodologias de ensenanza
- V15: Adaptacion temporal/frecuencial

### OUTPUT: Metricas de Rendimiento
- V16-V20: Desempeno y retencion
- V21-V24: Implicacion y equidad
- V25-V26: Validacion tecnica

## Instalacion

```bash
# Clonar repositorio
git clone https://github.com/upocuantitativo/plaip.git
cd plaip

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicacion
python app.py
```

## Uso

1. **Dashboard**: Vista general del sistema
2. **Itinerarios**: Visualizacion del arbol de aprendizaje con indicadores
3. **Estudiantes**: Gestion de perfiles y creacion de estudiantes de prueba
4. **Simulacion RL**: Entrenamiento del agente y ejecucion de simulaciones
5. **Analiticas**: Metricas de rendimiento por competencia

## API Endpoints

- `GET /api/tree` - Datos del arbol de itinerarios
- `GET/POST /api/students` - Gestion de estudiantes
- `POST /api/simulation/train` - Entrenar agente RL
- `POST /api/simulation/run` - Ejecutar simulaciones
- `POST /api/feedback` - Registrar feedback y ajustar itinerarios

## Tecnologias

- **Backend**: Flask, SQLAlchemy
- **RL**: Q-Learning (implementacion propia), Gymnasium
- **Frontend**: Bootstrap 5, D3.js, Plotly
- **Base de datos**: SQLite (desarrollo), PostgreSQL (produccion)

## Referencias

- [Basic Skills - European Commission](https://education.ec.europa.eu/education-levels/school-education/basic-skills)
- [DigComp 2.2 Framework](https://ec.europa.eu/jrc/en/digcomp)
- [ERASMUS+ Policy Experimentation](https://erasmus-plus.ec.europa.eu/)

## Licencia

Este proyecto es parte de una iniciativa educativa de la Universidad Pablo de Olavide.

## Contacto

- **Universidad Pablo de Olavide**
- Liderado por: Manuel Chaves Maza (Area de Metodos Cuantitativos) y Miguel Garcia Torres (Area de Lenguajes y Sistemas Informaticos)

---

*PLAIP - Proyecto ERASMUS-EDU-2026-POL-EXP-T03*

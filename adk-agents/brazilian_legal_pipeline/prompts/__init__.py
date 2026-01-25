"""
Instructions/Prompts para os agentes da pipeline juridica.

Cada agente tem sua instruction especifica que define:
- Funcao do agente
- Processamento obrigatorio
- Formato de output esperado
"""

from .intake import INTAKE_INSTRUCTION
from .verificador import VERIFICADOR_INSTRUCTION
from .cetico import CETICO_INSTRUCTION
from .construtor import CONSTRUTOR_INSTRUCTION
from .destruidor import DESTRUIDOR_INSTRUCTION
from .redator import REDATOR_INSTRUCTION
from .critico import CRITICO_INSTRUCTION
from .synthesizer import SYNTHESIZER_INSTRUCTION

__all__ = [
    "INTAKE_INSTRUCTION",
    "VERIFICADOR_INSTRUCTION",
    "CETICO_INSTRUCTION",
    "CONSTRUTOR_INSTRUCTION",
    "DESTRUIDOR_INSTRUCTION",
    "REDATOR_INSTRUCTION",
    "CRITICO_INSTRUCTION",
    "SYNTHESIZER_INSTRUCTION",
]

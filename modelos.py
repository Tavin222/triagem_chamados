"""Modelo de dados do sistema de triagem de chamados."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Chamado:
    """Representa um chamado de suporte aberto por um cliente."""

    texto: str
    categoria: str
    prioridade: int  # 1 = Crítica, 2 = Alta, 3 = Média, 4 = Baixa
    score: int
    id: Optional[int] = None
    status: str = "pendente"
    criado_em: str = ""
    atendido_em: str = ""

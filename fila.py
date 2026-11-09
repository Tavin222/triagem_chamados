"""Fila de prioridade para atendimento de chamados (estrutura de dados: heap).

Chamados de menor número de prioridade (1 = Crítica) saem primeiro. Em caso de
empate, vale a ordem de chegada (FIFO), garantida por um contador sequencial.
"""
import heapq
import itertools
from typing import List, Optional

from modelos import Chamado


class FilaPrioridade:
    def __init__(self) -> None:
        self._heap: list = []
        self._ordem = itertools.count()

    def inserir(self, chamado: Chamado) -> None:
        heapq.heappush(self._heap, (chamado.prioridade, next(self._ordem), chamado))

    def proximo(self) -> Optional[Chamado]:
        """Remove e devolve o próximo chamado a ser atendido."""
        if not self._heap:
            return None
        return heapq.heappop(self._heap)[2]

    def listar(self) -> List[Chamado]:
        """Devolve os chamados na ordem de atendimento, sem remover."""
        return [item[2] for item in sorted(self._heap, key=lambda i: (i[0], i[1]))]

    def __len__(self) -> int:
        return len(self._heap)

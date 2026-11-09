"""Persistência dos chamados em SQLite (biblioteca padrão do Python)."""
import sqlite3
from datetime import datetime
from typing import Dict, List

from modelos import Chamado

AGORA = lambda: datetime.now().isoformat(timespec="seconds")  # noqa: E731


class Banco:
    def __init__(self, caminho: str = "chamados.db") -> None:
        self.con = sqlite3.connect(caminho)
        self.con.row_factory = sqlite3.Row
        self.con.execute(
            """CREATE TABLE IF NOT EXISTS chamados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                texto TEXT NOT NULL,
                categoria TEXT NOT NULL,
                prioridade INTEGER NOT NULL,
                score INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pendente',
                criado_em TEXT NOT NULL,
                atendido_em TEXT
            )"""
        )
        self.con.commit()

    def salvar(self, c: Chamado) -> Chamado:
        c.criado_em = AGORA()
        cur = self.con.execute(
            "INSERT INTO chamados (texto, categoria, prioridade, score, status, criado_em)"
            " VALUES (?, ?, ?, ?, 'pendente', ?)",
            (c.texto, c.categoria, c.prioridade, c.score, c.criado_em),
        )
        self.con.commit()
        c.id = cur.lastrowid
        return c

    def pendentes(self) -> List[Chamado]:
        linhas = self.con.execute(
            "SELECT * FROM chamados WHERE status = 'pendente' ORDER BY id"
        ).fetchall()
        return [
            Chamado(l["texto"], l["categoria"], l["prioridade"], l["score"],
                    l["id"], l["status"], l["criado_em"], l["atendido_em"] or "")
            for l in linhas
        ]

    def marcar_atendido(self, id_chamado: int) -> None:
        self.con.execute(
            "UPDATE chamados SET status = 'atendido', atendido_em = ? WHERE id = ?",
            (AGORA(), id_chamado),
        )
        self.con.commit()

    def estatisticas(self) -> Dict:
        linhas = self.con.execute("SELECT * FROM chamados").fetchall()
        por_categoria: Dict[str, int] = {}
        por_prioridade: Dict[int, int] = {}
        esperas = []
        for l in linhas:
            por_categoria[l["categoria"]] = por_categoria.get(l["categoria"], 0) + 1
            por_prioridade[l["prioridade"]] = por_prioridade.get(l["prioridade"], 0) + 1
            if l["atendido_em"]:
                dif = datetime.fromisoformat(l["atendido_em"]) - datetime.fromisoformat(l["criado_em"])
                esperas.append(dif.total_seconds())
        atendidos = sum(1 for l in linhas if l["status"] == "atendido")
        return {
            "total": len(linhas),
            "atendidos": atendidos,
            "pendentes": len(linhas) - atendidos,
            "por_categoria": por_categoria,
            "por_prioridade": por_prioridade,
            "espera_media_s": sum(esperas) / len(esperas) if esperas else 0.0,
        }

    def fechar(self) -> None:
        self.con.close()

"""Classificação de chamados por palavras-chave e cálculo de prioridade.

Estratégia: o texto do chamado é normalizado (minúsculas, sem acentos) e
comparado com um dicionário de termos ponderados por categoria. A categoria
com maior pontuação vence. A prioridade é calculada somando a pontuação-base
da categoria com os termos de urgência encontrados no texto.
"""
import re
import unicodedata
from dataclasses import dataclass
from typing import List

# categoria -> (pontuação-base de prioridade, {termo: peso})
CATEGORIAS = {
    "Fraude e segurança": (6, {
        "fraude": 3, "golpe": 3, "clonado": 3, "clonaram": 3, "invadiram": 3,
        "invadida": 3, "invadido": 3, "hackeado": 3, "roubo": 3,
        "roubaram": 3, "phishing": 2, "nao reconheco": 3, "nao fui eu": 3,
    }),
    "Pagamentos e Pix": (3, {
        "pix": 2, "transferencia": 2, "boleto": 2, "pagamento": 1,
        "qr code": 2, "saldo": 1, "estorno": 2, "deposito": 1,
    }),
    "Cartão": (2, {
        "cartao": 2, "fatura": 2, "limite": 1, "anuidade": 1, "compra": 1,
        "chargeback": 2, "contestacao": 2,
    }),
    "Acesso à conta": (2, {
        "senha": 2, "login": 2, "acessar": 2, "entrar": 1, "token": 1,
        "biometria": 2, "bloqueada": 2, "bloqueado": 2, "cadastro": 1,
    }),
    "Cobrança e tarifas": (1, {
        "cobranca": 2, "tarifa": 2, "taxa": 2, "juros": 2, "cobrado": 2,
        "reembolso": 2,
    }),
}
CATEGORIA_PADRAO = "Dúvidas gerais"

# termos que indicam urgência e somam pontos à prioridade (máximo de 3)
URGENCIA = {
    "urgente": 2, "imediatamente": 2, "agora": 1, "nao consigo": 1,
    "fora do ar": 2, "nao funciona": 1, "dinheiro sumiu": 3,
    "perdi dinheiro": 3, "desesperado": 1, "ha dias": 1,
}
LIMITE_URGENCIA = 3

NIVEIS = {1: "Crítica", 2: "Alta", 3: "Média", 4: "Baixa"}


@dataclass
class Resultado:
    categoria: str
    score: int
    prioridade: int
    termos: List[str]


def normalizar(texto: str) -> str:
    """Converte para minúsculas e remove acentos."""
    decomposto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in decomposto if unicodedata.category(c) != "Mn")


def _contem(texto: str, termo: str) -> bool:
    return re.search(rf"\b{re.escape(termo)}\b", texto) is not None


def nivel_de_prioridade(score: int) -> int:
    """Converte a pontuação em nível: 1 (Crítica) a 4 (Baixa)."""
    if score >= 6:
        return 1
    if score >= 4:
        return 2
    if score >= 2:
        return 3
    return 4


def classificar(texto: str) -> Resultado:
    """Classifica um chamado e calcula sua prioridade."""
    t = normalizar(texto)
    melhor_categoria, melhor_peso, base, termos = CATEGORIA_PADRAO, 0, 0, []

    for categoria, (base_cat, palavras) in CATEGORIAS.items():
        achados = [p for p in palavras if _contem(t, p)]
        peso = sum(palavras[p] for p in achados)
        if peso > melhor_peso:
            melhor_categoria, melhor_peso = categoria, peso
            base, termos = base_cat, achados

    urgencia = sum(p for termo, p in URGENCIA.items() if _contem(t, termo))
    score = base + min(urgencia, LIMITE_URGENCIA)
    return Resultado(melhor_categoria, score, nivel_de_prioridade(score), termos)

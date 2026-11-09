"""Triagem de Chamados de Suporte - interface de linha de comando.

Uso:  python main.py
"""
import csv
import os

from banco import Banco
from classificador import NIVEIS, classificar
from fila import FilaPrioridade
from modelos import Chamado

CSV_EXEMPLO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados_exemplo.csv")


def abrir_chamado(texto: str, banco: Banco, fila: FilaPrioridade) -> Chamado:
    """Classifica o texto, grava no banco e coloca o chamado na fila."""
    r = classificar(texto)
    chamado = Chamado(texto=texto.strip(), categoria=r.categoria,
                      prioridade=r.prioridade, score=r.score)
    banco.salvar(chamado)
    fila.inserir(chamado)
    return chamado


def atender_proximo(banco: Banco, fila: FilaPrioridade):
    """Retira o chamado mais urgente da fila e o marca como atendido."""
    chamado = fila.proximo()
    if chamado is not None:
        banco.marcar_atendido(chamado.id)
    return chamado


def carregar_fila(banco: Banco) -> FilaPrioridade:
    """Reconstrói a fila em memória a partir dos chamados pendentes no banco."""
    fila = FilaPrioridade()
    for chamado in banco.pendentes():
        fila.inserir(chamado)
    return fila


def importar_csv(caminho: str, banco: Banco, fila: FilaPrioridade) -> int:
    """Importa chamados de um CSV com a coluna 'texto'. Devolve a quantidade."""
    total = 0
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        for linha in csv.DictReader(arquivo):
            abrir_chamado(linha["texto"], banco, fila)
            total += 1
    return total


def _linha(c: Chamado) -> str:
    return f"#{c.id:<3} [{NIVEIS[c.prioridade]:<7}] {c.categoria:<20} | {c.texto[:60]}"


def mostrar_fila(fila: FilaPrioridade) -> None:
    if not len(fila):
        print("Fila vazia.")
        return
    for c in fila.listar():
        print(_linha(c))


def mostrar_relatorio(banco: Banco) -> None:
    e = banco.estatisticas()
    print(f"Total: {e['total']} | Atendidos: {e['atendidos']} | Pendentes: {e['pendentes']}")
    print("Por categoria:")
    for cat, qtd in sorted(e["por_categoria"].items(), key=lambda x: -x[1]):
        print(f"  {cat:<22} {qtd}")
    print("Por prioridade:")
    for nivel in sorted(e["por_prioridade"]):
        print(f"  {NIVEIS[nivel]:<22} {e['por_prioridade'][nivel]}")
    print(f"Espera média até o atendimento: {e['espera_media_s']:.0f} s")


MENU = """
=== Triagem de Chamados de Suporte ===
1 - Abrir novo chamado
2 - Ver fila de atendimento
3 - Atender próximo chamado
4 - Relatório
5 - Carregar chamados de exemplo
0 - Sair
"""


def menu(caminho_banco: str = "chamados.db") -> None:
    banco = Banco(caminho_banco)
    fila = carregar_fila(banco)
    try:
        while True:
            print(MENU)
            try:
                opcao = input("Opção: ").strip()
            except EOFError:
                break
            if opcao == "1":
                texto = input("Descreva o problema do cliente: ").strip()
                if not texto:
                    print("Texto vazio. Chamado não criado.")
                    continue
                c = abrir_chamado(texto, banco, fila)
                print(f"Chamado #{c.id} criado -> {c.categoria}, prioridade {NIVEIS[c.prioridade]}.")
            elif opcao == "2":
                mostrar_fila(fila)
            elif opcao == "3":
                c = atender_proximo(banco, fila)
                print("Atendendo: " + _linha(c) if c else "Nenhum chamado pendente.")
            elif opcao == "4":
                mostrar_relatorio(banco)
            elif opcao == "5":
                print(f"{importar_csv(CSV_EXEMPLO, banco, fila)} chamados importados.")
            elif opcao == "0":
                break
            else:
                print("Opção inválida.")
    finally:
        banco.fechar()


if __name__ == "__main__":
    menu()

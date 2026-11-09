# Triagem de Chamados de Suporte

Programa em Python (somente biblioteca padrão, sem instalar nada) que recebe
chamados de suporte em texto livre, classifica cada um por categoria, calcula
a prioridade e organiza uma fila para que os casos mais urgentes (fraude,
Pix fora do ar etc.) sejam atendidos primeiro.

## Como executar

Desenvolvido e testado com Python 3.10.12 (somente biblioteca padrão). Versões anteriores não foram testadas.

```
python main.py                          # abre o menu
python -m unittest discover -s tests -v # roda os testes
```

No menu, a opção 5 carrega 15 chamados fictícios de `dados_exemplo.csv`.
Os dados ficam salvos no arquivo `chamados.db` (SQLite), criado automaticamente.

## Estrutura

| Arquivo | Função |
|---|---|
| `main.py` | Menu de linha de comando e funções de orquestração |
| `classificador.py` | Normalização do texto, categorias por palavras-chave e prioridade |
| `fila.py` | Fila de prioridade (heap) com desempate por ordem de chegada |
| `banco.py` | Persistência em SQLite e estatísticas do relatório |
| `modelos.py` | Classe `Chamado` |
| `tests/test_triagem.py` | Testes automatizados (unittest) |

## Regras de prioridade

Cada categoria tem uma pontuação-base (Fraude 6, Pagamentos/Pix 3, Cartão 2,
Acesso 2, Cobrança 1, Dúvidas 0). Termos de urgência no texto (ex.: "urgente",
"fora do ar", "dinheiro sumiu") somam até 3 pontos.

| Pontuação | Prioridade |
|---|---|
| 6 ou mais | 1 - Crítica |
| 4 a 5 | 2 - Alta |
| 2 a 3 | 3 - Média |
| 0 a 1 | 4 - Baixa |

## Conceitos de disciplina aplicados

Estruturas de dados (fila de prioridade/heap), lógica de programação,
manipulação de strings e expressões regulares, persistência com SQL e
testes automatizados.

Todos os dados de exemplo são fictícios.

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from banco import Banco  # noqa: E402
from classificador import classificar, normalizar  # noqa: E402
from fila import FilaPrioridade  # noqa: E402
from main import CSV_EXEMPLO, abrir_chamado, atender_proximo, carregar_fila, importar_csv  # noqa: E402


class TestClassificador(unittest.TestCase):
    def test_normalizar_remove_acentos(self):
        self.assertEqual(normalizar("Cartão NÃO funciona"), "cartao nao funciona")

    def test_fraude_e_critica(self):
        r = classificar("Acho que foi golpe, invadiram minha conta")
        self.assertEqual(r.categoria, "Fraude e segurança")
        self.assertEqual(r.prioridade, 1)

    def test_pix_fora_do_ar_e_alta_ou_critica(self):
        r = classificar("O Pix está fora do ar")
        self.assertEqual(r.categoria, "Pagamentos e Pix")
        self.assertLessEqual(r.prioridade, 2)

    def test_duvida_geral_e_baixa(self):
        r = classificar("Como faço para atualizar o aplicativo?")
        self.assertEqual(r.categoria, "Dúvidas gerais")
        self.assertEqual(r.prioridade, 4)

    def test_nao_casa_parte_de_palavra(self):
        self.assertEqual(classificar("Gosto de pixel art").categoria, "Dúvidas gerais")


class TestFila(unittest.TestCase):
    def _c(self, prioridade, texto="x"):
        from modelos import Chamado
        return Chamado(texto, "cat", prioridade, 0)

    def test_menor_numero_sai_primeiro(self):
        f = FilaPrioridade()
        f.inserir(self._c(3, "media"))
        f.inserir(self._c(1, "critica"))
        f.inserir(self._c(4, "baixa"))
        self.assertEqual(f.proximo().texto, "critica")

    def test_empate_respeita_ordem_de_chegada(self):
        f = FilaPrioridade()
        f.inserir(self._c(2, "primeiro"))
        f.inserir(self._c(2, "segundo"))
        self.assertEqual([c.texto for c in f.listar()], ["primeiro", "segundo"])

    def test_fila_vazia(self):
        self.assertIsNone(FilaPrioridade().proximo())


class TestIntegracao(unittest.TestCase):
    def setUp(self):
        self.banco = Banco(":memory:")
        self.fila = FilaPrioridade()

    def test_importar_e_atender_na_ordem(self):
        total = importar_csv(CSV_EXEMPLO, self.banco, self.fila)
        self.assertEqual(total, 15)
        prioridades = []
        while len(self.fila):
            prioridades.append(atender_proximo(self.banco, self.fila).prioridade)
        self.assertEqual(prioridades, sorted(prioridades))
        e = self.banco.estatisticas()
        self.assertEqual((e["atendidos"], e["pendentes"]), (15, 0))

    def test_fila_e_reconstruida_do_banco(self):
        abrir_chamado("Esqueci minha senha", self.banco, self.fila)
        abrir_chamado("Foi golpe, invadiram minha conta", self.banco, self.fila)
        nova = carregar_fila(self.banco)
        self.assertEqual(len(nova), 2)
        self.assertEqual(nova.proximo().categoria, "Fraude e segurança")


if __name__ == "__main__":
    unittest.main()

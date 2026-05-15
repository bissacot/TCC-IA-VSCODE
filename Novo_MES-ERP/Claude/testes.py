"""
Testes Unitários para o Sistema de Produção ERP/MES
Valida todas as funcionalidades e regras de negócio
"""

import unittest
from sistema_producao import (
    OrdemFabricacao, OrdemProducao, LinhaProducao
)


class TesteOrdemFabricacao(unittest.TestCase):
    """Testes para a classe OrdemFabricacao"""
    
    def test_criar_of_valida(self):
        """Testa criação de OF válida"""
        of = OrdemFabricacao(25, 1, 23)
        valido, msg = of.validar()
        self.assertTrue(valido)
        self.assertEqual(of.gerar_codigo(), "25123")
    
    def test_of_ano_invalido_negativo(self):
        """Testa OF com ano negativo"""
        of = OrdemFabricacao(-1, 0, 10)
        valido, msg = of.validar()
        self.assertFalse(valido)
    
    def test_of_ano_invalido_acima_99(self):
        """Testa OF com ano > 99"""
        of = OrdemFabricacao(100, 0, 10)
        valido, msg = of.validar()
        self.assertFalse(valido)
    
    def test_of_tipo_invalido(self):
        """Testa OF com tipo inválido"""
        of = OrdemFabricacao(25, 2, 10)  # Tipo deve ser 0 ou 1
        valido, msg = of.validar()
        self.assertFalse(valido)
    
    def test_of_cliente_invalido(self):
        """Testa OF com cliente fora do intervalo"""
        of = OrdemFabricacao(25, 1, 100)
        valido, msg = of.validar()
        self.assertFalse(valido)
    
    def test_of_normal(self):
        """Testa OF tipo normal"""
        of = OrdemFabricacao(25, 0, 10)
        self.assertEqual(of.gerar_codigo(), "25010")
    
    def test_of_premium(self):
        """Testa OF tipo premium"""
        of = OrdemFabricacao(25, 1, 10)
        self.assertEqual(of.gerar_codigo(), "25110")


class TesteOrdemProducao(unittest.TestCase):
    """Testes para a classe OrdemProducao"""
    
    def test_op_valida_completa(self):
        """Testa OP válida com todos os parâmetros"""
        op = OrdemProducao("2512312B05")
        self.assertTrue(op.valido)
        self.assertEqual(op.fase, 1)
        self.assertEqual(op.subfase, 2)
        self.assertEqual(op.modo, 'B')
        self.assertEqual(op.recurso_base, 5)
    
    def test_op_modo_a(self):
        """Testa OP com modo A (1 recurso)"""
        op = OrdemProducao("2512300A10")
        self.assertTrue(op.valido)
        self.assertEqual(op.obter_recursos(), [10])
        self.assertEqual(len(op.obter_recursos()), 1)
    
    def test_op_modo_b(self):
        """Testa OP com modo B (2 recursos)"""
        op = OrdemProducao("2512300B10")
        self.assertTrue(op.valido)
        self.assertEqual(op.obter_recursos(), [10, 11])
        self.assertEqual(len(op.obter_recursos()), 2)
    
    def test_op_modo_c(self):
        """Testa OP com modo C (3 recursos)"""
        op = OrdemProducao("2512300C10")
        self.assertTrue(op.valido)
        self.assertEqual(op.obter_recursos(), [10, 11, 12])
        self.assertEqual(len(op.obter_recursos()), 3)
    
    def test_op_fase_invalida(self):
        """Testa OP com fase inválida"""
        op = OrdemProducao("2512350A10")
        self.assertFalse(op.valido)
        self.assertIn("Fase", op.mensagem_erro)
    
    def test_op_subfase_invalida(self):
        """Testa OP com subfase inválida"""
        op = OrdemProducao("2512315A10")
        self.assertFalse(op.valido)
        self.assertIn("Subfase", op.mensagem_erro)
    
    def test_op_modo_invalido(self):
        """Testa OP com modo inválido"""
        op = OrdemProducao("2512300XA10")
        self.assertFalse(op.valido)
        self.assertIn("Modo", op.mensagem_erro)
    
    def test_op_recurso_invalido_acima_max(self):
        """Testa OP com recurso acima do máximo"""
        op = OrdemProducao("2512300A99")
        self.assertFalse(op.valido)
        self.assertIn("Recurso", op.mensagem_erro)
    
    def test_op_overflow_modo_b(self):
        """Testa OP com overflow no modo B"""
        op = OrdemProducao("2512300B26")
        self.assertFalse(op.valido)
        self.assertIn("Overflow", op.mensagem_erro)
    
    def test_op_overflow_modo_c(self):
        """Testa OP com overflow no modo C"""
        op = OrdemProducao("2512300C25")
        self.assertFalse(op.valido)
        self.assertIn("Overflow", op.mensagem_erro)
    
    def test_op_recurso_zero(self):
        """Testa OP com recurso 0 (válido)"""
        op = OrdemProducao("2512300A00")
        self.assertTrue(op.valido)
        self.assertEqual(op.obter_recursos(), [0])
    
    def test_op_recurso_26_modo_a(self):
        """Testa OP com recurso 26 modo A (válido)"""
        op = OrdemProducao("2512300A26")
        self.assertTrue(op.valido)
        self.assertEqual(op.obter_recursos(), [26])
    
    def test_op_recurso_25_modo_b(self):
        """Testa OP com recurso 25 modo B (válido)"""
        op = OrdemProducao("2512300B25")
        self.assertTrue(op.valido)
        self.assertEqual(op.obter_recursos(), [25, 26])
    
    def test_op_comprimento_invalido_curto(self):
        """Testa OP com formato muito curto"""
        op = OrdemProducao("251230A1")
        self.assertFalse(op.valido)
        self.assertIn("10 caracteres", op.mensagem_erro)
    
    def test_op_comprimento_invalido_longo(self):
        """Testa OP com formato muito longo"""
        op = OrdemProducao("25123001A010")
        self.assertFalse(op.valido)
        self.assertIn("10 caracteres", op.mensagem_erro)
    
    def test_op_modo_minusculo(self):
        """Testa OP com modo em minúsculo (deve converter)"""
        op = OrdemProducao("2512300a10")
        self.assertTrue(op.valido)
        self.assertEqual(op.modo, 'A')
    
    def test_op_detalhes(self):
        """Testa obtenção de detalhes da OP"""
        op = OrdemProducao("2512312B05")
        detalhes = op.obter_detalhes()
        
        self.assertEqual(detalhes['codigo'], "2512312B05")
        self.assertTrue(detalhes['valido'])
        self.assertEqual(detalhes['of'], "25123")
        self.assertEqual(detalhes['fase'], 1)
        self.assertEqual(detalhes['subfase'], 2)
        self.assertEqual(detalhes['modo'], 'B')
        self.assertEqual(detalhes['recurso_base'], "05")
        self.assertEqual(detalhes['quantidade_recursos'], 2)


class TesteLinhaProducao(unittest.TestCase):
    """Testes para a classe LinhaProducao"""
    
    def setUp(self):
        """Configura a linha para cada teste"""
        self.linha = LinhaProducao()
    
    def test_criar_of(self):
        """Testa criação de OF na linha"""
        of_codigo = self.linha.criar_ordem_fabricacao(25, 1, 23)
        self.assertEqual(of_codigo, "25123")
        self.assertIn(of_codigo, self.linha.ordens_fabricacao)
    
    def test_criar_of_invalida(self):
        """Testa criação de OF inválida retorna None"""
        of_codigo = self.linha.criar_ordem_fabricacao(100, 2, 23)
        self.assertIsNone(of_codigo)
    
    def test_gerar_op(self):
        """Testa geração de OP"""
        of = self.linha.criar_ordem_fabricacao(25, 1, 23)
        op = self.linha.gerar_ordem_producao(of, 1, 2, 'B', 5)
        
        self.assertEqual(op, "2512312B05")
        self.assertEqual(len(self.linha.ordens_producao), 1)
    
    def test_gerar_op_of_inexistente(self):
        """Testa geração de OP com OF inexistente"""
        op = self.linha.gerar_ordem_producao("99999", 1, 2, 'B', 5)
        self.assertIsNone(op)
    
    def test_validar_op(self):
        """Testa validação de OP"""
        valida, detalhes = self.linha.validar_ordem_producao("2512312B05")
        
        self.assertTrue(valida)
        self.assertEqual(detalhes['codigo'], "2512312B05")
    
    def test_validar_op_invalida(self):
        """Testa validação de OP inválida"""
        valida, detalhes = self.linha.validar_ordem_producao("2512315B05")
        
        self.assertFalse(valida)
        self.assertIn("Subfase", detalhes['mensagem'])
    
    def test_simular_op(self):
        """Testa simulação de OP"""
        resultado = self.linha.simular_execucao_op("2512312B05")
        
        self.assertEqual(resultado['status'], 'SUCESSO')
        self.assertEqual(resultado['op'], "2512312B05")
        self.assertTrue(resultado['valida'])
        self.assertEqual(len(resultado['recursos_alocados']), 2)
    
    def test_simular_op_invalida(self):
        """Testa simulação de OP inválida"""
        resultado = self.linha.simular_execucao_op("2512315B05")
        
        self.assertEqual(resultado['status'], 'ERRO')
        self.assertFalse(resultado['valida'])
        self.assertIn('erro', resultado)
    
    def test_historico_simulacoes(self):
        """Testa histórico de simulações"""
        self.linha.simular_execucao_op("2512300A10")
        self.linha.simular_execucao_op("2512300B10")
        
        self.assertEqual(len(self.linha.simulacoes), 2)
    
    def test_listar_estrutura(self):
        """Testa geração de informações da estrutura"""
        estrutura = self.linha.listar_estrutura()
        
        self.assertIn("ESTRUTURA", estrutura)
        self.assertIn("FASES", estrutura)
        self.assertIn("MODOS", estrutura)
        self.assertIn("RECURSOS", estrutura)


class TesteIntegracao(unittest.TestCase):
    """Testes de integração do sistema completo"""
    
    def setUp(self):
        self.linha = LinhaProducao()
    
    def test_fluxo_completo(self):
        """Testa um fluxo completo de produção"""
        # 1. Criar OF
        of1 = self.linha.criar_ordem_fabricacao(25, 0, 10)
        of2 = self.linha.criar_ordem_fabricacao(25, 1, 15)
        
        self.assertIsNotNone(of1)
        self.assertIsNotNone(of2)
        
        # 2. Gerar OPs
        op1 = self.linha.gerar_ordem_producao(of1, 0, 0, 'A', 5)
        op2 = self.linha.gerar_ordem_producao(of1, 1, 1, 'B', 10)
        op3 = self.linha.gerar_ordem_producao(of2, 2, 2, 'C', 20)
        
        self.assertIsNotNone(op1)
        self.assertIsNotNone(op2)
        self.assertIsNotNone(op3)
        
        # 3. Validar OPs
        for op in [op1, op2, op3]:
            valida, _ = self.linha.validar_ordem_producao(op)
            self.assertTrue(valida)
        
        # 4. Simular OPs
        for op in [op1, op2, op3]:
            resultado = self.linha.simular_execucao_op(op)
            self.assertEqual(resultado['status'], 'SUCESSO')
    
    def test_multiplas_ops_mesma_of(self):
        """Testa múltiplas OPs vinculadas à mesma OF"""
        of = self.linha.criar_ordem_fabricacao(25, 1, 23)
        
        ops = [
            self.linha.gerar_ordem_producao(of, 0, 0, 'A', 0),
            self.linha.gerar_ordem_producao(of, 1, 1, 'B', 5),
            self.linha.gerar_ordem_producao(of, 2, 2, 'C', 10),
        ]
        
        self.assertEqual(len(ops), 3)
        for op in ops:
            self.assertIsNotNone(op)
            self.assertTrue(op.startswith("25123"))


class TesteCasosBorda(unittest.TestCase):
    """Testes para casos extremos e bordas"""
    
    def test_recurso_minimo(self):
        """Testa com recurso mínimo (0)"""
        op = OrdemProducao("2512300A00")
        self.assertTrue(op.valido)
        self.assertEqual(op.obter_recursos(), [0])
    
    def test_recurso_maximo_modo_a(self):
        """Testa com recurso máximo modo A"""
        op = OrdemProducao("2512300A26")
        self.assertTrue(op.valido)
    
    def test_ano_zero(self):
        """Testa com ano zero"""
        of = OrdemFabricacao(0, 0, 0)
        valido, _ = of.validar()
        self.assertTrue(valido)
        self.assertEqual(of.gerar_codigo(), "00000")
    
    def test_ano_99(self):
        """Testa com ano máximo"""
        of = OrdemFabricacao(99, 1, 99)
        valido, _ = of.validar()
        self.assertTrue(valido)
        self.assertEqual(of.gerar_codigo(), "99199")
    
    def test_todas_fases_subfases(self):
        """Testa todas as combinações de fase/subfase"""
        linha = LinhaProducao()
        of = linha.criar_ordem_fabricacao(25, 0, 10)
        
        for fase in range(3):
            for subfase in range(3):
                op = linha.gerar_ordem_producao(of, fase, subfase, 'A', 10)
                self.assertIsNotNone(op)


def executar_testes():
    """Executa todos os testes"""
    # Criar suite de testes
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Adicionar testes
    suite.addTests(loader.loadTestsFromTestCase(TesteOrdemFabricacao))
    suite.addTests(loader.loadTestsFromTestCase(TesteOrdemProducao))
    suite.addTests(loader.loadTestsFromTestCase(TesteLinhaProducao))
    suite.addTests(loader.loadTestsFromTestCase(TesteIntegracao))
    suite.addTests(loader.loadTestsFromTestCase(TesteCasosBorda))
    
    # Executar testes
    runner = unittest.TextTestRunner(verbosity=2)
    resultado = runner.run(suite)
    
    # Exibir resumo
    print("\n" + "="*70)
    print("RESUMO DOS TESTES")
    print("="*70)
    print(f"Testes executados: {resultado.testsRun}")
    print(f"Sucessos: {resultado.testsRun - len(resultado.failures) - len(resultado.errors)}")
    print(f"Falhas: {len(resultado.failures)}")
    print(f"Erros: {len(resultado.errors)}")
    print("="*70 + "\n")
    
    return resultado.wasSuccessful()


if __name__ == "__main__":
    sucesso = executar_testes()
    exit(0 if sucesso else 1)

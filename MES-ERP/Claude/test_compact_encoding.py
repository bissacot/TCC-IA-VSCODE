"""
Testes Automatizados - Sistema de Codificação Compacta
Valida todas as funcionalidades e regras do sistema
"""

import sys
from io import StringIO
from Compact_Encoding_System import (
    OrdemFabricacao, 
    OrdemProducao, 
    LinhaProducao
)


class TestadorSistema:
    """Classe para executar testes no sistema de produção."""

    def __init__(self):
        self.testes_passados = 0
        self.testes_falhados = 0
        self.resultados = []

    def assert_igual(self, obtido, esperado, descricao: str):
        """Verifica se dois valores são iguais."""
        if obtido == esperado:
            self.testes_passados += 1
            self.resultados.append(f"✓ {descricao}")
        else:
            self.testes_falhados += 1
            self.resultados.append(f"✗ {descricao} (obtido: {obtido}, esperado: {esperado})")

    def assert_verdadeiro(self, condicao: bool, descricao: str):
        """Verifica se uma condição é verdadeira."""
        if condicao:
            self.testes_passados += 1
            self.resultados.append(f"✓ {descricao}")
        else:
            self.testes_falhados += 1
            self.resultados.append(f"✗ {descricao}")

    def assert_exception(self, funcao, tipo_exception, descricao: str):
        """Verifica se uma exceção é lançada."""
        try:
            funcao()
            self.testes_falhados += 1
            self.resultados.append(f"✗ {descricao} (nenhuma exceção lançada)")
        except tipo_exception:
            self.testes_passados += 1
            self.resultados.append(f"✓ {descricao}")
        except Exception as e:
            self.testes_falhados += 1
            self.resultados.append(f"✗ {descricao} (exceção incorreta: {type(e).__name__})")

    def executar_testes(self):
        """Executa todos os testes."""
        print("\n" + "="*70)
        print("TESTES AUTOMATIZADOS - SISTEMA DE CODIFICAÇÃO COMPACTA")
        print("="*70 + "\n")

        self.testar_ordem_fabricacao()
        self.testar_ordem_producao()
        self.testar_linha_producao()
        self.testar_validacoes()
        self.testar_conversoes()

        self.exibir_relatorio()

    def testar_ordem_fabricacao(self):
        """Testa a classe OrdemFabricacao."""
        print("TESTANDO ORDEM DE FABRICAÇÃO (OF)...")
        
        # Teste 1: Criar OF válida
        of = OrdemFabricacao(25, 1, 12)
        self.assert_igual(of.gerar_codigo(), "25112", "Geração de código OF válido")
        self.assert_igual(of.ano, 25, "Ano armazenado corretamente")
        self.assert_igual(of.tipo_linha, 1, "Tipo de linha armazenado corretamente")
        self.assert_igual(of.codigo_cliente, 12, "Código de cliente armazenado corretamente")
        
        # Teste 2: OF com ano > 99 deve reduzir módulo 100
        of2 = OrdemFabricacao(125, 0, 5)
        self.assert_igual(of2.ano, 25, "Ano reduzido com módulo 100")
        
        # Teste 3: Validações de OF
        self.assert_exception(
            lambda: OrdemFabricacao(-1, 0, 0),
            ValueError,
            "OF rejeita ano negativo"
        )
        self.assert_exception(
            lambda: OrdemFabricacao(25, 2, 0),
            ValueError,
            "OF rejeita tipo de linha inválido"
        )
        self.assert_exception(
            lambda: OrdemFabricacao(25, 0, 100),
            ValueError,
            "OF rejeita cliente fora do range"
        )
        print()

    def testar_ordem_producao(self):
        """Testa a classe OrdemProducao."""
        print("TESTANDO ORDEM DE PRODUÇÃO (OP)...")
        
        # Teste 1: OP válida com modo A
        op_a = OrdemProducao("25112", 0, 0, "A", 5)
        self.assert_igual(op_a.gerar_codigo(), "2511200A05", "Geração de código OP válido")
        self.assert_igual(op_a.obter_recursos(), [5], "Modo A gera 1 recurso")
        
        # Teste 2: OP válida com modo B
        op_b = OrdemProducao("25112", 1, 1, "B", 10)
        self.assert_igual(op_b.obter_recursos(), [10, 11], "Modo B gera 2 recursos acumulativos")
        
        # Teste 3: OP válida com modo C
        op_c = OrdemProducao("25112", 2, 2, "C", 20)
        self.assert_igual(op_c.obter_recursos(), [20, 21, 22], "Modo C gera 3 recursos acumulativos")
        
        # Teste 4: Case insensitive modo
        op_lower = OrdemProducao("25112", 0, 0, "a", 5)
        self.assert_igual(op_lower.modo_recurso, "A", "Modo convertido para maiúscula")
        
        # Teste 5: Simulação retorna dict correto
        sim = op_a.simular_execucao()
        self.assert_verdadeiro("codigo_op" in sim and "recursos_utilizados" in sim, "Simulação retorna dict com campos esperados")
        
        print()

    def testar_validacoes(self):
        """Testa as validações do sistema."""
        print("TESTANDO VALIDAÇÕES...")
        
        # Teste 1: Overflow com modo B
        self.assert_exception(
            lambda: OrdemProducao("25112", 0, 0, "B", 26),
            ValueError,
            "Rejeita modo B com base 26 (overflow)"
        )
        
        # Teste 2: Overflow com modo C
        self.assert_exception(
            lambda: OrdemProducao("25112", 0, 0, "C", 25),
            ValueError,
            "Rejeita modo C com base 25 (overflow)"
        )
        
        # Teste 3: Fase inválida (< 0)
        self.assert_exception(
            lambda: OrdemProducao("25112", -1, 0, "A", 5),
            ValueError,
            "Rejeita fase negativa"
        )
        
        # Teste 4: Fase inválida (> 2)
        self.assert_exception(
            lambda: OrdemProducao("25112", 3, 0, "A", 5),
            ValueError,
            "Rejeita fase > 2"
        )
        
        # Teste 5: Subfase inválida (< 0)
        self.assert_exception(
            lambda: OrdemProducao("25112", 0, -1, "A", 5),
            ValueError,
            "Rejeita subfase negativa"
        )
        
        # Teste 6: Subfase inválida (> 2)
        self.assert_exception(
            lambda: OrdemProducao("25112", 0, 3, "A", 5),
            ValueError,
            "Rejeita subfase > 2"
        )
        
        # Teste 7: Modo inválido
        self.assert_exception(
            lambda: OrdemProducao("25112", 0, 0, "D", 5),
            ValueError,
            "Rejeita modo inválido (D)"
        )
        
        # Teste 8: Recurso base inválido (< 0)
        self.assert_exception(
            lambda: OrdemProducao("25112", 0, 0, "A", -1),
            ValueError,
            "Rejeita recurso base negativo"
        )
        
        # Teste 9: Recurso base inválido (> 26)
        self.assert_exception(
            lambda: OrdemProducao("25112", 0, 0, "A", 27),
            ValueError,
            "Rejeita recurso base > 26"
        )
        
        # Teste 10: Código OF inválido (muito curto)
        self.assert_exception(
            lambda: OrdemProducao("251", 0, 0, "A", 5),
            ValueError,
            "Rejeita código OF muito curto"
        )
        
        print()

    def testar_conversoes(self):
        """Testa as funcionalidades de conversão da LinhaProducao."""
        print("TESTANDO CONVERSÕES...")
        
        linha = LinhaProducao("Linha Teste")
        
        # Teste 1: Criar e validar OF
        of = linha.criar_ordem_fabricacao(25, 1, 12)
        self.assert_igual(of.gerar_codigo(), "25112", "OF criada corretamente na linha")
        
        # Teste 2: Criar e validar OP
        op = linha.criar_ordem_producao("25112", 1, 2, "B", 5)
        self.assert_igual(op.gerar_codigo(), "2511212B05", "OP criada corretamente na linha")
        
        # Teste 3: Validar OP pelo código
        valido, msg = linha.validar_ordem_producao("2511212B05")
        self.assert_verdadeiro(valido, "Validação de OP válida retorna True")
        
        # Teste 4: Rejeitar OP inválida
        valido, msg = linha.validar_ordem_producao("INVALID")
        self.assert_verdadeiro(not valido, "Validação de OP inválida retorna False")
        
        # Teste 5: Converter OP para recursos
        valido, recursos = linha.converter_op_para_recursos("2511212B05")
        self.assert_verdadeiro(valido, "Conversão de OP válida retorna True")
        self.assert_igual(recursos, [5, 6], "Conversão retorna lista correta de recursos")
        
        # Teste 6: Listar estrutura não deve lançar erro
        try:
            estrutura = linha.listar_estrutura()
            self.assert_verdadeiro(
                "ESTRUTURA DA LINHA" in estrutura and "Fases" in estrutura,
                "Listar estrutura retorna conteúdo esperado"
            )
        except Exception as e:
            self.testes_falhados += 1
            self.resultados.append(f"✗ Listar estrutura falhou: {str(e)}")
        
        print()

    def testar_linha_producao(self):
        """Testa a classe LinhaProducao."""
        print("TESTANDO LINHA DE PRODUÇÃO...")
        
        linha = LinhaProducao("Linha Principal", num_recursos=27)
        
        # Teste 1: Inicialização
        self.assert_igual(linha.nome, "Linha Principal", "Nome da linha armazenado")
        self.assert_igual(linha.num_recursos, 27, "Número de recursos correto")
        self.assert_igual(len(linha.recursos), 27, "Recursos inicializados corretamente")
        
        # Teste 2: Criar múltiplas OFs
        of1 = linha.criar_ordem_fabricacao(25, 0, 1)
        of2 = linha.criar_ordem_fabricacao(25, 1, 2)
        self.assert_igual(len(linha.ordens_fabricacao), 2, "Múltiplas OFs registradas")
        
        # Teste 3: Criar múltiplas OPs
        op1 = linha.criar_ordem_producao("25001", 0, 0, "A", 0)
        op2 = linha.criar_ordem_producao("25001", 0, 1, "B", 5)
        op3 = linha.criar_ordem_producao("25001", 1, 2, "C", 20)
        self.assert_igual(len(linha.ordens_producao), 3, "Múltiplas OPs registradas")
        
        # Teste 4: OF inválida não registra
        try:
            linha.criar_ordem_fabricacao(25, 2, 0)
            self.testes_falhados += 1
            self.resultados.append("✗ OF inválida deveria lançar exceção")
        except ValueError:
            self.testes_passados += 1
            self.resultados.append("✓ OF inválida lança exceção e não registra")
        
        print()

    def exibir_relatorio(self):
        """Exibe o relatório final de testes."""
        print("="*70)
        print("RELATÓRIO DE TESTES")
        print("="*70 + "\n")
        
        for resultado in self.resultados:
            print(resultado)
        
        print("\n" + "="*70)
        print(f"TOTAL: {self.testes_passados + self.testes_falhados} testes")
        print(f"✓ PASSADOS: {self.testes_passados}")
        print(f"✗ FALHADOS: {self.testes_falhados}")
        
        if self.testes_falhados == 0:
            print("\n🎉 TODOS OS TESTES PASSARAM!")
        else:
            print(f"\n⚠️  {self.testes_falhados} teste(s) falhado(s).")
        
        print("="*70 + "\n")


def executar_testes_exemplo():
    """Executa exemplos práticos do sistema."""
    print("\n" + "="*70)
    print("EXEMPLOS PRÁTICOS DE USO")
    print("="*70 + "\n")
    
    # Exemplo 1: Criar linhas de produção
    print("1️⃣  CRIANDO LINHA DE PRODUÇÃO:")
    linha = LinhaProducao("Linha Premium")
    print(f"   → {linha}\n")
    
    # Exemplo 2: Criar OF
    print("2️⃣  CRIANDO ORDEM DE FABRICAÇÃO:")
    of = linha.criar_ordem_fabricacao(25, 1, 12)
    print(f"   → {of}\n")
    
    # Exemplo 3: Criar OP com diferentes modos
    print("3️⃣  CRIANDO ORDENS DE PRODUÇÃO:")
    op_a = linha.criar_ordem_producao("25112", 0, 0, "A", 5)
    print(f"   Modo A → {op_a}")
    
    op_b = linha.criar_ordem_producao("25112", 1, 1, "B", 10)
    print(f"   Modo B → {op_b}")
    
    op_c = linha.criar_ordem_producao("25112", 2, 2, "C", 20)
    print(f"   Modo C → {op_c}\n")
    
    # Exemplo 4: Validar OP
    print("4️⃣  VALIDANDO ORDEM DE PRODUÇÃO:")
    codigo = "2511222C20"
    valido, msg = linha.validar_ordem_producao(codigo)
    print(f"   {msg}\n")
    
    # Exemplo 5: Converter OP para recursos
    print("5️⃣  CONVERTENDO OP PARA LISTA DE RECURSOS:")
    valido, recursos = linha.converter_op_para_recursos("2511212B10")
    if valido:
        print(f"   OP: 2511212B10 → Recursos: {recursos}\n")
    
    # Exemplo 6: Simular execução
    print("6️⃣  SIMULANDO EXECUÇÃO DE OP:")
    simulacao = op_b.simular_execucao()
    print(f"   OP: {simulacao['codigo_op']}")
    print(f"   Modo: {simulacao['modo']} ({simulacao['modo_descricao']})")
    print(f"   Recursos: {simulacao['recursos_utilizados']}")
    print(f"   Status: {simulacao['status']}\n")


# Execução principal
if __name__ == "__main__":
    # Executar testes automatizados
    testador = TestadorSistema()
    testador.executar_testes()
    
    # Executar exemplos práticos
    executar_testes_exemplo()
    
    print("✓ Testes concluídos!\n")

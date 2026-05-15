"""
Exemplos de Uso e Testes do Sistema de Produção
Demonstra todas as funcionalidades da plataforma ERP/MES
"""

from sistema_producao import (
    OrdemFabricacao, OrdemProducao, LinhaProducao
)


def exemplo_1_criacao_of():
    """Exemplo 1: Criação de Ordem de Fabricação"""
    print("\n" + "="*70)
    print("EXEMPLO 1: CRIAÇÃO DE ORDEM DE FABRICAÇÃO (OF)")
    print("="*70 + "\n")
    
    # Criar OF: ano=25, tipo=1 (premium), cliente=12
    of = OrdemFabricacao(25, 1, 12)
    
    print(f"Criando OF com parâmetros:")
    print(f"  Ano: 25 (2025)")
    print(f"  Tipo: 1 (Premium)")
    print(f"  Cliente: 12\n")
    
    valido, msg = of.validar()
    print(f"Validação: {msg}")
    print(f"Código gerado: {of.gerar_codigo()}")
    print(f"\n{of}\n")


def exemplo_2_criacao_op_valida():
    """Exemplo 2: Criação de Ordem de Produção Válida"""
    print("\n" + "="*70)
    print("EXEMPLO 2: CRIAÇÃO DE ORDEM DE PRODUÇÃO VÁLIDA")
    print("="*70 + "\n")
    
    # Exemplo: 2512312B05
    # 25123 = OF (ano=25, tipo=1, cliente=23)
    # 1 = Fase 1
    # 2 = Subfase 2
    # B = Modo B (2 recursos)
    # 05 = Recurso base 05
    
    codigo_op = "2512312B05"
    
    print(f"Analisando OP: {codigo_op}\n")
    print("Decomposição do código:")
    print("  25123 = OF (ano=25, tipo=1, cliente=23)")
    print("  1 = Fase 1")
    print("  2 = Subfase 2")
    print("  B = Modo B (2 recursos)")
    print("  05 = Recurso base 05\n")
    
    op = OrdemProducao(codigo_op)
    print(f"Válida: {op.valido}")
    print(f"Mensagem: {op.mensagem_erro}\n")
    print(op)
    print()


def exemplo_3_criacao_op_invalida_overflow():
    """Exemplo 3: OP Inválida - Overflow de Recursos"""
    print("\n" + "="*70)
    print("EXEMPLO 3: OP INVÁLIDA - OVERFLOW DE RECURSOS")
    print("="*70 + "\n")
    
    # Tentativa: 2512325C25 (base=25, modo=C, precisaria de 25,26,27 mas máx é 26)
    codigo_op = "2512325C25"
    
    print(f"Analisando OP: {codigo_op}\n")
    print("Decomposição do código:")
    print("  25123 = OF")
    print("  2 = Fase 2")
    print("  5 = Subfase 5 (INVÁLIDA - máx é 2)")
    
    op = OrdemProducao(codigo_op)
    print(f"\nVálida: {op.valido}")
    print(f"Erro: {op.mensagem_erro}\n")
    
    # Tentar outro overflow: 2512322C25 (base=25, modo=C -> 25,26,27 excede)
    codigo_op = "2512322C25"
    print(f"\nAnalisando OP: {codigo_op}\n")
    print("Decomposição do código:")
    print("  25123 = OF")
    print("  2 = Fase 2")
    print("  2 = Subfase 2")
    print("  C = Modo C (3 recursos)")
    print("  25 = Recurso base 25")
    print("  → Precisaria de recursos 25, 26, 27 (27 > 26 - OVERFLOW!)\n")
    
    op = OrdemProducao(codigo_op)
    print(f"Válida: {op.valido}")
    print(f"Erro: {op.mensagem_erro}\n")


def exemplo_4_modos_recurso():
    """Exemplo 4: Diferentes Modos de Recurso"""
    print("\n" + "="*70)
    print("EXEMPLO 4: DIFERENTES MODOS DE RECURSO")
    print("="*70 + "\n")
    
    of_base = "25123"
    
    # Modo A: 1 recurso
    print("MODO A (1 recurso):")
    print("-" * 70)
    codigo_a = f"{of_base}00A10"
    op_a = OrdemProducao(codigo_a)
    print(f"OP: {codigo_a}")
    print(f"Recursos utilizados: {[f'{r:02d}' for r in op_a.obter_recursos()]}")
    print(f"Quantidade: {len(op_a.obter_recursos())}\n")
    
    # Modo B: 2 recursos
    print("MODO B (2 recursos sequenciais):")
    print("-" * 70)
    codigo_b = f"{of_base}00B10"
    op_b = OrdemProducao(codigo_b)
    print(f"OP: {codigo_b}")
    print(f"Recursos utilizados: {[f'{r:02d}' for r in op_b.obter_recursos()]}")
    print(f"Quantidade: {len(op_b.obter_recursos())}\n")
    
    # Modo C: 3 recursos
    print("MODO C (3 recursos sequenciais):")
    print("-" * 70)
    codigo_c = f"{of_base}00C10"
    op_c = OrdemProducao(codigo_c)
    print(f"OP: {codigo_c}")
    print(f"Recursos utilizados: {[f'{r:02d}' for r in op_c.obter_recursos()]}")
    print(f"Quantidade: {len(op_c.obter_recursos())}\n")


def exemplo_5_linha_producao():
    """Exemplo 5: Linha de Produção Completa"""
    print("\n" + "="*70)
    print("EXEMPLO 5: OPERAÇÕES COM LINHA DE PRODUÇÃO")
    print("="*70 + "\n")
    
    linha = LinhaProducao()
    
    # Criar OFs
    print("1. Criando Ordens de Fabricação...")
    of1 = linha.criar_ordem_fabricacao(25, 0, 10)
    of2 = linha.criar_ordem_fabricacao(25, 1, 15)
    print(f"   ✓ OF1: {of1}")
    print(f"   ✓ OF2: {of2}\n")
    
    # Gerar OPs
    print("2. Gerando Ordens de Produção...")
    op1 = linha.gerar_ordem_producao(of1, 0, 0, 'A', 5)
    op2 = linha.gerar_ordem_producao(of1, 1, 1, 'B', 10)
    op3 = linha.gerar_ordem_producao(of2, 2, 2, 'C', 20)
    print(f"   ✓ OP1: {op1}")
    print(f"   ✓ OP2: {op2}")
    print(f"   ✓ OP3: {op3}\n")
    
    # Validações
    print("3. Validando OPs...")
    for op in [op1, op2, op3]:
        valida, detalhes = linha.validar_ordem_producao(op)
        status = "✓ VÁLIDA" if valida else "✗ INVÁLIDA"
        print(f"   {op}: {status}")
    print()
    
    # Simulações
    print("4. Simulando execução das OPs...")
    for op in [op1, op2, op3]:
        resultado = linha.simular_execucao_op(op)
        recursos = ', '.join([r['id'] for r in resultado['recursos_alocados']])
        print(f"   {op}: {resultado['status']} - Recursos alocados: {recursos}")
    print()
    
    # Listar estrutura
    print("5. Estrutura da Linha:")
    print(linha.listar_estrutura())


def exemplo_6_detalhes_op():
    """Exemplo 6: Detalhes Completos de uma OP"""
    print("\n" + "="*70)
    print("EXEMPLO 6: DETALHES COMPLETOS DE UMA ORDEM DE PRODUÇÃO")
    print("="*70 + "\n")
    
    codigo_op = "2512102B15"
    op = OrdemProducao(codigo_op)
    
    print(f"Analisando OP: {codigo_op}\n")
    
    detalhes = op.obter_detalhes()
    
    print("Detalhes da OP:")
    for chave, valor in detalhes.items():
        if isinstance(valor, list):
            valor_str = f"[{', '.join(valor)}]"
        else:
            valor_str = str(valor)
        print(f"  {chave.replace('_', ' ').title()}: {valor_str}")
    
    print()


def exemplo_7_validacoes():
    """Exemplo 7: Demonstração de Validações"""
    print("\n" + "="*70)
    print("EXEMPLO 7: DEMONSTRAÇÃO DE VALIDAÇÕES")
    print("="*70 + "\n")
    
    casos_teste = [
        ("2512100A05", "OP Válida - Modo A"),
        ("2512100B05", "OP Válida - Modo B"),
        ("25121312C05", "OP Inválida - Formato (11 caracteres)"),
        ("251210XA05", "OP Inválida - Modo X (não existe)"),
        ("2512150A05", "OP Inválida - Subfase 5 (máx 2)"),
        ("251210A05", "OP Inválida - Formato (9 caracteres)"),
        ("2512100A99", "OP Inválida - Recurso 99 (máx 26)"),
        ("2512100C25", "OP Inválida - Overflow (25+2 > 26)"),
    ]
    
    for codigo, descricao in casos_teste:
        op = OrdemProducao(codigo)
        status = "✓ VÁLIDA" if op.valido else "✗ INVÁLIDA"
        print(f"{descricao}")
        print(f"  Código: {codigo}")
        print(f"  Status: {status}")
        print(f"  Mensagem: {op.mensagem_erro}\n")


def main():
    """Executa todos os exemplos"""
    print("\n")
    print("#"*70)
    print("# SISTEMA DE CODIFICAÇÃO COMPACTA PARA LINHA DE PRODUÇÃO ERP/MES")
    print("# Exemplos de Uso e Testes")
    print("#"*70)
    
    exemplo_1_criacao_of()
    exemplo_2_criacao_op_valida()
    exemplo_3_criacao_op_invalida_overflow()
    exemplo_4_modos_recurso()
    exemplo_5_linha_producao()
    exemplo_6_detalhes_op()
    
    # exemplo_7_validacoes() # Descomentar para ver mais validações
    
    print("\n")
    print("#"*70)
    print("# FIM DOS EXEMPLOS")
    print("#"*70)
    print("\n")


if __name__ == "__main__":
    main()

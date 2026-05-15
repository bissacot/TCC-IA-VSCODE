"""
Demonstração Interativa - Casos Reais de Uso
Exemplos práticos de operações em uma linha de produção
"""

from sistema_producao import LinhaProducao
import time


def separator(title=""):
    """Exibe um separador visual"""
    if title:
        print("\n" + "="*70)
        print(f"  {title}")
        print("="*70 + "\n")
    else:
        print("\n" + "-"*70 + "\n")


def pause():
    """Pausa para o usuário ler"""
    input("Pressione Enter para continuar...")


def demo_cenario_1_producao_simples():
    """
    CENÁRIO 1: Produção Simples
    Pequeno lote de um cliente premium
    """
    separator("CENÁRIO 1: PRODUÇÃO SIMPLES")
    
    print("📍 SITUAÇÃO:")
    print("  Uma indústria recebe pedido de um cliente premium")
    print("  Necessita fabricar 5 produtos em uma sequência simples\n")
    
    linha = LinhaProducao()
    
    print("1️⃣  CRIAR ORDEM DE FABRICAÇÃO")
    print("-" * 70)
    print("Dados do pedido:")
    print("  • Ano: 25 (2025)")
    print("  • Tipo: 1 (Premium - alta prioridade)")
    print("  • Cliente: 42\n")
    
    of = linha.criar_ordem_fabricacao(25, 1, 42)
    print(f"✓ OF gerada: {of}\n")
    
    print("2️⃣  ESTRUTURAR A PRODUÇÃO")
    print("-" * 70)
    print("Sequência de produção planejada:\n")
    
    sequencia = [
        (0, 0, 'A', 3),   # Fase 0, Subfase 0, Modo A, Recurso 3
        (0, 1, 'A', 8),   # Fase 0, Subfase 1, Modo A, Recurso 8
        (1, 0, 'B', 12),  # Fase 1, Subfase 0, Modo B, Recurso 12
        (1, 2, 'A', 15),  # Fase 1, Subfase 2, Modo A, Recurso 15
        (2, 0, 'A', 20),  # Fase 2, Subfase 0, Modo A, Recurso 20
    ]
    
    ops_criadas = []
    for i, (fase, subfase, modo, recurso) in enumerate(sequencia, 1):
        op = linha.gerar_ordem_producao(of, fase, subfase, modo, recurso)
        ops_criadas.append(op)
        print(f"  {i}. OP: {op}")
        print(f"     Fase {fase} → Subfase {subfase} | Modo {modo} | Recurso {recurso:02d}")
    
    print()
    
    print("3️⃣  EXECUTAR E MONITORAR")
    print("-" * 70)
    print("Simulando execução de cada etapa:\n")
    
    for i, op in enumerate(ops_criadas, 1):
        resultado = linha.simular_execucao_op(op)
        recursos = ', '.join([r['id'] for r in resultado['recursos_alocados']])
        print(f"  {i}. OP {op}: {resultado['status']}")
        print(f"     Recursos alocados: {recursos}")
    
    print()
    print("✅ PRODUÇÃO COMPLETADA COM SUCESSO")
    
    pause()


def demo_cenario_2_multiplos_clientes():
    """
    CENÁRIO 2: Múltiplos Clientes
    Processo paralelo de múltiplas ordens
    """
    separator("CENÁRIO 2: MÚLTIPLOS CLIENTES EM PARALELO")
    
    print("📍 SITUAÇÃO:")
    print("  Fábrica atende 3 clientes simultaneamente")
    print("  Cada um com diferentes tipos de produção\n")
    
    linha = LinhaProducao()
    
    print("1️⃣  CRIAR ORDENS DE FABRICAÇÃO")
    print("-" * 70)
    
    clientes = [
        (25, 0, 10, "Normal - Cliente 10"),
        (25, 1, 25, "Premium - Cliente 25"),
        (25, 0, 15, "Normal - Cliente 15"),
    ]
    
    ofs = []
    for ano, tipo, cliente, descricao in clientes:
        of = linha.criar_ordem_fabricacao(ano, tipo, cliente)
        ofs.append(of)
        tipo_str = "Premium" if tipo else "Normal"
        print(f"✓ OF: {of} | {descricao}")
    
    print()
    
    print("2️⃣  GERAR ORDENS DE PRODUÇÃO")
    print("-" * 70)
    print("Diferentes configurações por cliente:\n")
    
    for of, descricao in zip(ofs, [d[3] for d in clientes]):
        print(f"{descricao}")
        
        if "Normal" in descricao and "10" in descricao:
            ops = [
                linha.gerar_ordem_producao(of, 0, 0, 'A', 2),
                linha.gerar_ordem_producao(of, 1, 1, 'B', 5),
            ]
        elif "Premium" in descricao:
            ops = [
                linha.gerar_ordem_producao(of, 0, 0, 'C', 0),
                linha.gerar_ordem_producao(of, 1, 2, 'B', 10),
                linha.gerar_ordem_producao(of, 2, 0, 'A', 20),
            ]
        else:
            ops = [
                linha.gerar_ordem_producao(of, 0, 1, 'B', 8),
            ]
        
        for op in ops:
            print(f"  - {op}")
        print()
    
    print("3️⃣  SIMULAR PROCESSAMENTO PARALELO")
    print("-" * 70)
    print("Simulando fila de processos:\n")
    
    for i, sim in enumerate(linha.simulacoes, 1):
        if sim['status'] == 'SUCESSO':
            recursos = ', '.join([r['id'] for r in sim['recursos_alocados']])
            print(f"  [{i:02d}] OP {sim['op']}: {recursos}")
    
    print()
    print(f"✅ Total de {len(linha.simulacoes)} ordens processadas")
    
    pause()


def demo_cenario_3_validacoes_erros():
    """
    CENÁRIO 3: Tratamento de Erros e Validações
    Demonstra o tratamento de casos problemáticos
    """
    separator("CENÁRIO 3: VALIDAÇÃO E TRATAMENTO DE ERROS")
    
    print("📍 SITUAÇÃO:")
    print("  Operador tenta criar ordens com dados problemáticos")
    print("  Sistema valida e reporta erros\n")
    
    linha = LinhaProducao()
    
    # Criar uma OF válida para referenciar
    of_valida = linha.criar_ordem_fabricacao(25, 1, 23)
    print(f"OF válida criada para referência: {of_valida}\n")
    
    print("1️⃣  TENTAR CRIAR OP COM SUBFASE INVÁLIDA")
    print("-" * 70)
    codigo = f"{of_valida}05A10"  # Subfase 5 é inválida
    valida, detalhes = linha.validar_ordem_producao(codigo)
    print(f"Tentativa: {codigo}")
    print(f"Status: {'✓ VÁLIDA' if valida else '✗ INVÁLIDA'}")
    print(f"Erro: {detalhes['mensagem']}\n")
    
    print("2️⃣  TENTAR CRIAR OP COM OVERFLOW DE RECURSOS")
    print("-" * 70)
    codigo = f"{of_valida}22C25"  # Base 25 com Modo C = 25,26,27 (overflow!)
    valida, detalhes = linha.validar_ordem_producao(codigo)
    print(f"Tentativa: {codigo}")
    print(f"  Base: 25, Modo C → Tentaria usar: 25, 26, 27")
    print(f"Status: {'✓ VÁLIDA' if valida else '✗ INVÁLIDA'}")
    print(f"Erro: {detalhes['mensagem']}\n")
    
    print("3️⃣  TENTAR CRIAR OP COM MODO INVÁLIDO")
    print("-" * 70)
    codigo = f"{of_valida}00X10"  # Modo X não existe
    valida, detalhes = linha.validar_ordem_producao(codigo)
    print(f"Tentativa: {codigo}")
    print(f"Status: {'✓ VÁLIDA' if valida else '✗ INVÁLIDA'}")
    print(f"Erro: {detalhes['mensagem']}\n")
    
    print("4️⃣  CRIAR OP VÁLIDA (PARA COMPARAÇÃO)")
    print("-" * 70)
    codigo = f"{of_valida}00B15"  # Válida
    valida, detalhes = linha.validar_ordem_producao(codigo)
    print(f"Tentativa: {codigo}")
    print(f"Status: {'✓ VÁLIDA' if valida else '✗ INVÁLIDA'}")
    if valida:
        print(f"Recursos utilizados: {', '.join(detalhes['recursos_utilizados'])}")
    print()
    
    print("✅ VALIDAÇÕES FUNCIONANDO CORRETAMENTE")
    
    pause()


def demo_cenario_4_analise_recursos():
    """
    CENÁRIO 4: Análise de Alocação de Recursos
    Demonstra como recursos são alocados e utilizados
    """
    separator("CENÁRIO 4: ALOCAÇÃO E ANÁLISE DE RECURSOS")
    
    print("📍 SITUAÇÃO:")
    print("  Gerente quer entender como os recursos são utilizados\n")
    
    linha = LinhaProducao()
    
    print("1️⃣  VISUALIZAR ESTRUTURA DA LINHA")
    print("-" * 70)
    print(linha.listar_estrutura())
    
    print("2️⃣  COMPARAR DIFERENTES MODOS")
    print("-" * 70)
    print("Alocação de recursos para diferentes modos:\n")
    
    of = linha.criar_ordem_fabricacao(25, 0, 10)
    
    modos_teste = [
        ('A', 5),
        ('B', 5),
        ('C', 5),
    ]
    
    for modo, recurso_base in modos_teste:
        op = linha.gerar_ordem_producao(of, 0, 0, modo, recurso_base)
        valida, detalhes = linha.validar_ordem_producao(op)
        recursos = ', '.join(detalhes['recursos_utilizados'])
        print(f"Modo {modo}: Recurso {recurso_base:02d}")
        print(f"  → Utiliza: [{recursos}]")
        print(f"  → Quantidade: {detalhes['quantidade_recursos']}")
        print()
    
    print("3️⃣  CASOS LIMITANTES")
    print("-" * 70)
    print("Situações que chegam ao limite do sistema:\n")
    
    print("Caso 1: Máximo com Modo A")
    op = linha.gerar_ordem_producao(of, 0, 0, 'A', 26)
    valida, _ = linha.validar_ordem_producao(op)
    print(f"  OP: {op} → {'✓ VÁLIDA' if valida else '✗ INVÁLIDA'}")
    
    print("\nCaso 2: Máximo com Modo B")
    op = linha.gerar_ordem_producao(of, 0, 0, 'B', 25)
    valida, _ = linha.validar_ordem_producao(op)
    print(f"  OP: {op} → {'✓ VÁLIDA' if valida else '✗ INVÁLIDA'}")
    
    print("\nCaso 3: Seria overflow com Modo C")
    op_codigo = f"{of}00C25"
    op = linha.gerar_ordem_producao(of, 0, 0, 'C', 25)
    valida, detalhes = linha.validar_ordem_producao(op_codigo)
    print(f"  OP: {op_codigo} → {'✓ VÁLIDA' if valida else '✗ INVÁLIDA'}")
    if not valida:
        print(f"  Motivo: {detalhes['mensagem']}")
    print()
    
    print("✅ ANÁLISE DE RECURSOS COMPLETA")
    
    pause()


def demo_cenario_5_rastreamento():
    """
    CENÁRIO 5: Rastreamento e Histórico
    Demonstra capacidade de rastreamento
    """
    separator("CENÁRIO 5: RASTREAMENTO E HISTÓRICO")
    
    print("📍 SITUAÇÃO:")
    print("  Auditor quer rastrear todas as operações realizadas\n")
    
    linha = LinhaProducao()
    
    print("1️⃣  EXECUTAR SÉRIE DE OPERAÇÕES")
    print("-" * 70)
    
    # Criar múltiplas OFs
    ofs = []
    for cliente in [10, 15, 20, 25]:
        of = linha.criar_ordem_fabricacao(25, 1 if cliente > 17 else 0, cliente)
        ofs.append(of)
        print(f"✓ OF criada: {of}")
    
    print()
    
    # Gerar múltiplas OPs
    print("2️⃣  GERAR MÚLTIPLAS ORDENS DE PRODUÇÃO")
    print("-" * 70)
    
    ops = []
    for i, of in enumerate(ofs):
        for fase in range(3):
            op = linha.gerar_ordem_producao(of, fase, 0, 'A', 5)
            ops.append(op)
            if i == 0 and fase < 2:  # Mostrar exemplos
                print(f"✓ OP gerada: {op}")
    
    print(f"... e mais {len(ops) - 2} OPs\n")
    
    # Simular execução
    print("3️⃣  SIMULAR EXECUÇÃO")
    print("-" * 70)
    
    for op in ops[:5]:  # Mostrar primeiras 5
        resultado = linha.simular_execucao_op(op)
        print(f"  {op}: {resultado['status']}")
    
    print(f"... e mais {len(ops) - 5} simulações\n")
    
    print("4️⃣  HISTÓRICO COMPLETO")
    print("-" * 70)
    print(f"Total de simulações: {len(linha.simulacoes)}")
    print(f"Total de OPs processadas: {len(linha.ordens_producao)}")
    print(f"Total de OFs criadas: {len(linha.ordens_fabricacao)}")
    print()
    
    print("5️⃣  ÚLTIMAS OPERAÇÕES")
    print("-" * 70)
    
    for i, sim in enumerate(linha.simulacoes[-5:], 1):
        recursos = ', '.join([r['id'] for r in sim['recursos_alocados']]) \
                   if sim['recursos_alocados'] else 'N/A'
        print(f"  {i}. {sim['op']}: {sim['status']} ({recursos})")
    
    print()
    print("✅ RASTREAMENTO DISPONÍVEL PARA AUDITORIA")
    
    pause()


def menu_principal():
    """Menu principal de demonstrações"""
    
    while True:
        separator("DEMONSTRAÇÃO INTERATIVA - CASOS REAIS")
        
        print("Escolha um cenário para demonstração:\n")
        print("1. 📦 Produção Simples")
        print("   Pequeno lote de um cliente premium")
        print()
        print("2. 🏭 Múltiplos Clientes em Paralelo")
        print("   Processamento de várias ordens simultaneamente")
        print()
        print("3. ⚠️  Validação e Tratamento de Erros")
        print("   Como o sistema trata dados inválidos")
        print()
        print("4. 📊 Análise de Alocação de Recursos")
        print("   Compreender utilização de recursos")
        print()
        print("5. 📋 Rastreamento e Histórico")
        print("   Auditoria de operações")
        print()
        print("0. Sair")
        print()
        
        opcao = input("Escolha (0-5): ").strip()
        
        if opcao == '1':
            demo_cenario_1_producao_simples()
        elif opcao == '2':
            demo_cenario_2_multiplos_clientes()
        elif opcao == '3':
            demo_cenario_3_validacoes_erros()
        elif opcao == '4':
            demo_cenario_4_analise_recursos()
        elif opcao == '5':
            demo_cenario_5_rastreamento()
        elif opcao == '0':
            print("\n✅ Obrigado por usar a demonstração! Até logo.\n")
            break
        else:
            print("\n❌ Opção inválida. Tente novamente.\n")


if __name__ == "__main__":
    print("\n")
    print("#"*70)
    print("# DEMONSTRAÇÃO INTERATIVA - SISTEMA ERP/MES")
    print("# Casos Reais de Uso Industrial")
    print("#"*70)
    
    menu_principal()

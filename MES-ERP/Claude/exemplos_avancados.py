"""
Exemplos Avançados - Sistema de Codificação Compacta
Demonstra técnicas avançadas e extensões do sistema
"""

from Compact_Encoding_System import (
    OrdemFabricacao, 
    OrdemProducao, 
    LinhaProducao
)
from typing import List, Dict
from datetime import datetime


# ============================================================================
# EXEMPLO 1: Simulação de uma Jornada de Produção Completa
# ============================================================================

def simular_jornada_producao():
    """Simula uma jornada completa de produção."""
    print("\n" + "="*70)
    print("EXEMPLO 1: JORNADA COMPLETA DE PRODUÇÃO")
    print("="*70 + "\n")
    
    # Criar linha
    linha = LinhaProducao("Linha Principal")
    print(f"✓ Linha criada: {linha.nome}\n")
    
    # Criar ofertas de clientes
    clientes = [
        {"nome": "ClienteA", "tipo": 0, "cod": 1},
        {"nome": "ClienteB", "tipo": 1, "cod": 2},
        {"nome": "ClienteC", "tipo": 0, "cod": 3},
    ]
    
    print("CRIANDO ORDENS DE FABRICAÇÃO:")
    ordens_fabricacao = {}
    for cliente in clientes:
        of = linha.criar_ordem_fabricacao(25, cliente["tipo"], cliente["cod"])
        ordens_fabricacao[cliente["nome"]] = of.gerar_codigo()
        print(f"  ✓ {cliente['nome']}: {of.gerar_codigo()}")
    print()
    
    # Criar plano de produção
    print("CRIANDO PLANO DE PRODUÇÃO:")
    plano = [
        ("ClienteA", 0, 0, "A", 0),
        ("ClienteA", 0, 1, "B", 2),
        ("ClienteB", 1, 0, "C", 10),
        ("ClienteB", 1, 1, "A", 15),
        ("ClienteC", 2, 0, "B", 20),
        ("ClienteC", 2, 1, "C", 24),
    ]
    
    for cliente, fase, subfase, modo, base in plano:
        of_code = ordens_fabricacao[cliente]
        op = linha.criar_ordem_producao(of_code, fase, subfase, modo, base)
        recursos = op.obter_recursos()
        print(f"  ✓ OP {op.gerar_codigo()} → Recursos: {recursos}")
    print()
    
    return linha


# ============================================================================
# EXEMPLO 2: Análise de Utilização de Recursos
# ============================================================================

def analisar_utilizacao_recursos(linha: LinhaProducao) -> Dict:
    """Analisa quais recursos estão sendo utilizados."""
    print("\n" + "="*70)
    print("EXEMPLO 2: ANÁLISE DE UTILIZAÇÃO DE RECURSOS")
    print("="*70 + "\n")
    
    # Contar uso de cada recurso
    uso_recursos = {}
    ops_por_recurso = {}
    
    for op in linha.ordens_producao:
        recursos = op.obter_recursos()
        for recurso in recursos:
            uso_recursos[recurso] = uso_recursos.get(recurso, 0) + 1
            if recurso not in ops_por_recurso:
                ops_por_recurso[recurso] = []
            ops_por_recurso[recurso].append(op.gerar_codigo())
    
    # Exibir análise
    print("RECURSOS MAIS UTILIZADOS:\n")
    for recurso in sorted(uso_recursos.keys()):
        count = uso_recursos[recurso]
        ops = ops_por_recurso[recurso]
        barra = "█" * count
        print(f"  Recurso {recurso:02d}: {barra} ({count}x)")
        print(f"    OPs: {', '.join(ops[:3])}" + ("..." if len(ops) > 3 else ""))
    
    print(f"\nTOTAL DE RECURSOS ATIVOS: {len(uso_recursos)}/27")
    print(f"TAXA DE OCUPAÇÃO: {(len(uso_recursos)/27)*100:.1f}%\n")
    
    return uso_recursos


# ============================================================================
# EXEMPLO 3: Validação de Lote de OPs
# ============================================================================

def validar_lote_ops():
    """Valida um lote de códigos OP."""
    print("\n" + "="*70)
    print("EXEMPLO 3: VALIDAÇÃO DE LOTE DE OPs")
    print("="*70 + "\n")
    
    linha = LinhaProducao("Linha Validação")
    
    # Lote para validar
    lote = [
        "2500100A00",  # Válida
        "2500100B05",  # Válida
        "2500100C20",  # Válida
        "2500100A27",  # Inválida: recurso > 26
        "2500100B26",  # Inválida: overflow
        "INVALID123",  # Inválida: formato
        "2500103A10",  # Inválida: subfase > 2
        "2500100D10",  # Inválida: modo D não existe
    ]
    
    print("VALIDANDO LOTE:\n")
    validadas = 0
    rejeitadas = 0
    
    for op_code in lote:
        valida, msg = linha.validar_ordem_producao(op_code)
        if valida:
            print(f"  ✓ {op_code}: {msg}")
            validadas += 1
        else:
            print(f"  ✗ {op_code}: {msg}")
            rejeitadas += 1
    
    print(f"\nRESULTADO: {validadas} válidas, {rejeitadas} rejeitadas\n")


# ============================================================================
# EXEMPLO 4: Gerar Matriz de Compatibilidade
# ============================================================================

def gerar_matriz_compatibilidade():
    """Analisa compatibilidade de modos e recursos."""
    print("\n" + "="*70)
    print("EXEMPLO 4: MATRIZ DE COMPATIBILIDADE MODO/RECURSO")
    print("="*70 + "\n")
    
    print("RECURSOS MÁXIMOS POR MODO:\n")
    print("Modo  | Recursos | Base Máxima")
    print("------|----------|------------")
    
    modos = ['A', 'B', 'C']
    num_recursos_modo = {'A': 1, 'B': 2, 'C': 3}
    
    for modo in modos:
        num = num_recursos_modo[modo]
        base_max = 26 - num + 1
        recursos = f"1 até {num}"
        print(f"  {modo}   | {recursos:^8} | {base_max:^10}")
    
    print(f"\n")
    print("EXEMPLOS DE ACUMULAÇÃO:\n")
    
    exemplos = [
        (5, 'A'), (5, 'B'), (5, 'C'),
        (24, 'A'), (24, 'B'), (24, 'C'),
        (25, 'A'), (25, 'B'),
        (26, 'A'),
    ]
    
    print("Base | Modo | Recursos Resultantes | Status")
    print("-----|------|----------------------|--------")
    
    for base, modo in exemplos:
        try:
            op_teste = OrdemProducao("00000", 0, 0, modo, base)
            recursos = op_teste.obter_recursos()
            status = "✓"
        except ValueError:
            recursos = "INVÁLIDO"
            status = "✗"
        
        print(f" {base:2d}  |  {modo}   | {str(recursos):^20} | {status}")
    
    print()


# ============================================================================
# EXEMPLO 5: Gerar Relatório de Produção
# ============================================================================

def gerar_relatorio_producao(linha: LinhaProducao):
    """Gera um relatório completo de produção."""
    print("\n" + "="*70)
    print("EXEMPLO 5: RELATÓRIO DE PRODUÇÃO")
    print("="*70 + "\n")
    
    print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
    
    # Estatísticas gerais
    print("ESTATÍSTICAS GERAIS:")
    print(f"  Linha: {linha.nome}")
    print(f"  Recursos totais: {linha.num_recursos}")
    print(f"  OFs criadas: {len(linha.ordens_fabricacao)}")
    print(f"  OPs criadas: {len(linha.ordens_producao)}\n")
    
    # Distribuição por fase
    print("DISTRIBUIÇÃO POR FASE:")
    fases = {}
    for op in linha.ordens_producao:
        fase = op.fase
        fases[fase] = fases.get(fase, 0) + 1
    
    for fase in sorted(fases.keys()):
        count = fases[fase]
        print(f"  Fase {fase}: {count} OPs")
    print()
    
    # Distribuição por modo
    print("DISTRIBUIÇÃO POR MODO:")
    modos = {}
    for op in linha.ordens_producao:
        modo = op.modo_recurso
        modos[modo] = modos.get(modo, 0) + 1
    
    for modo in sorted(modos.keys()):
        count = modos[modo]
        print(f"  Modo {modo}: {count} OPs")
    print()
    
    # OPs ativas
    print("ORDENS DE PRODUÇÃO (Resumo):")
    for i, op in enumerate(linha.ordens_producao[:5], 1):
        print(f"  {i}. {op.gerar_codigo()} - {op.modo_recurso} - {op.obter_recursos()}")
    
    if len(linha.ordens_producao) > 5:
        print(f"  ... e mais {len(linha.ordens_producao) - 5}\n")
    else:
        print()


# ============================================================================
# EXEMPLO 6: Extensão - Classe CustomizadaOrdemProducao
# ============================================================================

class OrdemProducaoComPrioridade(OrdemProducao):
    """Extensão da OP com prioridade e SLA."""
    
    def __init__(self, codigo_of: str, fase: int, subfase: int, 
                 modo_recurso: str, recurso_base: int, 
                 prioridade: int = 5, sla_horas: int = 24):
        """
        Args:
            prioridade: 1-10 (1=baixa, 10=crítica)
            sla_horas: Horas para completar
        """
        super().__init__(codigo_of, fase, subfase, modo_recurso, recurso_base)
        self.prioridade = prioridade
        self.sla_horas = sla_horas
        
    def obter_info_extendida(self) -> Dict:
        """Retorna informações extendidas da OP."""
        return {
            'codigo': self.gerar_codigo(),
            'recursos': self.obter_recursos(),
            'prioridade': self.prioridade,
            'nivel_prioridade': self._nivel_prioridade(),
            'sla_horas': self.sla_horas
        }
    
    def _nivel_prioridade(self) -> str:
        """Retorna nível de prioridade em texto."""
        if self.prioridade >= 9:
            return "CRÍTICA"
        elif self.prioridade >= 7:
            return "Alta"
        elif self.prioridade >= 4:
            return "Normal"
        else:
            return "Baixa"


def exemplo_extensao():
    """Demonstra uso de extensão customizada."""
    print("\n" + "="*70)
    print("EXEMPLO 6: EXTENSÃO - OP COM PRIORIDADE")
    print("="*70 + "\n")
    
    # Criar OPs com prioridade
    op_normal = OrdemProducaoComPrioridade("25001", 0, 0, "A", 5, 
                                           prioridade=5, sla_horas=48)
    op_alta = OrdemProducaoComPrioridade("25001", 1, 1, "B", 10,
                                        prioridade=9, sla_horas=12)
    
    print("ORDENS COM PRIORIDADE:\n")
    
    for op in [op_normal, op_alta]:
        info = op.obter_info_extendida()
        print(f"  OP: {info['codigo']}")
        print(f"    Prioridade: [{info['prioridade']}/10] {info['nivel_prioridade']}")
        print(f"    SLA: {info['sla_horas']}h")
        print(f"    Recursos: {info['recursos']}\n")


# ============================================================================
# EXEMPLO 7: Simulação de Cenários
# ============================================================================

def simular_cenarios():
    """Simula diferentes cenários de produção."""
    print("\n" + "="*70)
    print("EXEMPLO 7: SIMULAÇÃO DE CENÁRIOS")
    print("="*70 + "\n")
    
    cenarios = {
        "Produção Leve": [
            ("25001", 0, 0, "A", 0),
            ("25001", 0, 1, "A", 5),
            ("25001", 0, 2, "A", 10),
        ],
        "Produção Média": [
            ("25002", 0, 0, "B", 0),
            ("25002", 1, 1, "B", 5),
            ("25002", 2, 2, "B", 15),
        ],
        "Produção Pesada": [
            ("25003", 0, 0, "C", 0),
            ("25003", 1, 1, "C", 10),
            ("25003", 2, 2, "C", 20),
        ],
    }
    
    for nome_cenario, ops_config in cenarios.items():
        print(f"\n{nome_cenario}:")
        print("─" * 50)
        
        total_recursos = 0
        for of, fase, subfase, modo, base in ops_config:
            try:
                op = OrdemProducao(of, fase, subfase, modo, base)
                recursos = op.obter_recursos()
                total_recursos += len(recursos)
                print(f"  {op.gerar_codigo()}: {recursos}")
            except ValueError as e:
                print(f"  ERRO: {e}")
        
        print(f"  Total de recursos: {total_recursos}")


# ============================================================================
# MAIN: Executar Todos os Exemplos
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("EXEMPLOS AVANÇADOS - SISTEMA DE CODIFICAÇÃO COMPACTA")
    print("="*70)
    
    # Exemplo 1
    linha = simular_jornada_producao()
    
    # Exemplo 2
    analisar_utilizacao_recursos(linha)
    
    # Exemplo 3
    validar_lote_ops()
    
    # Exemplo 4
    gerar_matriz_compatibilidade()
    
    # Exemplo 5
    gerar_relatorio_producao(linha)
    
    # Exemplo 6
    exemplo_extensao()
    
    # Exemplo 7
    simular_cenarios()
    
    print("\n" + "="*70)
    print("✓ Todos os exemplos foram executados!")
    print("="*70 + "\n")

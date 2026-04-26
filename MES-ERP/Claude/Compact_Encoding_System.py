"""
Sistema de Codificação Compacta para Linha de Produção
Inspirado em sistemas industriais ERP/MES
Autor: Sistema de Produção
Data: 2026
"""

from datetime import datetime
from typing import List, Tuple, Optional


class OrdemFabricacao:
    """
    Representa uma Ordem de Fabricação (OF)
    Formato: YYTCC
    - YY: ano (00–99)
    - T: tipo da linha (0=normal, 1=premium)
    - CC: código do cliente (00–99)
    """

    def __init__(self, ano: int, tipo_linha: int, codigo_cliente: int):
        """
        Inicializa uma Ordem de Fabricação.
        
        Args:
            ano: Ano (00-99, ou qualquer inteiro que será reduzido mod 100)
            tipo_linha: Tipo da linha (0=normal, 1=premium)
            codigo_cliente: Código do cliente (00-99)
        """
        if ano < 0:
            raise ValueError(f"Ano inválido: {ano}. Deve ser maior ou igual a 0")
        self.ano = ano % 100  # Reduz para 00-99
        self.tipo_linha = tipo_linha
        self.codigo_cliente = codigo_cliente
        self.data_criacao = datetime.now()
        self.validar()

    def validar(self) -> bool:
        """Valida os parâmetros da OF."""
        if self.tipo_linha not in [0, 1]:
            raise ValueError(f"Tipo de linha inválido: {self.tipo_linha}. Deve ser 0 (normal) ou 1 (premium)")
        if not (0 <= self.codigo_cliente <= 99):
            raise ValueError(f"Código do cliente inválido: {self.codigo_cliente}. Deve estar entre 0 e 99")
        return True

    def gerar_codigo(self) -> str:
        """Gera o código da OF no formato YYTCC."""
        return f"{self.ano:02d}{self.tipo_linha}{self.codigo_cliente:02d}"

    def __str__(self) -> str:
        tipo = "Premium" if self.tipo_linha == 1 else "Normal"
        return f"OF {self.gerar_codigo()} - Tipo: {tipo}, Cliente: {self.codigo_cliente:02d}, Data: {self.data_criacao.strftime('%Y-%m-%d %H:%M:%S')}"


class OrdemProducao:
    """
    Representa uma Ordem de Produção (OP)
    Estrutura: YYTCC + F + SF + M + RB
    - YYTCC: referência da OF
    - F: fase (0-2)
    - SF: subfase (0-2)
    - M: modo de recurso (A, B, C)
    - RB: recurso base (00-26)
    """

    def __init__(self, codigo_of: str, fase: int, subfase: int, modo_recurso: str, recurso_base: int):
        """
        Inicializa uma Ordem de Produção.
        
        Args:
            codigo_of: Código da OF (YYTCC)
            fase: Fase (0-2)
            subfase: Subfase (0-2)
            modo_recurso: Modo de recurso (A, B, C)
            recurso_base: Recurso base (00-26)
        """
        self.codigo_of = codigo_of
        self.fase = fase
        self.subfase = subfase
        self.modo_recurso = modo_recurso.upper()
        self.recurso_base = recurso_base
        self.data_criacao = datetime.now()
        self.status = "Criada"
        self.validar()

    def validar(self) -> bool:
        """Valida a Ordem de Produção."""
        # Validar código OF
        if not self._validar_codigo_of():
            raise ValueError(f"Código OF inválido: {self.codigo_of}")
        
        # Validar fase e subfase
        if not (0 <= self.fase <= 2):
            raise ValueError(f"Fase inválida: {self.fase}. Deve estar entre 0 e 2")
        
        if not (0 <= self.subfase <= 2):
            raise ValueError(f"Subfase inválida: {self.subfase}. Deve estar entre 0 e 2")
        
        # Validar modo de recurso
        if self.modo_recurso not in ['A', 'B', 'C']:
            raise ValueError(f"Modo de recurso inválido: {self.modo_recurso}. Deve ser A, B ou C")
        
        # Validar recurso base
        if not (0 <= self.recurso_base <= 26):
            raise ValueError(f"Recurso base inválido: {self.recurso_base}. Deve estar entre 0 e 26")
        
        # Validar overflow de recursos
        if not self._validar_overflow():
            raise ValueError(f"Overflow de recursos: base {self.recurso_base} com modo {self.modo_recurso} ultrapassaria 26")
        
        return True

    def _validar_codigo_of(self) -> bool:
        """Valida o formato do código OF (YYTCC)."""
        if len(self.codigo_of) != 5:
            return False
        try:
            int(self.codigo_of)
            return True
        except ValueError:
            return False

    def _validar_overflow(self) -> bool:
        """Verifica se há overflow de recursos."""
        num_recursos = self._obter_numero_recursos()
        recurso_maximo = self.recurso_base + num_recursos - 1
        return recurso_maximo <= 26

    def _obter_numero_recursos(self) -> int:
        """Retorna o número de recursos baseado no modo."""
        modo_recursos = {'A': 1, 'B': 2, 'C': 3}
        return modo_recursos.get(self.modo_recurso, 1)

    def gerar_codigo(self) -> str:
        """Gera o código completo da OP."""
        return f"{self.codigo_of}{self.fase}{self.subfase}{self.modo_recurso}{self.recurso_base:02d}"

    def obter_recursos(self) -> List[int]:
        """
        Gera a lista de recursos utilizados.
        Acumulação sequencial baseada no modo.
        """
        num_recursos = self._obter_numero_recursos()
        recursos = [self.recurso_base + i for i in range(num_recursos)]
        return recursos

    def simular_execucao(self) -> dict:
        """Simula a execução da OP fornecendo informações detalhadas."""
        recursos = self.obter_recursos()
        modo_descricao = {
            'A': '1 recurso',
            'B': '2 recursos (acumulativo)',
            'C': '3 recursos (acumulativo)'
        }
        
        return {
            'codigo_op': self.gerar_codigo(),
            'fase': self.fase,
            'subfase': self.subfase,
            'modo': self.modo_recurso,
            'modo_descricao': modo_descricao[self.modo_recurso],
            'recurso_base': self.recurso_base,
            'recursos_utilizados': recursos,
            'numero_recursos': len(recursos),
            'status': self.status
        }

    def __str__(self) -> str:
        recursos = ', '.join(map(str, self.obter_recursos()))
        return f"OP {self.gerar_codigo()} - Fase: {self.fase}.{self.subfase}, Modo: {self.modo_recurso}, Recursos: [{recursos}], Status: {self.status}"


class LinhaProducao:
    """
    Representa uma Linha de Produção completa com gerenciamento de recursos e ordens.
    """

    def __init__(self, nome: str, num_recursos: int = 27):
        """
        Inicializa uma Linha de Produção.
        
        Args:
            nome: Nome da linha
            num_recursos: Número total de recursos disponíveis (padrão: 27 = 0-26)
        """
        self.nome = nome
        self.num_recursos = num_recursos
        self.recursos = {i: {'disponivel': True, 'op_em_uso': None} for i in range(num_recursos)}
        self.ordens_producao: List[OrdemProducao] = []
        self.ordens_fabricacao: List[OrdemFabricacao] = []
        self.data_criacao = datetime.now()

    def criar_ordem_fabricacao(self, ano: int, tipo_linha: int, codigo_cliente: int) -> OrdemFabricacao:
        """Cria e registra uma nova Ordem de Fabricação."""
        try:
            of = OrdemFabricacao(ano, tipo_linha, codigo_cliente)
            self.ordens_fabricacao.append(of)
            return of
        except ValueError as e:
            raise ValueError(f"Erro ao criar OF: {str(e)}")

    def criar_ordem_producao(self, codigo_of: str, fase: int, subfase: int, 
                            modo_recurso: str, recurso_base: int) -> OrdemProducao:
        """Cria e registra uma nova Ordem de Produção."""
        try:
            op = OrdemProducao(codigo_of, fase, subfase, modo_recurso, recurso_base)
            self.ordens_producao.append(op)
            return op
        except ValueError as e:
            raise ValueError(f"Erro ao criar OP: {str(e)}")

    def validar_ordem_producao(self, codigo_op: str) -> Tuple[bool, str]:
        """
        Valida uma OP fornecida em formato de string.
        
        Formato esperado: YYTCCFSM RB
        - YYTCC: código OF
        - F: fase (0-2)
        - S: subfase (0-2)
        - M: modo (A, B, C)
        - RB: recurso base (00-26)
        """
        try:
            if len(codigo_op) < 10:
                return False, "Código OP muito curto. Formato esperado: YYTCCFSMRB (10 caracteres)"
            
            codigo_of = codigo_op[0:5]
            fase = int(codigo_op[5])
            subfase = int(codigo_op[6])
            modo = codigo_op[7].upper()
            recurso_base = int(codigo_op[8:10])
            
            # Tentar criar um objeto OP para validação
            op_teste = OrdemProducao(codigo_of, fase, subfase, modo, recurso_base)
            return True, f"OP válida: {op_teste.gerar_codigo()}"
        
        except (ValueError, IndexError) as e:
            return False, f"OP inválida: {str(e)}"

    def converter_op_para_recursos(self, codigo_op: str) -> Tuple[bool, List[int]]:
        """Converte um código OP em lista de recursos utilizados."""
        try:
            if len(codigo_op) < 10:
                return False, []
            
            codigo_of = codigo_op[0:5]
            fase = int(codigo_op[5])
            subfase = int(codigo_op[6])
            modo = codigo_op[7].upper()
            recurso_base = int(codigo_op[8:10])
            
            op = OrdemProducao(codigo_of, fase, subfase, modo, recurso_base)
            return True, op.obter_recursos()
        
        except (ValueError, IndexError):
            return False, []

    def listar_estrutura(self) -> str:
        """Retorna a estrutura completa da linha de produção."""
        estrutura = "\n" + "="*70 + "\n"
        estrutura += f"ESTRUTURA DA LINHA DE PRODUÇÃO: {self.nome}\n"
        estrutura += f"Data de Criação: {self.data_criacao.strftime('%Y-%m-%d %H:%M:%S')}\n"
        estrutura += "="*70 + "\n\n"
        
        # Informações gerais
        estrutura += "CONFIGURAÇÃO:\n"
        estrutura += f"  - Total de Recursos: {self.num_recursos} (0-26)\n"
        estrutura += f"  - Total de Ordens de Fabricação: {len(self.ordens_fabricacao)}\n"
        estrutura += f"  - Total de Ordens de Produção: {len(self.ordens_producao)}\n\n"
        
        # Fases e subfases
        estrutura += "FASES E SUBFASES:\n"
        estrutura += "  - Fases: 0, 1, 2\n"
        estrutura += "  - Subfases por fase: 0, 1, 2\n"
        estrutura += "  - Total de combinações fase/subfase: 9\n\n"
        
        # Modos de recurso
        estrutura += "MODOS DE RECURSO:\n"
        estrutura += "  - A: 1 recurso\n"
        estrutura += "  - B: 2 recursos (acumulativo)\n"
        estrutura += "  - C: 3 recursos (acumulativo)\n\n"
        
        # Exemplo de acumulação
        estrutura += "EXEMPLOS DE ACUMULAÇÃO:\n"
        estrutura += "  - Base 05, Modo A → [05]\n"
        estrutura += "  - Base 05, Modo B → [05, 06]\n"
        estrutura += "  - Base 05, Modo C → [05, 06, 07]\n\n"
        
        # Ordens de Fabricação
        if self.ordens_fabricacao:
            estrutura += "ORDENS DE FABRICAÇÃO REGISTRADAS:\n"
            for i, of in enumerate(self.ordens_fabricacao, 1):
                estrutura += f"  {i}. {of}\n"
            estrutura += "\n"
        
        # Ordens de Produção
        if self.ordens_producao:
            estrutura += "ORDENS DE PRODUÇÃO REGISTRADAS:\n"
            for i, op in enumerate(self.ordens_producao, 1):
                estrutura += f"  {i}. {op}\n"
            estrutura += "\n"
        
        # Estado dos recursos
        estrutura += "ESTADO DOS RECURSOS:\n"
        for i in range(self.num_recursos):
            status = "Disponível" if self.recursos[i]['disponivel'] else "Em uso"
            estrutura += f"  Recurso {i:02d}: {status}\n"
        
        estrutura += "\n" + "="*70
        return estrutura

    def __str__(self) -> str:
        return f"Linha de Produção '{self.nome}' - Recursos: {self.num_recursos}, OFs: {len(self.ordens_fabricacao)}, OPs: {len(self.ordens_producao)}"


class SistemaProducao:
    """
    Sistema interativo de gerenciamento de produção com menu de interface.
    """

    def __init__(self):
        """Inicializa o sistema de produção."""
        self.linha = None
        self.inicializar_linha()

    def inicializar_linha(self):
        """Inicializa a linha de produção principal."""
        self.linha = LinhaProducao("Linha Compacta Premium")

    def limpar_tela(self):
        """Limpa a tela do terminal."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

    def exibir_menu_principal(self):
        """Exibe o menu principal do sistema."""
        print("\n" + "="*70)
        print("SISTEMA DE PRODUÇÃO - CODIFICAÇÃO COMPACTA")
        print("="*70)
        print("\n1. Criar Ordem de Fabricação (OF)")
        print("2. Criar Ordem de Produção (OP)")
        print("3. Validar OP")
        print("4. Simular Execução de OP")
        print("5. Converter OP para Lista de Recursos")
        print("6. Listar Estrutura da Linha")
        print("7. Visualizar Todas as Ordens")
        print("8. Sair")
        print("="*70)

    def criar_of(self):
        """Cria uma novo Ordem de Fabricação através de entrada do usuário."""
        print("\n--- CRIAR ORDEM DE FABRICAÇÃO ---")
        try:
            ano = int(input("Ano (00-99): "))
            print("Tipo de linha: 0=Normal, 1=Premium")
            tipo = int(input("Tipo (0 ou 1): "))
            cliente = int(input("Código do cliente (00-99): "))
            
            of = self.linha.criar_ordem_fabricacao(ano, tipo, cliente)
            print(f"\n✓ OF criada com sucesso!")
            print(f"  Código: {of.gerar_codigo()}")
            print(f"  {of}")
            return of
        except ValueError as e:
            print(f"\n✗ Erro: {str(e)}")
            return None

    def criar_op(self):
        """Cria uma nova Ordem de Produção através de entrada do usuário."""
        print("\n--- CRIAR ORDEM DE PRODUÇÃO ---")
        
        # Listar OFs disponíveis
        if not self.linha.ordens_fabricacao:
            print("✗ Nenhuma OF criada ainda. Crie uma OF primeiro!")
            return None
        
        print("\nOFs disponíveis:")
        for i, of in enumerate(self.linha.ordens_fabricacao, 1):
            print(f"  {i}. {of.gerar_codigo()}")
        
        try:
            idx = int(input("\nEscolha uma OF (número): ")) - 1
            codigo_of = self.linha.ordens_fabricacao[idx].gerar_codigo()
            
            fase = int(input("Fase (0-2): "))
            subfase = int(input("Subfase (0-2): "))
            print("Modo de recurso: A=1 recurso, B=2 recursos, C=3 recursos")
            modo = input("Modo (A, B ou C): ").upper()
            recurso_base = int(input("Recurso base (00-26): "))
            
            op = self.linha.criar_ordem_producao(codigo_of, fase, subfase, modo, recurso_base)
            print(f"\n✓ OP criada com sucesso!")
            print(f"  Código: {op.gerar_codigo()}")
            print(f"  Recursos: {op.obter_recursos()}")
            print(f"  {op}")
            return op
        except (ValueError, IndexError) as e:
            print(f"\n✗ Erro: {str(e)}")
            return None

    def validar_op(self):
        """Valida uma OP fornecida pelo usuário."""
        print("\n--- VALIDAR ORDEM DE PRODUÇÃO ---")
        print("Formato esperado: YYTCCFSMRB (10 caracteres)")
        print("  YYTCC = Código OF")
        print("  F = Fase (0-2)")
        print("  S = Subfase (0-2)")
        print("  M = Modo (A, B, C)")
        print("  RB = Recurso Base (00-26)")
        
        codigo = input("\nDigite o código da OP (ex: 2512312B05): ").strip()
        valido, mensagem = self.linha.validar_ordem_producao(codigo)
        
        if valido:
            print(f"\n✓ {mensagem}")
            # Converter para recursos também
            _, recursos = self.linha.converter_op_para_recursos(codigo)
            print(f"  Recursos utilizados: {recursos}")
        else:
            print(f"\n✗ {mensagem}")

    def simular_op(self):
        """Simula a execução de uma OP."""
        print("\n--- SIMULAR EXECUÇÃO DE OP ---")
        
        if not self.linha.ordens_producao:
            print("✗ Nenhuma OP criada ainda!")
            return
        
        print("\nOPs disponíveis:")
        for i, op in enumerate(self.linha.ordens_producao, 1):
            print(f"  {i}. {op.gerar_codigo()}")
        
        try:
            idx = int(input("\nEscolha uma OP (número): ")) - 1
            op = self.linha.ordens_producao[idx]
            
            simulacao = op.simular_execucao()
            print(f"\n{'='*70}")
            print("SIMULAÇÃO DE EXECUÇÃO")
            print(f"{'='*70}")
            print(f"Código OP: {simulacao['codigo_op']}")
            print(f"Fase: {simulacao['fase']}")
            print(f"Subfase: {simulacao['subfase']}")
            print(f"Modo: {simulacao['modo']} ({simulacao['modo_descricao']})")
            print(f"Recurso Base: {simulacao['recurso_base']:02d}")
            print(f"Número de Recursos: {simulacao['numero_recursos']}")
            print(f"Recursos Utilizados: {simulacao['recursos_utilizados']}")
            print(f"Status: {simulacao['status']}")
            print(f"{'='*70}")
        except (ValueError, IndexError):
            print("\n✗ Escolha inválida!")

    def converter_op(self):
        """Converte um código OP em lista de recursos."""
        print("\n--- CONVERTER OP PARA LISTA DE RECURSOS ---")
        print("Formato esperado: YYTCCFSMRB (10 caracteres)")
        
        codigo = input("\nDigite o código da OP: ").strip()
        valido, recursos = self.linha.converter_op_para_recursos(codigo)
        
        if valido:
            print(f"\n✓ OP: {codigo}")
            print(f"  Recursos utilizados: {recursos}")
            print(f"  Total de recursos: {len(recursos)}")
        else:
            print(f"\n✗ Erro ao converter OP!")

    def listar_estrutura(self):
        """Exibe a estrutura completa da linha."""
        print(self.linha.listar_estrutura())

    def visualizar_ordens(self):
        """Visualiza todas as ordens criadas."""
        print("\n" + "="*70)
        print("TODAS AS ORDENS")
        print("="*70)
        
        if not self.linha.ordens_fabricacao and not self.linha.ordens_producao:
            print("\nNenhuma ordem criada ainda.")
            return
        
        if self.linha.ordens_fabricacao:
            print("\nORDENS DE FABRICAÇÃO:")
            for i, of in enumerate(self.linha.ordens_fabricacao, 1):
                print(f"  {i}. {of}")
        
        if self.linha.ordens_producao:
            print("\nORDENS DE PRODUÇÃO:")
            for i, op in enumerate(self.linha.ordens_producao, 1):
                print(f"  {i}. {op}")
        
        print("\n" + "="*70)

    def executar(self):
        """Executa o loop principal do sistema."""
        while True:
            try:
                self.exibir_menu_principal()
                opcao = input("\nDigite a opção desejada: ").strip()
                
                if opcao == '1':
                    self.criar_of()
                elif opcao == '2':
                    self.criar_op()
                elif opcao == '3':
                    self.validar_op()
                elif opcao == '4':
                    self.simular_op()
                elif opcao == '5':
                    self.converter_op()
                elif opcao == '6':
                    self.listar_estrutura()
                elif opcao == '7':
                    self.visualizar_ordens()
                elif opcao == '8':
                    print("\n✓ Encerrando sistema...")
                    break
                else:
                    print("\n✗ Opção inválida! Tente novamente.")
                
                input("\nPressione Enter para continuar...")
            except KeyboardInterrupt:
                print("\n\n✓ Sistema interrompido pelo usuário.")
                break
            except Exception as e:
                print(f"\n✗ Erro inesperado: {str(e)}")
                input("\nPressione Enter para continuar...")


# Script principal
if __name__ == "__main__":
    sistema = SistemaProducao()
    sistema.executar()

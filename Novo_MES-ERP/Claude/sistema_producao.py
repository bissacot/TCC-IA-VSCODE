"""
Sistema de Codificação Compacta para Linha de Produção ERP/MES
Implementa modelo de ordens de fabricação e produção com validações.
"""

from datetime import datetime
from typing import List, Optional, Tuple
import re


class OrdemFabricacao:
    """Representa uma Ordem de Fabricação (OF)"""
    
    def __init__(self, ano: int, tipo: int, codigo_cliente: int):
        """
        Inicializa uma Ordem de Fabricação.
        
        Args:
            ano: Ano (00-99)
            tipo: Tipo de linha (0=normal, 1=premium)
            codigo_cliente: Código do cliente (00-99)
        """
        self.ano = ano
        self.tipo = tipo
        self.codigo_cliente = codigo_cliente
        self.criada_em = datetime.now()
    
    def validar(self) -> Tuple[bool, str]:
        """
        Valida os parâmetros da OF.
        
        Returns:
            Tupla (válido, mensagem)
        """
        if not (0 <= self.ano <= 99):
            return False, "Ano deve estar entre 00 e 99"
        
        if self.tipo not in [0, 1]:
            return False, "Tipo deve ser 0 (normal) ou 1 (premium)"
        
        if not (0 <= self.codigo_cliente <= 99):
            return False, "Código do cliente deve estar entre 00 e 99"
        
        return True, "OF válida"
    
    def gerar_codigo(self) -> str:
        """
        Gera o código da OF no formato YYTCC.
        
        Returns:
            Código da OF
        """
        return f"{self.ano:02d}{self.tipo}{self.codigo_cliente:02d}"
    
    def __str__(self) -> str:
        return f"OF[{self.gerar_codigo()}] - Tipo: {'Premium' if self.tipo else 'Normal'}, Cliente: {self.codigo_cliente:02d}"


class OrdemProducao:
    """Representa uma Ordem de Produção (OP)"""
    
    MODOS_VALIDOS = ['A', 'B', 'C']
    RECURSOS_MAX = 26
    FASES_MAX = 2
    SUBFASES_MAX = 2
    
    def __init__(self, codigo_op: str):
        """
        Inicializa uma Ordem de Produção a partir do código.
        
        Args:
            codigo_op: Código da OP no formato YYTCCFSMRR (10 caracteres)
                      YY=ano, T=tipo, CC=cliente, F=fase, S=subfase, M=modo, RR=recurso_base
        """
        self.codigo_original = codigo_op
        self.valido = False
        self.mensagem_erro = ""
        self.of_codigo = ""
        self.fase = None
        self.subfase = None
        self.modo = ""
        self.recurso_base = None
        self.recursos_utilizados = []
        
        self._parsear_codigo()
    
    def _parsear_codigo(self) -> None:
        """Parseia o código da OP e extrai seus componentes."""
        
        if not isinstance(self.codigo_original, str):
            self.mensagem_erro = "Código deve ser uma string"
            return
        
        if len(self.codigo_original) != 10:
            self.mensagem_erro = f"Código deve ter exatamente 10 caracteres (fornecido: {len(self.codigo_original)})"
            return
        
        try:
            # Extrair componentes
            self.of_codigo = self.codigo_original[:5]  # YYTCC
            self.fase = int(self.codigo_original[5])     # F
            self.subfase = int(self.codigo_original[6])  # S
            self.modo = self.codigo_original[7].upper()  # M
            self.recurso_base = int(self.codigo_original[8:10])  # RR
            
            # Validar OF (apenas formato, não temos dados de cliente aqui)
            if not self._validar_of_formato():
                return
            
            # Validar fase e subfase
            if not self._validar_fase_subfase():
                return
            
            # Validar modo
            if not self._validar_modo():
                return
            
            # Validar recurso base
            if not self._validar_recurso_base():
                return
            
            # Gerar lista de recursos
            if not self._gerar_recursos():
                return
            
            self.valido = True
            self.mensagem_erro = "OP válida"
            
        except ValueError as e:
            self.mensagem_erro = f"Erro ao parsear código: {str(e)}"
    
    def _validar_of_formato(self) -> bool:
        """Valida o formato da OF (YYTCC)."""
        if not self.of_codigo.isdigit() or len(self.of_codigo) != 5:
            self.mensagem_erro = "Formato de OF inválido (esperado: YYTCC)"
            return False
        
        ano = int(self.of_codigo[:2])
        tipo = int(self.of_codigo[2])
        cliente = int(self.of_codigo[3:5])
        
        if not (0 <= ano <= 99):
            self.mensagem_erro = "Ano da OF fora do intervalo (00-99)"
            return False
        
        if tipo not in [0, 1]:
            self.mensagem_erro = "Tipo de linha inválido (deve ser 0 ou 1)"
            return False
        
        if not (0 <= cliente <= 99):
            self.mensagem_erro = "Código de cliente fora do intervalo (00-99)"
            return False
        
        return True
    
    def _validar_fase_subfase(self) -> bool:
        """Valida fase e subfase."""
        if not (0 <= self.fase <= self.FASES_MAX):
            self.mensagem_erro = f"Fase deve estar entre 0 e {self.FASES_MAX}"
            return False
        
        if not (0 <= self.subfase <= self.SUBFASES_MAX):
            self.mensagem_erro = f"Subfase deve estar entre 0 e {self.SUBFASES_MAX}"
            return False
        
        return True
    
    def _validar_modo(self) -> bool:
        """Valida o modo de recurso."""
        if self.modo not in self.MODOS_VALIDOS:
            self.mensagem_erro = f"Modo inválido: {self.modo} (deve ser A, B ou C)"
            return False
        
        return True
    
    def _validar_recurso_base(self) -> bool:
        """Valida o recurso base."""
        if not (0 <= self.recurso_base <= self.RECURSOS_MAX):
            self.mensagem_erro = f"Recurso base fora do intervalo (00-{self.RECURSOS_MAX})"
            return False
        
        return True
    
    def _gerar_recursos(self) -> bool:
        """Gera a lista de recursos baseado no modo."""
        quantidade_recursos = self._get_quantidade_recursos()
        
        # Validar overflow
        if self.recurso_base + quantidade_recursos - 1 > self.RECURSOS_MAX:
            self.mensagem_erro = (
                f"Overflow de recursos: base {self.recurso_base:02d} com modo {self.modo} "
                f"tentaria usar recurso {self.recurso_base + quantidade_recursos - 1} "
                f"(máximo: {self.RECURSOS_MAX})"
            )
            return False
        
        # Gerar lista de recursos
        self.recursos_utilizados = [
            self.recurso_base + i for i in range(quantidade_recursos)
        ]
        
        return True
    
    def _get_quantidade_recursos(self) -> int:
        """Retorna a quantidade de recursos baseado no modo."""
        modos_recursos = {
            'A': 1,
            'B': 2,
            'C': 3
        }
        return modos_recursos.get(self.modo, 0)
    
    def obter_recursos(self) -> List[int]:
        """
        Retorna a lista de recursos utilizados pela OP.
        
        Returns:
            Lista de IDs de recursos (00-26)
        """
        return self.recursos_utilizados if self.valido else []
    
    def obter_detalhes(self) -> dict:
        """Retorna um dicionário com todos os detalhes da OP."""
        return {
            'codigo': self.codigo_original,
            'valido': self.valido,
            'mensagem': self.mensagem_erro,
            'of': self.of_codigo,
            'fase': self.fase,
            'subfase': self.subfase,
            'modo': self.modo,
            'recurso_base': f"{self.recurso_base:02d}",
            'recursos_utilizados': [f"{r:02d}" for r in self.recursos_utilizados],
            'quantidade_recursos': len(self.recursos_utilizados)
        }
    
    def __str__(self) -> str:
        status = "✓ VÁLIDA" if self.valido else "✗ INVÁLIDA"
        recursos_str = ", ".join([f"{r:02d}" for r in self.recursos_utilizados])
        return (
            f"OP[{self.codigo_original}] {status}\n"
            f"  OF: {self.of_codigo} | Fase: {self.fase} | Subfase: {self.subfase}\n"
            f"  Modo: {self.modo} | Recurso Base: {self.recurso_base:02d}\n"
            f"  Recursos Utilizados: [{recursos_str}]"
        )


class LinhaProducao:
    """Representa a estrutura da Linha de Produção"""
    
    def __init__(self, nome: str = "Linha de Produção Principal"):
        """
        Inicializa a linha de produção.
        
        Args:
            nome: Nome da linha
        """
        self.nome = nome
        self.recursos = self._inicializar_recursos()
        self.ordens_fabricacao = {}  # Dicionário de OFs criadas
        self.ordens_producao = []     # Lista de OPs processadas
        self.simulacoes = []          # Histórico de simulações
    
    def _inicializar_recursos(self) -> dict:
        """Inicializa os recursos disponíveis (00-26)."""
        recursos = {}
        for i in range(27):  # 0 a 26
            recursos[f"{i:02d}"] = {
                'id': f"{i:02d}",
                'disponivel': True,
                'em_uso_por': None,
                'capacidade': 100,
                'ocupacao': 0
            }
        return recursos
    
    def criar_ordem_fabricacao(self, ano: int, tipo: int, codigo_cliente: int) -> Optional[str]:
        """
        Cria uma nova Ordem de Fabricação.
        
        Args:
            ano: Ano (00-99)
            tipo: Tipo (0=normal, 1=premium)
            codigo_cliente: Código do cliente (00-99)
        
        Returns:
            Código da OF se válida, None caso contrário
        """
        of = OrdemFabricacao(ano, tipo, codigo_cliente)
        valida, mensagem = of.validar()
        
        if not valida:
            return None
        
        codigo = of.gerar_codigo()
        self.ordens_fabricacao[codigo] = of
        return codigo
    
    def gerar_ordem_producao(self, of_codigo: str, fase: int, subfase: int, 
                           modo: str, recurso_base: int) -> Optional[str]:
        """
        Gera uma Ordem de Produção a partir dos parâmetros.
        
        Args:
            of_codigo: Código da OF (YYTCC)
            fase: Fase (0-2)
            subfase: Subfase (0-2)
            modo: Modo (A, B ou C)
            recurso_base: Recurso base (00-26)
        
        Returns:
            Código da OP se válida, None caso contrário
        """
        if of_codigo not in self.ordens_fabricacao:
            return None
        
        # Construir código da OP
        codigo_op = f"{of_codigo}{fase}{subfase}{modo.upper()}{recurso_base:02d}"
        
        op = OrdemProducao(codigo_op)
        
        if op.valido:
            self.ordens_producao.append(op)
            return codigo_op
        
        return None
    
    def validar_ordem_producao(self, codigo_op: str) -> Tuple[bool, dict]:
        """
        Valida um código de OP.
        
        Args:
            codigo_op: Código da OP
        
        Returns:
            Tupla (válida, detalhes)
        """
        op = OrdemProducao(codigo_op)
        return op.valido, op.obter_detalhes()
    
    def simular_execucao_op(self, codigo_op: str) -> dict:
        """
        Simula a execução de uma OP.
        
        Args:
            codigo_op: Código da OP
        
        Returns:
            Dicionário com resultado da simulação
        """
        op = OrdemProducao(codigo_op)
        
        simulacao = {
            'op': codigo_op,
            'timestamp': datetime.now().isoformat(),
            'valida': op.valido,
            'detalhes': op.obter_detalhes(),
            'recursos_alocados': [],
            'status': 'ERRO'
        }
        
        if not op.valido:
            simulacao['erro'] = op.mensagem_erro
            self.simulacoes.append(simulacao)
            return simulacao
        
        # Alocar recursos
        recursos_alocados = []
        for recurso_id in op.recursos_utilizados:
            recurso = self.recursos[f"{recurso_id:02d}"]
            recurso['em_uso_por'] = codigo_op
            recurso['ocupacao'] = 100
            recursos_alocados.append({
                'id': f"{recurso_id:02d}",
                'status': 'alocado',
                'ocupacao': 100
            })
        
        simulacao['recursos_alocados'] = recursos_alocados
        simulacao['status'] = 'SUCESSO'
        self.simulacoes.append(simulacao)
        
        return simulacao
    
    def listar_estrutura(self) -> str:
        """Retorna a estrutura da linha de produção."""
        saida = f"\n{'='*60}\n"
        saida += f"ESTRUTURA DA {self.nome.upper()}\n"
        saida += f"{'='*60}\n\n"
        
        # Informações de fases e subfases
        saida += "FASES E SUBFASES:\n"
        saida += "  Fases: 0, 1, 2\n"
        saida += "  Subfases por fase: 0, 1, 2\n"
        saida += "  Total de combinações: 3 × 3 = 9\n\n"
        
        # Informações de modos e recursos
        saida += "MODOS DE RECURSO:\n"
        saida += "  Modo A: 1 recurso\n"
        saida += "  Modo B: 2 recursos (sequencial)\n"
        saida += "  Modo C: 3 recursos (sequencial)\n\n"
        
        # Informações de recursos
        saida += "RECURSOS DISPONÍVEIS:\n"
        saida += f"  Total: {len(self.recursos)} recursos (00 a 26)\n"
        
        # Contar disponibilidade
        disponiveis = sum(1 for r in self.recursos.values() if r['disponivel'])
        em_uso = len(self.recursos) - disponiveis
        
        saida += f"  Disponíveis: {disponiveis}\n"
        saida += f"  Em uso: {em_uso}\n\n"
        
        # Status dos recursos
        saida += "STATUS DOS RECURSOS:\n"
        for i in range(0, 27, 10):
            recursos_linha = []
            for j in range(i, min(i + 10, 27)):
                recurso = self.recursos[f"{j:02d}"]
                status = "●" if recurso['disponivel'] else "○"
                recursos_linha.append(f"{j:02d}{status}")
            saida += "  " + "  ".join(recursos_linha) + "\n"
        
        saida += f"\n{'●'} = Disponível | {'○'} = Em uso\n"
        
        # Estatísticas
        saida += f"\n{'='*60}\n"
        saida += f"ESTATÍSTICAS:\n"
        saida += f"  OFs criadas: {len(self.ordens_fabricacao)}\n"
        saida += f"  OPs processadas: {len(self.ordens_producao)}\n"
        saida += f"  Simulações realizadas: {len(self.simulacoes)}\n"
        saida += f"{'='*60}\n"
        
        return saida
    
    def liberar_recursos(self, codigo_op: str) -> None:
        """Libera os recursos alocados para uma OP."""
        for recurso in self.recursos.values():
            if recurso['em_uso_por'] == codigo_op:
                recurso['em_uso_por'] = None
                recurso['ocupacao'] = 0
                recurso['disponivel'] = True


class MenuInterativo:
    """Interface interativa para o sistema de produção"""
    
    def __init__(self):
        self.linha = LinhaProducao("Linha de Produção ERP/MES")
        self.rodando = True
    
    def limpar_tela(self) -> None:
        """Limpa a tela do terminal."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def exibir_menu_principal(self) -> None:
        """Exibe o menu principal."""
        print("\n" + "="*60)
        print("SISTEMA DE CODIFICAÇÃO COMPACTA - ERP/MES")
        print("="*60)
        print("\n1. Criar Ordem de Fabricação (OF)")
        print("2. Gerar Ordem de Produção (OP)")
        print("3. Validar Ordem de Produção")
        print("4. Simular Execução de OP")
        print("5. Listar Estrutura da Linha")
        print("6. Histórico de Simulações")
        print("7. Sair")
        print("\n" + "="*60)
    
    def criar_of(self) -> None:
        """Cria uma nova Ordem de Fabricação."""
        print("\n--- CRIAR ORDEM DE FABRICAÇÃO ---\n")
        
        try:
            ano = int(input("Ano (00-99): "))
            print("Tipo de Linha:")
            print("  0 = Normal")
            print("  1 = Premium")
            tipo = int(input("Escolha o tipo (0 ou 1): "))
            codigo_cliente = int(input("Código do Cliente (00-99): "))
            
            codigo = self.linha.criar_ordem_fabricacao(ano, tipo, codigo_cliente)
            
            if codigo:
                print(f"\n✓ OF criada com sucesso: {codigo}")
                of = self.linha.ordens_fabricacao[codigo]
                print(f"  {of}")
            else:
                print("\n✗ Erro ao criar OF. Verifique os parâmetros.")
        
        except ValueError:
            print("\n✗ Entrada inválida. Digite números válidos.")
    
    def gerar_op(self) -> None:
        """Gera uma nova Ordem de Produção."""
        print("\n--- GERAR ORDEM DE PRODUÇÃO ---\n")
        
        if not self.linha.ordens_fabricacao:
            print("✗ Nenhuma OF criada. Crie uma OF primeiro.")
            return
        
        print("OFs disponíveis:")
        for i, (codigo, of) in enumerate(self.linha.ordens_fabricacao.items(), 1):
            print(f"  {i}. {codigo} - {of}")
        
        try:
            of_codigo = input("\nDigite o código da OF (YYTCC): ").strip()
            
            if of_codigo not in self.linha.ordens_fabricacao:
                print("✗ OF não encontrada.")
                return
            
            print("\nParâmetros da OP:")
            fase = int(input("Fase (0-2): "))
            subfase = int(input("Subfase (0-2): "))
            
            print("Modo de Recurso:")
            print("  A = 1 recurso")
            print("  B = 2 recursos (sequencial)")
            print("  C = 3 recursos (sequencial)")
            modo = input("Escolha o modo (A, B ou C): ").strip().upper()
            
            recurso_base = int(input("Recurso Base (00-26): "))
            
            codigo_op = self.linha.gerar_ordem_producao(of_codigo, fase, subfase, modo, recurso_base)
            
            if codigo_op:
                print(f"\n✓ OP gerada com sucesso: {codigo_op}")
                op = self.linha.ordens_producao[-1]
                print(f"\n{op}")
            else:
                print("\n✗ Erro ao gerar OP. Verifique os parâmetros.")
        
        except ValueError:
            print("\n✗ Entrada inválida.")
    
    def validar_op(self) -> None:
        """Valida uma Ordem de Produção."""
        print("\n--- VALIDAR ORDEM DE PRODUÇÃO ---\n")
        
        codigo_op = input("Digite o código da OP (10 caracteres): ").strip()
        
        valida, detalhes = self.linha.validar_ordem_producao(codigo_op)
        
        print("\n" + "="*60)
        print("RESULTADO DA VALIDAÇÃO")
        print("="*60)
        
        if valida:
            print("✓ OP VÁLIDA\n")
        else:
            print("✗ OP INVÁLIDA\n")
        
        print("Detalhes:")
        print(f"  Código: {detalhes['codigo']}")
        print(f"  OF: {detalhes['of']}")
        print(f"  Fase: {detalhes['fase']}")
        print(f"  Subfase: {detalhes['subfase']}")
        print(f"  Modo: {detalhes['modo']}")
        print(f"  Recurso Base: {detalhes['recurso_base']}")
        print(f"  Recursos Utilizados: {', '.join(detalhes['recursos_utilizados'])}")
        print(f"  Quantidade: {detalhes['quantidade_recursos']}")
        print(f"  Mensagem: {detalhes['mensagem']}")
        print("="*60)
    
    def simular_op(self) -> None:
        """Simula a execução de uma Ordem de Produção."""
        print("\n--- SIMULAR EXECUÇÃO DE OP ---\n")
        
        codigo_op = input("Digite o código da OP (10 caracteres): ").strip()
        
        resultado = self.linha.simular_execucao_op(codigo_op)
        
        print("\n" + "="*60)
        print("RESULTADO DA SIMULAÇÃO")
        print("="*60)
        
        print(f"OP: {resultado['op']}")
        print(f"Data/Hora: {resultado['timestamp']}")
        print(f"Status: {resultado['status']}")
        
        if resultado['valida']:
            detalhes = resultado['detalhes']
            print(f"\nDetalhes:")
            print(f"  OF: {detalhes['of']}")
            print(f"  Fase: {detalhes['fase']} | Subfase: {detalhes['subfase']}")
            print(f"  Modo: {detalhes['modo']}")
            print(f"  Recurso Base: {detalhes['recurso_base']}")
            
            print(f"\nRecursos Alocados:")
            for recurso in resultado['recursos_alocados']:
                print(f"  - Recurso {recurso['id']}: {recurso['status'].upper()}")
        else:
            print(f"\n✗ Erro: {resultado['detalhes']['mensagem']}")
        
        print("="*60)
    
    def listar_estrutura(self) -> None:
        """Lista a estrutura da linha de produção."""
        print(self.linha.listar_estrutura())
    
    def historico_simulacoes(self) -> None:
        """Exibe o histórico de simulações."""
        print("\n" + "="*60)
        print("HISTÓRICO DE SIMULAÇÕES")
        print("="*60 + "\n")
        
        if not self.linha.simulacoes:
            print("Nenhuma simulação realizada ainda.\n")
            return
        
        for i, sim in enumerate(self.linha.simulacoes, 1):
            print(f"{i}. OP: {sim['op']}")
            print(f"   Data/Hora: {sim['timestamp']}")
            print(f"   Status: {sim['status']}")
            
            if sim['valida']:
                print(f"   Recursos: {', '.join([r['id'] for r in sim['recursos_alocados']])}")
            else:
                print(f"   Erro: {sim.get('erro', 'Desconhecido')}")
            
            print()
        
        print("="*60)
    
    def executar(self) -> None:
        """Loop principal do menu interativo."""
        while self.rodando:
            self.exibir_menu_principal()
            
            opcao = input("\nEscolha uma opção (1-7): ").strip()
            
            if opcao == '1':
                self.criar_of()
            elif opcao == '2':
                self.gerar_op()
            elif opcao == '3':
                self.validar_op()
            elif opcao == '4':
                self.simular_op()
            elif opcao == '5':
                self.listar_estrutura()
            elif opcao == '6':
                self.historico_simulacoes()
            elif opcao == '7':
                print("\n✓ Saindo do sistema. Até logo!\n")
                self.rodando = False
            else:
                print("\n✗ Opção inválida. Escolha um número entre 1 e 7.")
            
            if self.rodando and opcao != '5':
                input("\nPressione Enter para continuar...")


def main():
    """Função principal."""
    menu = MenuInterativo()
    menu.executar()


if __name__ == "__main__":
    main()

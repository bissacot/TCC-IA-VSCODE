
# Sistema de Codificação Compacta para Linha de Produção ERP/MES

## Visão Geral

Sistema Python orientado a objetos que implementa um modelo de codificação compacta para ordens de fabricação e produção em uma linha de manufatura, inspirado em sistemas ERP/MES industriais.

O sistema permite criar, validar, gerenciar e simular ordens de produção com alocação automática de recursos e validações de integridade.

---

## Estrutura da Codificação

### Ordem de Fabricação (OF) - Formato YYTCC

```
YYTCC
├── YY: Ano (00-99)
├── T: Tipo de Linha
│   ├── 0 = Normal
│   └── 1 = Premium
└── CC: Código do Cliente (00-99)

Exemplo: 25123
  ├── 25 = Ano 2025
  ├── 1 = Premium
  └── 23 = Cliente 23
```

### Ordem de Produção (OP) - Formato YYTCCFSMRR

```
YYTCCFSMRR (10 caracteres)
├── YYTCC: Referência da OF (5 caracteres)
├── F: Fase (0-2)
├── S: Subfase (0-2)
├── M: Modo de Recurso (A, B ou C)
└── RR: Recurso Base (00-26)

Exemplo: 2512312B05
  ├── 25123 = OF (ano=25, tipo=1, cliente=23)
  ├── 1 = Fase 1
  ├── 2 = Subfase 2
  ├── B = Modo B (2 recursos)
  └── 05 = Recurso base 05
```

---

## Fases e Subfases

O sistema organiza a produção em **3 fases** (0, 1, 2), cada uma com **3 subfases** (0, 1, 2).

```
Estrutura de Fases:
├── Fase 0
│   ├── Subfase 0 (preparação inicial)
│   ├── Subfase 1 (preparação intermediária)
│   └── Subfase 2 (preparação final)
├── Fase 1
│   ├── Subfase 0 (processamento inicial)
│   ├── Subfase 1 (processamento intermediário)
│   └── Subfase 2 (processamento final)
└── Fase 2
    ├── Subfase 0 (finalização inicial)
    ├── Subfase 1 (finalização intermediária)
    └── Subfase 2 (finalização final)

Total: 3 × 3 = 9 combinações de fase/subfase
```

---

## Modos de Recurso

Cada OP especifica um **modo** que determina quantos recursos serão utilizados:

| Modo | Recursos | Descrição |
|------|----------|-----------|
| **A** | 1 | Um único recurso |
| **B** | 2 | Dois recursos sequenciais (acumulativo) |
| **C** | 3 | Três recursos sequenciais (acumulativo) |

### Exemplos de Alocação

```
Recurso Base: 05

Modo A (1 recurso):
  └─ [05]

Modo B (2 recursos):
  └─ [05, 06]

Modo C (3 recursos):
  └─ [05, 06, 07]
```

---

## Recursos Disponíveis

O sistema fornece **27 recursos** numerados de **00 a 26**.

- Cada OP utiliza de 1 a 3 recursos (dependendo do modo)
- Recursos são alocados sequencialmente a partir do recurso base
- Não é permitido overflow (recursos > 26)

---

## Validações Obrigatórias

Todas as seguintes validações são implementadas:

### 1. Formato de OF (YYTCC)
- Ano: 00-99
- Tipo: 0 ou 1
- Cliente: 00-99

### 2. Formato de OP
- Exatamente 10 caracteres
- OF válida
- Fase: 0-2
- Subfase: 0-2
- Modo: A, B ou C
- Recurso base: 00-26

### 3. Validação de Recursos
- Recurso base dentro do intervalo (00-26)
- Sem overflow (base + quantidade ≤ 26)

### 4. Exemplos de Rejeição
```
INVÁLIDO: 2512125C25
Razão: Overflow
Modo C requer 3 recursos (25, 26, 27)
27 > 26 (máximo permitido)

INVÁLIDO: 2512135A05
Razão: Subfase inválida (5 > 2)

INVÁLIDO: 251210XA05
Razão: Modo inválido (X não existe)
```

---

## Classes Principais

### OrdemFabricacao

Representa uma Ordem de Fabricação com validações.

```python
class OrdemFabricacao:
    def __init__(self, ano: int, tipo: int, codigo_cliente: int)
    def validar(self) -> Tuple[bool, str]
    def gerar_codigo(self) -> str
```

**Exemplo:**
```python
of = OrdemFabricacao(25, 1, 23)
valido, msg = of.validar()
codigo = of.gerar_codigo()  # "25123"
```

### OrdemProducao

Representa uma Ordem de Produção com parsing automático e validações.

```python
class OrdemProducao:
    def __init__(self, codigo_op: str)
    def obter_recursos(self) -> List[int]
    def obter_detalhes(self) -> dict
    def validar(self) -> Tuple[bool, str]
```

**Exemplo:**
```python
op = OrdemProducao("2512312B05")
if op.valido:
    recursos = op.obter_recursos()  # [5, 6]
    detalhes = op.obter_detalhes()
```

### LinhaProducao

Gerencia a linha de produção, OFs, OPs e simulações.

```python
class LinhaProducao:
    def criar_ordem_fabricacao(ano, tipo, cliente) -> str
    def gerar_ordem_producao(of, fase, subfase, modo, base) -> str
    def validar_ordem_producao(codigo_op) -> Tuple[bool, dict]
    def simular_execucao_op(codigo_op) -> dict
    def listar_estrutura(self) -> str
```

**Exemplo:**
```python
linha = LinhaProducao()

# Criar OF
of = linha.criar_ordem_fabricacao(25, 1, 23)

# Gerar OP
op = linha.gerar_ordem_producao(of, 1, 2, 'B', 5)

# Simular
resultado = linha.simular_execucao_op(op)
```

---

## Funcionalidades

### 1. Criar Ordem de Fabricação (OF)

Cria uma nova OF com validações.

```python
linha = LinhaProducao()
of_codigo = linha.criar_ordem_fabricacao(
    ano=25,
    tipo=1,  # Premium
    codigo_cliente=23
)
# Retorna: "25123"
```

### 2. Gerar Ordem de Produção (OP)

Gera uma OP vinculada a uma OF existente.

```python
op_codigo = linha.gerar_ordem_producao(
    of_codigo="25123",
    fase=1,
    subfase=2,
    modo='B',
    recurso_base=5
)
# Retorna: "2512312B05"
```

### 3. Validar OP

Valida um código de OP e retorna detalhes.

```python
valida, detalhes = linha.validar_ordem_producao("2512312B05")

print(detalhes)
# {
#     'codigo': '2512312B05',
#     'valido': True,
#     'recursos_utilizados': ['05', '06'],
#     'quantidade_recursos': 2,
#     ...
# }
```

### 4. Simular Execução de OP

Simula a execução alocando recursos.

```python
resultado = linha.simular_execucao_op("2512312B05")

print(resultado['status'])  # 'SUCESSO'
print(resultado['recursos_alocados'])
# [
#     {'id': '05', 'status': 'alocado', 'ocupacao': 100},
#     {'id': '06', 'status': 'alocado', 'ocupacao': 100}
# ]
```

### 5. Converter OP em Lista de Recursos

Obtém a lista real de recursos utilizados.

```python
op = OrdemProducao("2512312B05")
recursos = op.obter_recursos()
print(recursos)  # [5, 6]

# Formatado
print([f"{r:02d}" for r in recursos])  # ['05', '06']
```

### 6. Listar Estrutura da Linha

Exibe informações detalhadas da linha de produção.

```python
print(linha.listar_estrutura())
# Exibe: Fases, Subfases, Modos, Recursos, Estatísticas
```

---

## Interface Interativa

### Menu Principal

```
SISTEMA DE CODIFICAÇÃO COMPACTA - ERP/MES
============================================================

1. Criar Ordem de Fabricação (OF)
2. Gerar Ordem de Produção (OP)
3. Validar Ordem de Produção
4. Simular Execução de OP
5. Listar Estrutura da Linha
6. Histórico de Simulações
7. Sair
```

### Como Usar

1. **Iniciar o sistema:**
   ```bash
   python sistema_producao.py
   ```

2. **Criar uma OF:**
   - Menu → Opção 1
   - Digite: Ano (25), Tipo (1), Cliente (23)
   - Resultado: OF criada (25123)

3. **Gerar uma OP:**
   - Menu → Opção 2
   - Selecione a OF
   - Digite: Fase (1), Subfase (2), Modo (B), Base (5)
   - Resultado: OP gerada (2512312B05)

4. **Validar a OP:**
   - Menu → Opção 3
   - Digite o código: 2512312B05
   - Resultado: Validação com detalhes

5. **Simular Execução:**
   - Menu → Opção 4
   - Digite o código: 2512312B05
   - Resultado: Simulação com alocação de recursos

---

## Exemplos de Uso

### Exemplo 1: Criar OF

```python
from sistema_producao import OrdemFabricacao

of = OrdemFabricacao(25, 1, 23)
valido, msg = of.validar()
print(of.gerar_codigo())  # "25123"
```

### Exemplo 2: Validar OP

```python
from sistema_producao import OrdemProducao

op = OrdemProducao("2512312B05")
print(f"Válida: {op.valido}")
print(f"Recursos: {[f'{r:02d}' for r in op.obter_recursos()]}")
```

### Exemplo 3: Simular Execução

```python
from sistema_producao import LinhaProducao

linha = LinhaProducao()

# Criar OF
of = linha.criar_ordem_fabricacao(25, 1, 23)

# Gerar OP
op = linha.gerar_ordem_producao(of, 1, 2, 'B', 5)

# Simular
resultado = linha.simular_execucao_op(op)
print(resultado['status'])  # 'SUCESSO'
```

### Exemplo 4: Teste de Validações

```python
from sistema_producao import OrdemProducao

# OP válida
op1 = OrdemProducao("2512312B05")
print(op1.valido)  # True

# OP inválida - Subfase > 2
op2 = OrdemProducao("2512315B05")
print(op2.valido)  # False
print(op2.mensagem_erro)  # "Subfase deve estar entre 0 e 2"

# OP inválida - Overflow
op3 = OrdemProducao("2512312C25")
print(op3.valido)  # False
print(op3.mensagem_erro)  # "Overflow de recursos..."
```

---

## Execução

### 1. Interface Interativa (Recomendado)

```bash
python sistema_producao.py
```

Abre um menu interativo no terminal com todas as operações.

### 2. Exemplos Automáticos

```bash
python exemplos.py
```

Executa uma série de exemplos demonstrando todas as funcionalidades.

### 3. Programático

```python
from sistema_producao import OrdemFabricacao, OrdemProducao, LinhaProducao

# Seu código aqui...
```

---

## Arquivos do Projeto

```
├── sistema_producao.py    # Código principal com classes e menu
├── exemplos.py            # Exemplos de uso e testes
└── README.md              # Este arquivo
```

---

## Regras de Negócio

### Alocação de Recursos

- Recursos são sequenciais a partir do recurso base
- Modo A: base
- Modo B: base, base+1
- Modo C: base, base+1, base+2

### Validações Críticas

1. **Limite de Recursos**: Máximo recurso é 26
2. **Sem Overflow**: base + quantidade ≤ 26
3. **Formato Rigoroso**: Exatamente 10 caracteres
4. **Integridade de Fase**: Fase e subfase entre 0-2

### Exemplo de Rejeição

```
OP: 2512325C25
Análise:
  ├─ OF: 25123 ✓ Válida
  ├─ Fase: 2 ✓ Válida (0-2)
  ├─ Subfase: 5 ✗ INVÁLIDA (> 2)
  ├─ Modo: C ✓ Válida
  └─ Recurso: 25 ✓ Válida individualmente

Resultado: REJEITADA (Subfase inválida)
```

---

## Casos de Uso

### Manufatura Discreta

Adequado para:
- Linhas de montagem multi-fases
- Processos com múltiplas subfases
- Alocação flexível de recursos

### ERP/MES

Integração com:
- Planejamento de produção
- Controle de recursos
- Rastreamento de ordens
- Simulação de cenários

---

## Melhorias Futuras

- [ ] Persistência em banco de dados
- [ ] Integração com APIs REST
- [ ] Dashboard web
- [ ] Análise de desempenho
- [ ] Otimização de roteamento
- [ ] Alertas automáticos
- [ ] Relatórios avançados

---

## Autor

Sistema desenvolvido como demonstração de conceitos ERP/MES em Python.

---

## Licença

Livre para uso educacional e comercial.

---

## Suporte

Para dúvidas ou problemas, consulte os exemplos em `exemplos.py` ou execute a interface interativa.


# Sistema de Codificação Compacta para Linha de Produção

## 📋 Visão Geral

Sistema Python de gerenciamento de linha de produção inspirado em sistemas industriais ERP/MES, implementando um modelo de codificação compacta para Ordens de Fabricação (OF) e Ordens de Produção (OP).

## 🏗️ Arquitetura

### Classes Principais

#### **OrdemFabricacao**
Representa uma Ordem de Fabricação com código no formato **YYTCC**:
- **YY**: Ano (00–99)
- **T**: Tipo da linha (0=Normal, 1=Premium)
- **CC**: Código do cliente (00–99)

**Exemplo**: `2501` = 2025, Normal, Cliente 01

#### **OrdemProducao**
Representa uma Ordem de Produção com código estruturado **YYTCCFSMRB**:
- **YYTCC**: Referência da OF
- **F**: Fase (0-2)
- **S**: Subfase (0-2)
- **M**: Modo de recurso (A, B, C)
- **RB**: Recurso base (00-26)

**Exemplo**: `2512312B05` = OF 25123, Fase 1, Subfase 2, Modo B, Recurso 05

#### **LinhaProducao**
Gerencia a estrutura completa da produção:
- Registro de OF e OP
- Validação de regras
- Gerenciamento de recursos
- Simulação de execução

### Classes de Suporte

- **SistemaProducao**: Interface interativa com menu principal

## 📐 Regras do Sistema

### Fases e Subfases
- **3 fases**: 0, 1, 2
- **3 subfases por fase**: 0, 1, 2
- **Total de combinações**: 9

### Recursos
- **Range**: 00 a 26 (27 recursos globais)
- **Alocação por OP**: 1 a 3 recursos
- **Modo de alocação**:
  - **A** → 1 recurso
  - **B** → 2 recursos (acumulativo)
  - **C** → 3 recursos (acumulativo)

### Regra de Acumulação
O recurso base define o início, e os adicionais são sequenciais:

| Modo | Base | Resultado |
|------|------|-----------|
| A | 05 | [05] |
| B | 05 | [05, 06] |
| C | 05 | [05, 06, 07] |

### Validações
✓ Formato de OP válido (10 caracteres)
✓ Fase e subfase entre 0-2
✓ Modo (A, B, C)
✓ Recurso base entre 00-26
✓ Sem overflow (ex: base 25 com modo C é inválido)

## 🚀 Como Usar

### Execução do Sistema

```bash
python Compact_Encoding_System.py
```

### Menu Principal

```
===============================================================================
SISTEMA DE PRODUÇÃO - CODIFICAÇÃO COMPACTA
===============================================================================

1. Criar Ordem de Fabricação (OF)
2. Criar Ordem de Produção (OP)
3. Validar OP
4. Simular Execução de OP
5. Converter OP para Lista de Recursos
6. Listar Estrutura da Linha
7. Visualizar Todas as Ordens
8. Sair
===============================================================================
```

### Exemplos de Uso

#### 1️⃣ Criar Ordem de Fabricação

```
--- CRIAR ORDEM DE FABRICAÇÃO ---
Ano (00-99): 25
Tipo de linha: 0=Normal, 1=Premium
Tipo (0 ou 1): 1
Código do cliente (00-99): 12

✓ OF criada com sucesso!
  Código: 25112
```

#### 2️⃣ Criar Ordem de Produção

```
--- CRIAR ORDEM DE PRODUÇÃO ---
OFs disponíveis:
  1. 25112

Escolha uma OF (número): 1
Fase (0-2): 1
Subfase (0-2): 2
Modo de recurso: A=1 recurso, B=2 recursos, C=3 recursos
Modo (A, B ou C): B
Recurso base (00-26): 05

✓ OP criada com sucesso!
  Código: 2511212B05
  Recursos: [5, 6]
```

#### 3️⃣ Validar OP

```
--- VALIDAR ORDEM DE PRODUÇÃO ---
Formato esperado: YYTCCFSMRB (10 caracteres)

Digite o código da OP (ex: 2512312B05): 2511212B05

✓ OP válida: 2511212B05
  Recursos utilizados: [5, 6]
```

#### 4️⃣ Simular Execução de OP

```
--- SIMULAR EXECUÇÃO DE OP ---
OPs disponíveis:
  1. 2511212B05

Escolha uma OP (número): 1

======================================================================
SIMULAÇÃO DE EXECUÇÃO
======================================================================
Código OP: 2511212B05
Fase: 1
Subfase: 2
Modo: B (2 recursos (acumulativo))
Recurso Base: 05
Número de Recursos: 2
Recursos Utilizados: [5, 6]
Status: Criada
======================================================================
```

## 📊 Estrutura de Dados

### Ordem de Fabricação
```python
of = OrdemFabricacao(ano=25, tipo_linha=1, codigo_cliente=12)
print(of.gerar_codigo())  # "25112"
```

### Ordem de Produção
```python
op = OrdemProducao(
    codigo_of="25112",
    fase=1,
    subfase=2,
    modo_recurso="B",
    recurso_base=5
)
print(op.gerar_codigo())  # "2511212B05"
print(op.obter_recursos())  # [5, 6]
```

### Simulação
```python
sim = op.simular_execucao()
# Retorna dict com informações completas da execução
```

## ✅ Funcionalidades Implementadas

| Funcionalidade | Status |
|---|---|
| Criar Ordem de Fabricação (OF) | ✓ Completo |
| Gerar Ordem de Produção (OP) | ✓ Completo |
| Validar OP | ✓ Completo |
| Converter OP em lista de recursos | ✓ Completo |
| Listar estrutura da linha | ✓ Completo |
| Simular execução de OP | ✓ Completo |
| Interface interativa | ✓ Completo |
| Validações obrigatórias | ✓ Completo |
| OOP com classes | ✓ Completo |

## 🔍 Tratamento de Erros

O sistema valida todos os inputs e fornece mensagens de erro claras:

```python
try:
    op = OrdemProducao("25112", 1, 2, "B", 25)
except ValueError as e:
    print(f"Erro: {e}")
    # Erro: Overflow de recursos: base 25 com modo B ultrapassaria 26
```

## 📝 Exemplos de Códigos Válidos

### OFs Válidas
- **25001**: 2025, Normal, Cliente 01
- **24102**: 2024, Premium, Cliente 02
- **2655**: 2026, Normal, Cliente 55

### OPs Válidas
- **2500100A00**: OF 25001, Fase 0, Subfase 0, Modo A, Recurso 00
- **2510212B10**: OF 25102, Fase 1, Subfase 2, Modo B, Recurso 10
- **2510222C24**: OF 25102, Fase 2, Subfase 2, Modo C, Recurso 24

### OPs Inválidas
- **2500100A27**: Recurso base 27 > 26 ❌
- **2510212B26**: Modo B necessita 2 recursos, base 26 → overflow ❌
- **2510212D10**: Modo D não existe ❌

## 🛠️ Dependências

Apenas biblioteca padrão do Python:
- `datetime`: Para timestamps das ordens
- `typing`: Para type hints
- `os`: Para limpeza de tela

## 📱 Interface do Usuário

- Menu interativo e intuitivo
- Feedback visual com símbolos (✓, ✗)
- Separadores visuais para melhor legibilidade
- Suporte para interrupção por Ctrl+C
- Validação completa de inputs

## 🎯 Próximas Melhorias Possíveis

- [ ] Persistência em banco de dados (SQLite/PostgreSQL)
- [ ] Relatórios em PDF
- [ ] API REST para integração com sistemas ERP
- [ ] Dashboard em tempo real
- [ ] Histórico de execução
- [ ] Agendamento automático de OPs
- [ ] Análise de desempenho de recursos

## 👨‍💻 Autor

Sistema de Produção - 2026

## 📄 Licença

Desenvolvido para fins educacionais em TCC de IA em VS Code.


# Quick Start - Sistema de Codificação Compacta ERP/MES

## 📋 Requisitos

- Python 3.7+
- Nenhuma dependência externa (usa apenas bibliotecas padrão)

## 🚀 Instalação

### 1. Clone ou Copie os Arquivos

```bash
# Copie os arquivos para seu diretório
cp sistema_producao.py seu_diretorio/
cp exemplos.py seu_diretorio/
cp testes.py seu_diretorio/
```

### 2. Verifique a Instalação do Python

```bash
python --version
# ou
python3 --version
```

## 🏃 Como Executar

### 1️⃣ Interface Interativa (Menu Principal)

```bash
python sistema_producao.py
```

**O que acontece:**
- Abre um menu interativo no terminal
- Permite criar OFs, gerar OPs, validar e simular
- Interface amigável com validações em tempo real

**Exemplo de sessão:**
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

Escolha uma opção (1-7): 1

--- CRIAR ORDEM DE FABRICAÇÃO ---

Ano (00-99): 25
Tipo de Linha:
  0 = Normal
  1 = Premium
Escolha o tipo (0 ou 1): 1
Código do Cliente (00-99): 23

✓ OF criada com sucesso: 25123
```

### 2️⃣ Exemplos Automáticos

```bash
python exemplos.py
```

**O que mostra:**
- 6 exemplos completos do sistema funcionando
- Demonstração de validações
- Casos de erro tratados
- Fluxos completos de produção

**Exemplo de saída:**
```
======================================================================
EXEMPLO 1: CRIAÇÃO DE ORDEM DE FABRICAÇÃO (OF)
======================================================================

Criando OF com parâmetros:
  Ano: 25 (2025)
  Tipo: 1 (Premium)
  Cliente: 12

Validação: OF válida
Código gerado: 25112

OF[25112] - Tipo: Premium, Cliente: 12
```

### 3️⃣ Testes Unitários

```bash
python testes.py
```

**O que executa:**
- Mais de 50 testes unitários
- Valida todas as regras de negócio
- Testa casos extremos e bordas
- Testes de integração

**Exemplo de saída:**
```
test_ao_invalido_acima_99 (testes.TesteOrdemFabricacao) ... ok
test_ao_invalido_negativo (testes.TesteOrdemFabricacao) ... ok
test_ao_tipo_invalido (testes.TesteOrdemFabricacao) ... ok
...
======================================================================
RESUMO DOS TESTES
======================================================================
Testes executados: 54
Sucessos: 54
Falhas: 0
Erros: 0
======================================================================
```

### 4️⃣ Uso Programático

```python
from sistema_producao import OrdemFabricacao, OrdemProducao, LinhaProducao

# Criar uma linha
linha = LinhaProducao()

# Criar OF
of = linha.criar_ordem_fabricacao(25, 1, 23)
print(f"OF criada: {of}")

# Gerar OP
op = linha.gerar_ordem_producao(of, 1, 2, 'B', 5)
print(f"OP gerada: {op}")

# Validar OP
valida, detalhes = linha.validar_ordem_producao(op)
print(f"Válida: {valida}")
print(f"Recursos: {detalhes['recursos_utilizados']}")

# Simular
resultado = linha.simular_execucao_op(op)
print(f"Status: {resultado['status']}")
```

## 📊 Estrutura dos Arquivos

```
Claude/
├── sistema_producao.py          # ← Arquivo principal
├── exemplos.py                  # ← Demonstrações
├── testes.py                    # ← Testes unitários
├── QUICK_START.md               # ← Este arquivo
└── README.md                    # ← Documentação completa
```

## 🔍 Entendendo o Formato

### OF (Ordem de Fabricação) - YYTCC

```
Exemplo: 25123

25   → Ano (2025)
1    → Tipo (Premium)
23   → Cliente 23
```

### OP (Ordem de Produção) - YYTCCFSMRR

```
Exemplo: 2512312B05

25123 → OF (Ano=25, Tipo=1, Cliente=23)
1     → Fase 1
2     → Subfase 2
B     → Modo B (2 recursos)
05    → Recurso base 05
```

## 🧪 Teste Rápido

### Teste 1: OP Válida

```python
from sistema_producao import OrdemProducao

op = OrdemProducao("2512312B05")
print(op.valido)              # True
print(op.obter_recursos())    # [5, 6]
```

### Teste 2: OP Inválida (Subfase)

```python
op = OrdemProducao("2512315A05")
print(op.valido)              # False
print(op.mensagem_erro)       # "Subfase deve estar entre 0 e 2"
```

### Teste 3: OP Inválida (Overflow)

```python
op = OrdemProducao("2512322C25")
print(op.valido)              # False
print(op.mensagem_erro)       # "Overflow de recursos: base 25 com modo C..."
```

## 🎯 Casos de Uso Comuns

### 1. Criar e Validar uma Ordem

```bash
python sistema_producao.py
# Menu → 1 → Criar OF
# Menu → 2 → Gerar OP
# Menu → 3 → Validar OP
```

### 2. Simular Produção

```bash
python sistema_producao.py
# Menu → 4 → Simular execução
# Verá quais recursos serão alocados
```

### 3. Ver Estrutura da Linha

```bash
python sistema_producao.py
# Menu → 5 → Listar estrutura
# Exibe fases, subfases, modos, recursos
```

### 4. Histórico de Operações

```bash
python sistema_producao.py
# Menu → 6 → Ver histórico
# Lista todas as simulações realizadas
```

## ⚙️ Funcionalidades Principais

| Função | Descrição |
|--------|-----------|
| `criar_ordem_fabricacao()` | Cria uma OF (YYTCC) |
| `gerar_ordem_producao()` | Gera uma OP (YYTCCFSMRR) |
| `validar_ordem_producao()` | Valida uma OP |
| `obter_recursos()` | Lista recursos utilizados |
| `simular_execucao_op()` | Simula alocação de recursos |
| `listar_estrutura()` | Mostra info da linha |

## 🔐 Validações Implementadas

✓ Formato de OF (YYTCC)
✓ Formato de OP (YYTCCFSMRR)
✓ Fase e subfase (0-2)
✓ Modo (A, B, C)
✓ Recurso base (00-26)
✓ Sem overflow de recursos
✓ Sequência correta de recursos

## 📝 Exemplos de Saída

### OP Válida

```
OP[2512312B05] ✓ VÁLIDA
  OF: 25123 | Fase: 1 | Subfase: 2
  Modo: B | Recurso Base: 05
  Recursos Utilizados: [05, 06]
```

### OP Inválida

```
OP[2512325C25] ✗ INVÁLIDA
  Erro: Overflow de recursos: base 25 com modo C 
        tentaria usar recurso 27 (máximo: 26)
```

## 🐛 Solução de Problemas

### Python não encontrado

```bash
# Tente python3 em vez de python
python3 sistema_producao.py
```

### Erro de módulo não encontrado

```bash
# Verifique se está no diretório correto
cd caminho/para/Claude
python sistema_producao.py
```

### Caracteres especiais no terminal

```bash
# Alguns terminais não suportam caracteres especiais
# A aplicação funcionará normalmente, apenas sem alguns símbolos
```

## 📚 Mais Informações

- Leia [README.md](README.md) para documentação completa
- Veja [exemplos.py](exemplos.py) para mais casos de uso
- Consulte [testes.py](testes.py) para validações detalhadas

## ✨ Próximos Passos

1. Execute `python sistema_producao.py` para explorar
2. Crie algumas OFs e OPs
3. Teste as validações
4. Simule execuções
5. Leia a documentação para detalhes

## 📞 Suporte

Para dúvidas:
1. Verifique os exemplos em `exemplos.py`
2. Consulte a documentação em `README.md`
3. Execute os testes para ver funcionamento esperado

---

**Pronto para começar?** Execute:

```bash
python sistema_producao.py
```


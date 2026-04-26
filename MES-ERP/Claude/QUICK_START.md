# Guia de Início Rápido - Sistema de Codificação Compacta

## 🚀 Como Iniciar

### Opção 1: Executar o Sistema Interativo

```bash
python Compact_Encoding_System.py
```

O sistema abrirá um menu interativo no terminal com as seguintes opções:

### Opção 2: Usar Diretamente no Python

```python
from Compact_Encoding_System import OrdemFabricacao, OrdemProducao, LinhaProducao

# Criar uma linha de produção
linha = LinhaProducao("Minha Linha")

# Criar Ordem de Fabricação
of = linha.criar_ordem_fabricacao(ano=25, tipo_linha=1, codigo_cliente=12)
print(of.gerar_codigo())  # Saída: 25112

# Criar Ordem de Produção
op = linha.criar_ordem_producao(
    codigo_of="25112",
    fase=1,
    subfase=2,
    modo_recurso="B",
    recurso_base=5
)
print(op.gerar_codigo())  # Saída: 2511212B05
print(op.obter_recursos())  # Saída: [5, 6]
```

### Opção 3: Executar Testes Automatizados

```bash
python test_compact_encoding.py
```

## 📝 Exemplos de Uso Prático

### Exemplo 1: Criar uma Linha Completa

```python
from Compact_Encoding_System import LinhaProducao

# Inicializar
linha = LinhaProducao("Linha A")

# Criar várias OFs
of1 = linha.criar_ordem_fabricacao(25, 0, 1)   # Cliente Normal
of2 = linha.criar_ordem_fabricacao(25, 1, 5)   # Cliente Premium

# Criar OPs para cada OF
op1 = linha.criar_ordem_producao("25001", 0, 0, "A", 0)
op2 = linha.criar_ordem_producao("25001", 1, 1, "C", 20)
op3 = linha.criar_ordem_producao("25015", 2, 2, "B", 10)

# Visualizar estrutura
print(linha.listar_estrutura())
```

### Exemplo 2: Validar e Processar OP

```python
# Validar uma OP existente
codigo_op = "2511212B05"
valido, mensagem = linha.validar_ordem_producao(codigo_op)

if valido:
    print(f"✓ {mensagem}")
    
    # Converter para recursos
    status, recursos = linha.converter_op_para_recursos(codigo_op)
    print(f"Recursos: {recursos}")
```

### Exemplo 3: Simular Execução

```python
# Obter uma OP criada
op = linha.ordens_producao[0]

# Executar simulação
resultado = op.simular_execucao()

print(f"OP: {resultado['codigo_op']}")
print(f"Modo: {resultado['modo']} ({resultado['modo_descricao']})")
print(f"Recursos: {resultado['recursos_utilizados']}")
print(f"Status: {resultado['status']}")
```

## 🎯 Fluxo Típico de Uso

```
1. Criar Linha de Produção
   ↓
2. Criar Ordem de Fabricação (OF)
   ↓
3. Criar Ordem de Produção (OP) baseada na OF
   ↓
4. Validar a OP
   ↓
5. Simular execução da OP
   ↓
6. Ver resultados (recursos utilizados, etc)
```

## 🔍 Formato de Códigos

### Ordem de Fabricação (OF): YYTCC
```
25112
├─ 25 = Ano 2025
├─ 1  = Tipo Premium
└─ 12 = Cliente 12
```

### Ordem de Produção (OP): YYTCCFSMRB
```
2511212B05
├─ 25112 = Código OF
├─ 1     = Fase 1
├─ 2     = Subfase 2
├─ B     = Modo B (2 recursos)
└─ 05    = Recurso base 05
          → Recursos utilizados: [05, 06]
```

## ⚡ Comandos Rápidos

### Criar e testar localmente:

```python
# Script rápido
from Compact_Encoding_System import OrdemFabricacao, OrdemProducao

# OF simples
of = OrdemFabricacao(25, 1, 99)
print(f"OF: {of.gerar_codigo()}")

# OP simples
op = OrdemProducao("25199", 0, 0, "A", 0)
print(f"OP: {op.gerar_codigo()}")
print(f"Recursos: {op.obter_recursos()}")
```

## 📊 Casos de Teste Importantes

### ✓ Válidas
- `2500100A00` - OF 25001, Fase 0, Subfase 0, Modo A, Recurso 0
- `2510212B10` - OF 25102, Fase 1, Subfase 2, Modo B, Recurso 10
- `2501222C24` - OF 25012, Fase 2, Subfase 2, Modo C, Recurso 24

### ✗ Inválidas
- `2500100A27` - Recurso 27 > máximo 26
- `2510212B26` - Modo B precisa 2 recursos: 26 + overflow
- `2501222C24` - Modo C precisa 3 recursos: 24+25+26 OK! (Essa é válida)
- `2501222C25` - Modo C: 25+26+27 > 26 (inválida)

## 🐛 Troubleshooting

### Erro: "Recuso base inválido"
```python
# ✗ Errado
op = OrdemProducao("25112", 0, 0, "A", 30)  # 30 > 26

# ✓ Certo
op = OrdemProducao("25112", 0, 0, "A", 20)  # 20 ≤ 26
```

### Erro: "Overflow de recursos"
```python
# ✗ Errado
op = OrdemProducao("25112", 0, 0, "C", 26)  # 26+27+28 > 26

# ✓ Certo
op = OrdemProducao("25112", 0, 0, "C", 24)  # 24+25+26 = OK
```

### Erro: "Modo inválido"
```python
# ✗ Errado
op = OrdemProducao("25112", 0, 0, "X", 5)  # X não existe

# ✓ Certo
op = OrdemProducao("25112", 0, 0, "A", 5)  # A, B, ou C
```

## 📚 Estrutura de Arquivos

```
MES-ERP/
├── Compact_Encoding_System.py      # Sistema principal
├── test_compact_encoding.py         # Suite de testes automatizados
├── README_COMPACT_ENCODING.md       # Documentação completa
└── QUICK_START.md                   # Este arquivo
```

## 🎓 Conceitos-Chave

| Conceito | Descrição |
|----------|-----------|
| **OF** | Ordem de Fabricação - Identifica o cliente e tipo de produção |
| **OP** | Ordem de Produção - Define fase, subfase e recursos específicos |
| **Fase** | Etapa principal da produção (0-2) |
| **Subfase** | Sub-etapa dentro de uma fase (0-2) |
| **Modo** | Define quantos recursos serão utilizados (A=1, B=2, C=3) |
| **Recurso** | Máquina ou equipamento identificado por número (0-26) |

## 💡 Dicas

1. **Sempre crie uma OF antes de uma OP**
2. **Use modo A para produção simplificada, modo C para operações complexas**
3. **Valide OPs antes de simular execução**
4. **Combine múltiplas OPs para ver padrões de uso**
5. **Exporte dados das simulações para análise posterior**

---

**Pronto para começar! 🚀**

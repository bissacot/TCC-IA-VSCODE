
# 💎 Dicas e Truques - Uso Avançado

## 🎯 Para Usuários Avançados

Este documento contém dicas, truques e técnicas avançadas para maximizar o uso do sistema.

---

## 🐍 Uso Programático Avançado

### 1. Criar Factory de OPs em Lote

```python
from sistema_producao import LinhaProducao

def criar_lote_ops(linha: LinhaProducao, of: str, quantidade: int):
    """Cria múltiplas OPs automaticamente"""
    ops = []
    
    for i in range(quantidade):
        fase = i % 3
        subfase = (i // 3) % 3
        modo = ['A', 'B', 'C'][i % 3]
        recurso = (5 + i) % 27
        
        op = linha.gerar_ordem_producao(of, fase, subfase, modo, recurso)
        if op:
            ops.append(op)
    
    return ops

# Uso
linha = LinhaProducao()
of = linha.criar_ordem_fabricacao(25, 1, 50)
ops = criar_lote_ops(linha, of, 30)
print(f"Criadas {len(ops)} OPs")
```

### 2. Validação em Lote

```python
from sistema_producao import OrdemProducao

def validar_lote(codigos_op: list) -> dict:
    """Valida múltiplas OPs e retorna relatório"""
    resultado = {
        'total': len(codigos_op),
        'validas': 0,
        'invalidas': 0,
        'erros': {}
    }
    
    for codigo in codigos_op:
        op = OrdemProducao(codigo)
        if op.valido:
            resultado['validas'] += 1
        else:
            resultado['invalidas'] += 1
            resultado['erros'][codigo] = op.mensagem_erro
    
    return resultado

# Uso
ops = [f"2512300A{i:02d}" for i in range(27)]
relatorio = validar_lote(ops)
print(f"Válidas: {relatorio['validas']}, Inválidas: {relatorio['invalidas']}")
```

### 3. Simular Cenários Complexos

```python
def simular_cenario_estresse():
    """Simula situação de alta carga"""
    from sistema_producao import LinhaProducao, OrdemProducao
    import time
    
    linha = LinhaProducao()
    ops_para_simular = []
    
    # Criar múltiplas OFs e OPs
    for cliente in range(1, 11):
        of = linha.criar_ordem_fabricacao(25, cliente % 2, cliente)
        
        for fase in range(3):
            op = linha.gerar_ordem_producao(of, fase, 0, 'B', 10)
            if op:
                ops_para_simular.append(op)
    
    # Simular todas
    inicio = time.time()
    sucessos = 0
    
    for op in ops_para_simular:
        resultado = linha.simular_execucao_op(op)
        if resultado['status'] == 'SUCESSO':
            sucessos += 1
    
    tempo = time.time() - inicio
    
    print(f"Simulações: {sucessos}/{len(ops_para_simular)}")
    print(f"Tempo total: {tempo:.3f}s")
    print(f"Média: {tempo/len(ops_para_simular):.4f}s por OP")

# Executar
simular_cenario_estresse()
```

---

## 🔍 Análise e Relatórios

### 4. Gerar Relatório de Utilizações

```python
def relatorio_utilizacao_recursos(linha):
    """Análise detalhada de recursos"""
    
    from collections import defaultdict
    
    utilizacao = defaultdict(int)
    
    # Analisar todas as simulações
    for sim in linha.simulacoes:
        if sim['status'] == 'SUCESSO':
            for recurso in sim['recursos_alocados']:
                utilizacao[recurso['id']] += 1
    
    # Ordenar por uso
    ordenado = sorted(utilizacao.items(), key=lambda x: x[1], reverse=True)
    
    print("RELATÓRIO DE UTILIZAÇÃO DE RECURSOS")
    print("=" * 50)
    
    total_alocacoes = sum(v for k, v in ordenado)
    
    for recurso_id, count in ordenado:
        percentual = (count / total_alocacoes) * 100
        barra = "█" * int(percentual / 5)
        print(f"{recurso_id}: {barra} {percentual:.1f}% ({count}x)")
    
    print(f"\nTotal de alocações: {total_alocacoes}")
    print(f"Recursos utilizados: {len(utilizacao)}/27")

# Uso
linha = LinhaProducao()
# ... criar e simular algumas OPs ...
relatorio_utilizacao_recursos(linha)
```

### 5. Análise de Padrões

```python
def analisar_padroes(linha):
    """Identifica padrões nas operações"""
    
    from collections import Counter
    
    # Contar modos utilizados
    modos = Counter()
    fases = Counter()
    
    for op in linha.ordens_producao:
        op_obj = OrdemProducao(op.codigo_original)
        modos[op_obj.modo] += 1
        fases[op_obj.fase] += 1
    
    print("ANÁLISE DE PADRÕES")
    print("=" * 50)
    
    print("\nModos mais utilizados:")
    for modo, count in modos.most_common():
        print(f"  Modo {modo}: {count}x ({count/len(linha.ordens_producao)*100:.1f}%)")
    
    print("\nFases mais utilizadas:")
    for fase, count in fases.most_common():
        print(f"  Fase {fase}: {count}x ({count/len(linha.ordens_producao)*100:.1f}%)")
```

---

## 🚀 Otimizações de Performance

### 6. Cache de Validações

```python
from functools import lru_cache
from sistema_producao import OrdemProducao

@lru_cache(maxsize=1000)
def validar_op_cached(codigo: str) -> bool:
    """Validação com cache"""
    op = OrdemProducao(codigo)
    return op.valido

# Benchmarking
import time

codigos = [f"2512300B{i:02d}" for i in range(27)] * 100

# Sem cache
inicio = time.time()
for codigo in codigos:
    validar_op_cached.cache_clear()
    validar_op_cached(codigo)
tempo_sem_cache = time.time() - inicio

# Com cache
inicio = time.time()
for codigo in codigos:
    validar_op_cached(codigo)
tempo_com_cache = time.time() - inicio

print(f"Sem cache: {tempo_sem_cache:.3f}s")
print(f"Com cache: {tempo_com_cache:.3f}s")
print(f"Speedup: {tempo_sem_cache/tempo_com_cache:.1f}x")
```

### 7. Processamento Paralelo

```python
from concurrent.futures import ThreadPoolExecutor
from sistema_producao import LinhaProducao, OrdemProducao

def simular_op_paralelo(ops: list, max_workers: int = 4):
    """Simula múltiplas OPs em paralelo"""
    linha = LinhaProducao()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        resultados = list(executor.map(linha.simular_execucao_op, ops))
    
    sucessos = sum(1 for r in resultados if r['status'] == 'SUCESSO')
    print(f"Sucesso: {sucessos}/{len(ops)}")
    
    return resultados

# Uso
ops = [f"2512300B{i:02d}" for i in range(27)]
resultados = simular_op_paralelo(ops)
```

---

## 🎨 Personalização Avançada

### 8. Estender OrdemProducao

```python
from sistema_producao import OrdemProducao

class OrdenProducaoEstendida(OrdemProducao):
    """Versão estendida com funcionalidades adicionais"""
    
    def __init__(self, codigo_op: str):
        super().__init__(codigo_op)
        self.prioridade = 'normal'
        self.tags = set()
    
    def definir_prioridade(self, nivel: str):
        """Define prioridade (baixa, normal, alta)"""
        if nivel in ['baixa', 'normal', 'alta']:
            self.prioridade = nivel
        else:
            raise ValueError(f"Prioridade inválida: {nivel}")
    
    def adicionar_tag(self, tag: str):
        """Adiciona uma tag descritiva"""
        self.tags.add(tag)
    
    def obter_info_estendida(self) -> dict:
        """Retorna informações estendidas"""
        info = self.obter_detalhes()
        info['prioridade'] = self.prioridade
        info['tags'] = list(self.tags)
        return info

# Uso
op = OrdenProducaoEstendida("2512312B05")
op.definir_prioridade('alta')
op.adicionar_tag('cliente_vip')
op.adicionar_tag('express')
print(op.obter_info_estendida())
```

### 9. Logging Personalizado

```python
import logging
from datetime import datetime

class LoggerProducao:
    def __init__(self, arquivo: str = "producao.log"):
        self.logger = logging.getLogger('producao')
        self.logger.setLevel(logging.DEBUG)
        
        # Handler para arquivo
        fh = logging.FileHandler(arquivo)
        fh.setLevel(logging.DEBUG)
        
        # Handler para console
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
    
    def log_criacao_op(self, codigo: str, sucesso: bool):
        nivel = logging.INFO if sucesso else logging.WARNING
        self.logger.log(nivel, f"OP criada: {codigo} - {'✓' if sucesso else '✗'}")
    
    def log_simulacao(self, codigo: str, status: str):
        self.logger.info(f"Simulação {codigo}: {status}")

# Uso
logger = LoggerProducao()
logger.log_criacao_op("2512312B05", True)
```

---

## 📊 Integração com Pandas

### 10. Análise com Pandas

```python
import pandas as pd
from sistema_producao import LinhaProducao

def exportar_para_dataframe(linha: LinhaProducao) -> pd.DataFrame:
    """Exporta simulações para DataFrame pandas"""
    
    dados = []
    
    for sim in linha.simulacoes:
        op = sim['op']
        fase = op[5]
        subfase = op[6]
        modo = op[7]
        
        dados.append({
            'op': op,
            'timestamp': sim['timestamp'],
            'status': sim['status'],
            'fase': int(fase),
            'subfase': int(subfase),
            'modo': modo,
            'recursos_alocados': len(sim['recursos_alocados'])
        })
    
    return pd.DataFrame(dados)

# Uso
linha = LinhaProducao()
# ... criar e simular OPs ...
df = exportar_para_dataframe(linha)

# Análise
print(df.groupby('modo')['recursos_alocados'].mean())
print(df['status'].value_counts())
print(df.groupby('fase').size())
```

---

## 🔒 Validação Avançada

### 11. Validador Customizado

```python
from sistema_producao import OrdemProducao

class ValidadorOPAvancado:
    def __init__(self):
        self.regras_negocio = []
    
    def adicionar_regra(self, nome: str, funcao):
        """Adiciona regra de negócio customizada"""
        self.regras_negocio.append((nome, funcao))
    
    def validar(self, codigo: str) -> dict:
        """Valida OP com regras customizadas"""
        op = OrdemProducao(codigo)
        
        resultado = {
            'valida_basica': op.valido,
            'regras': {}
        }
        
        for nome, funcao in self.regras_negocio:
            resultado['regras'][nome] = funcao(op)
        
        return resultado

# Uso
validador = ValidadorOPAvancado()

# Adicionar regra: Modo C só para clientes premium
def apenas_premium_modo_c(op):
    if op.modo == 'C':
        cliente = int(op.of_codigo[3:5])
        return cliente > 50  # Premium (assumindo cliente > 50)
    return True

validador.adicionar_regra("premium_modo_c", apenas_premium_modo_c)

resultado = validador.validar("2512312C05")
print(resultado)
```

---

## 💾 Persistência Simples

### 12. Salvar/Carregar Estado com JSON

```python
import json
from pathlib import Path

def salvar_estado_json(linha, arquivo: str = "estado.json"):
    """Salva estado em JSON"""
    estado = {
        'ofs': {
            codigo: {
                'ano': of.ano,
                'tipo': of.tipo,
                'cliente': of.codigo_cliente
            }
            for codigo, of in linha.ordens_fabricacao.items()
        },
        'simulacoes_total': len(linha.simulacoes),
        'ops_total': len(linha.ordens_producao)
    }
    
    with open(arquivo, 'w') as f:
        json.dump(estado, f, indent=2, default=str)
    
    print(f"✓ Estado salvo em {arquivo}")

def carregar_estado_json(linha, arquivo: str = "estado.json"):
    """Carrega estado de JSON"""
    if not Path(arquivo).exists():
        print(f"✗ Arquivo {arquivo} não encontrado")
        return
    
    with open(arquivo) as f:
        estado = json.load(f)
    
    # Recriar OFs
    for codigo, dados in estado['ofs'].items():
        linha.criar_ordem_fabricacao(
            dados['ano'], dados['tipo'], dados['cliente']
        )
    
    print(f"✓ Estado carregado de {arquivo}")

# Uso
linha = LinhaProducao()
# ... fazer operações ...
salvar_estado_json(linha)

# Depois...
nova_linha = LinhaProducao()
carregar_estado_json(nova_linha)
```

---

## 🎯 Métodos de Debug

### 13. Inspeção Profunda

```python
def inspecionar_op_completa(codigo: str):
    """Inspeciona todos os aspectos de uma OP"""
    from sistema_producao import OrdemProducao
    
    print(f"\n{'='*60}")
    print(f"INSPEÇÃO COMPLETA DA OP: {codigo}")
    print(f"{'='*60}\n")
    
    op = OrdemProducao(codigo)
    
    # Info básica
    print("INFORMAÇÕES BÁSICAS:")
    print(f"  Válida: {op.valido}")
    print(f"  Mensagem: {op.mensagem_erro}")
    
    if not op.valido:
        print("\nERRO DETECTADO - Inspeção parada")
        return
    
    # Componentes
    print("\nCOMPONENTES:")
    print(f"  OF: {op.of_codigo}")
    print(f"  Fase: {op.fase}")
    print(f"  Subfase: {op.subfase}")
    print(f"  Modo: {op.modo}")
    print(f"  Recurso Base: {op.recurso_base:02d}")
    
    # Recursos
    print("\nRECURSOS:")
    for i, recurso in enumerate(op.recursos_utilizados, 1):
        print(f"  {i}. {recurso:02d}")
    
    # Detalhes
    print("\nDETALHES COMPLETOS:")
    detalhes = op.obter_detalhes()
    for chave, valor in detalhes.items():
        print(f"  {chave}: {valor}")
    
    print(f"\n{'='*60}\n")

# Uso
inspecionar_op_completa("2512312B05")
```

---

## 🎓 Casos de Uso Avançados

### 14. Reproduzir Erros

```python
def testar_casos_problematicos():
    """Testa casos que costumam gerar erros"""
    
    from sistema_producao import OrdemProducao
    
    casos = [
        # (codigo, descricao_esperada)
        ("2512325C25", "Overflow Modo C"),
        ("2512315A05", "Subfase inválida"),
        ("251210XA05", "Modo inválido"),
        ("25121099B05", "Recurso inválido"),
        ("251210A05", "Formato curto"),
    ]
    
    print("TESTE DE CASOS PROBLEMÁTICOS")
    print("=" * 60)
    
    for codigo, descricao in casos:
        op = OrdemProducao(codigo)
        status = "✓" if not op.valido else "✗"
        print(f"{status} {descricao}")
        print(f"   Código: {codigo}")
        print(f"   Erro: {op.mensagem_erro}\n")

# Usar
testar_casos_problematicos()
```

---

## 📚 Referência Rápida de Snippets

### Criar OF
```python
of = linha.criar_ordem_fabricacao(25, 1, 42)
```

### Gerar OP
```python
op = linha.gerar_ordem_producao(of, 1, 2, 'B', 5)
```

### Validar OP
```python
valida, detalhes = linha.validar_ordem_producao(op)
```

### Simular OP
```python
resultado = linha.simular_execucao_op(op)
```

### Obter Recursos
```python
recursos = OrdemProducao(op).obter_recursos()
```

### Listar Estrutura
```python
print(linha.listar_estrutura())
```

---

## 🚀 Performance Tips

1. **Use cache para validações repetidas**
2. **Process em paralelo para grandes volumes**
3. **Exportar para DataFrame para análises complexas**
4. **Usar logging estruturado**
5. **Implement batch operations**

---

## 🎯 Conclusão

Estas técnicas permitem:
- ✅ Análises profundas
- ✅ Automação completa
- ✅ Extensão funcional
- ✅ Integração com outros sistemas
- ✅ Otimização de performance

**Explore, experimente e customize!** 🚀


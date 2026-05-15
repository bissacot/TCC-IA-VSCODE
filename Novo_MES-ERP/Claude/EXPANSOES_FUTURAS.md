
# 🚀 Plano de Expansão - Melhorias Futuras

## 🎯 Visão Estratégica

Este sistema implementa um protótipo funcional de um ERP/MES para linhas de produção. A arquitetura foi projetada para ser facilmente extensível.

---

## 📋 Fases de Expansão

### FASE 1: Dados Persistentes (Priority: 🔴 ALTA)

**Objetivo:** Salvar e recuperar dados entre sessões

**Implementações Sugeridas:**

#### 1.1 SQLite Database
```python
# exemplo: adicionar em LinhaProducao
import sqlite3

class LinhaProducao:
    def __init__(self, nome: str, db_file: str = "producao.db"):
        self.db = sqlite3.connect(db_file)
        self._criar_tabelas()
    
    def _criar_tabelas(self):
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS ordens_fabricacao (
                id INTEGER PRIMARY KEY,
                codigo TEXT UNIQUE,
                ano INTEGER,
                tipo INTEGER,
                cliente INTEGER,
                criada_em TIMESTAMP
            )
        ''')
    
    def salvar_of(self, of: OrdemFabricacao):
        self.db.execute('''
            INSERT INTO ordens_fabricacao
            (codigo, ano, tipo, cliente, criada_em)
            VALUES (?, ?, ?, ?, ?)
        ''', (of.gerar_codigo(), of.ano, of.tipo, of.codigo_cliente, of.criada_em))
        self.db.commit()
```

#### 1.2 JSON File Storage
```python
import json
from pathlib import Path

class GerenciadorDados:
    def __init__(self, pasta: str = "dados"):
        self.pasta = Path(pasta)
        self.pasta.mkdir(exist_ok=True)
    
    def salvar_estado(self, linha: LinhaProducao):
        dados = {
            'ofs': {k: {...} for k, v in linha.ordens_fabricacao.items()},
            'ops': [...],
            'timestamp': datetime.now().isoformat()
        }
        with open(self.pasta / "estado.json", "w") as f:
            json.dump(dados, f, indent=2)
    
    def carregar_estado(self) -> dict:
        arquivo = self.pasta / "estado.json"
        if arquivo.exists():
            with open(arquivo) as f:
                return json.load(f)
        return None
```

**Tempo Estimado:** 4-6 horas

---

### FASE 2: API REST (Priority: 🔴 ALTA)

**Objetivo:** Expor funcionalidades via HTTP para integração externa

**Framework Sugerido:** Flask ou FastAPI

#### 2.1 Implementação com FastAPI
```python
# main_api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="ERP-MES API")
linha = LinhaProducao()

class OfRequest(BaseModel):
    ano: int
    tipo: int
    codigo_cliente: int

@app.post("/api/v1/ordem-fabricacao")
async def criar_of(request: OfRequest):
    of_codigo = linha.criar_ordem_fabricacao(
        request.ano, request.tipo, request.codigo_cliente
    )
    if not of_codigo:
        raise HTTPException(status_code=400, detail="OF inválida")
    return {"codigo": of_codigo}

@app.post("/api/v1/ordem-producao")
async def gerar_op(of_codigo: str, fase: int, subfase: int, 
                   modo: str, recurso_base: int):
    op_codigo = linha.gerar_ordem_producao(
        of_codigo, fase, subfase, modo, recurso_base
    )
    if not op_codigo:
        raise HTTPException(status_code=400, detail="OP inválida")
    return {"codigo": op_codigo}

@app.post("/api/v1/simular/{op_codigo}")
async def simular(op_codigo: str):
    resultado = linha.simular_execucao_op(op_codigo)
    return resultado
```

**Endpoints Sugeridos:**
- `POST /api/v1/ordem-fabricacao` - Criar OF
- `GET /api/v1/ordem-fabricacao/{id}` - Consultar OF
- `POST /api/v1/ordem-producao` - Gerar OP
- `GET /api/v1/ordem-producao/{id}` - Consultar OP
- `POST /api/v1/simular/{id}` - Simular OP
- `GET /api/v1/linha/estrutura` - Estrutura
- `GET /api/v1/historico` - Histórico

**Tempo Estimado:** 8-12 horas

---

### FASE 3: Dashboard Web (Priority: 🟡 MÉDIA)

**Objetivo:** Interface visual moderna para monitoramento

**Tecnologia Sugerida:** React + TypeScript

#### 3.1 Arquitetura
```
frontend/
├── components/
│   ├── OrdemFabricacao/
│   │   ├── FormCriarOf.tsx
│   │   └── ListaOfs.tsx
│   ├── OrdemProducao/
│   │   ├── FormGerarOp.tsx
│   │   └── ListaOps.tsx
│   └── Dashboard/
│       ├── EstatisticasWidget.tsx
│       ├── GraficoRecursos.tsx
│       └── HistoricoSimulacoes.tsx
├── services/
│   └── api.ts (chamadas para API)
└── pages/
    ├── Home.tsx
    ├── OrdensFabricacao.tsx
    └── Dashboard.tsx
```

**Features:**
- Dashboard com métricas em tempo real
- Gráficos de alocação de recursos
- Timeline de operações
- Tabelas com filtros
- Notificações de erros

**Tempo Estimado:** 20-30 horas

---

### FASE 4: Otimização de Roteamento (Priority: 🟡 MÉDIA)

**Objetivo:** Sugerir sequências otimizadas de produção

**Algoritmo Sugerido:** Algoritmo Genético ou Simulated Annealing

```python
class OtimizadorRoteamento:
    def __init__(self, linha: LinhaProducao):
        self.linha = linha
    
    def otimizar_sequencia(self, ops: List[str]) -> List[str]:
        """
        Encontra a sequência ótima de OPs
        Objetivo: Minimizar tempo total, maximizar uso de recursos
        """
        # Implementar algoritmo de otimização
        pass
    
    def sugerir_alocacao_recursos(self, op: str) -> List[int]:
        """
        Sugere os melhores recursos para uma OP
        Considerando disponibilidade e distância
        """
        pass
    
    def calcular_tempo_estimado(self, op: str) -> float:
        """
        Estima tempo de produção baseado em histórico
        """
        pass
```

**Tempo Estimado:** 12-18 horas

---

### FASE 5: Integração com IoT (Priority: 🔵 BAIXA)

**Objetivo:** Conectar com sensores e máquinas reais

**Tecnologia Sugerida:** MQTT + Modbus

```python
import paho.mqtt.client as mqtt

class IntegradorIoT:
    def __init__(self, broker_addr: str):
        self.client = mqtt.Client()
        self.client.connect(broker_addr, 1883, 60)
    
    def registrar_conclusao_op(self, op_codigo: str):
        """Callback para quando máquina completa OP"""
        self.client.publish(f"producao/op/{op_codigo}/concluida")
    
    def monitorar_recurso(self, recurso_id: str):
        """Monitora sensores de um recurso"""
        self.client.subscribe(f"recursos/{recurso_id}/status")
```

**Dados a Integrar:**
- Status de máquinas
- Sensores de temperatura/pressão
- Contador de peças
- Tempo real de execução

**Tempo Estimado:** 16-24 horas

---

### FASE 6: Análise Avançada (Priority: 🔵 BAIXA)

**Objetivo:** Machine Learning para previsões

**Bibliotecas Sugeridas:** scikit-learn, pandas

```python
from sklearn.ensemble import RandomForestRegressor
import numpy as np

class PreditorDesempenho:
    def __init__(self):
        self.modelo = RandomForestRegressor()
        self.dados_historicos = []
    
    def treinar(self, dados: List[dict]):
        """
        Treina modelo com dados históricos
        Input: [{'op': '...', 'fase': 1, 'modo': 'B', 'tempo': 125}]
        """
        X = np.array([[d['fase'], d['modo_numeric'], ...] for d in dados])
        y = np.array([d['tempo'] for d in dados])
        self.modelo.fit(X, y)
    
    def prever_tempo(self, op: OrdemProducao) -> float:
        """Prevê tempo de execução de uma OP"""
        X = [[op.fase, self._modo_para_numero(op.modo), ...]]
        return self.modelo.predict(X)[0]
    
    def detectar_anomalias(self, op_codigo: str) -> bool:
        """Detecta operações anômalas"""
        pass
```

**Previsões:**
- Tempo de execução
- Probabilidade de falha
- Melhor sequência de OPs
- Anomalias em operações

**Tempo Estimado:** 20-30 horas

---

## 🔄 Arquitetura Evolutiva

### Estrutura Proposta para Expansão

```
projeto/
├── core/                      (ATUAL)
│   ├── modelo_producao.py
│   ├── validadores.py
│   └── linhas.py
├── data/                      (FASE 1)
│   ├── database.py
│   ├── repositorio.py
│   └── migrações/
├── api/                       (FASE 2)
│   ├── main.py
│   ├── rotas/
│   │   ├── ordens_fabricacao.py
│   │   ├── ordens_producao.py
│   │   └── simulacoes.py
│   └── schemas/
├── frontend/                  (FASE 3)
│   ├── src/
│   ├── public/
│   └── package.json
├── otimizacao/               (FASE 4)
│   ├── roteador.py
│   ├── algoritmos.py
│   └── testes_performance.py
├── iot/                      (FASE 5)
│   ├── integradores.py
│   ├── sensores.py
│   └── protocolos/
├── ml/                       (FASE 6)
│   ├── predictor.py
│   ├── datasets/
│   └── modelos/
├── tests/
├── docs/
└── docker/
    ├── Dockerfile
    └── docker-compose.yml
```

---

## 🎯 Roadmap Recomendado

```
2025 Q2:
  ├─ FASE 1: Persistência (SQLite/JSON)
  └─ FASE 2: API REST (FastAPI)

2025 Q3:
  ├─ FASE 3: Dashboard Web (React)
  └─ Documentação API (OpenAPI/Swagger)

2025 Q4:
  ├─ FASE 4: Otimização (Algoritmos)
  └─ Testes de Carga

2026 Q1:
  ├─ FASE 5: IoT (MQTT/Modbus)
  └─ Integração com ERP

2026 Q2:
  └─ FASE 6: ML (Previsões)
```

---

## 💡 Sugestões de Expansão Rápida

### 1. Adicionar Log Estruturado
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('producao.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class OrdemProducao:
    def _parsear_codigo(self):
        logger.info(f"Parseando OP: {self.codigo_original}")
        # ...
```

### 2. Adicionar Configuração Externa
```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = os.getenv('DEBUG', False)
    DB_URL = os.getenv('DATABASE_URL', 'sqlite:///producao.db')
    API_PORT = int(os.getenv('API_PORT', 8000))
    MAX_RECURSOS = int(os.getenv('MAX_RECURSOS', 26))
```

### 3. Adicionar Cache
```python
from functools import lru_cache

class OrdemProducao:
    @lru_cache(maxsize=128)
    def obter_recursos_cached(self):
        return tuple(self.recursos_utilizados)
```

### 4. Adicionar Validação com Pydantic
```python
from pydantic import BaseModel, validator

class OpRequest(BaseModel):
    codigo: str
    
    @validator('codigo')
    def validar_formato(cls, v):
        if len(v) != 10:
            raise ValueError('Código deve ter 10 caracteres')
        return v
```

---

## 🧪 Sugestões de Testes Adicionais

### Testes de Performance
```python
import time

def teste_performance_validacao():
    """Testa tempo de validação de 1000 OPs"""
    ops = [f"2512300B{i:02d}" for i in range(27)]
    inicio = time.time()
    
    for _ in range(1000):
        for op in ops:
            OrdemProducao(op)
    
    tempo = time.time() - inicio
    print(f"1000 validações em {tempo:.3f}s")
    assert tempo < 1.0  # Deve ser rápido
```

### Testes de Carga
```python
def teste_carga_1000_operacoes():
    """Testa sistema com 1000 operações"""
    linha = LinhaProducao()
    
    for i in range(100):
        of = linha.criar_ordem_fabricacao(25, i % 2, i % 100)
        for j in range(10):
            op = linha.gerar_ordem_producao(of, j % 3, j % 3, chr(65 + (j % 3)), 10 + j)
            assert op is not None
```

---

## 📚 Recursos Recomendados

### Bibliotecas Úteis
```bash
# Persistência
pip install sqlalchemy  # ORM melhor
pip install alembic     # Migrações de BD

# API
pip install fastapi uvicorn

# Dashboard
npm install react react-router-dom
npm install recharts    # Gráficos

# Otimização
pip install deap        # Algoritmos genéticos
pip install scipy       # Otimização

# IoT
pip install paho-mqtt
pip install pymodbus

# ML
pip install scikit-learn pandas

# Qualidade
pip install black       # Formatação
pip install pylint      # Linting
pip install coverage    # Coverage
```

---

## 📖 Documentação Adicional

### Para Implementação

1. **README da API:** Como usar os endpoints
2. **Guia de Banco de Dados:** Schema e queries
3. **Guia IoT:** Integração com sensores
4. **ML Model Card:** Detalhes dos modelos

### Para Usuários

1. **Manual do Dashboard:** Como usar a interface
2. **Troubleshooting:** Problemas comuns
3. **FAQ:** Perguntas frequentes
4. **Video Tutorials:** Guias em vídeo

---

## ✅ Checklist de Qualidade

Antes de implementar cada fase:

- [ ] Escrever testes unitários
- [ ] Escrever testes de integração
- [ ] Documentar API/classes
- [ ] Fazer code review
- [ ] Testar performance
- [ ] Testar segurança
- [ ] Atualizar documentação
- [ ] Versionar (semver)
- [ ] Criar changelog
- [ ] Deploy para staging
- [ ] Testes de aceitação
- [ ] Deploy para produção

---

## 🎓 Conclusão

Este plano permite expandir o sistema incrementalmente sem comprometer a qualidade ou estabilidade existente. Cada fase é relativamente independente e pode ser desenvolvida parallelamente.

A priorização recomendada é:
1. **Fase 1 & 2** - Base para tudo mais (URGENTE)
2. **Fase 3** - Visualização (IMPORTANTE)
3. **Fase 4** - Inteligência (DESEJÁVEL)
4. **Fase 5 & 6** - Futuro (AVANÇADO)

---

**Documento de Referência**
Data: Maio 2025
Status: Rascunho para discussão


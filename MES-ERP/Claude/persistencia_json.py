"""
Módulo de Persistência em JSON
Permite salvar e carregar Ordens de Fabricação e Produção
"""

import json
from datetime import datetime
from typing import List, Dict
from Compact_Encoding_System import OrdemFabricacao, OrdemProducao, LinhaProducao


class PersistenciaJSON:
    """Gerencia persistência de dados em JSON."""
    
    @staticmethod
    def salvar_linha_producao(linha: LinhaProducao, arquivo: str) -> bool:
        """
        Salva uma Linha de Produção e seus dados em JSON.
        
        Args:
            linha: LinhaProducao a salvar
            arquivo: Caminho do arquivo JSON
            
        Returns:
            True se salvo com sucesso
        """
        try:
            dados = {
                "linha": {
                    "nome": linha.nome,
                    "num_recursos": linha.num_recursos,
                    "data_criacao": linha.data_criacao.isoformat()
                },
                "ordens_fabricacao": [],
                "ordens_producao": []
            }
            
            # Serializar OFs
            for of in linha.ordens_fabricacao:
                dados["ordens_fabricacao"].append({
                    "codigo": of.gerar_codigo(),
                    "ano": of.ano,
                    "tipo_linha": of.tipo_linha,
                    "codigo_cliente": of.codigo_cliente,
                    "data_criacao": of.data_criacao.isoformat()
                })
            
            # Serializar OPs
            for op in linha.ordens_producao:
                dados["ordens_producao"].append({
                    "codigo": op.gerar_codigo(),
                    "codigo_of": op.codigo_of,
                    "fase": op.fase,
                    "subfase": op.subfase,
                    "modo_recurso": op.modo_recurso,
                    "recurso_base": op.recurso_base,
                    "recursos_utilizados": op.obter_recursos(),
                    "status": op.status,
                    "data_criacao": op.data_criacao.isoformat()
                })
            
            # Escrever arquivo
            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)
            
            return True
        
        except Exception as e:
            print(f"Erro ao salvar: {str(e)}")
            return False
    
    @staticmethod
    def carregar_linha_producao(arquivo: str) -> LinhaProducao:
        """
        Carrega dados de uma Linha de Produção do JSON.
        
        Args:
            arquivo: Caminho do arquivo JSON
            
        Returns:
            LinhaProducao carregada
        """
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            # Reconstruir linha
            info_linha = dados["linha"]
            linha = LinhaProducao(info_linha["nome"], info_linha["num_recursos"])
            
            # Reconstruir OFs
            for of_data in dados.get("ordens_fabricacao", []):
                try:
                    of = OrdemFabricacao(
                        of_data["ano"],
                        of_data["tipo_linha"],
                        of_data["codigo_cliente"]
                    )
                    of.data_criacao = datetime.fromisoformat(of_data["data_criacao"])
                    linha.ordens_fabricacao.append(of)
                except Exception as e:
                    print(f"Erro ao carregar OF: {str(e)}")
            
            # Reconstruir OPs
            for op_data in dados.get("ordens_producao", []):
                try:
                    op = OrdemProducao(
                        op_data["codigo_of"],
                        op_data["fase"],
                        op_data["subfase"],
                        op_data["modo_recurso"],
                        op_data["recurso_base"]
                    )
                    op.data_criacao = datetime.fromisoformat(op_data["data_criacao"])
                    op.status = op_data["status"]
                    linha.ordens_producao.append(op)
                except Exception as e:
                    print(f"Erro ao carregar OP: {str(e)}")
            
            return linha
        
        except Exception as e:
            print(f"Erro ao carregar: {str(e)}")
            return None
    
    @staticmethod
    def exportar_relatorio_json(linha: LinhaProducao, arquivo: str) -> bool:
        """
        Exporta um relatório analítico em JSON.
        
        Args:
            linha: LinhaProducao para análise
            arquivo: Caminho do arquivo JSON
            
        Returns:
            True se exportado com sucesso
        """
        try:
            # Calcular estatísticas
            uso_recursos = {}
            distribuicao_fases = {}
            distribuicao_modos = {}
            
            for op in linha.ordens_producao:
                # Uso de recursos
                for recurso in op.obter_recursos():
                    uso_recursos[recurso] = uso_recursos.get(recurso, 0) + 1
                
                # Distribuição de fase
                fase = op.fase
                distribuicao_fases[fase] = distribuicao_fases.get(fase, 0) + 1
                
                # Distribuição de modo
                modo = op.modo_recurso
                distribuicao_modos[modo] = distribuicao_modos.get(modo, 0) + 1
            
            # Montar relatório
            relatorio = {
                "data_geracao": datetime.now().isoformat(),
                "linha": {
                    "nome": linha.nome,
                    "recursos_totais": linha.num_recursos
                },
                "estatisticas": {
                    "total_ofs": len(linha.ordens_fabricacao),
                    "total_ops": len(linha.ordens_producao),
                    "recursos_ativos": len(uso_recursos),
                    "taxa_ocupacao_recursos": f"{(len(uso_recursos)/linha.num_recursos)*100:.1f}%"
                },
                "uso_recursos": {
                    str(k): v for k, v in sorted(uso_recursos.items())
                },
                "distribuicao_fases": {
                    str(k): v for k, v in sorted(distribuicao_fases.items())
                },
                "distribuicao_modos": {
                    str(k): v for k, v in sorted(distribuicao_modos.items())
                },
                "ordens_producao_detalhes": [
                    {
                        "codigo": op.gerar_codigo(),
                        "fase": op.fase,
                        "subfase": op.subfase,
                        "modo": op.modo_recurso,
                        "recursos": op.obter_recursos(),
                        "status": op.status
                    }
                    for op in linha.ordens_producao
                ]
            }
            
            # Escrever arquivo
            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump(relatorio, f, indent=2, ensure_ascii=False)
            
            return True
        
        except Exception as e:
            print(f"Erro ao exportar relatório: {str(e)}")
            return False


# ============================================================================
# Exemplos de Uso
# ============================================================================

def exemplo_salvar_carregar():
    """Demonstra salvar e carregar dados."""
    print("\n" + "="*70)
    print("EXEMPLO: SALVAR E CARREGAR DADOS")
    print("="*70 + "\n")
    
    # 1. Criar linha com dados
    print("1️⃣  Criando e preenchendo linha de produção...")
    linha = LinhaProducao("Linha JSON")
    
    of1 = linha.criar_ordem_fabricacao(25, 1, 10)
    of2 = linha.criar_ordem_fabricacao(25, 0, 20)
    
    op1 = linha.criar_ordem_producao("25110", 0, 0, "A", 0)
    op2 = linha.criar_ordem_producao("25110", 1, 1, "B", 5)
    op3 = linha.criar_ordem_producao("25120", 2, 2, "C", 20)
    
    print(f"   ✓ {len(linha.ordens_fabricacao)} OFs criadas")
    print(f"   ✓ {len(linha.ordens_producao)} OPs criadas\n")
    
    # 2. Salvar dados
    print("2️⃣  Salvando em JSON...")
    arquivo_dados = "producao_dados.json"
    if PersistenciaJSON.salvar_linha_producao(linha, arquivo_dados):
        print(f"   ✓ Salvo em: {arquivo_dados}\n")
    else:
        print(f"   ✗ Erro ao salvar\n")
    
    # 3. Criar nova linha vazia
    print("3️⃣  Criando nova linha vazia...")
    linha_nova = LinhaProducao("Linha Nova")
    print(f"   OFs: {len(linha_nova.ordens_fabricacao)}")
    print(f"   OPs: {len(linha_nova.ordens_producao)}\n")
    
    # 4. Carregar dados
    print("4️⃣  Carregando dados do JSON...")
    linha_carregada = PersistenciaJSON.carregar_linha_producao(arquivo_dados)
    if linha_carregada:
        print(f"   ✓ Carregado de: {arquivo_dados}")
        print(f"   ✓ OFs restauradas: {len(linha_carregada.ordens_fabricacao)}")
        print(f"   ✓ OPs restauradas: {len(linha_carregada.ordens_producao)}\n")
    else:
        print(f"   ✗ Erro ao carregar\n")


def exemplo_exportar_relatorio():
    """Demonstra exportar relatório analítico."""
    print("\n" + "="*70)
    print("EXEMPLO: EXPORTAR RELATÓRIO ANALÍTICO")
    print("="*70 + "\n")
    
    # Criar linha com dados
    linha = LinhaProducao("Linha Análise")
    
    for i in range(1, 4):
        of = linha.criar_ordem_fabricacao(25, 0, i)
        for fase in range(3):
            for subfase in range(3):
                op = linha.criar_ordem_producao(
                    of.gerar_codigo(),
                    fase,
                    subfase,
                    ["A", "B", "C"][subfase % 3],
                    (i * 5) % 25
                )
    
    print(f"Linha criada com {len(linha.ordens_producao)} OPs\n")
    
    # Exportar relatório
    print("Exportando relatório...")
    arquivo_relatorio = "producao_relatorio.json"
    if PersistenciaJSON.exportar_relatorio_json(linha, arquivo_relatorio):
        print(f"✓ Relatório exportado: {arquivo_relatorio}\n")
        
        # Ler e exibir resumo
        with open(arquivo_relatorio, 'r', encoding='utf-8') as f:
            relatorio = json.load(f)
        
        est = relatorio["estatisticas"]
        print("RESUMO DO RELATÓRIO:")
        print(f"  Total OFs: {est['total_ofs']}")
        print(f"  Total OPs: {est['total_ops']}")
        print(f"  Recursos ativos: {est['recursos_ativos']}/27")
        print(f"  Taxa de ocupação: {est['taxa_ocupacao_recursos']}")
    else:
        print("✗ Erro ao exportar relatório")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("PERSISTÊNCIA EM JSON - SISTEMA DE PRODUÇÃO")
    print("="*70)
    
    exemplo_salvar_carregar()
    exemplo_exportar_relatorio()
    
    print("\n" + "="*70)
    print("✓ Exemplos de persistência concluídos!")
    print("="*70 + "\n")

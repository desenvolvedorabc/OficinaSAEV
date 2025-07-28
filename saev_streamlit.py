"""
📊 SAEV - Sistema de Análise Educacional do Espírito Santo
🎯 Painel Principal de Dados

Aplicativo Streamlit simples e funcional para visualização
dos dados SAEV com base no Star Schema documentado.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import duckdb
import numpy as np
from datetime import datetime

# =================== CONFIGURAÇÃO DA PÁGINA ===================
st.set_page_config(
    page_title="SAEV - Painel Principal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =================== FUNÇÕES AUXILIARES ===================

def conectar_banco():
    """Conecta ao banco DuckDB"""
    try:
        return duckdb.connect('db/avaliacao_prod.duckdb', read_only=True)
    except Exception as e:
        st.error(f"❌ Erro ao conectar ao banco: {e}")
        return None

@st.cache_data
def carregar_dados_principais():
    """Carrega dados principais para o painel"""
    con = conectar_banco()
    if not con:
        return {}
    
    try:
        dados = {}
        
        # 1. Métricas gerais
        dados['metricas'] = con.execute("""
            SELECT 
                COUNT(DISTINCT ALU_ID) as total_alunos,
                COUNT(DISTINCT ESC_INEP) as total_escolas,
                COUNT(DISTINCT MUN_NOME) as total_municipios,
                COUNT(DISTINCT TES_NOME) as total_testes,
                SUM(ACERTO + ERRO) as total_questoes,
                SUM(ACERTO) as total_acertos,
                ROUND(100.0 * SUM(ACERTO) / SUM(ACERTO + ERRO), 2) as taxa_acerto_geral
            FROM fato_resposta_aluno
        """).fetchdf()
        
        # 2. Top 10 Municípios por performance
        dados['top_municipios'] = con.execute("""
            SELECT 
                MUN_NOME,
                COUNT(DISTINCT ALU_ID) as total_alunos,
                SUM(ACERTO) as acertos,
                SUM(ERRO) as erros,
                ROUND(100.0 * SUM(ACERTO) / SUM(ACERTO + ERRO), 2) as taxa_acerto
            FROM fato_resposta_aluno
            GROUP BY MUN_NOME
            HAVING SUM(ACERTO + ERRO) >= 1000
            ORDER BY taxa_acerto DESC
            LIMIT 10
        """).fetchdf()
        
        # 3. Performance por disciplina
        dados['por_disciplina'] = con.execute("""
            SELECT 
                DIS_NOME,
                COUNT(DISTINCT ALU_ID) as total_alunos,
                COUNT(DISTINCT TES_NOME) as total_testes,
                SUM(ACERTO) as acertos,
                SUM(ERRO) as erros,
                ROUND(100.0 * SUM(ACERTO) / SUM(ACERTO + ERRO), 2) as taxa_acerto
            FROM fato_resposta_aluno
            GROUP BY DIS_NOME
            ORDER BY DIS_NOME
        """).fetchdf()
        
        # 4. Performance por série
        dados['por_serie'] = con.execute("""
            SELECT 
                SER_NOME,
                DIS_NOME,
                COUNT(DISTINCT ALU_ID) as total_alunos,
                SUM(ACERTO) as acertos,
                SUM(ERRO) as erros,
                ROUND(100.0 * SUM(ACERTO) / SUM(ACERTO + ERRO), 2) as taxa_acerto
            FROM fato_resposta_aluno
            GROUP BY SER_NOME, DIS_NOME
            ORDER BY SER_NOME, DIS_NOME
        """).fetchdf()
        
        # 5. Descritores mais difíceis
        dados['descritores_dificeis'] = con.execute("""
            SELECT 
                d.MTI_CODIGO,
                d.MTI_DESCRITOR,
                SUM(f.ACERTO) as acertos,
                SUM(f.ERRO) as erros,
                ROUND(100.0 * SUM(f.ACERTO) / SUM(f.ACERTO + f.ERRO), 2) as taxa_acerto
            FROM fato_resposta_aluno f
            JOIN dim_descritor d ON f.MTI_CODIGO = d.MTI_CODIGO
            GROUP BY d.MTI_CODIGO, d.MTI_DESCRITOR
            HAVING SUM(f.ACERTO + f.ERRO) >= 500
            ORDER BY taxa_acerto ASC
            LIMIT 10
        """).fetchdf()
        
        # 6. Distribuição de alunos por município
        dados['alunos_municipio'] = con.execute("""
            SELECT 
                MUN_NOME,
                COUNT(DISTINCT ALU_ID) as total_alunos
            FROM fato_resposta_aluno
            GROUP BY MUN_NOME
            ORDER BY total_alunos DESC
            LIMIT 15
        """).fetchdf()
        
        con.close()
        return dados
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        con.close()
        return {}

# =================== INTERFACE PRINCIPAL ===================

def main():
    """Função principal do aplicativo"""
    
    # Cabeçalho
    st.title("📊 SAEV - Sistema de Análise Educacional")
    st.subheader("🎯 Painel Principal de Dados")
    st.markdown("---")
    
    # Verificar conexão
    con = conectar_banco()
    if not con:
        st.error("❌ Não foi possível conectar ao banco de dados.")
        return
    con.close()
    
    # Carregar dados
    with st.spinner("📊 Carregando dados do painel..."):
        dados = carregar_dados_principais()
    
    if not dados:
        st.error("❌ Não foi possível carregar os dados.")
        return
    
    # =================== MÉTRICAS PRINCIPAIS ===================
    st.header("📈 Métricas Principais")
    
    metricas = dados['metricas'].iloc[0]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👨‍🎓 Total de Alunos", f"{metricas['total_alunos']:,}")
    
    with col2:
        st.metric("🏫 Total de Escolas", f"{metricas['total_escolas']:,}")
    
    with col3:
        st.metric("🏙️ Total de Municípios", f"{metricas['total_municipios']:,}")
    
    with col4:
        st.metric("📝 Total de Testes", f"{metricas['total_testes']:,}")
    
    col5, col6, col7 = st.columns(3)
    
    with col5:
        st.metric("❓ Total de Questões", f"{metricas['total_questoes']:,}")
    
    with col6:
        st.metric("✅ Total de Acertos", f"{metricas['total_acertos']:,}")
    
    with col7:
        st.metric("📊 Taxa de Acerto Geral", f"{metricas['taxa_acerto_geral']}%")
    
    st.markdown("---")
    
    # =================== VISUALIZAÇÕES ===================
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico 1: Top Municípios por Performance
        st.subheader("🏆 Top 10 Municípios - Taxa de Acerto")
        
        fig = px.bar(
            dados['top_municipios'],
            x='taxa_acerto',
            y='MUN_NOME',
            orientation='h',
            title="Municípios com Melhor Performance",
            labels={'taxa_acerto': 'Taxa de Acerto (%)', 'MUN_NOME': 'Município'},
            color='taxa_acerto',
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico 3: Performance por Série e Disciplina
        st.subheader("📚 Taxa de Acerto por Série e Disciplina")
        
        fig = px.bar(
            dados['por_serie'],
            x='SER_NOME',
            y='taxa_acerto',
            color='DIS_NOME',
            title="Performance por Série",
            labels={'taxa_acerto': 'Taxa de Acerto (%)', 'SER_NOME': 'Série'},
            barmode='group'
        )
        fig.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Gráfico 2: Distribuição de Alunos por Município
        st.subheader("👨‍🎓 Distribuição de Alunos por Município")
        
        fig = px.bar(
            dados['alunos_municipio'],
            x='total_alunos',
            y='MUN_NOME',
            orientation='h',
            title="Top 15 Municípios por Número de Alunos",
            labels={'total_alunos': 'Número de Alunos', 'MUN_NOME': 'Município'},
            color='total_alunos',
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico 4: Performance por Disciplina
        st.subheader("📖 Performance por Disciplina")
        
        fig = px.pie(
            dados['por_disciplina'],
            values='total_alunos',
            names='DIS_NOME',
            title="Distribuição de Alunos por Disciplina"
        )
        fig.update_layout(height=200)
        st.plotly_chart(fig, use_container_width=True)
        
        # Métricas por disciplina
        st.write("**Taxa de Acerto por Disciplina:**")
        for _, row in dados['por_disciplina'].iterrows():
            st.metric(
                f"📚 {row['DIS_NOME']}", 
                f"{row['taxa_acerto']}%",
                f"{row['total_testes']} testes"
            )
    
    st.markdown("---")
    
    # =================== SEÇÃO DE ANÁLISES DETALHADAS ===================
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Tabela: Top Municípios
        st.subheader("📋 Detalhes dos Top Municípios")
        
        # Formatar dados para exibição
        df_municipios = dados['top_municipios'].copy()
        df_municipios = df_municipios.rename(columns={
            'MUN_NOME': 'Município',
            'total_alunos': 'Alunos',
            'taxa_acerto': 'Taxa (%)'
        })
        
        st.dataframe(
            df_municipios[['Município', 'Alunos', 'Taxa (%)']],
            use_container_width=True,
            height=300
        )
    
    with col2:
        # Gráfico: Descritores Mais Difíceis
        st.subheader("🎯 Descritores Mais Difíceis")
        
        # Truncar descrições longas
        df_desc = dados['descritores_dificeis'].copy()
        df_desc['MTI_DESCRITOR_SHORT'] = df_desc['MTI_DESCRITOR'].str[:60] + '...'
        
        fig = px.bar(
            df_desc,
            x='taxa_acerto',
            y='MTI_DESCRITOR_SHORT',
            orientation='h',
            title="10 Descritores com Menor Taxa de Acerto",
            labels={'taxa_acerto': 'Taxa de Acerto (%)', 'MTI_DESCRITOR_SHORT': 'Descritor'},
            color='taxa_acerto',
            color_continuous_scale='Reds_r'
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # =================== INFORMAÇÕES DO SISTEMA ===================
    
    st.markdown("---")
    
    with st.expander("ℹ️ Informações do Sistema"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**📊 Estrutura dos Dados:**")
            st.write("- **Star Schema** otimizado para BI")
            st.write("- **Fato:** fato_resposta_aluno")
            st.write("- **Dimensões:** dim_aluno, dim_escola, dim_descritor")
        
        with col2:
            st.write("**🎯 Métricas Principais:**")
            st.write("- **ACERTO:** Total de respostas corretas")
            st.write("- **ERRO:** Total de respostas incorretas")
            st.write("- **Taxa de Acerto:** % de acertos sobre total")
        
        with col3:
            st.write("**🔄 Última Atualização:**")
            st.write(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            st.write("🔗 Dados em tempo real do DuckDB")
    
    # Rodapé
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; color: #666; font-size: 12px;'>
        📊 SAEV - Sistema de Análise Educacional do Espírito Santo<br>
        🎯 Painel Principal baseado no Star Schema<br>
        🕒 Última consulta: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
    </div>
    """, unsafe_allow_html=True)

# =================== EXECUÇÃO ===================

if __name__ == "__main__":
    main()

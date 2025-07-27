"""
📊 SAEV - Sistema de Análise Educacional do Espírito Santo
🎯 Galeria de Painéis com Filtros Avançados

Aplicativo Streamlit para visualização interativa dos dados SAEV
com múltiplos painéis e filtros dinâmicos.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import duckdb
import numpy as np
from datetime import datetime

# =================== CONFIGURAÇÃO DA PÁGINA ===================
st.set_page_config(
    page_title="SAEV - Painéis Educacionais",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =================== FUNÇÕES AUXILIARES ===================

def conectar_banco():
    """Conecta ao banco DuckDB e retorna a conexão"""
    try:
        con = duckdb.connect('db/avaliacao_prod.duckdb', read_only=True)
        return con
    except Exception as e:
        st.error(f"❌ Erro ao conectar ao banco: {e}")
        return None

@st.cache_data
def carregar_opcoes_filtros():
    """Carrega todas as opções disponíveis para os filtros"""
    con = conectar_banco()
    if not con:
        return {}
    
    try:
        opcoes = {}
        
        # Anos
        opcoes['anos'] = [row[0] for row in con.execute(
            "SELECT DISTINCT AVA_ANO FROM fato_resposta_aluno ORDER BY AVA_ANO"
        ).fetchall()]
        
        # Municípios
        opcoes['municipios'] = [row[0] for row in con.execute(
            "SELECT DISTINCT MUN_NOME FROM fato_resposta_aluno ORDER BY MUN_NOME"
        ).fetchall()]
        
        # Escolas
        opcoes['escolas'] = [row[0] for row in con.execute(
            "SELECT DISTINCT e.ESC_NOME FROM dim_escola e INNER JOIN fato_resposta_aluno f ON e.ESC_INEP = f.ESC_INEP ORDER BY e.ESC_NOME"
        ).fetchall()]
        
        # Disciplinas
        opcoes['disciplinas'] = [row[0] for row in con.execute(
            "SELECT DISTINCT DIS_NOME FROM fato_resposta_aluno ORDER BY DIS_NOME"
        ).fetchall()]
        
        # Séries
        opcoes['series'] = [row[0] for row in con.execute(
            "SELECT DISTINCT SER_NOME FROM fato_resposta_aluno ORDER BY SER_NUMBER"
        ).fetchall()]
        
        # Testes
        opcoes['testes'] = [row[0] for row in con.execute(
            "SELECT DISTINCT TES_NOME FROM fato_resposta_aluno ORDER BY TES_NOME"
        ).fetchall()]
        
        con.close()
        return opcoes
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar opções: {e}")
        con.close()
        return {}

def construir_query_base(filtros):
    """Constrói a query base com os filtros aplicados"""
    query = """
    SELECT 
        f.*,
        e.ESC_NOME,
        d.MTI_DESCRITOR
    FROM fato_resposta_aluno f
    LEFT JOIN dim_escola e ON f.ESC_INEP = e.ESC_INEP
    LEFT JOIN dim_descritor d ON f.MTI_CODIGO = d.MTI_CODIGO
    WHERE 1=1
    """
    
    params = []
    
    if filtros['anos']:
        query += f" AND AVA_ANO IN ({','.join(['?' for _ in filtros['anos']])})"
        params.extend(filtros['anos'])
    
    if filtros['municipios']:
        query += f" AND MUN_NOME IN ({','.join(['?' for _ in filtros['municipios']])})"
        params.extend(filtros['municipios'])
    
    if filtros['escolas']:
        query += f" AND e.ESC_NOME IN ({','.join(['?' for _ in filtros['escolas']])})"
        params.extend(filtros['escolas'])
    
    if filtros['disciplinas']:
        query += f" AND DIS_NOME IN ({','.join(['?' for _ in filtros['disciplinas']])})"
        params.extend(filtros['disciplinas'])
    
    if filtros['series']:
        query += f" AND SER_NOME IN ({','.join(['?' for _ in filtros['series']])})"
        params.extend(filtros['series'])
    
    if filtros['testes']:
        query += f" AND TES_NOME IN ({','.join(['?' for _ in filtros['testes']])})"
        params.extend(filtros['testes'])
    
    return query, params

@st.cache_data
def carregar_dados_filtrados(filtros):
    """Carrega dados com filtros aplicados"""
    con = conectar_banco()
    if not con:
        return pd.DataFrame()
    
    try:
        query, params = construir_query_base(filtros)
        df = con.execute(query, params).fetchdf()
        con.close()
        return df
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        con.close()
        return pd.DataFrame()

# =================== INTERFACE DOS FILTROS ===================

def criar_filtros():
    """Cria a sidebar com todos os filtros"""
    st.sidebar.header("🔍 Filtros de Análise")
    st.sidebar.markdown("---")
    
    # Carregar opções
    opcoes = carregar_opcoes_filtros()
    if not opcoes:
        st.sidebar.error("❌ Não foi possível carregar as opções de filtro")
        return {}
    
    # Inicializar estados dos botões "Todos" se não existirem
    if "todos_municipios_clicked" not in st.session_state:
        st.session_state.todos_municipios_clicked = False
    if "todos_escolas_clicked" not in st.session_state:
        st.session_state.todos_escolas_clicked = False
    
    filtros = {}
    
    # Filtro Ano
    st.sidebar.subheader("📅 Ano")
    filtros['anos'] = st.sidebar.multiselect(
        "Selecione os anos:",
        options=opcoes['anos'],
        default=[],
        key="filtro_anos"
    )
    
    # Filtro Município
    st.sidebar.subheader("🏙️ Município")
    col1, col2 = st.sidebar.columns([3, 1])
    
    # Verificar se botão "Todos" foi clicado
    default_municipios = opcoes['municipios'] if st.session_state.todos_municipios_clicked else []
    
    with col1:
        filtros['municipios'] = st.sidebar.multiselect(
            "Selecione os municípios:",
            options=opcoes['municipios'],
            default=default_municipios,
            key="filtro_municipios"
        )
    with col2:
        if st.sidebar.button("Todos", key="btn_todos_municipios"):
            st.session_state.todos_municipios_clicked = True
            st.rerun()
    
    # Filtro Escola
    st.sidebar.subheader("🏫 Escola")
    col1, col2 = st.sidebar.columns([3, 1])
    
    # Verificar se botão "Todos" foi clicado
    default_escolas = opcoes['escolas'] if st.session_state.todos_escolas_clicked else []
    
    with col1:
        filtros['escolas'] = st.sidebar.multiselect(
            "Selecione as escolas:",
            options=opcoes['escolas'],
            default=default_escolas,
            key="filtro_escolas"
        )
    with col2:
        if st.sidebar.button("Todos", key="btn_todos_escolas"):
            st.session_state.todos_escolas_clicked = True
            st.rerun()
    
    # Filtro Disciplina
    st.sidebar.subheader("📚 Disciplina")
    filtros['disciplinas'] = st.sidebar.multiselect(
        "Selecione as disciplinas:",
        options=opcoes['disciplinas'],
        default=[],
        key="filtro_disciplinas"
    )
    
    # Filtro Série
    st.sidebar.subheader("🎓 Série")
    filtros['series'] = st.sidebar.multiselect(
        "Selecione as séries:",
        options=opcoes['series'],
        default=[],
        key="filtro_series"
    )
    
    # Filtro Teste
    st.sidebar.subheader("📝 Teste")
    filtros['testes'] = st.sidebar.multiselect(
        "Selecione os testes:",
        options=opcoes['testes'],
        default=[],
        key="filtro_testes"
    )
    
    st.sidebar.markdown("---")
    
    # Botão Limpar Filtros
    if st.sidebar.button("🧹 Limpar Todos os Filtros", type="secondary"):
        # Limpar estados dos botões "Todos"
        st.session_state.todos_municipios_clicked = False
        st.session_state.todos_escolas_clicked = False
        # Limpar filtros
        for key in list(st.session_state.keys()):
            if key.startswith('filtro_'):
                del st.session_state[key]
        st.rerun()
    
    return filtros

# =================== PAINÉIS ===================

def painel_visao_geral(df):
    """Painel 1: Visão Geral dos Dados"""
    st.header("📊 Painel 1: Visão Geral dos Dados")
    
    if df.empty:
        st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")
        return
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_alunos = df['ALU_ID'].nunique()
        st.metric("👨‍🎓 Total de Alunos", f"{total_alunos:,}")
    
    with col2:
        total_escolas = df['ESC_INEP'].nunique()
        st.metric("🏫 Total de Escolas", f"{total_escolas:,}")
    
    with col3:
        total_municipios = df['MUN_NOME'].nunique()
        st.metric("🏙️ Total de Municípios", f"{total_municipios:,}")
    
    with col4:
        total_testes = df['TES_NOME'].nunique()
        st.metric("📝 Total de Testes", f"{total_testes:,}")
    
    st.markdown("---")
    
    # Layout em duas colunas
    col1, col2 = st.columns(2)
    
    with col1:
        # Número de alunos por município
        st.subheader("👨‍🎓 Alunos por Município")
        alunos_mun = df.groupby('MUN_NOME')['ALU_ID'].nunique().reset_index()
        alunos_mun = alunos_mun.sort_values('ALU_ID', ascending=False).head(15)
        
        fig = px.bar(
            alunos_mun, 
            x='ALU_ID', 
            y='MUN_NOME',
            orientation='h',
            title="Top 15 Municípios por Número de Alunos",
            labels={'ALU_ID': 'Número de Alunos', 'MUN_NOME': 'Município'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Municípios com maiores taxas de acerto
        st.subheader("🏆 Municípios - Maiores Taxas de Acerto")
        taxa_mun = df.groupby(['MUN_NOME', 'DIS_NOME', 'SER_NOME']).agg({
            'ACERTO': 'sum',
            'ERRO': 'sum'
        }).reset_index()
        taxa_mun['total_questoes'] = taxa_mun['ACERTO'] + taxa_mun['ERRO']
        taxa_mun['taxa_acerto'] = (taxa_mun['ACERTO'] / taxa_mun['total_questoes'] * 100).round(2)
        
        top_municipios = taxa_mun.groupby('MUN_NOME')['taxa_acerto'].mean().reset_index()
        top_municipios = top_municipios.sort_values('taxa_acerto', ascending=False).head(10)
        
        fig = px.bar(
            top_municipios,
            x='taxa_acerto',
            y='MUN_NOME',
            orientation='h',
            title="Top 10 Municípios - Taxa de Acerto Média",
            labels={'taxa_acerto': 'Taxa de Acerto (%)', 'MUN_NOME': 'Município'},
            color='taxa_acerto',
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Número de testes por disciplina
        st.subheader("📝 Testes por Disciplina")
        testes_disc = df.groupby('DIS_NOME')['TES_NOME'].nunique().reset_index()
        
        fig = px.pie(
            testes_disc,
            values='TES_NOME',
            names='DIS_NOME',
            title="Distribuição de Testes por Disciplina"
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # Taxa de acerto por disciplina e série
        st.subheader("📈 Taxa de Acerto por Disciplina e Série")
        taxa_disc_serie = df.groupby(['DIS_NOME', 'SER_NOME']).agg({
            'ACERTO': 'sum',
            'ERRO': 'sum'
        }).reset_index()
        taxa_disc_serie['total_questoes'] = taxa_disc_serie['ACERTO'] + taxa_disc_serie['ERRO']
        taxa_disc_serie['taxa_acerto'] = (taxa_disc_serie['ACERTO'] / taxa_disc_serie['total_questoes'] * 100).round(2)
        
        fig = px.bar(
            taxa_disc_serie,
            x='SER_NOME',
            y='taxa_acerto',
            color='DIS_NOME',
            title="Taxa de Acerto por Série e Disciplina",
            labels={'taxa_acerto': 'Taxa de Acerto (%)', 'SER_NOME': 'Série', 'DIS_NOME': 'Disciplina'},
            barmode='group'
        )
        fig.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

def painel_taxas_acerto(df):
    """Painel 2: Gráficos com Taxa de Acerto"""
    st.header("📈 Painel 2: Taxa de Acerto - Análises Detalhadas")
    
    if df.empty:
        st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")
        return
    
    # Calcular taxas de acerto
    df['taxa_acerto'] = (df['ACERTO'] / (df['ACERTO'] + df['ERRO']) * 100)
    
    # Layout em abas
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏙️ Por Município", 
        "🏫 Por Escola", 
        "📚 Por Disciplina", 
        "🎯 Por Descritor"
    ])
    
    with tab1:
        st.subheader("Taxa de Acerto por Município")
        
        # Agrupamento por município
        taxa_municipio = df.groupby(['MUN_NOME', 'DIS_NOME']).agg({
            'ACERTO': 'sum',
            'ERRO': 'sum'
        }).reset_index()
        taxa_municipio['total_questoes'] = taxa_municipio['ACERTO'] + taxa_municipio['ERRO']
        taxa_municipio['taxa_acerto'] = (taxa_municipio['ACERTO'] / taxa_municipio['total_questoes'] * 100).round(2)
        
        # Gráfico de barras por município
        fig = px.bar(
            taxa_municipio,
            x='MUN_NOME',
            y='taxa_acerto',
            color='DIS_NOME',
            title="Taxa de Acerto por Município e Disciplina",
            labels={'taxa_acerto': 'Taxa de Acerto (%)', 'MUN_NOME': 'Município'},
            barmode='group'
        )
        fig.update_layout(height=500, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Heatmap por município e série
        col1, col2 = st.columns(2)
        with col1:
            taxa_mun_serie = df.groupby(['MUN_NOME', 'SER_NOME']).agg({
                'ACERTO': 'sum',
                'ERRO': 'sum'
            }).reset_index()
            taxa_mun_serie['taxa_acerto'] = (taxa_mun_serie['ACERTO'] / (taxa_mun_serie['ACERTO'] + taxa_mun_serie['ERRO']) * 100).round(2)
            
            # Pivot para heatmap
            heatmap_data = taxa_mun_serie.pivot(index='MUN_NOME', columns='SER_NOME', values='taxa_acerto')
            
            fig = px.imshow(
                heatmap_data,
                title="Heatmap: Taxa de Acerto por Município e Série",
                aspect="auto",
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Ranking de municípios
            ranking_mun = taxa_municipio.groupby('MUN_NOME')['taxa_acerto'].mean().reset_index()
            ranking_mun = ranking_mun.sort_values('taxa_acerto', ascending=False).head(15)
            
            fig = px.bar(
                ranking_mun,
                x='taxa_acerto',
                y='MUN_NOME',
                orientation='h',
                title="Ranking: Top 15 Municípios",
                labels={'taxa_acerto': 'Taxa de Acerto Média (%)', 'MUN_NOME': 'Município'},
                color='taxa_acerto',
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Taxa de Acerto por Escola")
        
        # Agrupamento por escola
        taxa_escola = df.groupby(['ESC_NOME', 'DIS_NOME', 'MUN_NOME']).agg({
            'ACERTO': 'sum',
            'ERRO': 'sum'
        }).reset_index()
        taxa_escola['total_questoes'] = taxa_escola['ACERTO'] + taxa_escola['ERRO']
        taxa_escola['taxa_acerto'] = (taxa_escola['ACERTO'] / taxa_escola['total_questoes'] * 100).round(2)
        
        # Top escolas
        top_escolas = taxa_escola.groupby('ESC_NOME')['taxa_acerto'].mean().reset_index()
        top_escolas = top_escolas.sort_values('taxa_acerto', ascending=False).head(20)
        
        fig = px.bar(
            top_escolas,
            x='taxa_acerto',
            y='ESC_NOME',
            orientation='h',
            title="Top 20 Escolas - Taxa de Acerto Média",
            labels={'taxa_acerto': 'Taxa de Acerto (%)', 'ESC_NOME': 'Escola'},
            color='taxa_acerto',
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
        
        # Scatter plot: Escola vs Taxa de Acerto
        fig = px.scatter(
            taxa_escola,
            x='total_questoes',
            y='taxa_acerto',
            color='DIS_NOME',
            size='total_questoes',
            hover_data=['ESC_NOME', 'MUN_NOME'],
            title="Relação: Número de Questões vs Taxa de Acerto por Escola"
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Taxa de Acerto por Disciplina")
        
        # Por disciplina e série
        taxa_disc_serie = df.groupby(['DIS_NOME', 'SER_NOME']).agg({
            'ACERTO': 'sum',
            'ERRO': 'sum'
        }).reset_index()
        taxa_disc_serie['taxa_acerto'] = (taxa_disc_serie['ACERTO'] / (taxa_disc_serie['ACERTO'] + taxa_disc_serie['ERRO']) * 100).round(2)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de linhas por série
            fig = px.line(
                taxa_disc_serie,
                x='SER_NOME',
                y='taxa_acerto',
                color='DIS_NOME',
                title="Evolução da Taxa de Acerto por Série",
                labels={'taxa_acerto': 'Taxa de Acerto (%)', 'SER_NOME': 'Série'},
                markers=True
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Box plot por disciplina
            fig = px.box(
                df,
                x='DIS_NOME',
                y='taxa_acerto',
                title="Distribuição da Taxa de Acerto por Disciplina",
                labels={'taxa_acerto': 'Taxa de Acerto (%)', 'DIS_NOME': 'Disciplina'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Por teste
        taxa_teste = df.groupby(['TES_NOME', 'DIS_NOME']).agg({
            'ACERTO': 'sum',
            'ERRO': 'sum'
        }).reset_index()
        taxa_teste['taxa_acerto'] = (taxa_teste['ACERTO'] / (taxa_teste['ACERTO'] + taxa_teste['ERRO']) * 100).round(2)
        
        fig = px.bar(
            taxa_teste,
            x='TES_NOME',
            y='taxa_acerto',
            color='DIS_NOME',
            title="Taxa de Acerto por Teste",
            labels={'taxa_acerto': 'Taxa de Acerto (%)', 'TES_NOME': 'Teste'}
        )
        fig.update_layout(height=500, xaxis_tickangle=-90)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("Taxa de Acerto por Descritor (Habilidades)")
        
        # Agrupamento por descritor
        taxa_descritor = df.groupby(['MTI_DESCRITOR', 'DIS_NOME']).agg({
            'ACERTO': 'sum',
            'ERRO': 'sum'
        }).reset_index()
        taxa_descritor['total_questoes'] = taxa_descritor['ACERTO'] + taxa_descritor['ERRO']
        taxa_descritor['taxa_acerto'] = (taxa_descritor['ACERTO'] / taxa_descritor['total_questoes'] * 100).round(2)
        
        # Filtrar apenas descritores com dados significativos
        taxa_descritor = taxa_descritor[taxa_descritor['total_questoes'] >= 100]
        
        # Top e Bottom descritores
        col1, col2 = st.columns(2)
        
        with col1:
            # Descritores mais difíceis
            bottom_descritores = taxa_descritor.nsmallest(15, 'taxa_acerto')
            
            fig = px.bar(
                bottom_descritores,
                x='taxa_acerto',
                y='MTI_DESCRITOR',
                orientation='h',
                color='DIS_NOME',
                title="15 Descritores Mais Difíceis",
                labels={'taxa_acerto': 'Taxa de Acerto (%)', 'MTI_DESCRITOR': 'Descritor'}
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Descritores mais fáceis
            top_descritores = taxa_descritor.nlargest(15, 'taxa_acerto')
            
            fig = px.bar(
                top_descritores,
                x='taxa_acerto',
                y='MTI_DESCRITOR',
                orientation='h',
                color='DIS_NOME',
                title="15 Descritores Mais Fáceis",
                labels={'taxa_acerto': 'Taxa de Acerto (%)', 'MTI_DESCRITOR': 'Descritor'}
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        # Histograma de distribuição
        fig = px.histogram(
            taxa_descritor,
            x='taxa_acerto',
            color='DIS_NOME',
            title="Distribuição das Taxas de Acerto por Descritor",
            labels={'taxa_acerto': 'Taxa de Acerto (%)', 'count': 'Número de Descritores'},
            nbins=20
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

# =================== APLICATIVO PRINCIPAL ===================

def main():
    """Função principal do aplicativo"""
    
    # Cabeçalho
    st.title("📊 SAEV - Sistema de Análise Educacional")
    st.subheader("🎯 Galeria de Painéis com Filtros Avançados")
    st.markdown("---")
    
    # Verificar conexão com banco
    con = conectar_banco()
    if not con:
        st.error("❌ Não foi possível conectar ao banco de dados. Verifique se o arquivo 'db/avaliacao_prod.duckdb' existe.")
        return
    con.close()
    
    # Criar filtros na sidebar
    filtros = criar_filtros()
    
    # Verificar se algum filtro foi selecionado
    filtros_aplicados = any(filtros.values())
    
    if not filtros_aplicados:
        st.info("ℹ️ **Selecione ao menos um filtro na barra lateral para visualizar os dados.**")
        st.markdown("""
        ### 📋 Como usar este painel:
        
        1. **Selecione os filtros** na barra lateral à esquerda
        2. **Use múltipla seleção** para comparar diferentes categorias
        3. **Clique em "Todos"** nos filtros de Município e Escola para selecionar tudo
        4. **Explore os dois painéis** disponíveis:
           - **Painel 1:** Visão geral com estatísticas e distribuições
           - **Painel 2:** Análises detalhadas de taxa de acerto
        
        ### 🎯 Filtros disponíveis:
        - 📅 **Ano:** Período da avaliação
        - 🏙️ **Município:** Localização geográfica
        - 🏫 **Escola:** Instituição de ensino
        - 📚 **Disciplina:** Matéria avaliada
        - 🎓 **Série:** Ano escolar
        - 📝 **Teste:** Tipo de avaliação (Diagnóstica, Formativa)
        """)
        return
    
    # Carregar dados com filtros aplicados
    with st.spinner("📊 Carregando dados..."):
        df = carregar_dados_filtrados(filtros)
    
    if df.empty:
        st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados. Tente ajustar os filtros.")
        return
    
    # Mostrar resumo dos filtros aplicados
    st.success(f"✅ **{len(df):,} registros** encontrados com os filtros aplicados")
    
    # Seletor de painel
    painel = st.selectbox(
        "📋 Selecione o painel para visualização:",
        options=[
            "📊 Painel 1: Visão Geral dos Dados",
            "📈 Painel 2: Taxa de Acerto - Análises Detalhadas"
        ]
    )
    
    st.markdown("---")
    
    # Renderizar painel selecionado
    if "Painel 1" in painel:
        painel_visao_geral(df)
    elif "Painel 2" in painel:
        painel_taxas_acerto(df)
    
    # Rodapé
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; color: #666; font-size: 12px;'>
        📊 SAEV - Sistema de Análise Educacional do Espírito Santo<br>
        🕒 Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}<br>
        📈 Total de registros no banco: {len(df):,}
    </div>
    """, unsafe_allow_html=True)

# =================== EXECUÇÃO ===================

if __name__ == "__main__":
    main()

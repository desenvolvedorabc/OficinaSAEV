import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuração da página
st.set_page_config(
    page_title="SAEV - Rankings e Classificações",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🏆 SAEV - Rankings e Classificações por Teste")
st.markdown("---")

# Cache para conexão com banco
@st.cache_resource
def get_database_connection():
    """Conecta ao banco DuckDB"""
    try:
        conn = duckdb.connect('db/avaliacao_prod.duckdb', read_only=True)
        return conn
    except Exception as e:
        st.error(f"Erro ao conectar com o banco de dados: {e}")
        return None

# Cache para opções dos filtros
@st.cache_data
def load_filter_options():
    """Carrega opções para os filtros"""
    conn = get_database_connection()
    if not conn:
        return [], []
    
    try:
        # Disciplinas
        disciplinas_query = """
        SELECT DISTINCT DIS_NOME 
        FROM fato_resposta_aluno
        WHERE DIS_NOME IS NOT NULL
        ORDER BY DIS_NOME
        """
        disciplinas = conn.execute(disciplinas_query).df()['DIS_NOME'].tolist()
        
        # Testes
        testes_query = """
        SELECT DISTINCT TES_NOME 
        FROM fato_resposta_aluno
        WHERE TES_NOME IS NOT NULL
        ORDER BY TES_NOME
        """
        testes = conn.execute(testes_query).df()['TES_NOME'].tolist()
        
        return disciplinas, testes
        
    except Exception as e:
        st.error(f"Erro ao carregar opções dos filtros: {e}")
        return [], []

# Cache para ranking de alunos
@st.cache_data
def get_ranking_alunos(disciplina, teste, limite=50):
    """Obter ranking dos melhores alunos por disciplina e teste"""
    conn = get_database_connection()
    if not conn:
        return pd.DataFrame()
    
    try:
        query = f"""
        SELECT 
            a.ALU_NOME as nome_aluno,
            f.ALU_ID as id_aluno,
            e.ESC_NOME as nome_escola,
            f.ESC_INEP as codigo_escola,
            f.MUN_NOME as municipio,
            f.SER_NOME as serie,
            f.TUR_PERIODO as turno,
            SUM(f.ACERTO) as total_acertos,
            SUM(f.ERRO) as total_erros,
            SUM(f.ACERTO + f.ERRO) as total_questoes,
            ROUND(SUM(f.ACERTO) * 100.0 / SUM(f.ACERTO + f.ERRO), 2) as taxa_acerto,
            COUNT(DISTINCT f.MTI_CODIGO) as descritores_avaliados
        FROM fato_resposta_aluno f
        JOIN dim_aluno a ON f.ALU_ID = a.ALU_ID
        JOIN dim_escola e ON f.ESC_INEP = e.ESC_INEP
        WHERE f.DIS_NOME = '{disciplina}'
          AND f.TES_NOME = '{teste}'
          AND (f.ACERTO + f.ERRO) > 0
        GROUP BY 
            a.ALU_NOME, f.ALU_ID, e.ESC_NOME, f.ESC_INEP, 
            f.MUN_NOME, f.SER_NOME, f.TUR_PERIODO
        HAVING SUM(f.ACERTO + f.ERRO) >= 5  -- Filtro: pelo menos 5 questões
        ORDER BY taxa_acerto DESC, total_acertos DESC
        LIMIT {limite}
        """
        
        resultado = conn.execute(query).df()
        return resultado
        
    except Exception as e:
        st.error(f"Erro ao carregar ranking de alunos: {e}")
        return pd.DataFrame()

# Cache para ranking de escolas
@st.cache_data
def get_ranking_escolas(disciplina, teste, limite=10):
    """Obter ranking das melhores escolas por disciplina e teste"""
    conn = get_database_connection()
    if not conn:
        return pd.DataFrame()
    
    try:
        query = f"""
        SELECT 
            e.ESC_NOME as nome_escola,
            f.ESC_INEP as codigo_escola,
            f.MUN_NOME as municipio,
            COUNT(DISTINCT f.ALU_ID) as total_alunos,
            SUM(f.ACERTO) as total_acertos,
            SUM(f.ERRO) as total_erros,
            SUM(f.ACERTO + f.ERRO) as total_questoes,
            ROUND(SUM(f.ACERTO) * 100.0 / SUM(f.ACERTO + f.ERRO), 2) as taxa_acerto,
            COUNT(DISTINCT f.MTI_CODIGO) as descritores_avaliados,
            -- Distribuição por série
            COUNT(DISTINCT f.SER_NOME) as series_atendidas
        FROM fato_resposta_aluno f
        JOIN dim_escola e ON f.ESC_INEP = e.ESC_INEP
        WHERE f.DIS_NOME = '{disciplina}'
          AND f.TES_NOME = '{teste}'
          AND (f.ACERTO + f.ERRO) > 0
        GROUP BY 
            e.ESC_NOME, f.ESC_INEP, f.MUN_NOME
        HAVING 
            COUNT(DISTINCT f.ALU_ID) >= 10  -- Pelo menos 10 alunos
            AND SUM(f.ACERTO + f.ERRO) >= 100  -- Pelo menos 100 questões
        ORDER BY taxa_acerto DESC, total_alunos DESC
        LIMIT {limite}
        """
        
        resultado = conn.execute(query).df()
        return resultado
        
    except Exception as e:
        st.error(f"Erro ao carregar ranking de escolas: {e}")
        return pd.DataFrame()

# Cache para estatísticas gerais
@st.cache_data
def get_estatisticas_gerais(disciplina, teste):
    """Obter estatísticas gerais do teste"""
    conn = get_database_connection()
    if not conn:
        return {}
    
    try:
        query = f"""
        SELECT 
            COUNT(DISTINCT f.ALU_ID) as total_alunos,
            COUNT(DISTINCT f.ESC_INEP) as total_escolas,
            COUNT(DISTINCT f.MUN_NOME) as total_municipios,
            SUM(f.ACERTO) as total_acertos,
            SUM(f.ERRO) as total_erros,
            SUM(f.ACERTO + f.ERRO) as total_questoes,
            ROUND(SUM(f.ACERTO) * 100.0 / SUM(f.ACERTO + f.ERRO), 2) as taxa_acerto_geral,
            COUNT(DISTINCT f.MTI_CODIGO) as total_descritores,
            -- Estatísticas de distribuição
            ROUND(AVG(sub.taxa_aluno), 2) as media_taxa_alunos,
            ROUND(MIN(sub.taxa_aluno), 2) as min_taxa_aluno,
            ROUND(MAX(sub.taxa_aluno), 2) as max_taxa_aluno
        FROM fato_resposta_aluno f
        JOIN (
            SELECT 
                ALU_ID,
                ROUND(SUM(ACERTO) * 100.0 / SUM(ACERTO + ERRO), 2) as taxa_aluno
            FROM fato_resposta_aluno
            WHERE DIS_NOME = '{disciplina}' AND TES_NOME = '{teste}'
              AND (ACERTO + ERRO) > 0
            GROUP BY ALU_ID
            HAVING SUM(ACERTO + ERRO) >= 5
        ) sub ON f.ALU_ID = sub.ALU_ID
        WHERE f.DIS_NOME = '{disciplina}'
          AND f.TES_NOME = '{teste}'
        """
        
        resultado = conn.execute(query).df()
        return resultado.iloc[0].to_dict()
        
    except Exception as e:
        st.error(f"Erro ao carregar estatísticas gerais: {e}")
        return {}

# Interface principal
def main():
    # Carregar opções dos filtros
    disciplinas_opcoes, testes_opcoes = load_filter_options()
    
    if not disciplinas_opcoes or not testes_opcoes:
        st.error("Não foi possível carregar as opções de filtros. Verifique a conexão com o banco de dados.")
        return
    
    # Sidebar para filtros
    st.sidebar.header("🎯 Filtros para Ranking")
    st.sidebar.markdown("Selecione a disciplina e o teste:")
    
    # Filtro por Disciplina
    disciplina_selecionada = st.sidebar.selectbox(
        "📚 Disciplina:",
        options=disciplinas_opcoes,
        index=0
    )
    
    # Filtro por Teste
    teste_selecionado = st.sidebar.selectbox(
        "📝 Teste:",
        options=testes_opcoes,
        index=0
    )
    
    st.sidebar.markdown("---")
    
    # Opções de limite
    st.sidebar.markdown("### 🔢 Configurações de Ranking")
    
    limite_alunos = st.sidebar.slider(
        "👥 Número de alunos no ranking:",
        min_value=10,
        max_value=100,
        value=50,
        step=10
    )
    
    limite_escolas = st.sidebar.slider(
        "🏫 Número de escolas no ranking:",
        min_value=5,
        max_value=20,
        value=10,
        step=1
    )
    
    # Botão para atualizar dados
    if st.sidebar.button("🔄 Atualizar Rankings", type="primary"):
        st.cache_data.clear()
        st.rerun()
    
    # Mostrar seleção atual
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📋 Seleção Atual:")
    st.sidebar.markdown(f"**Disciplina:** {disciplina_selecionada}")
    st.sidebar.markdown(f"**Teste:** {teste_selecionado}")
    
    # Área principal
    if disciplina_selecionada and teste_selecionado:
        
        with st.spinner("Carregando dados e calculando rankings..."):
            # Carregar dados
            ranking_alunos = get_ranking_alunos(disciplina_selecionada, teste_selecionado, limite_alunos)
            ranking_escolas = get_ranking_escolas(disciplina_selecionada, teste_selecionado, limite_escolas)
            estatisticas = get_estatisticas_gerais(disciplina_selecionada, teste_selecionado)
        
        # Exibir estatísticas gerais
        if estatisticas:
            st.subheader("📊 Estatísticas Gerais do Teste")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="👥 Total de Alunos",
                    value=f"{estatisticas.get('total_alunos', 0):,}".replace(',', '.')
                )
            
            with col2:
                st.metric(
                    label="🏫 Total de Escolas",
                    value=f"{estatisticas.get('total_escolas', 0):,}".replace(',', '.')
                )
            
            with col3:
                st.metric(
                    label="📝 Total de Questões",
                    value=f"{estatisticas.get('total_questoes', 0):,}".replace(',', '.')
                )
            
            with col4:
                st.metric(
                    label="📊 Taxa de Acerto Geral",
                    value=f"{estatisticas.get('taxa_acerto_geral', 0):.2f}%"
                )
            
            # Segunda linha de métricas
            col5, col6, col7, col8 = st.columns(4)
            
            with col5:
                st.metric(
                    label="🎯 Descritores Avaliados",
                    value=f"{estatisticas.get('total_descritores', 0)}"
                )
            
            with col6:
                st.metric(
                    label="📈 Taxa Média dos Alunos",
                    value=f"{estatisticas.get('media_taxa_alunos', 0):.2f}%"
                )
            
            with col7:
                st.metric(
                    label="⬇️ Menor Taxa Individual",
                    value=f"{estatisticas.get('min_taxa_aluno', 0):.2f}%"
                )
            
            with col8:
                st.metric(
                    label="⬆️ Maior Taxa Individual", 
                    value=f"{estatisticas.get('max_taxa_aluno', 0):.2f}%"
                )
        
        st.markdown("---")
        
        # Layout em duas colunas para os rankings
        col_alunos, col_escolas = st.columns([3, 2])
        
        # Ranking de Alunos
        with col_alunos:
            st.subheader(f"🏆 Top {limite_alunos} Alunos - {disciplina_selecionada}")
            st.markdown(f"**Teste:** {teste_selecionado}")
            
            if not ranking_alunos.empty:
                # Criar tabela formatada
                ranking_display = ranking_alunos.copy()
                ranking_display['ranking'] = range(1, len(ranking_display) + 1)
                ranking_display['taxa_formatada'] = ranking_display['taxa_acerto'].apply(lambda x: f"{x:.2f}%")
                ranking_display['questoes_info'] = ranking_display.apply(
                    lambda row: f"{row['total_acertos']}/{row['total_questoes']}", axis=1
                )
                
                # Selecionar e renomear colunas para exibição
                colunas_exibicao = {
                    'ranking': '#',
                    'nome_aluno': 'Aluno',
                    'nome_escola': 'Escola',
                    'municipio': 'Município',
                    'serie': 'Série',
                    'turno': 'Turno',
                    'questoes_info': 'Acertos/Total',
                    'taxa_formatada': 'Taxa (%)',
                    'descritores_avaliados': 'Descritores'
                }
                
                df_display = ranking_display[list(colunas_exibicao.keys())].rename(columns=colunas_exibicao)
                
                # Exibir tabela
                st.dataframe(
                    df_display,
                    use_container_width=True,
                    height=600,
                    hide_index=True
                )
                
                # Gráfico de barras dos top 10
                if len(ranking_alunos) >= 10:
                    st.subheader("📊 Top 10 Alunos - Visualização")
                    top_10 = ranking_alunos.head(10)
                    
                    fig = px.bar(
                        top_10,
                        x='taxa_acerto',
                        y='nome_aluno',
                        orientation='h',
                        color='taxa_acerto',
                        color_continuous_scale='RdYlGn',
                        title=f"Taxa de Acerto - Top 10 Alunos",
                        labels={'taxa_acerto': 'Taxa de Acerto (%)', 'nome_aluno': 'Aluno'},
                        text='taxa_acerto'
                    )
                    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                    fig.update_layout(height=400, yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig, use_container_width=True)
                
                # Botão para download
                csv_alunos = ranking_alunos.to_csv(index=False)
                st.download_button(
                    label="📥 Download Ranking Alunos (CSV)",
                    data=csv_alunos,
                    file_name=f"ranking_alunos_{disciplina_selecionada}_{teste_selecionado}.csv",
                    mime="text/csv"
                )
            
            else:
                st.info("Nenhum aluno encontrado com os filtros aplicados.")
        
        # Ranking de Escolas
        with col_escolas:
            st.subheader(f"🏫 Top {limite_escolas} Escolas - {disciplina_selecionada}")
            st.markdown(f"**Teste:** {teste_selecionado}")
            
            if not ranking_escolas.empty:
                # Criar tabela formatada
                ranking_escolas_display = ranking_escolas.copy()
                ranking_escolas_display['ranking'] = range(1, len(ranking_escolas_display) + 1)
                ranking_escolas_display['taxa_formatada'] = ranking_escolas_display['taxa_acerto'].apply(lambda x: f"{x:.2f}%")
                
                # Selecionar e renomear colunas para exibição
                colunas_escolas = {
                    'ranking': '#',
                    'nome_escola': 'Escola',
                    'municipio': 'Município',
                    'total_alunos': 'Alunos',
                    'taxa_formatada': 'Taxa (%)',
                    'series_atendidas': 'Séries'
                }
                
                df_escolas_display = ranking_escolas_display[list(colunas_escolas.keys())].rename(columns=colunas_escolas)
                
                # Exibir tabela
                st.dataframe(
                    df_escolas_display,
                    use_container_width=True,
                    height=400,
                    hide_index=True
                )
                
                # Gráfico de barras das escolas
                fig_escolas = px.bar(
                    ranking_escolas,
                    x='taxa_acerto',
                    y='nome_escola',
                    orientation='h',
                    color='total_alunos',
                    color_continuous_scale='Blues',
                    title=f"Taxa de Acerto - Top {limite_escolas} Escolas",
                    labels={'taxa_acerto': 'Taxa de Acerto (%)', 'nome_escola': 'Escola', 'total_alunos': 'Nº Alunos'},
                    text='taxa_acerto'
                )
                fig_escolas.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig_escolas.update_layout(height=400, yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_escolas, use_container_width=True)
                
                # Botão para download
                csv_escolas = ranking_escolas.to_csv(index=False)
                st.download_button(
                    label="📥 Download Ranking Escolas (CSV)",
                    data=csv_escolas,
                    file_name=f"ranking_escolas_{disciplina_selecionada}_{teste_selecionado}.csv",
                    mime="text/csv"
                )
            
            else:
                st.info("Nenhuma escola encontrada com os filtros aplicados.")
    
    # Seção de informações técnicas
    with st.expander("ℹ️ Informações Técnicas"):
        st.markdown("""
        ### 🎯 **Critérios de Ranking:**
        
        #### **👥 Ranking de Alunos:**
        - **Filtro mínimo:** 5 questões respondidas
        - **Ordenação:** Taxa de acerto (DESC) → Total de acertos (DESC)
        - **Dados exibidos:** Nome, escola, município, série, turno, performance
        
        #### **🏫 Ranking de Escolas:**
        - **Filtro mínimo:** 10 alunos e 100 questões respondidas
        - **Ordenação:** Taxa de acerto (DESC) → Total de alunos (DESC)
        - **Dados exibidos:** Nome, município, nº alunos, taxa, séries atendidas
        
        ### 📊 **Métricas Calculadas:**
        - **Taxa de Acerto:** (Acertos ÷ Total de Questões) × 100
        - **Descritores Avaliados:** Número de competências testadas
        - **Séries Atendidas:** Diversidade de níveis na escola
        
        ### 🔧 **Funcionalidades:**
        - **Filtros Interativos:** Disciplina e teste específicos
        - **Limites Configuráveis:** Quantidade de resultados no ranking
        - **Download CSV:** Dados completos para análise externa
        - **Visualizações:** Gráficos interativos dos top performers
        """)

if __name__ == "__main__":
    main()

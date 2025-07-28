import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuração da página
st.set_page_config(
    page_title="SAEV - Dashboard Interativo com Filtros",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("📊 SAEV - Sistema de Avaliação da Educação do ES (com Filtros)")
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

# Cache para dados dos filtros
@st.cache_data
def load_filter_options():
    """Carrega opções para os filtros"""
    conn = get_database_connection()
    if not conn:
        return {}, {}, {}, {}
    
    try:
        # Municípios
        municipios_query = """
        SELECT DISTINCT f.MUN_NOME 
        FROM fato_resposta_aluno f
        WHERE f.MUN_NOME IS NOT NULL
        ORDER BY f.MUN_NOME
        """
        municipios = conn.execute(municipios_query).df()['MUN_NOME'].tolist()
        
        # Disciplinas
        disciplinas_query = """
        SELECT DISTINCT DIS_NOME 
        FROM fato_resposta_aluno
        WHERE DIS_NOME IS NOT NULL
        ORDER BY DIS_NOME
        """
        disciplinas = conn.execute(disciplinas_query).df()['DIS_NOME'].tolist()
        
        # Séries
        series_query = """
        SELECT DISTINCT SER_NOME 
        FROM fato_resposta_aluno
        WHERE SER_NOME IS NOT NULL
        ORDER BY SER_NOME
        """
        series = conn.execute(series_query).df()['SER_NOME'].tolist()
        
        # Testes
        testes_query = """
        SELECT DISTINCT TES_NOME 
        FROM fato_resposta_aluno
        WHERE TES_NOME IS NOT NULL
        ORDER BY TES_NOME
        """
        testes = conn.execute(testes_query).df()['TES_NOME'].tolist()
        
        return municipios, disciplinas, series, testes
        
    except Exception as e:
        st.error(f"Erro ao carregar opções dos filtros: {e}")
        return [], [], [], []

# Cache para métricas principais com filtros
@st.cache_data
def load_main_metrics(municipios_selecionados, disciplinas_selecionadas, series_selecionadas, testes_selecionados):
    """Carrega métricas principais com filtros aplicados"""
    conn = get_database_connection()
    if not conn:
        return {}
    
    # Construir condições WHERE baseadas nos filtros
    where_conditions = ["1=1"]  # Condição base sempre verdadeira
    
    if municipios_selecionados:
        municipios_str = "', '".join(municipios_selecionados)
        where_conditions.append(f"f.MUN_NOME IN ('{municipios_str}')")
    
    if disciplinas_selecionadas:
        disciplinas_str = "', '".join(disciplinas_selecionadas)
        where_conditions.append(f"f.DIS_NOME IN ('{disciplinas_str}')")
    
    if series_selecionadas:
        series_str = "', '".join(series_selecionadas)
        where_conditions.append(f"f.SER_NOME IN ('{series_str}')")
    
    if testes_selecionados:
        testes_str = "', '".join(testes_selecionados)
        where_conditions.append(f"f.TES_NOME IN ('{testes_str}')")
    
    where_clause = " AND ".join(where_conditions)
    
    try:
        metrics_query = f"""
        SELECT 
            COUNT(DISTINCT f.ALU_ID) as total_alunos,
            COUNT(DISTINCT f.ESC_INEP) as total_escolas,
            COUNT(DISTINCT f.MUN_NOME) as total_municipios,
            COUNT(DISTINCT f.TES_NOME) as total_testes,
            SUM(f.ACERTO + f.ERRO) as total_questoes,
            SUM(f.ACERTO) as total_acertos,
            ROUND(SUM(f.ACERTO) * 100.0 / SUM(f.ACERTO + f.ERRO), 2) as taxa_acerto_geral
        FROM fato_resposta_aluno f
        WHERE {where_clause}
        """
        
        result = conn.execute(metrics_query).df()
        return result.iloc[0].to_dict()
        
    except Exception as e:
        st.error(f"Erro ao calcular métricas: {e}")
        return {}

# Cache para dados dos gráficos com filtros
@st.cache_data
def load_chart_data(municipios_selecionados, disciplinas_selecionadas, series_selecionadas, testes_selecionados):
    """Carrega dados para os gráficos com filtros aplicados"""
    conn = get_database_connection()
    if not conn:
        return {}, {}, {}, {}, {}, {}
    
    # Construir condições WHERE
    where_conditions = ["1=1"]
    
    if municipios_selecionados:
        municipios_str = "', '".join(municipios_selecionados)
        where_conditions.append(f"f.MUN_NOME IN ('{municipios_str}')")
    
    if disciplinas_selecionadas:
        disciplinas_str = "', '".join(disciplinas_selecionadas)
        where_conditions.append(f"f.DIS_NOME IN ('{disciplinas_str}')")
    
    if series_selecionadas:
        series_str = "', '".join(series_selecionadas)
        where_conditions.append(f"f.SER_NOME IN ('{series_str}')")
    
    if testes_selecionados:
        testes_str = "', '".join(testes_selecionados)
        where_conditions.append(f"f.TES_NOME IN ('{testes_str}')")
    
    where_clause = " AND ".join(where_conditions)
    
    try:
        # 1. Top Municípios por Taxa de Acerto
        top_municipios_query = f"""
        SELECT 
            f.MUN_NOME as municipio,
            SUM(f.ACERTO + f.ERRO) as total_questoes,
            SUM(f.ACERTO) as acertos,
            ROUND(SUM(f.ACERTO) * 100.0 / SUM(f.ACERTO + f.ERRO), 2) as taxa_acerto
        FROM fato_resposta_aluno f
        WHERE {where_clause}
        GROUP BY f.MUN_NOME
        HAVING SUM(f.ACERTO + f.ERRO) >= 1000
        ORDER BY taxa_acerto DESC
        LIMIT 10
        """
        top_municipios = conn.execute(top_municipios_query).df()
        
        # 2. Distribuição de Alunos por Município
        alunos_municipio_query = f"""
        SELECT 
            f.MUN_NOME as municipio,
            COUNT(DISTINCT f.ALU_ID) as total_alunos
        FROM fato_resposta_aluno f
        WHERE {where_clause}
        GROUP BY f.MUN_NOME
        ORDER BY total_alunos DESC
        LIMIT 15
        """
        alunos_municipio = conn.execute(alunos_municipio_query).df()
        
        # 3. Taxa de Acerto por Série e Disciplina
        serie_disciplina_query = f"""
        SELECT 
            f.SER_NOME as serie,
            f.DIS_NOME as disciplina,
            SUM(f.ACERTO) as acertos,
            SUM(f.ACERTO + f.ERRO) as total_questoes,
            ROUND(SUM(f.ACERTO) * 100.0 / SUM(f.ACERTO + f.ERRO), 2) as taxa_acerto
        FROM fato_resposta_aluno f
        WHERE {where_clause}
        GROUP BY f.SER_NOME, f.DIS_NOME
        ORDER BY f.SER_NOME, f.DIS_NOME
        """
        serie_disciplina = conn.execute(serie_disciplina_query).df()
        
        # 4. Performance por Disciplina
        performance_disciplina_query = f"""
        SELECT 
            f.DIS_NOME as disciplina,
            SUM(f.ACERTO) as acertos,
            SUM(f.ACERTO + f.ERRO) as total_questoes,
            ROUND(SUM(f.ACERTO) * 100.0 / SUM(f.ACERTO + f.ERRO), 2) as taxa_acerto
        FROM fato_resposta_aluno f
        WHERE {where_clause}
        GROUP BY f.DIS_NOME
        ORDER BY taxa_acerto DESC
        """
        performance_disciplina = conn.execute(performance_disciplina_query).df()
        
        # 5. Detalhes dos Municípios (Tabela)
        detalhes_municipios_query = f"""
        SELECT 
            f.MUN_NOME as municipio,
            COUNT(DISTINCT f.ALU_ID) as alunos,
            SUM(f.ACERTO + f.ERRO) as questoes,
            ROUND(SUM(f.ACERTO) * 100.0 / SUM(f.ACERTO + f.ERRO), 2) as taxa_acerto
        FROM fato_resposta_aluno f
        WHERE {where_clause}
        GROUP BY f.MUN_NOME
        HAVING SUM(f.ACERTO + f.ERRO) >= 500
        ORDER BY taxa_acerto DESC
        LIMIT 20
        """
        detalhes_municipios = conn.execute(detalhes_municipios_query).df()
        
        # 6. Descritores Mais Difíceis
        descritores_dificeis_query = f"""
        SELECT 
            SUBSTR(d.MTI_DESCRITOR, 1, 80) || '...' as descritor,
            SUM(f.ACERTO + f.ERRO) as total_questoes,
            SUM(f.ACERTO) as acertos,
            ROUND(SUM(f.ACERTO) * 100.0 / SUM(f.ACERTO + f.ERRO), 2) as taxa_acerto
        FROM fato_resposta_aluno f
        JOIN dim_descritor d ON f.MTI_CODIGO = d.MTI_CODIGO
        WHERE {where_clause}
        GROUP BY d.MTI_DESCRITOR
        HAVING SUM(f.ACERTO + f.ERRO) >= 500
        ORDER BY taxa_acerto ASC
        LIMIT 10
        """
        descritores_dificeis = conn.execute(descritores_dificeis_query).df()
        
        return (top_municipios, alunos_municipio, serie_disciplina, 
                performance_disciplina, detalhes_municipios, descritores_dificeis)
        
    except Exception as e:
        st.error(f"Erro ao carregar dados dos gráficos: {e}")
        return {}, {}, {}, {}, {}, {}

# Interface principal
def main():
    # Carregar opções dos filtros
    municipios_opcoes, disciplinas_opcoes, series_opcoes, testes_opcoes = load_filter_options()
    
    # Sidebar para filtros
    st.sidebar.header("🎯 Filtros Interativos")
    st.sidebar.markdown("Selecione os filtros desejados:")
    
    # Botão para limpar filtros
    if st.sidebar.button("🗑️ Limpar Todos os Filtros"):
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Filtro por Município
    municipios_selecionados = st.sidebar.multiselect(
        "🏙️ Município:",
        options=municipios_opcoes,
        default=[],
        placeholder="Selecione municípios..."
    )
    
    # Filtro por Disciplina
    disciplinas_selecionadas = st.sidebar.multiselect(
        "📚 Disciplina:",
        options=disciplinas_opcoes,
        default=[],
        placeholder="Selecione disciplinas..."
    )
    
    # Filtro por Série
    series_selecionadas = st.sidebar.multiselect(
        "🎓 Série:",
        options=series_opcoes,
        default=[],
        placeholder="Selecione séries..."
    )
    
    # Filtro por Teste
    testes_selecionados = st.sidebar.multiselect(
        "📝 Teste:",
        options=testes_opcoes,
        default=[],
        placeholder="Selecione testes..."
    )
    
    # Mostrar filtros aplicados
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔍 Filtros Aplicados:")
    
    filtros_aplicados = []
    if municipios_selecionados:
        filtros_aplicados.append(f"**Municípios:** {len(municipios_selecionados)} selecionados")
    if disciplinas_selecionadas:
        filtros_aplicados.append(f"**Disciplinas:** {len(disciplinas_selecionadas)} selecionadas")
    if series_selecionadas:
        filtros_aplicados.append(f"**Séries:** {len(series_selecionadas)} selecionadas")
    if testes_selecionados:
        filtros_aplicados.append(f"**Testes:** {len(testes_selecionados)} selecionados")
    
    if filtros_aplicados:
        for filtro in filtros_aplicados:
            st.sidebar.markdown(f"- {filtro}")
    else:
        st.sidebar.markdown("*Nenhum filtro aplicado (mostrando todos os dados)*")
    
    # Área principal do dashboard
    with st.spinner("Carregando dados..."):
        # Carregar métricas
        metrics = load_main_metrics(municipios_selecionados, disciplinas_selecionadas, 
                                  series_selecionadas, testes_selecionados)
        
        # Carregar dados dos gráficos
        (top_municipios, alunos_municipio, serie_disciplina, 
         performance_disciplina, detalhes_municipios, descritores_dificeis) = load_chart_data(
            municipios_selecionados, disciplinas_selecionadas, 
            series_selecionadas, testes_selecionados
        )
    
    # Exibir métricas principais
    if metrics:
        st.subheader("🎯 Métricas Principais")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="👨‍🎓 Total de Alunos",
                value=f"{metrics.get('total_alunos', 0):,}".replace(',', '.')
            )
        
        with col2:
            st.metric(
                label="🏫 Total de Escolas",
                value=f"{metrics.get('total_escolas', 0):,}".replace(',', '.')
            )
        
        with col3:
            st.metric(
                label="🏙️ Total de Municípios",
                value=f"{metrics.get('total_municipios', 0):,}".replace(',', '.')
            )
        
        with col4:
            st.metric(
                label="📝 Total de Testes",
                value=f"{metrics.get('total_testes', 0):,}".replace(',', '.')
            )
        
        # Segunda linha de métricas
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            st.metric(
                label="❓ Total de Questões",
                value=f"{metrics.get('total_questoes', 0):,}".replace(',', '.')
            )
        
        with col6:
            st.metric(
                label="✅ Total de Acertos",
                value=f"{metrics.get('total_acertos', 0):,}".replace(',', '.')
            )
        
        with col7:
            taxa = metrics.get('taxa_acerto_geral', 0)
            st.metric(
                label="📊 Taxa de Acerto Geral",
                value=f"{taxa}%"
            )
        
        with col8:
            erros = metrics.get('total_questoes', 0) - metrics.get('total_acertos', 0)
            st.metric(
                label="❌ Total de Erros",
                value=f"{erros:,}".replace(',', '.')
            )
    
    st.markdown("---")
    
    # Gráficos e visualizações
    if isinstance(top_municipios, pd.DataFrame) and not top_municipios.empty:
        # Primeira linha de gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 Top 10 Municípios por Taxa de Acerto")
            fig1 = px.bar(
                top_municipios,
                x='taxa_acerto',
                y='municipio',
                orientation='h',
                color='taxa_acerto',
                color_continuous_scale='RdYlGn',
                title="Performance por Município (≥ 1000 questões)",
                labels={'taxa_acerto': 'Taxa de Acerto (%)', 'municipio': 'Município'}
            )
            fig1.update_layout(height=400)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            st.subheader("👨‍🎓 Distribuição de Alunos por Município")
            fig2 = px.bar(
                alunos_municipio,
                x='total_alunos',
                y='municipio',
                orientation='h',
                color='total_alunos',
                color_continuous_scale='Blues',
                title="Top 15 Municípios por Volume de Alunos",
                labels={'total_alunos': 'Total de Alunos', 'municipio': 'Município'}
            )
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, use_container_width=True)
        
        # Segunda linha de gráficos
        col3, col4 = st.columns(2)
        
        with col3:
            st.subheader("📚 Taxa de Acerto por Série e Disciplina")
            if isinstance(serie_disciplina, pd.DataFrame) and not serie_disciplina.empty:
                fig3 = px.bar(
                    serie_disciplina,
                    x='serie',
                    y='taxa_acerto',
                    color='disciplina',
                    barmode='group',
                    title="Comparação entre Disciplinas por Série",
                    labels={'taxa_acerto': 'Taxa de Acerto (%)', 'serie': 'Série', 'disciplina': 'Disciplina'}
                )
                fig3.update_layout(height=400)
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("Sem dados suficientes para exibir este gráfico com os filtros aplicados.")
        
        with col4:
            st.subheader("📖 Performance por Disciplina")
            if isinstance(performance_disciplina, pd.DataFrame) and not performance_disciplina.empty:
                fig4 = px.pie(
                    performance_disciplina,
                    values='total_questoes',
                    names='disciplina',
                    title="Distribuição de Questões por Disciplina",
                )
                fig4.update_layout(height=400)
                st.plotly_chart(fig4, use_container_width=True)
            else:
                st.info("Sem dados suficientes para exibir este gráfico com os filtros aplicados.")
        
        # Terceira linha
        col5, col6 = st.columns(2)
        
        with col5:
            st.subheader("📋 Detalhes dos Municípios")
            if isinstance(detalhes_municipios, pd.DataFrame) and not detalhes_municipios.empty:
                # Formatar a tabela
                detalhes_municipios_display = detalhes_municipios.copy()
                detalhes_municipios_display['Taxa (%)'] = detalhes_municipios_display['taxa_acerto'].apply(lambda x: f"{x}%")
                detalhes_municipios_display = detalhes_municipios_display[['municipio', 'alunos', 'Taxa (%)']]
                detalhes_municipios_display.columns = ['Município', 'Alunos', 'Taxa (%)']
                
                st.dataframe(
                    detalhes_municipios_display,
                    use_container_width=True,
                    height=400
                )
            else:
                st.info("Sem dados suficientes para exibir esta tabela com os filtros aplicados.")
        
        with col6:
            st.subheader("🎯 Descritores Mais Difíceis")
            if isinstance(descritores_dificeis, pd.DataFrame) and not descritores_dificeis.empty:
                fig6 = px.bar(
                    descritores_dificeis,
                    x='taxa_acerto',
                    y='descritor',
                    orientation='h',
                    color='taxa_acerto',
                    color_continuous_scale='Reds_r',
                    title="Competências com Menor Taxa de Acerto (≥ 500 questões)",
                    labels={'taxa_acerto': 'Taxa de Acerto (%)', 'descritor': 'Descritor'}
                )
                fig6.update_layout(height=400)
                st.plotly_chart(fig6, use_container_width=True)
            else:
                st.info("Sem dados suficientes para exibir este gráfico com os filtros aplicados.")
    
    else:
        st.warning("Nenhum dado encontrado com os filtros aplicados. Tente ajustar os filtros.")
    
    # Seção de informações técnicas
    with st.expander("ℹ️ Informações Técnicas"):
        st.markdown("""
        ### 📊 **Sobre este Dashboard:**
        - **Dados:** Sistema SAEV - Espírito Santo
        - **Arquitetura:** Star Schema com DuckDB
        - **Filtros:** Interativos por Município, Disciplina, Série e Teste
        - **Atualizações:** Dados atualizados automaticamente com cache inteligente
        
        ### 🎯 **Funcionalidades:**
        - **Filtros Múltiplos:** Combine diferentes critérios de análise
        - **Métricas Dinâmicas:** Valores recalculados em tempo real
        - **Visualizações Interativas:** Gráficos Plotly com hover e zoom
        - **Tabelas Detalhadas:** Dados tabulares para análise aprofundada
        
        ### ⚡ **Performance:**
        - **Cache Otimizado:** Dados reutilizados para melhor performance
        - **Queries Eficientes:** SQL otimizado para grandes volumes
        - **Filtros de Qualidade:** Apenas dados confiáveis (≥500 ou ≥1000 questões)
        """)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Dashboard específico para análise da disciplina Leitura no SAEV

Este dashboard trata a disciplina Leitura de forma diferenciada:
- Métricas baseadas em níveis de proficiência
- Visualizações específicas para distribuição de níveis
- Rankings baseados no nível mais alto atingido

Autor: Sistema SAEV
Data: 08/08/2025
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import duckdb
from pathlib import Path
from utils_leitura import (
    get_nivel_leitura_numerico, 
    get_descricao_nivel_leitura, 
    get_cor_nivel_leitura,
    calcular_metricas_leitura,
    NIVEIS_LEITURA,
    CORES_NIVEIS
)
from duckdb_manager import safe_get_dataframe, test_connection
from duckdb_concurrent_solution import cached_query_safe, safe_dataframe

# Configuração da página
st.set_page_config(
    page_title="SAEV - Análise de Leitura",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def carregar_dados_leitura():
    """Carrega dados específicos da disciplina Leitura usando gerenciador concorrente"""
    
    query = """
    SELECT 
        f.MUN_NOME,
        f.ESC_INEP,
        e.ESC_NOME,
        f.SER_NOME,
        f.ALU_ID,
        a.ALU_NOME,
        f.AVA_NOME,
        f.AVA_ANO,
        f.TES_NOME,
        f.NIVEL_LEITURA,
        f.NIVEL_NUMERICO
    FROM fato_resposta_aluno f
    JOIN dim_aluno a ON f.ALU_ID = a.ALU_ID
    JOIN dim_escola e ON f.ESC_INEP = e.ESC_INEP
    WHERE f.DIS_NOME = 'Leitura' 
      AND f.NIVEL_LEITURA IS NOT NULL
    ORDER BY f.MUN_NOME, f.SER_NOME, f.ALU_ID
    """
    
    # Usar o gerenciador concorrente com cache
    df = cached_query_safe(query)
    
    if df is None:
        st.error("❌ Erro ao carregar dados de Leitura")
        st.stop()
    
    # Adicionar descrições
    df['DESCRICAO_NIVEL'] = df['NIVEL_LEITURA'].apply(get_descricao_nivel_leitura)
    df['COR_NIVEL'] = df['NIVEL_LEITURA'].apply(get_cor_nivel_leitura)
    
    return df

def main():
    st.title("📚 SAEV - Análise de Proficiência em Leitura")
    st.markdown("---")
    
    # Carregar dados
    df = carregar_dados_leitura()
    
    if df.empty:
        st.warning("⚠️ Nenhum dado de Leitura encontrado no banco.")
        return
    
    # Sidebar - Filtros
    st.sidebar.header("🔍 Filtros")
    
    # Filtro por município
    municipios = ['Todos'] + sorted(df['MUN_NOME'].unique().tolist())
    municipio_selecionado = st.sidebar.selectbox("Município:", municipios)
    
    # Filtrar por município
    if municipio_selecionado != 'Todos':
        df_filtrado = df[df['MUN_NOME'] == municipio_selecionado]
    else:
        df_filtrado = df.copy()
    
    # Filtro por série
    series = ['Todas'] + sorted(df_filtrado['SER_NOME'].unique().tolist())
    serie_selecionada = st.sidebar.selectbox("Série:", series)
    
    if serie_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['SER_NOME'] == serie_selecionada]
    
    # Filtro por avaliação
    avaliacoes = ['Todas'] + sorted(df_filtrado['AVA_NOME'].unique().tolist())
    avaliacao_selecionada = st.sidebar.selectbox("Avaliação:", avaliacoes)
    
    if avaliacao_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['AVA_NOME'] == avaliacao_selecionada]
    
    # Estatísticas gerais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total de Alunos", f"{len(df_filtrado):,}")
    
    with col2:
        nivel_medio = df_filtrado['NIVEL_NUMERICO'].mean() if len(df_filtrado) > 0 else 0
        st.metric("📈 Nível Médio", f"{nivel_medio:.2f}/6")
    
    with col3:
        fluentes = (df_filtrado['NIVEL_LEITURA'] == 'fluente').sum()
        pct_fluentes = (fluentes / len(df_filtrado) * 100) if len(df_filtrado) > 0 else 0
        st.metric("🌟 Leitores Fluentes", f"{pct_fluentes:.1f}%")
    
    with col4:
        nao_leitores = (df_filtrado['NIVEL_LEITURA'] == 'nao_leitor').sum()
        pct_nao_leitores = (nao_leitores / len(df_filtrado) * 100) if len(df_filtrado) > 0 else 0
        st.metric("⚠️ Não Leitores", f"{pct_nao_leitores:.1f}%")
    
    st.markdown("---")
    
    # Visualizações
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Distribuição por Níveis de Leitura")
        
        # Contar por nível
        distribuicao = df_filtrado['NIVEL_LEITURA'].value_counts()
        
        # Garantir que todos os níveis apareçam
        distribuicao_completa = pd.Series(index=NIVEIS_LEITURA, dtype=int).fillna(0)
        for nivel in distribuicao.index:
            if nivel in distribuicao_completa.index:
                distribuicao_completa[nivel] = distribuicao[nivel]
        
        # Criar gráfico de barras
        fig_dist = go.Figure()
        
        for i, nivel in enumerate(NIVEIS_LEITURA):
            fig_dist.add_trace(go.Bar(
                x=[get_descricao_nivel_leitura(nivel)],
                y=[distribuicao_completa[nivel]],
                name=get_descricao_nivel_leitura(nivel),
                marker_color=CORES_NIVEIS[i],
                text=[f"{distribuicao_completa[nivel]:,}"],
                textposition='auto'
            ))
        
        fig_dist.update_layout(
            showlegend=False,
            xaxis_title="Nível de Leitura",
            yaxis_title="Quantidade de Alunos",
            height=400
        )
        
        st.plotly_chart(fig_dist, use_container_width=True)
    
    with col2:
        st.subheader("🥧 Percentual por Nível")
        
        # Gráfico de pizza
        valores = [distribuicao_completa[nivel] for nivel in NIVEIS_LEITURA]
        labels = [get_descricao_nivel_leitura(nivel) for nivel in NIVEIS_LEITURA]
        
        fig_pizza = go.Figure(data=[go.Pie(
            labels=labels,
            values=valores,
            marker_colors=CORES_NIVEIS,
            textinfo='label+percent',
            textposition='auto'
        )])
        
        fig_pizza.update_layout(height=400)
        st.plotly_chart(fig_pizza, use_container_width=True)
    
    # Análise por série
    if municipio_selecionado == 'Todos' and serie_selecionada == 'Todas':
        st.subheader("📈 Distribuição por Série")
        
        # Pivô por série e nível
        pivot_serie = df_filtrado.pivot_table(
            values='ALU_ID',
            index='SER_NOME',
            columns='NIVEL_LEITURA',
            aggfunc='count',
            fill_value=0
        )
        
        # Garantir que todas as colunas existam
        for nivel in NIVEIS_LEITURA:
            if nivel not in pivot_serie.columns:
                pivot_serie[nivel] = 0
        
        # Reordenar colunas
        pivot_serie = pivot_serie[NIVEIS_LEITURA]
        
        # Gráfico de barras empilhadas
        fig_serie = go.Figure()
        
        for i, nivel in enumerate(NIVEIS_LEITURA):
            fig_serie.add_trace(go.Bar(
                name=get_descricao_nivel_leitura(nivel),
                x=pivot_serie.index,
                y=pivot_serie[nivel],
                marker_color=CORES_NIVEIS[i]
            ))
        
        fig_serie.update_layout(
            barmode='stack',
            xaxis_title="Série",
            yaxis_title="Quantidade de Alunos",
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        
        st.plotly_chart(fig_serie, use_container_width=True)
    
    # Análise por município (se não filtrado)
    if municipio_selecionado == 'Todos':
        st.subheader("🏛️ Top 10 Municípios - Maior % de Leitores Fluentes")
        
        municipios_fluentes = df_filtrado.groupby('MUN_NOME').agg({
            'ALU_ID': 'count',
            'NIVEL_LEITURA': lambda x: (x == 'fluente').sum()
        }).rename(columns={'ALU_ID': 'TOTAL', 'NIVEL_LEITURA': 'FLUENTES'})
        
        municipios_fluentes['PCT_FLUENTES'] = (
            municipios_fluentes['FLUENTES'] / municipios_fluentes['TOTAL'] * 100
        ).round(2)
        
        municipios_fluentes = municipios_fluentes[
            municipios_fluentes['TOTAL'] >= 10
        ].sort_values('PCT_FLUENTES', ascending=False).head(10)
        
        fig_mun = px.bar(
            municipios_fluentes.reset_index(),
            x='MUN_NOME',
            y='PCT_FLUENTES',
            title="Percentual de Leitores Fluentes por Município",
            color='PCT_FLUENTES',
            color_continuous_scale='Viridis'
        )
        
        fig_mun.update_layout(
            xaxis_title="Município",
            yaxis_title="% Leitores Fluentes",
            height=400
        )
        
        st.plotly_chart(fig_mun, use_container_width=True)
    
    # Ranking de alunos
    st.subheader("🏆 Ranking de Alunos por Nível de Leitura")
    
    # Melhor nível por aluno
    ranking_alunos = df_filtrado.groupby(['ALU_ID', 'ALU_NOME', 'ESC_NOME', 'MUN_NOME', 'SER_NOME']).agg({
        'NIVEL_NUMERICO': 'max',
        'NIVEL_LEITURA': lambda x: x.iloc[x.values.argmax()]
    }).reset_index()
    
    ranking_alunos['DESCRICAO_NIVEL'] = ranking_alunos['NIVEL_LEITURA'].apply(get_descricao_nivel_leitura)
    ranking_alunos = ranking_alunos.sort_values(['NIVEL_NUMERICO', 'ALU_NOME'], ascending=[False, True])
    
    # Mostrar top 50
    st.dataframe(
        ranking_alunos.head(50)[['ALU_NOME', 'ESC_NOME', 'MUN_NOME', 'SER_NOME', 'DESCRICAO_NIVEL']].rename(columns={
            'ALU_NOME': 'Nome do Aluno',
            'ESC_NOME': 'Escola',
            'MUN_NOME': 'Município',
            'SER_NOME': 'Série',
            'DESCRICAO_NIVEL': 'Nível de Leitura'
        }),
        use_container_width=True,
        height=400
    )
    
    # Download dos dados
    st.subheader("📥 Download dos Dados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV da distribuição
        csv_distribuicao = distribuicao_completa.to_csv()
        st.download_button(
            label="📊 Download Distribuição por Níveis",
            data=csv_distribuicao,
            file_name=f"distribuicao_leitura_{municipio_selecionado.replace(' ', '_')}.csv",
            mime="text/csv"
        )
    
    with col2:
        # CSV do ranking
        csv_ranking = ranking_alunos.to_csv(index=False)
        st.download_button(
            label="🏆 Download Ranking de Alunos",
            data=csv_ranking,
            file_name=f"ranking_leitura_{municipio_selecionado.replace(' ', '_')}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("🕦 Painel TEC1 - Janela de Serviço do Técnico")
st.write("---")

# Verifica se a base de dados foi previamente carregada na página inicial
if 'dados_rota' in st.session_state:
    df = st.session_state['dados_rota'].copy()
    
    # ==========================================
    # CRIANDO OS FILTROS NA BARRA LATERAL (SIDEBAR)
    # ==========================================
    st.sidebar.header("Filtros de Monitoramento")
    
    # 1. Filtro de Janela de Serviço
    col_janela = 'Janela de Serviço'
    if col_janela in df.columns:
        opcoes_janela = sorted(df[col_janela].dropna().astype(str).unique())
        janela_sel = st.sidebar.selectbox("1. Selecione a Janela:", opcoes_janela)
        df_filtrado = df[df[col_janela] == janela_sel]
    else:
        st.sidebar.error("Coluna 'Janela de Serviço' não encontrada.")
        df_filtrado = df.copy()

    # 2. Filtro de Cidade (Para separar ABC de São Paulo)
    col_cidade = 'Cidade'
    if col_cidade in df.columns:
        opcoes_cidade = ["TODAS"] + sorted(df_filtrado[col_cidade].dropna().astype(str).unique())
        cidade_sel = st.sidebar.selectbox("2. Filtrar por Cidade/Região:", opcoes_cidade)
        if cidade_sel != "TODAS":
            df_filtrado = df_filtrado[df_filtrado[col_cidade] == cidade_sel]

    # 3. Filtro por Supervisor
    col_supervisor = 'SUPERVISOR'
    if col_supervisor in df.columns:
        opcoes_super = ["TODOS"] + sorted(df_filtrado[col_supervisor].dropna().astype(str).unique())
        supervisor_sel = st.sidebar.selectbox("3. Filtrar por Supervisor:", opcoes_super)
        if supervisor_sel != "TODOS":
            df_filtrado = df_filtrado[df_filtrado[col_supervisor] == supervisor_sel]

    # ==========================================
    # BLOCO DE MÉTRICAS RÁPIDAS (TOP CARDS)
    # ==========================================
    col1, col2, col3, col4 = st.columns(4)
    
    total_wos = len(df_filtrado)
    tecnicos_ativos = df_filtrado['Recurso'].nunique() if 'Recurso' in df_filtrado.columns else 0
    
    # Cálculo da soma de pontos da rota (Ponto 1 até Ponto 10)
    colunas_pontos = [f'Ponto {i}' for i in range(1, 11)]
    colunas_existentes = [c for c in colunas_pontos if c in df_filtrado.columns]
    
    if colunas_existentes:
        # Converte para numérico e soma todos os pontos das colunas existentes
        total_pontos = df_filtrado[colunas_existentes].apply(pd.to_numeric, errors='coerce').sum().sum()
    else:
        total_pontos = 0

    col1.metric("Total de Atividades / WO", total_wos)
    col2.metric("Técnicos em Campo", tecnicos_ativos)
    col3.metric("Pontuação Total da Janela", int(total_pontos))
    
    if 'Status da Atividade' in df_filtrado.columns:
        concluidas = len(df_filtrado[df_filtrado['Status da Atividade'].str.upper().str.contains('CONCLU', na=False)])
        col4.metric("Atividades Concluídas", concluidas)
    else:
        col4.metric("Atividades Concluídas", "N/A")

    st.write("---")

    # ==========================================
    # GRÁFICOS OPERACIONAIS
    # ==========================================
    g1, g2 = st.columns(2)

    with g1:
        st.write("### 📈 Carga Operacional por Técnico (Volume de Atividades)")
        if 'Recurso' in df_filtrado.columns:
            carga_tecnico = df_filtrado['Recurso'].value_counts()
            if not carga_tecnico.empty:
                st.bar_chart(carga_tecnico)
            else:
                st.info("Nenhuma atividade para exibir gráfico.")
        else:
            st.error("Coluna 'Recurso' (Técnico) não localizada.")

    with g2:
        st.write("### 📍 Distribuição de Atividades por Bairro")
        if 'Bairro' in df_filtrado.columns:
            carga_bairro = df_filtrado['Bairro'].value_counts().head(10) # Top 10 bairros
            if not carga_bairro.empty:
                st.bar_chart(carga_bairro)
            else:
                st.info("Nenhum dado de bairro disponível.")
        else:
            st.error("Coluna 'Bairro' não localizada.")

    # ==========================================
    # VISUALIZAÇÃO DA TABELA DETALHADA
    # ==========================================
    st.write("---")
    st.write("### 📋 Visão Detalhada das Rotas Filtradas")
    
    # Seleção de colunas essenciais para a TV de monitoramento não ficar poluída
    colunas_visao = ['SUPERVISOR', 'Recurso', 'Cidade', 'Bairro', 'Janela de Serviço', 'Status da Atividade', 'Tipo de Atividade', 'Número da WO']
    colunas_exibir = [c for c in colunas_visao if c in df_filtrado.columns]
    
    st.dataframe(df_filtrado[colunas_exibir], use_container_width=True)

else:
    st.warning("⚠️ Dados não encontrados. Por favor, acesse a página inicial no menu lateral para carregar a planilha 'rota'.")
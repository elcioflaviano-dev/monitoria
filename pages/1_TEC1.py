import streamlit as st
import pandas as pd

# Configura a página para ocupar toda a largura da tela
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Estilização focada no super destaque visual para os PENDENTES
st.markdown("""
    <style>
    /* Remove espaçamentos inúteis do topo do Streamlit */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }
    
    /* Títulos principais colados no topo */
    .title-abc-sp {
        font-size: 26px;
        font-weight: bold;
        color: #111111;
        margin-bottom: 5px;
        margin-top: 0px;
        padding-bottom: 2px;
        border-bottom: 2px solid #eae5da;
    }

    /* Estilo base geral para os blocos de métricas */
    div[data-testid="stMetric"] {
        background-color: #f7f5f0;
        border: 1px solid #eae5da;
        border-radius: 6px;
        padding: 5px !important;
        text-align: center;
    }
    
    /* === SUPER DESTAQUE: CAIXA DOS PENDENTES (1ª métrica de cada card) === */
    div[data-testid="stMetric"]:nth-of-type(3n+1) {
        background-color: #ffcccc !important; /* Fundo vermelho mais vivo e intenso */
        border: 2px solid #ff9999 !important; /* Borda reforçada */
    }
    
    /* Altera o número do PENDENTE para ficar maior e com cor forte de alerta */
    div[data-testid="stMetric"]:nth-of-type(3n+1) div[data-testid="stMetricValue"] div {
        font-size: 34px !important; /* Aumentado de 24px para 34px */
        color: #b30000 !important; /* Vermelho escuro industrial/alerta */
        font-weight: 900 !important;
    }
    
    /* Altera o rótulo "🔴 PENDENTES" para acompanhar o peso visual */
    div[data-testid="stMetric"]:nth-of-type(3n+1) div[data-testid="stMetricLabel"] p {
        color: #800000 !important;
        font-weight: 800 !important;
    }
    
    /* === ESTILO PADRÃO: EM ROTA E INICIADO (Demais métricas) === */
    div[data-testid="stMetricLabel"] p {
        font-size: 10px !important;
        font-weight: bold !important;
        text-transform: uppercase;
        color: #555 !important;
    }
    
    div[data-testid="stMetricValue"] div {
        font-size: 24px !important;
        font-weight: 900 !important;
        color: #333333;
    }
    </style>
""", unsafe_allow_html=True)

if 'dados_rota' in st.session_state:
    df = st.session_state['dados_rota'].copy()
    
    # --- FILTRO DA JANELA GLOBAL (BARRA LATERAL) ---
    st.sidebar.header("Filtros")
    col_janela = 'Janela de Serviço'
    
    if col_janela in df.columns:
        opcoes_janela = sorted(df[col_janela].dropna().astype(str).unique())
        janela_sel = st.sidebar.selectbox("Janela de Serviço:", opcoes_janela)
        df_tela = df[df[col_janela] == janela_sel]
    else:
        st.sidebar.error("Coluna 'Janela de Serviço' não encontrada.")
        df_tela = df.copy()
        janela_sel = "N/A"

    # --- SEPARAÇÃO LÓGICA DOS SUPERVISORES ---
    col_supervisor = 'SUPERVISOR'
    df_abc_lista, df_sp_lista = [], []
    
    if col_supervisor in df_tela.columns:
        for idx, linha in df_tela.iterrows():
            nome_super = str(linha[col_supervisor]).upper()
            if "FRANCISCO" in nome_super or "ALAN" in nome_super:
                df_sp_lista.append(linha)
            else:
                df_abc_lista.append(linha)
                
        df_abc = pd.DataFrame(df_abc_lista) if df_abc_lista else pd.DataFrame(columns=df_tela.columns)
        df_sp = pd.DataFrame(df_sp_lista) if df_sp_lista else pd.DataFrame(columns=df_tela.columns)
    else:
        df_abc, df_sp = pd.DataFrame(), pd.DataFrame()

    # --- CORPO VISUAL (COLUNAS LADO A LADO) ---
    col_coluna_abc, col_coluna_sp = st.columns(2)
    
    # --- COLUNA ESQUERDA: ABC ---
    with col_coluna_abc:
        st.markdown('<div class="title-abc-sp">ABC</div>', unsafe_allow_html=True)
        
        if not df_abc.empty:
            supervisores_abc = df_abc[col_supervisor].dropna().unique()
            for supervisor in sorted(supervisores_abc):
                df_super = df_abc[df_abc[col_supervisor] == supervisor]
                
                pendentes = len(df_super[df_super['Status da Atividade'].str.upper() == 'PENDENTE'])
                em_rota = len(df_super[df_super['Status da Atividade'].str.upper() == 'EM ROTA'])
                iniciados = len(df_super[df_super['Status da Atividade'].str.upper() == 'INICIADO'])
                total = len(df_super)
                
                with st.container(border=True):
                    st.markdown(f"#### **{str(supervisor).upper()}** <span style='float:right; font-size:14px; background-color:#e1f5fe; padding:2px 8px; border-radius:4px; color:#0288d1;'>Total: {total}</span>", unsafe_allow_html=True)
                    
                    m1, m2, m3 = st.columns(3)
                    m1.metric(label="🔴 PENDENTES", value=pendentes)
                    m2.metric(label="🟣 EM ROTA", value=em_rota)
                    m3.metric(label="🟢 INICIADO", value=iniciados)
        else:
            st.info("Nenhum supervisor ativo no ABC nesta janela.")

    # --- COLUNA DIREITA: SP ---
    with col_coluna_sp:
        st.markdown('<div class="title-abc-sp">SP</div>', unsafe_allow_html=True)
        
        if not df_sp.empty:
            supervisores_sp = df_sp[col_supervisor].dropna().unique()
            for supervisor in sorted(supervisores_sp):
                df_super = df_sp[df_sp[col_supervisor] == supervisor]
                
                pendentes = len(df_super[df_super['Status da Atividade'].str.upper() == 'PENDENTE'])
                em_rota = len(df_super[df_super['Status da Atividade'].str.upper() == 'EM ROTA'])
                iniciados = len(df_super[df_super['Status da Atividade'].str.upper() == 'INICIADO'])
                total = len(df_super)
                
                with st.container(border=True):
                    st.markdown(f"#### **{str(supervisor).upper()}** <span style='float:right; font-size:14px; background-color:#e1f5fe; padding:2px 8px; border-radius:4px; color:#0288d1;'>Total: {total}</span>", unsafe_allow_html=True)
                    
                    m1, m2, m3 = st.columns(3)
                    m1.metric(label="🔴 PENDENTES", value=pendentes)
                    m2.metric(label="🟣 EM ROTA", value=em_rota)
                    m3.metric(label="🟢 INICIADO", value=iniciados)
        else:
            st.info("Nenhum supervisor ativo em SP nesta janela.")

else:
    st.warning("⚠️ Dados não encontrados. Acesse a página inicial para carregar a planilha.")

import streamlit as st
import pandas as pd

# Configura a página para ocupar toda a largura
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Mantemos apenas o CSS das molduras e das cores internas das métricas
st.markdown("""
    <style>
    /* Remove barras de rolagem desnecessárias e ajusta margens */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }
    
    /* Moldura grande que envolve o ABC e SP */
    .region-frame {
        border: 2px solid #e6dfd5;
        border-radius: 12px;
        padding: 15px;
        background-color: #ffffff;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.03);
        height: 85vh;
        overflow-y: auto; /* Permite rolagem interna sutil apenas se estourar o monitor */
    }
    
    .region-header {
        font-size: 28px;
        font-weight: 800;
        color: #111111;
        margin-bottom: 12px;
        border-bottom: 2px solid #eae5da;
        padding-bottom: 5px;
    }

    /* Estilização das caixas de métricas */
    .metric-box {
        border-radius: 6px;
        padding: 6px;
        text-align: center;
        font-weight: bold;
        width: 100%;
    }
    .metric-pendente { background-color: #ffe6e6; border: 1px solid #ffcccc; color: #cc0000;}
    .metric-rota { background-color: #f7f5f0; border: 1px solid #eae5da; color: #333;}
    .metric-iniciado { background-color: #f7f5f0; border: 1px solid #eae5da; color: #333;}
    
    .metric-label { font-size: 9px; color: #666; text-transform: uppercase; font-weight: bold; margin-bottom: 2px;}
    .metric-value { font-size: 22px; font-weight: 900; line-height: 1;}
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

    # --- CORPO VISUAL (COLUNAS ESPELHADAS) ---
    col_coluna_abc, col_coluna_sp = st.columns(2)
    
    # --- COLUNA: ABC ---
    with col_coluna_abc:
        # Cria a moldura externa do ABC
        st.markdown('<div class="region-frame">', unsafe_allow_html=True)
        st.markdown('<div class="region-header">ABC</div>', unsafe_allow_html=True)
        
        if not df_abc.empty:
            supervisores_abc = df_abc[col_supervisor].dropna().unique()
            for supervisor in sorted(supervisores_abc):
                df_super = df_abc[df_abc[col_supervisor] == supervisor]
                
                pendentes = len(df_super[df_super['Status da Atividade'].str.upper() == 'PENDENTE'])
                em_rota = len(df_super[df_super['Status da Atividade'].str.upper() == 'EM ROTA'])
                iniciados = len(df_super[df_super['Status da Atividade'].str.upper() == 'INICIADO'])
                total = len(df_super)
                
                # Monta o card usando elementos 100% nativos e limpos do Streamlit
                with st.container(border=True):
                    # Cabeçalho do Card
                    c1, c2, c3 = st.columns([2, 1, 1])
                    c1.markdown(f"### **{str(supervisor).upper()}**")
                    c2.markdown(f"`Janela: {janela_sel}`")
                    c3.markdown(f"<div style='text-align:right; font-weight:bold;'>Total: {total}</div>", unsafe_allow_html=True)
                    
                    # Linha de Métricas Internas (Pendentes, Em Rota, Iniciado)
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.markdown(f'<div class="metric-box metric-pendente"><div class="metric-label">Pendentes</div><div class="metric-value">{pendentes}</div></div>', unsafe_allow_html=True)
                    with m2:
                        st.markdown(f'<div class="metric-box metric-rota"><div class="metric-label">Em Rota</div><div class="metric-value">{em_rota}</div></div>', unsafe_allow_html=True)
                    with m3:
                        st.markdown(f'<div class="metric-box metric-iniciado"><div class="metric-label">Iniciado</div><div class="metric-value">{iniciados}</div></div>', unsafe_allow_html=True)
        else:
            st.info("Nenhum supervisor ativo no ABC nesta janela.")
            
        st.markdown('</div>', unsafe_allow_html=True) # Fecha a moldura do ABC

    # --- COLUNA: SP ---
    with col_coluna_sp:
        # Cria a moldura externa de SP
        st.markdown('<div class="region-frame">', unsafe_allow_html=True)
        st.markdown('<div class="region-header">SP</div>', unsafe_allow_html=True)
        
        if not df_sp.empty:
            supervisores_sp = df_sp[col_supervisor].dropna().unique()
            for supervisor in sorted(supervisores_sp):
                df_super = df_sp[df_sp[col_supervisor] == supervisor]
                
                pendentes = len(df_super[df_super['Status da Atividade'].str.upper() == 'PENDENTE'])
                em_rota = len(df_super[df_super['Status da Atividade'].str.upper() == 'EM ROTA'])
                iniciados = len(df_super[df_super['Status da Atividade'].str.upper() == 'INICIADO'])
                total = len(df_super)
                
                # Monta o card usando elementos 100% nativos e limpos do Streamlit
                with st.container(border=True):
                    c1, c2, c3 = st.columns([2, 1, 1])
                    c1.markdown(f"### **{str(supervisor).upper()}**")
                    c2.markdown(f"`Janela: {janela_sel}`")
                    c3.markdown(f"<div style='text-align:right; font-weight:bold;'>Total: {total}</div>", unsafe_allow_html=True)
                    
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.markdown(f'<div class="metric-box metric-pendente"><div class="metric-label">Pendentes</div><div class="metric-value">{pendentes}</div></div>', unsafe_allow_html=True)
                    with m2:
                        st

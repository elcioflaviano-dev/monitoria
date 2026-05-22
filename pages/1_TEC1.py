import streamlit as st
import pandas as pd

# Configura a página para ocupar toda a largura da tela
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Estilização apenas para as molduras das colunas do ABC e SP (deixando-as fixas)
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }
    .region-frame {
        border: 2px solid #e6dfd5;
        border-radius: 12px;
        padding: 15px;
        background-color: #ffffff;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.03);
        height: 85vh;
        overflow-y: auto;
    }
    .region-header {
        font-size: 28px;
        font-weight: 800;
        color: #111111;
        margin-bottom: 12px;
        border-bottom: 2px solid #eae5da;
        padding-bottom: 5px;
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

    # --- CORPO VISUAL (COLUNAS ESPELHADAS NATIIVAS) ---
    col_coluna_abc, col_coluna_sp = st.columns(2)
    
    # --- COLUNA MESTRE: ABC ---
    with col_coluna_abc:
        st.markdown('<div class="region-frame">', unsafe_allow_html=True)
        st.markdown('<div class="region-header">ABC</div>', unsafe_allow_html=True)
        
        if not df_abc.empty:
            supervisores_abc = df_abc[col_supervisor].dropna().unique()
            for supervisor in sorted(supervisores_abc):
                df_super = df_abc[df_abc[col_supervisor] == supervisor]
                
                # Contagem dos status filtrados
                pendentes = len(df_super[df_super['Status da Atividade'].str.upper() == 'PENDENTE'])
                em_rota = len(df_super[df_super['Status da Atividade'].str.upper() == 'EM ROTA'])
                iniciados = len(df_super[df_super['Status da Atividade'].str.upper() == 'INICIADO'])
                total = len(df_super)
                
                # Criando o Card Nativo sem HTML interno para não quebrar a indentação
                with st.container(border=True):
                    # Título do supervisor e totalizadores
                    st.markdown(f"### **{str(supervisor).upper()}** — `Total: {total}`")
                    
                    # Linha com as 3 métricas coloridas automaticamente pelo Streamlit
                    m1, m2, m3 = st.columns(3)
                    m1.metric(label="🔴 PENDENTES", value=pendentes)
                    m2.metric(label="⚪ EM ROTA", value=em_rota)
                    m3.metric(label="🟢 INICIADO", value=iniciados)
        else:
            st.info("Nenhum supervisor ativo no ABC nesta janela.")
            
        st.markdown('</div>', unsafe_allow_html=True)

    # --- COLUNA MESTRE: SP ---
    with col_coluna_sp:
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
                
                with st.container(border=True):
                    st.markdown(f"### **{str(supervisor).upper()}** — `Total: {total}`")
                    
                    m1, m2, m3 = st.columns(3)
                    m1.metric(label="🔴 PENDENTES", value=pendentes)
                    m2.metric(label="⚪ EM ROTA", value=em_rota)
                    m3.metric(label="🟢 INICIADO", value=iniciados)
        else:
            st.info("Nenhum supervisor ativo em SP nesta janela.")
            
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.warning("⚠️ Dados não encontrados. Acesse a página inicial para carregar a planilha.")

import streamlit as st
import pandas as pd

# Configura a página para ocupar toda a largura da tela
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# MÁGICA: Abre e injeta o arquivo style.css externo no Streamlit
with open("style.css", "r") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# === AQUI ENTRA O SEU NOVO TÍTULO PRINCIPAL ===
st.markdown('<div class="main-dashboard-title">TEC1</div>', unsafe_allow_html=True)

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
        for idx, Server_linha in df_tela.iterrows():
            nome_super = str(Server_linha[col_supervisor]).upper()
            if "FRANCISCO" in nome_super or "ALAN" in nome_super:
                df_sp_lista.append(Server_linha)
            else:
                df_abc_lista.append(Server_linha)
                
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
                    with m1:
                        st.markdown(f"""
                            <div class="custom-pendente-box">
                                <div class="custom-pendente-label">🔴 PENDENTES</div>
                                <div class="custom-pendente-value">{pendentes}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    with m2:
                        st.metric(label="🟣 EM ROTA", value=em_rota)
                    with m3:
                        st.metric(label="🟢 INICIADO", value=iniciados)
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
                    with m1:
                        st.markdown(f"""
                            <div class="custom-pendente-box">
                                <div class="custom-pendente-label">🔴 PENDENTES</div>
                                <div class="custom-pendente-value">{pendentes}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    with m2:
                        st.metric(label="🟣 EM ROTA", value=em_rota)
                    with m3:
                        st.metric(label="🟢 INICIADO", value=iniciados)
        else:
            st.info("Nenhum supervisor ativo em SP nesta janela.")

else:
    st.warning("⚠️ Dados não encontrados. Acesse a página inicial para carregar a planilha.")

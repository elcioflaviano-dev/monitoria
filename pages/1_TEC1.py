import streamlit as st
import pandas as pd

# Configura a página para ocupar toda a largura e remove margens padrão do Streamlit
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# CSS Avançado para travar a rolagem e criar as molduras integradas
st.markdown("""
    <style>
    /* Remove scrollers e margens excessivas da tela principal */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }
    
    /* Molduras Principais das Regiões (ABC e SP) */
    .region-frame {
        border: 2px solid #d1c7bd;
        border-radius: 12px;
        padding: 12px;
        background-color: #ffffff;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.05);
        height: 82vh; /* Trava a altura em 82% da altura da tela do monitor */
        overflow: hidden;
    }
    
    .region-header {
        font-size: 26px;
        font-weight: 800;
        color: #111111;
        margin-bottom: 10px;
        border-bottom: 2px solid #eae5da;
        padding-bottom: 5px;
    }
    
    /* Cards dos Supervisores (Super Compactos) */
    .supervisor-card {
        border: 1px solid #e6dfd5;
        border-radius: 8px;
        padding: 8px 12px;
        margin-bottom: 10px;
        background-color: #fcfbfa;
    }
    
    .super-title {
        font-size: 15px;
        font-weight: bold;
        color: #006677;
        display: inline-block;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 55%;
    }
    
    .badge-janela {
        background-color: #f0ebe6;
        border-radius: 12px;
        padding: 1px 8px;
        font-size: 11px;
        font-weight: bold;
        margin-left: 6px;
        border: 1px solid #eae5da;
    }
    
    .total-badge {
        float: right;
        font-size: 12px;
        font-weight: bold;
        color: #444;
        background: #eae5da;
        padding: 1px 6px;
        border-radius: 4px;
    }
    
    /* Sub-Métricas (Boxes de Status) */
    .metric-row {
        display: flex;
        gap: 6px;
        margin-top: 6px;
    }
    
    .metric-box {
        flex: 1;
        border-radius: 5px;
        padding: 4px;
        text-align: center;
    }
    
    .metric-pendente { background-color: #ffe6e6; border: 1px solid #ffcccc; color: #cc0000;}
    .metric-rota { background-color: #f7f5f0; border: 1px solid #eae5da; color: #333;}
    .metric-iniciado { background-color: #f7f5f0; border: 1px solid #eae5da; color: #333;}
    
    .metric-label { font-size: 9px; color: #666; text-transform: uppercase; font-weight: bold;}
    .metric-value { font-size: 20px; font-weight: 900; line-height: 1.1;}
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

    # --- SEPARAÇÃO LOGICA DOS SUPERVISORES ---
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

    # --- ESTRUTURA VISUAL DA TELA SEM ROLAGEM ---
    # Dividindo o espaço em duas grandes colunas na proporção 50/50
    col_coluna_abc, col_coluna_sp = st.columns(2)
    
    # --- MOLDURA MESTRE: ABC ---
    with col_coluna_abc:
        # Iniciando a moldura integrada via HTML
        html_abc = f'<div class="region-frame"><div class="region-header">ABC</div>'
        
        if not df_abc.empty:
            supervisores_abc = df_abc[col_supervisor].dropna().unique()
            for supervisor in sorted(supervisores_abc):
                df_super = df_abc[df_abc[col_supervisor] == supervisor]
                
                pendentes = len(df_super[df_super['Status da Atividade'].str.upper() == 'PENDENTE'])
                em_rota = len(df_super[df_super['Status da Atividade'].str.upper() == 'EM ROTA'])
                iniciados = len(df_super[df_super['Status da Atividade'].str.upper() == 'INICIADO'])
                total = len(df_super)
                
                # Injeta cada card de supervisor compacto dentro da moldura ABC
                html_abc += f"""
                    <div class="supervisor-card">
                        <div>
                            <span class="super-title">{str(supervisor).upper()}</span>
                            <span class="badge-janela">Janela: {janela_sel}</span>
                            <span class="total-badge">Total: {total}</span>
                        </div>
                        <div class="metric-row">
                            <div class="metric-box metric-pendente"><div class="metric-label">Pendentes</div><div class="metric-value">{pendentes}</div></div>
                            <div class="metric-box metric-rota"><div class="metric-label">Em Rota</div><div class="metric-value">{em_rota}</div></div>
                            <div class="metric-box metric-iniciado"><div class="metric-label">Iniciado</div><div class="metric-value">{iniciados}</div></div>
                        </div>
                    </div>
                """
        else:
            html_abc += '<p style="color:#666; font-size:14px;">Nenhum supervisor ativo nesta janela.</p>'
            
        html_abc += '</div>' # Fechando a moldura mestre
        st.markdown(html_abc, unsafe_allow_html=True)

    # --- MOLDURA MESTRE: SP ---
    with col_coluna_sp:
        html_sp = f'<div class="region-frame"><div class="region-header">SP</div>'
        
        if not df_sp.empty:
            supervisores_sp = df_sp[col_supervisor].dropna().unique()
            for supervisor in sorted(supervisores_sp):
                df_super = df_sp[df_sp[col_supervisor] == supervisor]
                
                pendentes = len(df_super[df_super['Status da Atividade'].str.upper() == 'PENDENTE'])
                em_rota = len(df_super[df_super['Status da Atividade'].str.upper() == 'EM ROTA'])
                iniciados = len(df_super[df_super['Status da Atividade'].str.upper() == 'INICIADO'])
                total = len(df_super)
                
                # Injeta cada card de supervisor compacto dentro da moldura SP
                html_sp += f"""
                    <div class="supervisor-card">
                        <div>
                            <span class="super-title">{str(supervisor).upper()}</span>
                            <span class="badge-janela">Janela: {janela_sel}</span>
                            <span class="total-badge">Total: {total}</span>
                        </div>
                        <div class="metric-row">
                            <div class="metric-box metric-pendente"><div class="metric-label">Pendentes</div><div class="metric-value">{pendentes}</div></div>
                            <div class="metric-box metric-rota"><div class="metric-label">Em Rota</div><div class="metric-value">{em_rota}</div></div>
                            <div class="metric-box metric-iniciado"><div class="metric-label">Iniciado</div><div class="metric-value">{iniciados}</div></div>
                        </div>
                    </div>
                """
        else:
            html_sp += '<p style="color:#666; font-size:14px;">Nenhum supervisor ativo nesta janela.</p>'
            
        html_sp += '</div>' # Fechando a moldura mestre
        st.markdown(html_sp, unsafe_allow_html=True)

else:
    st.warning("⚠️ Dados não encontrados. Acesse a página inicial para carregar a planilha.")

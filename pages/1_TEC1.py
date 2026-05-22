import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# Customização via CSS para criar os cards idênticos aos da imagem (Bordas arredondadas e destaques)
st.markdown("""
    <style>
    .supervisor-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        background-color: #fcfbfa;
    }
    .super-title {
        font-size: 20px;
        font-weight: bold;
        color: #006677;
        display: inline-block;
    }
    .badge-janela {
        background-color: #f0ebe6;
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 12px;
        font-weight: bold;
        margin-left: 10px;
        border: 1px solid #ddd;
    }
    .total-badge {
        float: right;
        font-size: 13px;
        font-weight: bold;
        color: #333;
    }
    .metric-box {
        border-radius: 6px;
        padding: 8px;
        text-align: center;
        font-weight: bold;
    }
    .metric-pendente { background-color: #ffe6e6; border: 1px solid #ffcccc; color: #cc0000;}
    .metric-rota { background-color: #f7f5f0; border: 1px solid #eae5da; color: #333;}
    .metric-iniciado { background-color: #f7f5f0; border: 1px solid #eae5da; color: #333;}
    .metric-label { font-size: 10px; color: #666; text-transform: uppercase; margin-bottom: 2px;}
    .metric-value { font-size: 28px; font-weight: 900;}
    .region-header { font-size: 32px; font-weight: bold; color: #111; margin-bottom: 15px;}
    </style>
""", unsafe_allow_html=True)

if 'dados_rota' in st.session_state:
    df = st.session_state['dados_rota'].copy()
    
    # --- FILTRO DA JANELA GLOBAL (BARRA LATERAL) ---
    st.sidebar.header("Configuração da Tela")
    col_janela = 'Janela de Serviço'
    
    if col_janela in df.columns:
        opcoes_janela = sorted(df[col_janela].dropna().astype(str).unique())
        janela_sel = st.sidebar.selectbox("Filtrar Janela de Serviço ativa:", opcoes_janela)
        # Filtra os dados da tela para a janela escolhida
        df_tela = df[df[col_janela] == janela_sel]
    else:
        st.sidebar.error("Coluna 'Janela de Serviço' não encontrada.")
        df_tela = df.copy()
        janela_sel = "N/A"

    # --- DIVISÃO DA TELA EM ABC E SÃO PAULO ---
    col_abc, col_sp = st.columns(2)
    
    # Mapeamento lógico de Cidades para cada Região
    # Ajuste os nomes das cidades de acordo com o que está escrito exatamente na sua planilha
    cidades_abc = ['SÃO BERNARDO DO CAMPO', 'SANTO ANDRÉ', 'SÃO CAETANO DO SUL', 'DIADEMA', 'MAUÁ', 'RIBEIRÃO PIRES']
    
    with col_abc:
        st.markdown('<div class="region-header">ABC</div>', unsafe_allow_html=True)
        
        # Filtra dados pertencentes ao ABC
        if 'Cidade' in df_tela.columns:
            df_abc = df_tela[df_tela['Cidade'].str.upper().isin(cidades_abc)]
        else:
            df_abc = pd.DataFrame()
            
        if 'SUPERVISOR' in df_abc.columns and not df_abc.empty:
            supervisores_abc = df_abc['SUPERVISOR'].dropna().unique()
            
            for supervisor in supervisores_abc:
                df_super = df_abc[df_abc['SUPERVISOR'] == supervisor]
                
                # Separação dos status com base na coluna 'Status da Atividade'
                # IMPORTANTE: Ajuste os termos 'Pendente', 'Em rota' e 'Iniciado' para bater com a sua planilha
                pendentes = len(df_super[df_super['Status da Atividade'].str.upper() == 'PENDENTE'])
                em_rota = len(df_super[df_super['Status da Atividade'].str.upper() == 'EM ROTA'])
                iniciados = len(df_super[df_super['Status da Atividade'].str.upper() == 'INICIADO'])
                total = len(df_super)
                
                # Montagem do Card do Supervisor usando HTML estilizado para ficar igual à foto
                st.markdown(f"""
                    <div class="supervisor-card">
                        <div>
                            <span class="super-title">{str(supervisor).upper()}</span>
                            <span class="badge-janela">Janela: {janela_sel}</span>
                            <span class="total-badge">Total: {total}</span>
                        </div>
                        <div style="margin-top:12px;">
                """, unsafe_allow_html=True)
                
                # Colunas internas para as sub-métricas
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.markdown(f'<div class="metric-box metric-pendente"><div class="metric-label">Pendentes</div><div class="metric-value">{pendentes}</div></div>', unsafe_allow_html=True)
                with m2:
                    st.markdown(f'<div class="metric-box metric-rota"><div class="metric-label">Em Rota</div><div class="metric-value">{em_rota}</div></div>', unsafe_allow_html=True)
                with m3:
                    st.markdown(f'<div class="metric-box metric-iniciado"><div class="metric-label">Iniciado</div><div class="metric-value">{iniciados}</div></div>', unsafe_allow_html=True)
                
                st.markdown("</div></div>", unsafe_allow_html=True)
        else:
            st.info("Nenhum supervisor com rota ativa no ABC para esta janela.")

    with col_sp:
        st.markdown('<div class="region-header">SP</div>', unsafe_allow_html=True)
        
        # Filtra dados que NÃO pertencem ao ABC (portanto, pertencem a São Paulo / Capital)
        if 'Cidade' in df_tela.columns:
            df_sp = df_tela[~df_tela['Cidade'].str.upper().isin(cidades_abc)]
        else:
            df_sp = pd.DataFrame()
            
        if 'SUPERVISOR' in df_sp.columns and not df_sp.empty:
            supervisores_sp = df_sp['SUPERVISOR'].dropna().unique()
            
            for supervisor in sorted(supervisores_sp):
                df_super = df_sp[df_sp['SUPERVISOR'] == supervisor]
                
                pendentes = len(df_super[df_super['Status da Atividade'].str.upper() == 'PENDENTE'])
                em_rota = len(df_super[df_super['Status da Atividade'].str.upper() == 'EM ROTA'])
                iniciados = len(df_super[df_super['Status da Atividade'].str.upper() == 'INICIADO'])
                total = len(df_super)
                
                st.markdown(f"""
                    <div class="supervisor-card">
                        <div>
                            <span class="super-title">{str(supervisor).upper()}</span>
                            <span class="badge-janela">Janela: {janela_sel}</span>
                            <span class="total-badge">Total: {total}</span>
                        </div>
                        <div style="margin-top:12px;">
                """, unsafe_allow_html=True)
                
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.markdown(f'<div class="metric-box metric-pendente"><div class="metric-label">Pendentes</div><div class="metric-value">{pendentes}</div></div>', unsafe_allow_html=True)
                with m2:
                    st.markdown(f'<div class="metric-box metric-rota"><div class="metric-label">Em Rota</div><div class="metric-value">{em_rota}</div></div>', unsafe_allow_html=True)
                with m3:
                    st.markdown(f'<div class="metric-box metric-iniciado"><div class="metric-label">Iniciado</div><div class="metric-value">{iniciados}</div></div>', unsafe_allow_html=True)
                
                st.markdown("</div></div>", unsafe_allow_html=True)
        else:
            st.info("Nenhum supervisor com rota ativa em SP para esta janela.")

else:
    st.warning("⚠️ Dados não encontrados. Por favor, acesse a página inicial no menu lateral.")

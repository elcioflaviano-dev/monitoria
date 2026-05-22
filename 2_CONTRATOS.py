import streamlit as st
import pandas as pd
import time

# 1. Configuração da página
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 2. Carregar CSS externo
try:
    with open("style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass

# 3. CSS Extra para tabelas internas compactas
st.markdown("""
    <style>
    .compact-table {
        font-size: 11px !important;
        width: 100%;
        border-collapse: collapse;
    }
    .compact-table th { background-color: #f0ebe6; text-align: left; padding: 4px; }
    .compact-table td { border-bottom: 1px solid #eee; padding: 3px; }
    .status-badge { padding: 2px 5px; border-radius: 4px; font-weight: bold; font-size: 10px; }
    .status-pendente { background-color: #ffcccc; color: #b30000; }
    .status-rota { background-color: #e1f5fe; color: #0288d1; }
    .status-iniciado { background-color: #e8f5e9; color: #2e7d32; }
    </style>
""", unsafe_allow_html=True)

# 4. Título Centralizado
st.markdown('<h1 style="font-size: 38px; font-weight: 900; color: #006677; text-align: center; margin-top: 20px;">TEC1 - CONTRATOS</h1>', unsafe_allow_html=True)

# --- MÓDULO DE ALTERNÂNCIA AUTOMÁTICA (MODO TV) ---
# Este script espera 30 segundos e clica no link da próxima página no menu lateral
st.components.v1.html("""
    <script>
    window.parent.document.querySelectorAll('section[data-testid="stSidebarNav"] li')[0].querySelector('a').click();
    </script>
""", height=0)
# Nota: O índice [0] volta para a primeira página. No 1_TEC1.py usaremos índice [1] para vir para cá.

if 'dados_rota' in st.session_state:
    df = st.session_state['dados_rota'].copy()
    
    # Filtro de Janela
    col_janela = 'Janela de Serviço'
    if col_janela in df.columns:
        opcoes_janela = sorted(df[col_janela].dropna().astype(str).unique())
        janela_sel = st.sidebar.selectbox("Janela:", opcoes_janela)
        df_tela = df[df[col_janela] == janela_sel]
    else:
        df_tela = df.copy()
        janela_sel = "N/A"

    # Lógica de Separação (Igual ao TEC1)
    col_supervisor = 'SUPERVISOR'
    df_abc_lista, df_sp_lista = [], []
    for _, linha in df_tela.iterrows():
        nome_super = str(linha[col_supervisor]).upper()
        if "FRANCISCO" in nome_super or "ALAN" in nome_super:
            df_sp_lista.append(linha)
        else:
            df_abc_lista.append(linha)
            
    df_abc = pd.DataFrame(df_abc_lista) if df_abc_lista else pd.DataFrame(columns=df_tela.columns)
    df_sp = pd.DataFrame(df_sp_lista) if df_sp_lista else pd.DataFrame(columns=df_tela.columns)

    # Função para renderizar a lista priorizada
    def render_lista_priorizada(df_input):
        if df_input.empty:
            st.info("Sem atividades.")
            return

        supervisores = sorted(df_input[col_supervisor].dropna().unique())
        for super_nome in supervisores:
            df_super = df_input[df_input[col_supervisor] == super_nome].copy()
            
            # ORDEM DE PRIORIDADE: Pendente (1), Rota (2), Iniciado (3)
            prioridade = {'PENDENTE': 1, 'EM ROTA': 2, 'INICIADO': 3}
            df_super['ordem'] = df_super['Status da Atividade'].str.upper().map(prioridade).fillna(4)
            df_super = df_super.sort_values('ordem')

            with st.container(border=True):
                st.markdown(f"##### **{super_nome.upper()}**")
                
                # Criando a tabelinha compacta para a TV
                html_table = '<table class="compact-table"><tr><th>TÉCNICO</th><th>CONTRATO</th><th>STATUS</th></tr>'
                for _, r in df_super.iterrows():
                    status = str(r['Status da Atividade']).upper()
                    cor_classe = "status-pendente" if "PENDENTE" in status else ("status-rota" if "ROTA" in status else "status-iniciado")
                    
                    html_table += f"""
                        <tr>
                            <td>{str(r['Recurso'])[:20]}</td>
                            <td>{r['Contrato']}</td>
                            <td><span class="status-badge {cor_classe}">{status}</span></td>
                        </tr>
                    """
                html_table += '</table>'
                st.markdown(html_table, unsafe_allow_html=True)

    # Layout Colunas
    c_abc, c_sp = st.columns(2)
    with c_abc:
        st.markdown('<div class="title-abc-sp">ABC</div>', unsafe_allow_html=True)
        render_lista_priorizada(df_abc)
    with c_sp:
        st.markdown('<div class="title-abc-sp">SP</div>', unsafe_allow_html=True)
        render_lista_priorizada(df_sp)
else:
    st.warning("Aguardando carga de dados...")

# MODO TV: Volta para a página 1 após 30 segundos
st.components.v1.html("""
    <script>
    setTimeout(function(){
        window.parent.document.querySelectorAll('section[data-testid="stSidebarNav"] li')[0].querySelector('a').click();
    }, 30000);
    </script>
""", height=0)

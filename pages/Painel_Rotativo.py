import streamlit as st
import pandas as pd
import os
import time
import base64
from datetime import datetime, timedelta

# Configurações iniciais
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Funções de suporte
def carregar_logo_html(caminho):
    if os.path.exists(caminho):
        try:
            with open(caminho, "rb") as f:
                encoded = base64.b64encode(f.read()).decode('utf-8')
            return f'<img src="data:image/png;base64,{encoded}" style="height: 60px;">'
        except: return '<div></div>'
    return '<div></div>'

# CSS Global
st.markdown("""
    <style>
    [data-testid="stHeader"], .stDeployButton, footer, #MainMenu, [data-testid="stSidebar"] { visibility: hidden !important; }
    .stApp { background-color: #ffffff !important; }
    .topo-container { background: #003366; color: white; padding: 10px 30px; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; border-radius: 0 0 15px 15px; margin-bottom: 20px; }
    
    .super-bar { background-color: #f0f2f6; padding: 10px; border-radius: 6px; margin-bottom: 10px; border-left: 6px solid #008080; display: flex; justify-content: space-between; align-items: center; }
    .super-bar.sp { border-left: 6px solid #b30000; }
    .box-num { font-size: 24px; font-weight: 900; color: #cc6600; }
    .falta-box { background-color: #fff5f5; border: 1px solid #ffcdd2; border-radius: 4px; padding: 5px; text-align: center; width: 30%; }
    </style>
""", unsafe_allow_html=True)

# Lógica de estados e transição
if "idx" not in st.session_state: 
    st.session_state.idx = 4 # Começa na tela branca
    st.session_state.last_time = time.time()

# Gerenciador de Tempo e Telas
esperas = {0: 30, 1: 30, 2: 30, 3: 30, 4: 1} # 1s de tela branca é suficiente para limpar o buffer da TV
if time.time() - st.session_state.last_time > esperas.get(st.session_state.idx, 10):
    # Ciclo: 4 -> 0 -> 4 -> 1 -> 4 -> 3 -> 4 -> 2 (Repete)
    fluxo = {4: 0, 0: 4, 4: 1, 1: 4, 4: 3, 3: 4, 4: 2, 2: 4}
    st.session_state.idx = fluxo.get(st.session_state.idx, 0)
    st.session_state.last_time = time.time()
    st.rerun()

# --- RENDERIZAÇÃO DAS TELAS ---

if st.session_state.idx == 4:
    # TELA BRANCA (LIMPEZA)
    st.markdown('<div style="height: 100vh; background-color: white;"></div>', unsafe_allow_html=True)

else:
    # Cabeçalho Padrão
    st.markdown('<div class="topo-container"><div></div><div style="font-size:30px; font-weight:bold;">PAINEL OPERACIONAL</div><div></div></div>', unsafe_allow_html=True)

    if st.session_state.idx == 3: # TELA INDICADORES (NR35/CERT/BST)
        st.markdown('<h2 style="text-align:center;">📊 INDICADORES POR SUPERVISOR</h2>', unsafe_allow_html=True)
        df_ind = pd.read_csv(os.path.join(os.getcwd(), "indicadores_data.csv")) if os.path.exists("indicadores_data.csv") else pd.DataFrame()
        
        if not df_ind.empty:
            c1, c2 = st.columns(2)
            for base, col in [("ABC", c1), ("SP", c2)]:
                with col:
                    st.markdown(f"### {base}")
                    df_base = df_ind[df_ind["BASE"] == base]
                    for sup in df_base["SUPERVISOR"].unique():
                        df_sup = df_base[df_base["SUPERVISOR"] == sup]
                        # Soma as faltas (exemplo de lógica)
                        f_nr = df_sup[df_sup["INDICADOR"]=="NR35"]["VALOR"].sum()
                        f_ct = df_sup[df_sup["INDICADOR"]=="Certidão"]["VALOR"].sum()
                        f_bt = df_sup[df_sup["INDICADOR"]=="BST"]["VALOR"].sum()
                        
                        st.markdown(f'''
                            <div class="super-bar {'sp' if base=='SP' else ''}">
                                <b>{sup}</b>
                                <div style="display:flex; gap:10px; width:60%;">
                                    <div class="falta-box"><div style="font-size:10px">NR35</div><div class="box-num">{int(f_nr)}</div></div>
                                    <div class="falta-box"><div style="font-size:10px">CERT</div><div class="box-num">{int(f_ct)}</div></div>
                                    <div class="falta-box"><div style="font-size:10px">BST</div><div class="box-num">{int(f_bt)}</div></div>
                                </div>
                            </div>
                        ''', unsafe_allow_html=True)
        else: st.info("Sem dados de indicadores.")

    # ... Adicione aqui as outras telas (idx 0, 1, 2) usando a mesma lógica de st.markdown ...

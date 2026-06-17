import streamlit as st
import pandas as pd
import os
import time
import base64
from datetime import datetime, timedelta

# 1. CONFIGURAÇÕES
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
ROOT_DIR = os.getcwd()
ARQUIVO_ROTA_DISCO = os.path.join(ROOT_DIR, "rota_sincronizada.csv")
ARQUIVO_LOGO = os.path.join(ROOT_DIR, "logo.png")
if not os.path.exists(ARQUIVO_LOGO): ARQUIVO_LOGO = os.path.join(ROOT_DIR, "pages", "logo.png")

# 2. DEFINIÇÃO DA LOGO (RESOLVE O NAME ERROR)
def carregar_logo_html(caminho):
    if os.path.exists(caminho):
        with open(caminho, "rb") as f:
            enc = base64.b64encode(f.read()).decode('utf-8')
        return f'<img src="data:image/png;base64,{enc}" style="height: 60px;">'
    return '<div></div>'
logo_html = carregar_logo_html(ARQUIVO_LOGO)

# 3. CSS "CAMISA DE FORÇA"
st.markdown("""<style>
    [data-testid="stHeader"], footer, #MainMenu, [data-testid="stSidebar"] { visibility: hidden !important; }
    .stApp { background-color: #ffffff !important; }
    .topo-container { background: #003366; color: white; padding: 20px; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; border-radius: 0 0 15px 15px; }
    .topo-centro { font-size: 35px; font-weight: 900; text-align: center; }
</style>""", unsafe_allow_html=True)

# 4. MÁQUINA DE ESTADOS (CICLO 0 -> 1 -> 2 -> 0)
if "idx" not in st.session_state: 
    st.session_state.idx = 0
    st.session_state.last_time = time.time()

# Tempos (0=Base, 1=Pendentes, 2=Relógio)
esperas = {0: 45, 1: 45, 2: 30}

if time.time() - st.session_state.last_time > esperas.get(st.session_state.idx, 30):
    fluxo = {0: 1, 1: 2, 2: 0}
    st.session_state.idx = fluxo.get(st.session_state.idx, 0)
    st.session_state.last_time = time.time()
    st.rerun()

# 5. RENDERIZAÇÃO DAS TELAS
if st.session_state.idx == 0:
    st.markdown(f'<div class="topo-container"><div class="topo-esquerda">{logo_html}</div><div class="topo-centro">🚀 TÉCNICOS EM BASE</div></div>', unsafe_allow_html=True)
    # [COLE AQUI O CÓDIGO DA TELA 0]

elif st.session_state.idx == 1:
    st.markdown(f'<div class="topo-container"><div class="topo-esquerda">{logo_html}</div><div class="topo-centro">CONTRATOS PENDENTES</div></div>', unsafe_allow_html=True)
    # [COLE AQUI O CÓDIGO DA TELA 1]

elif st.session_state.idx == 2:
    st.markdown(f'<div class="topo-container"><div class="topo-esquerda">{logo_html}</div><div class="topo-centro">HORÁRIO</div></div>', unsafe_allow_html=True)
    st.markdown(f'''<div style="text-align:center; padding-top:100px;">
        <div style="font-size:180px; font-weight:900; color:#003366;">{datetime.now().strftime("%H:%M:%S")}</div>
    </div>''', unsafe_allow_html=True)

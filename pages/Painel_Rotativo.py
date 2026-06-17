import streamlit as st
import pandas as pd
import os
import time
import base64
from datetime import datetime, timedelta

# --- CONFIGURAÇÕES BÁSICAS ---
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# CSS "CAMISA DE FORÇA" (NÃO ALTERAR)
st.markdown("""<style>
    [data-testid="stHeader"], .stDeployButton, footer, #MainMenu, [data-testid="stSidebar"] { visibility: hidden !important; }
    .stApp { background-color: #ffffff !important; }
    .topo-container { background: #003366; color: white; padding: 10px 30px; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; border-radius: 0 0 15px 15px; margin-bottom: 20px; }
    .topo-centro { font-size: 35px; font-weight: 900; text-align: center; }
    .botao-home { color: #fff; border: 1px solid #fff; padding: 5px 10px; border-radius: 5px; text-decoration: none; }
</style>""", unsafe_allow_html=True)

# --- FUNÇÕES ---
def carregar_logo_html(caminho):
    if os.path.exists(caminho):
        with open(caminho, "rb") as f:
            enc = base64.b64encode(f.read()).decode('utf-8')
        return f'<img src="data:image/png;base64,{enc}" style="height: 60px;">'
    return '<div></div>'

logo_html = carregar_logo_html(os.path.join(os.getcwd(), "logo.png"))

# --- MÁQUINA DE ROTAÇÃO ---
if "idx" not in st.session_state: 
    st.session_state.idx = 0
    st.session_state.last_time = time.time()

# Tempos: Tela 0 (Base)=45s, Tela 1 (Pendentes)=45s, Tela 2 (Relógio)=30s
esperas = {0: 45, 1: 45, 2: 30}

if time.time() - st.session_state.last_time > esperas.get(st.session_state.idx, 30):
    # Ciclo limpo: 0 -> 1 -> 2 -> 0
    prox = {0: 1, 1: 2, 2: 0}
    st.session_state.idx = prox.get(st.session_state.idx, 0)
    st.session_state.last_time = time.time()
    st.rerun()

# --- RENDERIZAÇÃO DAS TELAS ---
if st.session_state.idx == 0:
    st.markdown(f'<div class="topo-container"><div class="topo-esquerda">{logo_html}</div><div class="topo-centro">🚀 TÉCNICOS EM BASE</div><div class="topo-direita"><a href="/" class="botao-home">HOME</a></div></div>', unsafe_allow_html=True)
    # [COLE AQUI APENAS O CÓDIGO DA SUA TELA 0 - REMOVA IDENTAÇÃO EXTRA]

elif st.session_state.idx == 1:
    st.markdown(f'<div class="topo-container"><div class="topo-esquerda">{logo_html}</div><div class="topo-centro">CONTRATOS PENDENTES</div><div class="topo-direita"><a href="/" class="botao-home">HOME</a></div></div>', unsafe_allow_html=True)
    # [COLE AQUI APENAS O CÓDIGO DA SUA TELA 1 - REMOVA IDENTAÇÃO EXTRA]

elif st.session_state.idx == 2:
    st.markdown(f'''<div style="text-align:center; padding-top:100px;">
        <div style="font-size:180px; font-weight:900; color:#003366;">{datetime.now().strftime("%H:%M:%S")}</div>
        <div style="font-size:40px; color:#666;">{datetime.now().strftime("%d/%m/%Y")}</div>
    </div>''', unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import os
import time
import base64
from datetime import datetime, timedelta

# 1. CONFIGURAÇÕES E DEFINIÇÃO DA LOGO (RESOLVE O NAME ERROR)
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

def carregar_logo_html(caminho_imagem):
    if os.path.exists(caminho_imagem):
        try:
            with open(caminho_imagem, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f'<img src="data:image/png;base64,{encoded_string}" style="height: 60px; width: auto; display: block;">'
        except: return '<div></div>'
    return '<div></div>'

# Tenta carregar a logo da raiz ou da pasta pages
ARQUIVO_LOGO = os.path.join(os.getcwd(), "logo.png")
if not os.path.exists(ARQUIVO_LOGO):
    ARQUIVO_LOGO = os.path.join(os.getcwd(), "pages", "logo.png")

logo_html = carregar_logo_html(ARQUIVO_LOGO) # DEFINIÇÃO DA VARIÁVEL AQUI

# 2. CSS DE ESTILO
st.markdown("""<style>
    [data-testid="stHeader"] { visibility: hidden !important; }
    .stApp { background-color: #ffffff !important; }
    .topo-container { background: #003366; color: white; padding: 15px 30px; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; border-radius: 0 0 15px 15px; margin-bottom: 20px; }
    .topo-centro { font-size: 35px; font-weight: 900; text-align: center; }
    .botao-home { color: #fff; font-size: 14px; font-weight: bold; border: 1px solid #fff; padding: 5px 10px; border-radius: 5px; text-decoration: none; }
</style>""", unsafe_allow_html=True)

# 3. MÁQUINA DE ROTAÇÃO (CICLO: 0 -> 1 -> 2 -> 0)
if "idx" not in st.session_state: 
    st.session_state.idx = 0
    st.session_state.last_time = time.time()

# Tempos: 0(Base)=45s, 1(Pendentes)=45s, 2(Relógio)=30s
esperas = {0: 45, 1: 45, 2: 30}

if time.time() - st.session_state.last_time > esperas.get(st.session_state.idx, 30):
    prox = {0: 1, 1: 2, 2: 0}
    st.session_state.idx = prox.get(st.session_state.idx, 0)
    st.session_state.last_time = time.time()
    st.rerun()

# 4. RENDERIZAÇÃO DAS TELAS
# Cabeçalho único para reutilizar
def render_header(titulo):
    st.markdown(f'''<div class="topo-container">
        <div class="topo-esquerda">{logo_html}</div>
        <div class="topo-centro">{titulo}</div>
        <div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div>
    </div>''', unsafe_allow_html=True)

if st.session_state.idx == 0:
    render_header("🚀 TÉCNICOS EM BASE")
    # [COLE AQUI SEU CÓDIGO DA TELA 0]

elif st.session_state.idx == 1:
    render_header("CONTRATOS PENDENTES")
    # [COLE AQUI SEU CÓDIGO DA TELA 1]

elif st.session_state.idx == 2:
    render_header("HORÁRIO")
    st.markdown(f'''<div style="text-align:center; padding-top:100px;">
        <div style="font-size:180px; font-weight:900; color:#003366;">{datetime.now().strftime("%H:%M:%S")}</div>
        <div style="font-size:40px; color:#666;">{datetime.now().strftime("%d/%m/%Y")}</div>
    </div>''', unsafe_allow_html=True)

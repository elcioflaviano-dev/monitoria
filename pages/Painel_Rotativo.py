import streamlit as st
import pandas as pd
import os
import time
import base64
import calendar
from datetime import datetime, timedelta

# =========================================================================
# CONFIGURAÇÕES E PARÂMETROS OPERACIONAIS 🚀
# =========================================================================
ROOT_DIR = os.getcwd()
ARQUIVO_ROTA_DISCO = os.path.join(ROOT_DIR, "rota_sincronizada.csv")
ARQUIVO_CONSULTIVO = os.path.join(ROOT_DIR, "consultivo_sincronizado.csv")

ARQUIVO_LOGO = os.path.join(ROOT_DIR, "logo.png")
if not os.path.exists(ARQUIVO_LOGO):
    ARQUIVO_LOGO = os.path.join(ROOT_DIR, "pages", "logo.png")

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

def carregar_logo_html(caminho_imagem):
    if os.path.exists(caminho_imagem):
        try:
            with open(caminho_imagem, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f'<img src="data:image/png;base64,{encoded_string}" style="height: 100px; width: auto; object-fit: contain; display: block;">'
        except: return '<div></div>'
    return '<div></div>'

logo_html = carregar_logo_html(ARQUIVO_LOGO)

st.markdown("""<style>
    [data-testid="stHeader"] { visibility: hidden !important; }
    .stDeployButton { display: none !important; }
    footer { visibility: hidden !important; }
    #MainMenu { visibility: hidden !important; }
    [data-testid="stSidebar"] { display: none !important; }
    .stApp { background-color: #ffffff !important; }
    .topo-container { background: #003366; color: white; padding: 0px 30px; border-radius: 0 0 15px 15px; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; margin-bottom: 10px; height: 100px; }
    .topo-centro { font-size: 45px; font-weight: 900; text-align: center; white-space: nowrap; }
    .relogio-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 70vh; background-color: #ffffff; width: 100%; }
    .hora-gigante { font-size: 180px; font-weight: 900; color: #003366; text-shadow: 4px 4px 10px rgba(0,0,0,0.1); line-height: 1; letter-spacing: 5px; }
    .data-media { font-size: 40px; color: #666; font-weight: bold; margin-top: -20px; }
</style>""", unsafe_allow_html=True)

SUPS_ABC = ["EDSON MARCO", "MARCOS ROBERTO", "NELSON"]
SUPS_SP = ["ALAN", "FRANCISCO", "JOAO CARLOS MIRON"]
SUPERVISORES_ORDENADOS = SUPS_ABC + SUPS_SP

def obter_nome_visual(nome_completo):
    n = str(nome_completo).upper()
    if 'FRANCISCO' in n: return "FRANCISCO"
    if 'MARCOS' in n: return "MARCOS ROBERTO"
    if 'EDSON' in n: return "EDSON MARCO"
    if 'JOAO' in n or 'MIRON' in n: return "JOÃO CARLOS"
    if 'NELSON' in n: return "NELSON"
    if 'ALAN' in n: return "ALAN"
    return n.split()[0]

if "idx" not in st.session_state: 
    st.session_state.idx = 0          
    st.session_state.last_main = 0   
    st.session_state.last_time = time.time()
    st.session_state.novo_ciclo = True
    st.session_state.script_audio_atual = ""

agora_br = datetime.utcnow() - timedelta(hours=3)
minutos_agora = agora_br.hour * 60 + agora_br.minute

# Lógica de áudio corrigida
regras_audio_ind = [(13*60, 13*60 + 15), (16*60, 16*60 + 15)]
permitir_audio_ind = any(inicio <= minutos_agora <= fim for inicio, fim in regras_audio_ind)
badge_ativo = '<span style="font-size: 14px; vertical-align: middle; background: #2e7d32; color: #fff; padding: 4px 10px; border-radius: 10px; margin-left: 15px;">🔊</span>'
badge_mudo = '<span style="font-size: 14px; vertical-align: middle; background: #c62828; color: #fff; padding: 4px 10px; border-radius: 10px; margin-left: 15px;">🔇</span>'
html_audio_ind = badge_ativo if permitir_audio_ind else badge_mudo

# Rotação de telas
if st.session_state.idx == 0: espera = 60
elif st.session_state.idx == 1: espera = 60
elif st.session_state.idx == 5: espera = 60
elif st.session_state.idx == 3: espera = 45
elif st.session_state.idx == 2: espera = 30
elif st.session_state.idx == 4: espera = 2

if time.time() - st.session_state.last_time > espera:
    seq = [1, 4, 5, 4, 3, 4, 2]
    idx_atual = seq.index(st.session_state.idx) if st.session_state.idx in seq else -1
    prox_idx = seq[(idx_atual + 1) % len(seq)]
    st.session_state.idx = prox_idx
    st.session_state.last_time = time.time()
    st.rerun()

CONTEUDO_TV = st.empty()

with CONTEUDO_TV.container():
    if st.session_state.idx == 4:
        st.markdown('<div style="height: 100vh; width: 100vw; background-color: #ffffff;"></div>', unsafe_allow_html=True)
        time.sleep(1.5)
        st.rerun()

    elif st.session_state.idx == 2:
        st.markdown(f'''<div class="topo-container">
            <div class="topo-esquerda">{logo_html}</div>
            <div class="topo-centro">HORÁRIO</div>
            <div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div>
        </div>''', unsafe_allow_html=True)
        tempo_real = datetime.utcnow() - timedelta(hours=3)
        st.markdown(f'''
            <div class="relogio-container">
                <div class="hora-gigante">{tempo_real.strftime("%H:%M:%S")}</div>
                <div class="data-media">{tempo_real.strftime("%d/%m/%Y")}</div>
            </div>
        ''', unsafe_allow_html=True)
        time.sleep(1)
        st.rerun()

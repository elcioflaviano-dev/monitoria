import streamlit as st
import pandas as pd
import os
import time
import base64
from datetime import datetime, timedelta

# CONFIGURAÇÕES DE CAMINHOS E LINKS
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1kB1YmUuhzHpfN1dLv8PaQn0ipXcHcd6kGKnI3nguT14/export?format=csv&gid=0"
ROOT_DIR = os.getcwd()
ARQUIVO_ROTA_DISCO = os.path.join(ROOT_DIR, "rota_sincronizada.csv")

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

# DEFINIÇÃO CRÍTICA PARA EVITAR NAMEERROR
logo_html = carregar_logo_html(ARQUIVO_LOGO)

st.markdown("""<style>
    [data-testid="stHeader"] { visibility: hidden !important; }
    .stDeployButton { display: none !important; }
    footer { visibility: hidden !important; }
    #MainMenu { visibility: hidden !important; }
    [data-testid="stSidebar"] { display: none !important; }
    .stApp { background-color: #ffffff !important; }

    .topo-container { background: #003366; color: white; padding: 0px 30px; border-radius: 0 0 15px 15px; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; margin-bottom: 10px; height: 100px; }
    .topo-esquerda { display: flex; justify-content: flex-start; align-items: center; height: 100%; }
    .topo-centro { font-size: 45px; font-weight: 900; text-align: center; white-space: nowrap; }
    .topo-direita { display: flex; justify-content: flex-end; align-items: center; }
    .botao-home { color: #fff; font-size: 18px; font-weight: bold; border: 2px solid #fff; padding: 8px 15px; border-radius: 5px; text-decoration: none; }
    
    .box-base { background: #e8f5e9; border-left: 10px solid #2e7d32; padding: 15px 10px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.15); margin-bottom: 10px; }
    .box-base-sp { background: #dcf7f5; border-left: 10px solid #03a398; padding: 15px 10px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.15); margin-bottom: 10px; }
    .nome-base { font-size: 28px; font-weight: 900; color: #333; text-transform: uppercase;}
    .num-base { font-size: 85px; font-weight: 900; color: #111; line-height: 1.1; }
    
    .box-contagem { background: #f0f2f6; border-left: 8px solid #cc6600; padding: 15px 5px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); margin-top: 15px; margin-left: 10px; margin-right: 10px; margin-bottom: 15px; position: relative; z-index: 1; }
    .box-nome { font-size: 18px; font-weight: 900; color: #003366; text-transform: uppercase;}
    .box-num { font-size: 65px; font-weight: 900; color: #cc6600; line-height: 1; }
    
    .destaque-ativo { transform: scale(1.30) !important; box-shadow: 0px 25px 45px rgba(204, 102, 0, 0.6) !important; border-left: 20px solid #ff8800 !important; background: #fff8e1 !important; z-index: 9999 !important; }
    .relogio-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 70vh; background-color: #ffffff; width: 100%; }
    .hora-gigante { font-size: 180px; font-weight: 900; color: #003366; text-shadow: 4px 4px 10px rgba(0,0,0,0.1); line-height: 1; letter-spacing: 5px; }
    .data-media { font-size: 40px; color: #666; font-weight: bold; margin-top: -20px; }
    .tec-base-nome { background: #f8f9fa; padding: 8px 12px; border-left: 5px solid #008080; border-radius: 4px; margin-bottom: 8px; font-weight: bold; font-size: 16px; color: #333; box-shadow: 1px 1px 3px rgba(0,0,0,0.1); }
</style>""", unsafe_allow_html=True)

# ... [MANTENHA AQUI SUAS LISTAS FIXAS E A FUNÇÃO obter_nome_visual] ...

# ⚙️ MÁQUINA DE TEMPO E ESTADOS
if "idx" not in st.session_state: 
    st.session_state.idx = 0
    st.session_state.last_time = time.time()
    st.session_state.novo_ciclo = True

# Lógica de Rotação (Apenas telas 0, 1, 2)
esperas = {0: 60, 1: 60, 2: 120, 4: 2} # Tela 4 é a branca de limpeza
tempo_passado = time.time() - st.session_state.last_time

if tempo_passado > esperas.get(st.session_state.idx, 30):
    fluxo = {0: 4, 4: 1, 1: 4, 4: 2, 2: 4, 4: 0} # 0 -> 4 -> 1 -> 4 -> 2 -> 4 -> 0
    st.session_state.idx = fluxo.get(st.session_state.idx, 0)
    st.session_state.last_time = time.time()
    st.session_state.novo_ciclo = True
    st.rerun()

# RENDERIZAÇÃO DAS TELAS
if st.session_state.idx == 4:
    st.markdown('<div style="height: 100vh; width: 100vw; background-color: #ffffff;"></div>', unsafe_allow_html=True)
elif st.session_state.idx == 0:
    # [COLE AQUI SEU CÓDIGO DA TELA 0]
elif st.session_state.idx == 1:
    # [COLE AQUI SEU CÓDIGO DA TELA 1]
elif st.session_state.idx == 2:
    # [COLE AQUI SEU CÓDIGO DA TELA 2 (RELÓGIO)]

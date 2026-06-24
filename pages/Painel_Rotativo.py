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

# ... (MANTENHA AQUI TODO O SEU CÓDIGO DA TELA 0 E 1 IGUAL) ...
# ... (APENAS SUBSTITUA O BLOCO DE ÁUDIO E O BLOCO DO RELÓGIO ABAIXO) ...

# 🔕 3. FECHADURA DE ÁUDIO EXCLUSIVA PARA INDICADORES (Tela 3)
permitir_audio_ind = False
regras_audio_ind = [(13*60, 13*60 + 15), (16*60, 16*60 + 15)]
# 🔥 CORREÇÃO: Removido o lixo de caracteres que causou o SyntaxError
for inicio, f in regras_audio_ind:
    if inicio <= minutos_agora <= f:
        permitir_audio_ind = True
        break

# ... (MANTENHA A LÓGICA DE ROTAÇÃO ATÉ O RELÓGIO) ...

# -------------------------------------------------------------------------
# TELA 2: HORÁRIO (CORRIGIDO)
# -------------------------------------------------------------------------
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
    
    if st.session_state.novo_ciclo:
        st.session_state.script_audio_atual = f"<script>{JS_MOTOR_AUDIO}anunciarBase('Hora certa: {tempo_real.strftime('%H e %M')}.', 0);</script>"
        st.session_state.novo_ciclo = False
    st.components.v1.html(st.session_state.script_audio_atual, height=0)
    time.sleep(1)
    st.rerun()

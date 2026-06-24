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
    .box-base { background: #e8f5e9; border-left: 10px solid #2e7d32; padding: 15px 10px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.15); margin-bottom: 15px; }
    .box-base-sp { background: #e0f2f1; border-left: 10px solid #00897b; padding: 15px 10px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.15); margin-bottom: 15px; }
    .nome-base { font-size: 22px; font-weight: 900; color: #333; text-transform: uppercase;}
    .num-base { font-size: 85px; font-weight: 900; color: #111; line-height: 1.1; }
    .sup-card { background: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .sup-name { font-size: 20px; font-weight: 900; color: #333; }
</style>""", unsafe_allow_html=True)

SUPS_ABC = ["EDSON MARCO", "MARCOS ROBERTO", "NELSON"]
SUPS_SP = ["ALAN", "FRANCISCO", "JOAO CARLOS MIRON"]
SUPERVISORES_ORDENADOS = SUPS_ABC + SUPS_SP

if "idx" not in st.session_state: 
    st.session_state.idx = 1
    st.session_state.last_time = time.time()

# Motor de Rotação
if time.time() - st.session_state.last_time > 45:
    seq = [1, 4, 5, 4, 3, 4, 2]
    st.session_state.idx = seq[(seq.index(st.session_state.idx) + 1) % len(seq)]
    st.session_state.last_time = time.time()
    st.rerun()

# RENDERIZAÇÃO
CONTEUDO = st.empty()
with CONTEUDO.container():
    if st.session_state.idx == 4:
        st.markdown('<div style="height: 100vh; width: 100vw; background-color: #ffffff;"></div>', unsafe_allow_html=True)
    
    elif st.session_state.idx == 5:
        st.markdown('<div class="topo-container"><div class="topo-centro">PERFORMANCE CONSULTIVO</div></div>', unsafe_allow_html=True)
        if os.path.exists(ARQUIVO_CONSULTIVO):
            df = pd.read_csv(ARQUIVO_CONSULTIVO, dtype=str)
            df.columns = [c.upper().strip() for c in df.columns]
            
            # Filtro de Venda e Base
            df = df[df['TIPO DE TABULAÇÃO'].str.upper() == 'VENDA'].copy()
            df = df[df['BASE'].str.upper() != 'GRU'].copy()
            
            # MOTOR DE EXTRAÇÃO: Qualquer sequência de 9 ou 10 dígitos
            df['QTD'] = df['OBSERVACAO'].fillna('').astype(str).str.findall(r'\d{9,10}').apply(len)
            
            # Exibição simplificada para teste
            c1, c2 = st.columns(2)
            c1.metric("ABC TOTAL", df[df['BASE'] == 'ABC']['QTD'].sum())
            c2.metric("SP TOTAL", df[df['BASE'] == 'SP']['QTD'].sum())
            st.write("Dados processados com sucesso.")

    elif st.session_state.idx == 2:
        st.markdown('<div class="topo-container"><div class="topo-centro">HORÁRIO</div></div>', unsafe_allow_html=True)
        t = datetime.utcnow() - timedelta(hours=3)
        st.markdown(f'<div class="relogio-container"><div class="hora-gigante">{t.strftime("%H:%M:%S")}</div></div>', unsafe_allow_html=True)
        time.sleep(1)
        st.rerun()

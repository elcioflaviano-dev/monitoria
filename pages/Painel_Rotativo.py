import streamlit as st
import pandas as pd
import os
import time
import base64
from datetime import datetime, timedelta

# =========================================================================
# CONFIGURAÇÕES DE CAMINHOS
# =========================================================================
ROOT_DIR = os.getcwd()
ARQUIVO_ROTA_DISCO = os.path.join(ROOT_DIR, "rota_sincronizada.csv")
ARQUIVO_LOGO = os.path.join(ROOT_DIR, "logo.png")
if not os.path.exists(ARQUIVO_LOGO):
    ARQUIVO_LOGO = os.path.join(ROOT_DIR, "pages", "logo.png")

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# MOTOR DE ÁUDIO E VOZ
JS_MOTOR_AUDIO = """
<script>
function tocarAlertaChamaAtencao() {
    try {
        let ctx = new (window.parent.AudioContext || window.AudioContext)();
        let tempo = ctx.currentTime;
        let osc1 = ctx.createOscillator(); let gain1 = ctx.createGain();
        osc1.type = 'triangle'; osc1.frequency.setValueAtTime(880, tempo);
        gain1.gain.setValueAtTime(0, tempo); gain1.gain.linearRampToValueAtTime(0.4, tempo + 0.05); gain1.gain.exponentialRampToValueAtTime(0.01, tempo + 0.6);
        osc1.connect(gain1); gain1.connect(ctx.destination); osc1.start(tempo); osc1.stop(tempo + 0.6);
    } catch(e) {}
}
function anunciarBase(texto) {
    tocarAlertaChamaAtencao();
    setTimeout(() => {
        let synth = window.parent.speechSynthesis || window.speechSynthesis;
        let m = new SpeechSynthesisUtterance(texto);
        m.lang = 'pt-BR'; synth.speak(m);
    }, 1000);
}
</script>
"""

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
    .topo-esquerda { display: flex; justify-content: flex-start; align-items: center; }
    .topo-centro { font-size: 45px; font-weight: 900; text-align: center; }
    .topo-direita { display: flex; justify-content: flex-end; }
    .botao-home { color: #fff; font-size: 18px; font-weight: bold; border: 2px solid #fff; padding: 8px 15px; border-radius: 5px; text-decoration: none; }
    .box-contagem { background: #f0f2f6; border-left: 8px solid #cc6600; padding: 15px; text-align: center; border-radius: 8px; margin: 10px; }
    .box-nome { font-size: 18px; font-weight: 900; color: #003366; }
    .box-num { font-size: 65px; font-weight: 900; color: #cc6600; }
    .relogio-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 60vh; }
    .hora-gigante { font-size: 180px; font-weight: 900; color: #003366; }
</style>""", unsafe_allow_html=True)

# LÓGICA DE ROTAÇÃO
if "idx" not in st.session_state: st.session_state.idx = 0
if "last_time" not in st.session_state: st.session_state.last_time = time.time()

# Playlist: Relógio -> Pendentes (Tec1) -> Relógio -> Base
ordem_telas = [2, 1, 2, 0] 

if time.time() - st.session_state.last_time > 30:
    st.session_state.idx = (st.session_state.idx + 1) % len(ordem_telas)
    st.session_state.last_time = time.time()
    st.rerun()

tela_atual = ordem_telas[st.session_state.idx]

# =========================================================================
# TELAS
# =========================================================================

# TELA 0: TÉCNICOS NA BASE
if tela_atual == 0:
    st.markdown(f'''<div class="topo-container"><div class="topo-esquerda">{logo_html}</div><div class="topo-centro">🚀 TÉCNICOS EM BASE</div><div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div></div>''', unsafe_allow_html=True)
    st.components.v1.html(JS_MOTOR_AUDIO + "<script>anunciarBase('Visualizando técnicos na base.');</script>", height=0)
    # Coloque aqui a sua lógica original de exibição dos técnicos da Tela 0

# TELA 1: CONTRATOS PENDENTES (TEC1)
elif tela_atual == 1:
    st.markdown(f'''<div class="topo-container"><div class="topo-esquerda">{logo_html}</div><div class="topo-centro">CONTRATOS PENDENTES</div><div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div></div>''', unsafe_allow_html=True)
    st.components.v1.html(JS_MOTOR_AUDIO + "<script>anunciarBase('Visualizando contratos pendentes.');</script>", height=0)
    
    if os.path.exists(ARQUIVO_ROTA_DISCO):
        df = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
        df.columns = df.columns.str.strip().str.upper()
        sups = sorted(df['SUPERVISOR'].dropna().unique().tolist()) if 'SUPERVISOR' in df.columns else []
        cols = st.columns(len(sups) if sups else 1)
        for i, sup in enumerate(sups):
            qtd = len(df[df['SUPERVISOR'].astype(str).str.contains(str(sup), na=False)])
            with cols[i]:
                st.markdown(f'<div class="box-contagem"><div class="box-nome">{sup}</div><div class="box-num">{qtd}</div></div>', unsafe_allow_html=True)

# TELA 2: HORÁRIO
elif tela_atual == 2:
    st.markdown(f'''<div class="topo-container"><div class="topo-esquerda">{logo_html}</div><div class="topo-centro">HORÁRIO</div><div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div></div>''', unsafe_allow_html=True)
    st.markdown(f'<div class="relogio-container"><div class="hora-gigante">{datetime.now().strftime("%H:%M:%S")}</div></div>', unsafe_allow_html=True)

time.sleep(1)
st.rerun()

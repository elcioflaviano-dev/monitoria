import streamlit as st
import pandas as pd
import os
import time
import base64
import streamlit.components.v1 as components
from datetime import datetime

# =========================================================================
# CONFIGURAÇÕES
# =========================================================================
URL_PLANILHA = "https://totaltecnologia-my.sharepoint.com/:x:/g/personal/elcio_nunes_totaltecnologia_onmicrosoft_com/IQBPzXoLVti8RJTgULiXf-nQAcrWXLiLMfks1IgJPO4nJeg?download=1"
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# CSS BLINDADO (Oculta menu e define o visual)
st.markdown("""<style>
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stHeader"] { visibility: hidden !important; }
    .stDeployButton { display: none !important; }
    footer { visibility: hidden !important; }
    .stApp { background-color: #ffffff !important; }
    
    .topo-container { background: #003366; color: white; padding: 10px 30px; border-radius: 0 0 15px 15px; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; height: 100px; }
    .topo-esquerda { display: flex; justify-content: flex-start; align-items: center; }
    .topo-centro { font-size: 35px; font-weight: 900; text-align: center; }
    .topo-direita { display: flex; justify-content: flex-end; }
    .botao-home { color: #fff; font-size: 18px; font-weight: bold; border: 2px solid #fff; padding: 8px 15px; border-radius: 5px; text-decoration: none; }
    
    .box-contagem { background: #f0f2f6; border-left: 8px solid #cc6600; padding: 10px; text-align: center; border-radius: 8px; margin: 5px; }
    .box-nome { font-size: 16px; font-weight: 800; color: #003366; }
    .box-num { font-size: 40px; font-weight: 900; color: #cc6600; }
    .relogio-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 60vh; }
    .hora-gigante { font-size: 150px; font-weight: 900; color: #003366; }
</style>""", unsafe_allow_html=True)

# =========================================================================
# FUNÇÕES DE APOIO
# =========================================================================
def tocar_alerta():
    js = "<script>var audio = new Audio('https://www.soundjay.com/buttons/beep-07.wav'); audio.play();</script>"
    components.html(js, height=0)

def renderizar_topo(titulo):
    logo_path = "logo.png" if os.path.exists("logo.png") else "pages/logo.png"
    logo_html = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_html = f'<img src="data:image/png;base64,{base64.b64encode(f.read()).decode()}" style="height: 60px;">'
    st.markdown(f'''<div class="topo-container">
        <div class="topo-esquerda">{logo_html}</div>
        <div class="topo-centro">{titulo}</div>
        <div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div>
    </div>''', unsafe_allow_html=True)

# LÓGICA DE ROTAÇÃO
if "idx" not in st.session_state: st.session_state.idx = 0
if "last_time" not in st.session_state: st.session_state.last_time = time.time()

ordem_telas = [2, 1, 2, 3] # Relógio -> Tec1 -> Relógio -> Indicadores

if time.time() - st.session_state.last_time > 30:
    st.session_state.idx = (st.session_state.idx + 1) % len(ordem_telas)
    st.session_state.last_time = time.time()
    tocar_alerta() # Toca o som na troca
    st.rerun()

tela_atual = ordem_telas[st.session_state.idx]

# =========================================================================
# TELAS
# =========================================================================

# TELA 1: TEC1 (Total Base + Pendentes Supervisor)
if tela_atual == 1:
    renderizar_topo("TEC 1 - OPERAÇÃO")
    if os.path.exists(ARQUIVO_ROTA_DISCO):
        df = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
        df.columns = df.columns.str.strip().str.upper()
        
        # 1. Total por Base (Topo da página)
        if 'BASE' in df.columns:
            bases = df['BASE'].value_counts()
            cols_base = st.columns(len(bases))
            for i, (base, qtd) in enumerate(bases.items()):
                with cols_base[i]:
                    st.markdown(f'<div class="box-contagem"><div class="box-nome">{base}</div><div class="box-num">{qtd}</div></div>', unsafe_allow_html=True)
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # 2. Pendentes por Supervisor
        if 'SUPERVISOR' in df.columns:
            sups = sorted(df['SUPERVISOR'].dropna().unique().tolist())
            cols_sup = st.columns(len(sups) if sups else 1)
            for i, sup in enumerate(sups):
                qtd = len(df[df['SUPERVISOR'] == sup])
                with cols_sup[i]:
                    st.markdown(f'<div class="box-contagem"><div class="box-nome">{sup}</div><div class="box-num">{qtd}</div></div>', unsafe_allow_html=True)
    else: st.error("Arquivo de rota não encontrado.")

# TELA 2: RELÓGIO
elif tela_atual == 2:
    renderizar_topo("HORÁRIO")
    st.markdown(f'<div class="relogio-container"><div class="hora-gigante">{datetime.now().strftime("%H:%M:%S")}</div></div>', unsafe_allow_html=True)

# TELA 3: INDICADORES
elif tela_atual == 3:
    renderizar_topo("📈 INDICADORES DA EQUIPE")
    try:
        df_ind = pd.read_excel(URL_PLANILHA, engine='openpyxl')
        df_ind.columns = df_ind.columns.str.strip().str.upper()
        st.dataframe(df_ind, use_container_width=True)
    except Exception as e:
        st.error(f"Erro no Excel Online: {e}")

time.sleep(1)
st.rerun()

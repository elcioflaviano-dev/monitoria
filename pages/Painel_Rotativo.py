import streamlit as st
import pandas as pd
import os
import time
import base64
from datetime import datetime, timedelta

# CONFIGURAÇÕES DE CAMINHOS E LINKS
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1kB1YmUuhzHpfN1dLv8PaQn0ipXcHcd6kGKnI3nguT14/export?format=csv&gid=0"
ROOT_DIR = os.getcwd()
ARQUIVO_INDICADORES = os.path.join(ROOT_DIR, "indicadores_data.csv")
ARQUIVO_ROTA_DISCO = os.path.join(ROOT_DIR, "rota_sincronizada.csv")
ARQUIVO_LOGO = os.path.join(ROOT_DIR, "logo.png")
if not os.path.exists(ARQUIVO_LOGO): ARQUIVO_LOGO = os.path.join(ROOT_DIR, "pages", "logo.png")

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# CSS GLOBAL
st.markdown("""<style>
    [data-testid="stHeader"] { visibility: hidden !important; }
    .stDeployButton { display: none !important; }
    footer { visibility: hidden !important; }
    #MainMenu { visibility: hidden !important; }
    [data-testid="stSidebar"] { display: none !important; }
    .stApp { background-color: #ffffff !important; }

    .topo-container { background: #003366; color: white; padding: 0px 30px; border-radius: 0 0 15px 15px; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; margin-bottom: 10px; height: 100px; }
    .topo-centro { font-size: 45px; font-weight: 900; text-align: center; }
    
    .box-base { background: #e8f5e9; border-left: 10px solid #2e7d32; padding: 15px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.1); margin-bottom: 10px; }
    .box-base-sp { background: #dcf7f5; border-left: 10px solid #03a398; padding: 15px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.1); margin-bottom: 10px; }
    .nome-base { font-size: 28px; font-weight: 900; color: #333; text-transform: uppercase;}
    .num-base { font-size: 85px; font-weight: 900; color: #111; line-height: 1.1; }
    
    .box-contagem { background: #f0f2f6; border-left: 8px solid #cc6600; padding: 10px; text-align: center; border-radius: 8px; margin: 10px; }
    .box-nome { font-size: 18px; font-weight: 900; color: #003366; text-transform: uppercase;}
    .box-num { font-size: 40px; font-weight: 900; color: #cc6600; }
    .falta-box { background: #ffebee; border: 1px solid #ffcdd2; padding: 5px; border-radius: 4px; }
    .falta-label { font-size: 10px; font-weight: bold; color: #c62828; }

    .hora-gigante { font-size: 180px; font-weight: 900; color: #003366; text-align: center; }
    .tec-base-nome { background: #f8f9fa; padding: 8px; border-left: 5px solid #008080; margin-bottom: 5px; font-weight: bold; }
</style>""", unsafe_allow_html=True)

# MÁQUINA DE TEMPO
if "idx" not in st.session_state: 
    st.session_state.idx = 0
    st.session_state.last_time = time.time()

agora = datetime.utcnow() - timedelta(hours=3)
esperas = {0: 60, 1: 30, 2: 60, 3: 30, 4: 1} # 4 é a tela branca rápida

if time.time() - st.session_state.last_time > esperas.get(st.session_state.idx, 10):
    # Ciclo lógico
    if agora.hour < 8: st.session_state.idx = 0
    else:
        fluxo = {0: 4, 4: 1, 1: 4, 4: 2, 2: 4, 4: 3, 3: 4}
        st.session_state.idx = fluxo.get(st.session_state.idx, 2)
    st.session_state.last_time = time.time()
    st.rerun()

# RENDERIZAÇÃO
if st.session_state.idx == 4:
    st.markdown('<div style="height: 100vh;"></div>', unsafe_allow_html=True)

elif st.session_state.idx == 0:
    st.markdown('<div class="topo-container"><div class="topo-centro">🚀 TÉCNICOS EM BASE</div></div>', unsafe_allow_html=True)
    # [AQUI VAI O TEU CÓDIGO DA TELA 0]

elif st.session_state.idx == 1:
    st.markdown('<div class="topo-container"><div class="topo-centro">CONTRATOS PENDENTES</div></div>', unsafe_allow_html=True)
    # [AQUI VAI O TEU CÓDIGO DA TELA 1]

elif st.session_state.idx == 2:
    st.markdown(f'<div class="relogio-container"><div class="hora-gigante">{datetime.now().strftime("%H:%M:%S")}</div></div>', unsafe_allow_html=True)

elif st.session_state.idx == 3:
    st.markdown('<div class="topo-container"><div class="topo-centro">📈 INDICADORES</div></div>', unsafe_allow_html=True)
    df_ind = pd.read_csv(ARQUIVO_INDICADORES) if os.path.exists(ARQUIVO_INDICADORES) else pd.DataFrame()
    if not df_ind.empty:
        c1, c2 = st.columns(2)
        def desenhar(base, col):
            df_b = df_ind[df_ind["BASE"] == base]
            for sup in sorted(df_b['SUPERVISOR'].unique()):
                d = df_b[df_b['SUPERVISOR'] == sup]
                st.markdown(f'''<div class="box-contagem">
                    <div class="box-nome">{sup}</div>
                    <div style="display:flex; justify-content:space-around;">
                        <div class="falta-box"><div class="falta-label">NR35</div><div class="box-num">{int(d[d["INDICADOR"]=="NR35"]["VALOR"].sum())}</div></div>
                        <div class="falta-box"><div class="falta-label">CERT</div><div class="box-num">{int(d[d["INDICADOR"]=="Certidão"]["VALOR"].sum())}</div></div>
                        <div class="falta-box"><div class="falta-label">BST</div><div class="box-num">{int(d[d["INDICADOR"]=="BST"]["VALOR"].sum())}</div></div>
                    </div>
                </div>''', unsafe_allow_html=True)
        with c1: desenhar("ABC", c1)
        with c2: desenhar("SP", c2)

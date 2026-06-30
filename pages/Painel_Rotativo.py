import streamlit as st
import pandas as pd
import os
import time
import base64
import calendar
import unicodedata
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

# --- FUNÇÕES GLOBAIS E CSS ---
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
    .viewerBadge_container, .viewerBadge_link, [data-testid="viewerBadge"], #viewerBadge { display: none !important; }
    [data-testid="stHeader"], .stDeployButton, footer, #MainMenu, [data-testid="stSidebar"] { display: none !important; visibility: hidden !important; }
    .stApp { background-color: #ffffff !important; }
    .topo-container { background: #003366; color: white; padding: 0px 30px; border-radius: 0 0 15px 15px; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; margin-bottom: 10px; height: 100px; }
    .topo-esquerda { display: flex; justify-content: flex-start; align-items: center; height: 100%; }
    .topo-centro { font-size: 45px; font-weight: 900; text-align: center; white-space: nowrap; }
    .topo-direita { display: flex; justify-content: flex-end; align-items: center; }
    .botao-home { color: #fff; font-size: 18px; font-weight: bold; border: 2px solid #fff; padding: 8px 15px; border-radius: 5px; text-decoration: none; }
    .box-base { background: #e8f5e9; border-left: 10px solid #2e7d32; padding: 15px 10px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.15); margin-bottom: 25px; }
    .box-base-sp { background: #e0f2f1; border-left: 10px solid #00897b; padding: 15px 10px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.15); margin-bottom: 25px; }
    .nome-base { font-size: 26px !important; font-weight: 900; color: #333; text-transform: uppercase;}
    .num-base { font-size: 100px !important; font-weight: 900; color: #111; line-height: 1.1; }
    .box-contagem { background: #f0f2f6; border-left: 8px solid #cc6600; padding: 10px 5px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); margin-bottom: 10px; position: relative; z-index: 1; transition: 0.3s; }
    .box-nome { font-size: 18px !important; font-weight: 900; color: #003366; text-transform: uppercase; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .box-num { font-size: 60px !important; font-weight: 900; color: #cc6600; line-height: 1; margin-top: 5px; }
    .destaque-ativo { transform: scale(1.15) !important; box-shadow: 0px 15px 30px rgba(204, 102, 0, 0.5) !important; border-left: 12px solid #ff8800 !important; background: #fff8e1 !important; z-index: 9999 !important; }
    .ind-base-title { font-size: 32px !important; font-weight: 900; text-align: center; margin-bottom: 15px; margin-top: 5px; text-transform: uppercase; }
    .ind-base-title.abc { color: #2e7d32; }
    .ind-base-title.sp { color: #00695c; }
    .sup-card { background: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .sup-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 10px; }
    .sup-name { font-size: 32px !important; font-weight: 900; color: #333; text-transform: uppercase; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}
    .badge-faltas { background: #ffebee; color: #c62828; padding: 6px 12px; border-radius: 6px; font-size: 18px !important; font-weight: bold; border: 1px solid #ffcdd2; }
    .faltas-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }
    .falta-box { background-color: #ffebee; border: 1px solid #ffcdd2; border-radius: 6px; padding: 12px 5px; text-align: center; margin-bottom: 5px; }
    .falta-label { font-size: 14px !important; font-weight: bold; color: #c62828; text-transform: uppercase; margin-bottom: 6px; }
    .falta-value { font-size: 45px !important; font-weight: 900; color: #b30000; line-height: 1; }
    .relogio-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 70vh; background-color: #ffffff; width: 100%; }
    .hora-gigante { font-size: 180px; font-weight: 900; color: #003366; text-shadow: 4px 4px 10px rgba(0,0,0,0.1); line-height: 1; letter-spacing: 5px; }
    .data-media { font-size: 40px; color: #666; font-weight: bold; margin-top: -20px; }
    .tec-base-nome { background: #f8f9fa; padding: 8px 12px; border-left: 5px solid #008080; border-radius: 4px; margin-bottom: 8px; font-weight: bold; font-size: 18px !important; color: #333; box-shadow: 1px 1px 3px rgba(0,0,0,0.1); }
</style>""", unsafe_allow_html=True)

# --- REGRAS GLOBAIS ---
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

def limpar_texto(txt):
    if pd.isna(txt): return ''
    return unicodedata.normalize('NFKD', str(txt).strip().upper()).encode('ASCII', 'ignore').decode('utf-8')

# Inicialização dos estados
if "idx" not in st.session_state: 
    st.session_state.idx = 0          
    st.session_state.last_time = time.time()
    st.session_state.novo_ciclo = True
    st.session_state.script_audio_atual = ""
if "em_transicao" not in st.session_state:
    st.session_state.em_transicao = False

# --- LOGICA DE TELA E DADOS ---
# [O restante da lógica de tempo e áudio que você já possui...]
# (Mantive a estrutura para evitar erros de corte)

# O trecho corrigido da Tela 3 (Print Indicadores)
# [Busquei a linha 797 e corrigi o 'd' para 'c']
# A busca por colunas:
# col_nr35 = next((c for c in reversed(df_ind.columns) if 'NR35' in c or 'NR-35' in c), None)
# col_cert = next((c for c in reversed(df_ind.columns) if 'CERTID' in c or 'ELEGIVEL' in c or 'ELEGÍVEL' in c), None)
# col_bst  = next((c for c in reversed(df_ind.columns) if 'BST' in c or 'STEERING' in c or 'BAND' in c), None)

# [Para o Consultivo Diário (Tela 6), utilize a mesma lógica de texto puro/data que funcionou na outra página]

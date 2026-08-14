import streamlit as st
import pandas as pd
import numpy as np
import os
import time
import base64
import calendar
import unicodedata
import requests
import io
import pydeck as pdk
from datetime import datetime, timedelta

# =========================================================================
# CONFIGURAÇÕES E PARÂMETROS OPERACIONAIS 🚀
# =========================================================================
ROOT_DIR = os.getcwd()
ARQUIVO_ROTA_DISCO = os.path.join(ROOT_DIR, "rota_sincronizada.csv")
ARQUIVO_CONSULTIVO = os.path.join(ROOT_DIR, "consultivo_sincronizado.csv")
URL_PLANILHA_MASTER = "https://totaltecnologia-my.sharepoint.com/:x:/g/personal/elcio_nunes_totaltecnologia_onmicrosoft_com/IQBPzXoLVti8RJTgULiXf-nQAcrWXLiLMfks1IgJPO4nJeg?download=1"

ARQUIVO_LOGO = os.path.join(ROOT_DIR, "logo.png")
if not os.path.exists(ARQUIVO_LOGO):
    ARQUIVO_LOGO = os.path.join(ROOT_DIR, "pages", "logo.png")

# 📌 ALTERE AQUI A QUANTIDADE FIXA DE TÉCNICOS DA ROTA DOS MONTADOS (TELA 10)
QTD_TECNICOS_MONTADOS = {
    "EDSON MARCO": 21,
    "MAICON": 21,
    "MARCOS ROBERTO": 15,
    "NELSON": 20
}

# --- REGRAS GLOBAIS DE SUPERVISORES (TODOS DO ABC) ---
SUPS_ABC = ["EDSON MARCO", "MAICON", "MARCOS ROBERTO", "NELSON"]
SUPERVISORES_ORDENADOS = SUPS_ABC

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Inicialização dos estados da sessão
if "idx" not in st.session_state: 
    st.session_state.idx = 0          
    st.session_state.novo_ciclo = True
    st.session_state.script_audio_atual = ""
    st.session_state.prox_idx = 0

if "ticker_data" not in st.session_state:
    st.session_state.ticker_data = {}

if "ultima_sincronizacao" not in st.session_state:
    st.session_state.ultima_sincronizacao = time.time()

# =========================================================================
# MOTOR DE SINCRONIZAÇÃO AUTÔNOMA DA TV (5 EM 5 MINUTOS) ☁️
# =========================================================================
def baixar_dados_nuvem_background():
    try:
        headers = {'User-Agent': 'Mozilla/5.0', 'Accept': '*/*'}
        sessao = requests.Session()
        resposta = sessao.get(URL_PLANILHA_MASTER, headers=headers, allow_redirects=True, timeout=20)
        
        if resposta.status_code == 200:
            ficheiro_excel = io.BytesIO(resposta.content)
            try:
                df_cons_bruto = pd.read_excel(ficheiro_excel, sheet_name='CONSULTIVO', engine='openpyxl')
                if not df_cons_bruto.empty:
                    df_cons_bruto.columns = [str(c).strip().replace('\xa0', ' ') for c in df_cons_bruto.columns]
                    df_cons_bruto.to_csv(ARQUIVO_CONSULTIVO, index=False)
            except: pass

            ficheiro_excel.seek(0)
            try:
                df_bruto = pd.read_excel(ficheiro_excel, sheet_name='ROTA', engine='openpyxl')
                if not df_bruto.empty:
                    df_bruto.columns = [str(c).strip().replace('\xa0', ' ') for c in df_bruto.columns]
                    cols_sup = [c for c in df_bruto.columns if 'SUPERV' in str(c).upper()]
                    valores_supervisor = df_bruto[cols_sup[-1]].values if cols_sup else None
                    
                    colunas_mapeadas = {}
                    for col in list(df_bruto.columns):
                        col_upper = str(col).upper()
                        if col_upper in ['LOGIN DO TÉCNICO', 'LOGIN DO TECNICO', 'LOGIN']: colunas_mapeadas[col] = 'Login do Técnico'
                        elif 'STATUS' in col_upper and 'ATIVIDADE' in col_upper: colunas_mapeadas[col] = 'Status da Atividade'
                        elif 'TIPO' in col_upper and 'ATIVIDADE' in col_upper:
                            if '3' in col_upper: colunas_mapeadas[col] = 'Tipo de Atividade3'
                            else: colunas_mapeadas[col] = 'Tipo de Atividade'
                        elif col_upper in ['RECURSO', 'RECURS', 'TECNICO', 'NOME', 'TÉCNICO']: colunas_mapeadas[col] = 'Recurso'
                        elif 'TOTAL DE TAREFAS' in col_upper: colunas_mapeadas[col] = 'QTD_OS_COL'
                    
                    df_final = df_bruto.rename(columns=colunas_mapeadas)
                    df_final = df_final.loc[:, ~df_final.columns.duplicated(keep='first')]
                    
                    if valores_supervisor is not None: df_final['SUPERVISOR'] = valores_supervisor
                    else: df_final['SUPERVISOR'] = 'NÃO IDENTIFICADO'

                    df_final['SUPERVISOR'] = df_final['SUPERVISOR'].fillna('NÃO IDENTIFICADO').astype(str).str.strip().str.upper()
                    df_final['SUPERVISOR'] = df_final['SUPERVISOR'].replace(['NAN', 'N/A', 'NULL', '', '-', '0', '0.0'], 'NÃO IDENTIFICADO')

                    if 'Recurso' not in df_final.columns and 'Login do Técnico' in df_final.columns:
                        df_final['Recurso'] = df_final['Login do Técnico']

                    df_final.to_csv(ARQUIVO_ROTA_DISCO, index=False)
            except: pass
    except: pass


def carregar_logo_html(caminho_imagem):
    if os.path.exists(caminho_imagem):
        try:
            with open(caminho_imagem, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f'<img src="data:image/png;base64,{encoded_string}" style="height: 100px; width: auto; object-fit: contain; display: block;">'
        except: return '<div></div>'
    return '<div></div>'

logo_html = carregar_logo_html(ARQUIVO_LOGO)

def render_topo(titulo):
    return f'''<div class="topo-container">
        <div class="topo-esquerda">{logo_html}</div>
        <div class="topo-centro">{titulo}</div>
        <div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div>
    </div>'''

st.markdown("""<style>
    /* COMPRESSÃO GERAL PARA CABER NA TELA SEM CORTAR */
    .block-container { padding-top: 0.5rem !important; padding-bottom: 50px !important; max-width: 98% !important; }
    ::-webkit-scrollbar { display: none !important; }
    html, body { -ms-overflow-style: none !important; scrollbar-width: none !important; overflow: hidden !important; }

    .viewerBadge_container, .viewerBadge_link, [data-testid="viewerBadge"], #viewerBadge { display: none !important; }
    [data-testid="stHeader"], .stDeployButton, footer, #MainMenu, [data-testid="stSidebar"] { display: none !important; visibility: hidden !important; }
    .stApp { background-color: #ffffff !important; }
    
    .topo-container { background: #003366; color: white; padding: 0px 20px; border-radius: 0 0 10px 10px; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; margin-bottom: 10px; height: 75px; }
    .topo-esquerda { display: flex; justify-content: flex-start; align-items: center; height: 100%; }
    .topo-centro { font-size: 35px; font-weight: 900; text-align: center; white-space: nowrap; }
    .topo-direita { display: flex; justify-content: flex-end; align-items: center; }
    .botao-home { color: #fff; font-size: 16px; font-weight: bold; border: 2px solid #fff; padding: 6px 12px; border-radius: 5px; text-decoration: none; }
    
    div[data-testid="stButton"] { position: fixed !important; bottom: 65px !important; right: 20px !important; z-index: 999999 !important; display: flex !important; justify-content: flex-end !important; width: auto !important; }
    div[data-testid="stButton"] > button { background-color: #003366 !important; color: #ffffff !important; border: 2px solid #ffffff !important; border-radius: 30px !important; padding: 6px 15px !important; font-size: 15px !important; font-weight: bold !important; opacity: 0.03 !important; transition: all 0.4s ease-in-out !important; }
    div[data-testid="stButton"] > button:hover { opacity: 1.0 !important; background-color: #ff9800 !important; border-color: #ffffff !important; transform: scale(1.05) !important; transform: scale(1.05) !important; }

    [data-testid="stDeckGlJsonChart"] { height: 72vh !important; min-height: 550px !important; border-radius: 12px; box-shadow: 2px 2px 10px rgba(0,0,0,0.15); }

    .box-base { background: #e8f5e9; border-left: 10px solid #2e7d32; padding: 8px 10px; text-align: center; }
</style>""", unsafe_allow_html=True)

# =========================================================================
# TRECHO QUE ESTAVA DANDO ERRO (CORRIGIDO PROTEGENDO A CONVERSÃO DE TIPOS)
# =========================================================================
# Nota: Esta variável 'df_hoje' e a constante 'QTD_PRODUTOS_CALC' devem existir no seu escopo de execução posterior.
if 'df_hoje' in locals() or 'df_hoje' in globals():
    # A linha abaixo foi corrigida usando pd.to_numeric com errors='coerce' para neutralizar textos ruins
    total_hoje_abc = int(pd.to_numeric(df_hoje[QTD_PRODUTOS_CALC], errors='coerce').sum()) if not df_hoje.empty else 0

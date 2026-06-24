import streamlit as st
import pandas as pd
import os
import time
import base64
import calendar
import unicodedata
from datetime import datetime, timedelta

# CONFIGURAÇÕES DA PÁGINA
st.set_page_config(page_title="Performance Consultivo", layout="wide")

ROOT_DIR = os.getcwd()
ARQUIVO_CONSULTIVO = os.path.join(ROOT_DIR, "consultivo_sincronizado.csv")
ARQUIVO_LOGO = os.path.join(ROOT_DIR, "logo.png")
if not os.path.exists(ARQUIVO_LOGO):
    ARQUIVO_LOGO = os.path.join(ROOT_DIR, "pages", "logo.png")

def carregar_logo_html(caminho_imagem):
    if os.path.exists(caminho_imagem):
        try:
            with open(caminho_imagem, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f'<img src="data:image/png;base64,{encoded_string}" style="height: 100px; width: auto; object-fit: contain; display: block;">'
        except: return '<div></div>'
    return '<div></div>'

logo_html = carregar_logo_html(ARQUIVO_LOGO)

# CSS GERAL
st.markdown("""<style>
    .stApp { background-color: #ffffff !important; }
    .topo-container { background: #003366; color: white; padding: 0px 30px; border-radius: 0 0 15px 15px; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; margin-bottom: 25px; height: 100px; }
    .topo-centro { font-size: 45px; font-weight: 900; text-align: center; }
    .box-base { background: #e8f5e9; border-left: 10px solid #2e7d32; padding: 15px; text-align: center; border-radius: 8px; margin-bottom: 25px; }
    .box-base-sp { background: #e0f2f1; border-left: 10px solid #00897b; padding: 15px; text-align: center; border-radius: 8px; margin-bottom: 25px; }
    .num-base { font-size: 85px; font-weight: 900; }
    .sup-card { background: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-bottom: 15px; }
    .falta-value { font-size: 32px; font-weight: 900; }
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

def limpar_texto(txt):
    if pd.isna(txt): return ''
    return unicodedata.normalize('NFKD', str(txt).strip().upper()).encode('ASCII', 'ignore').decode('utf-8')

# CABEÇALHO
st.markdown(f'''<div class="topo-container">
    <div class="topo-esquerda">{logo_html}</div>
    <div class="topo-centro">PERFORMANCE CONSULTIVO</div>
    <div class="topo-direita"></div>
</div>''', unsafe_allow_html=True)

if os.path.exists(ARQUIVO_CONSULTIVO):
    df_cons = pd.read_csv(ARQUIVO_CONSULTIVO, sep=None, engine='python', dtype=str)
    df_cons.columns = [unicodedata.normalize('NFKD', str(c)).encode('ASCII', 'ignore').decode('utf-8').strip().upper().replace(' ', '_') for c in df_cons.columns]

    df_cons['BASE'] = df_cons['BASE'].apply(limpar_texto) if 'BASE' in df_cons.columns else 'N/D'
    col_qtd = next((c for c in df_cons.columns if 'QTD' in c and 'PRODUTO' in c), None)
    df_cons['QTD_PRODUTOS_CALC'] = pd.to_numeric(df_cons[col_qtd].astype(str).str.replace(',', '.'), errors='coerce').fillna(0).astype(int) if col_qtd else 0

    # 🔥 SOMA TOTAL SEM #N/D 🔥
    total_abc = df_cons[(df_cons['BASE'] == 'ABC') & (df_cons['SUPERVISOR'] != '#N/D')]['QTD_PRODUTOS_CALC'].sum()
    total_sp = df_cons[(df_cons['BASE'] == 'SP') & (df_cons['SUPERVISOR'] != '#N/D')]['QTD_PRODUTOS_CALC'].sum()

    df_cons['SUPERVISOR'] = df_cons['SUPERVISOR'].apply(limpar_texto) if 'SUPERVISOR' in df_cons.columns else ''
    df_cons['SUPERVISOR_CLEAN'] = df_cons['SUPERVISOR'].apply(lambda x: next((s for s in SUPERVISORES_ORDENADOS if limpar_texto(s.split()[0]) in x), "DESCARTADO"))
    df_cards = df_cons[df_cons['SUPERVISOR_CLEAN'] != "DESCARTADO"].copy()

    col_abc, col_sp = st.columns(2)
    with col_abc:
        st.markdown(f'<div class="box-base"><div class="num-base">{total_abc}</div></div>', unsafe_allow_html=True)
        for sup in SUPS_ABC:
            qtd = df_cards[df_cards['SUPERVISOR_CLEAN'] == sup]['QTD_PRODUTOS_CALC'].sum()
            st.markdown(f'<div class="sup-card">{obter_nome_visual(sup)}: {qtd}</div>', unsafe_allow_html=True)
    with col_sp:
        st.markdown(f'<div class="box-base-sp"><div class="num-base">{total_sp}</div></div>', unsafe_allow_html=True)
        for sup in SUPS_SP:
            qtd = df_cards[df_cards['SUPERVISOR_CLEAN'] == sup]['QTD_PRODUTOS_CALC'].sum()
            st.markdown(f'<div class="sup-card">{obter_nome_visual(sup)}: {qtd}</div>', unsafe_allow_html=True)
else:
    st.warning("Arquivo não encontrado.")

time.sleep(60); st.rerun()

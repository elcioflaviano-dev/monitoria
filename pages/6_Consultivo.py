import streamlit as st
import pandas as pd
import os
import time
import base64
import unicodedata
from datetime import datetime, timedelta

# =========================================================================
# CONFIGURAÇÕES E CSS (LAYOUT MANTIDO)
# =========================================================================
st.set_page_config(page_title="Performance Consultivo", layout="wide")

ROOT_DIR = os.getcwd()
ARQUIVO_CONSULTIVO = os.path.join(ROOT_DIR, "consultivo_sincronizado.csv")
ARQUIVO_LOGO = os.path.join(ROOT_DIR, "logo.png")
if not os.path.exists(ARQUIVO_LOGO): ARQUIVO_LOGO = os.path.join(ROOT_DIR, "pages", "logo.png")

def carregar_logo_html(caminho_imagem):
    if os.path.exists(caminho_imagem):
        with open(caminho_imagem, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return f'<img src="data:image/png;base64,{encoded_string}" style="height: 100px; width: auto; object-fit: contain; display: block;">'
    return '<div></div>'

logo_html = carregar_logo_html(ARQUIVO_LOGO)

st.markdown("""<style>
    .stApp { background-color: #ffffff !important; }
    .topo-container { background: #003366; color: white; padding: 0px 30px; border-radius: 0 0 15px 15px; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; margin-bottom: 25px; height: 100px; }
    .topo-centro { font-size: 45px; font-weight: 900; text-align: center; }
    .box-base { background: #f8f9fa; border: 1px solid #ddd; padding: 20px; text-align: center; border-radius: 8px; margin-bottom: 25px; }
    .num-base { font-size: 85px; font-weight: 900; color: #111; }
    .sup-card { background: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .sup-header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 10px; border-bottom: 1px solid #eee; margin-bottom: 10px; }
    .sup-name { font-size: 24px; font-weight: 900; color: #333; }
    .badge-faltas { padding: 6px 12px; border-radius: 6px; font-weight: bold; border: 1px solid; }
    .faltas-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }
    .falta-box { border-radius: 6px; padding: 10px; text-align: center; border: 1px solid; }
    .falta-label { font-size: 11px; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; }
    .falta-value { font-size: 28px; font-weight: 900; }
</style>""", unsafe_allow_html=True)

# LÓGICA DE DADOS
SUPS_ABC = ["EDSON MARCO", "MARCOS ROBERTO", "NELSON"]
SUPS_SP = ["ALAN", "FRANCISCO", "JOAO CARLOS MIRON"]

if os.path.exists(ARQUIVO_CONSULTIVO):
    df = pd.read_csv(ARQUIVO_CONSULTIVO, sep=None, engine='python', dtype=str)
    df.columns = [str(c).upper().replace(' ', '_') for c in df.columns]
    
    df['SUPERVISOR'] = df['SUPERVISOR'].fillna('#N/D').str.upper().str.strip()
    df['BASE'] = df['BASE'].fillna('N/D').str.upper().str.strip()
    
    # Filtro: Remove #N/D e GRU para as contas
    df_valid = df[(df['SUPERVISOR'] != '#N/D') & (df['BASE'] != 'GRU')].copy()
    
    col_qtd = next((c for c in df_valid.columns if 'QTD' in c and 'PRODUTO' in c), 'QTD_PRODUTOS')
    df_valid['QTD'] = pd.to_numeric(df_valid[col_qtd].astype(str).str.replace(',', '.'), errors='coerce').fillna(0).astype(int)

    st.markdown(f'''<div class="topo-container">
        <div class="topo-esquerda">{logo_html}</div>
        <div class="topo-centro">PERFORMANCE CONSULTIVO</div>
        <div class="topo-direita"><a href="/" style="color:white; text-decoration:none; font-weight:bold;">🏠 HOME</a></div>
    </div>''', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    
    # ABC
    with c1:
        st.markdown(f'<div class="box-base"><div class="num-base">{df_valid[df_valid["BASE"]=="ABC"]["QTD"].sum()}</div><div style="font-size:18px; font-weight:bold; color: #2e7d32;">TOTAL BASE ABC</div></div>', unsafe_allow_html=True)
        for s in SUPS_ABC:
            val = df_valid[(df_valid["SUPERVISOR"].str.contains(s.split()[0])) & (df_valid["BASE"] == "ABC")]["QTD"].sum()
            st.markdown(f'''<div class="sup-card">
                <div class="sup-header"><div class="sup-name">📋 {s}</div><div class="badge-faltas" style="background:#e8f5e9; color:#2e7d32; border-color:#a5d6a7;">Alvo: 350</div></div>
                <div class="faltas-grid">
                    <div class="falta-box" style="background:#e8f5e9; border-color:#a5d6a7;"><div class="falta-label" style="color:#2e7d32;">TOTAL</div><div class="falta-value" style="color:#1b5e20;">{val}</div></div>
                    <div class="falta-box"><div class="falta-label">FALTA</div><div class="falta-value">{max(0, 350-val)}</div></div>
                    <div class="falta-box" style="background:#fff8e1; border-color:#ffe082;"><div class="falta-label" style="color:#b78103;">META/DIA</div><div class="falta-value" style="color:#b78103;">{round(max(0, 350-val)/20, 1)}</div></div>
                </div>
            </div>''', unsafe_allow_html=True)
            
    # SP
    with c2:
        st.markdown(f'<div class="box-base"><div class="num-base">{df_valid[df_valid["BASE"]=="SP"]["QTD"].sum()}</div><div style="font-size:18px; font-weight:bold; color: #00695c;">TOTAL BASE SÃO PAULO</div></div>', unsafe_allow_html=True)
        for s in SUPS_SP:
            val = df_valid[(df_valid["SUPERVISOR"].str.contains(s.split()[0])) & (df_valid["BASE"] == "SP")]["QTD"].sum()
            st.markdown(f'''<div class="sup-card">
                <div class="sup-header"><div class="sup-name">📋 {s}</div><div class="badge-faltas" style="background:#e0f2f1; color:#00695c; border-color:#b2dfdb;">Alvo: 350</div></div>
                <div class="faltas-grid">
                    <div class="falta-box" style="background:#e0f2f1; border-color:#b2dfdb;"><div class="falta-label" style="color:#00695c;">TOTAL</div><div class="falta-value" style="color:#004d40;">{val}</div></div>
                    <div class="falta-box"><div class="falta-label">FALTA</div><div class="falta-value">{max(0, 350-val)}</div></div>
                    <div class="falta-box" style="background:#fff8e1; border-color:#ffe082;"><div class="falta-label" style="color:#b78103;">META/DIA</div><div class="falta-value" style="color:#b78103;">{round(max(0, 350-val)/20, 1)}</div></div>
                </div>
            </div>''', unsafe_allow_html=True)

else: st.warning("Aguardando sincronização...")

# Finalização segura
time.sleep(60)
st.rerun()

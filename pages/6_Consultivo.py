import streamlit as st
import pandas as pd
import os
import unicodedata
from datetime import datetime, timedelta

# =========================================================================
# CONFIGURAÇÕES E CSS
# =========================================================================
st.set_page_config(page_title="Performance Consultivo", layout="wide")

ROOT_DIR = os.getcwd()
ARQUIVO_CONSULTIVO = os.path.join(ROOT_DIR, "consultivo_sincronizado.csv")

st.markdown("""<style>
    .stApp { background-color: #ffffff !important; }
    .topo-container { background: #003366; color: white; padding: 15px 30px; border-radius: 0 0 15px 15px; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; margin-bottom: 25px; }
    .topo-centro { font-size: 35px; font-weight: 900; text-align: center; }
    .box-base { background: #f8f9fa; border: 1px solid #ddd; padding: 20px; text-align: center; border-radius: 8px; margin-bottom: 25px; }
    .num-base { font-size: 85px; font-weight: 900; color: #111; }
    .sup-card { background: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .sup-header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 10px; border-bottom: 1px solid #eee; margin-bottom: 10px; }
    .sup-name { font-size: 24px; font-weight: 900; color: #333; }
    .badge-faltas { padding: 6px 12px; border-radius: 6px; font-weight: bold; border: 1px solid; }
    .faltas-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }
    .falta-box { border-radius: 6px; padding: 10px; text-align: center; border: 1px solid #eee; }
    .falta-label { font-size: 11px; font-weight: bold; color: #666; text-transform: uppercase; margin-bottom: 5px; }
    .falta-value { font-size: 28px; font-weight: 900; color: #333; }
</style>""", unsafe_allow_html=True)

# LÓGICA DE DADOS
SUPS_ABC = ["EDSON MARCO", "MARCOS ROBERTO", "NELSON"]
SUPS_SP = ["ALAN", "FRANCISCO", "JOAO CARLOS MIRON"]

def obter_nome_visual(n):
    n = n.upper()
    if 'FRANCISCO' in n: return "FRANCISCO"
    if 'MARCOS' in n: return "MARCOS ROBERTO"
    if 'EDSON' in n: return "EDSON MARCO"
    if 'JOAO' in n or 'MIRON' in n: return "JOÃO CARLOS"
    return n.split()[0]

if os.path.exists(ARQUIVO_CONSULTIVO):
    df = pd.read_csv(ARQUIVO_CONSULTIVO, sep=None, engine='python', dtype=str)
    df.columns = [str(c).upper().replace(' ', '_') for c in df.columns]
    
    df['SUPERVISOR'] = df['SUPERVISOR'].fillna('#N/D').str.upper().str.strip()
    df['BASE'] = df['BASE'].fillna('N/D').str.upper().str.strip()
    
    # Filtro: remove #N/D e GRU
    df_valid = df[(df['SUPERVISOR'] != '#N/D') & (df['BASE'] != 'GRU')].copy()
    
    col_qtd = next((c for c in df_valid.columns if 'QTD' in c and 'PRODUTO' in c), 'QTD_PRODUTOS')
    df_valid['QTD'] = pd.to_numeric(df_valid[col_qtd].astype(str).str.replace(',', '.'), errors='coerce').fillna(0).astype(int)

    st.markdown('<div class="topo-container"><div></div><div class="topo-centro">PERFORMANCE CONSULTIVO</div><div></div></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    
    # Função auxiliar para gerar os cards com cores dinâmicas
    def render_card(supervisor_nome, qtd_sup, cor_base, cor_secundaria, cor_texto_box):
        falta = max(0, 350 - qtd_sup)
        meta_dia = round(falta / 20, 1)
        st.markdown(f'''<div class="sup-card">
            <div class="sup-header">
                <div class="sup-name">📋 {obter_nome_visual(supervisor_nome)}</div>
                <div class="badge-faltas" style="background: {cor_base}; color: {cor_secundaria}; border-color: {cor_secundaria};">Alvo: 350</div>
            </div>
            <div class="faltas-grid">
                <div class="falta-box" style="background-color: {cor_base}; border-color: {cor_secundaria};">
                    <div class="falta-label" style="color: {cor_secundaria};">📦 TOTAL PROD</div>
                    <div class="falta-value" style="color: {cor_texto_box};">{qtd_sup}</div>
                </div>
                <div class="falta-box">
                    <div class="falta-label">📉 FALTA META</div>
                    <div class="falta-value">{falta}</div>
                </div>
                <div class="falta-box" style="background-color: #fff8e1; border-color: #ffe082;">
                    <div class="falta-label" style="color: #b78103;">🎯 META DIÁRIA</div>
                    <div class="falta-value" style="color: #b78103;">{meta_dia}</div>
                </div>
            </div>
        </div>''', unsafe_allow_html=True)

    with c1:
        st.markdown(f'<div class="box-base"><div class="num-base">{df_valid[df_valid["BASE"]=="ABC"]["QTD"].sum()}</div><div style="font-size:18px; font-weight:bold; color: #2e7d32;">TOTAL BASE ABC</div></div>', unsafe_allow_html=True)
        for s in SUPS_ABC:
            val = df_valid[(df_valid["SUPERVISOR"].str.contains(s.split()[0])) & (df_valid["BASE"] == "ABC")]["QTD"].sum()
            render_card(s, val, "#e8f5e9", "#2e7d32", "#1b5e20")
            
    with c2:
        st.markdown(f'<div class="box-base"><div class="num-base">{df_valid[df_valid["BASE"]=="SP"]["QTD"].sum()}</div><div style="font-size:18px; font-weight:bold; color: #00695c;">TOTAL BASE SÃO PAULO</div></div>', unsafe_allow_html=True)
        for s in SUPS_SP:
            val = df_valid[(df_valid["SUPERVISOR"].str.contains(s.split()[0])) & (df_valid["BASE"] == "SP")]["QTD"].sum()
            render_card(s, val, "#e0f2f1", "#00695c", "#004d40")

else: st.warning("Aguardando sincronização...")
time.sleep(60); st.rerun()

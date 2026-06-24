import streamlit as st
import pandas as pd
import os
import time
import base64
import unicodedata
from datetime import datetime, timedelta

# =========================================================================
# CONFIGURAÇÕES E CSS (LAYOUT ORIGINAL RESTAURADO)
# =========================================================================
st.set_page_config(page_title="Performance Consultivo", layout="wide")

ROOT_DIR = os.getcwd()
ARQUIVO_CONSULTIVO = os.path.join(ROOT_DIR, "consultivo_sincronizado.csv")

st.markdown("""<style>
    .stApp { background-color: #ffffff !important; }
    .topo-container { background: #003366; color: white; padding: 15px 30px; border-radius: 0 0 15px 15px; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; margin-bottom: 25px; }
    .topo-centro { font-size: 35px; font-weight: 900; text-align: center; }
    
    /* Cores das Bases */
    .box-base-abc { background: #e8f5e9; border-left: 10px solid #2e7d32; padding: 20px; text-align: center; border-radius: 8px; margin-bottom: 25px; }
    .box-base-sp { background: #e0f2f1; border-left: 10px solid #00897b; padding: 20px; text-align: center; border-radius: 8px; margin-bottom: 25px; }
    .num-base { font-size: 70px; font-weight: 900; color: #111; }
    
    /* Cards de Supervisor */
    .sup-card { background: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .sup-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 10px; }
    .sup-name { font-size: 20px; font-weight: 900; color: #333; }
    .badge-alvo { background: #f0f0f0; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    
    .faltas-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }
    .falta-box { background-color: #f8f9fa; border: 1px solid #eee; border-radius: 6px; padding: 8px; text-align: center; }
    .falta-label { font-size: 10px; font-weight: bold; color: #666; text-transform: uppercase; margin-bottom: 4px; }
    .falta-value { font-size: 22px; font-weight: 900; color: #333; }
</style>""", unsafe_allow_html=True)

# LÓGICA DE DADOS
SUPS_ABC = ["EDSON MARCO", "MARCOS ROBERTO", "NELSON"]
SUPS_SP = ["ALAN", "FRANCISCO", "JOAO CARLOS MIRON"]

if os.path.exists(ARQUIVO_CONSULTIVO):
    df = pd.read_csv(ARQUIVO_CONSULTIVO, sep=None, engine='python', dtype=str)
    df.columns = [str(c).upper().replace(' ', '_') for c in df.columns]
    
    # Padronização e Filtros (Aqui removemos os #N/D e GRU antes de somar)
    df['SUPERVISOR'] = df['SUPERVISOR'].fillna('#N/D').str.upper().str.strip()
    df['BASE'] = df['BASE'].fillna('N/D').str.upper().str.strip()
    
    # 🔥 A MÁGICA: O df_valid só tem dados limpos
    df_valid = df[(df['SUPERVISOR'] != '#N/D') & (df['BASE'] != 'GRU')].copy()
    
    col_qtd = next((c for c in df_valid.columns if 'QTD' in c and 'PRODUTO' in c), 'QTD_PRODUTOS')
    df_valid['QTD'] = pd.to_numeric(df_valid[col_qtd].astype(str).str.replace(',', '.'), errors='coerce').fillna(0).astype(int)

    st.markdown('<div class="topo-container"><div></div><div class="topo-centro">PERFORMANCE CONSULTIVO</div><div></div></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    
    # Coluna ABC (Verde)
    with c1:
        st.markdown(f'<div class="box-base-abc"><div class="num-base">{df_valid[df_valid["BASE"]=="ABC"]["QTD"].sum()}</div><div style="font-size:18px; font-weight:bold;">TOTAL BASE ABC</div></div>', unsafe_allow_html=True)
        for s in SUPS_ABC:
            val = df_valid[(df_valid["SUPERVISOR"].str.contains(s.split()[0])) & (df_valid["BASE"] == "ABC")]["QTD"].sum()
            st.markdown(f'''<div class="sup-card">
                <div class="sup-header"><div class="sup-name">{s}</div><div class="badge-alvo">Alvo: 350</div></div>
                <div class="faltas-grid">
                    <div class="falta-box"><div class="falta-label">Total Prod</div><div class="falta-value">{val}</div></div>
                    <div class="falta-box"><div class="falta-label">Falta Meta</div><div class="falta-value">{max(0, 350-val)}</div></div>
                    <div class="falta-box"><div class="falta-label">Meta/Dia</div><div class="falta-value">{round(max(0, 350-val)/20, 1)}</div></div>
                </div>
            </div>''', unsafe_allow_html=True)
            
    # Coluna SP (Teal)
    with c2:
        st.markdown(f'<div class="box-base-sp"><div class="num-base">{df_valid[df_valid["BASE"]=="SP"]["QTD"].sum()}</div><div style="font-size:18px; font-weight:bold;">TOTAL BASE SÃO PAULO</div></div>', unsafe_allow_html=True)
        for s in SUPS_SP:
            val = df_valid[(df_valid["SUPERVISOR"].str.contains(s.split()[0])) & (df_valid["BASE"] == "SP")]["QTD"].sum()
            st.markdown(f'''<div class="sup-card">
                <div class="sup-header"><div class="sup-name">{s}</div><div class="badge-alvo">Alvo: 350</div></div>
                <div class="faltas-grid">
                    <div class="falta-box"><div class="falta-label">Total Prod</div><div class="falta-value">{val}</div></div>
                    <div class="falta-box"><div class="falta-label">Falta Meta</div><div class="falta-value">{max(0, 350-val)}</div></div>
                    <div class="falta-box"><div class="falta-label">Meta/Dia</div><div class="falta-value">{round(max(0, 350-val)/20, 1)}</div></div>
                </div>
            </div>''', unsafe_allow_html=True)

else: st.warning("Aguardando sincronização...")
time.sleep(60); st.rerun()

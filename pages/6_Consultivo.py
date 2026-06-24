import streamlit as st
import pandas as pd
import os
import time
import base64

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
    
    /* Estilo dos Totais */
    .box-base-abc { background: #e8f5e9; border: 2px solid #a5d6a7; padding: 20px; text-align: center; border-radius: 8px; margin-bottom: 25px; }
    .box-base-sp { background: #e0f2f1; border: 2px solid #b2dfdb; padding: 20px; text-align: center; border-radius: 8px; margin-bottom: 25px; }
    .num-base { font-size: 85px; font-weight: 900; color: #111; }
    
    /* Estilo dos Cards */
    .sup-card { background: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .sup-header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 10px; border-bottom: 1px solid #eee; margin-bottom: 10px; }
    .sup-name { font-size: 20px; font-weight: 900; color: #333; }
    .badge-faltas { padding: 4px 8px; border-radius: 6px; font-size: 12px; font-weight: bold; border: 1px solid; }
    .faltas-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }
    .falta-box { border-radius: 6px; padding: 10px; text-align: center; border: 1px solid #eee; }
    .falta-label { font-size: 9px; font-weight: bold; text-transform: uppercase; margin-bottom: 4px; }
    .falta-value { font-size: 22px; font-weight: 900; }
</style>""", unsafe_allow_html=True)

# LÓGICA DE DADOS
SUPS_ABC = ["EDSON MARCO", "MARCOS ROBERTO", "NELSON"]
SUPS_SP = ["ALAN", "FRANCISCO", "JOAO CARLOS MIRON"]

def obter_nome_visual(n):
    return n.split()[0] if n else "N/D"

if os.path.exists(ARQUIVO_CONSULTIVO):
    try:
        df = pd.read_csv(ARQUIVO_CONSULTIVO, sep=None, engine='python', dtype=str)
        df.columns = [str(c).upper().replace(' ', '_') for c in df.columns]
        
        df['SUPERVISOR'] = df['SUPERVISOR'].fillna('#N/D').str.upper().str.strip()
        df['BASE'] = df['BASE'].fillna('N/D').str.upper().str.strip()
        
        df_valid = df[(df['SUPERVISOR'] != '#N/D') & (df['BASE'] != 'GRU')].copy()
        
        col_qtd = next((c for c in df_valid.columns if 'QTD' in c and 'PRODUTO' in c), 'QTD_PRODUTOS')
        df_valid['QTD'] = pd.to_numeric(df_valid[col_qtd].astype(str).str.replace(',', '.'), errors='coerce').fillna(0).astype(int)

        st.markdown('<div class="topo-container"><div></div><div class="topo-centro">PERFORMANCE CONSULTIVO</div><div></div></div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        
        # --- COLUNA ABC ---
        with c1:
            st.markdown(f'<div class="box-base-abc"><div class="num-base">{df_valid[df_valid["BASE"]=="ABC"]["QTD"].sum()}</div><div style="font-size:18px; font-weight:bold; color: #2e7d32;">TOTAL BASE ABC</div></div>', unsafe_allow_html=True)
            for s in SUPS_ABC:
                val = df_valid[(df_valid["SUPERVISOR"].str.contains(s.split()[0])) & (df_valid["BASE"] == "ABC")]["QTD"].sum()
                falta = max(0, 350 - val)
                meta_dia = round(falta / 20, 1)
                
                st.markdown(f'''<div class="sup-card">
                    <div class="sup-header"><div class="sup-name">📋 {obter_nome_visual(s)}</div><div class="badge-faltas" style="background: #e8f5e9; color: #2e7d32; border-color: #a5d6a7;">Alvo: 350</div></div>
                    <div class="faltas-grid">
                        <div class="falta-box" style="background-color: #e8f5e9; border-color: #a5d6a7;"><div class="falta-label" style="color: #2e7d32;">📦 TOTAL PROD</div><div class="falta-value" style="color: #1b5e20;">{val}</div></div>
                        <div class="falta-box"><div class="falta-label">📉 FALTA</div><div class="falta-value">{falta}</div></div>
                        <div class="falta-box" style="background-color: #fff8e1; border-color: #ffe082;"><div class="falta-label" style="color: #b78103;">🎯 META DIÁRIA</div><div class="falta-value" style="color: #b78103;">{meta_dia}</div></div>
                    </div>
                </div>''', unsafe_allow_html=True)
                
        # --- COLUNA SP ---
        with c2:
            st.markdown(f'<div class="box-base-sp"><div class="num-base">{df_valid[df_valid["BASE"]=="SP"]["QTD"].sum()}</div><div style="font-size:18px; font-weight:bold; color: #00695c;">TOTAL BASE SÃO PAULO</div></div>', unsafe_allow_html=True)
            for s in SUPS_SP:
                val = df_valid[(df_valid["SUPERVISOR"].str.contains(s.split()[0])) & (df_valid["BASE"] == "SP")]["QTD"].sum()
                falta = max(0, 350 - val)
                meta_dia = round(falta / 20, 1)
                
                st.markdown(f'''<div class="sup-card">
                    <div class="sup-header"><div class="sup-name">📋 {obter_nome_visual(s)}</div><div class="badge-faltas" style="background: #e0f2f1; color: #00695c; border-color: #b2dfdb;">Alvo: 350</div></div>
                    <div class="faltas-grid">
                        <div class="falta-box" style="background-color: #e0f2f1; border-color: #b2dfdb;"><div class="falta-label" style="color: #00695c;">📦 TOTAL PROD</div><div class="falta-value" style="color: #004d40;">{val}</div></div>
                        <div class="falta-box"><div class="falta-label">📉 FALTA</div><div class="falta-value">{falta}</div></div>
                        <div class="falta-box" style="background-color: #fff8e1; border-color: #ffe082;"><div class="falta-label" style="color: #b78103;">🎯 META DIÁRIA</div><div class="falta-value" style="color: #b78103;">{meta_dia}</div></div>
                    </div>
                </div>''', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Erro ao processar dados: {e}")
else: 
    st.warning("Aguardando sincronização...")

# Finalização (fora do if para evitar erro de escopo)
time.sleep(60)
st.rerun()

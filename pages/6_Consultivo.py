import streamlit as st
import pandas as pd
import os
import time
import unicodedata

# Configuração de Página
st.set_page_config(page_title="Performance Consultivo", layout="wide")

ROOT_DIR = os.getcwd()
ARQUIVO_CONSULTIVO = os.path.join(ROOT_DIR, "consultivo_sincronizado.csv")

# CSS IDÊNTICO AO SEU LAYOUT ORIGINAL
st.markdown("""<style>
    .stApp { background-color: #ffffff !important; }
    .topo-container { background: #003366; color: white; padding: 20px; border-radius: 15px; margin-bottom: 25px; text-align: center; font-size: 40px; font-weight: 900; }
    .box-base-abc { background: #e8f5e9; border: 2px solid #a5d6a7; padding: 20px; text-align: center; border-radius: 8px; margin-bottom: 25px; }
    .box-base-sp { background: #e0f2f1; border: 2px solid #b2dfdb; padding: 20px; text-align: center; border-radius: 8px; margin-bottom: 25px; }
    .num-base { font-size: 85px; font-weight: 900; color: #111; }
    .sup-card { background: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .sup-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 10px; }
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
    return n.split()[0] if n else "N/D"

if os.path.exists(ARQUIVO_CONSULTIVO):
    df = pd.read_csv(ARQUIVO_CONSULTIVO, sep=None, engine='python', dtype=str)
    df.columns = [str(c).upper().replace(' ', '_') for c in df.columns]
    
    df['SUPERVISOR'] = df['SUPERVISOR'].fillna('#N/D').str.upper().str.strip()
    df['BASE'] = df['BASE'].fillna('N/D').str.upper().str.strip()
    
    # 🔥 A MÁGICA: Filtramos #N/D e GRU aqui. Isso limpa TUDO.
    df_valid = df[(df['SUPERVISOR'] != '#N/D') & (df['BASE'] != 'GRU')].copy()
    
    col_qtd = next((c for c in df_valid.columns if 'QTD' in c and 'PRODUTO' in c), 'QTD_PRODUTOS')
    df_valid['QTD'] = pd.to_numeric(df_valid[col_qtd].astype(str).str.replace(',', '.'), errors='coerce').fillna(0).astype(int)

    st.markdown('<div class="topo-container">PERFORMANCE CONSULTIVO</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    
    # --- BASE ABC ---
    with c1:
        st.markdown(f'<div class="box-base-abc"><div class="num-base">{df_valid[df_valid["BASE"]=="ABC"]["QTD"].sum()}</div><div style="font-size:18px; font-weight:bold; color: #2e7d32;">TOTAL BASE ABC</div></div>', unsafe_allow_html=True)
        for s in SUPS_ABC:
            qtd_sup = df_valid[(df_valid["SUPERVISOR"].str.contains(s.split()[0])) & (df_valid["BASE"] == "ABC")]["QTD"].sum()
            falta_individual = max(0, 350 - qtd_sup)
            ritmo_diario_individual = round(falta_individual / 20, 1)
            
            st.markdown(f'''<div class="sup-card">
                <div class="sup-header">
                    <div class="sup-name">📋 {obter_nome_visual(s)}</div>
                    <div class="badge-faltas" style="background: #e8f5e9; color: #2e7d32; border-color: #a5d6a7;">Alvo: 350</div>
                </div>
                <div class="faltas-grid">
                    <div class="falta-box" style="background-color: #e8f5e9; border-color: #a5d6a7;">
                        <div class="falta-label" style="color: #2e7d32;">📦 TOTAL PRODUTOS</div>
                        <div class="falta-value" style="color: #1b5e20;">{qtd_sup}</div>
                    </div>
                    <div class="falta-box">
                        <div class="falta-label">📉 FALTA PARA META</div>
                        <div class="falta-value">{falta_individual}</div>
                    </div>
                    <div class="falta-box" style="background-color: #fff8e1; border-color: #ffe082;">
                        <div class="falta-label" style="color: #b78103;">🎯 META DIÁRIA</div>
                        <div class="falta-value" style="color: #b78103;">{ritmo_diario_individual}</div>
                    </div>
                </div>
            </div>''', unsafe_allow_html=True)
            
    # --- BASE SP ---
    with c2:
        st.markdown(f'<div class="box-base-sp"><div class="num-base">{df_valid[df_valid["BASE"]=="SP"]["QTD"].sum()}</div><div style="font-size:18px; font-weight:bold; color: #00695c;">TOTAL BASE SÃO PAULO</div></div>', unsafe_allow_html=True)
        for s in SUPS_SP:
            qtd_sup = df_valid[(df_valid["SUPERVISOR"].str.contains(s.split()[0])) & (df_valid["BASE"] == "SP")]["QTD"].sum()
            falta_individual = max(0, 350 - qtd_sup)
            ritmo_diario_individual = round(falta_individual / 20, 1)
            
            st.markdown(f'''<div class="sup-card">
                <div class="sup-header">
                    <div class="sup-name">📋 {obter_nome_visual(s)}</div>
                    <div class="badge-faltas" style="background: #e0f2f1; color: #00695c; border-color: #b2dfdb;">Alvo: 350</div>
                </div>
                <div class="faltas-grid">
                    <div class="falta-box" style="background-color: #e0f2f1; border-color: #b2dfdb;">
                        <div class="falta-label" style="color: #00695c;">📦 TOTAL PRODUTOS</div>
                        <div class="falta-value" style="color: #004d40;">{qtd_sup}</div>
                    </div>
                    <div class="falta-box">
                        <div class="falta-label">📉 FALTA PARA META</div>
                        <div class="falta-value">{falta_individual}</div>
                    </div>
                    <div class="falta-box" style="background-color: #fff8e1; border-color: #ffe082;">
                        <div class="falta-label" style="color: #b78103;">🎯 META DIÁRIA</div>
                        <div class="falta-value" style="color: #b78103;">{ritmo_diario_individual}</div>
                    </div>
                </div>
            </div>''', unsafe_allow_html=True)

else: st.warning("Aguardando sincronização...")
time.sleep(60); st.rerun()

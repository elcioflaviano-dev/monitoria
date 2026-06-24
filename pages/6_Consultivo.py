import streamlit as st
import pandas as pd
import os
import time
import base64
import calendar
import unicodedata
from datetime import datetime, timedelta

# =========================================================================
# CONFIGURAÇÕES DA PÁGINA
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

# =========================================================================
# ESTILOS (LAYOUT ORIGINAL)
# =========================================================================
st.markdown("""<style>
    .stApp { background-color: #ffffff !important; }
    .topo-container { background: #003366; color: white; padding: 0px 30px; border-radius: 0 0 15px 15px; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; margin-bottom: 25px; height: 100px; }
    .topo-centro { font-size: 45px; font-weight: 900; text-align: center; }
    .box-base { background: #e8f5e9; border-left: 10px solid #2e7d32; padding: 15px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.15); margin-bottom: 25px; }
    .box-base-sp { background: #e0f2f1; border-left: 10px solid #00897b; padding: 15px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.15); margin-bottom: 25px; }
    .num-base { font-size: 85px; font-weight: 900; color: #111; }
    .sup-card { background: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .sup-header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 10px; border-bottom: 1px solid #eee; margin-bottom: 10px; }
    .sup-name { font-size: 24px; font-weight: 900; color: #333; }
    .badge-faltas { background: #e8f5e9; color: #2e7d32; padding: 6px 12px; border-radius: 6px; font-weight: bold; border: 1px solid #a5d6a7; }
    .faltas-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }
    .falta-box { background-color: #f8f9fa; border: 1px solid #eee; border-radius: 6px; padding: 10px; text-align: center; }
    .falta-label { font-size: 11px; font-weight: bold; color: #666; text-transform: uppercase; margin-bottom: 5px; }
    .falta-value { font-size: 28px; font-weight: 900; color: #333; }
</style>""", unsafe_allow_html=True)

# =========================================================================
# LÓGICA DE DADOS (FILTRO ANTI-#N/D)
# =========================================================================
SUPS_ABC = ["EDSON MARCO", "MARCOS ROBERTO", "NELSON"]
SUPS_SP = ["ALAN", "FRANCISCO", "JOAO CARLOS MIRON"]

if os.path.exists(ARQUIVO_CONSULTIVO):
    df = pd.read_csv(ARQUIVO_CONSULTIVO, sep=None, engine='python', dtype=str)
    df.columns = [str(c).upper().replace(' ', '_') for c in df.columns]
    
    # Tratamento de Nulos e limpeza
    df['SUPERVISOR'] = df['SUPERVISOR'].fillna('#N/D').str.upper().str.strip()
    df['BASE'] = df['BASE'].fillna('N/D').str.upper().str.strip()
    
    # 🔥 A MÁGICA: Filtramos #N/D aqui. df_valid contém apenas dados dos supervisores
    df_valid = df[df['SUPERVISOR'] != '#N/D'].copy()
    
    col_qtd = next((c for c in df_valid.columns if 'QTD' in c and 'PRODUTO' in c), 'QTD_PRODUTOS')
    df_valid['QTD'] = pd.to_numeric(df_valid[col_qtd].astype(str).str.replace(',', '.'), errors='coerce').fillna(0).astype(int)

    st.markdown(f'''<div class="topo-container">
        <div class="topo-esquerda">{logo_html}</div>
        <div class="topo-centro">PERFORMANCE CONSULTIVO</div>
        <div class="topo-direita"><a href="/" style="color:white; text-decoration:none; font-weight:bold;">🏠 HOME</a></div>
    </div>''', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="box-base"><div class="num-base">{df_valid[df_valid["BASE"]=="ABC"]["QTD"].sum()}</div><div style="font-size:18px; font-weight:bold;">TOTAL BASE ABC</div></div>', unsafe_allow_html=True)
        for s in SUPS_ABC:
            val = df_valid[(df_valid["SUPERVISOR"].str.contains(s.split()[0])) & (df_valid["BASE"] == "ABC")]["QTD"].sum()
            st.markdown(f'''<div class="sup-card">
                <div class="sup-header"><div class="sup-name">{s}</div><div class="badge-faltas">Alvo: 350</div></div>
                <div class="faltas-grid">
                    <div class="falta-box"><div class="falta-label">Total</div><div class="falta-value">{val}</div></div>
                    <div class="falta-box"><div class="falta-label">Falta</div><div class="falta-value">{max(0, 350-val)}</div></div>
                    <div class="falta-box"><div class="falta-label">Meta/Dia</div><div class="falta-value">{round(max(0, 350-val)/20, 1)}</div></div>
                </div>
            </div>''', unsafe_allow_html=True)
            
    with c2:
        st.markdown(f'<div class="box-base-sp"><div class="num-base">{df_valid[df_valid["BASE"]=="SP"]["QTD"].sum()}</div><div style="font-size:18px; font-weight:bold;">TOTAL BASE SP</div></div>', unsafe_allow_html=True)
        for s in SUPS_SP:
            val = df_valid[(df_valid["SUPERVISOR"].str.contains(s.split()[0])) & (df_valid["BASE"] == "SP")]["QTD"].sum()
            st.markdown(f'''<div class="sup-card">
                <div class="sup-header"><div class="sup-name">{s}</div><div class="badge-faltas">Alvo: 350</div></div>
                <div class="faltas-grid">
                    <div class="falta-box"><div class="falta-label">Total</div><div class="falta-value">{val}</div></div>
                    <div class="falta-box"><div class="falta-label">Falta</div><div class="falta-value">{max(0, 350-val)}</div></div>
                    <div class="falta-box"><div class="falta-label">Meta/Dia</div><div class="falta-value">{round(max(0, 350-val)/20, 1)}</div></div>
                </div>
            </div>''', unsafe_allow_html=True)

else: st.warning("Aguardando sincronização...")
time.sleep(60); st.rerun()

import streamlit as st
import pandas as pd
from urllib.parse import quote, unquote

# 1. Configuração da página
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# 2. Carregar CSS de forma ultra isolada
css_conteudo = ""
try:
    with open("style.css", "r") as f:
        css_conteudo = f.read()
except:
    pass

if css_conteudo:
    st.markdown(f"<style>{css_conteudo}</style>", unsafe_allow_html=True)

# CSS interno sem f-string
st.markdown("""
    <style>
    .item-pendente-tv { background-color: #ffe6e6 !important; border: 2px solid #ff9999 !important; border-radius: 6px; padding: 6px 12px !important; margin-bottom: 6px !important; display: flex !important; justify-content: space-between !important; align-items: center !important; width: 100% !important; }
    .tecnico-nome-tv { color: #b30000 !important; font-size: 14px !important; font-weight: 900 !important; text-transform: uppercase !important; }
    .contrato-numero-tv { background-color: #b30000 !important; color: white !important; padding: 3px 10px !important; border-radius: 4px !important; font-weight: bold !important; font-size: 14px !important; }
    .no-pendente-tv { color: #2e7d32; font-weight: bold; font-size: 14px; text-align: center; padding: 5px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="font-size: 38px; font-weight: 900; color: #b30000; text-align: center; margin-top: 25px; margin-bottom: 10px;">⚠️ TEC1 - PENDENTES</h1>', unsafe_allow_html=True)

# === MÓDULO DE CARGA ===
def carregar_dados_sheets():
    try:
        url = st.secrets["public_gsheets_url"]
        if "/edit" in url:
            csv_url = url.split("/edit")[0] + "/gviz/tq?tqx=out:csv"
            if "gid=" in url:
                gid = url.split("gid=")[1].split("&")[0]
                csv_url += "&gid=" + gid
        else:
            csv_url = url

        df_sheets = pd.read_csv(csv_url)
        df_sheets.columns = df_sheets.columns.str.strip()
        
        colunas_mapeadas = {}
        for col in df_sheets.columns:
            col_upper = col.upper()
            if "SUPERVISOR" in col_upper: colunas_mapeadas[col] = "SUPERVISOR"
            elif "JANELA" in col_upper: colunas_mapeadas[col] = "JANELA_SERVICO"

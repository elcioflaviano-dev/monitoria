import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

# [MANTENHA A LÓGICA DE HERANÇA E REFRESH QUE JÁ TEM FUNCIONANDO]
# ... (O código de sincronização que já usamos permanece igual) ...

# CSS DE ESTILIZAÇÃO DOS NOVOS BLOCOS DE INDICADORES
st.markdown("""
    <style>
    .falta-box { background-color: #ffebee; border: 1px solid #ffcdd2; border-radius: 6px; padding: 10px 5px; text-align: center; margin-bottom: 5px; }
    .falta-label { font-size: 11px; font-weight: bold; color: #c62828; text-transform: uppercase; margin-bottom: 4px; }
    .falta-value { font-size: 24px; font-weight: 900; color: #b30000; line-height: 1; }
    .section-base-title { background-color: #005088; color: white; padding: 8px 15px; border-radius: 4px; font-size: 16px; font-weight: bold; margin-top: 20px; margin-bottom: 12px; }
    </style>
""", unsafe_allow_html=True)

# ... (Mantenha o resto da lógica do painel principal até chegar no fim das bases) ...

# --- INSERIR ESTE BLOCO ABAIXO, NO FINAL DO FICHEIRO ---
st.markdown("<br><hr style='border: 2px solid #cc6600;'><br>", unsafe_allow_html=True)
st.markdown('<h2 style="text-align:center; color:#cc6600;">🚨 TOTAL DE FALTAS DE INDICADORES (RESUMO)</h2>', unsafe_allow_html=True)

df_dash = st.session_state.get('df_rota_ativa', None)
if df_dash is not None:
    # 1. Identificar colunas
    col_nr35 = next((c for c in reversed(df_dash.columns) if 'NR35' in c.upper()), None)
    col_cert = next((c for c in reversed(df_dash.columns) if 'CERTID' in c.upper()), None)
    col_bst  = next((c for c in reversed(df_dash.columns) if 'BST' in c.upper()), None)
    
    # 2. Filtrar contratos produtivos únicos
    df_prod = df_dash[df_dash['Status_Atividade_Upper'].str.contains('CONCL|PRODUTIVO|INIC', na=False)].drop_duplicates(subset=['Contrato'])
    
    # 3. Calcular faltas
    df_prod['FALTA_NR35'] = df_prod[col_nr35].fillna('').str.upper().str.contains('NÃO|NAO|FALTA', na=False).astype(int) if col_nr35 else 0
    df_prod['FALTA_CERT'] = df_prod[col_cert].fillna('').str.upper().str.contains('NÃO|NAO|FALTA', na=False).astype(int) if col_cert else 0
    df_prod['FALTA_BST'] = df_prod[col_bst].fillna('').str.upper().str.contains('NÃO|NAO|FALTA', na=False).astype(int) if col_bst else 0
    
    # 4. Agrupar por Supervisor (usando a mesma lógica de normalização que já temos)
    matriz = df_prod.groupby('SUPERVISOR')[['FALTA_NR35', 'FALTA_CERT', 'FALTA_BST']].sum().reset_index()
    
    # 5. Exibir
    cols = st.columns(3) # Exibe 3 supervisores por linha
    for i, supervisor in enumerate(sorted(matriz['SUPERVISOR'].unique())):
        dados = matriz[matriz['SUPERVISOR'] == supervisor].iloc[0]
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"**{supervisor}**")
                m1, m2, m3 = st.columns(3)
                m1.markdown(f'<div class="falta-box"><div class="falta-label">NR35</div><div class="falta-value">{int(dados["FALTA_NR35"])}</div></div>', unsafe_allow_html=True)
                m2.markdown(f'<div class="falta-box"><div class="falta-label">CERT</div><div class="falta-value">{int(dados["FALTA_CERT"])}</div></div>', unsafe_allow_html=True)
                m3.markdown(f'<div class="falta-box"><div class="falta-label">BST</div><div class="falta-value">{int(dados["FALTA_BST"])}</div></div>', unsafe_allow_html=True)

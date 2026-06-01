import streamlit as st
import pandas as pd
import os
import time

# 1. Configuração da página ampla para a TV
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

# 🔄 HERANÇA INTELIGENTE
if ('df_rota_ativa' not in st.session_state or st.session_state['df_rota_ativa'] is None) and os.path.exists(ARQUIVO_ROTA_DISCO):
    try: 
        st.session_state['df_rota_ativa'] = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    except: 
        pass

st.markdown("""
    <style>
        .title-abc-sp { font-size: 26px !important; font-weight: 800 !important; color: #005088; text-align: center; border-bottom: 3px solid #008080; }
        .item-linha-tec { font-size: 20px; padding: 10px 15px; border-bottom: 1px solid #eee; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="font-size: 36px; font-weight: 900; color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

df_master = st.session_state.get('df_rota_ativa', None)

if df_master is not None and not df_master.empty:
    df = df_master.copy()
    
    # Índice das colunas baseado na foto: [3, 4, 13, 23, 119]
    # LOGIN (3), STATUS (4), JANELA (13), TIPO (23), SUPERVISOR (119)
    df_clean = df.iloc[:, [3, 4, 13, 23, 119]].copy()
    df_clean.columns = ['LOGIN', 'STATUS', 'JANELA', 'TIPO', 'SUPERVISOR']
    
    # 🔥 BLINDAGEM: Força a conversão para String explícita antes de qualquer operação .str
    df_clean['STATUS'] = df_clean['STATUS'].astype(str)
    df_clean['TIPO'] = df_clean['TIPO'].astype(str)
    
    # Filtro: Contém "Na Base" em TIPO e "Pendente" em STATUS (case insensitive)
    df_tela = df_clean[
        df_clean['TIPO'].str.contains('NA BASE', case=False, na=False) & 
        df_clean['STATUS'].str.contains('PENDENTE', case=False, na=False)
    ].copy()

    if df_tela.empty:
        st.success("🎉 100% da equipe liberada para a rua! Nenhum técnico com 'Na Base' pendente.")
    else:
        # Lógica de divisão regional
        df_tela['SUP'] = df_tela['SUPERVISOR'].fillna('MAICON').str.upper()
        
        cond_sp = df_tela['SUP'].str.contains('FRANCISCO|ALAN', na=False)
        df_sp = df_tela[cond_sp].drop_duplicates(subset=['LOGIN'])
        df_abc = df_tela[~cond_sp].drop_duplicates(subset=['LOGIN'])

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="title-abc-sp">ABC / GUARULHOS</div>', unsafe_allow_html=True)
            for _, row in df_abc.iterrows():
                st.markdown(f'<div class="item-linha-tec">🏃‍♂️ <b>{row["LOGIN"]}</b> <span style="float:right">Janela: {row["JANELA"]}</span></div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="title-abc-sp">SÃO PAULO (SP)</div>', unsafe_allow_html=True)
            for _, row in df_sp.iterrows():
                st.markdown(f'<div class="item-linha-tec">🏃‍♂️ <b>{row["LOGIN"]}</b> <span style="float:right">Janela: {row["JANELA"]}</span></div>', unsafe_allow_html=True)
else: 
    st.warning("👈 Por favor, insira os arquivos de rota na página inicial.")

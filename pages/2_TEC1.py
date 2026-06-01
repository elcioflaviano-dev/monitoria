import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if ('df_rota_ativa' not in st.session_state or st.session_state['df_rota_ativa'] is None) and os.path.exists(ARQUIVO_ROTA_DISCO):
    try: st.session_state['df_rota_ativa'] = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    except: pass

st.markdown('<h1 style="font-size: 42px; font-weight: 900; color: #006677; text-align: center;">TEC1</h1>', unsafe_allow_html=True)

df_master = st.session_state.get('df_rota_ativa', None)

if df_master is not None and not df_master.empty:
    df = df_master.copy()
    col_supervisor = 'SUPERVISOR' if 'SUPERVISOR' in df.columns else 'Supervisor'
    
    # Lógica de Padronização que você queria
    def padronizar_supervisor(nome):
        nome = str(nome).upper().strip()
        if 'ALAN' in nome or 'FRANCISCO' in nome: return 'SP'
        return 'ABC'

    # Cria a coluna que o código usa para agrupar
    df['SUPERVISOR_MOSTRAR'] = df[col_supervisor].apply(padronizar_supervisor)
    
    # Criamos a coluna original para exibir o nome do supervisor real no agrupamento
    df['NOME_SUPERVISOR_REAL'] = df[col_supervisor].fillna('SEM SUPERVISOR')

    # Agrupa pelo nome real, mas filtra pela região que criamos
    def exibir_coluna(coluna_st, filtro_regiao, titulo):
        with coluna_st:
            st.markdown(f'<div style="font-size:18px; font-weight: bold; text-align: center;">{titulo}</div>', unsafe_allow_html=True)
            df_subset = df[filtro_regiao]
            # Agrupa pelo NOME_SUPERVISOR_REAL para aparecer o nome correto
            matriz = df_subset.groupby('NOME_SUPERVISOR_REAL')[['P_COUNT', 'R_COUNT', 'I_COUNT']].sum().reset_index()
            for _, row in matriz.iterrows():
                with st.container(border=True):
                    st.markdown(f"📋 **{row['NOME_SUPERVISOR_REAL']}**")
                    m1, m2, m3 = st.columns(3)
                    m1.metric("🔴 PENDENTES", int(row['P_COUNT']))
                    m2.metric("🟣 EM ROTA", int(row['R_COUNT']))
                    m3.metric("🟢 INICIADO", int(row['I_COUNT']))

    col_abc, col_sp = st.columns(2)
    exibir_coluna(col_abc, df['SUPERVISOR_MOSTRAR'] == 'ABC', "ABC")
    exibir_coluna(col_sp, df['SUPERVISOR_MOSTRAR'] == 'SP', "SÃO PAULO (SP)")

else:
    st.warning("👈 Por favor, faça o upload dos arquivos de rota.")

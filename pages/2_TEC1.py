import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta

# Configurações iniciais
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if ('df_rota_ativa' not in st.session_state or st.session_state['df_rota_ativa'] is None) and os.path.exists(ARQUIVO_ROTA_DISCO):
    try: st.session_state['df_rota_ativa'] = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    except: pass

if 'df_rota_ativa' in st.session_state and st.session_state['df_rota_ativa'] is not None:
    if "last_refresh_tec1" not in st.session_state: st.session_state["last_refresh_tec1"] = time.time()
    if time.time() - st.session_state["last_refresh_tec1"] > 30:
        st.session_state["last_refresh_tec1"] = time.time()
        st.rerun()

st.markdown('<h1 style="font-size: 42px; font-weight: 900; color: #006677; text-align: center; margin-top: 25px; margin-bottom: 5px;">TEC1</h1>', unsafe_allow_html=True)

df_master = st.session_state.get('df_rota_ativa', None)

if df_master is not None and not df_master.empty:
    df = df_master.copy()
    df.columns = [str(c).strip() for c in df.columns]
    
    col_tecnico_check = 'Recurso' if 'Recurso' in df.columns else df.columns[0]
    col_status_real = 'Status da Atividade' if 'Status da Atividade' in df.columns else 'STATUS_ATIVIDADE'
    col_tipo_real = 'Tipo de Atividade' if 'Tipo de Atividade' in df.columns else df.columns[-1]
    col_supervisor = 'SUPERVISOR' if 'SUPERVISOR' in df.columns else 'Supervisor'

    df = df[df[col_tecnico_check].fillna('').astype(str).str.strip() != ''].copy()
    df['Status_Atividade_Upper'] = df[col_status_real].fillna('').astype(str).str.upper().str.strip()
    
    # Cálculos de contagem
    df['P_COUNT'] = df['Status_Atividade_Upper'].str.contains('PENDENTE|EM ABERTO|ABERTO|PEND', na=False).astype(int)
    df['R_COUNT'] = df['Status_Atividade_Upper'].str.contains('ROTA|DESLOC|DESLOCAMENTO', na=False).astype(int)
    df['I_COUNT'] = df['Status_Atividade_Upper'].str.contains('INICIADO|PRODUTIVO|EXECUCAO|INIC', na=False).astype(int)

    # === PADRONIZAÇÃO RÍGIDA DE SUPERVISOR ===
    def padronizar_supervisor(nome):
        nome = str(nome).upper().strip()
        if 'ALAN' in nome or 'FRANCISCO' in nome: return 'SP'
        return 'ABC' # Maicon e todos os outros caem aqui

    df['SUPERVISOR_MOSTRAR'] = df[col_supervisor].apply(padronizar_supervisor)

    # === MOTOR DE JANELAS (Simplificado) ===
    df_tela = df.copy() 
    
    # Exibição
    col_coluna_abc, col_coluna_sp = st.columns(2)
    
    for nome_col, cond_filtro, titulo, cor in [(col_coluna_abc, df['SUPERVISOR_MOSTRAR'] == 'ABC', "ABC", "#008080"), 
                                              (col_coluna_sp, df['SUPERVISOR_MOSTRAR'] == 'SP', "SÃO PAULO (SP)", "#b30000")]:
        with nome_col:
            st.markdown(f'<div style="font-size:18px; font-weight: bold; color: {cor}; text-align: center;">{titulo}</div>', unsafe_allow_html=True)
            df_subset = df_tela[cond_filtro]
            if not df_subset.empty:
                matriz = df_subset.groupby('SUPERVISOR_MOSTRAR')[['P_COUNT', 'R_COUNT', 'I_COUNT']].sum().reset_index()
                for _, row in matriz.iterrows():
                    with st.container(border=True):
                        st.markdown(f"📋 **{row['SUPERVISOR_MOSTRAR']}**")
                        m1, m2, m3 = st.columns(3)
                        m1.metric("🔴 PENDENTES", int(row['P_COUNT']))
                        m2.metric("🟣 EM ROTA", int(row['R_COUNT']))
                        m3.metric("🟢 INICIADO", int(row['I_COUNT']))
else:
    st.warning("👈 Por favor, faça o upload dos arquivos de rota.")

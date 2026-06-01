import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if ('df_rota_ativa' not in st.session_state or st.session_state['df_rota_ativa'] is None) and os.path.exists(ARQUIVO_ROTA_DISCO):
    try: st.session_state['df_rota_ativa'] = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    except: pass

st.markdown('<h1 style="font-size: 42px; font-weight: 900; color: #006677; text-align: center;">TEC1</h1>', unsafe_allow_html=True)

df_master = st.session_state.get('df_rota_ativa', None)

if df_master is not None and not df_master.empty:
    df = df_master.copy()
    col_status_real = 'Status da Atividade' if 'Status da Atividade' in df.columns else 'STATUS_ATIVIDADE'
    col_supervisor = 'SUPERVISOR' if 'SUPERVISOR' in df.columns else 'Supervisor'
    
    # 1. RECUPERAÇÃO DOS CÁLCULOS QUE ESTAVAM FALTANDO
    df['Status_Atividade_Upper'] = df[col_status_real].fillna('').astype(str).str.upper().str.strip()
    df['P_COUNT'] = df['Status_Atividade_Upper'].str.contains('PENDENTE|EM ABERTO|ABERTO|PEND', na=False).astype(int)
    df['R_COUNT'] = df['Status_Atividade_Upper'].str.contains('ROTA|DESLOC|DESLOCAMENTO', na=False).astype(int)
    df['I_COUNT'] = df['Status_Atividade_Upper'].str.contains('INICIADO|PRODUTIVO|EXECUCAO|INIC', na=False).astype(int)
    
    # 2. Padronização de Supervisor
    def padronizar_supervisor(nome):
        nome = str(nome).upper().strip()
        if 'ALAN' in nome or 'FRANCISCO' in nome: return 'SP'
        return 'ABC'

    df['SUPERVISOR_MOSTRAR'] = df[col_supervisor].apply(padronizar_supervisor)
    df['NOME_SUPERVISOR_REAL'] = df[col_supervisor].fillna('SEM SUPERVISOR')

    # 3. Função de exibição corrigida
    def exibir_coluna(coluna_st, filtro_regiao, titulo):
        with coluna_st:
            st.markdown(f'<div style="font-size:18px; font-weight: bold; text-align: center; color: #008080;">{titulo}</div>', unsafe_allow_html=True)
            df_subset = df[filtro_regiao]
            if not df_subset.empty:
                matriz = df_subset.groupby('NOME_SUPERVISOR_REAL')[['P_COUNT', 'R_COUNT', 'I_COUNT']].sum().reset_index()
                for _, row in matriz.iterrows():
                    with st.container(border=True):
                        st.markdown(f"📋 **{row['NOME_SUPERVISOR_REAL']}**")
                        m1, m2, m3 = st.columns(3)
                        m1.metric("🔴 PENDENTES", int(row['P_COUNT']))
                        m2.metric("🟣 EM ROTA", int(row['R_COUNT']))
                        m3.metric("🟢 INICIADO", int(row['I_COUNT']))
            else:
                st.info(f"Nenhum contrato ativo para {titulo}.")

    col_abc, col_sp = st.columns(2)
    exibir_coluna(col_abc, df['SUPERVISOR_MOSTRAR'] == 'ABC', "ABC")
    exibir_coluna(col_sp, df['SUPERVISOR_MOSTRAR'] == 'SP', "SÃO PAULO (SP)")

else:
    st.warning("👈 Por favor, faça o upload dos arquivos de rota.")

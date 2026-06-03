import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

# LIGAÇÃO AO GOOGLE SHEETS
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1kB1YmUuhzHpfN1dLv8PaQn0ipXcHcd6kGKnI3nguT14/export?format=csv&gid=0"

SUPERVISORES = []
try:
    df_equipe = pd.read_csv(URL_PLANILHA)
    if not df_equipe.empty and len(df_equipe.columns) >= 3:
        df_equipe.columns = df_equipe.columns.str.strip().str.upper()
        SUPERVISORES = [str(s).strip().upper() for s in df_equipe["SUPERVISOR"].dropna().unique().tolist() if str(s).strip() != ""]
except Exception:
    pass

if ('df_rota_ativa' not in st.session_state or st.session_state['df_rota_ativa'] is None) and os.path.exists(ARQUIVO_ROTA_DISCO):
    try: 
        st.session_state['df_rota_ativa'] = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    except: 
        pass

if 'df_rota_ativa' in st.session_state and st.session_state['df_rota_ativa'] is not None:
    if "last_refresh_pendentes" not in st.session_state: 
        st.session_state["last_refresh_pendentes"] = time.time()
    if time.time() - st.session_state["last_refresh_pendentes"] > 30:
        st.session_state["last_refresh_pendentes"] = time.time()
        st.rerun()

st.markdown("""
    <style>
        .block-container { padding-top: 10px !important; padding-bottom: 5px !important; }
        .stDeployButton { display:none; }
        .title-abc-sp { font-size: 26px; font-weight: bold; color: #111111; margin-bottom: 10px; border-bottom: 3px solid #b30000; padding-bottom: 5px; }
        .super-bar { background-color: #f7f5f0; border-left: 5px solid #d32f2f; padding: 6px 10px; font-size: 16px; font-weight: bold; color: #333; margin-top: 10px; margin-bottom: 5px; display: flex; justify-content: space-between; align-items: center; border-radius: 4px; box-shadow: 1px 1px 3px rgba(0,0,0,0.1); }
        .super-total { background-color: #d32f2f; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px; }
        .item-linha { font-size: 13px; color: #444; border-bottom: 1px solid #eee; padding: 4px 0; margin-left: 5px; }
        .item-linha:hover { background-color: #f9f9f9; }
        .item-contrato { font-weight: bold; color: #111; font-family: monospace; font-size: 14px; }
        .divisor-item { color: #ccc; margin: 0 5px; }
    </style>
""", unsafe_allow_html=True)

def padronizar_supervisor_dinamico(nome_cru):
    nome = str(nome_cru).upper().strip()
    for sup in SUPERVISORES:
        if sup in nome or nome in sup:
            return sup
    return nome

df = st.session_state.get('df_rota_ativa', None)

if df is not None and not df.empty:
    
    col_status = 'Status da Atividade' if 'Status da Atividade' in df.columns else 'STATUS_ATIVIDADE'
    col_tecnico_check = 'Técnico' if 'Técnico' in df.columns else ('Recurso' if 'Recurso' in df.columns else None)
    
    if col_status and col_tecnico_check:
        df['Status_Atividade_Upper'] = df[col_status].fillna('').astype(str).str.upper().str.strip()
        df[col_tecnico_check] = df[col_tecnico_check].fillna('').astype(str).str.upper().str.strip()
        
        df_validos = df[df['Status_Atividade_Upper'].str.contains('PENDENTE|EM ABERTO|ABERTO|PEND', na=False)].copy()
        
        if 'Contrato' in df_validos.columns:
            df_validos['Contrato'] = df_validos['Contrato'].fillna('').astype(str).apply(lambda x: str(x).split('.')[0])
            df_validos = df_validos.drop_duplicates(subset=['Contrato', col_tecnico_check])

        # FILTRO DE JANELA DE HORÁRIO DINÂMICA E INTELIGENTE
        col_janela = None
        for col in df_validos.columns:
            if 'JANELA' in str(col).upper() or 'INTERVALO' in str(col).upper():
                col_janela = col
                break
                
        hora_atual = (datetime.utcnow() - timedelta(hours=3)).hour
        df_janela_atual = pd.DataFrame()
        
        if col_janela is not None and not df_validos.empty:
            df_validos['Intervalo_Tratado'] = df_validos[col_janela].fillna('').astype(str).str.strip()
            def extrair_hora_limite(janela_str):
                try: return int(janela_str.replace(':', '').split('-')[1].strip()[:2])
                except: return 24
            df_validos['Hora_Limite_Janela'] = df_validos['Intervalo_Tratado'].apply(extrair_hora_limite)
            
            if hora_atual < 12: condicao_horario = (df_validos['Hora_Limite_Janela'] <= 12)
            elif 12 <= hora_atual < 15: condicao_horario = (df_validos['Hora_Limite_Janela'] <= 15)
            else: condicao_horario = (df_validos['Hora_Limite_Janela'] <= 24)
            
            df_janela_atual = df_validos[condicao_horario].copy()
            if df_janela_atual.empty: df_janela_atual = df_validos.copy()
        else:
            df_janela_atual = df_validos.copy()

        df_janela_atual['SUPERVISOR_MOSTRAR'] = df_janela_atual['SUPERVISOR'].apply(padronizar_supervisor_dinamico)

        cond_sp = df_janela_atual['SUPERVISOR_MOSTRAR'].str.contains('FRANCISCO|ALAN', na=False)
        df_sp = df_janela_atual[cond_sp].copy()
        df_abc = df_janela_atual[~cond_sp].copy()

        col_coluna_abc, col_coluna_sp = st.columns(2)

        with col_coluna_abc:
            st.markdown('<div class="title-abc-sp">ABC PAULISTA</div>', unsafe_allow_html=True)
            if not df_abc.empty:
                for supervisor in sorted(df_abc['SUPERVISOR_MOSTRAR'].unique()):
                    df_super = df_abc[df_abc['SUPERVISOR_MOSTRAR'] == supervisor]
                    st.markdown(f'<div class="super-bar">👤 {supervisor} <span class="super-total">Pendentes: {len(df_super)}</span></div>', unsafe_allow_html=True)
                    for _, linha in df_super.iterrows():
                        st.markdown(f'<div class="item-linha">📄 <span class="item-contrato">{linha.get("Contrato", "N/A")}</span> <span class="divisor-item">|</span> 👤 {str(linha.get(col_tecnico_check, "TÉCNICO")).upper()}</div>', unsafe_allow_html=True)
            else: 
                st.info("Nenhum pendente no ABC para esta janela.")

        with col_coluna_sp:
            st.markdown('<div class="title-abc-sp">SÃO PAULO (SP)</div>', unsafe_allow_html=True)
            if not df_sp.empty:
                for supervisor in sorted(df_sp['SUPERVISOR_MOSTRAR'].unique()):
                    df_super = df_sp[df_sp['SUPERVISOR_MOSTRAR'] == supervisor]
                    st.markdown(f'<div class="super-bar">👤 {supervisor} <span class="super-total">Pendentes: {len(df_super)}</span></div>', unsafe_allow_html=True)
                    for _, linha in df_super.iterrows():
                        st.markdown(f'<div class="item-linha">📄 <span class="item-contrato">{linha.get("Contrato", "N/A")}</span> <span class="divisor-item">|</span> 👤 {str(linha.get(col_tecnico_check, "TÉCNICO")).upper()}</div>', unsafe_allow_html=True)
            else:
                st.info("Nenhum pendente em SP para esta janela.")
    else:
        st.warning("Colunas 'Status da Atividade' ou 'Técnico' não encontradas.")
else:
    st.info("Aguardando upload na página inicial...")

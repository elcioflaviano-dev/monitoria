import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta

# 1. Configura a página para ocupar toda a largura da tela
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1kB1YmUuhzHpfN1dLv8PaQn0ipXcHcd6kGKnI3nguT14/export?format=csv&gid=0"

# 🔄 HERANÇA INTELIGENTE
if ('df_rota_ativa' not in st.session_state or st.session_state['df_rota_ativa'] is None) and os.path.exists(ARQUIVO_ROTA_DISCO):
    try: 
        st.session_state['df_rota_ativa'] = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    except: 
        pass

# 🚀 MAPEAMENTO AO VIVO DO GOOGLE SHEETS (INVISÍVEL NO VISUAL)
mapa_base = {}
mapa_sup = {}
try:
    df_equipe = pd.read_csv(URL_PLANILHA)
    if not df_equipe.empty and len(df_equipe.columns) >= 3:
        df_equipe.columns = df_equipe.columns.str.strip().str.upper()
        mapa_base = dict(zip(df_equipe['NOME'].astype(str).str.strip().str.upper(), df_equipe['BASE'].astype(str).str.strip().str.upper()))
        mapa_sup = dict(zip(df_equipe['NOME'].astype(str).str.strip().str.upper(), df_equipe['SUPERVISOR'].astype(str).str.strip().str.upper()))
except:
    pass

# 🚀 REFRESH (30s)
if 'df_rota_ativa' in st.session_state and st.session_state['df_rota_ativa'] is not None:
    if "last_refresh_tec1" not in st.session_state: 
        st.session_state["last_refresh_tec1"] = time.time()
    if time.time() - st.session_state["last_refresh_tec1"] > 30:
        st.session_state["last_refresh_tec1"] = time.time()
        st.rerun()

try:
    with open("style.css", "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except:
    pass

st.markdown('<h1 style="font-size: 42px; font-weight: 900; color: #006677; text-align: center; margin-top: 25px; margin-bottom: 5px;">TEC1</h1>', unsafe_allow_html=True)

df = st.session_state.get('df_rota_ativa', None)

if df is not None and not df.empty:
    df = df.copy()
    
    col_status = 'Status da Atividade' if 'Status da Atividade' in df.columns else 'STATUS_ATIVIDADE'
    col_tecnico = 'Técnico' if 'Técnico' in df.columns else ('Recurso' if 'Recurso' in df.columns else None)
    
    if col_status and col_tecnico:
        df['Status_Atividade_Upper'] = df[col_status].fillna('').astype(str).str.upper().str.strip()
        df[col_tecnico] = df[col_tecnico].fillna('').astype(str).str.upper().str.strip()
        
        df_limpo = df[df['Status_Atividade_Upper'] != 'SUSPENSO'].copy()
        
        df_limpo['P_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('PENDENTE|EM ABERTO|ABERTO|PEND', na=False).astype(int)
        df_limpo['R_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('ROTA|DESLOC|DESLOCAMENTO', na=False).astype(int)
        df_limpo['I_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('INICIADO|PRODUTIVO|EXECUCAO|INIC', na=False).astype(int)
        
        df_validos = df_limpo[(df_limpo['P_COUNT'] > 0) | (df_limpo['R_COUNT'] > 0) | (df_limpo['I_COUNT'] > 0)].copy()
        
        if 'Contrato' in df_validos.columns:
            df_validos['Contrato'] = df_validos['Contrato'].fillna('').astype(str).apply(lambda x: str(x).split('.')[0])
            df_validos = df_validos.drop_duplicates(subset=['Contrato', col_tecnico])

        # APLICA O MAPEAMENTO DINÂMICO
        if mapa_sup:
            df_validos['SUPERVISOR_MOSTRAR'] = df_validos[col_tecnico].map(mapa_sup).fillna('NÃO IDENTIFICADO')
        else:
            df_validos['SUPERVISOR_MOSTRAR'] = df_validos.get('SUPERVISOR', 'NÃO IDENTIFICADO').astype(str).str.upper().str.strip()

        if mapa_base:
            df_validos['BASE_LIVE'] = df_validos[col_tecnico].map(mapa_base).fillna('GERAL')
        else:
            cond_sp = df_validos['SUPERVISOR_MOSTRAR'].str.contains('FRANCISCO|ALAN', na=False)
            df_validos['BASE_LIVE'] = ['SP' if x else 'ABC' for x in cond_sp]

        df_sp = df_validos[df_validos['BASE_LIVE'] == 'SP'].copy()
        df_abc = df_validos[df_validos['BASE_LIVE'] == 'ABC'].copy()

        col_coluna_abc, col_coluna_sp = st.columns(2)
        
        with col_coluna_abc:
            st.markdown('<div class="title-abc-sp">ABC PAULISTA</div>', unsafe_allow_html=True)
            if not df_abc.empty:
                matriz_abc = df_abc.groupby('SUPERVISOR_MOSTRAR')[['P_COUNT', 'R_COUNT', 'I_COUNT']].sum().reset_index()
                for supervisor in sorted(matriz_abc['SUPERVISOR_MOSTRAR'].unique()):
                    dados_super = matriz_abc[matriz_abc['SUPERVISOR_MOSTRAR'] == supervisor].iloc[0]
                    pendentes, em_rota, iniciados = int(dados_super['P_COUNT']), int(dados_super['R_COUNT']), int(dados_super['I_COUNT'])
                    total_real = pendentes + em_rota + iniciados
                    
                    with st.container(border=True):
                        st.markdown(f'<div style="font-size:20px; font-weight:bold; margin-bottom:10px;">📋 {supervisor} <span style="float:right; font-size:14px; background-color:#e8f5e9; padding:2px 8px; border-radius:4px; color:#2e7d32;">Total Contratos: {total_real}</span></div>', unsafe_allow_html=True)
                        m1, m2, m3 = st.columns(3)
                        with m1: st.markdown(f'<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 PENDENTES</div><div class="custom-pendente-value">{pendentes}</div></div>', unsafe_allow_html=True)
                        with m2: st.metric(label="🟣 EM ROTA", value=em_rota)
                        with m3: st.metric(label="🟢 INICIADOS", value=iniciados)
            else:
                st.info("Nenhum dado produtivo no ABC.")
                
        with col_coluna_sp:
            st.markdown('<div class="title-abc-sp">SÃO PAULO (SP)</div>', unsafe_allow_html=True)
            if not df_sp.empty:
                matriz_sp = df_sp.groupby('SUPERVISOR_MOSTRAR')[['P_COUNT', 'R_COUNT', 'I_COUNT']].sum().reset_index()
                for supervisor in sorted(matriz_sp['SUPERVISOR_MOSTRAR'].unique()):
                    dados_super = matriz_sp[matriz_sp['SUPERVISOR_MOSTRAR'] == supervisor].iloc[0]
                    pendentes, em_rota, iniciados = int(dados_super['P_COUNT']), int(dados_super['R_COUNT']), int(dados_super['I_COUNT'])
                    total_real = pendentes + em_rota + iniciados
                    
                    with st.container(border=True):
                        st.markdown(f'<div style="font-size:20px; font-weight:bold; margin-bottom:10px;">📋 {supervisor} <span style="float:right; font-size:14px; background-color:#e1f5fe; padding:2px 8px; border-radius:4px; color:#0288d1;">Total Contratos: {total_real}</span></div>', unsafe_allow_html=True)
                        m1, m2, m3 = st.columns(3)
                        with m1: st.markdown(f'<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 PENDENTES</div><div class="custom-pendente-value">{pendentes}</div></div>', unsafe_allow_html=True)
                        with m2: st.metric(label="🟣 EM ROTA", value=em_rota)
                        with m3: st.metric(label="🟢 INICIADOS", value=iniciados)
            else:
                st.info("Nenhum dado produtivo em SP.")
    else:
        st.warning("Colunas 'Status da Atividade' ou 'Técnico' não encontradas no arquivo.")
else:
    st.info("Aguardando upload na página inicial...")

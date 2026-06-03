import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta

# 1. Configuração da página
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# LIGAÇÃO AO GOOGLE SHEETS
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1kB1YmUuhzHpfN1dLv8PaQn0ipXcHcd6kGKnI3nguT14/export?format=csv&gid=0"

SUPERVISORES, LISTA_SP_FIXA, LISTA_ABC_FIXA = [], [], []

try:
    df_equipe = pd.read_csv(URL_PLANILHA)
    if not df_equipe.empty and len(df_equipe.columns) >= 3:
        df_equipe.columns = df_equipe.columns.str.strip().str.upper()
        SUPERVISORES = [str(s).strip().upper() for s in df_equipe["SUPERVISOR"].dropna().unique().tolist() if str(s).strip() != ""]
        LISTA_SP_FIXA = df_equipe[df_equipe["BASE"].str.strip().str.upper() == "SP"]["NOME"].str.strip().str.upper().dropna().tolist()
        LISTA_ABC_FIXA = df_equipe[df_equipe["BASE"].str.strip().str.upper() == "ABC"]["NOME"].str.strip().str.upper().dropna().tolist()
except Exception:
    pass

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

# 🔄 HERANÇA INTELIGENTE VIA DISCO RÍGIDO (À PROVA DE QUEDAS DE SESSÃO)
if ('df_rota_ativa' not in st.session_state or st.session_state['df_rota_ativa'] is None) and os.path.exists(ARQUIVO_ROTA_DISCO):
    try:
        st.session_state['df_rota_ativa'] = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    except:
        pass

# 🚀 SISTEMA DE REFRESH AUTOMÁTICO PARA A TV (60 Segundos)
if 'df_rota_ativa' in st.session_state and st.session_state['df_rota_ativa'] is not None:
    if "last_refresh_dash" not in st.session_state:
        st.session_state["last_refresh_dash"] = time.time()
    
    if time.time() - st.session_state["last_refresh_dash"] > 60:
        st.session_state["last_refresh_dash"] = time.time()
        st.rerun()

# 2. Carregar o CSS
try:
    with open("style.css", "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
except:
    pass # Falha silenciosa se não encontrar o CSS

# Tenta carregar o DataFrame da sessão
df = st.session_state.get('df_rota_ativa', None)

if df is not None and not df.empty:
    
    col_status_real = 'Status da Atividade' if 'Status da Atividade' in df.columns else 'STATUS_ATIVIDADE'
    col_tecnico_check = 'Técnico' if 'Técnico' in df.columns else ('Recurso' if 'Recurso' in df.columns else None)
    
    if col_status_real and col_tecnico_check:
        df['Status_Atividade_Upper'] = df[col_status_real].fillna('').astype(str).str.upper().str.strip()
        df[col_tecnico_check] = df[col_tecnico_check].fillna('').astype(str).str.upper().str.strip()
        
        df_limpo = df[df['Status_Atividade_Upper'] != 'SUSPENSO'].copy()
        
        df_limpo['P_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('PENDENTE|EM ABERTO|ABERTO|PEND', na=False).astype(int)
        df_limpo['R_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('ROTA|DESLOC|DESLOCAMENTO', na=False).astype(int)
        df_limpo['I_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('INICIADO|PRODUTIVO|EXECUCAO|INIC', na=False).astype(int)
        
        df_validos = df_limpo[(df_limpo['P_COUNT'] > 0) | (df_limpo['R_COUNT'] > 0) | (df_limpo['I_COUNT'] > 0)].copy()

        if 'Contrato' in df_validos.columns:
            df_validos['Contrato'] = df_validos['Contrato'].fillna('').astype(str).apply(lambda x: str(x).split('.')[0])
            df_validos = df_validos.drop_duplicates(subset=['Contrato', col_tecnico_check])

        # Definir a Base de cada Técnico de forma inteligente usando as listas do Google Sheets
        def definir_base(nome):
            if nome in LISTA_SP_FIXA: return 'SP'
            if nome in LISTA_ABC_FIXA: return 'ABC'
            # Se não encontrar, tenta deduzir ou joga para GERAL (você pode ajustar esta lógica de fallback se quiser)
            return 'GERAL' 

        df_validos['BASE_ALVO'] = df_validos[col_tecnico_check].apply(definir_base)

        for nome_base, base_filtrada in [("SÃO PAULO (SP)", "SP"), ("ABC PAULISTA", "ABC")]:
            df_base = df_validos[df_validos['BASE_ALVO'] == base_filtrada].copy()
            
            base_p = df_base['P_COUNT'].sum()
            base_r = df_base['R_COUNT'].sum()
            base_i = df_base['I_COUNT'].sum()
            base_qtd_tecnicos = df_base[col_tecnico_check].nunique()
            base_total_real = base_p + base_r + base_i
            base_total_retornos = 0 
            
            if base_qtd_tecnicos > 0: media_contratos_por_tec = base_total_real / base_qtd_tecnicos
            else: media_contratos_por_tec = 0

            if base_total_real > 0: progresso_base = ((base_r + base_i) / base_total_real) * 100
            else: progresso_base = 0

            st.markdown(f'<div class="title-abc-sp">{nome_base}</div>', unsafe_allow_html=True)
            
            c1, c2, c3, c4, c5, c6 = st.columns([1.5, 1.5, 1, 1, 1.5, 2.5])
            
            with c1:
                with st.container(border=True):
                    st.markdown(f'<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 Total Pendentes</div><div class="custom-pendente-value">{base_p}</div></div>', unsafe_allow_html=True)
            with c2:
                with st.container(border=True):
                    st.markdown(f'<div style="font-size:11px; font-weight:bold; color:#777; text-transform:uppercase;">🟢 Em Rota / Iniciado</div>', unsafe_allow_html=True)
                    st.markdown(f'<div style="font-size:24px; font-weight:900; color:#2e7d32;">{base_r + base_i} <span style="font-size:14px; font-weight:normal; color:#666;">/ {base_total_real} (Total)</span></div>', unsafe_allow_html=True)
            with c3:
                with st.container(border=True):
                    st.markdown(f'<div style="font-size:11px; font-weight:bold; color:#777; text-transform:uppercase;">🏃‍♂️ Técnicos em Rota</div>', unsafe_allow_html=True)
                    st.markdown(f'<div style="font-size:24px; font-weight:900; color:#005088;">{base_qtd_tecnicos}</div>', unsafe_allow_html=True)
            with c4:
                with st.container(border=True):
                    st.markdown(f'<div style="font-size:11px; font-weight:bold; color:#777; text-transform:uppercase;">⚠️ Total Retornos</div>', unsafe_allow_html=True)
                    st.markdown(f'<div style="font-size:24px; font-weight:900; color:#b30000;">{base_total_retornos}</div>', unsafe_allow_html=True)
            with c5:
                with st.container(border=True):
                    st.markdown(f'<div style="font-size:11px; font-weight:bold; color:#777; text-transform:uppercase;">¼ Média Contratos/Téc</div>', unsafe_allow_html=True)
                    st.markdown(f'<div style="font-size:24px; font-weight:900; color:#008080;">{media_contratos_por_tec:.2f}</div>', unsafe_allow_html=True)
            with c6:
                with st.container(border=True):
                    st.markdown(f'<div style="font-size:11px; font-weight:bold; color:#777; text-transform:uppercase;">📈 Produtividade Geral</div>', unsafe_allow_html=True)
                    st.progress(progresso_base / 100)
                    st.markdown(f'<div style="text-align:right; font-size:14px; font-weight:bold; color:#2e7d32; margin-top:-10px;">{progresso_base:.1f}%</div>', unsafe_allow_html=True)

            st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
            
    else:
        st.warning("Colunas 'Status da Atividade' ou 'Técnico' não encontradas.")
else:
    st.info("Aguardando o upload da nova rota...")

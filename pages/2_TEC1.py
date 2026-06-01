import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta

# 1. Configura a página para ocupar toda a largura da tela
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

# 🔄 HERANÇA INTELIGENTE VIA DISCO RÍGIDO
if ('df_rota_ativa' not in st.session_state or st.session_state['df_rota_ativa'] is None) and os.path.exists(ARQUIVO_ROTA_DISCO):
    try: st.session_state['df_rota_ativa'] = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    except: pass

# 🚀 REFRESH AUTOMÁTICO PARA A TV (30 Segundos)
if 'df_rota_ativa' in st.session_state and st.session_state['df_rota_ativa'] is not None:
    if "last_refresh_tec1" not in st.session_state: st.session_state["last_refresh_tec1"] = time.time()
    if time.time() - st.session_state["last_refresh_tec1"] > 30:
        st.session_state["last_refresh_tec1"] = time.time()
        st.rerun()

try:
    with open("style.css", "r") as f: st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except: pass

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
    
    if 'Contrato' in df.columns:
        df['Contrato'] = df['Contrato'].fillna('').astype(str).apply(lambda x: x.split('.')[0] if '.' in x else x).str.strip()

    df['Status_Atividade_Upper'] = df[col_status_real].fillna('').astype(str).str.upper().str.strip()
    df_limpo = df[df['Status_Atividade_Upper'] != 'SUSPENSO'].copy()
    
    df_limpo['Tipo_Activity_Str'] = df_limpo[col_tipo_real].fillna('').astype(str)
    df_limpo = df_limpo[~df_limpo['Tipo_Activity_Str'].str.contains('Refeicao', case=False, na=False)]
        
    df_limpo['P_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('PENDENTE|EM ABERTO|ABERTO|PEND', na=False).astype(int)
    df_limpo['R_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('ROTA|DESLOC|DESLOCAMENTO', na=False).astype(int)
    df_limpo['I_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('INICIADO|PRODUTIVO|EXECUCAO|INIC', na=False).astype(int)
    
    df_validos = df_limpo[(df_limpo['P_COUNT'] > 0) | (df_limpo['R_COUNT'] > 0) | (df_limpo['I_COUNT'] > 0)].copy()

    # === MOTOR DE JANELAS ACUMULATIVO ===
    col_janela = None
    for c in df_validos.columns:
        if 'JANELA' in str(c).upper() or 'INTERVALO' in str(c).upper(): col_janela = c; break

    hora_atual = (datetime.utcnow() - timedelta(hours=3)).hour

    if col_janela is not None and not df_validos.empty:
        df_validos['Intervalo_Tratado'] = df_validos[col_janela].fillna('').astype(str).str.strip()
        
        def extrair_hora_limite(janela_str):
            try:
                partes = janela_str.replace(':', '').split('-')
                return int(partes[1].strip()[:2]) if len(partes) == 2 else 24
            except: return 24

        df_validos['Hora_Limite_Janela'] = df_validos['Intervalo_Tratado'].apply(extrair_hora_limite)
        
        if hora_atual < 12:
            condicao_horario = (df_validos['Hora_Limite_Janela'] <= 12)
            texto_status_janela = "Exibindo Manhã (Janelas até 11:00 e 12:00)"
        elif 12 <= hora_atual < 15:
            condicao_horario = (df_validos['Hora_Limite_Janela'] <= 15)
            texto_status_janela = "Exibindo Acumulado Manhã + Tarde (Janelas até 15:00)"
        else:
            condicao_horario = (df_validos['Hora_Limite_Janela'] <= 24)
            texto_status_janela = "Exibindo Visão Geral do Turno (Janelas até 18:00 / Acumulado)"

        df_tela = df_validos[condicao_horario | (df_validos['R_COUNT'] > 0) | (df_validos['I_COUNT'] > 0)].copy()
        if df_tela.empty: df_tela = df_validos.copy()
        st.markdown(f'<div style="text-align: center; color: #008080; font-size: 14px; font-weight: bold; margin-bottom: 15px;">🔄 Fila Progressiva Cumulativa Ativa • {texto_status_janela}</div>', unsafe_allow_html=True)
    else:
        df_tela = df_validos.copy()

    # 🔥 LEITURA LIMPA E PADRONIZAÇÃO DO SUPERVISOR DIRETAMENTE DO ARQUIVO DA HOME 🔥
    df_tela['SUPERVISOR_MOSTRAR'] = df_tela[col_supervisor].fillna('MAICON').astype(str).str.upper().str.strip()
    df_tela['SUPERVISOR_MOSTRAR'] = df_tela['SUPERVISOR_MOSTRAR'].replace({'#N/A': 'MAICON', 'NAN': 'MAICON', '': 'MAICON'})
    df_tela['SUPERVISOR_MOSTRAR'] = df_tela['SUPERVISOR_MOSTRAR'].apply(lambda x: 'ALAN' if 'ALAN' in str(x) else ('MARCOS ROBERTO' if 'MARCOS' in str(x) else x))

    cond_sp = df_tela['SUPERVISOR_MOSTRAR'].str.contains('FRANCISCO|ALAN', na=False)
    df_sp = df_tela[cond_sp].copy()
    df_abc = df_tela[~cond_sp].copy()

    col_coluna_abc, col_coluna_sp = st.columns(2)
    
    with col_coluna_abc:
        st.markdown('<div class="title-abc-sp" style="font-size:18px; font-weight: bold; margin-bottom: 10px; color: #008080; text-align: center;">ABC</div>', unsafe_allow_html=True)
        if not df_abc.empty:
            matriz_abc = df_abc.groupby('SUPERVISOR_MOSTRAR')[['P_COUNT', 'R_COUNT', 'I_COUNT']].sum().reset_index()
            for _, dados_super in matriz_abc.iterrows():
                supervisor = dados_super['SUPERVISOR_MOSTRAR']
                pendentes, em_rota, iniciados = int(dados_super['P_COUNT']), int(dados_super['R_COUNT']), int(dados_super['I_COUNT'])
                with st.container(border=True):
                    st.markdown(f'<div style="font-size:20px; font-weight:bold; margin-bottom:10px;">📋 {supervisor} <span style="float:right; font-size:14px; background-color:#e1f5fe; padding:2px 8px; border-radius:4px; color:#0288d1;">Total: {pendentes+em_rota+iniciados}</span></div>', unsafe_allow_html=True)
                    m1, m2, m3 = st.columns(3)
                    with m1: st.markdown(f'<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 PENDENTES</div><div class="custom-pendente-value">{pendentes}</div></div>', unsafe_allow_html=True)
                    with m2: st.metric(label="🟣 EM ROTA", value=em_rota)
                    with m3: st.metric(label="🟢 INICIADO", value=iniciados)
        else: st.info("Nenhum contrato ativo para o ABC nesta janela.")

    with col_coluna_sp:
        st.markdown('<div style="font-size:18px; font-weight: bold; margin-bottom: 10px; color: #b30000; text-align: center;">SÃO PAULO (SP)</div>', unsafe_allow_html=True)
        if not df_sp.empty:
            matriz_sp = df_sp.groupby('SUPERVISOR_MOSTRAR')[['P_COUNT', 'R_COUNT', 'I_COUNT']].sum().reset_index()
            for _, dados_super in matriz_sp.iterrows():
                supervisor = dados_super['SUPERVISOR_MOSTRAR']
                pendentes, em_rota, iniciados = int(dados_super['P_COUNT']), int(dados_super['R_COUNT']), int(dados_super['I_COUNT'])
                with st.container(border=True):
                    st.markdown(f'<div style="font-size:20px; font-weight:bold; margin-bottom:10px;">📋 {supervisor} <span style="float:right; font-size:14px; background-color:#e1f5fe; padding:2px 8px; border-radius:4px; color:#0288d1;">Total: {pendentes+em_rota+iniciados}</span></div>', unsafe_allow_html=True)
                    m1, m2, m3 = st.columns(3)
                    with m1: st.markdown(f'<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 PENDENTES</div><div class="custom-pendente-value">{pendentes}</div></div>', unsafe_allow_html=True)
                    with m2: st.metric(label="🟣 EM ROTA", value=em_rota)
                    with m3: st.metric(label="🟢 INICIADO", value=iniciados)
        else: st.info("Nenhum contrato ativo para SP nesta janela.")
else: st.warning("👈 Por favor, faça o upload dos arquivos de rota na página inicial primeiro.")

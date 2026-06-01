import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta

# 1. Configuração da página ampla para a TV
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

# 🔄 HERANÇA INTELIGENTE VIA DISCO RÍGIDO
if ('df_rota_ativa' not in st.session_state or st.session_state['df_rota_ativa'] is None) and os.path.exists(ARQUIVO_ROTA_DISCO):
    try: 
        st.session_state['df_rota_ativa'] = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    except: 
        pass

# 🚀 REFRESH AUTOMÁTICO PARA A TV (30 Segundos)
if 'df_rota_ativa' in st.session_state and st.session_state['df_rota_ativa'] is not None:
    if "last_refresh_ativar" not in st.session_state: 
        st.session_state["last_refresh_ativar"] = time.time()
    if time.time() - st.session_state["last_refresh_ativar"] > 30:
        st.session_state["last_refresh_ativar"] = time.time()
        st.rerun()

try:
    with open("style.css", "r") as f: 
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except: 
    pass

st.markdown("""
    <style>
        .block-container { padding-top: 10px !important; padding-bottom: 5px !important; }
        .stDeployButton { display:none; }
        .title-abc-sp { font-size: 24px !important; font-weight: 800 !important; margin-bottom: 10px !important; text-align: center; color: #005088; }
        .super-bar { background-color: #f0f2f6; padding: 6px 12px; border-radius: 4px; font-size: 16px; font-weight: bold; color: #333; margin-top: 12px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center; border-left: 5px solid #008080; }
        .super-total { background-color: #e0f2f1; color: #004d40; padding: 2px 10px; border-radius: 4px; font-size: 13px; font-weight: 900; }
        .item-linha { font-size: 16px; padding: 5px 12px; border-bottom: 1px solid #eee; color: #222; }
        .item-tecnico { font-weight: 900; color: #008080; font-size: 17px; }
        .divisor-item { color: #bbb; margin: 0 8px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="font-size: 32px; font-weight: 900; color: #008080; text-align: center; margin-top: 5px; margin-bottom: 5px;">🚀 ATIVAR ROTA OPERACIONAL</h1>', unsafe_allow_html=True)

df_master = st.session_state.get('df_rota_ativa', None)

if df_master is not None and not df_master.empty:
    df = df_master.copy()
    df.columns = [str(c).strip() for c in df.columns]
    
    # 🛠️ TRAVA DE COLUNAS UNIFICADA
    col_tecnico_check = 'Recurso' if 'Recurso' in df.columns else df.columns[0]
    col_status_real = 'Status da Atividade' if 'Status da Atividade' in df.columns else 'STATUS_ATIVIDADE'
    col_supervisor = 'SUPERVISOR' if 'SUPERVISOR' in df.columns else 'Supervisor'
    
    if col_tecnico_check:
        df = df[df[col_tecnico_check].fillna('').astype(str).str.strip() != ''].copy()

    df['Status_Atividade_Upper'] = df[col_status_real].fillna('').astype(str).str.upper().str.strip()
    df_limpo = df[df['Status_Atividade_Upper'] != 'SUSPENSO'].copy()
    
    # Identifica quem está com status de base pendente para largada
    df_limpo['P_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('PENDENTE|EM ABERTO|ABERTO|PEND', na=False).astype(int)
    df_limpo['R_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('ROTA|DESLOC|DESLOCAMENTO', na=False).astype(int)
    df_limpo['I_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('INICIADO|PRODUTIVO|EXECUCAO|INIC', na=False).astype(int)
    
    df_validos = df_limpo[(df_limpo['P_COUNT'] > 0) | (df_limpo['R_COUNT'] > 0) | (df_limpo['I_COUNT'] > 0)].copy()

    # === MOTOR DE JANELAS ACUMULATIVO SINCRONIZADO ===
    col_janela = None
    for c in df_validos.columns:
        if 'JANELA' in str(c).upper() or 'INTERVALO' in str(c).upper(): 
            col_janela = c
            break

    hora_atual = (datetime.utcnow() - timedelta(hours=3)).hour

    if col_janela is not None and not df_validos.empty:
        df_validos['Intervalo_Tratado'] = df_validos[col_janela].fillna('').astype(str).str.strip()
        
        def extrair_hora_limite(janela_str):
            try:
                partes = janela_str.replace(':', '').split('-')
                return int(partes[1].strip()[:2]) if len(partes) == 2 else 24
            except: 
                return 24

        df_validos['Hora_Limite_Janela'] = df_validos['Intervalo_Tratado'].apply(extrair_hora_limite)
        
        if hora_atual < 12:
            condicao_horario = (df_validos['Hora_Limite_Janela'] <= 12)
            texto_status_janela = "Fila da Manhã (Até 12:00)"
        elif 12 <= hora_atual < 15:
            condicao_horario = (df_validos['Hora_Limite_Janela'] <= 15)
            texto_status_janela = "Acumulado Tarde (Até 15:00)"
        else:
            condicao_horario = (df_validos['Hora_Limite_Janela'] <= 24)
            texto_status_janela = "Visão Geral (Turno Completo)"

        df_base_janela = df_validos[condicao_horario | (df_validos['R_COUNT'] > 0) | (df_validos['I_COUNT'] > 0)].copy()
        # Filtra estritamente os que ainda estão pendentes para largada
        df_tela = df_base_janela[df_base_janela['P_COUNT'] > 0].copy()
        
        if df_tela.empty and df_base_janela.empty: 
            df_tela = df_validos[df_validos['P_COUNT'] > 0].copy()
            
        st.markdown(f'<div style="text-align: center; color: #008080; font-size: 14px; font-weight: bold; margin-bottom: 15px;">⏰ Filtro Progressivo: {texto_status_janela}</div>', unsafe_allow_html=True)
    else:
        df_tela = df_validos[df_validos['P_COUNT'] > 0].copy()

    if df_tela.empty:
        st.success("🎉 Todos os técnicos da janela já ativaram rota e saíram a campo!")
    else:
        # 🔥 ALINHAMENTO COMPLETO E PADRONIZAÇÃO DOS SUPERVISORES DIRETO DO DISCO 🔥
        df_tela['SUPERVISOR_MOSTRAR'] = df_tela[col_supervisor].fillna('MAICON').astype(str).str.upper().str.strip()
        df_tela['SUPERVISOR_MOSTRAR'] = df_tela['SUPERVISOR_MOSTRAR'].replace({'#N/A': 'MAICON', 'NAN': 'MAICON', '': 'MAICON'})
        df_tela['SUPERVISOR_MOSTRAR'] = df_tela['SUPERVISOR_MOSTRAR'].apply(
            lambda x: 'ALAN' if 'ALAN' in str(x) 
            else ('FRANCISCO GERALDO CARVALHO JUNIOR' if 'FRANCISCO' in str(x) 
            else ('MARCOS ROBERTO' if 'MARCOS' in str(x) else x))
        )

        # Divisão Regional Estável
        cond_sp = df_tela['SUPERVISOR_MOSTRAR'].str.contains('FRANCISCO|ALAN', na=False)
        df_sp = df_tela[cond_sp].copy()
        df_abc = df_tela[~cond_sp].copy()

        col_coluna_abc, col_coluna_sp = st.columns(2)
        
        with col_coluna_abc:
            st.markdown('<div class="title-abc-sp">ABC</div>', unsafe_allow_html=True)
            if not df_abc.empty:
                for supervisor in sorted(df_abc['SUPERVISOR_MOSTRAR'].unique()):
                    df_super = df_abc[df_abc['SUPERVISOR_MOSTRAR'] == supervisor].drop_duplicates(subset=[col_tecnico_check])
                    sup_exibicao = "FRANCISCO" if "FRANCISCO" in supervisor else supervisor
                    
                    st.markdown(f'<div class="super-bar">👤 {sup_exibicao} <span class="super-total">Aguardando: {len(df_super)}</span></div>', unsafe_allow_html=True)
                    for _, linha in df_super.iterrows():
                        st.markdown(f'<div class="item-linha">🏃‍♂️ <span class="item-tecnico">{str(linha.get(col_tecnico_check, "TÉCNICO")).upper()}</span> <span class="divisor-item">|</span> Janela: {linha.get(col_janela if col_janela else "Intervalo", "N/A")}</div>', unsafe_allow_html=True)
            else: 
                st.info("Nenhum técnico retido na base no ABC.")

        with col_coluna_sp:
            st.markdown('<div class="title-abc-sp">SÃO PAULO (SP)</div>', unsafe_allow_html=True)
            if not df_sp.empty:
                for supervisor in sorted(df_sp['SUPERVISOR_MOSTRAR'].unique()):
                    df_super = df_sp[df_sp['SUPERVISOR_MOSTRAR'] == supervisor].drop_duplicates(subset=[col_tecnico_check])
                    sup_exibicao = "FRANCISCO" if "FRANCISCO" in supervisor else supervisor
                    
                    st.markdown(f'<div class="super-bar">👤 {sup_exibicao} <span class="super-total">Aguardando: {len(df_super)}</span></div>', unsafe_allow_html=True)
                    for _, linha in df_super.iterrows():
                        st.markdown(f'<div class="item-linha">🏃‍♂️ <span class="item-tecnico">{str(linha.get(col_tecnico_check, "TÉCNICO")).upper()}</span> <span class="divisor-item">|</span> Janela: {linha.get(col_janela if col_janela else "Intervalo", "N/A")}</div>', unsafe_allow_html=True)
            else: 
                st.info("Nenhum técnico retido na base em SP.")
else: 
    st.warning("👈 Por favor, insira os arquivos de rota na página inicial primeiro.")

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

if 'df_rota_ativa' in st.session_state and st.session_state['df_rota_ativa'] is not None:
    if "last_refresh_pendentes" not in st.session_state: st.session_state["last_refresh_pendentes"] = time.time()
    if time.time() - st.session_state["last_refresh_pendentes"] > 30:
        st.session_state["last_refresh_pendentes"] = time.time()
        st.rerun()

st.markdown("""
    <style>
        [data-testid="stHeader"] { visibility: hidden !important; }
        .stDeployButton { display: none !important; }
        footer { visibility: hidden !important; }
        #MainMenu { visibility: hidden !important; }
        
        .block-container { padding-top: 10px !important; padding-bottom: 5px !important; }
        .title-abc-sp { font-size: 24px !important; font-weight: 800 !important; margin-bottom: 10px !important; text-align: center; color: #005088; }
        .super-bar { background-color: #f0f2f6; padding: 6px 12px; border-radius: 4px; font-size: 16px; font-weight: bold; color: #333; margin-top: 12px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center; border-left: 5px solid #cc6600; }
        .super-bar-erro { border-left: 5px solid #b30000; background-color: #ffebee; color: #b30000; }
        .super-total { background-color: #ffffff; color: #c62828; padding: 2px 10px; border-radius: 4px; font-size: 13px; font-weight: 900; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .item-linha { font-size: 16px; padding: 5px 12px; border-bottom: 1px solid #eee; color: #222; }
        .item-contrato { font-weight: 900; color: #cc6600; font-size: 17px; }
        .divisor-item { color: #bbb; margin: 0 8px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="font-size: 32px; font-weight: 900; color: #cc6600; text-align: center; margin-top: 5px; margin-bottom: 5px;">⏳ TEC1 PENDENTES</h1>', unsafe_allow_html=True)

df_master = st.session_state.get('df_rota_ativa', None)

if df_master is not None and not df_master.empty:
    df = df_master.copy()
    df.columns = [str(c).strip() for c in df.columns]
    
    col_tecnico_check = 'Recurso' if 'Recurso' in df.columns else df.columns[0]
    col_status_real = 'Status da Atividade' if 'Status da Atividade' in df.columns else 'STATUS_ATIVIDADE'
    col_supervisor = 'SUPERVISOR' if 'SUPERVISOR' in df.columns else 'Supervisor'
    
    if col_tecnico_check: df = df[df[col_tecnico_check].fillna('').astype(str).str.strip() != ''].copy()
    
    if 'Contrato' in df.columns:
        df['Contrato'] = df['Contrato'].fillna('').astype(str).apply(lambda x: x.split('.')[0] if '.' in x else x).str.strip()
        df = df[df['Contrato'] != ''].copy()

    df['Status_Atividade_Upper'] = df[col_status_real].fillna('').astype(str).str.upper().str.strip()
    df_limpo = df[df['Status_Atividade_Upper'] != 'SUSPENSO'].copy()
    
    df_limpo['P_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('PENDENTE|EM ABERTO|ABERTO|PEND', na=False).astype(int)
    df_limpo['R_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('ROTA|DESLOC|DESLOCAMENTO', na=False).astype(int)
    df_limpo['I_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('INICIADO|PRODUTIVO|EXECUCAO|INIC', na=False).astype(int)
    
    df_validos = df_limpo[(df_limpo['P_COUNT'] > 0) | (df_limpo['R_COUNT'] > 0) | (df_limpo['I_COUNT'] > 0)].copy()

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
            except: return 24

        df_validos['Hora_Limite_Janela'] = df_validos['Intervalo_Tratado'].apply(extrair_hora_limite)
        
        if hora_atual < 12:
            condicao_horario = (df_validos['Hora_Limite_Janela'] <= 12)
            texto_status_janela = "Pendentes da Manhã (Janelas até 11h e 12h)"
        elif 12 <= hora_atual < 15:
            condicao_horario = (df_validos['Hora_Limite_Janela'] <= 15)
            texto_status_janela = "Pendentes Acumulados (Manhã + Janelas até 15h)"
        else:
            condicao_horario = (df_validos['Hora_Limite_Janela'] <= 24)
            texto_status_janela = "Todos os Pendentes do Turno (Acumulado Completo)"

        df_base_janela = df_validos[condicao_horario | (df_validos['R_COUNT'] > 0) | (df_validos['I_COUNT'] > 0)].copy()
        df_tela = df_base_janela[df_base_janela['P_COUNT'] > 0].copy()
        
        if df_tela.empty and df_base_janela.empty: df_tela = df_validos[df_validos['P_COUNT'] > 0].copy()
        st.markdown(f'<div style="text-align: center; color: #cc6600; font-size: 14px; font-weight: bold; margin-bottom: 15px;">⏰ Progressão: {texto_status_janela}</div>', unsafe_allow_html=True)
    else:
        df_tela = df_validos[df_validos['P_COUNT'] > 0].copy()

    if df_tela.empty:
        st.success("🎉 Nenhum contrato pendente para esta janela no ABC!")
    else:
        if col_supervisor in df_tela.columns:
            df_tela['SUPERVISOR_MOSTRAR'] = df_tela[col_supervisor].fillna('').astype(str).str.upper().str.strip()
        else:
            df_tela['SUPERVISOR_MOSTRAR'] = ''

        def vincular_supervisor_tecnico(row):
            sup_orig = str(row.get('SUPERVISOR_MOSTRAR', '')).upper().strip()
            if sup_orig not in ['NÃO IDENTIFICADO', 'NAN', 'N/A', '', 'NULL', '#N/A']:
                if "MARCOS" in sup_orig and "ROBERTO" not in sup_orig: return "MARCOS ROBERTO"
                if "MAICON" in sup_orig and "MAICON" not in sup_orig: return "MAICON"
                return sup_orig
            return "⚠️ SEM SUPERVISOR (VERIFICAR EXCEL)"

        df_tela['SUPERVISOR_MOSTRAR'] = df_tela.apply(vincular_supervisor_tecnico, axis=1)

        # Filtra as equipes de São Paulo
        cond_sp = df_tela['SUPERVISOR_MOSTRAR'].str.contains('FRANCISCO|ALAN|JOAO|MIRON', na=False)
        df_abc = df_tela[~cond_sp].copy()

        st.markdown('<div class="title-abc-sp">REGIONAL ABC</div>', unsafe_allow_html=True)
        if not df_abc.empty:
            cols = st.columns(4)
            for i, supervisor in enumerate(sorted(df_abc['SUPERVISOR_MOSTRAR'].unique())):
                df_super = df_abc[df_abc['SUPERVISOR_MOSTRAR'] == supervisor]
                classe_css = "super-bar super-bar-erro" if "⚠️" in supervisor else "super-bar"
                
                with cols[i % 4]:
                    st.markdown(f'<div class="{classe_css}">👤 {supervisor} <span class="super-total">Pendentes: {len(df_super)}</span></div>', unsafe_allow_html=True)
                    for _, linha in df_super.iterrows():
                        st.markdown(f'<div class="item-linha">📄 <span class="item-contrato">{linha.get("Contrato", "N/A")}</span> <span class="divisor-item">|</span> 👤 {str(linha.get(col_tecnico_check, "TÉCNICO")).upper()}</div>', unsafe_allow_html=True)
        else: 
            st.info("Nenhum pendente no ABC para esta janela.")

else: 
    st.warning("👈 Insira os arquivos na página inicial primeiro.")

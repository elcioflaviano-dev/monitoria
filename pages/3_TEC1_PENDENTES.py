import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

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
        .title-abc-sp { font-size: 24px !important; font-weight: 800 !important; margin-bottom: 10px !important; text-align: center; color: #005088; }
        .super-bar { background-color: #f0f2f6; padding: 6px 12px; border-radius: 4px; font-size: 16px; font-weight: bold; color: #333; margin-top: 12px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center; border-left: 5px solid #cc6600; }
        .super-total { background-color: #ffebee; color: #c62828; padding: 2px 10px; border-radius: 4px; font-size: 13px; font-weight: 900; }
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
    
    # 🛠️ TRAVA DE COLUNAS IDÊNTICA AO TEC1 OPERACIONAL
    col_tecnico_check = 'Recurso' if 'Recurso' in df.columns else df.columns[0]
    col_status_real = 'Status da Atividade' if 'Status da Atividade' in df.columns else 'STATUS_ATIVIDADE'
    
    if col_tecnico_check:
        df = df[df[col_tecnico_check].fillna('').astype(str).str.strip() != ''].copy()
    
    if 'Contrato' in df.columns:
        df['Contrato'] = df['Contrato'].fillna('').astype(str).apply(lambda x: x.split('.')[0] if '.' in x else x).str.strip()
        df = df[df['Contrato'] != ''].copy()

    # Cria a verificação exata dos status pendentes na coluna do seu Excel
    df['Status_Atividade_Upper'] = df[col_status_real].fillna('').astype(str).str.upper().str.strip()
    df_limpo = df[df['Status_Atividade_Upper'] != 'SUSPENSO'].copy()
    
    # 🔥 Conta os pendentes reais
    df_limpo['P_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('PENDENTE|EM ABERTO|ABERTO|PEND', na=False).astype(int)
    df_tela = df_limpo[df_limpo['P_COUNT'] > 0].copy()

    if df_tela.empty:
        st.success("🎉 Nenhum contrato pendente para esta janela!")
    else:
        # Puxa o supervisor original gravado
        if 'SUPERVISOR' in df_tela.columns:
            df_tela['SUPERVISOR_MOSTRAR'] = df_tela['SUPERVISOR'].fillna('').astype(str).str.upper().str.strip()
        else:
            df_tela['SUPERVISOR_MOSTRAR'] = ''

        # Mapeamento de supervisores por primeiro nome do técnico (Garante a sincronia completa)
        def vincular_supervisor_tecnico(row):
            nome_u = str(row[col_tecnico_check]).upper().strip()
            sup_orig = str(row['SUPERVISOR_MOSTRAR'])
            
            if "FRANCISCO" in sup_orig: return "FRANCISCO"
            if "ALAN" in sup_orig: return "ALAN"
            if "MAICON" in sup_orig: return "MAICON"
            if "NELSON" in sup_orig: return "NELSON"
            if "MARCOS" in sup_orig: return "MARCOS ROBERTO"

            if "ADRIEL" in nome_u or "AMANDA" in nome_u or "DEBORA" in nome_u or "ELIAS" in nome_u or "AIRON" in nome_u: 
                return "ALAN"
            if "ALINE" in nome_u or "ALEX" in nome_u or "EDER" in nome_u or "ENOQUE" in nome_u: 
                return "FRANCISCO"
            if "MARCOS" in nome_u: 
                return "MARCOS ROBERTO"
            if "NELSON" in nome_u: 
                return "NELSON"
                
            return "MAICON"

        df_tela['SUPERVISOR_MOSTRAR'] = df_tela.apply(vincular_supervisor_tecnico, axis=1)

        # Divisão regional
        cond_sp = df_tela['SUPERVISOR_MOSTRAR'].str.contains('FRANCISCO|ALAN', na=False)
        df_sp = df_tela[cond_sp].copy()
        df_abc = df_tela[~cond_sp].copy()

        col_coluna_abc, col_coluna_sp = st.columns(2)
        
        with col_coluna_abc:
            st.markdown('<div class="title-abc-sp">ABC</div>', unsafe_allow_html=True)
            if not df_abc.empty:
                for supervisor in sorted(df_abc['SUPERVISOR_MOSTRAR'].unique()):
                    df_super = df_abc[df_abc['SUPERVISOR_MOSTRAR'] == supervisor]
                    st.markdown(f'<div class="super-bar">👤 {supervisor} <span class="super-total">Pendentes: {len(df_super)}</span></div>', unsafe_allow_html=True)
                    for _, linha in df_super.iterrows():
                        st.markdown(f'<div class="item-linha">📄 <span class="item-contrato">{linha.get("Contrato", "N/A")}</span> <span class="divisor-item">|</span> 👤 {str(linha.get(col_tecnico_check, "TÉCNICO")).upper()}</div>', unsafe_allow_html=True)
            else: 
                st.info("Nenhum pendente no ABC.")

        with col_coluna_sp:
            st.markdown('<div class="title-abc-sp">SÃO PAULO (SP)</div>', unsafe_allow_html=True)
            if not df_sp.empty:
                for supervisor in sorted(df_sp['SUPERVISOR_MOSTRAR'].unique()):
                    df_super = df_sp[df_sp['SUPERVISOR_MOSTRAR'] == supervisor]
                    st.markdown(f'<div class="super-bar">👤 {supervisor} <span class="super-total">Pendentes: {len(df_super)}</span></div>', unsafe_allow_html=True)
                    for _, linha in df_super.iterrows():
                        st.markdown(f'<div class="item-linha">📄 <span class="item-contrato">{linha.get("Contrato", "N/A")}</span> <span class="divisor-item">|</span> 👤 {str(linha.get(col_tecnico_check, "TÉCNICO")).upper()}</div>', unsafe_allow_html=True)
            else: 
                st.info("Nenhum pendente em SP.")
else: 
    st.warning("👈 Insira os arquivos na página inicial primeiro.")

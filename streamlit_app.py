import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta

# Configurações de layout da página
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

# 🔄 HERANÇA ESTÁVEL DO ARQUIVO FÍSICO
if ('df_rota_ativa' not in st.session_state or st.session_state['df_rota_ativa'] is None) and os.path.exists(ARQUIVO_ROTA_DISCO):
    try:
        st.session_state['df_rota_ativa'] = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    except:
        pass

# Carrega os estilos do arquivo CSS para manter o visual bonito das caixas
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

df_master = st.session_state.get('df_rota_ativa', None)

# MATRIZ DE DE-PARA UNIFICADA PARA OS SUPERVISORES
def vincular_supervisor_tecnico(nome_planilha):
    nome_u = str(nome_planilha).upper().strip()
    cadastro_recs = {
        "ADRIEL": "ALAN", "AIRON": "ALAN", "ALAN": "ALAN DE ANDRADE DIAS", 
        "ALEX": "FRANCISCO", "ALINE": "MAICON", "AMANDA": "ALAN", 
        "DEBORA": "ALAN", "ELIAS": "ALAN", "ENOQUE": "ALAN"
    }
    for chave, supervisor in cadastro_recs.items():
        if chave in nome_u: 
            return supervisor
    return "MAICON"

if df_master is not None and not df_master.empty:
    df = df_master.copy()
    df.columns = [str(c).strip() for c in df.columns]
    
    # 🛠️ MAPEAMENTO SEGURO DAS COLUNAS DO EXCEL REAL
    col_tecnico_check = 'Recurso' if 'Recurso' in df.columns else df.columns[0]
    col_status_real = 'Status da Atividade' if 'Status da Atividade' in df.columns else 'STATUS_ATIVIDADE'
    col_tipo_real = 'Tipo de Atividade' if 'Tipo de Atividade' in df.columns else df.columns[-1]

    # Limpa linhas inválidas
    df = df[df[col_tecnico_check].fillna('').astype(str).str.strip() != ''].copy()
    
    if 'Contrato' in df.columns:
        df['Contrato'] = df['Contrato'].fillna('').astype(str).apply(lambda x: x.split('.')[0] if '.' in x else x).str.strip()
    
    df['Status_Atividade_Upper'] = df[col_status_real].fillna('').astype(str).str.upper().str.strip()
    df_limpo = df[df['Status_Atividade_Upper'] != 'SUSPENSO'].copy()
    
    # Remove marcação de almoço
    df_limpo['Tipo_Activity_Str'] = df_limpo[col_tipo_real].fillna('').astype(str)
    df_limpo = df_limpo[~df_limpo['Tipo_Activity_Str'].str.contains('Refeicao', case=False, na=False)]
    
    # Contadores operacionais
    df_limpo['P_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('PENDENTE|EM ABERTO|ABERTO|PEND', na=False).astype(int)
    df_limpo['R_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('ROTA|DESLOC|DESLOCAMENTO', na=False).astype(int)
    df_limpo['I_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('INICIADO|PRODUTIVO|EXECUCAO|INIC', na=False).astype(int)
    
    # 🔥 APLICAÇÃO DA REGRA UNIFICADA: Vincula supervisor por primeiro nome
    df_limpo['SUPERVISOR_MOSTRAR'] = df_limpo[col_tecnico_check].apply(vincular_supervisor_tecnico)
    
    # Separação regional por supervisor âncora
    cond_sp = df_limpo['SUPERVISOR_MOSTRAR'].str.contains('FRANCISCO|ALAN', na=False)

    # Lógica para alternar as telas no painel rotativo (Baseado no tempo ou parâmetro existente)
    # Aqui dividimos o código nas duas funções visuais idênticas para renderizar conforme a sua lógica de rotação:
    
    # =========================================================================
    # LÓGICA DA VISÃO: TEC1 OPERACIONAL (image_fe6f5d.png)
    # =========================================================================
    def renderizar_visao_operacional():
        st.markdown('<h1 style="font-size: 42px; font-weight: 900; color: #006677; text-align: center; margin-top: 10px; margin-bottom: 5px;">📊 TEC1 OPERACIONAL</h1>', unsafe_allow_html=True)
        
        df_tela = df_limpo[(df_limpo['P_COUNT'] > 0) | (df_limpo['R_COUNT'] > 0) | (df_limpo['I_COUNT'] > 0)].copy()
        df_sp = df_tela[cond_sp].copy()
        df_abc = df_tela[~cond_sp].copy()
        
        c_abc, c_sp = st.columns(2)
        with c_abc:
            st.markdown('<div class="title-abc-sp" style="font-size:18px; font-weight: bold; margin-bottom: 10px; color: #008080; text-align: center;">ABC</div>', unsafe_allow_html=True)
            if not df_abc.empty:
                matriz_abc = df_abc.groupby('SUPERVISOR_MOSTRAR')[['P_COUNT', 'R_COUNT', 'I_COUNT']].sum().reset_index()
                for _, dados in matriz_abc.iterrows():
                    superv = dados['SUPERVISOR_MOSTRAR']
                    p, r, i = int(dados['P_COUNT']), int(dados['R_COUNT']), int(dados['I_COUNT'])
                    with st.container(border=True):
                        st.markdown(f'<div style="font-size:20px; font-weight:bold; margin-bottom:10px;">📋 {superv} <span style="float:right; font-size:14px; background-color:#e1f5fe; padding:2px 8px; border-radius:4px; color:#0288d1;">Total: {p+r+i}</span></div>', unsafe_allow_html=True)
                        m1, m2, m3 = st.columns(3)
                        with m1: st.markdown(f'<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 PENDENTES</div><div class="custom-pendente-value">{p}</div></div>', unsafe_allow_html=True)
                        with m2: st.metric(label="🟣 EM ROTA", value=r)
                        with m3: st.metric(label="🟢 INICIADO", value=i)
        
        with c_sp:
            st.markdown('<div style="font-size:18px; font-weight: bold; margin-bottom: 10px; color: #b30000; text-align: center;">SÃO PAULO (SP)</div>', unsafe_allow_html=True)
            if not df_sp.empty:
                matriz_sp = df_sp.groupby('SUPERVISOR_MOSTRAR')[['P_COUNT', 'R_COUNT', 'I_COUNT']].sum().reset_index()
                for _, dados in matriz_sp.iterrows():
                    superv = dados['SUPERVISOR_MOSTRAR']
                    p, r, i = int(dados['P_COUNT']), int(dados['R_COUNT']), int(dados['I_COUNT'])
                    with st.container(border=True):
                        st.markdown(f'<div style="font-size:20px; font-weight:bold; margin-bottom:10px;">📋 {superv} <span style="float:right; font-size:14px; background-color:#e1f5fe; padding:2px 8px; border-radius:4px; color:#0288d1;">Total: {p+r+i}</span></div>', unsafe_allow_html=True)
                        m1, m2, m3 = st.columns(3)
                        with m1: st.markdown(f'<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 PENDENTES</div><div class="custom-pendente-value">{p}</div></div>', unsafe_allow_html=True)
                        with m2: st.metric(label="🟣 EM ROTA", value=r)
                        with m3: st.metric(label="🟢 INICIADO", value=i)

    # =========================================================================
    # LÓGICA DA VISÃO: TEC1 CONTRATOS PENDENTES (image_fe6f27.png)
    # =========================================================================
    def renderizar_visao_listagem_pendentes():
        st.markdown('<h1 style="font-size: 32px; font-weight: 900; color: #cc6600; text-align: center; margin-top: 5px; margin-bottom: 5px;">⏳ TEC1 CONTRATOS PENDENTES</h1>', unsafe_allow_html=True)
        
        df_pend = df_limpo[df_limpo['P_COUNT'] > 0].copy()
        df_sp = df_pend[cond_sp].copy()
        df_abc = df_pend Ram[~cond_sp].copy()
        
        c_abc, c_sp = st.columns(2)
        with c_abc:
            st.markdown('<div class="title-abc-sp" style="font-size: 24px; font-weight: 800; text-align: center; color: #005088;">ABC</div>', unsafe_allow_html=True)
            if not df_abc.empty:
                for supervisor in sorted(df_abc['SUPERVISOR_MOSTRAR'].unique()):
                    df_super = df_abc[df_abc['SUPERVISOR_MOSTRAR'] == supervisor]
                    st.markdown(f'<div style="background-color: #f0f2f6; padding: 6px 12px; border-radius: 4px; font-size: 16px; font-weight: bold; color: #333; margin-top: 12px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center; border-left: 5px solid #008080;">👤 {supervisor} <span style="background-color: #ffebee; color: #c62828; padding: 2px 10px; border-radius: 4px; font-size: 13px; font-weight: 900;">Pendentes: {len(df_super)}</span></div>', unsafe_allow_html=True)
                    for _, linha in df_super.iterrows():
                        st.markdown(f'<div style="font-size: 15px; padding: 5px 12px; border-bottom: 1px solid #eee; color: #222;">📄 <span style="font-weight: 900; color: #cc6600; font-size: 16px;">{linha.get("Contrato", "N/A")}</span> <span style="color: #bbb; margin: 0 8px;">|</span> 👤 {str(linha.get(col_tecnico_check, "TÉCNICO")).upper()}</div>', unsafe_allow_html=True)
            else:
                st.success("🎉 Nenhum contrato pendente no ABC para esta janela!")
                
        with c_sp:
            st.markdown('<div class="title-abc-sp" style="font-size: 24px; font-weight: 800; text-align: center; color: #005088;">SÃO PAULO (SP)</div>', unsafe_allow_html=True)
            if not df_sp.empty:
                for supervisor in sorted(df_sp['SUPERVISOR_MOSTRAR'].unique()):
                    df_super = df_sp[df_sp['SUPERVISOR_MOSTRAR'] == supervisor]
                    st.markdown(f'<div style="background-color: #f0f2f6; padding: 6px 12px; border-radius: 4px; font-size: 16px; font-weight: bold; color: #333; margin-top: 12px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center; border-left: 5px solid #b30000;">👤 {supervisor} <span style="background-color: #ffebee; color: #c62828; padding: 2px 10px; border-radius: 4px; font-size: 13px; font-weight: 900;">Pendentes: {len(df_super)}</span></div>', unsafe_allow_html=True)
                    for _, linha in df_super.iterrows():
                        st.markdown(f'<div style="font-size: 15px; padding: 5px 12px; border-bottom: 1px solid #eee; color: #222;">📄 <span style="font-weight: 900; color: #cc6600; font-size: 16px;">{linha.get("Contrato", "N/A")}</span> <span style="color: #bbb; margin: 0 8px;">|</span> 👤 {str(linha.get(col_tecnico_check, "TÉCNICO")).upper()}</div>', unsafe_allow_html=True)
            else:
                st.success("🎉 Nenhum contrato pendente em SP para esta janela!")

    # === CONTROLE DO CARROSSEL DE TEMPO DO PAINEL ROTATIVO ===
    # Mantém a sua lógica existente de alternância usando st.session_state
    if "index_rotacao" not in st.session_state:
        st.session_state["index_rotacao"] = 0

    # Alterna entre as duas visões de forma limpa a cada ciclo de refresh
    if st.session_state["index_rotacao"] == 0:
        renderizar_visao_operacional()
        st.session_state["index_rotacao"] = 1
    else:
        renderizar_visao_listagem_pendentes()
        st.session_state["index_rotacao"] = 0
else:
    st.warning("👈 Por favor, carregue o arquivo de rota na tela inicial primeiro.")

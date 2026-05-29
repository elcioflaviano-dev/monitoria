import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta

# 1. Configuração da página ampla para a TV
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"
TEMPO_ROTACAO_SEGUNDOS = 15  # Tempo exato de cada tela na TV

# --- REFRESH NATIVO VIA HTML METATAG ---
st.markdown(f'<meta http-equiv="refresh" content="{TEMPO_ROTACAO_SEGUNDOS}">', unsafe_allow_html=True)

# --- ⏱️ MOTOR DE ROTAÇÃO POR RELÓGIO REAL (BLINDADO CONTRA RESET DE F5) ---
# Usa os segundos atuais do relógio para definir qual painel mostrar
segundos_atuais = datetime.now().second

# Divide o minuto em blocos de 15 segundos:
# 00 a 14s -> Tela 1
# 15 a 29s -> Tela 2
# 30 a 44s -> Tela 1
# 45 a 59s -> Tela 2
if segundos_atuais < 15 or (segundos_atuais >= 30 and segundos_atuais < 45):
    painel_atual = "TEC1_OPERACIONAL"
else:
    painel_atual = "TEC1_PENDENTES"

# 🔄 HERANÇA INTELIGENTE VIA DISCO RÍGIDO
df_master = None
if os.path.exists(ARQUIVO_ROTA_DISCO):
    try:
        df_master = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    except:
        pass

# 🔥 INJEÇÃO DE CSS AGRESSIVA (ZERA O MENU DIRETO NA RAIZ DO NAVEGADOR)
st.markdown("""
    <style>
        /* Desativa e apaga qualquer elemento de sidebar na marra */
        section[data-testid="stSidebar"], 
        [data-testid="stSidebar"], 
        div[data-testid="stSidebarCollapseButton"],
        button[data-testid="stSidebarCollapseButton"] {
            display: none !important;
            visibility: hidden !important;
            width: 0px !important;
            transform: translateX(-100%) !important;
        }
        
        /* Força a área principal a ocupar 100% da tela sem recuo esquerdo */
        section.main, .stAppDeployButton {
            margin-left: 0px !important;
            padding-left: 0px !important;
        }
        
        /* Dá 80px de espaço no topo para o título */
        .block-container { padding-top: 80px !important; padding-bottom: 5px !important; }
        .stDeployButton { display:none; }
        
        /* Barra preta fixada no topo absoluto da tela */
        .barra-status-tv {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 999995;
            background-color: #111; color: #fff; padding: 10px 20px;
            font-size: 13px; font-weight: bold; display: flex; justify-content: space-between; align-items: center;
            font-family: sans-serif;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        }
        
        /* Botão de voltar customizado para a Home */
        .btn-voltar-home {
            background-color: #cc6600;
            color: white !important;
            padding: 5px 12px;
            border-radius: 4px;
            text-decoration: none !important;
            font-size: 12px;
            font-weight: bold;
            transition: 0.2s;
        }
        .btn-voltar-home:hover {
            background-color: #ff8811;
        }
        
        .title-abc-sp { font-size: 24px !important; font-weight: 800 !important; margin-bottom: 10px !important; text-align: center; color: #005088; }
        .super-bar {
            background-color: #f0f2f6; padding: 6px 12px; border-radius: 4px; font-size: 16px;
            font-weight: bold; color: #333; margin-top: 12px; margin-bottom: 6px;
            display: flex; justify-content: space-between; align-items: center; border-left: 5px solid #cc6600;
        }
        .super-total { background-color: #ffebee; color: #c62828; padding: 2px 10px; border-radius: 4px; font-size: 13px; font-weight: 900; }
        .item-linha { font-size: 16px; padding: 5px 12px; border-bottom: 1px solid #eee; color: #222; }
        .item-contrato { font-weight: 900; color: #cc6600; font-size: 17px; }
        .divisor-item { color: #bbb; margin: 0 8px; }
        .custom-pendente-box { background-color: #ffebee; padding: 5px; border-radius: 4px; text-align: center; }
        .custom-pendente-label { font-size: 10px; font-weight: bold; color: #c62828; }
        .custom-pendente-value { font-size: 18px; font-weight: 900; color: #c62828; }
    </style>
""", unsafe_allow_html=True)

# Barra fixa superior com link direto para a página inicial (Home)
st.markdown(f'''
    <div class="barra-status-tv">
        <div>
            <a href="/" target="_self" class="btn-voltar-home">🏠 VOLTAR PARA A HOME</a>
            <span style="margin-left: 15px;">📺 MODO TV ATIVO • EXIBINDO: {painel_atual.replace("_", " ")}</span>
        </div>
        <span>🔄 Sincronizado por Relógio • Próximo giro em 15s</span>
    </div>
''', unsafe_allow_html=True)


# =============================================================================
# OPERATIONAL LOGIC (Processamento de dados unificado)
# =============================================================================
if df_master is not None and not df_master.empty:
    df = df_master.copy()
    
    col_tecnico_check = None
    for c in df.columns:
        if 'TECNICO' in str(c).upper() or 'LOGIN' in str(c).upper(): 
            col_tecnico_check = c
            break
            
    if col_tecnico_check:
        df = df[df[col_tecnico_check].fillna('').astype(str).str.strip() != ''].copy()
    
    if 'Contrato' in df.columns:
        df['Contrato'] = df['Contrato'].fillna('').astype(str).apply(lambda x: x.split('.')[0] if '.' in x else x).str.strip()
        df = df[df['Contrato'] != ''].copy()

    df['Status_Atividade_Upper'] = df['STATUS_ATIVIDADE'].fillna('').astype(str).str.upper().str.strip() if 'STATUS_ATIVIDADE' in df.columns else ''
    df_limpo = df[df['Status_Atividade_Upper'] != 'SUSPENSO'].copy()
    
    if 'Tipo de Atividade' in df_limpo.columns:
        df_limpo['Tipo_Activity_Str'] = df_limpo['Tipo de Atividade'].fillna('').astype(str)
        df_limpo = df_limpo[~df_limpo['Tipo_Activity_Str'].str.contains('Refeicao', case=False, na=False)]

    df_limpo['P_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('PENDENTE|EM ABERTO|ABERTO', na=False).astype(int)
    df_limpo['R_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('ROTA|DESLOC|DESLOCAMENTO', na=False).astype(int)
    df_limpo['I_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('INICIADO|PRODUTIVO|EXECUCAO|INIC', na=False).astype(int)

    col_janela = None
    for c in df_limpo.columns:
        if 'JANELA' in str(c).upper() or 'INTERVALO' in str(c).upper(): 
            col_janela = c
            break

    if col_janela is not None and not df_limpo.empty:
        df_limpo['Intervalo_Tratado'] = df_limpo[col_janela].fillna('').astype(str).str.strip()
        hora_atual = (datetime.utcnow() - timedelta(hours=3)).hour
        def extrair_hora_limite(janela_str):
            try:
                partes = janela_str.replace(':', '').split('-')
                return int(partes[1].strip()[:2]) if len(partes) == 2 else 24
            except: return 24
        df_limpo['Hora_Limite_Janela'] = df_limpo['Intervalo_Tratado'].apply(extrair_hora_limite)
        df_janela_ativa = df_limpo[df_limpo['Hora_Limite_Janela'] <= (hora_atual + 1)].copy()
        if df_janela_ativa.empty: df_janela_ativa = df_limpo.copy()
    else:
        df_janela_ativa = df_limpo.copy()

    if 'SUPERVISOR' in df_janela_ativa.columns:
        df_janela_ativa['SUPERVISOR_MOSTRAR'] = df_janela_ativa['SUPERVISOR'].fillna('PENDENTE CADASTRO').replace({'#N/A': 'PENDENTE CADASTRO', 'NAN': 'PENDENTE CADASTRO', '': 'PENDENTE CADASTRO'}).astype(str).str.upper().str.strip()
    else:
        df_janela_ativa['SUPERVISOR_MOSTRAR'] = 'PENDENTE CADASTRO'

    cond_sp = (df_janela_ativa['REGIAO_BASE'].fillna('').astype(str).str.upper().str.contains('SÃO PAULO|SP', na=False) | df_janela_ativa['SUPERVISOR_MOSTRAR'].str.contains('FRANCISCO|ALAN', na=False))
    df_sp = df_janela_ativa[cond_sp].copy()
    df_abc = df_janela_ativa[~cond_sp].copy()

    # =========================================================================
    # VISUAL 1: TEC1 OPERACIONAL
    # =========================================================================
    if painel_atual == "TEC1_OPERACIONAL":
        st.markdown('<h1 style="font-size: 36px; font-weight: 900; color: #006677; text-align: center; margin-bottom: 15px;">📊 TEC1 OPERACIONAL</h1>', unsafe_allow_html=True)
        
        col_coluna_abc, col_coluna_sp = st.columns(2)
        with col_coluna_abc:
            st.markdown('<div style="font-size:18px; font-weight: bold; margin-bottom: 10px; color: #008080; text-align: center;">ABC</div>', unsafe_allow_html=True)
            df_abc_ops = df_abc[(df_abc['P_COUNT'] > 0) | (df_abc['R_COUNT'] > 0) | (df_abc['I_COUNT'] > 0)].copy()
            if not df_abc_ops.empty:
                matriz_abc = df_abc_ops.groupby('SUPERVISOR_MOSTRAR')[['P_COUNT', 'R_COUNT', 'I_COUNT']].sum().reset_index()
                for _, dados_super in matriz_abc.iterrows():
                    sup = dados_super['SUPERVISOR_MOSTRAR']
                    p, r, i = int(dados_super['P_COUNT']), int(dados_super['R_COUNT']), int(dados_super['I_COUNT'])
                    with st.container(border=True):
                        st.markdown(f'<div style="font-size:18px; font-weight:bold; margin-bottom:8px;">📋 {sup} <span style="float:right; font-size:13px; background-color:#e1f5fe; padding:2px 8px; border-radius:4px; color:#0288d1;">Total: {p+r+i}</span></div>', unsafe_allow_html=True)
                        m1, m2, m3 = st.columns(3)
                        with m1: st.markdown(f'<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 PENDENTES</div><div class="custom-pendente-value">{p}</div></div>', unsafe_allow_html=True)
                        with m2: st.metric(label="🟣 EM ROTA", value=r)
                        with m3: st.metric(label="🟢 INICIADO", value=i)
            else: st.info("Nenhum contrato ativo para o ABC nesta janela.")

        with col_coluna_sp:
            st.markdown('<div style="font-size:18px; font-weight: bold; margin-bottom: 10px; color: #b30000; text-align: center;">SÃO PAULO (SP)</div>', unsafe_allow_html=True)
            df_sp_ops = df_sp[(df_sp['P_COUNT'] > 0) | (df_sp['R_COUNT'] > 0) | (df_sp['I_COUNT'] > 0)].copy()
            if not df_sp_ops.empty:
                matriz_sp = df_sp_ops.groupby('SUPERVISOR_MOSTRAR')[['P_COUNT', 'R_COUNT', 'I_COUNT']].sum().reset_index()
                for _, dados_super in matriz_sp.iterrows():
                    sup = dados_super['SUPERVISOR_MOSTRAR']
                    p, r, i = int(dados_super['P_COUNT']), int(dados_super['R_COUNT']), int(dados_super['I_COUNT'])
                    with st.container(border=True):
                        st.markdown(f'<div style="font-size:18px; font-weight:bold; margin-bottom:8px;">📋 {sup} <span style="float:right; font-size:13px; background-color:#e1f5fe; padding:2px 8px; border-radius:4px; color:#0288d1;">Total: {p+r+i}</span></div>', unsafe_allow_html=True)
                        m1, m2, m3 = st.columns(3)
                        with m1: st.markdown(f'<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 PENDENTES</div><div class="custom-pendente-value">{p}</div></div>', unsafe_allow_html=True)
                        with m2: st.metric(label="🟣 EM ROTA", value=r)
                        with m3: st.metric(label="🟢 INICIADO", value=i)
            else: st.info("Nenhum contrato ativo para SP nesta janela.")

    # =========================================================================
    # VISUAL 2: TEC1 PENDENTES
    # =========================================================================
    elif painel_atual == "TEC1_PENDENTES":
        st.markdown('<h1 style="font-size: 32px; font-weight: 900; color: #cc6600; text-align: center; margin-bottom: 15px;">⏳ TEC1 CONTRATOS PENDENTES</h1>', unsafe_allow_html=True)
        
        df_abc_p = df_abc[df_abc['P_COUNT'] > 0].copy()
        df_sp_p = df_sp[df_sp['P_COUNT'] > 0].copy()

        col_coluna_abc, col_coluna_sp = st.columns(2)
        with col_coluna_abc:
            st.markdown('<div class="title-abc-sp">ABC</div>', unsafe_allow_html=True)
            if not df_abc_p.empty:
                for supervisor in sorted(df_abc_p['SUPERVISOR_MOSTRAR'].unique()):
                    df_super = df_abc_p[df_abc_p['SUPERVISOR_MOSTRAR'] == supervisor]
                    st.markdown(f'<div class="super-bar">👤 {supervisor} <span class="super-total">Pendentes: {len(df_super)}</span></div>', unsafe_allow_html=True)
                    for _, linha in df_super.iterrows():
                        st.markdown(f'<div class="item-linha">📄 <span class="item-contrato">{linha.get("Contrato", "N/A")}</span> <span class="divisor-item">|</span> 👤 {str(linha.get("Recurso", "TÉCNICO")).upper()}</div>', unsafe_allow_html=True)
            else: st.success("🎉 Nenhum contrato pendente no ABC para esta janela!")

        with col_coluna_sp:
            st.markdown('<div class="title-abc-sp">SÃO PAULO (SP)</div>', unsafe_allow_html=True)
            if not df_sp_p.empty:
                for supervisor in sorted(df_sp_p['SUPERVISOR_MOSTRAR'].unique()):
                    df_super = df_sp_p[df_sp_p['SUPERVISOR_MOSTRAR'] == supervisor]
                    st.markdown(f'<div class="super-bar">👤 {supervisor} <span class="super-total">Pendentes: {len(df_super)}</span></div>', unsafe_allow_html=True)
                    for _, linha in df_super.iterrows():
                        st.markdown(f'<div class="item-linha">📄 <span class="item-contrato">{linha.get("Contrato", "N/A")}</span> <span class="divisor-item">|</span> 👤 {str(linha.get("Recurso", "TÉCNICO")).upper()}</div>', unsafe_allow_html=True)
            else: st.success("🎉 Nenhum contrato pendente em SP para esta janela!")
else:
    st.warning("👈 Por favor, insira os arquivos de rota na página inicial primeiro.")

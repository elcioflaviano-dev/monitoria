import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta

# Configura a página para ocupar toda a largura da tela
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

# 🔄 HERANÇA INTELIGENTE VIA DISCO RÍGIDO (À PROVA DE QUEDAS DE SESSÃO)
if ('df_rota_ativa' not in st.session_state or st.session_state['df_rota_ativa'] is None) and os.path.exists(ARQUIVO_ROTA_DISCO):
    try:
        st.session_state['df_rota_ativa'] = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    except:
        pass

# 🚀 SISTEMA DE REFRESH AUTOMÁTICO PARA A TV (30 Segundos para monitoramento de pendências)
if 'df_rota_ativa' in st.session_state and st.session_state['df_rota_ativa'] is not None:
    if "last_refresh_pendentes" not in st.session_state:
        st.session_state["last_refresh_pendentes"] = time.time()
    
    # 🌟 CORREÇÃO: Removido st.text_input antigo para eliminar o vazamento de números soltos no topo
    if time.time() - st.session_state["last_refresh_pendentes"] > 30:
        st.session_state["last_refresh_pendentes"] = time.time()
        st.rerun()

# Injeta CSS customizado para remover margens desnecessárias e ajustar fontes grandes
st.markdown("""
    <style>
        .block-container { padding-top: 10px !important; padding-bottom: 5px !important; }
        .stDeployButton { display:none; }
        .title-abc-sp { font-size: 24px !important; font-weight: 800 !important; margin-bottom: 10px !important; text-align: center; color: #005088; }
        
        /* Barra do Supervisor com Total na mesma linha */
        .super-bar {
            background-color: #f0f2f6;
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 16px;
            font-weight: bold;
            color: #333;
            margin-top: 12px;
            margin-bottom: 6px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-left: 5px solid #cc6600;
        }
        .super-total {
            background-color: #ffebee;
            color: #c62828;
            padding: 2px 10px;
            border-radius: 4px;
            font-size: 13px;
            font-weight: 900;
        }
        
        /* Linhas dos Contratos e Técnicos OTIMIZADAS e MAIORES */
        .item-linha {
            font-size: 16px;
            padding: 5px 12px;
            border-bottom: 1px solid #eee;
            color: #222;
        }
        .item-contrato {
            font-weight: 900;
            color: #cc6600;
            font-size: 17px;
        }
        .divisor-item {
            color: #bbb;
            margin: 0 8px;
        }
    </style>
""", unsafe_allow_html=True)

# Título Principal Enxuto
st.markdown(
    '<h1 style="font-size: 32px; font-weight: 900; color: #cc6600; text-align: center; margin-top: 5px; margin-bottom: 5px;">⏳ TEC1 PENDENTES</h1>', 
    unsafe_allow_html=True
)

df_master = st.session_state.get('df_rota_ativa', None)

if df_master is not None and not df_master.empty:
    df = df_master.copy()
    
    # === PASSO 1: LIMPEZA DE LINHAS VAZIAS E TRATAMENTO DE .0 ===
    col_tecnico_check = 'Login do Técnico' if 'Login do Técnico' in df.columns else None
    if not col_tecnico_check:
        for c in df.columns:
            if 'TECNICO' in str(c).upper() or 'LOGIN' in str(c).upper():
                col_tecnico_check = c
                break
                
    if col_tecnico_check:
        df = df[df[col_tecnico_check].fillna('').astype(str).str.strip() != ''].copy()
    
    # Remove o ".0" limpando strings de contrato vazias
    if 'Contrato' in df.columns:
        df['Contrato'] = df['Contrato'].fillna('').astype(str).apply(lambda x: x.split('.')[0] if '.' in x else x).str.strip()
        df = df[df['Contrato'] != ''].copy()

    # === ALINHAMENTO DE COLUNAS OPERACIONAIS ===
    df['Status_Atividade_Upper'] = df['STATUS_ATIVIDADE'].fillna('').astype(str).str.upper().str.strip() if 'STATUS_ATIVIDADE' in df.columns else ''
    df_limpo = df[df['Status_Atividade_Upper'] != 'SUSPENSO'].copy()
    
    if 'Tipo de Atividade' in df_limpo.columns:
        df_limpo['Tipo_Activity_Str'] = df_limpo['Tipo de Atividade'].fillna('').astype(str)
        df_limpo = df_limpo[~df_limpo['Tipo_Activity_Str'].str.contains('Refeicao', case=False, na=False)]

    # PASSO 2: FILTRAGEM PRÉVIA DOS CONTRATOS PENDENTES
    df_limpo['P_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('PENDENTE|EM ABERTO|ABERTO', na=False).astype(int)
    df_validos = df_limpo[df_limpo['P_COUNT'] > 0].copy()
        
    col_janela = 'Janela de Serviço' if 'Janela de Serviço' in df_validos.columns else None
    if not col_janela:
        for c in df_validos.columns:
            if 'JANELA' in str(c).upper() or 'INTERVALO' in str(c).upper(): col_janela = c; break
            
    if col_janela is not None and not df_validos.empty:
        df_validos['Intervalo_Tratado'] = df_validos[col_janela].fillna('').astype(str).str.strip()
        
        # MOTOR AUTOMÁTICO POR HORÁRIO OPERACIONAL (FUSO SÃO PAULO)
        hora_atual = (datetime.utcnow() - timedelta(hours=3)).hour
        
        def extrair_hora_limite(janela_str):
            try:
                partes = janela_str.replace(':', '').split('-')
                if len(partes) == 2:
                    return int(partes[1].strip()[:2])
                return 24
            except:
                return 24

        df_validos['Hora_Limite_Janela'] = df_validos['Intervalo_Tratado'].apply(extrair_hora_limite)
        
        # 🌟 CORREÇÃO DA JANELA OPERACIONAL (Igualamos a margem de +2 horas do TEC1)
        df_tela = df_validos[df_validos['Hora_Limite_Janela'] <= (hora_atual + 2)].copy()
        
        # Fallback de segurança
        if df_tela.empty:
            df_tela = df_validos.copy()
            st.markdown(f'<div style="text-align: center; color: #cc6600; font-size: 14px; font-weight: bold; margin-bottom: 15px;">⏰ [Hora Local: {hora_atual:02d}h] - Mostrando Todos os Pendentes Acumulados</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="text-align: center; color: #008080; font-size: 14px; font-weight: bold; margin-bottom: 15px;">🔄 Fila Dinâmica Ativa [Hora Local: {hora_atual:02d}h]</div>', unsafe_allow_html=True)
    else:
        df_tela = df_validos.copy()

    if df_tela.empty:
        st.warning("⚠️ Não existem contratos pendentes para esta janela.")
    else:
        # Identifica o nome ou login do recurso
        col_rec = 'Recurso' if 'Recurso' in df_tela.columns else None
        if not col_rec:
            for c in df_tela.columns:
                if 'TECNICO' in str(c).upper() or 'LOGIN' in str(c).upper(): col_rec = c; break
        df_tela['Recurso_Tratado'] = df_tela[col_rec].fillna('TÉCNICO').astype(str).str.upper() if col_rec else 'TÉCNICO'

        # Define quem vai aparecer no topo do cartão
        if 'SUPERVISOR' in df_tela.columns:
            df_tela['SUPERVISOR_MOSTRAR'] = df_tela.apply(
                lambda r: str(r['Recurso_Tratado']).upper() if str(r['SUPERVISOR']).strip().upper() in ['#N/A', 'NAN', '', 'PENDENTE CADASTRO'] else str(r['SUPERVISOR']).upper(), axis=1
            )
        else:
            df_tela['SUPERVISOR_MOSTRAR'] = df_tela['Recurso_Tratado']
            
        df_tela['SUPERVISOR_MOSTRAR'] = df_tela['SUPERVISOR_MOSTRAR'].astype(str).str.upper().str.strip()

        # Divisão Regional utilizando as travas de segurança da Home
        cond_sp = (
            df_tela['REGIAO_BASE'].fillna('').astype(str).str.upper().str.strip().str.contains('SÃO PAULO|SP', na=False) |
            df_tela['SUPERVISOR_MOSTRAR'].str.contains('FRANCISCO|ALAN', na=False)
        )
        
        df_sp = df_tela[cond_sp].copy()
        df_abc = df_tela[~cond_sp].copy()

        # Renderização Lado a Lado
        col_coluna_abc, col_coluna_sp = st.columns(2)
        
        with col_coluna_abc:
            st.markdown('<div class="title-abc-sp">ABC</div>', unsafe_allow_html=True)
            if not df_abc.empty:
                supervisores_abc = sorted(df_abc['SUPERVISOR_MOSTRAR'].unique())
                for supervisor in supervisores_abc:
                    df_super = df_abc[df_abc['SUPERVISOR_MOSTRAR'] == supervisor]
                    total_pendentes = df_super['P_COUNT'].sum()
                    
                    st.markdown(f'<div class="super-bar">👤 {supervisor} <span class="super-total">Pendentes: {total_pendentes}</span></div>', unsafe_allow_html=True)
                    
                    for idx, linha in df_super.iterrows():
                        contrato_num = linha.get('Contrato', 'N/A')
                        tecnico_nome = linha.get('Recurso_Tratado', 'N/A')
                        st.markdown(f'<div class="item-linha">📄 <span class="item-contrato">{contrato_num}</span> <span class="divisor-item">|</span> 👤 {tecnico_nome}</div>', unsafe_allow_html=True)
            else:
                st.info("Nenhum pendente no ABC.")

        with col_coluna_sp:
            st.markdown('<div class="title-abc-sp">SÃO PAULO (SP)</div>', unsafe_allow_html=True)
            if not df_sp.empty:
                supervisores_sp = sorted(df_sp['SUPERVISOR_MOSTRAR'].unique())
                for supervisor in supervisores_sp:
                    df_super = df_sp[df_sp['SUPERVISOR_MOSTRAR'] == supervisor]
                    total_pendentes = df_super['P_COUNT'].sum()
                    
                    st.markdown(f'<div class="super-bar">👤 {supervisor} <span class="super-total">Pendentes: {total_pendentes}</span></div>', unsafe_allow_html=True)
                    
                    for idx, linha in df_super.iterrows():
                        contrato_num = linha.get('Contrato', 'N/A')
                        tecnico_nome = linha.get('Recurso_Tratado', 'N/A')
                        st.markdown(f'<div class="item-linha">📄 <span class="item-contrato">{contrato_num}</span> <span class="divisor-item">|</span> 👤 {tecnico_nome}</div>', unsafe_allow_html=True)
            else:
                st.info("Nenhum pendente em SP.")
else:
    st.warning("👈 Insira os arquivos na página inicial primeiro.")

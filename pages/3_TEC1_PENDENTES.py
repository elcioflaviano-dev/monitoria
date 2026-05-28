import streamlit as st
import pandas as pd
from datetime import datetime

# Configura a página para ocupar toda a largura da tela
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

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
            font-size: 16px; /* Fonte aumentada para Modo TV */
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

# 🔄 HERANÇA INTELIGENTE
df_master = st.session_state.get('df_rota_ativa', None)

if df_master is not None and not df_master.empty:
    df = df_master.copy()
    
    # === PASSO 1: LIMPEZA DE LINHAS VAZIAS ===
    col_tecnico_check = 'Login do Técnico' if 'Login do Técnico' in df.columns else None
    if not col_tecnico_check:
        for c in df.columns:
            if 'TECNICO' in str(c).upper() or 'LOGIN' in str(c).upper():
                col_tecnico_check = c
                break
                
    if col_tecnico_check:
        df = df[df[col_tecnico_check].fillna('').astype(str).str.strip() != ''].copy()
    
    if 'Contrato' in df.columns:
        df = df[df['Contrato'].fillna('').astype(str).str.strip() != ''].copy()

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
        df_janelas_filtradas = df_validos[(df_validos['Intervalo_Tratado'] != '') & (df_validos['Intervalo_Tratado'].str.len() <= 7)].copy()
        opcoes_janela = sorted(df_janelas_filtradas['Intervalo_Tratado'].dropna().unique())
        
        if opcoes_janela:
            janela_sel = st.sidebar.selectbox("Janela de Serviço:", opcoes_janela)
            df_tela = df_validos[df_validos['Intervalo_Tratado'] == janela_sel].copy()
        else:
            df_tela = df_validos.copy()
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
                    
                    # 🌟 LISTA DE TEXTO LIMPA: Sem as palavras repetitivas e com fonte maior
                    for idx, linha in df_super.iterrows():
                        contrato_num = linha.get('Contrato', 'N/A')
                        tecnico_nome = linha.get('Recurso_Tratado', 'N/A')
                        st.markdown(f'<div class="item-linha">📄 <span class="item-contrato">{contrato_num}</span> <span class="divisor-item">|</span> 👤 {tecnico_nome}</div>', unsafe_allow_html=True)
            else:
                st.info("Nenhum pendente no ABC.")

        with col_coluna_sp:
            st.markdown('<div class="title-abc-

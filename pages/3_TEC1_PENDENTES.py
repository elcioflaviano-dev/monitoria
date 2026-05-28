import streamlit as st
import pandas as pd
from datetime import datetime

# Configura a página para ocupar toda a largura da tela (Idêntico ao TEC1)
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Abre e injeta o arquivo style.css externo
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

# Título Centralizado no mesmo padrão visual
st.markdown(
    '<h1 style="font-size: 42px; font-weight: 900; color: #cc6600; text-align: center; margin-top: 25px; margin-bottom: 5px;">TEC1 PENDENTES</h1>', 
    unsafe_allow_html=True
)

# 🔄 HERANÇA INTELIGENTE: Puxa o DataFrame unificado da memória global (Home)
df_master = st.session_state.get('df_rota_ativa', None)

st.markdown(f'<div style="text-align: center; color: #555; font-size: 13px; font-weight: bold; margin-bottom: 20px;">🔄 Base sincronizada em tempo real via Upload</div>', unsafe_allow_html=True)

if df_master is not None and not df_master.empty:
    df = df_master.copy()
    
    # === PASSO 1: LIMPEZA ABSOLUTA DE LINHAS VAZIAS ===
    col_tecnico_check = 'Login do Técnico' if 'Login do Técnico' in df.columns else None
    if not col_tecnico_check:
        for c in df.columns:
            if 'TECNICO' in str(c).upper() or 'LOGIN' in str(c).upper():
                col_tecnico_check = c
                break
                
    if col_tecnico_check:
        df = df[df[col_tecnico_check].fillna('').astype(str).str.strip() != ''].copy()
        df = df[df[col_tecnico_check].fillna('').astype(str).str.upper() != 'NAN'].copy()
    
    if 'Contrato' in df.columns:
        df = df[df['Contrato'].fillna('').astype(str).str.strip() != ''].copy()
        df = df[df['Contrato'].fillna('').astype(str).str.upper() != 'NAN'].copy()

    # === ALINHAMENTO DE COLUNAS OPERACIONAIS ===
    df['Status_Atividade_Upper'] = df['STATUS_ATIVIDADE'].fillna('').astype(str).str.upper().str.strip() if 'STATUS_ATIVIDADE' in df.columns else ''
    
    # Filtragem de segurança: Remove suspensos
    df_limpo = df[df['Status_Atividade_Upper'] != 'SUSPENSO'].copy()
    
    # Remove as marcações operacionais de almoço (Refeicao)
    if 'Tipo de Atividade' in df_limpo.columns:
        df_limpo['Tipo_Activity_Str'] = df_limpo['Tipo de Atividade'].fillna('').astype(str)
        df_limpo = df_limpo[~df_limpo['Tipo_Activity_Str'].str.contains('Refeicao', case=False, na=False)]

    # PASSO 2: MARCAÇÃO E FILTRAGEM PRÉVIA DOS CONTRATOS PENDENTES
    df_limpo['P_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('PENDENTE|EM ABERTO|ABERTO', na=False).astype(int)
    
    # Mantém estritamente os contratos com status pendentes ativos antes de verificar os horários
    df_validos = df_limpo[df_limpo['P_COUNT'] > 0].copy()
        
    # Tratamento e montagem do filtro dinâmico de Janelas
    col_janela = 'Janela de Serviço' if 'Janela de Serviço' in df_validos.columns else None
    if not col_janela:
        for c in df_validos.columns:
            if 'JANELA' in str(c).upper() or 'INTERVALO' in str(c).upper():
                col_janela = c
                break
            
    if col_janela is not None and not df_validos.empty:
        df_validos['Intervalo_Tratado'] = df_validos[col_janela].fillna('').astype(str).str.strip()
        
        # Filtra a lista de opções para remover horários quebrados/sujeira
        df_janelas_filtradas = df_validos[
            (df_validos['Intervalo_Tratado'] != '') & 
            (~df_validos['Intervalo_Tratado'].str.upper().str.contains('SEM JANELA')) &
            (df_validos['Intervalo_Tratado'].str.len() <= 7)
        ].copy()
        
        opcoes_janela = sorted(df_janelas_filtradas['Intervalo_Tratado'].dropna().unique())
        opcoes_janela = [j for j in opcoes_janela if j.upper() not in ['NAN', 'NONE', 'N/A']]
        
        if opcoes_janela:
            janela_sel = st.sidebar.selectbox("Janela de Serviço:", opcoes_janela)
            df_tela = df_validos[df_validos['Intervalo_Tratado'] == janela_sel].copy()
        else:
            df_tela = df_validos.copy()
    else:
        df_tela = df_validos.copy()

    if df_tela.empty:
        st.warning("⚠️ Não existem contratos pendentes para os filtros aplicados nesta janela.")
    else:
        # Identifica o nome ou login do recurso
        col_rec = 'Recurso' if 'Recurso' in df_tela.columns else None
        if not col_rec:
            for c in df_tela.columns:
                if 'TECNICO' in str(c).upper() or 'LOGIN' in str(c).upper():
                    col_rec = c
                    break
        df_tela['Recurso_Tratado'] = df_tela[col_rec].fillna('TÉCNICO PENDENTE').astype(str).str.upper() if col_rec else 'TÉCNICO PENDENTE'

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

        col_coluna_abc, col_coluna_sp = st.columns(2)
        
        with col_coluna_abc:
            st.markdown('<div class="title-abc-sp">ABC</div>', unsafe_allow_html=True)
            
            if not df_abc.empty:
                # Pega a lista de supervisores únicos
                supervisores_abc = sorted(df_abc['SUPERVISOR_MOSTRAR'].unique())
                
                for supervisor in supervisores_abc:
                    df_super = df_abc[df_abc['SUPERVISOR_MOSTRAR'] == supervisor]
                    total_pendentes = df_super['P_COUNT'].sum()
                    
                    with st.container(border=True):
                        st.markdown('<div style="font-size:18px; font-weight:bold; margin-bottom:10px;">👤 ' + str(supervisor) + '</div>', unsafe_allow_html=True)
                        st.markdown('<div class="custom-pendente-box" style="width: 100%; margin-bottom:12px;"><div class="custom-pendente-label">🔴 CONTRATOS PENDENTES</div><div class="custom-pendente-value">' + str(total_pendentes) + '</div></div>', unsafe_allow_html=True)
                        
                        # 🌟 NOVO: Lista aberta de contratos e técnicos deste bloco
                        df_lista_super = df_super[['Contrato', 'Recurso_Tratado']].copy()
                        df_lista_super = df_lista_super.rename(columns={'Contrato': 'Nº Contrato', 'Recurso_Tratado': 'Técnico / Login'})
                        st.dataframe(df_lista_super, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhum contrato pendente localizado para o ABC nesta janela.")

        with col_coluna_sp:
            st.markdown('<div class="title-abc-sp">SÃO PAULO (SP)</div>', unsafe_allow_html=True)
            
            if not df_sp.empty:
                # Pega a lista de supervisores únicos
                supervisores_sp = sorted(df_sp['SUPERVISOR_MOSTRAR'].unique())
                
                for supervisor in supervisores_sp:
                    df_super = df_sp[df_sp['SUPERVISOR_MOSTRAR'] == supervisor]
                    total_pendentes = df_super['P_COUNT'].sum()
                    
                    with st.container(border=True):
                        st.markdown('<div style="font-size:18px; font-weight:bold; margin-bottom:10px;">👤 ' + str(supervisor) + '</div>', unsafe_allow_html=True)
                        st.markdown('<div class="custom-pendente-box" style="width: 100%; margin-bottom:12px;"><div class="custom-pendente-label">🔴 CONTRATOS PENDENTES</div><div class="custom-pendente-value">' + str(total_pendentes) + '</div></div>', unsafe_allow_html=True)
                        
                        # 🌟 NOVO: Lista aberta de contratos e técnicos deste bloco
                        df_lista_super = df_super[['Contrato', 'Recurso_Tratado']].copy()
                        df_lista_super = df_lista_super.rename(columns={'Contrato': 'Nº Contrato', 'Recurso_Tratado': 'Técnico / Login'})
                        st.dataframe(df_lista_super, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhum contrato pendente localizado para SP nesta janela.")

    # MODO TV AUTOMÁTICO
    st.components.v1.html("""
        <script>
        setTimeout(function(){ window.parent.location.hash = "#certidao"; }, 30000);
        </script>
    """, height=0)
else:
    st.warning("👈 Por favor, faça o upload dos arquivos de rota na página inicial (streamlit_app.py) primeiro.")

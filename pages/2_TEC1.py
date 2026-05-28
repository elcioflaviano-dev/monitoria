import streamlit as st
import pandas as pd
from datetime import datetime

# Configura a página para ocupar toda a largura da tela (Igual ao original)
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Abre e injeta o arquivo style.css externo
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

# Título Centralizado
st.markdown(
    '<h1 style="font-size: 42px; font-weight: 900; color: #006677; text-align: center; margin-top: 25px; margin-bottom: 5px;">TEC1</h1>', 
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
    
    # Filtragem: Remove suspensos
    df_limpo = df[df['Status_Atividade_Upper'] != 'SUSPENSO'].copy()
    
    # Remove as marcações operacionais de almoço (Refeicao)
    if 'Tipo de Atividade' in df_limpo.columns:
        df_limpo['Tipo_Activity_Str'] = df_limpo['Tipo de Atividade'].fillna('').astype(str)
        df_limpo = df_limpo[~df_limpo['Tipo_Activity_Str'].str.contains('Refeicao', case=False, na=False)]
        
    # Tratamento e montagem do filtro dinâmico de Janelas
    col_janela = 'Janela de Serviço' if 'Janela de Serviço' in df_limpo.columns else None
    if not col_janela:
        for c in df_limpo.columns:
            if 'JANELA' in str(c).upper() or 'INTERVALO' in str(c).upper():
                col_janela = c
                break
            
    if col_janela is not None:
        df_limpo['Intervalo_Tratado'] = df_limpo[col_janela].fillna('').astype(str).str.strip()
        df_janelas_validas = df_limpo[
            (df_limpo['Intervalo_Tratado'] != '') & 
            (~df_limpo['Intervalo_Tratado'].str.upper().str.contains('SEM JANELA'))
        ].copy()
        
        opcoes_janela = sorted(df_janelas_validas['Intervalo_Tratado'].dropna().unique())
        opcoes_janela = [j for j in opcoes_janela if j.upper() not in ['NAN', 'NONE', 'N/A']]
        
        if opcoes_janela:
            janela_sel = st.sidebar.selectbox("Janela de Serviço:", opcoes_janela)
            df_tela = df_limpo[df_limpo['Intervalo_Tratado'] == janela_sel].copy()
        else:
            df_tela = df_limpo.copy()
    else:
        df_tela = df_limpo.copy()

    if df_tela.empty:
        st.warning("⚠️ Não existem dados correspondentes para os filtros aplicados nesta janela.")
    else:
        # Cria as colunas de soma dos status operacionais
        df_tela['P_COUNT'] = df_tela['Status_Atividade_Upper'].str.contains('PENDENTE|EM ABERTO|ABERTO', na=False).astype(int)
        df_tela['R_COUNT'] = df_tela['Status_Atividade_Upper'].str.contains('ROTA|DESLOC|DESLOCAMENTO', na=False).astype(int)
        df_tela['I_COUNT'] = df_tela['Status_Atividade_Upper'].str.contains('INICIADO|PRODUTIVO|EXECUCAO|INIC', na=False).astype(int)
        
        df_tela = df_tela[(df_tela['P_COUNT'] > 0) | (df_tela['R_COUNT'] > 0) | (df_tela['I_COUNT'] > 0)].copy()

        # Padroniza a coluna do Supervisor vinda do PROCV da Home
        if 'SUPERVISOR' in df_tela.columns:
            df_tela['SUPERVISOR_MOSTRAR'] = df_tela['SUPERVISOR'].fillna('PENDENTE CADASTRO').replace({'#N/A': 'PENDENTE CADASTRO', 'NAN': 'PENDENTE CADASTRO', '': 'PENDENTE CADASTRO'})
        else:
            df_tela['SUPERVISOR_MOSTRAR'] = 'PENDENTE CADASTRO'
            
        df_tela['SUPERVISOR_MOSTRAR'] = df_tela['SUPERVISOR_MOSTRAR'].astype(str).str.upper().str.strip()

        # 🌟 SOLUÇÃO DO INVALIDINDEXERROR: Divisão vetorizada rápida e direta (Sem usar iterrows)
        # Cria uma regra de verdadeiro/falso para identificar quem pertence a SP
        cond_sp = (
            df_tela['REGIAO_BASE'].fillna('').astype(str).str.upper().str.strip().str.contains('SÃO PAULO|SP', na=False) |
            df_tela['SUPERVISOR_MOSTRAR'].str.contains('FRANCISCO|ALAN', na=False)
        )
        
        # Filtra os blocos inteiros de uma vez, preservando a integridade das colunas
        df_sp = df_tela[cond_sp].copy()
        df_abc = df_tela[~cond_sp].copy()

        col_coluna_abc, col_coluna_sp = st.columns(2)
        
        with col_coluna_abc:
            st.markdown('<div class="title-abc-sp">ABC</div>', unsafe_allow_html=True)
            
            if not df_abc.empty:
                matriz_abc = df_abc.groupby('SUPERVISOR_MOSTRAR')[['P_COUNT', 'R_COUNT', 'I_COUNT']].sum().reset_index()
                
                for supervisor in sorted(matriz_abc['SUPERVISOR_MOSTRAR'].unique()):
                    dados_super = matriz_abc[matriz_abc['SUPERVISOR_MOSTRAR'] == supervisor].iloc[0]
                    pendentes = int(dados_super['P_COUNT'])
                    em_rota = int(dados_super['R_COUNT'])
                    iniciados = int(dados_super['I_COUNT'])
                    total_real = pendentes + em_rota + iniciados
                    
                    with st.container(border=True):
                        st.markdown('<div style="font-size:20px; font-weight:bold; margin-bottom:10px;">📋 ' + str(supervisor) + ' <span style="float:right; font-size:14px; background-color:#e1f5fe; padding:2px 8px; border-radius:4px; color:#0288d1;">Total Contratos: ' + str(total_real) + '</span></div>', unsafe_allow_html=True)
                        
                        m1, m2, m3 = st.columns(3)
                        with m1: st.markdown('<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 PENDENTES</div><div class="custom-pendente-value">' + str(pendentes) + '</div></div>', unsafe_allow_html=True)
                        with m2: st.metric(label="🟣 EM ROTA", value=em_rota)
                        with m3: st.metric(label="🟢 INICIADO", value=iniciados)
            else:
                st.info("Nenhum contrato ativo para o ABC nesta janela.")

        with col_coluna_sp:
            st.markdown('<div class="title-abc-sp">SÃO PAULO (SP)</div>', unsafe_allow_html=True)
            
            if not df_sp.empty:
                matriz_sp = df_sp.groupby('SUPERVISOR_MOSTRAR')[['P_COUNT', 'R_COUNT', 'I_COUNT']].sum().reset_index()
                
                for supervisor in sorted(matriz_sp['SUPERVISOR_MOSTRAR'].unique()):
                    dados_super = matriz_sp[matriz_sp['SUPERVISOR_MOSTRAR'] == supervisor].iloc[0]
                    pendentes = int(dados_super['P_COUNT'])
                    em_rota = int(dados_super['R_COUNT'])
                    iniciados = int(dados_super['I_COUNT'])
                    total_real = pendentes + em_rota + iniciados
                    
                    with st.container(border=True):
                        st.markdown('<div style="font-size:20px; font-weight:bold; margin-bottom:10px;">📋 ' + str(supervisor) + ' <span style="float:right; font-size:14px; background-color:#e1f5fe; padding:2px 8px; border-radius:4px; color:#0288d1;">Total Contratos: ' + str(total_real) + '</span></div>', unsafe_allow_html=True)
                        
                        m1, m2, m3 = st.columns(3)
                        with m1: st.markdown('<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 PENDENTES</div><div class="custom-pendente-value">' + str(pendentes) + '</div></div>', unsafe_allow_html=True)
                        with m2: st.metric(label="🟣 EM ROTA", value=em_rota)
                        with m3: st.metric(label="🟢 INICIADO", value=iniciados)
            else:
                st.info("Nenhum contrato ativo para SP nesta janela.")

    # MODO TV
    st.components.v1.html("""
        <script>
        setTimeout(function(){ window.parent.location.hash = "#3-tec1-pendentes"; }, 30000);
        </script>
    """, height=0)
else:
    st.warning("👈 Por favor, faça o upload dos arquivos de rota na página inicial (streamlit_app.py) primeiro.")

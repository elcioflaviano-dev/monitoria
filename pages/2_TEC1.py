import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configura a página para ocupar toda a largura da tela
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Abre e injeta o arquivo style.css externo
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

# Título TEC1 Centralizado
st.markdown(
    '<h1 style="font-size: 42px; font-weight: 900; color: #006677; text-align: center; margin-top: 25px; margin-bottom: 5px;">TEC1</h1>', 
    unsafe_allow_html=True
)

# 🔄 HERANÇA INTELIGENTE: Puxa o DataFrame da memória global
df_master = st.session_state.get('df_rota_ativa', None)

if df_master is not None and not df_master.empty:
    df = df_master.copy()
    
    # === PASSO 1: LIMPEZA DE LINHAS VAZIAS DA ROTA ===
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
    
    # FILTRAGEM: Remove status suspensos
    df_limpo = df[df['Status_Atividade_Upper'] != 'SUSPENSO'].copy()
    
    # Remove as marcações operacionais de almoço (Refeicao)
    if 'Tipo de Atividade' in df_limpo.columns:
        df_limpo['Tipo_Activity_Str'] = df_limpo['Tipo de Atividade'].fillna('').astype(str)
        df_limpo = df_limpo[~df_limpo['Tipo_Activity_Str'].str.contains('Refeicao', case=False, na=False)]
        
    # === PASSO 2: FILTRAGEM PRÉVIA DE STATUS ATIVOS EM CAMPO ===
    df_limpo['P_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('PENDENTE|EM ABERTO|ABERTO', na=False).astype(int)
    df_limpo['R_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('ROTA|DESLOC|DESLOCAMENTO', na=False).astype(int)
    df_limpo['I_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('INICIADO|PRODUTIVO|EXECUCAO|INIC', na=False).astype(int)
    
    # Cria uma base apenas com os contratos válidos que estão acontecendo no dia
    df_validos = df_limpo[(df_limpo['P_COUNT'] > 0) | (df_limpo['R_COUNT'] > 0) | (df_limpo['I_COUNT'] > 0)].copy()

    # Mapeia a coluna de Janela
    col_janela = 'Janela de Serviço' if 'Janela de Serviço' in df_validos.columns else None
    if not col_janela:
        for c in df_validos.columns:
            if 'JANELA' in str(c).upper() or 'INTERVALO' in str(c).upper(): col_janela = c; break

    if col_janela is not None and not df_validos.empty:
        df_validos['Intervalo_Tratado'] = df_validos[col_janela].fillna('').astype(str).str.strip()
        
        # 🌟 PASSO 3: MOTOR DE HORÁRIO AUTOMÁTICO (FUSO BRASÍLIA) 🌟
        hora_brasilia = (datetime.utcnow() - timedelta(hours=3)).hour
        
        if hora_brasilia < 11:
            janelas_automaticas = ['08 - 10']
            texto_status_janela = f"⏰ [Hora Local: {hora_brasilia:02d}h] - Janela da Manhã (08 - 10)"
        elif 11 <= hora_brasilia < 15:
            janelas_automaticas = ['08 - 10', '11 - 14', '12:00 - 15:00']
            texto_status_janela = f"⏰ [Hora Local: {hora_brasilia:02d}h] - Janela Ativa (11 - 14 / 12 - 15) + Acumulados"
        else:
            janelas_automaticas = ['08 - 10', '11 - 14', '12:00 - 15:00', '15 - 18']
            texto_status_janela = f"⏰ [Hora Local: {hora_brasilia:02d}h] - Janela da Tarde (15 - 18) + Tudo Pendente do Dia"

        # 🌟 CRÍTICO: Monta as opções olhando APENAS para os contratos válidos e limpa horários quebrados
        df_janelas_limpas = df_validos[
            (df_validos['Intervalo_Tratado'] != '') & 
            (~df_validos['Intervalo_Tratado'].str.upper().str.contains('SEM JANELA')) &
            (df_validos['Intervalo_Tratado'].str.len() <= 7) # Força apenas formatos curtos tipo "11 - 14"
        ].copy()
        
        opcoes_janela_todas = sorted(df_janelas_limpas['Intervalo_Tratado'].dropna().unique())
        opcoes_janela_todas = [j for j in opcoes_janela_todas if j.upper() not in ['NAN', 'NONE', 'N/A']]
        
        # Insere a opção "AUTOMÁTICO" no topo da lista limpa
        lista_selectbox = ["AUTOMÁTICO 🔄"] + opcoes_janela_todas
        janela_sel = st.sidebar.selectbox("Filtro de Janela:", lista_selectbox)
        
        if janela_sel == "AUTOMÁTICO 🔄":
            df_tela = df_validos[df_validos['Intervalo_Tratado'].isin(janelas_automaticas)].copy()
            st.markdown(f'<div style="text-align: center; color: #cc6600; font-size: 14px; font-weight: bold; margin-bottom: 15px;">{texto_status_janela}</div>', unsafe_allow_html=True)
        else:
            df_tela = df_validos[df_validos['Intervalo_Tratado'] == janela_sel].copy()
            st.markdown(f'<div style="text-align: center; color: #555; font-size: 14px; font-weight: bold; margin-bottom: 15px;">🎯 Filtro Manual Forçado: Janela {janela_sel}</div>', unsafe_allow_html=True)
    else:
        df_tela = df_validos.copy()

    if df_tela.empty:
        st.warning("⚠️ Não existem dados correspondentes para os filtros aplicados nesta janela.")
    else:
        # Padroniza a coluna do Supervisor vinda do PROCV da Home
        if 'SUPERVISOR' in df_tela.columns:
            df_tela['SUPERVISOR_MOSTRAR'] = df_tela['SUPERVISOR'].fillna('PENDENTE CADASTRO').replace({'#N/A': 'PENDENTE CADASTRO', 'NAN': 'PENDENTE CADASTRO', '': 'PENDENTE CADASTRO'})
        else:
            df_tela['SUPERVISOR_MOSTRAR'] = 'PENDENTE CADASTRO'
            
        df_tela['SUPERVISOR_MOSTRAR'] = df_tela['SUPERVISOR_MOSTRAR'].astype(str).str.upper().str.strip()

        # Divisão Regional utilizando as regras da Home
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
                matriz_abc = df_abc.groupby('SUPERVISOR_MOSTRAR')[['P_COUNT', 'R_COUNT', 'I_COUNT']].sum().reset_index()
                for supervisor in sorted(matriz_abc['SUPERVISOR_MOSTRAR'].unique()):
                    dados_super = matriz_abc[matriz_abc['SUPERVISOR_MOSTRAR'] == supervisor].iloc[0]
                    pendentes, em_rota, iniciados = int(dados_super['P_COUNT']), int(dados_super['R_COUNT']), int(dados_super['I_COUNT'])
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
                    pendentes, em_rota, iniciados = int(dados_super['P_COUNT']), int(dados_super['R_COUNT']), int(dados_super['I_COUNT'])
                    total_real = pendentes + em_rota + iniciados
                    
                    with st.container(border=True):
                        st.markdown('<div style="font-size:20px; font-weight:bold; margin-bottom:10px;">📋 ' + str(supervisor) + ' <span style="float:right; font-size:14px; background-color:#e1f5fe; padding:2px 8px; border-radius:4px; color:#0288d1;">Total Contratos: ' + str(total_real) + '</span></div>', unsafe_allow_html=True)
                        m1, m2, m3 = st.columns(3)
                        with m1: st.markdown('<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 PENDENTES</div><div class="custom-pendente-value">' + str(pendentes) + '</div></div>', unsafe_allow_html=True)
                        with m2: st.metric(label="🟣 EM ROTA", value=em_rota)
                        with m3: st.metric(label="🟢 INICIADO", value=iniciados)
            else:
                st.info("Nenhum contrato ativo para SP nesta janela.")

    # MODO TV AUTOMÁTICO
    st.components.v1.html("""
        <script>
        setTimeout(function(){ window.parent.location.hash = "#3-tec1-pendentes"; }, 30000);
        </script>
    """, height=0)
else:
    st.warning("👈 Por favor, faça o upload dos arquivos de rota na página inicial (streamlit_app.py) primeiro.")

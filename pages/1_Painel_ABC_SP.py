import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. Configuração da página ampla padrão
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 2. Carregar Estilos Globais (CSS)
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

st.markdown('<h1 style="font-size: 38px; font-weight: 900; color: #005088; text-align: center; margin-top: 20px; margin-bottom: 5px;">📊 VISÃO REGIONAL - ABC & SÃO PAULO</h1>', unsafe_allow_html=True)

# 🔄 3. HERANÇA INTELIGENTE: Puxa o DataFrame unificado da memória global (Home)
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
    
    # Remove marcações de almoço
    if 'Tipo de Atividade' in df_limpo.columns:
        df_limpo['Tipo_Activity_Str'] = df_limpo['Tipo de Atividade'].fillna('').astype(str)
        df_limpo = df_limpo[~df_limpo['Tipo_Activity_Str'].str.contains('Refeicao', case=False, na=False)]

    # === PASSO 2: FILTRAGEM PRÉVIA DE STATUS ATIVOS ===
    df_limpo['P_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('PENDENTE|EM ABERTO|ABERTO', na=False).astype(int)
    df_limpo['R_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('ROTA|DESLOC|DESLOCAMENTO', na=False).astype(int)
    df_limpo['I_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('INICIADO|PRODUTIVO|EXECUCAO|INIC', na=False).astype(int)
    
    df_validos = df_limpo[(df_limpo['P_COUNT'] > 0) | (df_limpo['R_COUNT'] > 0) | (df_limpo['I_COUNT'] > 0)].copy()

    # Mapeamento e Tratamento de Janelas (Com motor automático e fuso corrigido)
    col_janela = 'Janela de Serviço' if 'Janela de Serviço' in df_validos.columns else None
    if not col_janela:
        for c in df_validos.columns:
            if 'JANELA' in str(c).upper() or 'INTERVALO' in str(c).upper(): col_janela = c; break

    if col_janela is not None and not df_validos.empty:
        df_validos['Intervalo_Tratado'] = df_validos[col_janela].fillna('').astype(str).str.strip()
        
        # Fuso Horário de Brasília Blindado
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

        # Limpa o menu lateral deixando só o que é real
        df_janelas_limpas = df_validos[(df_validos['Intervalo_Tratado'] != '') & (~df_validos['Intervalo_Tratado'].str.upper().str.contains('SEM JANELA')) & (df_validos['Intervalo_Tratado'].str.len() <= 15)].copy()
        opcoes_janela_todas = sorted(df_janelas_limpas['Intervalo_Tratado'].dropna().unique())
        
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
        st.warning("⚠️ Não existem dados correspondentes para esta janela.")
    else:
        # 🌟 VALIDAÇÃO DA COLUNA DO SUPERVISOR (Evita o KeyError)
        if 'SUPERVISOR' in df_tela.columns:
            df_tela['SUPERVISOR_MOSTRAR'] = df_tela['SUPERVISOR'].fillna('PENDENTE CADASTRO').replace({'#N/A': 'PENDENTE CADASTRO', 'NAN': 'PENDENTE CADASTRO', '': 'PENDENTE CADASTRO'})
        else:
            df_tela['SUPERVISOR_MOSTRAR'] = 'PENDENTE CADASTRO'
            
        df_tela['SUPERVISOR_MOSTRAR'] = df_tela['SUPERVISOR_MOSTRAR'].astype(str).str.upper().str.strip()

        # Divisão Regional utilizando as regras consolidadas da Home
        cond_sp = (
            df_tela['REGIAO_BASE'].fillna('').astype(str).str.upper().str.strip().str.contains('SÃO PAULO|SP', na=False) |
            df_tela['SUPERVISOR_MOSTRAR'].str.contains('FRANCISCO|ALAN', na=False)
        )
        
        df_sp = df_tela[cond_sp].copy()
        df_abc = df_tela[~cond_sp].copy()

        # Renderização dos KPIs Consolidados das duas Regiões
        c_abc, c_sp = st.columns(2)
        
        with c_abc:
            st.markdown('<div style="background-color:#005088; padding:8px; color:white; font-weight:bold; font-size:20px; border-radius:4px; text-align:center; margin-bottom:10px;">📍 BLOCO REGIONAL - ABC</div>', unsafe_allow_html=True)
            if not df_abc.empty:
                t_p = int(df_abc['P_COUNT'].sum())
                t_r = int(df_abc['R_COUNT'].sum())
                t_i = int(df_abc['I_COUNT'].sum())
                tot = t_p + t_r + t_i
                
                with st.container(border=True):
                    st.markdown(f'<div style="font-size:16px; font-weight:bold; color:#333; margin-bottom:5px;">Total do Bloco: {tot} Contratos</div>', unsafe_allow_html=True)
                    m1, m2, m3 = st.columns(3)
                    with m1: st.markdown(f'<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 PENDENTES</div><div class="custom-pendente-value">{t_p}</div></div>', unsafe_allow_html=True)
                    with m2: st.metric(label="🟣 EM ROTA", value=t_r)
                    with m3: st.metric(label="🟢 INICIADO", value=t_i)
            else:
                st.info("Nenhum contrato ativo para o ABC.")

        with c_sp:
            st.markdown('<div style="background-color:#006677; padding:8px; color:white; font-weight:bold; font-size:20px; border-radius:4px; text-align:center; margin-bottom:10px;">📍 BLOCO REGIONAL - SÃO PAULO</div>', unsafe_allow_html=True)
            if not df_sp.empty:
                t_p = int(df_sp['P_COUNT'].sum())
                t_r = int(df_sp['R_COUNT'].sum())
                t_i = int(df_sp['I_COUNT'].sum())
                tot = t_p + t_r + t_i
                
                with st.container(border=True):
                    st.markdown(f'<div style="font-size:16px; font-weight:bold; color:#333; margin-bottom:5px;">Total do Bloco: {tot} Contratos</div>', unsafe_allow_html=True)
                    m1, m2, m3 = st.columns(3)
                    with m1: st.markdown(f'<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 PENDENTES</div><div class="custom-pendente-value">{t_p}</div></div>', unsafe_allow_html=True)
                    with m2: st.metric(label="🟣 EM ROTA", value=t_r)
                    with m3: st.metric(label="🟢 INICIADO", value=t_i)
            else:
                st.info("Nenhum contrato ativo para São Paulo.")

    # MODO TV AUTOMÁTICO (Roda para a próxima página da fila)
    st.components.v1.html("""
        <script>
        setTimeout(function(){ window.parent.location.hash = "#2-tec1"; }, 30000);
        </script>
    """, height=0)
else:
    st.warning("👈 Por favor, faça o upload dos arquivos de rota na página inicial (streamlit_app.py) primeiro.")

import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta

# 1. Configuração da página
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1kB1YmUuhzHpfN1dLv8PaQn0ipXcHcd6kGKnI3nguT14/export?format=csv&gid=0"

# 🔄 HERANÇA INTELIGENTE VIA DISCO RÍGIDO
if ('df_rota_ativa' not in st.session_state or st.session_state['df_rota_ativa'] is None) and os.path.exists(ARQUIVO_ROTA_DISCO):
    try:
        st.session_state['df_rota_ativa'] = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    except:
        pass

# 🚀 MAPEAMENTO AO VIVO DO GOOGLE SHEETS (SEM QUEBRAR O VISUAL)
mapa_base = {}
mapa_sup = {}
try:
    df_equipe = pd.read_csv(URL_PLANILHA)
    if not df_equipe.empty and len(df_equipe.columns) >= 3:
        df_equipe.columns = df_equipe.columns.str.strip().str.upper()
        # Cria dicionários para atualizar a base e supervisor do técnico na hora
        mapa_base = dict(zip(df_equipe['NOME'].astype(str).str.strip().str.upper(), df_equipe['BASE'].astype(str).str.strip().str.upper()))
        mapa_sup = dict(zip(df_equipe['NOME'].astype(str).str.strip().str.upper(), df_equipe['SUPERVISOR'].astype(str).str.strip().str.upper()))
except:
    pass

# 🚀 SISTEMA DE REFRESH AUTOMÁTICO PARA A TV (60 Segundos)
if 'df_rota_ativa' in st.session_state and st.session_state['df_rota_ativa'] is not None:
    if "last_refresh_dash" not in st.session_state:
        st.session_state["last_refresh_dash"] = time.time()
    
    if time.time() - st.session_state["last_refresh_dash"] > 60:
        st.session_state["last_refresh_dash"] = time.time()
        st.rerun()

# 2. Carregar Estilos Globais
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

# Customização CSS Original de Alta Performance para os Cards e Grid de 6 Colunas
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem !important; }
    div[data-testid="stHorizontalBlock"] { gap: 10px !important; }
    
    /* Grid dos Cards de KPI do 1º Contrato (Topo) */
    .kpi-container-atend {
        display: flex;
        justify-content: center;
        gap: 25px;
        margin-bottom: 15px;
    }
    .kpi-card-atend {
        background-color: #ffffff;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        padding: 10px 25px;
        text-align: center;
        min-width: 280px;
        border-top: 5px solid #006677;
    }
    .kpi-card-atend.abc { border-top-color: #008080; }
    .kpi-card-atend.sp { border-top-color: #b30000; }
    .kpi-title-atend { font-size: 13px; color: #666; font-weight: bold; text-transform: uppercase; margin-bottom: 4px; }
    .kpi-value-atend { font-size: 26px; color: #111; font-weight: 900; }
    
    /* Faixa de Título das Bases Operacionais */
    .section-base-title {
        background-color: #005088;
        color: white;
        padding: 8px 15px;
        border-radius: 4px;
        font-size: 16px;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 12px;
        text-transform: uppercase;
    }
    
    /* Ajuste de espaçamento para os 6 cards laterais */
    div[data-testid="stKPIBlock"] {
        padding: 6px 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="font-size: 38px; font-weight: 900; color: #008080; text-align: center; margin-top: 25px; margin-bottom: 5px;">📊 PAINEL ABC SP - DASHBOARDS</h1>', unsafe_allow_html=True)

df_dash = st.session_state.get('df_rota_ativa', None)

# --- FUNÇÕES AUXILIARES PARA O CÁLCULO DE MÉDIAS DO 1º CONTRATO ---
def tratar_horario(val):
    if pd.isna(val) or str(val).strip() in ['', 'N/A', 'NAN', 'NaN', '00:00']:
        return None
    try:
        texto = str(val).strip().split()[-1]
        return datetime.strptime(texto, '%H:%M:%S').time()
    except:
        try:
            texto = str(val).strip().split()[-1]
            return datetime.strptime(texto, '%H:%M').time()
        except:
            return None

def calcular_media_horarios(lista_horas):
    if not lista_horas:
        return "--:--"
    total_segundos = 0
    qtd = 0
    for h in lista_horas:
        if h is not None:
            total_segundos += h.hour * 3600 + h.minute * 60 + h.second
            qtd += 1
    if qtd == 0:
        return "--:--"
    media_segundos = total_segundos / qtd
    media_time = str(timedelta(seconds=int(media_segundos)))
    return ":".join(media_time.split(":")[:2])

if df_dash is not None and not df_dash.empty:
    
    col_recurso = 'Recurso' if 'Recurso' in df_dash.columns else df_dash.columns[0]
    col_status = 'STATUS_ATIVIDADE' if 'STATUS_ATIVIDADE' in df_dash.columns else 'Status da Atividade'
    status_upper_bruto = df_dash[col_status].fillna('').astype(str).str.upper().str.strip()
    contrato_limpo_bruto = df_dash['Contrato'].fillna('').astype(str).str.strip()
    
    # ATUALIZA A BASE AO VIVO USANDO O GOOGLE SHEETS
    if mapa_base:
        df_dash['REGIAO_BASE_LIVE'] = df_dash[col_recurso].fillna('').astype(str).str.upper().str.strip().map(mapa_base)
        df_dash['REGIAO_BASE_LIVE'] = df_dash['REGIAO_BASE_LIVE'].fillna(df_dash.get('REGIAO_BASE', 'GERAL'))
    else:
        df_dash['REGIAO_BASE_LIVE'] = df_dash.get('REGIAO_BASE', 'GERAL')

    # =========================================================================
    # ⏱️ MOTOR: 1º ATENDIMENTO OPERACIONAL (CARDS FIXOS DO TOPO)
    # =========================================================================
    media_abc, media_sp = "--:--", "--:--"
    
    col_inicio_estrito = 'Início'
    for c in df_dash.columns:
        c_clean = str(c).upper().strip().split('.')[0]
        if c_clean in ['INÍCIO', 'INICIO'] and '-' not in str(c) and 'DO' not in str(c).upper():
            col_inicio_estrito = c
            break

    df_atend_isolado = df_dash[
        (status_upper_bruto.str.contains('CONCL|INIC|SUSP', na=False)) &
        (contrato_limpo_bruto != '') &
        (~contrato_limpo_bruto.isin(['nan', '0', '#N/A']))
    ].copy()
    
    df_atend_isolado['Hora_Inicio_Time'] = df_atend_isolado[col_inicio_estrito].apply(tratar_horario)
    df_atend_isolado = df_atend_isolado[df_atend_isolado['Hora_Inicio_Time'].notna()]
    
    if not df_atend_isolado.empty:
        df_primeiros_horarios = df_atend_isolado.sort_values('Hora_Inicio_Time').groupby(col_recurso).first().reset_index()
        
        # Filtra ABC e SP baseado no nosso mapa ao vivo
        horas_abc = df_primeiros_horarios[df_primeiros_horarios['REGIAO_BASE_LIVE'].str.contains("ABC", na=False)]['Hora_Inicio_Time'].tolist()
        horas_sp = df_primeiros_horarios[df_primeiros_horarios['REGIAO_BASE_LIVE'].str.contains("SP", na=False)]['Hora_Inicio_Time'].tolist()
        
        media_abc = calcular_media_horarios(horas_abc)
        media_sp = calcular_media_horarios(horas_sp)

    st.session_state['media_global_abc'] = media_abc
    st.session_state['media_global_sp'] = media_sp

    st.markdown(f'''
        <div class="kpi-container-atend">
            <div class="kpi-card-atend abc">
                <div class="kpi-title-atend">⏱️ Média 1º Contrato - ABC</div>
                <div class="kpi-value-atend">{media_abc}</div>
            </div>
            <div class="kpi-card-atend sp">
                <div class="kpi-title-atend">⏱️ Média 1º Contrato - SÃO PAULO</div>
                <div class="kpi-value-atend">{media_sp}</div>
            </div>
        </div>
    ''', unsafe_allow_html=True)

    st.markdown("<hr style='margin-top:0px; margin-bottom:15px; border-color:#eee;'>", unsafe_allow_html=True)

    # === HIGIENIZAÇÃO COMPLETA PARA OS CARDS MACRO POR BASE ===
    df_working = df_dash.copy()
    df_working['Contrato_Limpo'] = contrato_limpo_bruto
    df_working['Status_Atividade_Upper'] = status_upper_bruto
    
    df_working['Mestre_Tipo_Atividade_Upper'] = ""
    for c in df_working.columns:
        if 'TIPO' in str(c).upper() and 'ATIV' in str(c).upper():
            df_working['Mestre_Tipo_Atividade_Upper'] += " " + df_working[c].fillna('').astype(str).str.upper().str.strip()
            
    cond_saudavel = (
        (df_working['Contrato_Limpo'] != '') & 
        (df_working['Contrato_Limpo'] != 'nan') & 
        (~df_working['Contrato_Limpo'].str.contains('#N/A', na=False)) &
        (~df_working['Status_Atividade_Upper'].str.contains('SUSPENSO', na=False)) &
        (~df_working['Mestre_Tipo_Atividade_Upper'].str.contains('REFEI', na=False))
    )
    df_working = df_working[cond_saudavel].copy()

    col_tarefas = 'QTD_OS_COL' if 'QTD_OS_COL' in df_working.columns else 'Total de tarefas'
    df_working['Total_OS_Num'] = pd.to_numeric(df_working[col_tarefas], errors='coerce').fillna(0).astype(int) if col_tarefas in df_working.columns else 1

    # Filtro Lateral de Supervisor
    if mapa_sup:
        df_working['SUPERVISOR_LIVE'] = df_working[col_recurso].fillna('').astype(str).str.upper().str.strip().map(mapa_sup).fillna('NÃO IDENTIFICADO')
        lista_supervisores = ["TODOS"] + sorted(df_working['SUPERVISOR_LIVE'].unique())
        supervisor_sel = st.sidebar.selectbox("Filtrar por Supervisor:", lista_supervisores)
        if supervisor_sel != "TODOS":
            df_working = df_working[df_working['SUPERVISOR_LIVE'] == supervisor_sel]

    # =========================================================================
    # 📊 LAÇO DE COMPILAÇÃO DAS BASES: O SEU GRID DE 6 COLUNAS ORIGINAL
    # =========================================================================
    df_working['REGIAO_BASE_LIVE'] = df_working['REGIAO_BASE_LIVE'].fillna('NÃO DEFINIDA').astype(str).str.upper().str.strip()
    bases_disponiveis = sorted(df_working['REGIAO_BASE_LIVE'].unique())
    
    for base in bases_disponiveis:
        df_base_atual = df_working[df_working['REGIAO_BASE_LIVE'] == base]
        
        # Totais Brutos
        base_qtd_tecnicos = df_base_atual[col_recurso].nunique()
        base_contratos_bruto = df_base_atual['Contrato_Limpo'].nunique()
        base_total_os_bruto = df_base_atual['Total_OS_Num'].sum()
        
        # Filtro de Retornos
        cond_retorno_linha = df_base_atual['Mestre_Tipo_Atividade_Upper'].str.contains('RETORNO', na=False)
        df_retornos_base = df_base_atual[cond_retorno_linha]
        base_total_retornos = df_retornos_base['Contrato_Limpo'].nunique()
        base_total_os_retorno = df_retornos_base['Total_OS_Num'].sum()
        
        # Engenharia Líquida Subtrativa
        base_contratos_liquido = base_contratos_bruto - base_total_retornos
        base_total_os_liquido = base_total_os_bruto - base_total_os_retorno
        
        divisor_tecnicos = base_qtd_tecnicos if base_qtd_tecnicos > 0 else 1
        media_contratos_por_tec = base_contratos_liquido / divisor_tecnicos
        media_os_por_tec = base_total_os_liquido / divisor_tecnicos
        
        st.markdown(f'<div class="section-base-title">📍 BASE OPERACIONAL: {base}</div>', unsafe_allow_html=True)
        
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        
        with c1:
            with st.container(border=True):
                st.markdown(f'<div style="font-size:11px; font-weight:bold; color:#777; text-transform:uppercase;">📋 Geral Contratos</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:24px; font-weight:900; color:#008080;">{base_contratos_bruto}</div>', unsafe_allow_html=True)
        with c2:
            with st.container(border=True):
                st.markdown(f'<div style="font-size:11px; font-weight:bold; color:#777; text-transform:uppercase;">🛠️ Volume Total OS</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:24px; font-weight:900; color:#333;">{base_total_os_bruto}</div>', unsafe_allow_html=True)
        with c3:
            with st.container(border=True):
                st.markdown(f'<div style="font-size:11px; font-weight:bold; color:#777; text-transform:uppercase;">🏃\u200d♂️ Técnicos em Rota</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:24px; font-weight:900; color:#005088;">{base_qtd_tecnicos}</div>', unsafe_allow_html=True)
        with c4:
            with st.container(border=True):
                st.markdown(f'<div style="font-size:11px; font-weight:bold; color:#777; text-transform:uppercase;">⚠️ Total Retornos</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:24px; font-weight:900; color:#b30000;">{base_total_retornos}</div>', unsafe_allow_html=True)
        with c5:
            with st.container(border=True):
                st.markdown(f'<div style="font-size:11px; font-weight:bold; color:#777; text-transform:uppercase;">¼ Média Contratos/Téc</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:24px; font-weight:900; color:#008080;">{media_contratos_por_tec:.2f}</div>', unsafe_allow_html=True)
        with c6:
            with st.container(border=True):
                st.markdown(f'<div style="font-size:11px; font-weight:bold; color:#777; text-transform:uppercase;">⚡ Média OS/Téc</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:24px; font-weight:900; color:#ff9800;">{media_os_por_tec:.2f}</div>', unsafe_allow_html=True)

else:
    st.warning("👈 Por favor, faça o upload dos arquivos de rota na página inicial (streamlit_app.py) primeiro para gerar o painel.")

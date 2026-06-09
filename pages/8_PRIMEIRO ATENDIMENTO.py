import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta

# 1. Configuração da página ampla e título da aba
st.set_page_config(layout="wide", page_title="1º ATENDIMENTO", initial_sidebar_state="collapsed")

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

# 🔄 HERANÇA INTELIGENTE VIA DISCO RÍGIDO (À PROVA DE QUEDAS DE SESSÃO)
if ('df_rota_ativa' not in st.session_state or st.session_state['df_rota_ativa'] is None) and os.path.exists(ARQUIVO_ROTA_DISCO):
    try:
        st.session_state['df_rota_ativa'] = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    except:
        pass

# 🚀 SISTEMA DE REFRESH AUTOMÁTICO PARA A TV (60 Segundos)
if 'df_rota_ativa' in st.session_state and st.session_state['df_rota_ativa'] is not None:
    if "last_refresh_atend" not in st.session_state:
        st.session_state["last_refresh_atend"] = time.time()
    
    if time.time() - st.session_state["last_refresh_atend"] > 60:
        st.session_state["last_refresh_atend"] = time.time()
        st.rerun()

# 2. Carregar Estilos Globais
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

# Customização CSS de Alta Performance Visual e Limpeza da Interface
st.markdown("""
    <style>
    /* CSS PARA ESCONDER OS ATALHOS DO STREAMLIT */
    [data-testid="stHeader"] { visibility: hidden !important; }
    .stDeployButton { display: none !important; }
    footer { visibility: hidden !important; }
    #MainMenu { visibility: hidden !important; }
    
    .block-container { padding-top: 1.5rem !important; }
    div[data-testid="stHorizontalBlock"] { gap: 16px !important; }
    
    .kpi-container {
        display: flex;
        justify-content: center;
        gap: 25px;
        margin-bottom: 25px;
    }
    .kpi-card {
        background-color: #ffffff;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        padding: 15px 30px;
        text-align: center;
        min-width: 260px;
        border-top: 5px solid #006677;
    }
    .kpi-card.abc { border-top-color: #008080; }
    .kpi-card.sp { border-top-color: #b30000; }
    .kpi-title { font-size: 14px; color: #666; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; }
    .kpi-value { font-size: 28px; color: #111; font-weight: 900; }
    
    .stDataFrame div { font-size: 13px !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="font-size: 30px; font-weight: 900; color: #006677; text-align: center; margin-top: 5px; margin-bottom: 20px;">⏱️ 1º ATENDIMENTO OPERACIONAL</h1>', unsafe_allow_html=True)

# 🔄 HERANÇA DA HOME
df_master = st.session_state.get('df_rota_ativa', None)

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

def caçador_de_horario(row, col_principal):
    """Busca o horário na coluna de Início. Se estiver vazia (comum em contratos suspensos), procura em outras colunas."""
    h = tratar_horario(row.get(col_principal))
    if h is not None:
        return h
    
    # Se a coluna Início falhar, procura em colunas de atualização ou fim
    for c in row.index:
        if any(x in str(c).upper() for x in ['HORA', 'ATUALIZA', 'FIM', 'TÉRM']):
            h_alt = tratar_horario(row.get(c))
            if h_alt is not None:
                return h_alt
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

if df_master is not None and not df_master.empty:
    df_temp = df_master.copy()
    df_temp.columns = [str(c).strip() for c in df_temp.columns]
    
    col_recurso = 'Recurso' if 'Recurso' in df_temp.columns else df_temp.columns[0]
    col_status = 'STATUS_ATIVIDADE' if 'STATUS_ATIVIDADE' in df_temp.columns else 'Status da Atividade'
    col_supervisor = 'SUPERVISOR' if 'SUPERVISOR' in df_temp.columns else 'Supervisor'
    
    col_inicio_estrito = 'Início'
    for c in df_temp.columns:
        c_clean = str(c).upper().strip().split('.')[0]
        if c_clean in ['INÍCIO', 'INICIO'] and '-' not in str(c) and 'DO' not in str(c).upper():
            col_inicio_estrito = c
            break

    status_upper_bruto = df_temp[col_status].fillna('').astype(str).str.upper().str.strip()
    contrato_limpo_bruto = df_temp['Contrato'].fillna('').astype(str).str.strip() if 'Contrato' in df_temp.columns else pd.Series(['']*len(df_temp))

    # 🔥 FILTRO MAIS PERMISSIVO: Capta INIC, CONCL, SUSP, EXECUCAO sem obrigar a ter contrato preenchido
    df_atend_isolado = df_temp[
        (status_upper_bruto.str.contains('CONCL|INIC|SUSP|EXEC|PROD', na=False)) &
        (df_temp[col_recurso].fillna('').astype(str).str.strip() != '') &
        (~contrato_limpo_bruto.isin(['nan', '#N/A']))
    ].copy()
    
    # Aplica o novo Caçador de Horário para resgatar os suspensos vazios
    df_atend_isolado['Hora_Inicio_Time'] = df_atend_isolado.apply(lambda row: caçador_de_horario(row, col_inicio_estrito), axis=1)
    df_atend_isolado = df_atend_isolado[df_atend_isolado['Hora_Inicio_Time'].notna()]
    
    if not df_atend_isolado.empty:
        df_primeiros_horarios = df_atend_isolado.sort_values('Hora_Inicio_Time').groupby(col_recurso).first().reset_index()
        df_primeiros_horarios['Horário'] = df_primeiros_horarios['Hora_Inicio_Time'].apply(lambda x: x.strftime('%H:%M') if x else '--:--')
        
        # 🔥 MOTOR DE SUPERVISOR IDÊNTICO AO TEC1 PARA EVITAR FUGAS
        def vincular_supervisor_tecnico(row):
            nome_u = str(row[col_recurso]).upper().strip()
            sup_orig = str(row.get(col_supervisor, '')).upper().strip()
            
            if "FRANCISCO" in sup_orig: return "FRANCISCO"
            if "ALAN" in sup_orig: return "ALAN"
            if "MAICON" in sup_orig: return "MAICON"
            if "NELSON" in sup_orig: return "NELSON"
            if "MARCOS" in sup_orig: return "MARCOS ROBERTO"

            # Fallback por nome
            if any(x in nome_u for x in ["ADRIEL", "AMANDA", "DEBORA", "ELIAS", "AIRON"]): return "ALAN"
            if any(x in nome_u for x in ["ALINE", "ALEX", "EDER", "ENOQUE"]): return "FRANCISCO"
            if "MARCOS" in nome_u: return "MARCOS ROBERTO"
            if "NELSON" in nome_u: return "NELSON"
                
            return "MAICON"

        df_primeiros_horarios['Supervisor_Limpo'] = df_primeiros_horarios.apply(vincular_supervisor_tecnico, axis=1)
        
        df_exibicao = df_primeiros_horarios[['Supervisor_Limpo', col_recurso, 'Horário', 'Hora_Inicio_Time']].rename(columns={col_recurso: 'Técnico', 'Supervisor_Limpo': 'Supervisor'})
        df_exibicao = df_exibicao[(df_exibicao['Técnico'] != 'N/A') & (df_exibicao['Técnico'] != '')]
        
        # Separação das Regionais
        cond_sp = df_exibicao['Supervisor'].str.contains("FRANCISCO|ALAN", na=False)
        df_sp = df_exibicao[cond_sp].copy()
        df_abc = df_exibicao[~cond_sp].copy()

        # =========================================================================
        # 🌟 CÁLCULO DE MÉDIAS SINCRONIZADO VIA MEMÓRIA OU PROCESSAMENTO DIRETO
        # =========================================================================
        if 'media_global_abc' in st.session_state and 'media_global_sp' in st.session_state:
            media_abc = st.session_state['media_global_abc']
            media_sp = st.session_state['media_global_sp']
        else:
            horas_abc = df_primeiros_horarios[~df_primeiros_horarios['Supervisor_Limpo'].str.contains("FRANCISCO|ALAN", na=False)]['Hora_Inicio_Time'].tolist()
            horas_sp = df_primeiros_horarios[df_primeiros_horarios['Supervisor_Limpo'].str.contains("FRANCISCO|ALAN", na=False)]['Hora_Inicio_Time'].tolist()
            media_abc = calcular_media_horarios(horas_abc)
            media_sp = calcular_media_horarios(horas_sp)

        st.markdown(f'''
            <div class="kpi-container">
                <div class="kpi-card abc">
                    <div class="kpi-title">⏱️ Média 1º Contrato - ABC</div>
                    <div class="kpi-value">{media_abc}</div>
                </div>
                <div class="kpi-card sp">
                    <div class="kpi-title">⏱️ Média 1º Contrato - SÃO PAULO</div>
                    <div class="kpi-value">{media_sp}</div>
                </div>
            </div>
        ''', unsafe_allow_html=True)

        # ==========================================
        # 🔴 REGIONAL ABC
        # ==========================================
        st.markdown('<div style="background-color:#008080; padding:6px 15px; border-radius:4px; margin-bottom:15px;"><h2 style="color:white; margin:0px; font-size:18px; font-weight: bold;">📍 DETALHAMENTO DA EQUIPE - REGIONAL ABC</h2></div>', unsafe_allow_html=True)
        
        if not df_abc.empty:
            supervisores_abc = sorted(df_abc['Supervisor'].unique().tolist())
            cols_abc = st.columns(len(supervisores_abc) if len(supervisores_abc) > 0 else 1)
            
            for i, sup in enumerate(supervisores_abc):
                with cols_abc[i]:
                    df_sup_abc = df_abc[df_abc['Supervisor'] == sup][['Técnico', 'Horário', 'Hora_Inicio_Time']].sort_values('Horário')
                    media_supervisor = calcular_media_horarios(df_sup_abc['Hora_Inicio_Time'].tolist())
                    
                    st.markdown(f'''
                        <div style="background-color:#f1f7f6; border-left:4px solid #008080; padding:8px 12px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-weight:bold; color:#004d40; font-size:13px; text-transform: uppercase;">👤 {sup}</span>
                            <span style="background-color:#008080; color:white; padding:3px 8px; border-radius:3px; font-weight:900; font-size:14px;">⏱️ {media_supervisor}</span>
                        </div>
                    ''', unsafe_allow_html=True)
                    
                    st.dataframe(df_sup_abc[['Técnico', 'Horário']], use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum atendimento produtivo registrado na região ABC.")

        st.markdown("<br><hr><br>", unsafe_allow_html=True)

        # ==========================================
        # 🔵 REGIONAL SÃO PAULO (SP)
        # ==========================================
        st.markdown('<div style="background-color:#b30000; padding:6px 15px; border-radius:4px; margin-bottom:15px;"><h2 style="color:white; margin:0px; font-size:18px; font-weight: bold;">📍 DETALHAMENTO DA EQUIPE - REGIONAL SÃO PAULO (SP)</h2></div>', unsafe_allow_html=True)
        
        if not df_sp.empty:
            supervisores_sp = sorted(df_sp['Supervisor'].unique().tolist())
            cols_sp = st.columns(len(supervisores_sp) if len(supervisores_sp) > 0 else 1)
            
            for i, sup in enumerate(supervisores_sp):
                with cols_sp[i]:
                    df_sup_sp = df_sp[df_sp['Supervisor'] == sup][['Técnico', 'Horário', 'Hora_Inicio_Time']].sort_values('Horário')
                    media_supervisor = calcular_media_horarios(df_sup_sp['Hora_Inicio_Time'].tolist())
                    
                    st.markdown(f'''
                        <div style="background-color:#fff2f2; border-left:4px solid #b30000; padding:8px 12px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-weight:bold; color:#660000; font-size:13px; text-transform: uppercase;">👤 {sup}</span>
                            <span style="background-color:#b30000; color:white; padding:3px 8px; border-radius:3px; font-weight:900; font-size:14px;">⏱️ {media_supervisor}</span>
                        </div>
                    ''', unsafe_allow_html=True)
                    
                    st.dataframe(df_sup_sp[['Técnico', 'Horário']], use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum atendimento produtivo registrado na região de SP.")
    else:
        st.warning("⚠️ Dados de rotas estão vazios ou inválidos.")
else:
    st.warning("👈 Por favor, faça o upload dos arquivos de rota na página inicial primeiro.")

import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta

st.set_page_config(layout="wide", page_title="1º ATENDIMENTO", initial_sidebar_state="collapsed")

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if ('df_rota_ativa' not in st.session_state or st.session_state['df_rota_ativa'] is None) and os.path.exists(ARQUIVO_ROTA_DISCO):
    try:
        st.session_state['df_rota_ativa'] = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    except:
        pass

if 'df_rota_ativa' in st.session_state and st.session_state['df_rota_ativa'] is not None:
    if "last_refresh_atend" not in st.session_state:
        st.session_state["last_refresh_atend"] = time.time()
    
    st.text_input("refresh_trigger_atend", value=str(st.session_state["last_refresh_atend"]), label_visibility="collapsed")
    
    if time.time() - st.session_state["last_refresh_atend"] > 60:
        st.session_state["last_refresh_atend"] = time.time()
        st.rerun()

try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

st.markdown("""
    <style>
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
        border-top: 5px solid #008080;
    }
    .kpi-title { font-size: 14px; color: #666; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; }
    .kpi-value { font-size: 28px; color: #111; font-weight: 900; }
    
    .stDataFrame div { font-size: 13px !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="font-size: 30px; font-weight: 900; color: #006677; text-align: center; margin-top: 5px; margin-bottom: 20px;">⏱️ 1º ATENDIMENTO OPERACIONAL</h1>', unsafe_allow_html=True)

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
    contrato_limpo_bruto = df_temp['Contrato'].fillna('').astype(str).str.strip()

    df_atend_isolado = df_temp[
        (status_upper_bruto.str.contains('CONCL|INIC|SUSP', na=False)) &
        (contrato_limpo_bruto != '') &
        (~contrato_limpo_bruto.isin(['nan', '0', '#N/A']))
    ].copy()
    
    df_atend_isolado['Hora_Inicio_Time'] = df_atend_isolado[col_inicio_estrito].apply(tratar_horario)
    df_atend_isolado = df_atend_isolado[df_atend_isolado['Hora_Inicio_Time'].notna()]
    
    if not df_atend_isolado.empty:
        df_primeiros_horarios = df_atend_isolado.sort_values('Hora_Inicio_Time').groupby(col_recurso).first().reset_index()
        df_primeiros_horarios['Horário'] = df_primeiros_horarios['Hora_Inicio_Time'].apply(lambda x: x.strftime('%H:%M') if x else '--:--')
        
        df_primeiros_horarios['Supervisor_Limpo'] = df_primeiros_horarios[col_supervisor].fillna('MAICON').astype(str).str.upper().str.strip()
        df_primeiros_horarios['Supervisor_Limpo'] = df_primeiros_horarios['Supervisor_Limpo'].replace({'#N/A': 'MAICON', 'NAN': 'MAICON', '': 'MAICON'})
        
        df_exibicao = df_primeiros_horarios[['Supervisor_Limpo', col_recurso, 'Horário', 'Hora_Inicio_Time']].rename(columns={col_recurso: 'Técnico', 'Supervisor_Limpo': 'Supervisor'})
        df_exibicao = df_exibicao[(df_exibicao['Técnico'] != 'N/A') & (df_exibicao['Técnico'] != '')]
        
        # Filtra a base para não exibir supervisores de SP (ALAN, FRANCISCO, JOAO, MIRON)
        cond_sp = df_exibicao['Supervisor'].str.contains("FRANCISCO|ALAN|JOAO|MIRON", na=False)
        df_abc = df_exibicao[~cond_sp].copy()

        if 'media_global_abc' in st.session_state:
            media_abc = st.session_state['media_global_abc']
        else:
            horas_abc = df_primeiros_horarios[~df_primeiros_horarios['Supervisor_Limpo'].str.contains("FRANCISCO|ALAN|JOAO|MIRON", na=False)]['Hora_Inicio_Time'].tolist()
            media_abc = calcular_media_horarios(horas_abc)

        st.markdown(f'''
            <div class="kpi-container">
                <div class="kpi-card abc">
                    <div class="kpi-title">⏱️ Média 1º Contrato - ABC</div>
                    <div class="kpi-value">{media_abc}</div>
                </div>
            </div>
        ''', unsafe_allow_html=True)

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

    else:
        st.warning("⚠️ Dados de rotas estão vazios ou inválidos.")
else:
    st.warning("👈 Por favor, faça o upload dos arquivos de rota na página inicial primeiro.")

import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta

st.set_page_config(layout="wide", page_title="1º ATENDIMENTO", initial_sidebar_state="collapsed")

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1kB1YmUuhzHpfN1dLv8PaQn0ipXcHcd6kGKnI3nguT14/export?format=csv&gid=0"

# MAPA INFALÍVEL: RELACIONA CADA SUPERVISOR À SUA RESPECTIVA BASE USANDO O GOOGLE SHEETS
mapa_sup_base = {}
try:
    df_equipe = pd.read_csv(URL_PLANILHA)
    if not df_equipe.empty and len(df_equipe.columns) >= 3:
        df_equipe.columns = df_equipe.columns.str.strip().str.upper()
        mapa_sup_base = dict(zip(df_equipe['SUPERVISOR'].astype(str).str.strip().str.upper(), df_equipe['BASE'].astype(str).str.strip().str.upper()))
except:
    pass

if ('df_rota_ativa' not in st.session_state or st.session_state['df_rota_ativa'] is None) and os.path.exists(ARQUIVO_ROTA_DISCO):
    try: st.session_state['df_rota_ativa'] = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    except: pass

if 'df_rota_ativa' in st.session_state and st.session_state['df_rota_ativa'] is not None:
    if "last_refresh_atend" not in st.session_state: st.session_state["last_refresh_atend"] = time.time()
    st.text_input("refresh_trigger_atend", value=str(st.session_state["last_refresh_atend"]), label_visibility="collapsed")
    if time.time() - st.session_state["last_refresh_atend"] > 60:
        st.session_state["last_refresh_atend"] = time.time()
        st.rerun()

try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except: pass

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem !important; }
    div[data-testid="stHorizontalBlock"] { gap: 16px !important; }
    .kpi-container { display: flex; justify-content: center; gap: 25px; margin-bottom: 25px; }
    .kpi-card { background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); padding: 15px 30px; text-align: center; min-width: 260px; border-top: 5px solid #006677; }
    .kpi-card.abc { border-top-color: #008080; }
    .kpi-card.sp { border-top-color: #b30000; }
    .kpi-title { font-size: 14px; color: #666; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; }
    .kpi-value { font-size: 28px; color: #111; font-weight: 900; }
    .stDataFrame div { font-size: 13px !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="font-size: 30px; font-weight: 900; color: #006677; text-align: center; margin-top: 5px; margin-bottom: 20px;">⏱️ 1º ATENDIMENTO OPERACIONAL</h1>', unsafe_allow_html=True)

df_master = st.session_state.get('df_rota_ativa', None)

def tratar_horario(val):
    if pd.isna(val) or str(val).strip() in ['', 'N/A', 'NAN', 'NaN', '00:00']: return None
    try: return datetime.strptime(str(val).strip().split()[-1], '%H:%M:%S').time()
    except:
        try: return datetime.strptime(str(val).strip().split()[-1], '%H:%M').time()
        except: return None

def calcular_media_horarios(lista_horas):
    if not lista_horas: return "--:--"
    total_segundos = sum(h.hour * 3600 + h.minute * 60 + h.second for h in lista_horas if h is not None)
    qtd = sum(1 for h in lista_horas if h is not None)
    if qtd == 0: return "--:--"
    return ":".join(str(timedelta(seconds=int(total_segundos / qtd))).split(":")[:2])

if df_master is not None and not df_master.empty:
    df_temp = df_master.copy()
    df_temp.columns = [str(c).strip() for c in df_temp.columns]
    
    col_recurso = 'Recurso' if 'Recurso' in df_temp.columns else df_temp.columns[0]
    col_status = 'STATUS_ATIVIDADE' if 'STATUS_ATIVIDADE' in df_temp.columns else 'Status da Atividade'
    col_supervisor = 'SUPERVISOR' if 'SUPERVISOR' in df_temp.columns else 'Supervisor'
    
    col_inicio_estrito = 'Início'
    for c in df_temp.columns:
        if str(c).upper().strip().split('.')[0] in ['INÍCIO', 'INICIO'] and '-' not in str(c) and 'DO' not in str(c).upper():
            col_inicio_estrito = c
            break

    status_upper_bruto = df_temp[col_status].fillna('').astype(str).str.upper().str.strip()
    contrato_limpo_bruto = df_temp['Contrato'].fillna('').astype(str).str.strip()

    df_atend_isolado = df_temp[(status_upper_bruto.str.contains('CONCL|INIC|SUSP', na=False)) & (contrato_limpo_bruto != '') & (~contrato_limpo_bruto.isin(['nan', '0', '#N/A']))].copy()
    df_atend_isolado['Hora_Inicio_Time'] = df_atend_isolado[col_inicio_estrito].apply(tratar_horario)
    df_atend_isolado = df_atend_isolado[df_atend_isolado['Hora_Inicio_Time'].notna()]
    
    if not df_atend_isolado.empty:
        df_primeiros_horarios = df_atend_isolado.sort_values('Hora_Inicio_Time').groupby(col_recurso).first().reset_index()
        df_primeiros_horarios['Horário'] = df_primeiros_horarios['Hora_Inicio_Time'].apply(lambda x: x.strftime('%H:%M') if x else '--:--')
        
        df_primeiros_horarios['Supervisor_Limpo'] = df_primeiros_horarios[col_supervisor].fillna('NÃO IDENTIFICADO').astype(str).str.upper().str.strip()
        
        # DEFINIÇÃO DE BASE ATRAVÉS DO SUPERVISOR
        def get_base_pa(row):
            if 'REGIAO_BASE' in row and pd.notna(row['REGIAO_BASE']) and str(row['REGIAO_BASE']).strip() != '':
                return str(row['REGIAO_BASE']).upper().strip()
            sup = str(row['Supervisor_Limpo'])
            if sup in mapa_sup_base: return mapa_sup_base[sup]
            if 'FRANCISCO' in sup or 'ALAN' in sup: return 'SP'
            return 'ABC'

        df_primeiros_horarios['BASE_LIVE'] = df_primeiros_horarios.apply(get_base_pa, axis=1)
        cond_sp = df_primeiros_horarios['BASE_LIVE'].str.contains('SP|SÃO PAULO|SAO PAULO', na=False)
        
        df_exibicao = df_primeiros_horarios[['Supervisor_Limpo', col_recurso, 'Horário', 'Hora_Inicio_Time', 'BASE_LIVE']].rename(columns={col_recurso: 'Técnico', 'Supervisor_Limpo': 'Supervisor'})
        df_exibicao = df_exibicao[(df_exibicao['Técnico'] != 'N/A') & (df_exibicao['Técnico'] != '')]
        
        df_sp = df_exibicao[cond_sp].copy()
        df_abc = df_exibicao[~cond_sp].copy()

        horas_abc = df_abc['Hora_Inicio_Time'].tolist()
        horas_sp = df_sp['Hora_Inicio_Time'].tolist()
        media_abc = calcular_media_horarios(horas_abc)
        media_sp = calcular_media_horarios(horas_sp)

        st.session_state['media_global_abc'] = media_abc
        st.session_state['media_global_sp'] = media_sp

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

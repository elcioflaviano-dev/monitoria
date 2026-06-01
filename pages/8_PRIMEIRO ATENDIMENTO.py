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
    
    st.text_input("refresh_trigger_atend", value=str(st.session_state["last_refresh_atend"]), label_visibility="collapsed")
    
    if time.time() - st.session_state["last_refresh_atend"] > 60:
        st.session_state["last_refresh_atend"] = time.time()
        st.rerun()

# 2. Carregar Estilos Globais
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

# Customização CSS de Alta Performance Visual
st.markdown("""
    <style>
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

df_base = None
if df_master is not None and not df_master.empty:
    df_temp = df_master.copy()
    df_temp.columns = [str(c).strip() for c in df_temp.columns]
    
    # Captura Inteligente das Colunas Puras do Excel Sincronizado
    col_recurso = 'Recurso' if 'Recurso' in df_temp.columns else df_temp.columns[0]
    col_supervisor = 'SUPERVISOR' if 'SUPERVISOR' in df_temp.columns else 'Supervisor'
    col_status_os = 'Status da Atividade' if 'Status da Atividade' in df_temp.columns else ('STATUS_ATIVIDADE' if 'STATUS_ATIVIDADE' in df_temp.columns else df_temp.columns[3])
    col_inicio_estrito = 'Início'
    
    for c in df_temp.columns:
        get_upper = str(c).upper().strip().split('.')[0]
        if get_upper in ['INÍCIO', 'INICIO'] and '-' not in str(c) and 'DO' not in str(c).upper():
            col_inicio_estrito = c
            break

    # Extração segura
    series_recurso = df_temp[col_recurso] if col_recurso in df_temp.columns else df_temp.iloc[:, 0]
    series_status = df_temp[col_status_os] if col_status_os in df_temp.columns else df_temp.iloc[:, 3]
    series_inicio = df_temp[col_inicio_estrito] if col_inicio_estrito in df_temp.columns else df_temp.iloc[:, 10]
    series_supervisor = df_temp[col_supervisor] if col_supervisor in df_temp.columns else pd.Series([''] * len(df_temp))

    # Conversão segura para listas limpas
    lista_recurso = [str(x).strip() for x in series_recurso.fillna('N/A').tolist()]
    lista_status_os = [str(x).lower().strip() for x in series_status.fillna('').tolist()]
    lista_horarios = [tratar_horario(x) for x in series_inicio.tolist()]
    lista_supervisor = [str(x).upper().strip() for x in series_supervisor.fillna('').tolist()]

    df_base = pd.DataFrame({
        'Recurso': lista_recurso,
        'SUPERVISOR_ORIGINAL': lista_supervisor,
        'Status_OS': lista_status_os,
        'Hora_Inicio': lista_horarios
    })
    
    # 🔥 MOTOR DE DISTRIBUIÇÃO COMPLETO E CORRIGIDO PARA AS TABELAS 🔥
    def vincular_supervisor_tecnico_local(row):
        nome_u = str(row['Recurso']).upper().strip()
        sup_orig = str(row['SUPERVISOR_ORIGINAL'])
        
        # 1. Se o arquivo já trouxe o supervisor preenchido corretamente, mantém e padroniza
        if "FRANCISCO" in sup_orig: return "FRANCISCO"
        if "ALAN" in sup_orig: return "ALAN"
        if "MAICON" in sup_orig: return "MAICON"
        if "NELSON" in sup_orig: return "NELSON"
        if "MARCOS" in sup_orig: return "MARCOS ROBERTO"

        # 2. Plano B: Identifica por primeiro nome do técnico (Mapeamento Expandido)
        if "ADRIEL" in nome_u or "AMANDA" in nome_u or "DEBORA" in nome_u or "ELIAS" in nome_u or "AIRON" in nome_u: 
            return "ALAN"
        if "ALINE" in nome_u or "ALEX" in nome_u or "EDER" in nome_u or "ENOQUE" in nome_u: 
            return "FRANCISCO"
        if "MARCOS" in nome_u: 
            return "MARCOS ROBERTO"
        if "NELSON" in nome_u: 
            return "NELSON"
            
        return "MAICON"

    df_base['Supervisor'] = df_base.apply(vincular_supervisor_tecnico_local, axis=1)

if df_base is not None and not df_base.empty:
    
    # Filtra apenas os status produtivos (concluido, iniciado, suspenso)
    df_filtrado_excel = df_base[
        (df_base['Status_OS'].str.contains('concl|inic|susp', na=False)) &
        (df_base['Hora_Inicio'].notna())
    ].copy()
    
    # Agrupa pegando o menor horário da coluna Início de cada técnico
    df_primeiro = df_filtrado_excel.sort_values('Hora_Inicio').groupby('Recurso').first().reset_index()
    df_primeiro['Horário'] = df_primeiro['Hora_Inicio'].apply(lambda x: x.strftime('%H:%M') if x else '--:--')
    
    df_exibicao = df_primeiro[['Supervisor', 'Recurso', 'Horário', 'Hora_Inicio']].rename(columns={'Recurso': 'Técnico'})
    df_exibicao = df_exibicao[(df_exibicao['Técnico'] != 'N/A') & (df_exibicao['Técnico'] != '')]
    
    # Divisão Regional baseada estritamente nos supervisores mapeados
    cond_sp = df_exibicao['Supervisor'].str.contains("FRANCISCO|ALAN", na=False)
    df_sp = df_exibicao[cond_sp].copy()
    df_abc = df_exibicao[~cond_sp].copy()

    # =========================================================================
    # 🌟 MOTOR DE MEMÓRIA COMPARTILHADA DA MÉDIA DO TOPO
    # =========================================================================
    if 'media_global_abc' in st.session_state and 'media_global_sp' in st.session_state:
        media_abc = st.session_state['media_global_abc']
        media_sp = st.session_state['media_global_sp']
    else:
        horas_abc = df_primeiro[df_primeiro['Recurso'].isin(df_abc['Técnico'])]['Hora_Inicio'].tolist()
        media_abc = calcular_media_horarios(horas_abc)
        
        horas_sp = df_primeiro[df_primeiro['Recurso'].isin(df_sp['Técnico'])]['Hora_Inicio'].tolist()
        media_sp = calcular_media_horarios(horas_sp)

    # Cards superiores cravados
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
                df_sup_abc = df_abc[df_abc['Supervisor'] == sup][['Técnico', 'Horário', 'Hora_Inicio']].sort_values('Horário')
                media_supervisor = calcular_media_horarios(df_sup_abc['Hora_Inicio'].tolist())
                
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
                df_sup_sp = df_sp[df_sp['Supervisor'] == sup][['Técnico', 'Horário', 'Hora_Inicio']].sort_values('Horário')
                media_supervisor = calcular_media_horarios(df_sup_sp['Hora_Inicio'].tolist())
                
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
    st.warning("👈 Por favor, faça o upload dos arquivos de rota na página inicial primeiro.")

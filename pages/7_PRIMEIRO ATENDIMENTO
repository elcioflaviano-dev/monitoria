import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. Configuração da página ampla e título da aba
st.set_page_config(layout="wide", page_title="1º ATENDIMENTO", initial_sidebar_state="collapsed")

# 2. Carregar Estilos Globais
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

# Customização CSS para aumentar fontes das médias e ajustar layout
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem !important; }
    div[data-testid="stHorizontalBlock"] { gap: 16px !important; }
    
    /* Estilização personalizada para as tabelas ficarem mais compactas */
    .stDataFrame div {
        font-size: 13px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Título principal atualizado
st.markdown('<h1 style="font-size: 32px; font-weight: 900; color: #006677; text-align: center; margin-top: 5px; margin-bottom: 25px;">⏱️ 1º ATENDIMENTO</h1>', unsafe_allow_html=True)

# 🔄 HERANÇA INTELIGENTE DIRETA DA HOME
df_master = st.session_state.get('df_rota_ativa', None)

# Função auxiliar para converter horários
def tratar_horario(val):
    if pd.isna(val) or str(val).strip() in ['', 'N/A', 'NAN', 'NaN']:
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
    return ":".join(media_time.split(":")[:2]) # Retorna HH:MM

df_base = None
if df_master is not None and not df_master.empty:
    df_temp = df_master.copy()
    
    col_tipo = 'Tipo de Atividade' if 'Tipo de Atividade' in df_temp.columns else ('Tipo de A' if 'Tipo de A' in df_temp.columns else 'TIPO_ATIVIDADE_COL')
    col_status = 'STATUS_ATIVIDADE' if 'STATUS_ATIVIDADE' in df_temp.columns else ('Status da' if 'Status da' in df_temp.columns else 'Status da Atividade')
    col_inicio = 'Início' if 'Início' in df_temp.columns else ('Hora Início' if 'Hora Início' in df_temp.columns else None)
    
    if not col_inicio:
        for c in df_temp.columns:
            if 'INIC' in str(c).upper() or 'HORA' in str(c).upper(): col_inicio = c; break
    if col_tipo not in df_temp.columns:
        for c in df_temp.columns:
            if 'TIPO DE A' in str(c).upper() or 'TIPO ATIV' in str(c).upper(): col_tipo = c; break

    lista_recurso = [str(x).strip() for x in pd.DataFrame(df_temp['Recurso']).iloc[:, 0].fillna('N/A').tolist()] if 'Recurso' in df_temp.columns else ['N/A'] * len(df_temp)
    lista_supervisor = [str(x).upper().strip() for x in pd.DataFrame(df_temp['SUPERVISOR']).iloc[:, 0].fillna('').tolist()] if 'SUPERVISOR' in df_temp.columns else [''] * len(df_temp)
    lista_tipo_ativ = [str(x).upper().strip() for x in pd.DataFrame(df_temp[col_tipo]).iloc[:, 0].fillna('').tolist()] if col_tipo in df_temp.columns else [''] * len(df_temp)
    lista_horarios = [tratar_horario(x) for x in df_temp[col_inicio].tolist()] if col_inicio else [None] * len(df_temp)

    df_base = pd.DataFrame({
        'Recurso': lista_recurso,
        'SUPERVISOR_ORIGINAL': lista_supervisor,
        'Tipo_Atividade': lista_tipo_ativ,
        'Hora_Inicio': lista_horarios
    })
    
    df_sup_mapeado = df_base[
        (df_base['SUPERVISOR_ORIGINAL'] != '') & (~df_base['SUPERVISOR_ORIGINAL'].isin(['N/A', 'NAN', '#N/A']))
    ].groupby('Recurso')['SUPERVISOR_ORIGINAL'].first().reset_index(name='SUPERVISOR_VALIDO')
    
    df_base = pd.merge(df_base, df_sup_mapeado, on='Recurso', how='left')
    df_base['Supervisor'] = df_base['SUPERVISOR_VALIDO'].fillna(df_base['SUPERVISOR_ORIGINAL']).str.upper().str.strip()

if df_base is not None and not df_base.empty:
    
    # Filtra apenas registros de campo produtivos com horário válido
    df_produtivo = df_base[
        (~df_base['Tipo_Atividade'].str.contains("BASE|REFEI|ALMO|DESLOCAMENTO FIM", na=False)) &
        (df_base['Hora_Inicio'].notna())
    ].copy()
    
    df_primeiro = df_produtivo.sort_values('Hora_Inicio').groupby('Recurso').first().reset_index()
    df_primeiro['Horário'] = df_primeiro['Hora_Inicio'].apply(lambda x: x.strftime('%H:%M') if x else '--:--')
    
    df_exibicao = df_primeiro[['Supervisor', 'Recurso', 'Horário', 'Hora_Inicio']].rename(columns={'Recurso': 'Técnico'})
    df_exibicao = df_exibicao[(df_exibicao['Técnico'] != 'N/A') & (df_exibicao['Técnico'] != '')]
    
    # Separação das bases
    df_sp = df_exibicao[df_exibicao['Supervisor'].fillna('').str.contains("FRANCISCO|ALAN", na=False)].copy()
    df_abc = df_exibicao[~df_exibicao['Supervisor'].fillna('').str.contains("FRANCISCO|ALAN", na=False)].copy()

    # ==========================================
    # 🔴 BLOCÃO REGIÃO ABC
    # ==========================================
    horas_abc = df_primeiro[df_primeiro['Recurso'].isin(df_abc['Técnico'])]['Hora_Inicio'].tolist()
    media_abc = calcular_media_horarios(horas_abc)
    
    # Barra de Título Regional com FONTE DA MÉDIA AUMENTADA (font-size: 20px)
    st.markdown(f'''
        <div style="background-color:#008080; padding:10px 18px; border-radius:6px; margin-bottom:15px; display:flex; justify-content:space-between; align-items:center;">
            <span style="color:white; font-weight:bold; font-size:22px; margin:0;">📍 BASE ABC</span>
            <span style="background-color:rgba(255,255,255,0.25); color:white; padding:6px 14px; border-radius:4px; font-weight:900; font-size:20px; letter-spacing: 0.5px;">⏱️ MÉDIA REAL: {media_abc}</span>
        </div>
    ''', unsafe_allow_html=True)
    
    if not df_abc.empty:
        supervisores_abc = sorted(df_abc['Supervisor'].unique().tolist())
        cols_abc = st.columns(len(supervisores_abc))
        
        for i, sup in enumerate(supervisores_abc):
            with cols_abc[i]:
                df_sup_abc = df_abc[df_abc['Supervisor'] == sup][['Técnico', 'Horário', 'Hora_Inicio']].sort_values('Horário')
                
                horas_especificas = df_sup_abc['Hora_Inicio'].tolist()
                media_supervisor = calcular_media_horarios(horas_especificas)
                
                # Card do Supervisor com FONTE DA MÉDIA INTERNA MAIOR (font-size: 14px)
                st.markdown(f'''
                    <div style="background-color:#f1f7f6; border-left:4px solid #008080; padding:8px 12px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                        <span style="font-weight:bold; color:#004d40; font-size:14px; text-transform: uppercase;">👤 {sup}</span>
                        <span style="background-color:#008080; color:white; padding:3px 8px; border-radius:3px; font-weight:900; font-size:14px;">⏱️ {media_supervisor}</span>
                    </div>
                ''', unsafe_allow_html=True)
                
                st.dataframe(df_sup_abc[['Técnico', 'Horário']], use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum atendimento produtivo registrado na região ABC.")

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # ==========================================
    # 🔵 BLOCÃO REGIÃO SÃO PAULO (SP)
    # ==========================================
    horas_sp = df_primeiro[df_primeiro['Recurso'].isin(df_sp['Técnico'])]['Hora_Inicio'].tolist()
    media_sp = calcular_media_horarios(horas_sp)
    
    # Barra de Título Regional com FONTE DA MÉDIA AUMENTADA (font-size: 20px)
    st.markdown(f'''
        <div style="background-color:#b30000; padding:10px 18px; border-radius:6px; margin-bottom:15px; display:flex; justify-content:space-between; align-items:center;">
            <span style="color:white; font-weight:bold; font-size:22px; margin:0;">📍 BASE SÃO PAULO (SP)</span>
            <span style="background-color:rgba(255,255,255,0.25); color:white; padding:6px 14px; border-radius:4px; font-weight:900; font-size:20px; letter-spacing: 0.5px;">⏱️ MÉDIA REAL: {media_sp}</span>
        </div>
    ''', unsafe_allow_html=True)
    
    if not df_sp.empty:
        supervisores_sp = sorted(df_sp['Supervisor'].unique().tolist())
        cols_sp = st.columns(len(supervisores_sp))
        
        for i, sup in enumerate(supervisores_sp):
            with cols_sp[i]:
                df_sup_sp = df_sp[df_sp['Supervisor'] == sup][['Técnico', 'Horário', 'Hora_Inicio']].sort_values('Horário')
                
                horas_especificas = df_sup_sp['Hora_Inicio'].tolist()
                media_supervisor = calcular_media_horarios(horas_especificas)
                
                # Card do Supervisor com FONTE DA MÉDIA INTERNA MAIOR (font-size: 14px)
                st.markdown(f'''
                    <div style="background-color:#fff2f2; border-left:4px solid #b30000; padding:8px 12px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                        <span style="font-weight:bold; color:#660000; font-size:14px; text-transform: uppercase;">👤 {sup}</span>
                        <span style="background-color:#b30000; color:white; padding:3px 8px; border-radius:3px; font-weight:900; font-size:14px;">⏱️ {media_supervisor}</span>
                    </div>
                ''', unsafe_allow_html=True)
                
                st.dataframe(df_sup_sp[['Técnico', 'Horário']], use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum atendimento produtivo registrado na região de SP.")
else:
    st.warning("👈 Por favor, faça o upload dos arquivos de rota na página inicial primeiro.")

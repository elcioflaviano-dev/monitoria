import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. Configuração da página ampla
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 2. Carregar Estilos Globais
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

st.markdown('<h1 style="font-size: 34px; font-weight: 900; color: #006677; text-align: center; margin-top: 20px; margin-bottom: 5px;">⏱️ HORÁRIO DO 1º ATENDIMENTO</h1>', unsafe_allow_html=True)

# 🔄 HERANÇA INTELIGENTE DIRETA DA HOME
df_master = st.session_state.get('df_rota_ativa', None)

# Função auxiliar para converter horários em texto/datetime para cálculo de média
def tratar_horario(val):
    if pd.isna(val) or str(val).strip() in ['', 'N/A', 'NAN', 'NaN']:
        return None
    try:
        # Tenta extrair apenas a hora (HH:MM:SS ou HH:MM) caso venha com data junto
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

df_ativar = None
if df_master is not None and not df_master.empty:
    df_temp = df_master.copy()
    
    # Identificação dinâmica das colunas
    col_tipo = 'Tipo de Atividade' if 'Tipo de Atividade' in df_temp.columns else ('Tipo de A' if 'Tipo de A' in df_temp.columns else 'TIPO_ATIVIDADE_COL')
    col_status = 'STATUS_ATIVIDADE' if 'STATUS_ATIVIDADE' in df_temp.columns else ('Status da' if 'Status da' in df_temp.columns else 'Status da Atividade')
    col_inicio = 'Início' if 'Início' in df_temp.columns else ( 'Hora Início' if 'Hora Início' in df_temp.columns else None)
    
    # Busca aproximada para coluna de horário de início caso mude o nome
    if not col_inicio:
        for c in df_temp.columns:
            if 'INIC' in str(c).upper() or 'HORA' in str(c).upper() or 'AGEND' in str(c).upper(): col_inicio = c; break

    if col_tipo not in df_temp.columns:
        for c in df_temp.columns:
            if 'TIPO DE A' in str(c).upper() or 'TIPO ATIV' in str(c).upper(): col_tipo = c; break

    # Extração de segurança
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
    
    # PROCV do Supervisor pelo Nome do técnico para garantir linhas limpas
    df_sup_mapeado = df_base[
        (df_base['SUPERVISOR_ORIGINAL'] != '') & (~df_base['SUPERVISOR_ORIGINAL'].isin(['N/A', 'NAN', '#N/A']))
    ].groupby('Recurso')['SUPERVISOR_ORIGINAL'].first().reset_index(name='SUPERVISOR_VALIDO')
    
    df_base = pd.merge(df_base, df_sup_mapeado, on='Recurso', how='left')
    df_base['Supervisor'] = df_base['SUPERVISOR_VALIDO'].fillna(df_base['SUPERVISOR_ORIGINAL']).str.upper().str.strip()

# --- HEADER DE RETORNO ---
if df_base is not None:
    st.markdown(f'<div style="text-align: center; color: #555; font-size: 13px; font-weight: bold; margin-bottom: 20px;">📊 Analisando o primeiro acionamento de campo produtivo do dia</div>', unsafe_allow_html=True)
else:
    st.warning("👈 Por favor, faça o upload dos arquivos de rota na página inicial primeiro.")

# --- PROCESSAMENTO OPERACIONAL ---
if df_base is not None and not df_base.empty:
    
    # 1. Filtra apenas O.S. produtivas de verdade (descarta Base, Refeição, Deslocamento Fim, etc.)
    df_produtivo = df_base[
        (~df_base['Tipo_Atividade'].str.contains("BASE|REFEI|ALMO|DESLOCAMENTO FIM", na=False)) &
        (df_base['Hora_Inicio'].notna())
    ].copy()
    
    # 2. Captura o primeiro atendimento de cada técnico (menor horário registrado)
    df_primeiro = df_produtivo.sort_values('Hora_Inicio').groupby('Recurso').first().reset_index()
    
    # Formata a hora para exibição amigável na tabela (HH:MM)
    df_primeiro['1º Atendimento'] = df_primeiro['Hora_Inicio'].apply(lambda x: x.strftime('%H:%M') if x else '--:--')
    
    # Seleção e renomeação final das colunas da tabela
    df_exibicao = df_primeiro[['Supervisor', 'Recurso', '1º Atendimento']].rename(columns={'Recurso': 'Técnico'})
    
    # Limpa possíveis registros fantasmas
    df_exibicao = df_exibicao[(df_exibicao['Técnico'] != 'N/A') & (df_exibicao['Técnico'] != '')]
    
    # Divisão Regional (Francisco/Alan = SP, o restante é ABC)
    df_sp = df_exibicao[df_exibicao['Supervisor'].fillna('').str.contains("FRANCISCO|ALAN", na=False)].copy()
    df_abc = df_exibicao[~df_exibicao['Supervisor'].fillna('').str.contains("FRANCISCO|ALAN", na=False)].copy()

    # Estilização da linha de sumário de médias
    def destacar_linha_media(row):
        return ['background-color: #dfede9; font-weight: bold; color: #004d40; border-top: 2px solid #008080;'] * len(row)

    # ==========================================
    # 🔴 REGIÃO ABC
    # ==========================================
    st.markdown('<div style="background-color:#008080; padding:6px 12px; border-radius:4px; margin-bottom:15px;"><h2 style="color:white; margin:0px; font-size:22px;">📍 1º ATENDIMENTO DO DIA - REGIÃO ABC</h2></div>', unsafe_allow_html=True)
    
    if not df_abc.empty:
        st.dataframe(df_abc.sort_values(['Supervisor', '1º Atendimento']), use_container_width=True, hide_index=True)
        
        # Extrai a lista de objetos datetime.time para tirar a média real
        lista_horas_abc = df_primeiro[df_primeiro['Recurso'].isin(df_abc['Técnico'])]['Hora_Inicio'].tolist()
        media_abc = calcular_media_horarios(lista_horas_abc)
        
        df_tot_abc = pd.DataFrame([{"Supervisor": "MÉDIA DA BASE ABC", "Técnico": "-", "1º Atendimento": f"⏱️ {media_abc}"}])
        st.dataframe(df_tot_abc.style.apply(destacar_linha_media, axis=1), use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum atendimento produtivo iniciado na região ABC até o momento.")

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # ==========================================
    # 🔵 REGIÃO SÃO PAULO (SP)
    # ==========================================
    st.markdown('<div style="background-color:#b30000; padding:6px 12px; border-radius:4px; margin-bottom:15px;"><h2 style="color:white; margin:0px; font-size:22px;">📍 1º ATENDIMENTO DO DIA - REGIÃO SÃO PAULO (SP)</h2></div>', unsafe_allow_html=True)
    
    if not df_sp.empty:
        st.dataframe(df_sp.sort_values(['Supervisor', '1º Atendimento']), use_container_width=True, hide_index=True)
        
        # Extrai a lista de objetos datetime.time para tirar a média real
        lista_horas_sp = df_primeiro[df_primeiro['Recurso'].isin(df_sp['Técnico'])]['Hora_Inicio'].tolist()
        media_sp = calcular_media_horarios(lista_horas_sp)
        
        df_tot_sp = pd.DataFrame([{"Supervisor": "MÉDIA DA BASE SÃO PAULO", "Técnico": "-", "1º Atendimento": f"⏱️ {media_sp}"}])
        st.dataframe(df_tot_sp.style.apply(destacar_linha_media, axis=1), use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum atendimento produtivo iniciado na região de SP até o momento.")

import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

# 1. Configuração da página ampla
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 2. Carregar Estilos Globais
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

st.markdown('<h1 style="font-size: 34px; font-weight: 900; color: #006677; text-align: center; margin-top: 20px; margin-bottom: 5px;">📊 INDICADORES IA - ANÁLISE OPERACIONAL</h1>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #666; font-size: 14px; margin-bottom: 25px;">TMA, Ranking de Produtividade Técnica e Causa Raiz de O.S NE</div>', unsafe_allow_html=True)

# 🔄 HERANÇA INTELIGENTE DIRETA DA HOME
df_master = st.session_state.get('df_rota_ativa', None)

df_av = None
if df_master is not None and not df_master.empty:
    # Mapeamento seguro preventivo contra colunas duplicadas no Excel (.iloc[:, 0])
    col_janela = 'Janela de Serviço' if 'Janela de Serviço' in df_master.columns else 'Intervalo de Tempo'
    col_status_at = 'STATUS_ATIVIDADE' if 'STATUS_ATIVIDADE' in df_master.columns else 'Status da Atividade'
    
    col_tipo_os = 'Tipo O.S 1' if 'Tipo O.S 1' in df_master.columns else ('Tipo de OS' if 'Tipo de OS' in df_master.columns else None)
    if not col_tipo_os:
        for c in df_master.columns:
            if 'OS' in str(c).upper() and 'STATUS' not in str(c).upper(): col_tipo_os = c; break
            
    lista_supervisor = [str(x).upper().strip() for x in pd.DataFrame(df_master['SUPERVISOR']).iloc[:, 0].fillna('N/A').tolist()] if 'SUPERVISOR' in df_master.columns else ['N/A'] * len(df_master)
    lista_recurso = [str(x).upper().strip() for x in pd.DataFrame(df_master['Recurso']).iloc[:, 0].fillna('N/A').tolist()] if 'Recurso' in df_master.columns else ['N/A'] * len(df_master)
    lista_status_at = [str(x).upper().strip() for x in pd.DataFrame(df_master[col_status_at]).iloc[:, 0].fillna('PENDENTE').tolist()] if col_status_at in df_master.columns else ['PENDENTE'] * len(df_master)
    
    if col_tipo_os:
        lista_tipo_os = [str(x).upper().strip() for x in pd.DataFrame(df_master[col_tipo_os]).iloc[:, 0].fillna('N/A').tolist()]
    else:
        lista_tipo_os = ['N/A'] * len(df_master)
        
    lista_status_os1 = [str(x).strip() for x in pd.DataFrame(df_master['STATUS_OS1']).iloc[:, 0].fillna('').tolist()] if 'STATUS_OS1' in df_master.columns else [''] * len(df_master)
    
    col_tipo_ativ = 'Tipo de Atividade' if 'Tipo de Atividade' in df_master.columns else 'TIPO_ATIVIDADE_COL'
    lista_tipo_ativ = [str(x).upper().strip() for x in pd.DataFrame(df_master[col_tipo_ativ]).iloc[:, 0].fillna('').tolist()] if col_tipo_ativ in df_master.columns else [''] * len(df_master)

    lista_janela = [str(x).strip() for x in pd.DataFrame(df_master[col_janela]).iloc[:, 0].fillna('SEM JANELA').tolist()] if col_janela in df_master.columns else ['SEM JANELA'] * len(df_master)
    col_vol = 'Total de Tarefas' if 'Total de Tarefas' in df_master.columns else ('VOLUME' if 'VOLUME' in df_master.columns else 'QTD_OS_COL')
    lista_vol = [str(x).strip() for x in pd.DataFrame(df_master[col_vol]).iloc[:, 0].fillna('1').tolist()] if col_vol in df_master.columns else ['1'] * len(df_master)

    # Criação do DataFrame unificado e higienizado para os Indicadores Analíticos
    df_av = pd.DataFrame({
        'Supervisor_Upper': lista_supervisor,
        'Recurso_Upper': lista_recurso,
        'STATUS_ATIVIDADE': lista_status_at,
        'Tipo_OS_Upper': lista_tipo_os,
        'STATUS_OS1': lista_status_os1,
        'Tipo_Ativ_Check': lista_tipo_ativ,
        'Janela': lista_janela,
        'QTD_OS_COL': lista_vol,
        'SUPERVISOR': lista_supervisor,
        'Recurso': lista_recurso
    })

# --- EXIBIÇÃO DA DATA DE ATUALIZAÇÃO SINCADA ---
data_sinc = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
if df_av is not None:
    st.markdown(f'<div style="text-align: center; color: #555; font-size: 13px; font-weight: bold; margin-bottom: 25px;">🔄 Motor de Indicadores Sincronizado em tempo real via Upload: <span style="color: #006677;">{data_sinc}</span></div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div style="text-align: center; color: #cc6600; font-size: 13px; font-weight: bold; margin-bottom: 25px;">⚠️ Aguardando upload dos arquivos na página inicial</div>', unsafe_allow_html=True)

# Lógica padrão de conversão de status
def status_operacional(baixa, status_at):
    baixa = str(baixa).upper().strip()
    status_at = str(status_at).upper().strip()
    codigos_ne = ["101", "106", "110", "112", "113", "125", "203", "205", "206", "301", "305", "306", "402", "100"]
    for cod in codigos_ne:
        if baixa.startswith(cod) or f"{cod} -" in baixa: return "O.S NE"
    if "PENDENTE" in baixa or "INICIADO" in baixa or "EM ROTA" in baixa or "PENDENTE" in status_at: return "EM ABERTO"
    return "PRODUTIVO"

if df_av is not None and not df_av.empty:
    
    # Filtros de Limpeza Rígidos originais
    df_av = df_av[(~df_av['Supervisor_Upper'].isin(['#N/A', 'N/A', '', 'NAN'])) & (df_av['STATUS_ATIVIDADE'] != "SUSPENSO")].copy()
    df_av = df_av[~df_av['Recurso_Upper'].str.contains('TEC1|TEC 1', na=False)].copy()
    
    # Conversão de volume real baseado na coluna Total de Tarefas
    if 'QTD_OS_COL' in df_av.columns:
        df_av['QTD_OS_NUM'] = pd.to_numeric(df_av['QTD_OS_COL'], errors='coerce').fillna(0).astype(int)
    else:
        df_av['QTD_OS_NUM'] = 1
        
    df_av['Classificacao_Excel'] = df_av.apply(lambda r: status_operacional(r['STATUS_OS1'], r['STATUS_ATIVIDADE']), axis=1)

    # -------------------------------------------------------------------------
    # 🏆 SEÇÃO 1: RANKING DE PRODUTIVIDADE INDIVIDUAL
    # -------------------------------------------------------------------------
    st.markdown('<div style="background-color:#008080; padding:6px 12px; border-radius:4px; margin-bottom:15px;"><h3 style="color:white; margin:0px; font-size:20px;">🏆 RANKING DE PRODUTIVIDADE INDIVIDUAL (TOP PRODUTIVOS)</h3></div>', unsafe_allow_html=True)
    
    df_produtivos = df_av[df_av['Classificacao_Excel'] == 'PRODUTIVO'].groupby(['Supervisor_Upper', 'Recurso_Upper'])['QTD_OS_NUM'].sum().reset_index()
    df_produtivos = df_produtivos.sort_values(by='QTD_OS_NUM', ascending=False).reset_index(drop=True)
    df_produtivos.index = df_produtivos.index + 1
    df_produtivos = df_produtivos.rename(columns={'Supervisor_Upper': 'Supervisor', 'Recurso_Upper': 'Nome do Técnico', 'QTD_OS_NUM': 'Total O.S Produtivas'})
    
    c_rank1, c_rank2 = st.columns([2, 1])
    with c_rank1:
        st.markdown("**📈 Desempenho de Entregas por Técnico**")
        st.dataframe(df_produtivos, use_container_width=True, hide_index=False)
    with c_rank2:
        st.markdown("**⭐ Destaques da Operação (Top 3)**")
        if not df_produtivos.empty:
            for i, row in df_produtivos.head(3).iterrows():
                st.success(f"🏅 **{i}º Lugar:** {row['Nome do Técnico']} ({row['Total O.S Produtivas']} OS) - Equipe: {row['Supervisor']}")
        else:
            st.info("Aguardando confirmação de ordens produtivas na base.")

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # ⏱️ SEÇÃO 2: VOLUME POR JANELA DE ATENDIMENTO
    # -------------------------------------------------------------------------
    st.markdown('<div style="background-color:#005088; padding:6px 12px; border-radius:4px; margin-bottom:15px;"><h3 style="color:white; margin:0px; font-size:20px;">⏱️ COMPORTAMENTO DE VOLUME POR JANELA DE SERVIÇO</h3></div>', unsafe_allow_html=True)
    
    if 'Janela' in df_av.columns:
        df_av['Janela_Limpa'] = df_av['Janela'].fillna('SEM JANELA').astype(str).str.strip()
        df_janelas = df_av.groupby(['Janela_Limpa', 'Classificacao_Excel'])['QTD_OS_NUM'].sum().unstack(fill_value=0).reset_index()
        
        for c in ['PRODUTIVO', 'O.S NE', 'EM ABERTO']:
            if c not in df_janelas.columns: df_janelas[c] = 0
            
        df_janelas['Total Geral'] = df_janelas['PRODUTIVO'] + df_janelas['O.S NE'] + df_janelas['EM ABERTO']
        df_janelas = df_janelas.rename(columns={'Janela_Limpa': 'Horário / Janela de Agendamento'})
        st.dataframe(df_janelas, use_container_width=True, hide_index=True)
    else:
        st.info("Coluna de Janela/Horário de atendimento não localizada no mapeamento.")

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 📉 SEÇÃO 3: ANÁLISE DE CAUSA RAIZ (CÓDIGOS DE NE)
    # -------------------------------------------------------------------------
    st.markdown('<div style="background-color:#b30000; padding:6px 12px; border-radius:4px; margin-bottom:15px;"><h3 style="color:white; margin:0px; font-size:20px;">📉 ANÁLISE DE CAUSA RAIZ - CÓDIGOS DE QUEBRA (O.S NE)</h3></div>', unsafe_allow_html=True)
    
    df_ne_only = df_av[df_av['Classificacao_Excel'] == 'O.S NE'].copy()
    
    if not df_ne_only.empty:
        df_ne_only['Código Motivo'] = df_ne_only['STATUS_OS1'].apply(lambda x: str(x).strip()[:40] if len(str(x)) > 0 else "Código Não Informado")
        
        df_causa = df_ne_only.groupby('Código Motivo')['QTD_OS_NUM'].sum().reset_index(name='Soma OS')
        df_causa = df_causa.sort_values(by='Soma OS', ascending=False).reset_index(drop=True)
        
        c_graf1, c_graf2 = st.columns([1, 1])
        with c_graf1:
            st.markdown("**📋 Tabela Consolidada de Motivos de Não Execução**")
            st.dataframe(df_causa, use_container_width=True, hide_index=True)
        with c_graf2:
            st.markdown("**📊 Gráfico de Concentração das Quebras**")
            chart = alt.Chart(df_causa.head(7)).mark_bar(color='#b30000').encode(
                x=alt.X('Soma OS:Q', title='Volume de Quebras'),
                y=alt.Y('Código Motivo:N', sort='-x', title=None)
            ).properties(height=250)
            st.altair_chart(chart, use_container_width=True)
    else:
        st.success("✅ Excelente! Nenhuma quebra por O.S NE foi registrada na base de dados hoje.")

else:
    st.warning("👈 Por favor, faça o upload dos arquivos de rota na página inicial (streamlit_app.py) primeiro para processar os indicadores analíticos.")

st.markdown("---")

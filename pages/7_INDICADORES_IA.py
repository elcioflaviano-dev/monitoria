import streamlit as st
import pandas as pd
import requests
import io
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

# === FUNÇÃO DE CARGA OPERACIONAL ONLINE ===
def buscar_base_rotas_online():
    try:
        url = st.secrets.get('public_gsheets_url', "https://docs.google.com/spreadsheets/d/1kB1YmUuhzHpfN1dLv8PaQn0ipXcHcd6kGKnI3nguT14/edit?gid=208394608#gid=208394608").strip()
        if 'spreadsheets/d/' in url:
            id_planilha = url.split('/spreadsheets/d/')[1].split('/')[0].strip()
            csv_url = f"https://docs.google.com/spreadsheets/d/{id_planilha}/export?format=csv"
            if 'gid=' in url:
                gid = url.split('gid=')[1].split('#')[0].split('&')[0].strip()
                csv_url += f"&gid={gid}"
        else:
            csv_url = url

        headers = {'User-Agent': 'Mozilla/5.0'}
        resposta = requests.get(csv_url, headers=headers, timeout=15)
        if resposta.status_code != 200:
            return None
            
        import zoneinfo
        fuso_sp = zoneinfo.ZoneInfo("America/Sao_Paulo")
        st.session_state['data_avancados'] = datetime.now(fuso_sp).strftime('%d/%m/%Y às %H:%M:%S')

        conteudo_bruto = resposta.text
        linhas_puras = conteudo_bruto.splitlines()
        
        linha_do_cabecalho_real = 0
        encontrou_cabecalho = False
        for i, texto_linha in enumerate(linhas_puras[:30]):
            linha_upper = texto_linha.upper()
            if 'SUPERVISOR' in linha_upper or 'CONTRATO' in linha_upper or 'INTERVALO' in linha_upper or 'STATUS' in linha_upper:
                linha_do_cabecalho_real = i
                encontrou_cabecalho = True
                break

        if encontrou_cabecalho:
            texto_corrigido = "\n".join(linhas_puras[linha_do_cabecalho_real:])
            df_sheets = pd.read_csv(io.StringIO(texto_corrigido), dtype=str, on_bad_lines='skip')
        else:
            df_sheets = pd.read_csv(io.StringIO(conteudo_bruto), dtype=str, on_bad_lines='skip')
            
        if df_sheets is None or df_sheets.empty:
            return None

        df_sheets.columns = [str(c).strip().replace('\xa0', ' ') for c in df_sheets.columns]
        df_final = df_sheets.copy()
        
        colunas_mapeadas = {}
        for col in df_sheets.columns:
            col_upper = col.upper()
            if 'SUPERVISOR' in col_upper: colunas_mapeadas[col] = 'SUPERVISOR'
            elif ('INTERVALO' in col_upper or 'TEMPO' in col_upper or 'JANELA' in col_upper): colunas_mapeadas[col] = 'Janela'
            elif 'STATUS' in col_upper: colunas_mapeadas[col] = 'STATUS_ATIVIDADE'
            elif ('RECURSO' in col_upper or 'TECNICO' in col_upper or 'TÉCNICO' in col_upper): colunas_mapeadas[col] = 'Recurso'
            elif ('TIPO O.S 1' in col_upper or 'TIPO DE OS' in col_upper or 'TIPO ATIVIDADE' in col_upper): colunas_mapeadas[col] = 'Tipo O.S 1'
            elif ('STATUS DA O.S 1' in col_upper or 'STATUS OS 1' in col_upper or 'BAIXA' in col_upper): colunas_mapeadas[col] = 'STATUS_OS1'
            elif ('TOTAL DE TAREFAS' in col_upper or 'TOTAL TAREFAS' in col_upper or 'VOLUME' in col_upper): colunas_mapeadas[col] = 'QTD_OS_COL'
            elif ('CATEGORIA' in col_upper or 'CAPACIDADE' in col_upper): colunas_mapeadas[col] = 'CATEGORIA_CAPACIDADE'
        
        df_final = df_final.rename(columns=colunas_mapeadas)
        df_final = df_final.loc[:, ~df_final.columns.duplicated()]
            
        return df_final
    except:
        return None

df_av = buscar_base_rotas_online()

data_sinc = st.session_state.get('data_avancados', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
st.markdown(f'<div style="text-align: center; color: #555; font-size: 13px; font-weight: bold; margin-bottom: 25px;">🔄 Motor de IA Sincronizado: <span style="color: #006677;">{data_sinc}</span></div>', unsafe_allow_html=True)

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
    
    # Higienização Geral da Base
    df_av['Supervisor_Upper'] = df_av['SUPERVISOR'].fillna('N/A').astype(str).str.upper().str.strip()
    df_av['Recurso_Upper'] = df_av['Recurso'].fillna('N/A').astype(str).str.upper().str.strip()
    df_av['Status_Atividade_Upper'] = df_av['STATUS_ATIVIDADE'].fillna('').astype(str).str.upper().str.strip()
    df_av['Tipo_OS_Upper'] = df_av['Tipo O.S 1'].fillna('').astype(str).str.upper().str.strip()
    df_av['STATUS_OS1'] = df_av['STATUS_OS1'].fillna('').astype(str).str.strip()
    
    # Filtros de Limpeza Rígidos
    df_av = df_av[(~df_av['Supervisor_Upper'].isin(['#N/A', 'N/A', '', 'NAN'])) & (df_av['Status_Atividade_Upper'] != "SUSPENSO")].copy()
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
        for i, row in df_produtivos.head(3).iterrows():
            st.success(f"🏅 **{i}º Lugar:** {row['Nome do Técnico']} ({row['Total O.S Produtivas']} OS) - Equipe: {row['Supervisor']}")

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
    st.warning("⚠️ Aguardando carregamento estável dos dados para renderizar as análises.")

import streamlit as st
import pandas as pd
import requests
import io
from datetime import datetime

# 1. Configuração da página ampla
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 2. Carregar Estilos Globais
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

st.markdown('<h1 style="font-size: 34px; font-weight: 900; color: #005088; text-align: center; margin-top: 20px; margin-bottom: 5px;">🤖 PAINEL IA - INTELIGÊNCIA PREDITIVA</h1>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #666; font-size: 14px; margin-bottom: 20px;">Análise preditiva em tempo real usando modelos estatísticos locais (R$ 0,00)</div>', unsafe_allow_html=True)

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
        st.session_state['data_preditivo'] = datetime.now(fuso_sp).strftime('%d/%m/%Y às %H:%M:%S')
        st.session_state['hora_atual_int'] = datetime.now(fuso_sp).hour

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
            elif 'STATUS' in col_upper: colunas_mapeadas[col] = 'STATUS_ATIVIDADE'
            elif ('RECURSO' in col_upper or 'TECNICO' in col_upper or 'TÉCNICO' in col_upper): colunas_mapeadas[col] = 'Recurso'
            elif ('TIPO DE ATIVIDADE' in col_upper or 'TIPO ATIVIDADE' in col_upper): colunas_mapeadas[col] = 'Tipo de Atividade'
            elif ('TIPO O.S 1' in col_upper or 'TIPO DE OS' in col_upper or 'TIPO ATIVIDADE' in col_upper): colunas_mapeadas[col] = 'Tipo O.S 1'
            elif ('STATUS DA O.S 1' in col_upper or 'STATUS OS 1' in col_upper or 'BAIXA' in col_upper): colunas_mapeadas[col] = 'STATUS_OS1'
            elif ('TOTAL DE TAREFAS' in col_upper or 'TOTAL TAREFAS' in col_upper or 'VOLUME' in col_upper): colunas_mapeadas[col] = 'QTD_OS_COL'
        
        df_final = df_final.rename(columns=colunas_mapeadas)
        df_final = df_final.loc[:, ~df_final.columns.duplicated()]
            
        return df_final
    except:
        return None

df_ia = buscar_base_rotas_online()

data_sinc = st.session_state.get('data_preditivo', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
hora_atual = st.session_state.get('hora_atual_int', 8)
st.markdown(f'<div style="text-align: center; color: #555; font-size: 13px; font-weight: bold; margin-bottom: 25px;">🔄 Motor de IA Sincronizado: <span style="color: #005088;">{data_sinc}</span></div>', unsafe_allow_html=True)

# Lógica de quebra analítica para alimentar a árvore preditiva
def inteligência_status_excel(baixa, status_at):
    baixa = str(baixa).upper().strip()
    status_at = str(status_at).upper().strip()
    codigos_ne = ["101", "106", "110", "112", "113", "125", "203", "205", "206", "301", "305", "306", "402", "100"]
    for cod in codigos_ne:
        if baixa.startswith(cod): return "O.S NE"
    if "PENDENTE" in baixa or "INICIADO" in baixa or "EM ROTA" in baixa or "PENDENTE" in status_at: return "EM ABERTO"
    return "PRODUTIVO"

if df_ia is not None and not df_ia.empty:
    
    # Higienização Padrão Máster das colunas
    df_ia['Supervisor_Upper'] = df_ia['SUPERVISOR'].fillna('N/A').astype(str).str.upper().str.strip()
    df_ia['Recurso_Upper'] = df_ia['Recurso'].fillna('N/A').astype(str).str.upper().str.strip()
    df_ia['Status_Atividade_Upper'] = df_ia['STATUS_ATIVIDADE'].fillna('').astype(str).str.upper().str.strip()
    df_ia['Tipo_OS_Upper'] = df_ia['Tipo O.S 1'].fillna('').astype(str).str.upper().str.strip()
    df_ia['STATUS_OS1'] = df_ia['STATUS_OS1'].fillna('')
    
    # Expulsa dados desnecessários ou poluídos
    df_ia = df_ia[(~df_ia['Supervisor_Upper'].isin(['#N/A', 'N/A', '', 'NAN'])) & (df_ia['Status_Atividade_Upper'] != "SUSPENSO")].copy()
    df_ia = df_ia[~df_ia['Recurso_Upper'].str.contains('TEC1|TEC 1', na=False)].copy()
    
    df_ia['Classe_Analitica'] = df_ia.apply(lambda r: inteligência_status_excel(r['STATUS_OS1'], r['STATUS_ATIVIDADE']), axis=1)

    # -------------------------------------------------------------------------
    # 🔮 MÓDULO IA 1: MONITOR DE RISCO DE QUEBRA EM TEMPO REAL
    # -------------------------------------------------------------------------
    st.markdown('### 🔮 MÓDULO 1: PREVISOR DE RISCO DE QUEBRA (CONTRATOS EM CAMPO)')
    
    # Gera o fator probabilístico cruzando as quebras atuais de cada carteira
    historico_quebra = df_ia.groupby(['Supervisor_Upper', 'Tipo_OS_Upper']).apply(
        lambda x: (x['Classe_Analitica'] == 'O.S NE').sum() / ((x['Classe_Analitica'] == 'PRODUTIVO').sum() + (x['Classe_Analitica'] == 'O.S NE').sum() + 0.001)
    ).reset_index(name='Fator_Risco')

    # Filtra ordens que estão ativas na rua neste minuto
    df_rua = df_ia[df_ia['Status_Atividade_Upper'].isin(['EM ROTA', 'INICIADO', 'PENDENTE']) & (df_ia['Tipo_OS_Upper'] != 'NA BASE')].copy()
    
    if not df_rua.empty:
        df_analisado = pd.merge(df_rua, historico_quebra, on=['Supervisor_Upper', 'Tipo_OS_Upper'], how='left')
        df_analisado['Fator_Risco'] = df_analisado['Fator_Risco'].fillna(0.15)
        
        # Algoritmo local ponderando o status atual e peso histórico da carteira
        df_analisado['Probabilidade_Quebra'] = df_analisado.apply(
            lambda r: min(95.0, round((r['Fator_Risco'] * 100) + (25 if r['Status_Atividade_Upper'] == 'PENDENTE' else 10), 2)), axis=1
        )
        
        # Isola os registros com criticidade acima do limite aceitável (30%)
        df_risco = df_analisado[df_analisado['Probabilidade_Quebra'] >= 30.0].copy()
        
        if not df_risco.empty:
            df_vitrine_ia = df_risco.groupby(['Supervisor_Upper', 'Recurso_Upper', 'Tipo_OS_Upper', 'Status_Atividade_Upper'])['Probabilidade_Quebra'].max().reset_index()
            df_vitrine_ia = df_vitrine_ia.sort_values(by='Probabilidade_Quebra', ascending=False)
            df_vitrine_ia = df_vitrine_ia.rename(columns={
                'Supervisor_Upper': 'Supervisor', 'Recurso_Upper': 'Técnico em Campo', 
                'Tipo_OS_Upper': 'Descrição da O.S', 'Status_Atividade_Upper': 'Status Atual', 'Probabilidade_Quebra': 'Probabilidade de Quebra (%)'
            })
            
            st.dataframe(df_vitrine_ia, use_container_width=True, hide_index=True)
            st.caption("💡 *Ação Recomendada:* Monitores devem focar suporte preventivo nos técnicos no topo da lista.")
        else:
            st.success("🧠 IA analisou as rotas ativas: Nenhuma anomalia de alto risco detectada em campo.")
    else:
        st.info("Nenhum contrato ativo em campo para análise neste momento.")

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 🚨 MÓDULO IA 2: ALERTA PREDITIVO DE ABSENTEÍSMO
    # -------------------------------------------------------------------------
    st.markdown('### 🚨 MÓDULO 2: ALERTA PREDITIVO DE ABSENTEÍSMO (LARGADA MATINAL)')
    
    if 'Tipo de Atividade' in df_ia.columns:
        df_ia['Tipo_Ativ_Check'] = df_ia['Tipo de Atividade'].fillna('').astype(str).str.upper().str.strip()
    else:
        df_ia['Tipo_Ativ_Check'] = ''
        
    df_base = df_ia[df_ia['Tipo_Ativ_Check'] == "NA BASE"].copy()
    
    if not df_base.empty:
        df_travados = df_base[df_base['Classe_Analitica'] == "EM ABERTO"].copy()
        
        if not df_travados.empty:
            # Escala de criticidade temporal atrelada ao relógio operacional
            if hora_atual < 8:
                criticidade_ia = "⚠️ BAIXA (Aguardando início padrão do turno)"
                cor_alerta = "#e1f5fe"
            elif 8 <= hora_atual <= 9:
                criticidade_ia = "⚡ MÉDIA (Atraso operacional em andamento)"
                cor_alerta = "#fff3e0"
            else:
                criticidade_ia = "🚨 ALTA (Risco severo de perda ou quebra de rota completa)"
                cor_alerta = "#ffe6e6"
                
            st.markdown(f'<div style="background-color:{cor_alerta}; padding:12px; border-radius:6px; border-left:6px solid #ff9999; font-weight:bold; color:#111; margin-bottom:15px;">Nível de Urgência da IA: {criticidade_ia}</div>', unsafe_allow_html=True)
            
            df_lista_atrasados = df_travados.groupby(['Supervisor_Upper', 'Recurso_Upper']).size().reset_index()
            df_lista_atrasados = df_lista_atrasados.rename(columns={'Supervisor_Upper': 'Supervisor', 'Recurso_Upper': 'Técnico Desconectado'})
            df_lista_atrasados = df_lista_atrasados[['Supervisor', 'Técnico Desconectado']]
            
            st.dataframe(df_lista_atrasados, use_container_width=True, hide_index=True)
        else:
            st.success("✅ Motor de IA validou a largada: 100% dos técnicos ativaram o status 'Na Base' dentro do prazo.")
    else:
        st.info("Aguardando geração de dados do indicador 'Na Base' na planilha ativa.")

else:
    st.warning("⚠️ Aguardando carga estável da planilha para processamento da inteligência preditiva.")

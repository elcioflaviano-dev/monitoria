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

st.markdown('<h1 style="font-size: 34px; font-weight: 900; color: #005088; text-align: center; margin-top: 20px; margin-bottom: 5px;">🤖 PAINEL IA - INTELIGÊNCIA PREDITIVA</h1>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #666; font-size: 14px; margin-bottom: 20px;">Análise preditiva em tempo real usando modelos estatísticos locais (R$ 0,00)</div>', unsafe_allow_html=True)

# 🌟 HERANÇA INTELIGENTE: Substitui o download antigo pelos dados reais do Upload da Home
df_master = st.session_state.get('df_rota_ativa', None)

df_ia = None
if df_master is not None and not df_master.empty:
    df_ia = df_master.copy()
    
    # Faz o alinhamento das chaves operacionais e colunas esperadas pelo algoritmo preditivo original
    df_ia['STATUS_ATIVIDADE'] = df_ia['STATUS_ATIVIDADE'].fillna('PENDENTE') if 'STATUS_ATIVIDADE' in df_ia.columns else ('Status da Atividade' if 'Status da Atividade' in df_ia.columns else 'PENDENTE')
    df_ia['STATUS_OS1'] = df_ia['STATUS_OS1'].fillna('') if 'STATUS_OS1' in df_ia.columns else ''
    df_ia['Recurso'] = df_ia['Recurso'].fillna('N/A')
    
    # Tratamento dinâmico para a coluna 'Tipo O.S 1'
    col_tipo_os = 'Tipo O.S 1' if 'Tipo O.S 1' in df_ia.columns else ('Tipo de OS' if 'Tipo de OS' in df_ia.columns else None)
    if not col_tipo_os:
        for c in df_ia.columns:
            if 'OS' in str(c).upper() and 'STATUS' not in str(c).upper(): col_tipo_os = c; break
    df_ia['Tipo O.S 1'] = df_ia[col_tipo_os].fillna('N/A') if col_tipo_os else 'N/A'

# 🌟 CALIBRAGEM DO HORÁRIO (IGUAL AO TEC1 - FUSO BRASÍLIA BLINDADO)
hora_atual = (datetime.utcnow() - timedelta(hours=3)).hour
data_sinc = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

if df_ia is not None:
    st.markdown(f'<div style="text-align: center; color: #555; font-size: 13px; font-weight: bold; margin-bottom: 25px;">🔄 Motor de IA Sincronizado em tempo real via Upload: <span style="color: #005088;">{data_sinc}</span></div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div style="text-align: center; color: #cc6600; font-size: 13px; font-weight: bold; margin-bottom: 25px;">⚠️ Aguardando upload dos arquivos na página inicial</div>', unsafe_allow_html=True)

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
            st.markdown('<div class="custom-pendente-label" style="color: #555; font-size:12px; margin-top:5px;">💡 <b>Ação Recomendada:</b> Monitores devem focar suporte preventivo nos técnicos no topo da lista.</div>', unsafe_allow_html=True)
        else:
            st.success("🧠 IA analisou as rotas ativas: Nenhuma anomalia de alto risco detectada em campo.")
    else:
        st.info("Nenhum contrato ativo em campo para análise neste momento.")

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 🚨 MÓDULO IA 2: ALERTA PREDITIVO DE ABSENTEÍSMO
    # -------------------------------------------------------------------------
    st.markdown('### 🚨 MÓDULO 2: ALERTA PREDITIVO DE ABSENTEÍSMO (LARGADA MATINAL)')
    
    col_tipo_ativ = 'Tipo de Atividade' if 'Tipo de Atividade' in df_ia.columns else 'TIPO_ATIVIDADE_COL'
    if col_tipo_ativ in df_ia.columns:
        df_ia['Tipo_Ativ_Check'] = df_ia[col_tipo_ativ].fillna('').astype(str).str.upper().str.strip()
    else:
        df_ia['Tipo_Ativ_Check'] = ''
        
    df_base = df_ia[df_ia['Tipo_Ativ_Check'] == "NA BASE"].copy()
    
    if not df_base.empty:
        df_travados = df_base[df_base['Classe_Analitica'] == "EM ABERTO"].copy()
        
        if not df_travados.empty:
            # Escala de criticidade temporal atrelada ao relógio operacional real de Brasília
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
    st.warning("👈 Por favor, faça o upload dos arquivos de rota na página inicial (streamlit_app.py) primeiro para processar a inteligência preditiva.")

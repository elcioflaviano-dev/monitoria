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

st.markdown('<h1 style="font-size: 36px; font-weight: 900; color: #005088; text-align: center; margin-top: 20px; margin-bottom: 5px;">🤖 PAINEL IA - CENTRAL DE INTELIGÊNCIA OPERACIONAL</h1>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #666; font-size: 14px; margin-bottom: 25px;">Análise preditiva multidimensional e estatística local em tempo real (R$ 0,00)</div>', unsafe_allow_html=True)

# 🔄 HERANÇA INTELIGENTE DIRETA DA HOME
df_master = st.session_state.get('df_rota_ativa', None)

df_ia = None
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

    # Criação do DataFrame unificado e higienizado
    df_ia = pd.DataFrame({
        'Supervisor_Upper': lista_supervisor,
        'Recurso_Upper': lista_recurso,
        'Status_Atividade_Upper': lista_status_at,
        'Tipo_OS_Upper': lista_tipo_os,
        'STATUS_OS1': lista_status_os1,
        'Tipo_Ativ_Check': lista_tipo_ativ,
        'SUPERVISOR': lista_supervisor
    })

# 🌟 RELÓGIO DE BRASÍLIA OPERACIONAL
hora_atual = (datetime.utcnow() - timedelta(hours=3)).hour
data_sinc = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

if df_ia is not None:
    st.markdown(f'<div style="text-align: center; color: #555; font-size: 13px; font-weight: bold; margin-bottom: 25px;">🔄 Motor de IA Ativo: <span style="color: #005088;">{data_sinc}</span></div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div style="text-align: center; color: #cc6600; font-size: 13px; font-weight: bold; margin-bottom: 25px;">⚠️ Aguardando upload dos arquivos na página inicial</div>', unsafe_allow_html=True)

# Função auxiliar estatística de status
def inteligência_status_excel(baixa, status_at):
    baixa = str(baixa).upper().strip()
    status_at = str(status_at).upper().strip()
    codigos_ne = ["101", "106", "110", "112", "113", "125", "203", "205", "206", "301", "305", "306", "402", "100"]
    for cod in codigos_ne:
        if baixa.startswith(cod): return "O.S NE"
    if "PENDENTE" in baixa or "INICIADO" in baixa or "EM ROTA" in baixa or "PENDENTE" in status_at: return "EM ABERTO"
    return "PRODUTIVO"

# Função auxiliar para atribuir pontos com base no nome aproximado da O.S (Regras de Produtividade)
def calcular_pontos_os(nome_os):
    nome = str(nome_os).upper()
    if "INSTALACAO" in nome or "INSTALA" in nome: return 15
    if "REPARO" in nome or "MANUTEN" in nome: return 10
    if "MUDANCA" in nome or "ENDERECO" in nome: return 12
    if "RETIRADA" in nome or "RECOLHA" in nome: return 8
    return 5  # Valor padrão para demais nomenclaturas

if df_ia is not None and not df_ia.empty:
    
    # Filtro operacional mestre (Limpa cancelados/suspensos)
    df_ia = df_ia[(~df_ia['Supervisor_Upper'].isin(['#N/A', 'N/A', '', 'NAN'])) & (df_ia['Status_Atividade_Upper'] != "SUSPENSO")].copy()
    df_ia = df_ia[~df_ia['Recurso_Upper'].str.contains('TEC1|TEC 1', na=False)].copy()
    
    df_ia['Classe_Analitica'] = df_ia.apply(lambda r: inteligência_status_excel(r['STATUS_OS1'], r['Status_Atividade_Upper']), axis=1)

    # =========================================================================
    # 🔮 MÓDULO 1: PREVISOR DE RISCO DE QUEBRA
    # =========================================================================
    st.markdown('### 🔮 MÓDULO 1: PREVISOR DE RISCO DE QUEBRA (CONTRATOS EM CAMPO)')
    historico_quebra = df_ia.groupby(['Supervisor_Upper', 'Tipo_OS_Upper']).apply(
        lambda x: (x['Classe_Analitica'] == 'O.S NE').sum() / ((x['Classe_Analitica'] == 'PRODUTIVO').sum() + (x['Classe_Analitica'] == 'O.S NE').sum() + 0.001)
    ).reset_index(name='Fator_Risco')

    df_rua = df_ia[df_ia['Status_Atividade_Upper'].isin(['EM ROTA', 'INICIADO', 'PENDENTE']) & (df_ia['Tipo_OS_Upper'] != 'NA BASE')].copy()
    
    if not df_rua.empty:
        df_analisado = pd.merge(df_rua, historico_quebra, on=['Supervisor_Upper', 'Tipo_OS_Upper'], how='left')
        df_analisado['Fator_Risco'] = df_analisado['Fator_Risco'].fillna(0.15)
        df_analisado['Probabilidade_Quebra'] = df_analisado.apply(
            lambda r: min(95.0, round((r['Fator_Risco'] * 100) + (25 if r['Status_Atividade_Upper'] == 'PENDENTE' else 10), 2)), axis=1
        )
        df_risco = df_analisado[df_analisado['Probabilidade_Quebra'] >= 30.0].copy()
        
        if not df_risco.empty:
            df_vitrine_ia = df_risco.groupby(['Supervisor_Upper', 'Recurso_Upper', 'Tipo_OS_Upper', 'Status_Atividade_Upper'])['Probabilidade_Quebra'].max().reset_index()
            df_vitrine_ia = df_vitrine_ia.sort_values(by='Probabilidade_Quebra', ascending=False)
            df_vitrine_ia = df_vitrine_ia.rename(columns={
                'Supervisor_Upper': 'Supervisor', 'Recurso_Upper': 'Técnico em Campo', 
                'Tipo_OS_Upper': 'Descrição da O.S', 'Status_Atividade_Upper': 'Status Atual', 'Probabilidade_Quebra': 'Probabilidade de Quebra (%)'
            })
            st.dataframe(df_vitrine_ia, use_container_width=True, hide_index=True)
        else:
            st.success("🧠 IA analisou as rotas ativas: Nenhuma anomalia de alto risco detectada em campo.")
    else:
        st.info("Nenhum contrato ativo em campo para análise neste momento.")

    st.markdown("<hr>", unsafe_allow_html=True)

    # =========================================================================
    # 🚨 MÓDULO 2: ALERTA PREDITIVO DE ABSENTEÍSMO
    # =========================================================================
    st.markdown('### 🚨 MÓDULO 2: ALERTA PREDITIVO DE ABSENTEÍSMO (LARGADA MATINAL)')
    df_base = df_ia[df_ia['Tipo_Ativ_Check'] == "NA BASE"].copy()
    
    if not df_base.empty:
        df_travados = df_base[df_base['Classe_Analitica'] == "EM ABERTO"].copy()
        if not df_travados.empty:
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
            st.dataframe(df_lista_atrasados[['Supervisor', 'Técnico Desconectado']], use_container_width=True, hide_index=True)
        else:
            st.success("✅ Motor de IA validou a largada: 100% dos técnicos ativaram o status 'Na Base' dentro do prazo.")
    else:
        st.info("Aguardando geração de dados do indicador 'Na Base' na planilha ativa.")

    st.markdown("<hr>", unsafe_allow_html=True)

    # =========================================================================
    # 📊 MÓDULO 3: SIMULADOR DE PONTUAÇÃO DE PRODUTIVIDADE (NOVO!)
    # =========================================================================
    st.markdown('### 📊 MÓDULO 3: SIMULADOR PARCIAL DE PONTUAÇÃO (PRODUTIVIDADE)')
    
    # Filtra apenas o que de fato foi produtivo (executado com sucesso)
    df_produtivo = df_ia[df_ia['Classe_Analitica'] == 'PRODUTIVO'].copy()
    df_produtivo['Pontos_OS'] = df_produtivo['Tipo_OS_Upper'].apply(calcular_pontos_os)
    
    if not df_produtivo.empty:
        # Agrupamento por Técnico para gerar a somatória de pontos do dia
        df_ranking_tec = df_produtivo.groupby(['Supervisor_Upper', 'Recurso_Upper']).agg(
            OS_Concluidas=('Contrato', 'count'),
            Pontos_Acumulados=('Pontos_OS', 'sum')
        ).reset_index().sort_values(by='Pontos_Acumulados', ascending=False)
        
        df_ranking_tec = df_ranking_tec.rename(columns={
            'Supervisor_Upper': 'Supervisor', 'Recurso_Upper': 'Técnico',
            'OS_Concluidas': 'Qtd O.S Feitas', 'Pontos_Acumulados': 'Pontuação Conquistada'
        })
        
        c1, col_ranking = st.columns([1, 3])
        with c1:
            st.metric(label="🏆 Maior Pontuação Atual", value=f"{df_ranking_tec['Pontuação Conquistada'].max()} pts")
            st.metric(label="📈 Média da Equipe", value=f"{round(df_ranking_tec['Pontuação Conquistada'].mean(), 1)} pts")
        with col_ranking:
            st.dataframe(df_ranking_tec, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma O.S concluída na base para calcular pontuação até o momento.")

    st.markdown("<hr>", unsafe_allow_html=True)

    # =========================================================================
    # ⏳ MÓDULO 4: PREDITOR DE ESTOURO DE JORNADA / HORA EXTRA (NOVO!)
    # =========================================================================
    st.markdown('### ⏳ MÓDULO 4: ALERTA PREDITIVO DE ESTOURO DE JORNADA (HORA EXTRA)')
    
    # Filtra contratos pendentes ou iniciados em campo (desconsiderando largada matinal)
    df_pendentes_rua = df_ia[df_ia['Status_Atividade_Upper'].isin(['PENDENTE', 'INICIADO', 'EM ROTA']) & (df_ia['Tipo_OS_Upper'] != 'NA BASE')].copy()
    
    if not df_pendentes_rua.empty:
        df_vol_pendente = df_pendentes_rua.groupby(['Supervisor_Upper', 'Recurso_Upper']).size().reset_index(name='OS_Restantes')
        
        # Algoritmo de projeção baseado no horário limite (Gera risco severo se passar de 3 OS pendentes após as 15h)
        def calcular_risco_he(qtd_restante):
            if hora_atual < 13: return "BAIXO"
            if 13 <= hora_atual < 16:
                return "MÉDIO" if qtd_restante <= 2 else "ALTO"
            return "CRÍTICO" if qtd_restante > 1 else "MÉDIO"
            
        df_vol_pendente['Risco_Hora_Extra'] = df_vol_pendente['OS_Restantes'].apply(calcular_risco_he)
        df_vol_pendente = df_vol_pendente.sort_values(by='OS_Restantes', ascending=False)
        
        df_vol_pendente = df_vol_pendente.rename(columns={
            'Supervisor_Upper': 'Supervisor', 'Recurso_Upper': 'Técnico em Campo', 'OS_Restantes': 'Contratos Pendentes na Rota'
        })
        
        # Destaca apenas quem tem risco real de estourar o horário padrão
        st.dataframe(df_vol_pendente, use_container_width=True, hide_index=True)
    else:
        st.success("✅ Sem riscos de hora extra: Todos os técnicos estão com a rota de campo limpa!")

    st.markdown("<hr>", unsafe_allow_html=True)

    # =========================================================================
    # 📉 MÓDULO 5: TERMÔMETRO DE CONVERSÃO OPERACIONAL (NOVO!)
    # =========================================================================
    st.markdown('### 📉 MÓDULO 5: TERMÔMETRO DE CONVERSÃO REGIONAL (ABC vs SP)')
    
    # Separação Regional nativa baseada na regra Francisco/Alan para SP
    df_ia['Regiao'] = df_ia['Supervisor_Upper'].apply(lambda s: 'SÃO PAULO (SP)' if 'FRANCISCO' in str(s) or 'ALAN' in str(s) else 'ABC')
    
    df_conversao = df_ia[df_ia['Tipo_OS_Upper'] != 'NA BASE'].copy()
    
    if not df_conversao.empty:
        df_grafico = df_conversao.groupby(['Regiao', 'Classe_Analitica']).size().unstack(fill_value=0).reset_index()
        
        # Adiciona colunas se não existirem para evitar KeyError
        for col in ['PRODUTIVO', 'O.S NE', 'EM ABERTO']:
            if col not in df_grafico.columns: df_grafico[col] = 0
            
        df_grafico['Total_Carteira'] = df_grafico['PRODUTIVO'] + df_grafico['O.S NE'] + df_grafico['EM ABERTO']
        df_grafico['Eficiência de Conversão (%)'] = round((df_grafico['PRODUTIVO'] / (df_grafico['PRODUTIVO'] + df_grafico['O.S NE'] + 0.001)) * 100, 1)
        
        df_grafico = df_grafico.rename(columns={
            'Regiao': 'Região Operacional', 'PRODUTIVO': 'Sucesso (Produtivo)', 'O.S NE': 'Quebras (Instabilidades)', 'EM ABERTO': 'Ainda em Campo'
        })
        
        st.dataframe(df_grafico[['Região Operacional', 'Sucesso (Produtivo)', 'Quebras (Instabilidades)', 'Ainda em Campo', 'Total_Carteira', 'Eficiência de Conversão (%)']], use_container_width=True, hide_index=True)
    else:
        st.info("Aguardando dados de volumetria de campo para consolidar o termômetro regional.")

st.markdown("---")

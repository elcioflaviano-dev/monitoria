import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta

# 1. Configuração da página ampla para a TV
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

# --- CONTROLE INTERNO DE ROTAÇÃO NATIVA ---
# Define a lista de painéis que vão rodar na TV
PAINEIS = ["LARGADA_MATINAL", "TEC1_PENDENTES", "PRIMEIRO_ATENDIMENTO"]

if "indice_painel" not in st.session_state:
    st.session_state["indice_painel"] = 0

if "ultimo_giro" not in st.session_state:
    st.session_state["ultimo_giro"] = time.time()

# Motor do tempo: Altera o painel a cada 30 segundos
TEMPO_ROTACAO_SEGUNDOS = 30
tempo_passado = time.time() - st.session_state["ultimo_giro"]

# Injeta uma entrada oculta apenas para forçar o Streamlit a escutar o timer de refresh
st.text_input("timer_trigger", value=str(st.session_state["ultimo_giro"]), label_visibility="collapsed")

if tempo_passado >= TEMPO_ROTACAO_SEGUNDOS:
    st.session_state["indice_painel"] = (st.session_state["indice_painel"] + 1) % len(PAINEIS)
    st.session_state["ultimo_giro"] = time.time()
    st.rerun()

# Define qual painel está ativo nesta rodada
painel_atual = PAINEIS[st.session_state["indice_painel"]]

# 🔄 HERANÇA INTELIGENTE VIA DISCO RÍGIDO (À PROVA DE QUEDAS DE SESSÃO)
df_master = None
if os.path.exists(ARQUIVO_ROTA_DISCO):
    try:
        df_master = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    except:
        pass

# Injeta o CSS base para Modo TV
st.markdown("""
    <style>
        .block-container { padding-top: 10px !important; padding-bottom: 5px !important; }
        .stDeployButton { display:none; }
        .barra-status-tv {
            background-color: #111;
            color: #fff;
            padding: 5px 15px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
        }
        /* Estilos do Bloco de Pendentes */
        .title-abc-sp { font-size: 24px !important; font-weight: 800 !important; margin-bottom: 10px !important; text-align: center; color: #005088; }
        .super-bar {
            background-color: #f0f2f6; padding: 6px 12px; border-radius: 4px; font-size: 16px;
            font-weight: bold; color: #333; margin-top: 12px; margin-bottom: 6px;
            display: flex; justify-content: space-between; align-items: center; border-left: 5px solid #cc6600;
        }
        .super-total { background-color: #ffebee; color: #c62828; padding: 2px 10px; border-radius: 4px; font-size: 13px; font-weight: 900; }
        .item-linha { font-size: 16px; padding: 5px 12px; border-bottom: 1px solid #eee; color: #222; }
        .item-contrato { font-weight: 900; color: #cc6600; font-size: 17px; }
        .divisor-item { color: #bbb; margin: 0 8px; }
        
        /* Estilos do Primeiro Atendimento */
        .kpi-container { display: flex; justify-content: center; gap: 25px; margin-bottom: 20px; }
        .kpi-card { background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); padding: 10px 25px; text-align: center; min-width: 240px; border-top: 5px solid #006677; }
        .kpi-card.abc { border-top-color: #008080; }
        .kpi-card.sp { border-top-color: #b30000; }
        .kpi-title { font-size: 13px; color: #666; font-weight: bold; text-transform: uppercase; }
        .kpi-value { font-size: 26px; color: #111; font-weight: 900; }
    </style>
""", unsafe_allow_html=True)

# Barra superior de monitoramento da TV
tempo_restante = int(TEMPO_ROTACAO_SEGUNDOS - tempo_passado)
st.markdown(f'''
    <div class="barra-status-tv">
        <span>📺 MODO TV ATIVO • EXIBINDO: {painel_atual.replace("_", " ")}</span>
        <span>⏱️ Próxima tela em: {tempo_restante}s</span>
    </div>
''', unsafe_allow_html=True)

# Funções auxiliares para tratamento de dados do 1º Atendimento
def tratar_horario(val):
    if pd.isna(val) or str(val).strip() in ['', 'N/A', 'NAN', 'NaN', '00:00']: return None
    try:
        texto = str(val).strip().split()[-1]
        return datetime.strptime(texto, '%H:%M:%S').time()
    except:
        try:
            texto = str(val).strip().split()[-1]
            return datetime.strptime(texto, '%H:%M').time()
        except: return None

def calcular_media_horarios(lista_horas):
    if not lista_horas: return "--:--"
    total_segundos = 0; qtd = 0
    for h in lista_horas:
        if h is not None:
            total_segundos += h.hour * 3600 + h.minute * 60 + h.second
            qtd += 1
    if qtd == 0: return "--:--"
    media_segundos = total_segundos / qtd
    media_time = str(timedelta(seconds=int(media_segundos)))
    return ":".join(media_time.split(":")[:2])

def destacar_linha_total(row):
    try:
        if "TOTAL" in str(row.iloc[0]).upper():
            return ['background-color: #eae5da; font-weight: bold; color: #111111; border-top: 1px solid #b5b5b5;'] * len(row)
    except: pass
    return [''] * len(row)


# =============================================================================
# 🟢 VISUAL 1: LARGADA MATINAL ("NA BASE")
# =============================================================================
if painel_atual == "LARGADA_MATINAL":
    st.markdown('<h1 style="font-size: 30px; font-weight: 900; color: #006677; text-align: center; margin-bottom: 15px;">🚀 LARGADA MATINAL - STATUS NA BASE</h1>', unsafe_allow_html=True)
    
    if df_master is not None and not df_master.empty:
        df_temp = df_master.copy()
        col_tipo = 'Tipo de Atividade' if 'Tipo de Atividade' in df_temp.columns else 'TIPO_ATIVIDADE_COL'
        col_status = 'STATUS_ATIVIDADE' if 'STATUS_ATIVIDADE' in df_temp.columns else 'Status da Atividade'
        
        for c in df_temp.columns:
            if 'TIPO DE A' in str(c).upper() or 'TIPO ATIV' in str(c).upper(): col_tipo = c; break
        for c in df_temp.columns:
            if 'STATUS DA' in str(c).upper() or 'STATUS_AT' in str(c).upper(): col_status = c; break
            
        df_temp['Tipo_Atividade_Upper'] = df_temp[col_tipo].fillna('').astype(str).str.upper().str.strip() if col_tipo in df_temp.columns else ''
        df_temp['Status_Conclusao_Upper'] = df_temp[col_status].fillna('').astype(str).str.upper().str.strip() if col_status in df_temp.columns else ''
        df_temp['Supervisor_Tratado'] = df_temp['SUPERVISOR'].fillna('').astype(str).str.upper().str.strip() if 'SUPERVISOR' in df_temp.columns else 'PENDENTE'
        df_temp['Login_Tratado'] = df_temp['Login'].fillna('').astype(str).str.strip() if 'Login' in df_temp.columns else '-'
        df_temp['Recurso_Tratado'] = df_temp['Recurso'].fillna('TÉCNICO').astype(str).str.strip() if 'Recurso' in df_temp.columns else 'TÉCNICO'

        df_base_linhas = df_temp[df_temp['Tipo_Atividade_Upper'].str.contains("BASE", na=False)].copy()
        df_pendentes_reais = df_base_linhas[df_base_linhas['Status_Conclusao_Upper'].str.contains("PEND", na=False)].copy()
        
        if not df_pendentes_reais.empty:
            df_lista = df_pendentes_reais.groupby(['Supervisor_Tratado', 'Login_Tratado', 'Recurso_Tratado']).size().reset_index()
            df_lista = df_lista.rename(columns={'Supervisor_Tratado': 'Supervisor', 'Login_Tratado': 'Login', 'Recurso_Tratado': 'Técnico Pendente'})
            df_lista = df_lista[(df_lista['Técnico Pendente'] != 'N/A') & (df_lista['Técnico Pendente'].str.upper() != 'NAN')]
        else:
            df_lista = pd.DataFrame(columns=['Supervisor', 'Login', 'Técnico Pendente'])

        df_sp = df_lista[df_lista['Supervisor'].str.contains("FRANCISCO|ALAN", na=False)].copy()
        df_abc = df_lista[~df_lista['Supervisor'].str.contains("FRANCISCO|ALAN", na=False)].copy()

        c_abc, c_sp = st.columns(2)
        with c_abc:
            st.markdown('<div style="background-color:#008080; padding:5px; border-radius:4px;"><h3 style="color:white; margin:0; font-size:16px; text-align:center;">📍 ABC - PENDENTES</h3></div>', unsafe_allow_html=True)
            if not df_abc.empty:
                st.dataframe(df_abc[['Supervisor', 'Login', 'Técnico Pendente']], use_container_width=True, hide_index=True)
                df_tot_abc = pd.DataFrame([{"Supervisor": "TOTAL PENDENTE", "Login": "-", "Técnico Pendente": f"{df_abc['Técnico Pendente'].nunique()} Técnicos"}])
                st.dataframe(df_tot_abc.style.apply(destacar_linha_total, axis=1), use_container_width=True, hide_index=True)
            else: st.success("✅ 100% da equipe ABC liberada!")
            
        with c_sp:
            st.markdown('<div style="background-color:#b30000; padding:5px; border-radius:4px;"><h3 style="color:white; margin:0; font-size:16px; text-align:center;">📍 SÃO PAULO - PENDENTES</h3></div>', unsafe_allow_html=True)
            if not df_sp.empty:
                st.dataframe(df_sp[['Supervisor', 'Login', 'Técnico Pendente']], use_container_width=True, hide_index=True)
                df_tot_sp = pd.DataFrame([{"Supervisor": "TOTAL PENDENTE", "Login": "-", "Técnico Pendente": f"{df_sp['Técnico Pendente'].nunique()} Técnicos"}])
                st.dataframe(df_tot_sp.style.apply(destacar_linha_total, axis=1), use_container_width=True, hide_index=True)
            else: st.success("✅ 100% da equipe SP liberada!")
    else:
        st.warning("👈 Aguardando os arquivos na página inicial.")


# =============================================================================
# 🟢 VISUAL 2: TEC1 PENDENTES (FILA DINÂMICA)
# =============================================================================
elif painel_atual == "TEC1_PENDENTES":
    st.markdown('<h1 style="font-size: 30px; font-weight: 900; color: #cc6600; text-align: center; margin-bottom: 15px;">⏳ TEC1 PENDENTES OPERACIONAIS</h1>', unsafe_allow_html=True)
    
    if df_master is not None and not df_master.empty:
        df = df_master.copy()
        col_tecnico_check = 'Login do Técnico' if 'Login do Técnico' in df.columns else None
        for c in df.columns:
            if 'TECNICO' in str(c).upper() or 'LOGIN' in str(c).upper(): col_tecnico_check = c; break
                
        if col_tecnico_check: df = df[df[col_tecnico_check].fillna('').astype(str).str.strip() != ''].copy()
        if 'Contrato' in df.columns:
            df['Contrato'] = df['Contrato'].fillna('').astype(str).apply(lambda x: x.split('.')[0] if '.' in x else x).str.strip()
            df = df[df['Contrato'] != ''].copy()

        df['Status_Atividade_Upper'] = df['STATUS_ATIVIDADE'].fillna('').astype(str).str.upper().str.strip() if 'STATUS_ATIVIDADE' in df.columns else ''
        df_limpo = df[df['Status_Atividade_Upper'] != 'SUSPENSO'].copy()
        if 'Tipo de Atividade' in df_limpo.columns:
            df_limpo['Tipo_Activity_Str'] = df_limpo['Tipo de Atividade'].fillna('').astype(str)
            df_limpo = df_limpo[~df_limpo['Tipo_Activity_Str'].str.contains('Refeicao', case=False, na=False)]

        df_limpo['P_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('PENDENTE|EM ABERTO|ABERTO', na=False).astype(int)
        df_validos = df_limpo[df_limpo['P_COUNT'] > 0].copy()
            
        col_janela = 'Janela de Serviço' if 'Janela de Serviço' in df_validos.columns else None
        for c in df_validos.columns:
            if 'JANELA' in str(c).upper() or 'INTERVALO' in str(c).upper(): col_janela = c; break
                
        if col_janela is not None and not df_validos.empty:
            df_validos['Intervalo_Tratado'] = df_validos[col_janela].fillna('').astype(str).str.strip()
            hora_atual = (datetime.utcnow() - timedelta(hours=3)).hour
            def extrair_hora_limite(janela_str):
                try:
                    partes = janela_str.replace(':', '').split('-')
                    return int(partes[1].strip()[:2]) if len(partes) == 2 else 24
                except: return 24
            df_validos['Hora_Limite_Janela'] = df_validos['Intervalo_Tratado'].apply(extrair_hora_limite)
            df_tela = df_validos[df_validos['Hora_Limite_Janela'] <= (hora_atual + 1)].copy()
            if df_tela.empty: df_tela = df_validos.copy()
        else:
            df_tela = df_validos.copy()

        if not df_tela.empty:
            col_rec = 'Recurso' if 'Recurso' in df_tela.columns else None
            for c in df_tela.columns:
                if 'TECNICO' in str(c).upper() or 'LOGIN' in str(c).upper(): col_rec = c; break
            df_tela['Recurso_Tratado'] = df_tela[col_rec].fillna('TÉCNICO').astype(str).str.upper() if col_rec else 'TÉCNICO'

            if 'SUPERVISOR' in df_tela.columns:
                df_tela['SUPERVISOR_MOSTRAR'] = df_tela.apply(lambda r: str(r['Recurso_Tratado']).upper() if str(r['SUPERVISOR']).strip().upper() in ['#N/A', 'NAN', '', 'PENDENTE CADASTRO'] else str(r['SUPERVISOR']).upper(), axis=1)
            else: df_tela['SUPERVISOR_MOSTRAR'] = df_tela['Recurso_Tratado']
            df_tela['SUPERVISOR_MOSTRAR'] = df_tela['SUPERVISOR_MOSTRAR'].astype(str).str.upper().str.strip()

            cond_sp = (df_tela['REGIAO_BASE'].fillna('').astype(str).str.upper().str.contains('SÃO PAULO|SP', na=False) | df_tela['SUPERVISOR_MOSTRAR'].str.contains('FRANCISCO|ALAN', na=False))
            df_sp = df_tela[cond_sp].copy()
            df_abc = df_tela[~cond_sp].copy()

            col_coluna_abc, col_coluna_sp = st.columns(2)
            with col_coluna_abc:
                st.markdown('<div class="title-abc-sp">ABC</div>', unsafe_allow_html=True)
                if not df_abc.empty:
                    for supervisor in sorted(df_abc['SUPERVISOR_MOSTRAR'].unique()):
                        df_super = df_abc[df_abc['SUPERVISOR_MOSTRAR'] == supervisor]
                        st.markdown(f'<div class="super-bar">👤 {supervisor} <span class="super-total">Pendentes: {df_super["P_COUNT"].sum()}</span></div>', unsafe_allow_html=True)
                        for idx, linha in df_super.iterrows():
                            st.markdown(f'<div class="item-linha">📄 <span class="item-contrato">{linha.get("Contrato", "N/A")}</span> <span class="divisor-item">|</span> 👤 {linha.get("Recurso_Tratado", "N/A")}</div>', unsafe_allow_html=True)
                else: st.info("Nenhum pendente no ABC.")

            with col_coluna_sp:
                st.markdown('<div class="title-abc-sp">SÃO PAULO (SP)</div>', unsafe_allow_html=True)
                if not df_sp.empty:
                    for supervisor in sorted(df_sp['SUPERVISOR_MOSTRAR'].unique()):
                        df_super = df_sp[df_sp['SUPERVISOR_MOSTRAR'] == supervisor]
                        st.markdown(f'<div class="super-bar">👤 {supervisor} <span class="super-total">Pendentes: {df_super["P_COUNT"].sum()}</span></div>', unsafe_allow_html=True)
                        for idx, linha in df_super.iterrows():
                            st.markdown(f'<div class="item-linha">📄 <span class="item-contrato">{linha.get("Contrato", "N/A")}</span> <span class="divisor-item">|</span> 👤 {linha.get("Recurso_Tratado", "N/A")}</div>', unsafe_allow_html=True)
                else: st.info("Nenhum pendente em SP.")
        else: st.success("🎉 Nenhum contrato pendente na janela ativa!")
    else: st.warning("👈 Aguardando os arquivos na página inicial.")


# =============================================================================
# 🟢 VISUAL 3: 1º ATENDIMENTO OPERACIONAL (MÉDIAS)
# =============================================================================
elif painel_atual == "PRIMEIRO_ATENDIMENTO":
    st.markdown('<h1 style="font-size: 30px; font-weight: 900; color: #006677; text-align: center; margin-bottom: 15px;">⏱️ MÉDIA DO 1º ATENDIMENTO</h1>', unsafe_allow_html=True)
    
    if df_master is not None and not df_master.empty:
        df_temp = df_master.copy()
        col_recurso = 'Recurso' if 'Recurso' in df_temp.columns else df_temp.columns[0]
        col_supervisor = 'SUPERVISOR'; col_status_os = 'Status'; col_inicio_estrito = 'Início'
        
        for c in df_temp.columns:
            g_up = str(c).upper().strip().split('.')[0]
            if g_up in ['INÍCIO', 'INICIO'] and '-' not in str(c) and 'DO' not in str(c).upper(): col_inicio_estrito = c
            elif g_up == 'STATUS': col_status_os = c
            elif 'SUPERV' in g_up: col_supervisor = c

        df_base = pd.DataFrame({
            'Recurso': [str(x).strip() for x in df_temp[col_recurso].fillna('N/A').tolist()] if col_recurso in df_temp.columns else ['N/A']*len(df_temp),
            'SUPERVISOR_ORIGINAL': [str(x).upper().strip() for x in df_temp[col_supervisor].fillna('').tolist()] if col_supervisor in df_temp.columns else ['']*len(df_temp),
            'Status_OS': [str(x).lower().strip() for x in df_temp[col_status_os].fillna('').tolist()] if col_status_os in df_temp.columns else ['']*len(df_temp),
            'Hora_Inicio': [tratar_horario(x) for x in df_temp[col_inicio_estrito].tolist()] if col_inicio_estrito in df_temp.columns else [None]*len(df_temp)
        })
        
        df_sup_mapeado = df_base[(df_base['SUPERVISOR_ORIGINAL'] != '') & (~df_base['SUPERVISOR_ORIGINAL'].isin(['N/A', 'NAN', '#N/A']))].groupby('Recurso')['SUPERVISOR_ORIGINAL'].first().reset_index(name='SUPERVISOR_VALIDO')
        df_base = pd.merge(df_base, df_sup_mapeado, on='Recurso', how='left')
        df_base['Supervisor'] = df_base['SUPERVISOR_VALIDO'].fillna(df_base['SUPERVISOR_ORIGINAL']).str.upper().str.strip()

        df_filtrado_excel = df_base[(df_base['Status_OS'].str.contains('concl|inic|susp', na=False)) & (df_base['Hora_Inicio'].notna())].copy()
        
        if not df_filtrado_excel.empty:
            df_primeiro = df_filtrado_excel.sort_values('Hora_Inicio').groupby('Recurso').first().reset_index()
            df_primeiro['Horário'] = df_primeiro['Hora_Inicio'].apply(lambda x: x.strftime('%H:%M') if x else '--:--')
            df_exibicao = df_primeiro[['Supervisor', 'Recurso', 'Horário', 'Hora_Inicio']].rename(columns={'Recurso': 'Técnico'})
            df_exibicao = df_exibicao[(df_exibicao['Técnico'] != 'N/A') & (df_exibicao['Técnico'] != '')]
            
            df_sp = df_exibicao[df_exibicao['Supervisor'].fillna('').str.contains("FRANCISCO|ALAN", na=False)].copy()
            df_abc = df_exibicao[~df_exibicao['Supervisor'].fillna('').str.contains("FRANCISCO|ALAN", na=False)].copy()

            media_abc = calcular_media_horarios(df_primeiro[df_primeiro['Recurso'].isin(df_abc['Técnico'])]['Hora_Inicio'].tolist())
            media_sp = calcular_media_horarios(df_primeiro[df_primeiro['Recurso'].isin(df_sp['Técnico'])]['Hora_Inicio'].tolist())

            st.markdown(f'''
                <div class="kpi-container">
                    <div class="kpi-card abc"><div class="kpi-title">⏱️ Média 1º Contrato - ABC</div><div class="kpi-value">{media_abc}</div></div>
                    <div class="kpi-card sp"><div class="kpi-title">⏱️ Média 1º Contrato - SÃO PAULO</div><div class="kpi-value">{media_sp}</div></div>
                </div>
            ''', unsafe_allow_html=True)

            c_detalhe_abc, c_detalhe_sp = st.columns(2)
            with c_detalhe_abc:
                st.markdown('<div style="background-color:#008080; padding:4px 10px; border-radius:4px; margin-bottom:10px;"><h4 style="color:white; margin:0; font-size:14px;">📍 VISÃO SUPERVISORES - ABC</h4></div>', unsafe_allow_html=True)
                if not df_abc.empty:
                    for sup in sorted(df_abc['Supervisor'].unique().tolist()):
                        df_sup_abc = df_abc[df_abc['Supervisor'] == sup]
                        m_sup = calcular_media_horarios(df_sup_abc['Hora_Inicio'].tolist())
                        st.markdown(f'<div style="font-size:13px; font-weight:bold; color:#004d40; background:#f1f7f6; padding:4px 8px; border-radius:4px; display:flex; justify-content:space-between; margin-bottom:4px;"><span>👤 {sup}</span><span>⏱️ {m_sup} ({len(df_sup_abc)} Tecs)</span></div>', unsafe_allow_html=True)
                else: st.info("Sem dados para o ABC.")
                
            with c_detalhe_sp:
                st.markdown('<div style="background-color:#b30000; padding:4px 10px; border-radius:4px; margin-bottom:10px;"><h4 style="color:white; margin:0; font-size:14px;">📍 VISÃO SUPERVISORES - SP</h4></div>', unsafe_allow_html=True)
                if not df_sp.empty:
                    for sup in sorted(df_sp['Supervisor'].unique().tolist()):
                        df_sup_sp = df_sp[df_sp['Supervisor'] == sup]
                        m_sup = calcular_media_horarios(df_sup_sp['Hora_Inicio'].tolist())
                        st.markdown(f'<div style="font-size:13px; font-weight:bold; color:#660000; background:#fff2f2; padding:4px 8px; border-radius:4px; display:flex; justify-content:space-between; margin-bottom:4px;"><span>👤 {sup}</span><span>⏱️ {m_sup} ({len(df_sup_sp)} Tecs)</span></div>', unsafe_allow_html=True)
                else: st.info("Sem dados para SP.")
        else: st.info("Nenhum atendimento realizado até o momento.")
    else: st.warning("👈 Aguardando os arquivos na página inicial.")

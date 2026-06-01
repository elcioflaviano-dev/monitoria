import streamlit as st

import pandas as pd

import os

import time

from datetime import datetime, timedelta



# 1. Configuração da página ampla para a TV

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")



ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

TEMPO_ROTACAO_SEGUNDOS = 15  # Tempo exato para girar de tela



# 🔄 HERANÇA INTELIGENTE VIA DISCO RÍGIDO

df_master = None

if os.path.exists(ARQUIVO_ROTA_DISCO):

    try:

        df_master = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)

    except:

        pass



# 🔥 CONTROLADOR DE SESSÃO E SUB-PÁGINAS (CENÁRIO VS CONTRATOS) 🔥

if "last_rotacao_tv" not in st.session_state:

    st.session_state["last_rotacao_tv"] = time.time()



if "index_supervisor_tv" not in st.session_state:

    st.session_state["index_supervisor_tv"] = 0



if "sub_painel_tv" not in st.session_state:

    st.session_state["sub_painel_tv"] = "CENARIO"  # Inicializa na tela macro



if "chave_fala_gatilho" not in st.session_state:

    st.session_state["chave_fala_gatilho"] = ""



SUPERVISORES_CICLO = ["MAICON", "NELSON", "MARCOS ROBERTO", "ALAN", "FRANCISCO GERALDO CARVALHO JUNIOR"]



# ⏱️ RELÓGIO DE ALTERNAÇÃO DE SUB-PÁGINAS

tempo_decorrido = time.time() - st.session_state["last_rotacao_tv"]



if tempo_decorrido >= TEMPO_ROTACAO_SEGUNDOS:

    if st.session_state["sub_painel_tv"] == "CENARIO":

        st.session_state["sub_painel_tv"] = "CONTRATOS"  # Muda para a lista

    else:

        st.session_state["sub_painel_tv"] = "CENARIO"  # Volta para o macro do próximo

        st.session_state["index_supervisor_tv"] = (st.session_state["index_supervisor_tv"] + 1) % len(SUPERVISORES_CICLO)

        

    st.session_state["last_rotacao_tv"] = time.time()

    st.rerun()



supervisor_atual = SUPERVISORES_CICLO[st.session_state["index_supervisor_tv"]]

sub_tela_atual = st.session_state["sub_painel_tv"]



# Nome simplificado apenas para exibição no título da barra

supervisor_titulo = "FRANCISCO" if "FRANCISCO" in supervisor_atual else supervisor_atual



# 🔥 INJEÇÃO DE CSS AGRESSIVA (SOME COM O MENU LATERAL DE VEZ)

st.markdown("""

    <style>

        section[data-testid="stSidebar"], 

        [data-testid="stSidebar"], 

        div[data-testid="stSidebarCollapseButton"],

        button[data-testid="stSidebarCollapseButton"] {

            display: none !important;

            visibility: hidden !important;

            width: 0px !important;

            transform: translateX(-100%) !important;

        }

        section.main, .stAppDeployButton {

            margin-left: 0px !important;

            padding-left: 0px !important;

        }

        .block-container { padding-top: 65px !important; padding-bottom: 5px !important; }

        .stDeployButton { display:none; }

        

        .barra-status-tv {

            position: fixed; top: 0; left: 0; right: 0; z-index: 999995;

            background-color: #111; color: #fff; padding: 10px 20px;

            font-size: 13px; font-weight: bold; display: flex; justify-content: space-between; align-items: center;

            font-family: sans-serif; box-shadow: 0 2px 5px rgba(0,0,0,0.3);

        }

        .btn-voltar-home {

            background-color: #cc6600; color: white !important; padding: 5px 12px;

            border-radius: 4px; text-decoration: none !important; font-size: 12px; font-weight: bold;

        }

        .title-supervisor-tv { font-size: 42px !important; font-weight: 900 !important; color: #005088; text-align: center; margin-bottom: 25px; text-transform: uppercase; }

        .item-linha-tv { font-size: 21px; padding: 10px 15px; border-bottom: 1px solid #eee; color: #111; }

        .item-contrato-tv { font-weight: 900; color: #cc6600; font-size: 22px; }

        .divisor-item-tv { color: #bbb; margin: 0 10px; }

        

        .custom-pendente-box { background-color: #ffcccc !important; border: 2px solid #ff9999 !important; border-radius: 6px; padding: 25px !important; text-align: center; }

        .custom-pendente-label { font-size: 15px !important; font-weight: 800 !important; text-transform: uppercase; color: #800000 !important; margin-bottom: 6px; }

        .custom-pendente-value { font-size: 64px !important; color: #b30000 !important; font-weight: 900 !important; line-height: 1.1; }

        

        .card-meta-tv { background-color: #f8f9fa; border-radius: 6px; padding: 25px; text-align: center; border-top: 5px solid #6c757d; }

        .card-meta-label { font-size: 15px; font-weight: bold; color: #555; text-transform: uppercase; margin-bottom: 6px; }

        .card-meta-value { font-size: 64px; font-weight: 900; color: #212529; line-height: 1.1; }

        .card-meta-tv.rota { border-top-color: #0288d1; }

        .card-meta-tv.rota .card-meta-value { color: #0288d1; }

        .card-meta-tv.iniciado { border-top-color: #2e7d32; }

        .card-meta-tv.iniciado .card-meta-value { color: #2e7d32; }

    </style>

""", unsafe_allow_html=True)



# Barra fixa superior dinâmica com indicador de sub-página

st.markdown(f'''

    <div class="barra-status-tv">

        <div>

            <a href="/" target="_self" class="btn-voltar-home">🏠 VOLTAR PARA A HOME</a>

            <span style="margin-left: 15px;">📺 TV MODE • EQUIPE: <b style="color: #ff9800;">{supervisor_titulo}</b> • TELA: <b style="color: #008080;">{sub_tela_atual}</b></span>

        </div>

        <span>🔄 Próxima transição em {int(max(0, TEMPO_ROTACAO_SEGUNDOS - tempo_decorrido))}s</span>

    </div>

''', unsafe_allow_html=True)



# =============================================================================

# PROCESSAMENTO DOS DADOS COM FILA CUMULATIVA

# =============================================================================

if df_master is not None and not df_master.empty:

    df = df_master.copy()

    df.columns = [str(c).strip() for c in df.columns]

    

    col_tecnico_check = 'Recurso' if 'Recurso' in df.columns else df.columns[0]

    col_status_real = 'Status da Atividade' if 'Status da Atividade' in df.columns else 'STATUS_ATIVIDADE'

    col_tipo_real = 'Tipo de Atividade' if 'Tipo de Atividade' in df.columns else df.columns[-1]

    col_supervisor = 'SUPERVISOR' if 'SUPERVISOR' in df.columns else 'Supervisor'

            

    df = df[df[col_tecnico_check].fillna('').astype(str).str.strip() != ''].copy()

    

    if 'Contrato' in df.columns:

        df['Contrato'] = df['Contrato'].fillna('').astype(str).apply(lambda x: x.split('.')[0] if '.' in x else x).str.strip()

        df = df[df['Contrato'] != ''].copy()



    df['Status_Atividade_Upper'] = df[col_status_real].fillna('').astype(str).str.upper().str.strip()

    df_limpo = df[df['Status_Atividade_Upper'] != 'SUSPENSO'].copy()

    

    df_limpo['Tipo_Activity_Str'] = df_limpo[col_tipo_real].fillna('').astype(str)

    df_limpo = df_limpo[~df_limpo['Tipo_Activity_Str'].str.contains('Refeicao', case=False, na=False)]



    df_limpo['P_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('PENDENTE|EM ABERTO|ABERTO|PEND', na=False).astype(int)

    df_limpo['R_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('ROTA|DESLOC|DESLOCAMENTO', na=False).astype(int)

    df_limpo['I_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('INICIADO|PRODUTIVO|EXECUCAO|INIC', na=False).astype(int)



    df_validos = df_limpo[(df_limpo['P_COUNT'] > 0) | (df_limpo['R_COUNT'] > 0) | (df_limpo['I_COUNT'] > 0)].copy()



    # === MOTOR DE JANELAS ACUMULATIVO ===

    col_janela = None

    for c in df_validos.columns:

        if 'JANELA' in str(c).upper() or 'INTERVALO' in str(c).upper(): col_janela = c; break



    hora_atual = (datetime.utcnow() - timedelta(hours=3)).hour



    texto_audio_janela = "geral"

    if col_janela is not None and not df_validos.empty:

        df_validos['Intervalo_Tratado'] = df_validos[col_janela].fillna('').astype(str).str.strip()

        def extrair_hora_limite(janela_str):

            try:

                partes = janela_str.replace(':', '').split('-')

                return int(partes[1].strip()[:2]) if len(partes) == 2 else 24

            except: return 24

        df_validos['Hora_Limite_Janela'] = df_validos['Intervalo_Tratado'].apply(extrair_hora_limite)

        

        if hora_atual < 12:

            condicao_horario = (df_validos['Hora_Limite_Janela'] <= 12)

            texto_status_janela = "Fila da Manhã (Até 12:00)"

            texto_audio_janela = "Até doze horas"

        elif 12 <= hora_atual < 15:

            condicao_horario = (df_validos['Hora_Limite_Janela'] <= 15)

            texto_status_janela = "Fila da Tarde (Acumulado até 15:00)"

            texto_audio_janela = "Acumulado até quinze horas"

        else:

            condicao_horario = (df_validos['Hora_Limite_Janela'] <= 24)

            texto_status_janela = "Visão Completa Turno (Acumulado)"

            texto_audio_janela = "Fechamento de turno"



        df_tela = df_validos[condicao_horario | (df_validos['R_COUNT'] > 0) | (df_validos['I_COUNT'] > 0)].copy()

        if df_tela.empty: df_tela = df_validos.copy()

            

        st.markdown(f'<div style="text-align: center; color: #008080; font-size: 14px; font-weight: bold; margin-bottom: 10px; margin-top: -15px;">🔄 Fila Cumulativa: {texto_status_janela}</div>', unsafe_allow_html=True)

    else:

        df_tela = df_validos.copy()



    # Padronização e Limpeza dos Supervisores

    df_tela['SUPERVISOR_MOSTRAR'] = df_tela[col_supervisor].fillna('MAICON').astype(str).str.upper().str.strip()

    df_tela['SUPERVISOR_MOSTRAR'] = df_tela['SUPERVISOR_MOSTRAR'].replace({'#N/A': 'MAICON', 'NAN': 'MAICON', '': 'MAICON'})

    df_tela['SUPERVISOR_MOSTRAR'] = df_tela['SUPERVISOR_MOSTRAR'].apply(

        lambda x: 'ALAN' if 'ALAN' in str(x) 

        else ('FRANCISCO GERALDO CARVALHO JUNIOR' if 'FRANCISCO' in str(x) 

        else ('MARCOS ROBERTO' if 'MARCOS' in str(x) else x))

    )



    df_supervisor_atual = df_tela[df_tela['SUPERVISOR_MOSTRAR'] == supervisor_atual].copy()



    # =========================================================================

    # 🏛️ FLUXO DE RENDERIZAÇÃO POR SUB-TELA

    # =========================================================================

    p_total = int(df_supervisor_atual['P_COUNT'].sum()) if not df_supervisor_atual.empty else 0

    r_total = int(df_supervisor_atual['R_COUNT'].sum()) if not df_supervisor_atual.empty else 0

    i_total = int(df_supervisor_atual['I_COUNT'].sum()) if not df_supervisor_atual.empty else 0



    if sub_tela_atual == "CENARIO":

        st.markdown(f'<div class="title-supervisor-tv">👤 SUPERVISÃO: {supervisor_titulo}</div>', unsafe_allow_html=True)

        

        # Exibe APENAS os cards em proporções enormes ocupando o meio da tela

        st.markdown("<br><br>", unsafe_allow_html=True)

        c_kpi1, c_kpi2, c_kpi3 = st.columns(3)

        with c_kpi1:

            st.markdown(f'<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 CONTRATOS PENDENTES</div><div class="custom-pendente-value">{p_total}</div></div>', unsafe_allow_html=True)

        with c_kpi2:

            st.markdown(f'<div class="card-meta-tv rota"><div class="card-meta-label">🟣 TÉCNICOS EM ROTA</div><div class="card-meta-value">{r_total}</div></div>', unsafe_allow_html=True)

        with c_kpi3:

            st.markdown(f'<div class="card-meta-tv iniciado"><div class="card-meta-label">🟢 ATENDIMENTOS INICIADOS</div><div class="card-meta-value">{i_total}</div></div>', unsafe_allow_html=True)

            

        # 🔥 GATILHO DA VOZ EXCLUSIVO PARA A TELA DE CENÁRIO (Dispara apenas uma vez)

        id_unico_fala = f"{supervisor_titulo}_{p_total}_{r_total}_{i_total}"

        if st.session_state["chave_fala_gatilho"] != id_unico_fala:

            frase_narracao = f"Téc um {texto_audio_janela}. Supervisor {supervisor_titulo.lower()}, possui {p_total} pendentes, {r_total} em rota, e {i_total} iniciados."

            st.components.v1.html(f"""

                <script>

                    var msg = new SpeechSynthesisUtterance();

                    msg.text = "{frase_narracao}";

                    msg.lang = "pt-BR";

                    msg.rate = 1.0;

                    window.speechSynthesis.speak(msg);

                </script>

            """, height=0, width=0)

            st.session_state["chave_fala_gatilho"] = id_unico_fala



    elif sub_tela_atual == "CONTRATOS":

        st.markdown(f'<div class="title-supervisor-tv" style="color: #cc6600;">⏳ CONTRATOS PENDENTES: {supervisor_titulo}</div>', unsafe_allow_html=True)

        

        # Exibe estritamente a listagem limpa em duas colunas com fonte ampliada

        if not df_supervisor_atual.empty:

            df_pendentes_lista = df_supervisor_atual[df_supervisor_atual['P_COUNT'] > 0].copy()

            

            if not df_pendentes_lista.empty:

                df_ordenado = df_pendentes_lista.sort_values('Contrato').drop_duplicates(subset=['Contrato'])

                total_linhas = len(df_ordenado)

                

                df_col1 = df_ordenado.iloc[:(total_linhas + 1) // 2]

                df_col2 = df_ordenado.iloc[(total_linhas + 1) // 2:]

                

                t_col1, t_col2 = st.columns(2)

                with t_col1:

                    for _, linha in df_col1.iterrows():

                        st.markdown(f'<div class="item-linha-tv">📄 <span class="item-contrato-tv">{linha.get("Contrato", "N/A")}</span> <span class="divisor-item-tv">|</span> 👤 {str(linha.get(col_tecnico_check, "TÉCNICO")).upper()}</div>', unsafe_allow_html=True)

                with t_col2:

                    for _, linha in df_col2.iterrows():

                        st.markdown(f'<div class="item-linha-tv">📄 <span class="item-contrato-tv">{linha.get("Contrato", "N/A")}</span> <span class="divisor-item-tv">|</span> 👤 {str(linha.get(col_tecnico_check, "TÉCNICO")).upper()}</div>', unsafe_allow_html=True)

            else:

                st.success(f"🎉 Excelente! Nenhum contrato pendente para a equipe do {supervisor_titulo}!")

        else:

            st.info(f"Nenhum registro ativo para o supervisor {supervisor_titulo}.")

else:

    st.warning("👈 Por favor, insira os arquivos de rota na página inicial primeiro.")



# ⏱️ Sincronizador contínuo do timer em background (1 segundo)

time.sleep(1)

st.rerun() 


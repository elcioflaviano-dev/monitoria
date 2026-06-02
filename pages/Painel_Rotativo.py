import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

st.markdown("""<style>
    [data-testid="stSidebar"] { display: none !important; }
    .topo-container { background: #003366; color: white; padding: 25px; border-radius: 0 0 15px 15px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;}
    .nome-sup { font-size: 45px; font-weight: 900; }
    .card-p { background:#fff3e0; padding:10px; border-radius:4px; font-size:14px; font-weight:bold; border-left:4px solid #cc6600; border:1px solid #ddd; margin-bottom: 8px; }
    .card-r { background:#e3f2fd; padding:10px; border-radius:4px; font-size:14px; font-weight:bold; border-left:4px solid #1976d2; border:1px solid #ddd; margin-bottom: 8px; }
    .card-i { background:#e8f5e9; padding:10px; border-radius:4px; font-size:14px; font-weight:bold; border-left:4px solid #388e3c; border:1px solid #ddd; margin-bottom: 8px; }
    .hora-gigante { font-size: 150px; text-align:center; margin-top: 100px; color: #333; }
    .resumo-sup { font-size: 20px; font-weight: 900; margin-top: 15px; color: #003366; border-bottom: 2px solid #ccc; padding-bottom: 5px; }
</style>""", unsafe_allow_html=True)

SUPERVISORES = ["MAICON", "NELSON", "MARCOS ROBERTO", "ALAN", "FRANCISCO GERALDO CARVALHO JUNIOR"]

# O índice vai até len(SUPERVISORES) + 1. (0 a 4 = Supervisores, 5 = Resumo, 6 = Hora)
if "idx" not in st.session_state: st.session_state.idx = 0
if "last_time" not in st.session_state: st.session_state.last_time = time.time()
if "falar" not in st.session_state: st.session_state.falar = True

# Lógica de tempo (10s por supervisor, 15s no Resumo, 40s na Hora)
if st.session_state.idx < len(SUPERVISORES):
    espera = 10
elif st.session_state.idx == len(SUPERVISORES):
    espera = 15 # Tempo da tela de Resumo Geral
else:
    espera = 40 # Tempo da tela de Hora

tempo_passado = time.time() - st.session_state.last_time

if tempo_passado > espera:
    # Avança no carrossel. O total de telas é len(SUPERVISORES) + 2 (Resumo e Hora)
    st.session_state.idx = (st.session_state.idx + 1) % (len(SUPERVISORES) + 2)
    st.session_state.last_time = time.time()
    st.session_state.falar = True
    st.rerun()

# LIMPEZA ABSOLUTA DE TELA
conteudo = st.empty()
conteudo.empty()

with conteudo.container():
    if st.session_state.idx < len(SUPERVISORES):
        sup = SUPERVISORES[st.session_state.idx]
    elif st.session_state.idx == len(SUPERVISORES):
        sup = "RESUMO GERAL PENDENTES"
    else:
        sup = "PAUSA"

    # Topo
    st.markdown(f'''<div class="topo-container">
        <div class="nome-sup">{sup}</div>
        <a href="/" style="color:#fff; font-size:18px; font-weight:bold; border:2px solid #fff; padding:8px 15px; border-radius:5px; text-decoration:none;">🏠 HOME</a>
    </div>''', unsafe_allow_html=True)

    # Lógica de Dados (Supervisores ou Resumo)
    if st.session_state.idx <= len(SUPERVISORES):
        if os.path.exists("rota_sincronizada.csv"):
            df = pd.read_csv("rota_sincronizada.csv", dtype=str)
            df.columns = [str(c).strip() for c in df.columns]
            df['SUPERVISOR_CLEAN'] = df['SUPERVISOR'].astype(str).str.strip().str.upper()
            
            # --- TELA INDIVIDUAL DO SUPERVISOR ---
            if st.session_state.idx < len(SUPERVISORES):
                # ZERANDO VARIÁVEIS A CADA LOOP
                df_sup = pd.DataFrame()
                df_pendentes = pd.DataFrame()
                df_rota = pd.DataFrame()
                df_iniciado = pd.DataFrame()

                df_sup = df[df['SUPERVISOR_CLEAN'] == sup.strip().upper()].copy()
                
                if not df_sup.empty:
                    col_status_real = 'Status da Atividade' if 'Status da Atividade' in df_sup.columns else 'STATUS_ATIVIDADE'
                    df_sup['Status_Atividade_Upper'] = df_sup[col_status_real].fillna('').astype(str).str.upper().str.strip()
                    df_limpo = df_sup[df_sup['Status_Atividade_Upper'] != 'SUSPENSO'].copy()
                    
                    df_pendentes = df_limpo[df_limpo['Status_Atividade_Upper'].str.contains('PENDENTE|EM ABERTO|ABERTO|PEND', na=False)].copy()
                    df_rota = df_limpo[df_limpo['Status_Atividade_Upper'].str.contains('ROTA|DESLOC|DESLOCAMENTO', na=False)].copy()
                    df_iniciado = df_limpo[df_limpo['Status_Atividade_Upper'].str.contains('INICIADO|PRODUTIVO|EXECUCAO|INIC', na=False)].copy()

                    # Limpeza de duplicados por Contrato
                    if 'Contrato' in df_pendentes.columns and not df_pendentes.empty: df_pendentes = df_pendentes.drop_duplicates(subset=['Contrato'])
                    if 'Contrato' in df_rota.columns and not df_rota.empty: df_rota = df_rota.drop_duplicates(subset=['Contrato'])
                    if 'Contrato' in df_iniciado.columns and not df_iniciado.empty: df_iniciado = df_iniciado.drop_duplicates(subset=['Contrato'])

                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.subheader(f"🔴 {len(df_pendentes)} PENDENTES")
                    for _, row in df_pendentes.iterrows():
                        st.markdown(f'<div class="card-p">📄 {row.get("Contrato", "")}<br>👤 {str(row.get("Recurso", "TÉC")).upper()}</div>', unsafe_allow_html=True)
                
                with col2:
                    st.subheader(f"🔵 {len(df_rota)} EM ROTA")
                    for _, row in df_rota.iterrows():
                        st.markdown(f'<div class="card-r">📄 {row.get("Contrato", "")}<br>👤 {str(row.get("Recurso", "TÉC")).upper()}</div>', unsafe_allow_html=True)
                
                with col3:
                    st.subheader(f"🟢 {len(df_iniciado)} INICIADOS")
                    for _, row in df_iniciado.iterrows():
                        st.markdown(f'<div class="card-i">📄 {row.get("Contrato", "")}<br>👤 {str(row.get("Recurso", "TÉC")).upper()}</div>', unsafe_allow_html=True)

                # VOZ: Fala APENAS os pendentes do supervisor
                if st.session_state.falar:
                    texto_fala = f"Supervisor {sup}, {len(df_pendentes)} pendentes."
                    st.components.v1.html(f"<script>var m=new SpeechSynthesisUtterance('{texto_fala}'); window.speechSynthesis.speak(m);</script>", height=0)
                    st.session_state.falar = False

            # --- TELA DE RESUMO GERAL PENDENTES ---
            elif st.session_state.idx == len(SUPERVISORES):
                col_status_real = 'Status da Atividade' if 'Status da Atividade' in df.columns else 'STATUS_ATIVIDADE'
                df['Status_Atividade_Upper'] = df[col_status_real].fillna('').astype(str).str.upper().str.strip()
                df_limpo_geral = df[df['Status_Atividade_Upper'] != 'SUSPENSO'].copy()
                df_pendentes_gerais = df_limpo_geral[df_limpo_geral['Status_Atividade_Upper'].str.contains('PENDENTE|EM ABERTO|ABERTO|PEND', na=False)].copy()
                
                if 'Contrato' in df_pendentes_gerais.columns and not df_pendentes_gerais.empty:
                    df_pendentes_gerais = df_pendentes_gerais.drop_duplicates(subset=['Contrato'])

                st.subheader(f"🔴 TOTAL DE PENDENTES NA OPERAÇÃO: {len(df_pendentes_gerais)}")
                
                # Divide os supervisores em colunas para o resumo
                cols_resumo = st.columns(len(SUPERVISORES))
                
                for idx_col, supervisor_nome in enumerate(SUPERVISORES):
                    with cols_resumo[idx_col]:
                        # Filtra pendentes desse supervisor específico
                        pendentes_deste = df_pendentes_gerais[df_pendentes_gerais['SUPERVISOR_CLEAN'] == supervisor_nome.strip().upper()]
                        st.markdown(f'<div class="resumo-sup">{supervisor_nome} ({len(pendentes_deste)})</div>', unsafe_allow_html=True)
                        for _, row in pendentes_deste.iterrows():
                            st.markdown(f'<div class="card-p">📄 {row.get("Contrato", "")}<br>👤 {str(row.get("Recurso", "TÉC")).upper()}</div>', unsafe_allow_html=True)

                if st.session_state.falar:
                    st.components.v1.html(f"<script>var m=new SpeechSynthesisUtterance('Atenção. Resumo de pendentes: {len(df_pendentes_gerais)} contratos.'); window.speechSynthesis.speak(m);</script>", height=0)
                    st.session_state.falar = False
        else:
            st.error("Arquivo rota_sincronizada.csv não encontrado.")
            
    # --- TELA DA HORA (PAUSA) ---
    else:
        hora = (datetime.utcnow() - timedelta(hours=3)).strftime("%H:%M:%S")
        st.markdown(f'<div class="hora-gigante">{hora}</div>', unsafe_allow_html=True)

time.sleep(1); st.rerun()

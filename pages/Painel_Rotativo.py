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
    .card-c { background:#f9f9f9; padding:10px; border-radius:4px; font-size:14px; font-weight:bold; border-left:4px solid #cc6600; border:1px solid #ddd; margin-bottom: 10px; }
    .hora-gigante { font-size: 150px; text-align:center; margin-top: 100px; color: #333; }
</style>""", unsafe_allow_html=True)

SUPERVISORES = ["MAICON", "NELSON", "MARCOS ROBERTO", "ALAN", "FRANCISCO GERALDO CARVALHO JUNIOR"]

if "idx" not in st.session_state: st.session_state.idx = 0
if "last_time" not in st.session_state: st.session_state.last_time = time.time()

# Lógica de tempo (5 segundos por supervisor, 40 segundos na hora)
espera = 5 if st.session_state.idx < len(SUPERVISORES) else 40
tempo_passado = time.time() - st.session_state.last_time

if tempo_passado > espera:
    st.session_state.idx = (st.session_state.idx + 1) % (len(SUPERVISORES) + 1)
    st.session_state.last_time = time.time()
    st.rerun()

tela = st.empty()

with tela.container():
    sup = SUPERVISORES[st.session_state.idx] if st.session_state.idx < len(SUPERVISORES) else "PAUSA"

    # Topo
    st.markdown(f'''<div class="topo-container">
        <div class="nome-sup">{sup}</div>
        <a href="/" style="color:#fff; font-size:18px; font-weight:bold; border:2px solid #fff; padding:8px 15px; border-radius:5px; text-decoration:none;">🏠 HOME</a>
    </div>''', unsafe_allow_html=True)

    if st.session_state.idx < len(SUPERVISORES):
        if os.path.exists("rota_sincronizada.csv"):
            df = pd.read_csv("rota_sincronizada.csv", dtype=str)
            df.columns = [str(c).strip() for c in df.columns]
            
            # Limpeza do supervisor garantindo comparação exata
            df['SUPERVISOR_CLEAN'] = df['SUPERVISOR'].astype(str).str.strip().str.upper()
            
            # Filtro do supervisor atual
            df_sup = df[df['SUPERVISOR_CLEAN'] == sup.strip().upper()].copy()
            
            # --- MOTOR DE JANELAS (Copiado do seu TEC1) ---
            if not df_sup.empty:
                col_status_real = 'Status da Atividade' if 'Status da Atividade' in df_sup.columns else 'STATUS_ATIVIDADE'
                df_sup['Status_Atividade_Upper'] = df_sup[col_status_real].fillna('').astype(str).str.upper().str.strip()
                df_limpo = df_sup[df_sup['Status_Atividade_Upper'] != 'SUSPENSO'].copy()
                
                df_limpo['P_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('PENDENTE|EM ABERTO|ABERTO|PEND', na=False).astype(int)
                df_limpo['R_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('ROTA|DESLOC|DESLOCAMENTO', na=False).astype(int)
                df_limpo['I_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('INICIADO|PRODUTIVO|EXECUCAO|INIC', na=False).astype(int)
                
                df_validos = df_limpo[(df_limpo['P_COUNT'] > 0) | (df_limpo['R_COUNT'] > 0) | (df_limpo['I_COUNT'] > 0)].copy()
                
                col_janela = None
                for c in df_validos.columns:
                    if 'JANELA' in str(c).upper() or 'INTERVALO' in str(c).upper():
                        col_janela = c
                        break

                hora_atual = (datetime.utcnow() - timedelta(hours=3)).hour

                if col_janela is not None and not df_validos.empty:
                    df_validos['Intervalo_Tratado'] = df_validos[col_janela].fillna('').astype(str).str.strip()
                    
                    def extrair_hora_limite(janela_str):
                        try:
                            partes = janela_str.replace(':', '').split('-')
                            return int(partes[1].strip()[:2]) if len(partes) == 2 else 24
                        except: 
                            return 24

                    df_validos['Hora_Limite_Janela'] = df_validos['Intervalo_Tratado'].apply(extrair_hora_limite)
                    
                    if hora_atual < 12:
                        condicao_horario = (df_validos['Hora_Limite_Janela'] <= 12)
                    elif 12 <= hora_atual < 15:
                        condicao_horario = (df_validos['Hora_Limite_Janela'] <= 15)
                    else:
                        condicao_horario = (df_validos['Hora_Limite_Janela'] <= 24)

                    df_base_janela = df_validos[condicao_horario | (df_validos['R_COUNT'] > 0) | (df_validos['I_COUNT'] > 0)].copy()
                    pendentes = df_base_janela[df_base_janela['P_COUNT'] > 0].copy()
                    
                    if pendentes.empty and df_base_janela.empty: 
                        pendentes = df_validos[df_validos['P_COUNT'] > 0].copy()
                else:
                    pendentes = df_validos[df_validos['P_COUNT'] > 0].copy()
            else:
                pendentes = pd.DataFrame()
            # --- FIM DO MOTOR DE JANELAS ---

            # Proteção contra duplicados visuais baseados no número do Contrato
            if 'Contrato' in pendentes.columns and not pendentes.empty:
                pendentes['Contrato'] = pendentes['Contrato'].astype(str).apply(lambda x: x.split('.')[0] if '.' in x else x)
                pendentes = pendentes.drop_duplicates(subset=['Contrato'])

            st.subheader(f"🔴 {len(pendentes)} PENDENTES")
            cols = st.columns(4)
            for i, (_, row) in enumerate(pendentes.iterrows()):
                with cols[i % 4]:
                    st.markdown(f'<div class="card-c">📄 {row.get("Contrato", "")}<br>👤 {str(row.get("Recurso", "TÉC")).upper()}</div>', unsafe_allow_html=True)
        else:
            st.error("Arquivo não encontrado.")
    else:
        # LÓGICA DA PAUSA (Hora atual)
        hora = (datetime.utcnow() - timedelta(hours=3)).strftime("%H:%M:%S")
        st.markdown(f'<div class="hora-gigante">{hora}</div>', unsafe_allow_html=True)

time.sleep(1); st.rerun()

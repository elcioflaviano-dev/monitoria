import streamlit as st
import pandas as pd
import os
import time

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

# Carregamento
df_master = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str) if os.path.exists(ARQUIVO_ROTA_DISCO) else None

# Controle de Ciclo
if "index_sup_tv" not in st.session_state: st.session_state["index_sup_tv"] = 0
if "ciclo_completo" not in st.session_state: st.session_state["ciclo_completo"] = False

SUPERVISORES = ["MAICON", "NELSON", "MARCOS ROBERTO", "ALAN", "FRANCISCO GERALDO CARVALHO JUNIOR"]

# Lógica de Tempo (5s por supervisor, 40s no final)
if st.session_state["ciclo_completo"]:
    time.sleep(40)
    st.session_state["ciclo_completo"] = False
    st.session_state["index_sup_tv"] = 0
    st.rerun()
else:
    time.sleep(5)
    st.session_state["index_sup_tv"] += 1
    if st.session_state["index_sup_tv"] >= len(SUPERVISORES):
        st.session_state["ciclo_completo"] = True
    st.rerun()

supervisor_atual = SUPERVISORES[st.session_state["index_sup_tv"] % len(SUPERVISORES)]

# CSS Aprimorado
st.markdown("""<style>
    .barra-preta { background: #000; color: #fff; padding: 15px; text-align: center; font-size: 24px; font-weight: bold; }
    .card-contrato { background: #f4f4f4; border-left: 6px solid #cc6600; padding: 15px; margin: 10px; border-radius: 5px; display: flex; justify-content: space-between; align-items: center; }
    .contrato-txt { font-size: 24px; font-weight: 800; color: #333; }
    .tecnico-txt { font-size: 20px; color: #666; }
</style>""", unsafe_allow_html=True)

# Layout
st.markdown(f'<div class="barra-preta">TV MODE • EQUIPE: {supervisor_atual}</div>', unsafe_allow_html=True)

if df_master is not None:
    df = df_master.copy()
    # Limpeza do .0
    if 'Contrato' in df.columns:
        df['Contrato'] = df['Contrato'].astype(str).str.replace('.0', '', regex=False)
    
    # Filtro
    df_sup = df[df['SUPERVISOR'].str.contains(supervisor_atual, case=False, na=False)]
    pendentes = df_sup[df_sup['Status da Atividade'].fillna('').str.contains('PENDENTE', case=False, na=False)]
    
    p_total = len(pendentes)
    
    st.markdown(f"<h1 style='text-align:center'>Total de Pendentes: {p_total}</h1>", unsafe_allow_html=True)
    
    # Fala
    st.components.v1.html(f"""<script>
        var msg = new SpeechSynthesisUtterance("Supervisor {supervisor_atual}, {p_total} pendentes.");
        msg.lang = "pt-BR"; window.speechSynthesis.speak(msg);
    </script>""", height=0)
    
    # Layout Visual dos Contratos
    for _, linha in pendentes.iterrows():
        st.markdown(f'''
            <div class="card-contrato">
                <span class="contrato-txt">📄 CONTRATO: {linha.get('Contrato', 'N/A')}</span>
                <span class="tecnico-txt">👤 {linha.get('Recurso', 'TÉCNICO').upper()}</span>
            </div>
        ''', unsafe_allow_html=True)
else:
    st.warning("Carregando...")

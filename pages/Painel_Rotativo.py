import streamlit as st
import pandas as pd
import time

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 1. Carregamento Seguro
if not os.path.exists("rota_sincronizada.csv"):
    st.error("Arquivo rota_sincronizada.csv não encontrado!")
    st.stop()

df = pd.read_csv("rota_sincronizada.csv", dtype=str)
if 'Contrato' in df.columns:
    df['Contrato'] = df['Contrato'].str.replace('.0', '', regex=False)

SUPERVISORES = ["MAICON", "NELSON", "MARCOS ROBERTO", "ALAN", "FRANCISCO GERALDO CARVALHO JUNIOR"]

# 2. Sessão
if "idx" not in st.session_state: st.session_state.idx = 0
if "last_time" not in st.session_state: st.session_state.last_time = time.time()

# 3. Tempo (5s por tela, 40s no final)
espera = 5 if st.session_state.idx < len(SUPERVISORES) else 40
if time.time() - st.session_state.last_time > espera:
    st.session_state.idx = (st.session_state.idx + 1) % (len(SUPERVISORES) + 1)
    st.session_state.last_time = time.time()
    st.rerun()

# 4. Layout Simples (Nada que quebre o CSS)
sup = SUPERVISORES[st.session_state.idx % len(SUPERVISORES)] if st.session_state.idx < len(SUPERVISORES) else "PAUSA"

st.markdown(f"## EQUIPE: {sup} | Tempo de tela: {int(espera - (time.time() - st.session_state.last_time))}s")

if st.session_state.idx < len(SUPERVISORES):
    pendentes = df[(df['SUPERVISOR'].str.contains(sup, case=False, na=False)) & 
                   (df['Status da Atividade'].fillna('').str.contains('PENDENTE', case=False, na=False))]
    
    # Exibição simples: Número grande e lista logo abaixo
    st.title(f"🔴 {len(pendentes)} PENDENTES")
    
    # Fala
    st.components.v1.html(f"<script>var m=new SpeechSynthesisUtterance('Supervisor {sup}, {len(pendentes)} pendentes.'); window.speechSynthesis.speak(m);</script>", height=0)
    
    # Lista (Simples, sem colunas complexas para não bugar)
    for _, row in pendentes.iterrows():
        st.write(f"📄 CONTRATO: {row['Contrato']}  |  👤 TÉCNICO: {row.get('Recurso', 'N/A')}")
else:
    st.title("⏳ PAINEL EM PAUSA (40s)")

time.sleep(1)
st.rerun()

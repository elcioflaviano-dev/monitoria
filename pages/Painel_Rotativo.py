import streamlit as st
import pandas as pd
import time
from datetime import datetime

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# CSS para travar o layout
st.markdown("""<style>
    [data-testid="stSidebar"] { display: none !important; }
    .barra-preta { background:#000; color:#fff; padding:15px; text-align:center; font-size:30px; font-weight:900; position:fixed; top:0; left:0; width:100%; z-index:999; }
    .hora-gigante { font-size: 150px; font-weight:900; text-align:center; margin-top: 150px; color: #000; }
    .card-c { background:#eee; padding:8px; border-radius:4px; font-size:16px; font-weight:bold; border-left:5px solid #cc6600; margin-bottom:5px; }
</style>""", unsafe_allow_html=True)

SUPERVISORES = ["MAICON", "NELSON", "MARCOS ROBERTO", "ALAN", "FRANCISCO GERALDO CARVALHO JUNIOR"]

if "idx" not in st.session_state: st.session_state.idx = 0
if "last_time" not in st.session_state: st.session_state.last_time = time.time()

# Lógica de Tempo
espera = 5 if st.session_state.idx < len(SUPERVISORES) else 40
tempo_passado = time.time() - st.session_state.last_time

if tempo_passado > espera:
    st.session_state.idx = (st.session_state.idx + 1) % (len(SUPERVISORES) + 1)
    st.session_state.last_time = time.time()
    st.rerun()

# --- A MUDANÇA ESTÁ AQUI: Criamos um container para o conteúdo ---
conteudo = st.container()

with conteudo:
    if st.session_state.idx < len(SUPERVISORES):
        sup = SUPERVISORES[st.session_state.idx]
        
        # BARRA NO TOPO
        st.markdown(f'<div class="barra-preta">{sup} | {int(espera - tempo_passado)}s</div>', unsafe_allow_html=True)
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        
        # Leitura e Filtro
        df = pd.read_csv("rota_sincronizada.csv", dtype=str)
        if 'Contrato' in df.columns: df['Contrato'] = df['Contrato'].str.replace('.0', '', regex=False)
        
        pendentes = df[(df['SUPERVISOR'].str.strip().str.upper() == sup.strip().upper()) & 
                       (df['Status da Atividade'].fillna('').str.contains('PENDENTE', case=False, na=False))]
        
        st.title(f"🔴 {len(pendentes)} PENDENTES")
        
        # Grade de contratos
        cols = st.columns(2)
        for i, (_, row) in enumerate(pendentes.iterrows()):
            cols[i % 2].markdown(f'<div class="card-c">📄 {row["Contrato"]} | 👤 {row.get("Recurso", "TÉC").upper()}</div>', unsafe_allow_html=True)
        
        # Fala (Apenas no primeiro segundo)
        if tempo_passado < 1.0:
            st.components.v1.html(f"<script>var m=new SpeechSynthesisUtterance('Supervisor {sup}, {len(pendentes)} pendentes.'); window.speechSynthesis.speak(m);</script>", height=0)
    else:
        # PAUSA: Hora com segundos
        hora_atual = datetime.now().strftime("%H:%M:%S")
        st.markdown(f'<div class="barra-preta">PAUSA | {int(espera - tempo_passado)}s</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="hora-gigante">{hora_atual}</div>', unsafe_allow_html=True)

time.sleep(1); st.rerun()

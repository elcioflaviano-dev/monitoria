import streamlit as st
import pandas as pd
import os
import time

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 1. Configuração dos Supervisores
SUPERVISORES = ["MAICON", "NELSON", "MARCOS ROBERTO", "ALAN", "FRANCISCO GERALDO CARVALHO JUNIOR"]

# 2. Sessão para Rotação
if "idx" not in st.session_state: st.session_state.idx = 0
if "last_time" not in st.session_state: st.session_state.last_time = time.time()

# 3. Lógica de Tempo (5s por supervisor / 40s final)
espera = 5 if st.session_state.idx < len(SUPERVISORES) else 40
if time.time() - st.session_state.last_time > espera:
    st.session_state.idx = (st.session_state.idx + 1) % (len(SUPERVISORES) + 1)
    st.session_state.last_time = time.time()
    st.rerun()

# 4. Renderização
if st.session_state.idx < len(SUPERVISORES):
    sup = SUPERVISORES[st.session_state.idx]
    
    # Barra Superior Preta
    st.markdown(f"""
        <div style="background:#000; color:#fff; padding:10px; text-align:center; font-weight:bold; font-size:20px;">
            EQUIPE: {sup} | SEG: {int(espera - (time.time() - st.session_state.last_time))}s
        </div>
    """, unsafe_allow_html=True)
    
    # Carregamento do arquivo
    if os.path.exists("rota_sincronizada.csv"):
        df = pd.read_csv("rota_sincronizada.csv", dtype=str)
        if 'Contrato' in df.columns:
            df['Contrato'] = df['Contrato'].str.replace('.0', '', regex=False)
        
        pendentes = df[(df['SUPERVISOR'].str.contains(sup, case=False, na=False)) & 
                       (df['Status da Atividade'].fillna('').str.contains('PENDENTE', case=False, na=False))]
        
        # Layout: Número grande e Lista
        st.title(f"🔴 {len(pendentes)} PENDENTES")
        
        # Fala (Dispara apenas no carregamento da tela)
        st.components.v1.html(f"<script>var m=new SpeechSynthesisUtterance('Supervisor {sup}, {len(pendentes)} pendentes.'); window.speechSynthesis.speak(m);</script>", height=0)
        
        # Exibição simples dos contratos
        for _, row in pendentes.iterrows():
            st.markdown(f"**📄 CONTRATO:** {row['Contrato']}  |  **👤 TÉCNICO:** {row.get('Recurso', 'N/A').upper()}")
            st.divider()
    else:
        st.error("Arquivo rota_sincronizada.csv não encontrado na pasta!")
else:
    st.title("⏳ PAINEL EM PAUSA (40s)")

time.sleep(1)
st.rerun()

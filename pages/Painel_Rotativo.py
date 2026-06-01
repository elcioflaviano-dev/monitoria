import streamlit as st
import pandas as pd
import time

st.set_page_config(layout="wide")

# Barra Fixa e Estilo Simples
st.markdown("""<style>
    .header { background: #000; color: #fff; padding: 15px; text-align: center; font-size: 25px; font-weight: bold; position: fixed; top:0; left:0; width:100%; z-index:999; }
    .content { margin-top: 80px; }
    .box-pendente { background: #ffcccc; color: #b30000; padding: 20px; border-radius: 10px; text-align: center; font-size: 30px; font-weight: bold; }
    .item-contrato { background: #eee; padding: 10px; margin: 5px 0; border-radius: 5px; font-size: 18px; }
</style>""", unsafe_allow_html=True)

# Lógica de Controle
SUPERVISORES = ["MAICON", "NELSON", "MARCOS ROBERTO", "ALAN", "FRANCISCO GERALDO CARVALHO JUNIOR"]
if "idx" not in st.session_state: st.session_state.idx = 0
if "last_time" not in st.session_state: st.session_state.last_time = time.time()

espera = 5 if st.session_state.idx < len(SUPERVISORES) else 40
if time.time() - st.session_state.last_time > espera:
    st.session_state.idx = (st.session_state.idx + 1) % (len(SUPERVISORES) + 1)
    st.session_state.last_time = time.time()
    st.rerun()

# Renderização
if st.session_state.idx < len(SUPERVISORES):
    sup = SUPERVISORES[st.session_state.idx]
    st.markdown(f'<div class="header">EQUIPE: {sup}</div>', unsafe_allow_html=True)
    
    df = pd.read_csv("rota_sincronizada.csv", dtype=str)
    df['Contrato'] = df['Contrato'].str.replace('.0', '', regex=False)
    
    pendentes = df[(df['SUPERVISOR'].str.contains(sup, case=False, na=False)) & 
                   (df['Status da Atividade'].fillna('').str.contains('PENDENTE', case=False, na=False))]
    
    st.markdown('<div class="content"></div>', unsafe_allow_html=True)
    
    # Visualização Simples
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.markdown(f'<div class="box-pendente">{len(pendentes)} PENDENTES</div>', unsafe_allow_html=True)
    with col_b:
        for _, row in pendentes.iterrows():
            st.markdown(f'<div class="item-contrato">📄 {row["Contrato"]} | 👤 {row.get("Recurso", "Técnico")}</div>', unsafe_allow_html=True)

    # Fala
    st.components.v1.html(f"<script>var m=new SpeechSynthesisUtterance('Supervisor {sup}, {len(pendentes)} pendentes.'); window.speechSynthesis.speak(m);</script>", height=0)

else:
    st.markdown('<div class="header">PAINEL EM PAUSA</div>', unsafe_allow_html=True)

time.sleep(1)
st.rerun()

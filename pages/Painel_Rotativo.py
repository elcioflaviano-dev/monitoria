import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# CSS para o botão parecer um link mas agir como botão do Streamlit
st.markdown("""<style>
    [data-testid="stSidebar"] { display: none !important; }
    .barra-preta { background:#000; color:#fff; padding:15px; text-align:center; font-size:24px; font-weight:900; position:fixed; top:0; left:0; width:100%; z-index:9999; display: flex; justify-content: space-between; align-items: center; }
    /* Ajusta o botão para parecer link */
    div.stButton > button { background: transparent; color: #fff; border: 1px solid #fff; padding: 5px 15px; font-weight: bold; border-radius: 5px; }
    .conteudo { margin-top: 80px; }
    .card-c { background:#eee; padding:10px; border-radius:5px; font-size:16px; font-weight:bold; border-left:5px solid #cc6600; margin:5px; max-width: 450px; }
    .grid-contratos { display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 10px; }
</style>""", unsafe_allow_html=True)

SUPERVISORES = ["MAICON", "NELSON", "MARCOS ROBERTO", "ALAN", "FRANCISCO GERALDO CARVALHO JUNIOR"]

# Sessão
if "idx" not in st.session_state: st.session_state.idx = 0
if "last_time" not in st.session_state: st.session_state.last_time = time.time()

# Botão Home: Se clicado, redireciona para a página principal (ajuste o caminho se necessário)
# Se o arquivo estiver na pasta raiz, basta "/"
if st.sidebar.button("🏠 HOME"):
    st.switch_page("main.py") # Substitua pelo nome do seu arquivo principal

# Lógica de Tempo
espera = 5 if st.session_state.idx < len(SUPERVISORES) else 40
tempo_passado = time.time() - st.session_state.last_time
if tempo_passado > espera:
    st.session_state.idx = (st.session_state.idx + 1) % (len(SUPERVISORES) + 1)
    st.session_state.last_time = time.time()
    st.rerun()

# Barra Superior Fixa
sup_ou_pausa = SUPERVISORES[st.session_state.idx] if st.session_state.idx < len(SUPERVISORES) else "PAUSA"
st.markdown(f'''<div class="barra-preta">
    <div style="width: 100px;"></div> 
    <span>{sup_ou_pausa} | {int(espera - tempo_passado)}s</span>
    <div style="width: 100px;"></div>
</div>''', unsafe_allow_html=True)

# Botão Home posicionado manualmente sobre a barra (usando colunas no topo ou CSS)
# Como o st.button na barra é difícil, vamos usar um link simples com target fixo
st.markdown(f'''<div style="position:fixed; top:12px; left:20px; z-index:10000;">
    <a href="/" target="_self" style="color:#fff; text-decoration:none; border:1px solid #fff; padding:5px 10px; border-radius:5px; font-weight:bold;">🏠 HOME</a>
</div>''', unsafe_allow_html=True)

# Conteúdo com limpeza
conteudo = st.container()
with conteudo:
    st.markdown('<div class="conteudo">', unsafe_allow_html=True)
    if st.session_state.idx < len(SUPERVISORES):
        sup = SUPERVISORES[st.session_state.idx]
        if os.path.exists("rota_sincronizada.csv"):
            df = pd.read_csv("rota_sincronizada.csv", dtype=str)
            if 'Contrato' in df.columns: df['Contrato'] = df['Contrato'].str.replace('.0', '', regex=False)
            
            pendentes = df[(df['SUPERVISOR'].str.strip().str.upper() == sup.strip().upper()) & 
                           (df['Status da Atividade'].fillna('').str.contains('PENDENTE', case=False, na=False))]
            
            st.title(f"🔴 {len(pendentes)} PENDENTES")
            st.markdown('<div class="grid-contratos">', unsafe_allow_html=True)
            for _, row in pendentes.iterrows():
                st.markdown(f'<div class="card-c">📄 {row["Contrato"]} | 👤 {row.get("Recurso", "TÉC").upper()}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        hora_local = (datetime.utcnow() - timedelta(hours=3)).strftime("%H:%M:%S")
        st.markdown(f'<h1 style="text-align:center; font-size:150px; margin-top:100px;">{hora_local}</h1>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

time.sleep(1); st.rerun()

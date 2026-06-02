import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# CSS: Esconde o menu lateral e formata os cards e o topo
st.markdown("""<style>
    [data-testid="stSidebar"] { display: none !important; }
    
    .topo-container { 
        background: #003366; 
        color: white; 
        padding: 25px; 
        border-radius: 0 0 15px 15px; 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        margin-bottom: 20px;
    }
    .nome-sup { font-size: 45px; font-weight: 900; }
    .card-c { background:#f9f9f9; padding:10px; border-radius:4px; font-size:14px; font-weight:bold; border-left:4px solid #cc6600; border:1px solid #ddd; margin-bottom: 10px; }
</style>""", unsafe_allow_html=True)

# Definição do Supervisor desta página
sup = "NELSON"

# Topo com nome e botão
st.markdown(f'''<div class="topo-container">
    <div class="nome-sup">{sup}</div>
    <a href="/" style="color:#fff; font-size:18px; font-weight:bold; border:2px solid #fff; padding:8px 15px; border-radius:5px; text-decoration:none;">🏠 HOME</a>
</div>''', unsafe_allow_html=True)

# Leitura e processamento
if os.path.exists("rota_sincronizada.csv"):
    df = pd.read_csv("rota_sincronizada.csv", dtype=str)
    
    # Limpeza extra por segurança
    df['SUPERVISOR_CLEAN'] = df['SUPERVISOR'].astype(str).str.strip().str.upper()
    
    # Filtro exato do supervisor
    pendentes = df[
        (df['SUPERVISOR_CLEAN'] == sup) & 
        (df['Status da Atividade'].fillna('').str.contains("PENDENTE", case=False, na=False))
    ]

    st.subheader(f"🔴 {len(pendentes)} PENDENTES")
    
    # Renderização nas 4 colunas nativas do Streamlit
    cols = st.columns(4)
    for i, (_, row) in enumerate(pendentes.iterrows()):
        with cols[i % 4]:
            contrato = str(row.get("Contrato", "")).replace(".0", "")
            tecnico = str(row.get("Recurso", "TÉC")).upper()
            st.markdown(f'<div class="card-c">📄 {contrato}<br>👤 {tecnico}</div>', unsafe_allow_html=True)
            
    # Voz sintética ao carregar a página
    st.components.v1.html(f"<script>var m=new SpeechSynthesisUtterance('Supervisor {sup}, {len(pendentes)} pendentes.'); window.speechSynthesis.speak(m);</script>", height=0)

else:
    st.error("Arquivo rota_sincronizada.csv não encontrado no sistema.")

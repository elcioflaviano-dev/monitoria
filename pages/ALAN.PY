import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# CSS para o topo colorido e 4 colunas
st.markdown("""<style>
    .topo { background: #003366; color: white; padding: 20px; text-align: center; font-size: 40px; font-weight: 900; border-radius: 10px; }
    .card-c { background:#f9f9f9; padding:10px; border-radius:4px; border-left:4px solid #cc6600; margin:5px; font-size:14px; }
</style>""", unsafe_allow_html=True)

st.markdown('<div class="topo">ALAN</div>', unsafe_allow_html=True)

df = pd.read_csv("rota_sincronizada.csv", dtype=str)
pendentes = df[(df['SUPERVISOR'].str.contains("ALAN", case=False, na=False)) & 
               (df['Status da Atividade'].str.contains("PENDENTE", case=False, na=False))]

st.subheader(f"🔴 {len(pendentes)} PENDENTES")
cols = st.columns(4)
for i, (_, row) in enumerate(pendentes.iterrows()):
    cols[i % 4].markdown(f'<div class="card-c">📄 {row["Contrato"]}<br>👤 {row.get("Recurso", "TÉC").upper()}</div>', unsafe_allow_html=True)

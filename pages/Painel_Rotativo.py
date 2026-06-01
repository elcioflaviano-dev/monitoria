import streamlit as st
import pandas as pd
import os
import time

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

# Carregamento
df_master = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str) if os.path.exists(ARQUIVO_ROTA_DISCO) else None

# CSS Fixo
st.markdown("""<style>
    .barra-status-tv { background-color: #111; color: #fff; padding: 10px; font-weight: bold; }
    .title-supervisor-tv { font-size: 36px; font-weight: 900; color: #005088; text-align: center; margin-bottom: 20px; }
    .custom-pendente-box { background-color: #ffcccc; border: 2px solid #ff9999; padding: 15px; text-align: center; }
    .custom-pendente-value { font-size: 40px; font-weight: 900; color: #b30000; }
    .card-meta-tv { background-color: #f8f9fa; border: 1px solid #ddd; padding: 15px; text-align: center; }
    .card-meta-value { font-size: 40px; font-weight: 900; }
</style>""", unsafe_allow_html=True)

st.markdown('<div class="barra-status-tv">📺 PAINEL OPERACIONAL FIXO</div>', unsafe_allow_html=True)

if df_master is not None and not df_master.empty:
    df = df_master.copy()
    col_sup = 'SUPERVISOR' if 'SUPERVISOR' in df.columns else 'Supervisor'
    
    # Cálculos
    df['P_COUNT'] = df['Status da Atividade'].fillna('').str.contains('PENDENTE', case=False, na=False).astype(int)
    df['R_COUNT'] = df['Status da Atividade'].fillna('').str.contains('ROTA', case=False, na=False).astype(int)
    df['I_COUNT'] = df['Status da Atividade'].fillna('').str.contains('INICIADO', case=False, na=False).astype(int)

    # Agrupa todos os supervisores na mesma tela
    matriz = df.groupby(col_sup)[['P_COUNT', 'R_COUNT', 'I_COUNT']].sum().reset_index()

    for _, row in matriz.iterrows():
        st.markdown(f"---")
        st.markdown(f"### 👤 SUPERVISOR: {row[col_sup]}")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="custom-pendente-box"><div class="custom-pendente-value">{int(row["P_COUNT"])}</div>🔴 PENDENTES</div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="card-meta-tv"><div class="card-meta-value">{int(row["R_COUNT"])}</div>🟣 EM ROTA</div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="card-meta-tv"><div class="card-meta-value">{int(row["I_COUNT"])}</div>🟢 INICIADO</div>', unsafe_allow_html=True)

else:
    st.warning("Carregue o arquivo de rota.")

# Refresh para manter dados atualizados
time.sleep(30)
st.rerun()

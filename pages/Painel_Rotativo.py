import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

# CSS para o Layout ficar bonito e profissional
st.markdown("""
    <style>
        .barra-topo { background: #000; color: #fff; padding: 20px; text-align: center; font-size: 32px; font-weight: 900; margin-bottom: 20px; }
        .card-supervisor { background: #005088; color: #fff; padding: 15px; font-size: 28px; font-weight: 800; border-radius: 5px; margin-top: 30px; }
        .card-pendente { background: #f8f9fa; border-left: 8px solid #cc6600; padding: 15px; margin: 10px 0; border-radius: 5px; box-shadow: 2px 2px 5px #ccc; }
        .txt-contrato { font-size: 22px; font-weight: 800; color: #cc6600; }
        .txt-tecnico { font-size: 20px; color: #333; float: right; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="barra-topo">PAINEL DE GESTÃO DE PENDÊNCIAS</div>', unsafe_allow_html=True)

if os.path.exists(ARQUIVO_ROTA_DISCO):
    df = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    # Limpa o ".0" de todos os contratos
    if 'Contrato' in df.columns:
        df['Contrato'] = df['Contrato'].str.replace('.0', '', regex=False)
    
    supervisores = df['SUPERVISOR'].unique()
    
    for sup in supervisores:
        df_sup = df[df['SUPERVISOR'] == sup]
        pendentes = df_sup[df_sup['Status da Atividade'].fillna('').str.contains('PENDENTE', case=False, na=False)]
        
        # Cabeçalho do Supervisor
        st.markdown(f'<div class="card-supervisor">👤 SUPERVISOR: {sup} (Total Pendentes: {len(pendentes)})</div>', unsafe_allow_html=True)
        
        if not pendentes.empty:
            # Layout em colunas para os contratos ficarem organizados
            cols = st.columns(2)
            for i, (_, row) in enumerate(pendentes.iterrows()):
                cols[i % 2].markdown(f'''
                    <div class="card-pendente">
                        <span class="txt-contrato">📄 {row.get('Contrato', 'N/A')}</span>
                        <span class="txt-tecnico">👤 {row.get('Recurso', 'TÉCNICO').upper()}</span>
                    </div>
                ''', unsafe_allow_html=True)
        else:
            st.info(f"Equipe {sup} sem pendências no momento.")
else:
    st.error("Arquivo de dados não encontrado.")

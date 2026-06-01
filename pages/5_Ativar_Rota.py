import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if os.path.exists(ARQUIVO_ROTA_DISCO):
    # Lemos como texto puro, sem cabeçalhos
    df = pd.read_csv(ARQUIVO_ROTA_DISCO, header=None, dtype=str)
    
    st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

    # Lógica: Se uma linha contiver "NA BASE" e "PENDENTE", capturamos o nome.
    # O nome está na COLUNA 0 (de acordo com o que identificamos como correto agora).
    
    tecnicos_pendentes = []
    
    for index, row in df.iterrows():
        linha_texto = " ".join(row.fillna('').astype(str)).upper()
        if "NA BASE" in linha_texto and "PENDENTE" in linha_texto:
            # Captura o nome da coluna 0 (ajuste se for outra coluna)
            nome = row[0] 
            if nome and nome != "nan":
                tecnicos_pendentes.append(nome)
    
    tecnicos_unicos = sorted(list(set(tecnicos_pendentes)))
    
    if not tecnicos_unicos:
        st.success("🎉 Todos os técnicos foram liberados para a rua!")
    else:
        st.markdown('<h2 style="color: #005088; text-align: center;">TÉCNICOS PENDENTES</h2>', unsafe_allow_html=True)
        for nome in tecnicos_unicos:
            st.markdown(f'🏃‍♂️ <b>{nome}</b>', unsafe_allow_html=True)
            
else:
    st.error("Arquivo rota_sincronizada.csv não encontrado.")

import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if os.path.exists(ARQUIVO_ROTA_DISCO):
    df = pd.read_csv(ARQUIVO_ROTA_DISCO, header=None, dtype=str)
    
    # 1. CRIAR TABELA DE REFERÊNCIA (Nome -> Supervisor)
    # Procuramos onde o nome aparece junto com o supervisor (qualquer linha que não esteja "Na Base")
    # Na sua foto, o nome está na col 0 e o supervisor está na col 10 (exemplo)
    # Precisamos achar as colunas corretas. Vou assumir posições baseadas na sua estrutura.
    df_ref = df.iloc[1:][[0, 10]].drop_duplicates() # Ajuste o 10 para a coluna correta do supervisor
    df_ref.columns = ['NOME', 'SUPERVISOR']
    df_ref = df_ref.dropna()
    
    # 2. IDENTIFICAR QUEM ESTÁ "NA BASE"
    tecnicos_base = []
    for index, row in df.iterrows():
        linha = " ".join(row.fillna('').astype(str)).upper()
        if "NA BASE" in linha and "PENDENTE" in linha:
            tecnicos_base.append(row[0]) # Nome do técnico
    
    # 3. CRUZAR DADOS
    df_base = pd.DataFrame(tecnicos_base, columns=['NOME']).drop_duplicates()
    df_final = df_base.merge(df_ref, on='NOME', how='left')
    
    # 4. EXIBIR SEPARADO
    st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('### ABC / GUARULHOS')
        for _, row in df_final.iterrows():
            sup = str(row['SUPERVISOR']).upper()
            if 'ALAN' not in sup and 'FRANCISCO' not in sup:
                st.write(f'🏃‍♂️ {row["NOME"]}')
    with col2:
        st.markdown('### SÃO PAULO (SP)')
        for _, row in df_final.iterrows():
            sup = str(row['SUPERVISOR']).upper()
            if 'ALAN' in sup or 'FRANCISCO' in sup:
                st.write(f'🏃‍♂️ {row["NOME"]}')
else:
    st.error("Arquivo rota_sincronizada.csv não encontrado.")

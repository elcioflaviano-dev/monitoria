import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if os.path.exists(ARQUIVO_ROTA_DISCO):
    # 🛠️ Correção: usamos sep=None com engine='python' para o Pandas detectar o separador sozinho
    # Isso evita que vírgulas em endereços quebrem a tabela
    try:
        df = pd.read_csv(ARQUIVO_ROTA_DISCO, sep=None, engine='python', quotechar='"', dtype=str)
    except:
        df = pd.read_csv(ARQUIVO_ROTA_DISCO, sep=';', dtype=str)

    # 🛠️ Correção: Trata colunas duplicadas renomeando-as automaticamente
    cols = []
    for i, col in enumerate(df.columns):
        new_col = f"{col}_{i}" if col in cols else col
        cols.append(new_col)
    df.columns = cols

    # Agora você pode acessar a coluna pelo nome único gerado (ex: "Tipo de Atividade_22")
    # Para saber o nome correto da coluna, adicione isso temporariamente:
    # st.write(df.columns.tolist()) 

    # Filtro de "Na Base" + "pendente" (ajuste os nomes conforme o que aparecer no st.write)
    # Exemplo: df['Status da Atividade_2'] == 'pendente'
    
    st.title("🚀 TÉCNICOS EM BASE")
    st.dataframe(df.head()) # Verifique se agora os dados estão nas colunas certas

else:
    st.error("Arquivo rota_sincronizada.csv não encontrado.")

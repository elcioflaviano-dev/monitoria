import streamlit as st
import pandas as pd

# LINK DIRETO DA SUA PLANILHA GOOGLE
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1kB1YmUuhzHpfN1dLv8PaQn0ipXcHcd6kGKnI3nguT14/export?format=csv"

st.set_page_config(page_title="Gestão de Equipe", layout="centered")

st.markdown('<h1 style="color: #008080; text-align: center;">⚙️ Gestão de Funcionários</h1>', unsafe_allow_html=True)
st.write("Agora a sua lista está integrada com o **Google Sheets** na nuvem de forma permanente!")
st.divider()

try:
    df_equipe = pd.read_csv(URL_PLANILHA)
    
    st.markdown("### 📝 Como fazer alterações na equipe?")
    st.info("Para adicionar, remover ou alterar o nome de técnicos e supervisores, basta abrir a sua planilha no Google Drive, fazer a alteração lá e o painel atualizará sozinho!")
    
    st.divider()
    st.write("### 👁️ Lista Atual Carregada Direto do Google Drive:")
    st.dataframe(df_equipe, use_container_width=True, height=500)

except Exception as e:
    st.error(f"Não foi possível ler os dados da Planilha do Google. Certifique-se de que ela está compartilhada como 'Qualquer pessoa com o link' em modo Leitor. Erro: {e}")

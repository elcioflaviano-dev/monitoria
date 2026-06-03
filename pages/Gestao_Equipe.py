import streamlit as st
import pandas as pd

# LINK DA SUA PLANILHA GOOGLE
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1kB1YmUuhzHpfN1dLv8PaQn0ipXcHcd6kGKnI3nguT14/export?format=csv"

st.set_page_config(page_title="Gestão de Equipe", layout="centered")

st.markdown('<h1 style="color: #008080; text-align: center;">⚙️ Conexão de Funcionários</h1>', unsafe_allow_html=True)
st.write("A sua lista está perfeitamente integrada com o **Google Sheets** na nuvem!")
st.divider()

try:
    df_equipe = pd.read_csv(URL_PLANILHA)
    df_equipe.columns = df_equipe.columns.str.strip().str.upper()
    
    st.markdown("### 📝 Como gerenciar a equipe a partir de agora?")
    st.success("Tudo automatizado! Sempre que precisar de adicionar ou remover técnicos e supervisores, basta abrir a sua planilha direto no Google Drive. O painel e a página de ativar rota atualizam sozinhos na hora.")
    
    st.divider()
    st.write("### 👁️ Lista Atual Carregada Direto do seu Google Sheets:")
    st.dataframe(df_equipe, use_container_width=True, height=500)

except Exception as e:
    st.error(f"Não foi possível ler os dados. Garanta que a planilha está compartilhada como 'Qualquer pessoa com o link' em modo Leitor. Erro: {e}")

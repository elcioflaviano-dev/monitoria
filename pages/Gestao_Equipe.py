import streamlit as st
import pandas as pd

# LINK CONFIGURADO DIRETO PARA A SUA ABA SUPERVISORES (gid=0)
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1kB1YmUuhzHpfN1dLv8PaQn0ipXcHcd6kGKnI3nguT14/export?format=csv&gid=0"

st.set_page_config(page_title="Gestão de Equipe", layout="centered")

st.markdown('<h1 style="color: #008080; text-align: center;">⚙️ Conexão de Funcionários</h1>', unsafe_allow_html=True)
st.write("A sua lista está perfeitamente integrada com o **Google Sheets** na nuvem!")
st.divider()

try:
    df_equipe = pd.read_csv(URL_PLANILHA)
    if df_equipe.empty or len(df_equipe.columns) < 3:
        st.warning("⚠️ Alerta: O Google Sheets enviou um arquivo vazio. Verifique se os dados estão na aba 'supervisores' e se o link contém o 'gid' correto.")
    else:
        df_equipe.columns = df_equipe.columns.str.strip().str.upper()
        st.markdown("### 📝 Como gerenciar a equipe?")
        st.success("Tudo automatizado! Sempre que precisar adicionar ou remover técnicos/supervisores, altere direto no Google Drive. O painel atualiza sozinho na hora.")
        
        st.divider()
        st.write("### 👁️ Lista Atual Carregada Direto do seu Google Sheets:")
        st.dataframe(df_equipe, use_container_width=True, height=500)

except Exception as e:
    st.error(f"Não foi possível ler os dados. Garanta que a planilha está compartilhada como 'Qualquer pessoa com o link' em modo Leitor. Erro: {e}")

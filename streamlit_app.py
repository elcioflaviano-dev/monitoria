import streamlit as st
import pandas as pd

# Configuração da tela para modo amplo (ocupa a tela toda da TV/Monitor)
st.set_page_config(page_title="Painel de Supervisão", layout="wide")

st.title("📊 Painel Operacional de Rotas - ABC & SP")
st.write("---")
st.markdown("### Bem-vindo! Use o menu lateral para acessar os painéis.")

# Função com cache automático para carregar os dados
@st.cache_data(ttl=120)  # Atualiza os dados a cada 2 minutos se a página for recarregada
def carregar_dados():
    # ATENÇÃO: Substitua o link abaixo pelo link da sua planilha "rota"
    # Lembre de mudar o final para /export?format=xlsx
    URL_SHEETS = "https://docs.google.com/spreadsheets/d/SEU_ID_AQUI/export?format=xlsx"
    
    df = pd.read_excel(URL_SHEETS)
    df.columns = df.columns.str.strip() # Remove espaços extras nos nomes das colunas
    return df

try:
    st.session_state['dados_rota'] = carregar_dados()
    st.success("✅ Conexão estabelecida! Dados da planilha 'rota' atualizados.")
    
    total_linhas = len(st.session_state['dados_rota'])
    st.metric(label="Total de Atividades na Base", value=f"{total_linhas} registros")

except Exception as e:
    st.error("❌ Erro ao conectar com o Google Sheets. Verifique o link e as permissões.")
    st.code(e)

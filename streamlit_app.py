import streamlit as st
import pandas as pd

# Configuração da página para modo amplo (ocupa a tela toda da TV/Monitor)
st.set_page_config(page_title="Painel de Supervisão", layout="wide")

st.title("📊 Painel Operacional de Rotas - ABC & SP")
st.write("---")
st.markdown("### Bem-vindo! Use o menu lateral para acessar os painéis.")

# Função com cache automático para carregar os dados sem sobrecarregar o Sheets
@st.cache_data(ttl=120)  # Atualiza os dados a cada 2 minutos se a página for recarregada
def carregar_dados():
    # LINK DA SUA PLANILHA: Substitua abaixo pelo seu link real terminado em /export?format=xlsx
    URL_SHEETS = "https://docs.google.com/spreadsheets/d/1kB1YmUuhzHpfN1dLv8PaQn0ipXcHcd6kGKnI3nguT14/export?format=xlsx"
    
    # Lê a planilha do Google Sheets
    df = pd.read_excel(URL_SHEETS)
    
    # Padroniza os nomes das colunas removendo espaços extras antes ou depois do texto
    df.columns = df.columns.str.strip()
    
    return df

try:
    # Executa a carga dos dados e salva na memória compartilhada do Streamlit
    st.session_state['dados_rota'] = carregar_dados()
    st.success("✅ Conexão estabelecida! Dados da planilha 'rota' atualizados.")
    
    # Mostra um resumo rápido da quantidade de dados carregados
    total_linhas = len(st.session_state['dados_rota'])
    st.metric(label="Total de Atividades na Base", value=f"{total_linhas} registros")

except Exception as e:
    st.error("❌ Erro ao conectar com o Google Sheets. Verifique o link e se as permissões de compartilhamento estão públicas.")
    st.code(e)

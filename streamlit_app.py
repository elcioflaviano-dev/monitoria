import streamlit as st
import pandas as pd

# Configuração da tela para modo amplo (ocupa a tela toda da TV/Monitor)
st.set_page_config(page_title="Painel de Supervisão", layout="wide")

st.title("📊 Painel Operacional de Rotas - ABC & SP")
st.write("---")
st.markdown("### Bem-vindo! Use o menu lateral para acessar os painéis.")

# 🛠️ REMOVE O MENU DO TOPO E AS BARRAS QUE DISPARAM DIÁLOGOS
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden !important;}
    .stAppDeployButton {display:none !important;}
    </style>
""", unsafe_allow_html=True)

# 🛠️ CORREÇÃO CIRÚRGICA: Bloqueia a tecla 'C' sozinha, mas LIBERA o 'Ctrl + C' para copiar!
st.components.v1.html("""
    <script>
    window.parent.document.addEventListener('keydown', function(e) {
        // Se a pessoa estiver apertando Ctrl (ou Command no Mac) junto com o C, deixa copiar normal!
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'c') {
            return; 
        }
        
        # Se for APENAS a tecla 'C' ou 'R' sozinha, bloqueia pro aviso de cache não subir
        if (e.key.toLowerCase() === 'c' || e.key.toLowerCase() === 'r') {
            e.preventDefault();
            e.stopPropagation();
        }
    }, true);
    </script>
""", height=0)

# Função com cache automático para carregar os dados
@st.cache_data(ttl=120)  # Atualiza os dados a cada 2 minutos se a página for recarregada
def carregar_dados():
    # 🚨 LINK REAL DA SUA PLANILHA APLICADO AQUI:
    URL_SHEETS = "https://docs.google.com/spreadsheets/d/1kB1YmUuhzHpfN1dLv8PaQn0ipXcHcd6kGKnI3nguT14/export?format=xlsx"
    
    # 🛠️ CORREÇÃO CRÍTICA: Força a leitura de todas as colunas como TEXTO (String)
    df = pd.read_excel(URL_SHEETS, dtype=str)
    
    # Remove espaços extras nos nomes das colunas
    df.columns = df.columns.str.strip() 
    
    # Preenche células vazias com texto vazio para não quebrar o .str das páginas internas
    df = df.fillna('')
    
    return df

try:
    st.session_state['dados_rota'] = carregar_dados()
    st.success("✅ Conexão estabelecida! Dados da planilha 'rota' atualizados.")
    
    total_linhas = len(st.session_state['dados_rota'])
    st.metric(label="Total de Atividades na Base", value=f"{total_linhas} registros")

except Exception as e:
    st.error("❌ Erro ao conectar com o Google Sheets. Verifique o link e as permissões.")
    st.code(e)

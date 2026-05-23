import streamlit as st

# 1. Configuração da página (Deve ser a primeira coisa do arquivo principal)
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 2. Definição das páginas do seu sistema de forma organizada
paginas = [
    st.Page("pages/1_TEC1.py", title="🏠 Painel Geral TEC1"),
    st.Page("pages/2_TEC1_PENDENTES.py", title="⚠️ Técnicos Pendentes"),
    st.Page("pages/3_CERTIDAO.py", title="📜 Sistema de Certidão"),
    st.Page("pages/4_PAINEL_ABC_SP.py", title="📊 Dashboards ABC SP")
]

# 3. Inicializa o motor de navegação oficial do Streamlit
# Isso desativa completamente o título nativo "streamlit app"
pg = st.navigation(paginas)

# 4. Cria o seu título personalizado com ação de atualizar logo acima do menu
st.sidebar.markdown(
    '<h3 style="font-size: 14px; font-weight: 900; color: #008080; text-align: center; margin-top: 15px; margin-bottom: 15px; letter-spacing: 0.5px;">🔄 CLIQUE PARA ATUALIZAR A BASE</h3>', 
    unsafe_allow_html=True
)
st.sidebar.markdown("---")

# 5. Executa a página que o usuário clicou
pg.run()

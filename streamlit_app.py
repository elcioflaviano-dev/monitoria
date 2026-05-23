import streamlit as st

# Configuração inicial da página principal
st.set_page_config(
    page_title="Monitoria TEC1",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Mensagem de boas-vindas ou redirecionamento na Home
st.markdown('<h1 style="font-size: 36px; font-weight: 900; color: #008080; text-align: center; margin-top: 50px;">Monitoria Operacional TEC1</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666; font-size: 16px;">Utilize o menu lateral para navegar entre os painéis, listas de pendências e relatórios de certidão.</p>', unsafe_allow_html=True)

st.markdown("---")

# Exibe um resumo rápido ou orientações para a operação
col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown("### 🏠 Painel Geral")
        st.write("Visualização em tempo real dos status de Pendentes, Em Rota e Iniciados divididos por regiões e supervisores.")

with col2:
    with st.container(border=True):
        st.markdown("### ⚠️ Pendentes TV")
        st.write("Modo de exibição focado em alertas de técnicos com contratos parados na janela de atendimento atual.")

with col3:
    with st.container(border=True):
        st.markdown("### 📜 Certidões")
        st.write("Sistema de auditoria para checar e gravar a validação dos contratos concluídos em campo.")

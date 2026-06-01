import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# Inicializa as listas dinâmicas se não existirem
if "novos_sp" not in st.session_state: st.session_state["novos_sp"] = []
if "novos_abc" not in st.session_state: st.session_state["novos_abc"] = []

# Listas oficiais iniciais
TECNICOS_SP = [...] # (Insira a lista completa que te passei antes aqui)
TECNICOS_ABC = [...] # (Insira a lista completa que te passei antes aqui)

st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

# --- CAMPO PARA NOVO NOME ---
with st.expander("➕ Incluir Novo Técnico Manualmente"):
    col_a, col_b, col_c = st.columns([2, 1, 1])
    novo_nome = col_a.text_input("Nome do Técnico:").upper().strip()
    nova_base = col_b.selectbox("Base:", ["SP", "ABC"])
    if col_c.button("Adicionar"):
        if novo_nome:
            if nova_base == "SP": st.session_state["novos_sp"].append(novo_nome)
            else: st.session_state["novos_abc"].append(novo_nome)
            st.rerun()

if 'df_rota_ativa' in st.session_state and st.session_state['df_rota_ativa'] is not None:
    df = st.session_state['df_rota_ativa']
    df_tela = df[
        (df['Tipo de Atividade.1'].astype(str).str.contains('NA BASE', na=False, case=False)) & 
        (df['Status da Atividade'].astype(str).str.contains('PENDENTE', na=False, case=False))
    ].copy()

    nomes_na_base = sorted(df_tela['Recurso'].unique().tolist())
    
    # Consolidar listas oficiais + nomes incluídos manualmente
    lista_sp_final = [n.upper() for n in TECNICOS_SP] + [n.upper() for n in st.session_state["novos_sp"]]
    lista_abc_final = [n.upper() for n in TECNICOS_ABC] + [n.upper() for n in st.session_state["novos_abc"]]

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('### 🏢 ABC / GUARULHOS')
        for nome in nomes_na_base:
            if nome.upper() in lista_abc_final or nome.upper() not in lista_sp_final:
                st.markdown(f'🏃‍♂️ {nome}')
                
    with col2:
        st.markdown('### 🏙️ SÃO PAULO (SP)')
        for nome in nomes_na_base:
            if nome.upper() in lista_sp_final:
                st.markdown(f'🏃‍♂️ {nome}')
else:
    st.error("⚠️ Nenhum dado carregado na página inicial.")

import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# (Mantenha as suas listas LISTA_SP_FIXA e LISTA_ABC_FIXA aqui como no código anterior)

st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

if 'df_rota_ativa' in st.session_state and st.session_state['df_rota_ativa'] is not None:
    df = st.session_state['df_rota_ativa']
    df_tela = df[
        (df['Tipo de Atividade.1'].astype(str).str.contains('NA BASE', na=False, case=False)) & 
        (df['Status da Atividade'].astype(str).str.contains('PENDENTE', na=False, case=False))
    ].copy()

    nomes_na_base = sorted(df_tela['Recurso'].unique().tolist())
    
    lista_sp = [str(n).upper() for n in LISTA_SP_FIXA] + [str(n).upper() for n in st.session_state.get("novos_sp", [])]
    lista_abc = [str(n).upper() for n in LISTA_ABC_FIXA] + [str(n).upper() for n in st.session_state.get("novos_abc", [])]

    # Separar os nomes em listas para distribuir nas 4 colunas
    nomes_abc = [n for n in nomes_na_base if str(n).upper() in lista_abc or str(n).upper() not in lista_sp]
    nomes_sp = [n for n in nomes_na_base if str(n).upper() in lista_sp]

    # Dividir as listas ao meio para colocar em duas colunas cada
    mid_abc = len(nomes_abc) // 2
    mid_sp = len(nomes_sp) // 2

    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown('### 🏢 ABC (1/2)')
        for nome in nomes_abc[:mid_abc]: st.markdown(f'🏃‍♂️ {nome}')
    with c2:
        st.markdown('### 🏢 ABC (2/2)')
        for nome in nomes_abc[mid_abc:]: st.markdown(f'🏃‍♂️ {nome}')
    with c3:
        st.markdown('### 🏙️ SP (1/2)')
        for nome in nomes_sp[:mid_sp]: st.markdown(f'🏃‍♂️ {nome}')
    with c4:
        st.markdown('### 🏙️ SP (2/2)')
        for nome in nomes_sp[mid_sp:]: st.markdown(f'🏃‍♂️ {nome}')

    # --- INCLUSAO MANUAL NA PARTE DE BAIXO ---
    st.divider()
    with st.expander("➕ Incluir Novo Técnico (Na parte inferior)"):
        c_a, c_b, c_c = st.columns([2, 1, 1])
        nome_input = c_a.text_input("Nome do Técnico:").upper().strip()
        base_input = c_b.selectbox("Base:", ["SP", "ABC"])
        if c_c.button("Adicionar"):
            if nome_input:
                if base_input == "SP": st.session_state["novos_sp"].append(nome_input)
                else: st.session_state["novos_abc"].append(nome_input)
                st.rerun()

else:
    st.error("⚠️ Nenhum dado de rota carregado.")

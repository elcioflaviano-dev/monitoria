import streamlit as st
import pandas as pd

# LINK DIRETO DA SUA PLANILHA GOOGLE
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1kB1YmUuhzHpfN1dLv8PaQn0ipXcHcd6kGKnI3nguT14/export?format=csv"

st.set_page_config(layout="wide")

try:
    df_equipe = pd.read_csv(URL_PLANILHA)
    LISTA_SP_FIXA = df_equipe[(df_equipe["FUNCAO"].str.strip().str.upper() == "TECNICO") & (df_equipe["BASE"].str.strip().str.upper() == "SP")]["NOME"].dropna().tolist()
    LISTA_ABC_FIXA = df_equipe[(df_equipe["FUNCAO"].str.strip().str.upper() == "TECNICO") & (df_equipe["BASE"].str.strip().str.upper() == "ABC")]["NOME"].dropna().tolist()
except:
    st.error("⚠️ Erro ao carregar a lista de equipe centralizada vinda do Google Sheets.")
    LISTA_SP_FIXA, LISTA_ABC_FIXA = [], []

if "novos_sp" not in st.session_state: st.session_state["novos_sp"] = []
if "novos_abc" not in st.session_state: st.session_state["novos_abc"] = []

st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

if 'df_rota_ativa' in st.session_state and st.session_state['df_rota_ativa'] is not None:
    df = st.session_state['df_rota_ativa']
    col_tipo = 'Tipo de Atividade.1' if 'Tipo de Atividade.1' in df.columns else ('Tipo de Atividade' if 'Tipo de Atividade' in df.columns else None)
    col_status = 'Status da Atividade' if 'Status da Atividade' in df.columns else 'STATUS_ATIVIDADE'

    if col_tipo and col_status:
        df_tela = df[(df[col_tipo].astype(str).str.contains('NA BASE', na=False, case=False)) & (df[col_status].astype(str).str.contains('PENDENTE', na=False, case=False))].copy()
        nomes_na_base = sorted(df_tela['Recurso'].dropna().unique().tolist())
        
        lista_sp = [n.upper() for n in LISTA_SP_FIXA] + [n.upper() for n in st.session_state["novos_sp"]]
        lista_abc = [n.upper() for n in LISTA_ABC_FIXA] + [n.upper() for n in st.session_state["novos_abc"]]

        nomes_abc = [n for n in nomes_na_base if str(n).upper() in lista_abc or str(n).upper() not in lista_sp]
        nomes_sp = [n for n in nomes_na_base if str(n).upper() in lista_sp]

        c1, c2, c3, c4 = st.columns(4)
        mid_abc = len(nomes_abc) // 2
        mid_sp = len(nomes_sp) // 2
        
        with c1:
            st.markdown('### 🏢 ABC (1/2)')
            for n in nomes_abc[:mid_abc]: st.markdown(f'🏃‍♂️ {n}')
        with c2:
            st.markdown('### 🏢 ABC (2/2)')
            for n in nomes_abc[mid_abc:]: st.markdown(f'🏃‍♂️ {n}')
        with c3:
            st.markdown('### 🏙️ SP (1/2)')
            for n in nomes_sp[:mid_sp]: st.markdown(f'🏃‍♂️ {n}')
        with c4:
            st.markdown('### 🏙️ SP (2/2)')
            for n in nomes_sp[mid_sp:]: st.markdown(f'🏃‍♂️ {n}')

        st.divider()
        with st.expander("➕ Incluir Novo Técnico Temporário (Só para hoje)"):
            c_a, c_b, c_c = st.columns([2, 1, 1])
            nome_i = c_a.text_input("Nome:").upper()
            base_i = c_b.selectbox("Base:", ["SP", "ABC"])
            if c_c.button("Adicionar"):
                if nome_i:
                    if base_i == "SP": st.session_state["novos_sp"].append(nome_i)
                    else: st.session_state["novos_abc"].append(nome_i)
                    st.rerun()
    else: st.error("⚠️ Colunas não encontradas.")
else: st.error("⚠️ Nenhum dado carregado na rota ativa.")

import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# CSS DE LIMPEZA
st.markdown("""
    <style>
    [data-testid="stHeader"], .stDeployButton, footer, #MainMenu, [data-testid="stSidebar"] { visibility: hidden !important; }
    .stApp { background-color: #ffffff !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

# 1. Recupera o dataframe da sessão (o mesmo que a TEC1 usa)
if 'df_rota_ativa' not in st.session_state or st.session_state['df_rota_ativa'] is None:
    st.error("⚠️ Nenhum dado carregado. Por favor, acesse o Painel Inicial primeiro para sincronizar os dados.")
    st.stop()

df = st.session_state['df_rota_ativa'].copy()
df.columns = [str(c).strip() for c in df.columns]

# 2. DETECÇÃO DINÂMICA DE COLUNAS (A lógica robusta da TEC1)
# Procura as colunas independente do nome exato, buscando palavras-chave
col_recurso = 'Recurso' # Como visto no seu print
col_tipo = next((c for c in df.columns if 'TIPO' in c.upper() and 'ATIVIDADE3' in c.upper()), None)
col_status = next((c for c in df.columns if 'STATUS' in c.upper()), None)

if col_tipo and col_status:
    # 3. LIMPEZA E FILTRAGEM (Iguais à lógica da TEC1)
    df_tela = df[
        (df[col_tipo].fillna('').astype(str).str.strip().str.lower() == 'na base') & 
        (df[col_status].fillna('').astype(str).str.strip().str.lower() == 'pendente')
    ].copy()

    # Remover duplicados pelo recurso
    nomes_na_base = sorted(df_tela[col_recurso].dropna().unique().tolist())
    
    # Listas fixas para organizar
    LISTA_SP = [n.upper() for n in ["ABNER MAKALAS MARTINS PAULINO", "ADRIANO JOSE DE OLIVEIRA", "ALYSON CAMPOS ANDRADE", "ANTONIO CICERO PEREIRA DA SILVA", "BRUNO CARLOS COUTO CRUZ", "BRUNO MIRANDA SANTOS", "CARLIELTON FERREIRA SANTOS", "CLAYTON IONAMINE", "Edcarlos Pereira de Jesus", "GETULIO DOS SANTOS CAFE", "Glemerson Lima De Souza", "GUILHERME DE OLIVEIRA DANTAS", "ILTON OLIVEIRA CORREIA", "ISAQUE INACIO BARRETO MENDONCA", "JANAILSON RICARDO FERREIRA DOS SANTOS", "JHONNY DORNELLES DE ALMEIDA", "JOSE CARLOS DA SILVA SANTOS", "LUCAS DE OLIVEIRA SANTOS", "MARCOS VINICIUS BARRETO", "NICHOLAS CZAR LEITAO SANTOS", "RAFAEL GOMES PEREIRA", "RINALDO ANTONIO DA SILVA JUNIOR", "THIAGO ARAUJO SANTOS", "VICENTE RODRIGUES DOS SANTOS", "VINICIUS ARAUJO DA SILVA", "VINICIUS SILVA FARIAS", "VITORIA FERREIRA", "Alan Cesar Cardoso", "ALEXANDRE ROGERIO GONCALVES DE MACEDO", "BARBARA CRISTINA DOS SANTOS PINTO", "BRUNA DA SILVA GOMES FERREIRA", "DOUGLAS WILLIAM SANTOS", "EMERSON DA SILVA", "FABIO OLIVEIRA CAMPOS FARIAS", "FABIO XAVIER CATAO", "FELIPE DE SOUZA OLIVEIRA", "FERNANDO LOPES", "FRANCISCO ALVES FILHO", "FRANKLIM ALVES MAIA", "GUILHERME SILVA DIAS CASTRO", "HELVIO STAFF", "JOAO CARLOS MIRON", "JOSE MARCIO DA SILVA VELOSO", "LUCAS FREIRIA PINTO", "MANOELA MIRANDA", "MATHEUS DOS SANTOS OLIVEIRA", "PEDRO LUIZ FEREEIRA CORREA", "PEDRO OLIVEIRA CARLOS DA SILVA", "RAFAELA SANTOS SILVA", "ROBSON SANTIAGO DA LUZ", "TIAGO MEIRA DA SILVA", "VALMIR RAMOS", "VITOR OLIVEIRA DA SILVA", "WELLINGTON GOMES DE OLIVEIRA", "TAILSON JUAN SANTOS DA CONCEICAO", "DIEGO FRAGOSO DE BRITO", "ALYSON ALBERTO MARTINS", "AUGUSTO MOREIRA DA SILVA", "ENDERSON CLEITON SOUZA CRUZ", "CARLOS SEBASTIAO MORAIS", "EZIEL DE OLIVEIRA BARROS", "VICTOR BORGES ALVES", "MATHEUS CARDOSO DE OLIVEIRA", "ROGERIO AFONSO DA SILVA", "KAIO NASCIMENTO ALVES DOS SANTOS", "KELVIN RIBEIRO BENTO DA COSTA", "MARCELO BUENO SEGURA", "MAYKON RIBEIRO GUIMARAES", "THIAGO JOSE ASSUNCAO", "GUSTAVO SANTOS SANT ANA"]]

    nomes_abc = [n for n in nomes_na_base if n.upper() not in LISTA_SP]
    nomes_sp = [n for n in nomes_na_base if n.upper() in LISTA_SP]

    # Exibição (4 colunas)
    st.markdown(f"<h4 style='text-align: center; color: #555;'>Total na Base: {len(nomes_na_base)}</h4>", unsafe_allow_html=True)
    st.divider()
    
    c1, c2, c3, c4 = st.columns(4)
    for i, (lista, col, tit) in enumerate(zip(
        [nomes_abc[:(len(nomes_abc)+1)//2], nomes_abc[(len(nomes_abc)+1)//2:], nomes_sp[:(len(nomes_sp)+1)//2], nomes_sp[(len(nomes_sp)+1)//2:]],
        [c1, c2, c3, c4],
        ["🏢 ABC (1/2)", "🏢 ABC (2/2)", "🏙️ SP (1/2)", "🏙️ SP (2/2)"]
    )):
        with col:
            st.markdown(f'### {tit}')
            for n in lista: st.markdown(f'🏃‍♂️ **{n}**')
            
else:
    st.error("Erro: As colunas necessárias não foram encontradas no arquivo.")
    st.write("Colunas disponíveis:", list(df.columns))

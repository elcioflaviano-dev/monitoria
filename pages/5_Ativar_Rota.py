import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# Lista de técnicos de São Paulo (Alan e Francisco)
TECNICOS_SP = [
    "ABNER MAKALAS MARTINS PAULINO", "ADRIANO JOSE DE OLIVEIRA", "ALYSON CAMPOS ANDRADE",
    "ANTONIO CICERO PEREIRA DA SILVA", "BRUNO CARLOS COUTO CRUZ", "BRUNO MIRANDA SANTOS",
    "CARLIELTON FERREIRA SANTOS", "CLAYTON IONAMINE", "EDCARLOS PEREIRA DE JESUS",
    "GETULIO DOS SANTOS CAFE", "GLEMERSON LIMA DE SOUZA", "GUILHERME DE OLIVEIRA DANTAS",
    "ILTON OLIVEIRA CORREIA", "ISAQUE INACIO BARRETO MENDONCA", "JANAILSON RICARDO FERREIRA DOS SANTOS",
    "JHONNY DORNELLES DE ALMEIDA", "JOSE CARLOS DA SILVA SANTOS", "LUCAS DE OLIVEIRA SANTOS",
    "MARCOS VINICIUS BARRETO", "NICHOLAS CZAR LEITAO SANTOS", "RAFAEL GOMES PEREIRA",
    "RINALDO ANTONIO DA SILVA JUNIOR", "THIAGO ARAUJO SANTOS", "VICENTE RODRIGUES DOS SANTOS",
    "VINICIUS ARAUJO DA SILVA", "VINICIUS SILVA FARIAS", "VITORIA FERREIRA", "TAILSON JUAN SANTOS DA CONCEICAO",
    "ALAN CESAR CARDOSO", "ALEXANDRE ROGERIO GONCALVES DE MACEDO", "BARBARA CRISTINA DOS SANTOS PINTO",
    "BRUNA DA SILVA GOMES FERREIRA", "DOUGLAS WILLIAM SANTOS", "EMERSON DA SILVA",
    "FABIO OLIVEIRA CAMPOS FARIAS", "FABIO XAVIER CATAO", "FELIPE DE SOUZA OLIVEIRA",
    "FERNANDO LOPES", "FRANCISCO ALVES FILHO", "FRANKLIM ALVES MAIA",
    "GUILHERME SILVA DIAS CASTRO", "HELVIO STAFF", "JOAO CARLOS MIRON",
    "JOSE MARCIO DA SILVA VELOSO", "LUCAS FREIRIA PINTO", "MANOELA MIRANDA",
    "MATHEUS DOS SANTOS OLIVEIRA", "PEDRO LUIZ FEREEIRA CORREA", "PEDRO OLIVEIRA CARLOS DA SILVA",
    "RAFAELA SANTOS SILVA", "ROBSON SANTIAGO DA LUZ", "TIAGO MEIRA DA SILVA",
    "VALMIR RAMOS", "VITOR OLIVEIRA DA SILVA", "WELLINGTON GOMES DE OLIVEIRA", "DIEGO FRAGOSO DE BRITO"
]

st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

if 'df_rota_ativa' in st.session_state and st.session_state['df_rota_ativa'] is not None:
    df = st.session_state['df_rota_ativa']
    
    # Filtro automático
    df_tela = df[
        (df['Tipo de Atividade.1'].astype(str).str.contains('NA BASE', na=False, case=False)) & 
        (df['Status da Atividade'].astype(str).str.contains('PENDENTE', na=False, case=False))
    ].copy()

    nomes_na_base = sorted(df_tela['Recurso'].unique().tolist())

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('### 🏢 ABC / GUARULHOS')
        for nome in nomes_na_base:
            # Se não estiver na lista de SP, é ABC
            if nome.upper() not in [n.upper() for n in TECNICOS_SP]:
                st.markdown(f'🏃‍♂️ {nome}')
                
    with col2:
        st.markdown('### 🏙️ SÃO PAULO (SP)')
        for nome in nomes_na_base:
            # Se estiver na lista de SP, é SP
            if nome.upper() in [n.upper() for n in TECNICOS_SP]:
                st.markdown(f'🏃‍♂️ {nome}')
else:
    st.error("⚠️ Nenhum dado carregado. Vá na página inicial e suba o arquivo.")

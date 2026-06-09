import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# CSS PARA LIMPEZA DA INTERFACE (REMOVE ATALHOS DO STREAMLIT)
st.markdown("""
    <style>
    [data-testid="stHeader"] { visibility: hidden !important; }
    .stDeployButton { display: none !important; }
    footer { visibility: hidden !important; }
    #MainMenu { visibility: hidden !important; }
    </style>
""", unsafe_allow_html=True)

# 1. LISTAS FIXAS (DECLARADAS DENTRO DA PÁGINA PARA SEGURANÇA)
LISTA_SP_FIXA = [
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

LISTA_ABC_FIXA = [
    "ADRIEL ALEXANDER DE LIMA", "AIRON HENRIQUE FERREIRA MINA", "ALAN RODRIGUES COSTA", "ALEX BERNARDES DA SILVA", "ALINE CAMARGO PIRES", 
    "AMANDA CAROLINE DOS SANTOS", "ANA LUISA CULAU SILVA", "ANDERSON MARCELO LOPES DOS SANTOS", "AUGUSTO ERNANDES DA SILVA", "BRUNO MARTINS AVELINO", 
    "CARLOS ALBERTO LIMA REBOUÇAS", "DANIEL SOUZA OLIVEIRA", "DANILO FERREIRA LIMA", "DEBORA BENEVENUTO PEREIRA", "DOMINGOS PEREIRA DA SILVA", 
    "EDSON JAIRO DE ALMEIDA SOUSA", "EDUARDO FERNANDES BERNARDO DE MELO", "ELIAS AGUIAR LOPES", "ENOQUE FERREIRA SANTOS FILHO", "ERICK PAULO FERREIRA DA SILVA", 
    "ERIK CASSIMIRO DA SILVA GOMES", "ESTEVAM MATEUS GONCALVES", "FABIO OLIVEIRA MOURA", "FELIPI ANTONIO DA SILVA", "FRANCISCO IGOR SOARES DA SILVA", 
    "HELTON LIMA DE QUEIROZ", "IGOR DA SILVA VAYDA", "JAKSON DE JESUS E SILVA", "JEANDERSON SOUZA BERTO DA SILVA", "JEFFERSON BRADAO BASTOS", 
    "JEFFERSON FRANCISCO DA SILVA", "JOANDERSON LOPES DA CONCEIÇÃO", "JOAO BATISTA DE LIMA TOME", "JUSCIELIO LIRA DE OLIVEIRA", "LEANDRO SOARES DA SILVA", 
    "LEONARDO BESERRA DOS SANTOS", "LUCAS SILVA DE LIMA", "LUIS HENRIQUE GOMES DA SILVA", "MARCOS VINICIUS OLIVEIRA GOVEIA", "NATALIA SANT ANA VELASCO", 
    "MATHEUS BOAVENTURA DA SILVA", "OSCLEY FRANCA DE SOUSA", "ODIRLEI APARECIDO PIERETI", "PATRICIA DE ARAUJO RAMALHO", "RENATO FUTRO ROSSI", 
    "PAULO CESAR BATISTA DE SOUSA", "RAFAEL DOS ANJOS BATISTA ONOFRE", "SIDNEY ROSENDO DA SILVA", "RICARDO SANTOS", "RODRIGO FEITOZA DA SILVA", 
    "VICTOR MENDES DOS SANTOS", "SILAS DA SILVA NASCIMENTO", "YURI URCESINO COSTA", "WESLAYNE CELINA FERREIRA SILVA", "DANIEL AUGUSTO PEREIRA", 
    "JULIO CESAR SILVA DOS SANTOS", "EDER SALES MONTEIRO", "ANTONIO WESLEY HOLANDA DA SILVA", "MAICON JORDAN PEDRO SANTOS GARCEZ", "LUIS GUSTAVO CECCONELLO", 
    "CLEBER FERREIRA SANTOS", "ALEX DE JESUS FREIRE", "ANTHONY HULLY PEREIRA DIAS", "ANTONIO CHARLES MARINHO", "ARLAN DUARTE NASCIMENTO", "EVERTON ALVES", 
    "IGOR DAVID DE MARCHI", "JAZIEL DOS SANTOS SILVA", "KAUAN PASCHOAL", "LUCAS SILVA SOBRINHO", "NICOLAS CALEGARI STARCHARVSKI", "RENATO ESPERANÇA", 
    "ROBERVAL LEAO DE ALBUQUERQUE", "RYAN PIMENTEL BARROS", "SAMUEL AUGUSTO DE OLIVEIRA", "VITOR MATOS DE ALMEIDA"

]

# Inicializa session_state
if "novos_sp" not in st.session_state: st.session_state["novos_sp"] = []
if "novos_abc" not in st.session_state: st.session_state["novos_abc"] = []

st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

if 'df_rota_ativa' in st.session_state and st.session_state['df_rota_ativa'] is not None:
    df = st.session_state['df_rota_ativa']
    df_tela = df[
        (df['Tipo de Atividade.1'].astype(str).str.contains('NA BASE', na=False, case=False)) & 
        (df['Status da Atividade'].astype(str).str.contains('PENDENTE', na=False, case=False))
    ].copy()

    nomes_na_base = sorted(df_tela['Recurso'].unique().tolist())
    
    # Consolida listas usando a variável definida acima
    lista_sp = [n.upper() for n in LISTA_SP_FIXA] + [n.upper() for n in st.session_state["novos_sp"]]
    lista_abc = [n.upper() for n in LISTA_ABC_FIXA] + [n.upper() for n in st.session_state["novos_abc"]]

    # Distribuição em 4 colunas
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
    with st.expander("➕ Incluir Novo Técnico"):
        c_a, c_b, c_c = st.columns([2, 1, 1])
        nome_i = c_a.text_input("Nome:").upper()
        base_i = c_b.selectbox("Base:", ["SP", "ABC"])
        if c_c.button("Adicionar"):
            if nome_i:
                if base_i == "SP": st.session_state["novos_sp"].append(nome_i)
                else: st.session_state["novos_abc"].append(nome_i)
                st.rerun()
else:
    st.error("⚠️ Nenhum dado carregado.")

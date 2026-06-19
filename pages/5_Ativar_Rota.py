import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# CSS PARA LIMPEZA
st.markdown("""
    <style>
    [data-testid="stHeader"], .stDeployButton, footer, #MainMenu, [data-testid="stSidebar"] { visibility: hidden !important; }
    .stApp { background-color: #ffffff !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

# LISTAS FIXAS
LISTA_SP_FIXA = ["ABNER MAKALAS MARTINS PAULINO", "ADRIANO JOSE DE OLIVEIRA", "ALYSON CAMPOS ANDRADE", "ANTONIO CICERO PEREIRA DA SILVA", "BRUNO CARLOS COUTO CRUZ", "BRUNO MIRANDA SANTOS", "CARLIELTON FERREIRA SANTOS", "CLAYTON IONAMINE", "Edcarlos Pereira de Jesus", "GETULIO DOS SANTOS CAFE", "Glemerson Lima De Souza", "GUILHERME DE OLIVEIRA DANTAS", "ILTON OLIVEIRA CORREIA", "ISAQUE INACIO BARRETO MENDONCA", "JANAILSON RICARDO FERREIRA DOS SANTOS", "JHONNY DORNELLES DE ALMEIDA", "JOSE CARLOS DA SILVA SANTOS", "LUCAS DE OLIVEIRA SANTOS", "MARCOS VINICIUS BARRETO", "NICHOLAS CZAR LEITAO SANTOS", "RAFAEL GOMES PEREIRA", "RINALDO ANTONIO DA SILVA JUNIOR", "THIAGO ARAUJO SANTOS", "VICENTE RODRIGUES DOS SANTOS", "VINICIUS ARAUJO DA SILVA", "VINICIUS SILVA FARIAS", "VITORIA FERREIRA", "Alan Cesar Cardoso", "ALEXANDRE ROGERIO GONCALVES DE MACEDO", "BARBARA CRISTINA DOS SANTOS PINTO", "BRUNA DA SILVA GOMES FERREIRA", "DOUGLAS WILLIAM SANTOS", "EMERSON DA SILVA", "FABIO OLIVEIRA CAMPOS FARIAS", "FABIO XAVIER CATAO", "FELIPE DE SOUZA OLIVEIRA", "FERNANDO LOPES", "FRANCISCO ALVES FILHO", "FRANKLIM ALVES MAIA", "GUILHERME SILVA DIAS CASTRO", "HELVIO STAFF", "JOAO CARLOS MIRON", "JOSE MARCIO DA SILVA VELOSO", "LUCAS FREIRIA PINTO", "MANOELA MIRANDA", "MATHEUS DOS SANTOS OLIVEIRA", "PEDRO LUIZ FEREEIRA CORREA", "PEDRO OLIVEIRA CARLOS DA SILVA", "RAFAELA SANTOS SILVA", "ROBSON SANTIAGO DA LUZ", "TIAGO MEIRA DA SILVA", "VALMIR RAMOS", "VITOR OLIVEIRA DA SILVA", "WELLINGTON GOMES DE OLIVEIRA", "TAILSON JUAN SANTOS DA CONCEICAO", "DIEGO FRAGOSO DE BRITO", "ALYSON ALBERTO MARTINS", "AUGUSTO MOREIRA DA SILVA", "ENDERSON CLEITON SOUZA CRUZ", "CARLOS SEBASTIAO MORAIS", "EZIEL DE OLIVEIRA BARROS", "VICTOR BORGES ALVES", "MATHEUS CARDOSO DE OLIVEIRA", "ROGERIO AFONSO DA SILVA", "KAIO NASCIMENTO ALVES DOS SANTOS", "KELVIN RIBEIRO BENTO DA COSTA", "MARCELO BUENO SEGURA", "MAYKON RIBEIRO GUIMARAES", "THIAGO JOSE ASSUNCAO", "GUSTAVO SANTOS SANT ANA"]
LISTA_ABC_FIXA = ["ADRIEL ALEXANDER DE LIMA", "AIRON HENRIQUE FERREIRA MINA", "ALAN RODRIGUES COSTA", "ALEX BERNARDES DA SILVA", "ALINE CAMARGO PIRES", "AMANDA CAROLINE DOS SANTOS", "ANA LUISA CULAU SILVA", "ANDERSON MARCELO LOPES DOS SANTOS", "AUGUSTO ERNANDES DA SILVA", "BRUNO MARTINS AVELINO", "CARLOS ALBERTO LIMA REBOUÇAS", "DANIEL SOUZA OLIVEIRA", "DANILO FERREIRA LIMA", "DEBORA BENEVENUTO PEREIRA", "DOMINGOS PEREIRA DA SILVA", "EDSON JAIRO DE ALMEIDA SOUSA", "EDUARDO FERNANDES BERNARDO DE MELO", "ELIAS AGUIAR LOPES", "ENOQUE FERREIRA SANTOS FILHO", "ERICK PAULO FERREIRA DA SILVA", "ERIK CASSIMIRO DA SILVA GOMES", "ESTEVAM MATEUS GONCALVES", "FABIO OLIVEIRA MOURA", "FELIPI ANTONIO DA SILVA", "FRANCISCO IGOR SOARES DA SILVA", "HELTON LIMA DE QUEIROZ", "IGOR DA SILVA VAYDA", "JAKSON DE JESUS E SILVA", "JEANDERSON SOUZA BERTO DA SILVA", "JEFFERSON BRADAO BASTOS", "JEFFERSON FRANCISCO DA SILVA", "JOANDERSON LOPES DA CONCEIÇÃO", "JOAO BATISTA DE LIMA TOME", "JUSCIELIO LIRA DE OLIVEIRA", "LEANDRO SOARES DA SILVA", "LEONARDO BESERRA DOS SANTOS", "LUCAS SILVA DE LIMA", "LUIS HENRIQUE GOMES DA SILVA", "MARCOS VINICIUS OLIVEIRA GOVEIA", "NATALIA SANT ANA VELASCO", "MATHEUS BOAVENTURA DA SILVA", "OSCLEY FRANCA DE SOUSA", "ODIRLEI APARECIDO PIERETI", "PATRICIA DE ARAUJO RAMALHO", "RENATO FUTRO ROSSI", "PAULO CESAR BATISTA DE SOUSA", "RAFAEL DOS ANJOS BATISTA ONOFRE", "SIDNEY ROSENDO DA SILVA", "RICARDO SANTOS", "RODRIGO FEITOZA DA SILVA", "VICTOR MENDES DOS SANTOS", "SILAS DA SILVA NASCIMENTO", "YURI URCESINO COSTA", "WESLAYNE CELINA FERREIRA SILVA", "DANIEL AUGUSTO PEREIRA", "JULIO CESAR SILVA DOS SANTOS", "EDER SALES MONTEIRO", "ANTONIO WESLEY HOLANDA DA SILVA", "MAICON JORDAN PEDRO SANTOS GARCEZ", "LUIS GUSTAVO CECCONELLO", "CLEBER FERREIRA SANTOS", "ALEX DE JESUS FREIRE", "ANTHONY HULLY PEREIRA DIAS", "ANTONIO CHARLES MARINHO", "ARLAN DUARTE NASCIMENTO", "EVERTON ALVES", "IGOR DAVID DE MARCHI", "JAZIEL DOS SANTOS SILVA", "KAUAN PASCHOAL", "LUCAS SILVA SOBRINHO", "NICOLAS CALEGARI STARCHARVSKI", "RENATO ESPERANÇA", "ROBERVAL LEAO DE ALBUQUERQUE", "RYAN PIMENTEL BARROS", "SAMUEL AUGUSTO DE OLIVEIRA", "VITOR MATOS DE ALMEIDA"]

if "novos_sp" not in st.session_state: st.session_state["novos_sp"] = []
if "novos_abc" not in st.session_state: st.session_state["novos_abc"] = []

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if os.path.exists(ARQUIVO_ROTA_DISCO):
    df = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    # DETECÇÃO AUTOMÁTICA DAS COLUNAS
    col_recurso = next((c for c in df.columns if any(x in c for x in ['RECURSO', 'NOME', 'TÉCN'])), df.columns[0])
    col_tipo = next((c for c in df.columns if 'TIPO' in c), None)
    col_status = next((c for c in df.columns if 'STATUS' in c), None)
    
    if col_tipo and col_status:
        # Normalização dos dados para filtro robusto
        df['TIPO_NORM'] = df[col_tipo].fillna('').astype(str).str.upper()
        df['STATUS_NORM'] = df[col_status].fillna('').astype(str).str.upper()
        
        # Filtro: Contém "BASE" e "PEND" (independente do nome exato da coluna)
        df_tela = df[
            df['TIPO_NORM'].str.contains('BASE', na=False) & 
            df['STATUS_NORM'].str.contains('PEND', na=False)
        ].copy()

        nomes_na_base = sorted(df_tela[col_recurso].dropna().unique().tolist())
        
        # Consolida listas
        lista_sp = [n.upper() for n in LISTA_SP_FIXA] + [n.upper() for n in st.session_state["novos_sp"]]
        lista_abc = [n.upper() for n in LISTA_ABC_FIXA] + [n.upper() for n in st.session_state["novos_abc"]]

        nomes_abc = [n for n in nomes_na_base if str(n).upper() in lista_abc or str(n).upper() not in lista_sp]
        nomes_sp = [n for n in nomes_na_base if str(n).upper() in lista_sp]

        c1, c2, c3, c4 = st.columns(4)
        for i, (lista, col, tit) in enumerate(zip(
            [nomes_abc[:(len(nomes_abc)+1)//2], nomes_abc[(len(nomes_abc)+1)//2:], nomes_sp[:(len(nomes_sp)+1)//2], nomes_sp[(len(nomes_sp)+1)//2:]],
            [c1, c2, c3, c4],
            ["🏢 ABC (1/2)", "🏢 ABC (2/2)", "🏙️ SP (1/2)", "🏙️ SP (2/2)"]
        )):
            with col:
                st.markdown(f'### {tit}')
                for n in lista: st.markdown(f'🏃‍♂️ {n}')
    else:
        st.error(f"⚠️ Colunas não encontradas automaticamente. Colunas disponíveis: {list(df.columns)}")
else:
    st.error("⚠️ 'rota_sincronizada.csv' não encontrado.")

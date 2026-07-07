import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# CSS: Mantém o menu lateral visível e interface limpa
st.markdown("""
    <style>
    .stDeployButton { display: none !important; }
    footer { visibility: hidden !important; }
    .stApp { background-color: #ffffff !important; }
    </style>
""", unsafe_allow_html=True)

# LISTAS FIXAS
LISTA_SP_FIXA = ["ABNER MAKALAS MARTINS PAULINO", "ADRIANO JOSE DE OLIVEIRA", "ALYSON CAMPOS ANDRADE", "ANTONIO CICERO PEREIRA DA SILVA", "BRUNO CARLOS COUTO CRUZ", "BRUNO MIRANDA SANTOS", "CARLIELTON FERREIRA SANTOS", "CLAYTON IONAMINE", "Edcarlos Pereira de Jesus", "GETULIO DOS SANTOS CAFE", "Glemerson Lima De Souza", "GUILHERME DE OLIVEIRA DANTAS", "ILTON OLIVEIRA CORREIA", "ISAQUE INACIO BARRETO MENDONCA", "JANAILSON RICARDO FERREIRA DOS SANTOS", "JHONNY DORNELLES DE ALMEIDA", "JOSE CARLOS DA SILVA SANTOS", "LUCAS DE OLIVEIRA SANTOS", "MARCOS VINICIUS BARRETO", "NICHOLAS CZAR LEITAO SANTOS", "RAFAEL GOMES PEREIRA", "RINALDO ANTONIO DA SILVA JUNIOR", "THIAGO ARAUJO SANTOS", "VICENTE RODRIGUES DOS SANTOS", "VINICIUS ARAUJO DA SILVA", "VINICIUS SILVA FARIAS", "VITORIA FERREIRA", "Alan Cesar Cardoso", "ALEXANDRE ROGERIO GONCALVES DE MACEDO", "BARBARA CRISTINA DOS SANTOS PINTO", "BRUNA DA SILVA GOMES FERREIRA", "DOUGLAS WILLIAM SANTOS", "EMERSON DA SILVA", "FABIO OLIVEIRA CAMPOS FARIAS", "FABIO XAVIER CATAO", "FELIPE DE SOUZA OLIVEIRA", "FERNANDO LOPES", "FRANCISCO ALVES FILHO", "FRANKLIM ALVES MAIA", "GUILHERME SILVA DIAS CASTRO", "HELVIO STAFF", "JOAO CARLOS MIRON", "JOSE MARCIO DA SILVA VELOSO", "LUCAS FREIRIA PINTO", "MANOELA MIRANDA", "MATHEUS DOS SANTOS OLIVEIRA", "PEDRO LUIZ FEREEIRA CORREA", "PEDRO OLIVEIRA CARLOS DA SILVA", "RAFAELA SANTOS SILVA", "ROBSON SANTIAGO DA LUZ", "TIAGO MEIRA DA SILVA", "VALMIR RAMOS", "VITOR OLIVEIRA DA SILVA", "WELLINGTON GOMES DE OLIVEIRA", "TAILSON JUAN SANTOS DA CONCEICAO", "DIEGO FRAGOSO DE BRITO", "ALYSON ALBERTO MARTINS", "AUGUSTO MOREIRA DA SILVA", "ENDERSON CLEITON SOUZA CRUZ", "CARLOS SEBASTIAO MORAIS", "EZIEL DE OLIVEIRA BARROS", "VICTOR BORGES ALVES", "MATHEUS CARDOSO DE OLIVEIRA", "ROGERIO AFONSO DA SILVA", "KAIO NASCIMENTO ALVES DOS SANTOS", "KELVIN RIBEIRO BENTO DA COSTA", "MARCELO BUENO SEGURA", "MAYKON RIBEIRO GUIMARAES", "THIAGO JOSE ASSUNCAO", "GUSTAVO SANTOS SANT ANA"]
LISTA_ABC_FIXA = ["ADRIEL ALEXANDER DE LIMA", "AIRON HENRIQUE FERREIRA MINA", "ALAN RODRIGUES COSTA", "ALEX BERNARDES DA SILVA", "ALINE CAMARGO PIRES", "AMANDA CAROLINE DOS SANTOS", "ANA LUISA CULAU SILVA", "ANDERSON MARCELO LOPES DOS SANTOS", "AUGUSTO ERNANDES DA SILVA", "BRUNO MARTINS AVELINO", "CARLOS ALBERTO LIMA REBOUÇAS", "DANIEL SOUZA OLIVEIRA", "DANILO FERREIRA LIMA", "DEBORA BENEVENUTO PEREIRA", "DOMINGOS PEREIRA DA SILVA", "EDSON JAIRO DE ALMEIDA SOUSA", "EDUARDO FERNANDES BERNARDO DE MELO", "ELIAS AGUIAR LOPES", "ENOQUE FERREIRA SANTOS FILHO", "ERICK PAULO FERREIRA DA SILVA", "ERIK CASSIMIRO DA SILVA GOMES", "ESTEVAM MATEUS GONCALVES", "FABIO OLIVEIRA MOURA", "FELIPI ANTONIO DA SILVA", "FRANCISCO IGOR SOARES DA SILVA", "HELTON LIMA DE QUEIROZ", "IGOR DA SILVA VAYDA", "JAKSON DE JESUS E SILVA", "JEANDERSON SOUZA BERTO DA SILVA", "JEFFERSON BRADAO BASTOS", "JEFFERSON FRANCISCO DA SILVA", "JOANDERSON LOPES DA CONCEIÇÃO", "JOAO BATISTA DE LIMA TOME", "JUSCIELIO LIRA DE OLIVEIRA", "LEANDRO SOARES DA SILVA", "LEONARDO BESERRA DOS SANTOS", "LUCAS SILVA DE LIMA", "LUIS HENRIQUE GOMES DA SILVA", "MARCOS VINICIUS OLIVEIRA GOVEIA", "NATALIA SANT ANA VELASCO", "MATHEUS BOAVENTURA DA SILVA", "OSCLEY FRANCA DE SOUSA", "ODIRLEI APARECIDO PIERETI", "PATRICIA DE ARAUJO RAMALHO", "RENATO FUTRO ROSSI", "PAULO CESAR BATISTA DE SOUSA", "RAFAEL DOS ANJOS BATISTA ONOFRE", "SIDNEY ROSENDO DA SILVA", "RICARDO SANTOS", "RODRIGO FEITOZA DA SILVA", "VICTOR MENDES DOS SANTOS", "SILAS DA SILVA NASCIMENTO", "YURI URCESINO COSTA", "WESLAYNE CELINA FERREIRA SILVA", "DANIEL AUGUSTO PEREIRA", "JULIO CESAR SILVA DOS SANTOS", "EDER SALES MONTEIRO", "ANTONIO WESLEY HOLANDA DA SILVA", "MAICON JORDAN PEDRO SANTOS GARCEZ", "LUIS GUSTAVO CECCONELLO", "CLEBER FERREIRA SANTOS", "ALEX DE JESUS FREIRE", "ANTHONY HULLY PEREIRA DIAS", "ANTONIO CHARLES MARINHO", "ARLAN DUARTE NASCIMENTO", "EVERTON ALVES", "IGOR DAVID DE MARCHI", "JAZIEL DOS SANTOS SILVA", "KAUAN PASCHOAL", "LUCAS SILVA SOBRINHO", "NICOLAS CALEGARI STARCHARVSKI", "RENATO ESPERANÇA", "ROBERVAL LEAO DE ALBUQUERQUE", "RYAN PIMENTEL BARROS", "SAMUEL AUGUSTO DE OLIVEIRA", "VITOR MATOS DE ALMEIDA"]

st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if os.path.exists(ARQUIVO_ROTA_DISCO):
    try:
        df = pd.read_csv(ARQUIVO_ROTA_DISCO, sep=None, engine='python', dtype=str)
        df.columns = [str(c).strip() for c in df.columns]

        col_recurso = next((c for c in df.columns if 'RECURSO' in c.upper() or 'NOME' in c.upper()), df.columns[0])
        col_status = next((c for c in df.columns if 'STATUS' in c.upper()), None)
        
        # Procura EXATAMENTE pela coluna "Tipo de Atividade3"
        col_tipo_exata = next((c for c in df.columns if 'TIPO DE ATIVIDADE3' in c.upper() or 'TIPO DE ATIVIDADE 3' in c.upper()), None)

        if col_status:
            mask_status = df[col_status].fillna('').astype(str).str.lower().str.contains('pend')
            
            if col_tipo_exata:
                # SE A COLUNA EXISTIR: Faz o filtro estrito
                mask_base = df[col_tipo_exata].fillna('').astype(str).str.strip().str.lower() == 'na base'
            else:
                # FALLBACK DE SEGURANÇA: Se não achar, usa qualquer coluna de Tipo
                cols_tipo = [c for c in df.columns if 'TIPO' in c.upper()]
                mask_base = df[cols_tipo].apply(lambda col: col.astype(str).str.strip().str.lower() == 'na base').any(axis=1)

            df_tela = df[mask_base & mask_status].copy()

            nomes_na_base = sorted([str(n).strip().upper() for n in df_tela[col_recurso].dropna().unique()])

            lista_sp = [n.upper() for n in LISTA_SP_FIXA]
            lista_abc = [n.upper() for n in LISTA_ABC_FIXA]

            nomes_abc = [n for n in nomes_na_base if n in lista_abc or n not in lista_sp]
            nomes_sp = [n for n in nomes_na_base if n in lista_sp]

            st.markdown(f"<h4 style='text-align: center; color: #555;'>Total na Base: {len(nomes_na_base)}</h4>", unsafe_allow_html=True)
            st.divider()

            c1, c2, c3, c4 = st.columns(4)

            meio_abc = (len(nomes_abc) + 1) // 2
            meio_sp = (len(nomes_sp) + 1) // 2

            with c1:
                st.markdown('<h3 style="color:#008080;">🏢 ABC (1/2)</h3>', unsafe_allow_html=True)
                for n in nomes_abc[:meio_abc]: st.markdown(f'**{n}**')
            with c2:
                st.markdown('<h3 style="color:#008080;">🏢 ABC (2/2)</h3>', unsafe_allow_html=True)
                for n in nomes_abc[meio_abc:]: st.markdown(f'**{n}**')
            with c3:
                st.markdown('<h3 style="color:#c62828;">🏙️ SP (1/2)</h3>', unsafe_allow_html=True)
                for n in nomes_sp[:meio_sp]: st.markdown(f'**{n}**')
            with c4:
                st.markdown('<h3 style="color:#c62828;">🏙️ SP (2/2)</h3>', unsafe_allow_html=True)
                for n in nomes_sp[meio_sp:]: st.markdown(f'**{n}**')

            if len(nomes_na_base) == 0:
                if col_tipo_exata:
                    st.success("✅ Nenhum técnico pendente na base no momento!")
                else:
                    st.warning("⚠️ A coluna 'Tipo de Atividade3' ainda não foi detectada no CSV. Atualize a base na página inicial do aplicativo para que as mudanças no Excel sejam refletidas aqui.")

        else:
            st.error("⚠️ Coluna 'Status' não encontrada no arquivo.")
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
else:
    st.error("⚠️ Ficheiro 'rota_sincronizada.csv' não encontrado.")

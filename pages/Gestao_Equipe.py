import streamlit as st
import pandas as pd
import os
import time

st.set_page_config(page_title="Gestão de Equipe", layout="centered")

st.markdown('<h1 style="color: #008080; text-align: center;">⚙️ Gestão de Supervisores e Técnicos</h1>', unsafe_allow_html=True)
st.write("Use esta página para atualizar a lista fixa de funcionários do sistema sem precisar de alterar o código-fonte.")
st.divider()

ARQUIVO_EQUIPE = "cadastro_equipe.csv"

if os.path.exists(ARQUIVO_EQUIPE):
    # O Python tenta ler o arquivo tentando os dois separadores mais comuns (, ou ;)
    try:
        df_equipe = pd.read_csv(ARQUIVO_EQUIPE, sep=',')
        if len(df_equipe.columns) < 3: # Se não encontrou as colunas, o Excel estragou o separador
             df_equipe = pd.read_csv(ARQUIVO_EQUIPE, sep=';')
    except:
        df_equipe = pd.read_csv(ARQUIVO_EQUIPE, sep=';')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('### 📥 1. Baixar Lista Atual')
        st.write("Baixe o arquivo, abra no Excel, adicione/remova os nomes (MANTENHA os nomes das colunas intactos) e salve novamente.")
        
        # Converte o DataFrame para CSV FORÇANDO o separador ponto e vírgula para não desconfigurar no Excel PT-BR
        csv = df_equipe.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8')
        st.download_button(
            label="⬇️ Download do Arquivo Atual",
            data=csv,
            file_name='cadastro_equipe.csv',
            mime='text/csv',
            use_container_width=True
        )

    with col2:
        st.markdown('### 📤 2. Enviar Lista Atualizada')
        arquivo_up = st.file_uploader("Selecione o seu arquivo CSV atualizado:", type=["csv"])
        
        if arquivo_up is not None:
            try:
                # O Python tenta ler o arquivo que você subiu tentando os dois separadores
                try:
                    df_novo = pd.read_csv(arquivo_up, sep=';', encoding='utf-8-sig')
                    if len(df_novo.columns) < 3:
                        arquivo_up.seek(0)
                        df_novo = pd.read_csv(arquivo_up, sep=',', encoding='utf-8-sig')
                except:
                    arquivo_up.seek(0)
                    df_novo = pd.read_csv(arquivo_up, sep=',', encoding='utf-8-sig')
                    
                # Verifica se o arquivo tem as colunas exatas que precisamos (limpando espaços em branco)
                df_novo.columns = df_novo.columns.str.strip().str.upper()
                
                if all(col in df_novo.columns for col in ["NOME", "FUNCAO", "BASE"]):
                    # Sobrescreve o arquivo antigo pelo novo (salvando sempre com vírgula para o painel principal ler limpo)
                    df_novo.to_csv(ARQUIVO_EQUIPE, index=False, sep=',')
                    st.success("✅ Equipe atualizada com sucesso! O Painel Rotativo já está usando a nova lista.")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(f"⚠️ O arquivo enviado está inválido. Colunas encontradas: {list(df_novo.columns)}. Certifique-se de que tem as colunas: NOME, FUNCAO, BASE.")
            except Exception as e:
                st.error(f"Erro ao processar o arquivo: {e}")

    st.divider()
    st.write("### 👁️ Visualização da Equipe Atual Registada no Sistema:")
    st.dataframe(df_equipe, use_container_width=True, height=400)

else:
    st.warning("⚠️ O arquivo de equipe ainda não foi gerado. Por favor, abra a página do **Painel Rotativo** pelo menos uma vez para que o sistema crie o ficheiro de base automaticamente.")

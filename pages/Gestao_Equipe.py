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
    # Lendo o arquivo interno do sistema (sempre flexível para evitar quebras)
    try:
        df_equipe = pd.read_csv(ARQUIVO_EQUIPE, sep=',', encoding='utf-8')
        if len(df_equipe.columns) < 3:
            df_equipe = pd.read_csv(ARQUIVO_EQUIPE, sep=';', encoding='utf-8')
    except:
        try:
            df_equipe = pd.read_csv(ARQUIVO_EQUIPE, sep=';', encoding='iso-8859-1')
        except:
            df_equipe = pd.read_csv(ARQUIVO_EQUIPE, sep=',', encoding='iso-8859-1')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('### 📥 1. Baixar Lista Atual')
        st.write("Baixe o arquivo, abra no Excel, adicione/remova os nomes (MANTENHA os nomes das colunas intactos) e salve novamente.")
        
        # Forçamos a saída como UTF-8-SIG e Ponto e Vírgula para o Excel no Brasil não desconfigurar
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
            # MOTOR DE LEITURA À PROVA DE FALHAS (Testa todas as possibilidades do Excel)
            df_novo = None
            codificacoes_para_testar = ['utf-8', 'iso-8859-1', 'cp1252']
            separadores_para_testar = [';', ',']
            
            for codificacao in codificacoes_para_testar:
                for separador in separadores_para_testar:
                    try:
                        arquivo_up.seek(0) # Volta ao início do arquivo a cada tentativa
                        df_temp = pd.read_csv(arquivo_up, sep=separador, encoding=codificacao)
                        if len(df_temp.columns) >= 3: # Garante que encontrou as colunas separadas
                            df_novo = df_temp
                            break # Achou a combinação certa!
                    except:
                        pass
                if df_novo is not None:
                    break
            
            if df_novo is not None:
                # Verifica se tem as colunas corretas
                df_novo.columns = df_novo.columns.str.strip().str.upper()
                
                if all(col in df_novo.columns for col in ["NOME", "FUNCAO", "BASE"]):
                    # Salva no formato universal para o Streamlit
                    df_novo.to_csv(ARQUIVO_EQUIPE, index=False, sep=',', encoding='utf-8')
                    st.success("✅ Equipe atualizada com sucesso! O Painel Rotativo já está usando a nova lista.")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(f"⚠️ Faltam colunas obrigatórias. O arquivo deve ter: NOME, FUNCAO, BASE.")
            else:
                st.error("❌ Não foi possível ler o arquivo. O formato está corrompido.")

    st.divider()
    st.write("### 👁️ Visualização da Equipe Atual Registada no Sistema:")
    st.dataframe(df_equipe, use_container_width=True, height=400)

else:
    st.warning("⚠️ O arquivo de equipe ainda não foi gerado. Por favor, abra a página do **Painel Rotativo** pelo menos uma vez para que o sistema crie o ficheiro de base automaticamente.")

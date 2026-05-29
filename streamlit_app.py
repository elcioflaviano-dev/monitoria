import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.title("🚀 Painel de Controle - Upload de Rotas")

# 1. Botão de Upload na Página Inicial
arquivo_upload = st.file_uploader("Arraste ou selecione o arquivo Excel da Rota do Dia (.xlsx)", type=["xlsx"])

if arquivo_upload is not None:
    try:
        # Lê o arquivo que você acabou de subir
        df_carregado = pd.read_excel(arquivo_upload)
        
        # Garante que todas as colunas sejam lidas como texto para evitar erros de formatação
        df_carregado = df_carregado.astype(str)
        
        st.success("📊 Arquivo processado com sucesso pelo sistema!")
        
        # 2. O SISTEMA GUARDA AUTOMATICAMENTE NA NUVEM
        with st.spinner("💾 O sistema está salvando a rota no Google Sheets de forma persistente..."):
            conexao_sheets = GSheetsConnection(connection_name="gsheets")
            conexao_sheets.update(worksheet="Rota_Ativa", data=df_carregado)
            
        st.balloons()
        st.success("✅ Rota salva e sincronizada! Agora está guardada na nuvem e disponível para todas as páginas.")
        
        # Guarda também na sessão atual para uso imediato
        st.session_state['df_rota_ativa'] = df_carregado
        
    except Exception as e:
        st.error(f"❌ Erro ao processar ou salvar o arquivo: {e}")

# 3. Garante que se você mudar de página, o sistema busca o que ele mesmo guardou
else:
    if 'df_rota_ativa' not in st.session_state:
        try:
            conexao_sheets = GSheetsConnection(connection_name="gsheets")
            df_salvo = conexao_sheets.read(worksheet="Rota_Ativa", ttl="0d", dtype=str)
            if df_salvo is not None and not df_salvo.empty:
                st.session_state['df_rota_ativa'] = df_salvo
                st.info("🔄 Rota ativa carregada automaticamente da memória da nuvem!")
        except:
            pass

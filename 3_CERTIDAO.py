import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. Configuração da página
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 2. Carregar Estilos Globais (opcional)
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

st.markdown('<h1 style="font-size: 42px; font-weight: 900; color: #008080; text-align: center; margin-top: 25px; margin-bottom: 20px;">📜 SISTEMA DE CERTIDÃO</h1>', unsafe_allow_html=True)

# === BANCO DE DADOS LOCAL (ARQUIVO PERMANENTE) ===
ARQUIVO_BANCO = "banco_certidoes.csv"

# Função para carregar o histórico do arquivo para a memória do Streamlit
def carregar_banco_historico():
    if os.path.exists(ARQUIVO_BANCO):
        try:
            return pd.read_csv(ARQUIVO_BANCO, dtype=str)
        except:
            return pd.DataFrame(columns=["Data/Hora", "Contrato", "Status", "Responsável", "Observação"])
    else:
        return pd.DataFrame(columns=["Data/Hora", "Contrato", "Status", "Responsável", "Observação"])

# Inicializa a memória da sessão para evitar perda de dados em cliques intermediários
if "historico_certidoes" not in st.session_state:
    st.session_state["historico_certidoes"] = carregar_banco_historico()

# === FORMULÁRIO DE ENTRADA DE DADOS ===
st.markdown("### 🔍 Verificar e Registrar Contrato")

# Layout em colunas para o formulário ficar elegante
col1, col2, col3 = st.columns([2, 2, 3])

with col1:
    contrato_input = st.text_input("Número do Contrato:", placeholder="Digite o contrato aqui...").strip()

with col2:
    status_selecionado = st.selectbox("Resultado da Verificação:", ["ATENDE", "NÃO ATENDE", "EM ANÁLISE"])

with col3:
    obs_input = st.text_input("Observações / Motivo:", placeholder="Ex: Documentação validada / Falta assinatura...")

# Botão para salvar
if st.button("💾 Gravar e Certificar Contrato", type="primary"):
    if contrato_input == "":
        st.warning("⚠️ Por favor, digite um número de contrato válido antes de salvar.")
    else:
        # Captura o momento exato do registro
        agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Cria a nova linha de dados
        nova_linha = pd.DataFrame([{
            "Data/Hora": agora,
            "Contrato": contrato_input,
            "Status": status_selecionado,
            "Responsável": "Operador",  # Pode ser customizado depois
            "Observação": obs_input if obs_input else "N/A"
        }])
        
        # 1. Atualiza a memória ativa da tela (Session State)
        st.session_state["historico_certidoes"] = pd.concat([nova_linha, st.session_state["historico_certidoes"]], ignore_index=True)
        
        # 2. Salva permanentemente no arquivo CSV do servidor
        st.session_state["historico_certidoes"].to_csv(ARQUIVO_BANCO, index=False)
        
        st.success(f"✅ Contrato {contrato_input} registrado com sucesso!")
        
        # Dá um refresh leve para limpar os campos visuais se necessário (opcional)
        st.rerun()

st.markdown("---")

# === EXIBIÇÃO DO HISTÓRICO ACUMULADO ===
st.markdown("### 🗂️ Histórico de Contratos Verificados")

df_exibicao = st.session_state["historico_certidoes"]

if not df_exibicao.empty:
    # Filtro de busca rápido na tabela de histórico
    busca_historico = st.text_input("🔍 Filtrar histórico por Contrato:", placeholder="Digite para buscar no histórico...")
    
    if busca_historico:
        df_filtrado = df_exibicao[df_exibicao["Contrato"].str.contains(busca_historico, case=False, na=False)]
    else:
        df_filtrado = df_exibicao

    # Estilização básica para colorir as linhas baseado no Status
    def colorir_status(val):
        if val == "ATENDE":
            return "background-color: #d4edda; color: #155724; font-weight: bold;"
        elif val == "NÃO ATENDE":
            return "background-color: #f8d7da; color: #721c24; font-weight: bold;"
        return "background-color: #fff3cd; color: #856404;"

    try:
        df_estilizado = df_filtrado.style.map(colorir_status, subset=["Status"])
        st.dataframe(df_estilizado, use_container_width=True, hide_index=True)
    except:
        # Fallback caso a versão do pandas seja mais antiga
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
        
    # Botão para baixar o relatório em Excel/CSV se a operação precisar
    csv_download = df_exibicao.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar Banco de Dados Completo (CSV)",
        data=csv_download,
        file_name="relatorio_certidoes.csv",
        mime="text/csv",
    )
else:
    st.info("ℹ️ Nenhum contrato foi verificado ou certificado ainda hoje.")

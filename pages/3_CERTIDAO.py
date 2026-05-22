import streamlit as st
import pandas as pd
import requests
import io
import os
from datetime import datetime

# 1. Configuração da página
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 2. Carregar Estilos Globais
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

st.markdown('<h1 style="font-size: 42px; font-weight: 900; color: #008080; text-align: center; margin-top: 25px; margin-bottom: 20px;">📜 SISTEMA DE CERTIDÃO</h1>', unsafe_allow_html=True)

# === BANCO DE DADOS LOCAL (ARQUIVO PERMANENTE) ===
ARQUIVO_BANCO = "banco_certidoes.csv"

def carregar_banco_historico():
    if os.path.exists(ARQUIVO_BANCO):
        try:
            return pd.read_csv(ARQUIVO_BANCO, dtype=str)
        except:
            return pd.DataFrame(columns=["Data/Hora", "Contrato", "Status", "Supervisor", "Observação"])
    return pd.DataFrame(columns=["Data/Hora", "Contrato", "Status", "Supervisor", "Observação"])

# === FUNÇÃO DE CONSULTA OPERACIONAL (CONEXÃO COM LINK ESTÁVEL DO SHEETS) ===
def buscar_base_rotas_online():
    try:
        url = st.secrets.get('public_gsheets_url', "https://docs.google.com/spreadsheets/d/1kB1YmUuhzHpfN1dLv8PaQn0ipXcHcd6kGKnI3nguT14/edit?gid=208394608#gid=208394608").strip()
        if 'spreadsheets/d/' in url:
            id_planilha = url.split('/spreadsheets/d/')[1].split('/')[0].strip()
            csv_url = "https://docs.google.com/spreadsheets/d/" + id_planilha + "/export?format=csv"
            if 'gid=' in url:
                gid = url.split('gid=')[1].split('#')[0].split('&')[0].strip()
                csv_url += "&gid=" + gid
        else:
            csv_url = url

        headers = {'User-Agent': 'Mozilla/5.0'}
        resposta = requests.get(csv_url, headers=headers, timeout=15)
        if resposta.status_code != 200:
            return None
            
        conteudo_bruto = resposta.text
        linhas_puras = conteudo_bruto.splitlines()
        linha_do_cabecalho_real = 0
        encontrou_cabecalho = False
        
        for i, linha_texto in enumerate(linhas_puras[:50]):
            linha_upper = linha_texto.upper()
            if 'SUPERVISOR' in linha_upper or 'STATUS' in linha_upper or 'JANELA' in linha_upper or 'CONTRATO' in linha_upper:
                linha_do_cabecalho_real = i
                encontrou_cabecalho = True
                break

        if encontrou_cabecalho:
            texto_corrigido = "\n".join(linhas_puras[linha_do_cabecalho_real:])
            df_sheets = pd.read_csv(io.StringIO(texto_corrigido), dtype=str, on_bad_lines='skip')
        else:
            df_sheets = pd.read_csv(io.StringIO(conteudo_bruto), dtype=str, on_bad_lines='skip')
            
        df_sheets.columns = [str(c).strip().replace('\xa0', ' ') for c in df_sheets.columns]
        
        colunas_mapeadas = {}
        for col in df_sheets.columns:
            col_upper = col.upper()
            if 'SUPERVISOR' in col_upper: colunas_mapeadas[col] = 'SUPERVISOR'
            elif 'STATUS' in col_upper: colunas_mapeadas[col] = 'Status da Atividade'
            elif 'CONTRATO' in col_upper: colunas_mapeadas[col] = 'Contrato'
            
        return df_sheets.rename(columns=colunas_mapeadas)
    except:
        return None

# Inicializa as memórias de sessão
if "historico_certidoes" not in st.session_state:
    st.session_state["historico_certidoes"] = carregar_banco_historico()

# Garante o carregamento da base online para validação automática
df_base_online = buscar_base_rotas_online()

# === FORMULÁRIO DE ENTRADA COM ANÁLISE AUTOMÁTICA ===
st.markdown("### 🔍 Verificar e Registrar Contrato")

col1, col2, col3 = st.columns([2, 2, 3])

with col1:
    contrato_input = st.text_input("Número do Contrato:", placeholder="Digite o contrato aqui...").strip()

# --- LÓGICA INTERNA DE CRUZAMENTO EM TEMPO REAL ---
status_sugerido = "NÃO ENCONTRADO"
supervisor_detectado = "N/A"
detalhes_validacao = ""

if contrato_input and df_base_online is not None:
    # Garante a formatação limpa (remove possíveis pontos flutuantes do texto do contrato)
    df_base_online['Contrato_Limpo'] = df_base_online['Contrato'].fillna('').astype(str).apply(lambda x: x.split('.')[0].strip())
    
    # Procura o contrato na planilha online
    contrato_encontrado = df_base_online[df_base_online['Contrato_Limpo'] == contrato_input]
    
    if not contrato_encontrado.empty:
        linha_contrato = contrato_encontrado.iloc[0]
        supervisor_detectado = str(linha_contrato.get('SUPERVISOR', 'N/A')).upper()
        status_atividade = str(linha_contrato.get('Status da Atividade', '')).upper().strip()
        
        # MUDANÇA AUTOMÁTICA: Se o status na planilha já for aceito ou regularizado, vira OK
        if status_atividade in ['OK', 'CONCLUÍDO', 'CONCLUIDO', 'FINALIZADO']:
            status_sugerido = "OK"
            detalhes_validacao = f"🟢 Encontrado na base de rotas! Supervisor: {supervisor_detectado}."
        else:
            status_sugerido = "NÃO ATENDE"
            detalhes_validacao = f"⚠️ Encontrado, mas o status atual na rota é: '{status_atividade}'."
    else:
        detalhes_validacao = "❌ Contrato não localizado na base de rotas online."

if contrato_input:
    st.caption(detalhes_validacao)

with col2:
    # O selectbox agora adota dinamicamente a sugestão automática do motor de busca
    opcoes_status = ["OK", "NÃO ATENDE", "EM ANÁLISE", "NÃO ENCONTRADO"]
    idx_default = opcoes_status.index(status_sugerido) if status_sugerido in opcoes_status else 1
    status_final = st.selectbox("Resultado da Verificação:", opcoes_status, index=idx_default)

with col3:
    obs_input = st.text_input("Observações / Motivo:", placeholder="Caso queira, insira um comentário sobre este contrato...")

# Botão para salvar dados
if st.button("💾 Gravar e Certificar Contrato", type="primary"):
    if contrato_input == "":
        st.warning("⚠️ Por favor, digite um número de contrato válido antes de salvar.")
    else:
        agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        nova_linha = pd.DataFrame([{
            "Data/Hora": agora,
            "Contrato": contrato_input,
            "Status": status_final,
            "Supervisor": supervisor_detectado,
            "Observação": obs_input if obs_input else "Validação automática do sistema."
        }])
        
        st.session_state["historico_certidoes"] = pd.concat([nova_linha, st.session_state["historico_certidoes"]], ignore_index=True)
        st.session_state["historico_certidoes"].to_csv(ARQUIVO_BANCO, index=False)
        
        st.success(f"✅ Contrato {contrato_input} registrado como {status_final}!")
        st.rerun()

st.markdown("---")

# === EXIBIÇÃO DO HISTÓRICO ACUMULADO ===
st.markdown("### 🗂️ Histórico de Contratos Verificados")

df_exibicao = st.session_state["historico_certidoes"]

if not df_exibicao.empty:
    busca_historico = st.text_input("🔍 Filtrar histórico por Contrato:", placeholder="Digite o número para pesquisar...")
    
    if busca_historico:
        df_filtrado = df_exibicao[df_exibicao["Contrato"].str.contains(busca_historico, case=False, na=False)]
    else:
        df_filtrado = df_exibicao

    # Cores inteligentes para a tabela de histórico acumulada
    def colorir_status(val):
        if val == "OK":
            return "background-color: #d4edda; color: #155724; font-weight: bold;"
        elif val == "NÃO ATENDE" or val == "NÃO ENCONTRADO":
            return "background-color: #f8d7da; color: #721c24; font-weight: bold;"
        return "background-color: #fff3cd; color: #856404;"

    try:
        df_estilizado = df_filtrado.style.map(colorir_status, subset=["Status"])
        st.dataframe(df_estilizado, use_container_width=True, hide_index=True)
    except:
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
        
    csv_download = df_exibicao.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar Banco de Dados Completo (CSV)",
        data=csv_download,
        file_name="relatorio_certidoes.csv",
        mime="text/csv",
    )
else:
    st.info("ℹ️ Nenhum contrato foi verificado ou certificado até ao momento.")

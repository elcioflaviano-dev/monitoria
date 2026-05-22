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

# === BANCO DE DADOS LOCAL (ARQUIVO PERMANENTE DE REGISTROS) ===
ARQUIVO_BANCO = "banco_certidoes.csv"

def carregar_banco_historico():
    if os.path.exists(ARQUIVO_BANCO):
        try:
            return pd.read_csv(ARQUIVO_BANCO, dtype=str)
        except:
            return pd.DataFrame(columns=["Data/Hora", "Contrato", "Status", "Supervisor", "Observação", "Janela"])
    return pd.DataFrame(columns=["Data/Hora", "Contrato", "Status", "Supervisor", "Observação", "Janela"])

# === FUNÇÃO DE CARGA OPERACIONAL ONLINE ===
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
            
        conteudo_bruto = response_text = resposta.text
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
        
        # Mapeamento dinâmico estendido para incluir a O.S 1
        colunas_mapeadas = {}
        for col in df_sheets.columns:
            col_upper = col.upper()
            if 'SUPERVISOR' in col_upper: colunas_mapeadas[col] = 'SUPERVISOR'
            elif 'JANELA' in col_upper: colunas_mapeadas[col] = 'Janela de Serviço'
            elif 'STATUS DA ATIVIDADE' in col_upper or ('STATUS' in col_upper and 'ATIVIDADE' in col_upper): colunas_mapeadas[col] = 'Status da Atividade'
            elif 'STATUS DA O.S 1' in col_upper or 'O.S 1' in col_upper or 'OS 1' in col_upper: colunas_mapeadas[col] = 'Status da O.S 1'
            elif 'CONTRATO' in col_upper: colunas_mapeadas[col] = 'Contrato'
            
        return df_sheets.rename(columns=colunas_mapeadas)
    except:
        return None

# Inicializa banco local em memória
if "historico_certidoes" not in st.session_state:
    st.session_state["historico_certidoes"] = carregar_banco_historico()

df_base_online = buscar_base_rotas_online()

# --- FILTRO DA JANELA GLOBAL NA BARRA LATERAL ---
if df_base_online is not None and 'Janela de Serviço' in df_base_online.columns:
    opcoes_janela = sorted(df_base_online['Janela de Serviço'].dropna().astype(str).unique())
    janela_sel = st.sidebar.selectbox("Janela de Atendimento Ativa:", opcoes_janela)
else:
    janela_sel = "N/A"

# === FORMULÁRIO DE ENTRADA COM ANÁLISE AUTOMÁTICA DE CRITÉRIOS ===
st.markdown("### 🔍 Verificar e Registrar Contrato")

col1, col2, col3 = st.columns([2, 2, 3])

with col1:
    contrato_input = st.text_input("Número do Contrato:", placeholder="Digite o contrato para checar...").strip()

status_sugerido = "NOK"
supervisor_detectado = "N/A"
detalhes_validacao = ""

if contrato_input and df_base_online is not None:
    # Ajusta contratos para formato limpo string
    df_base_online['Contrato_Limpo'] = df_base_online['Contrato'].fillna('').astype(str).apply(lambda x: x.split('.')[0].strip())
    contrato_encontrado = df_base_online[df_base_online['Contrato_Limpo'] == contrato_input]
    
    if not contrato_encontrado.empty:
        linha_contrato = contrato_encontrado.iloc[0]
        supervisor_detectado = str(linha_contrato.get('SUPERVISOR', 'N/A')).upper()
        status_os1 = str(linha_contrato.get('Status da O.S 1', '')).upper().strip()
        
        # APLICAÇÃO DO CRITÉRIO: Valida se é executado na O.S 1
        if "EXECUTADO" in status_os1 and "NÃO" not in status_os1:
            status_sugerido = "NOK"
            detalhes_validacao = f"🎯 Aderente (O.S 1 Executada). Padrão definido: NOK (Aguardando digitação)."
        else:
            status_sugerido = "NÃO ADERENTE"
            detalhes_validacao = f"⚠️ Contrato encontrado, mas Status da O.S 1 é '{status_os1}' (Não Aderente)."
    else:
        detalhes_validacao = "❌ Contrato não localizado na base de rotas online."

if contrato_input:
    st.caption(detalhes_validacao)

with col2:
    opcoes_status = ["NOK", "OK", "NÃO ADERENTE"]
    idx_default = opcoes_status.index(status_sugerido) if status_sugerido in opcoes_status else 0
    status_final = st.selectbox("Resultado da Verificação:", opcoes_status, index=idx_default)

with col3:
    obs_input = st.text_input("Observações / Motivo:", placeholder="Insira notas adicionais aqui...")

# Botão Gravar
if st.button("💾 Gravar e Certificar Contrato", type="primary"):
    if contrato_input == "":
        st.warning("⚠️ Por favor, digite um número de contrato válido.")
    else:
        agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        nova_linha = pd.DataFrame([{
            "Data/Hora": agora,
            "Contrato": contrato_input,
            "Status": status_final,
            "Supervisor": supervisor_detectado,
            "Observação": obs_input if obs_input else "Registro efetuado pelo sistema.",
            "Janela": janela_sel
        }])
        
        # Guarda no histórico acumulado permanente
        st.session_state["historico_certidoes"] = pd.concat([nova_linha, st.session_state["historico_certidoes"]], ignore_index=True)
        st.session_state["historico_certidoes"].to_csv(ARQUIVO_BANCO, index=False)
        
        st.success(f"✅ Contrato {contrato_input} registrado como {status_final}!")
        st.rerun()

st.markdown("---")

# === SEÇÃO NOVIDADE: CERTIDÃO PENDENTES AGRUPADOS POR SUPERVISOR ===
st.markdown("### 🗂️ CERTIDÃO PENDENTES")

df_banco_atual = st.session_state["historico_certidoes"]

if df_base_online is not None and not df_banco_atual.empty:
    # 1. Filtra do Banco Local apenas quem está NOK
    df_nok_local = df_banco_atual[df_banco_atual["Status"] == "NOK"]
    
    if not df_nok_local.empty and 'Status da Atividade' in df_base_online.columns:
        # Cruza os dados locais NOK com a base do Sheets para validar o Status da Atividade em tempo real
        df_base_online['Contrato_Limpo'] = df_base_online['Contrato'].fillna('').astype(str).apply(lambda x: x.split('.')[0].strip())
        
        # Filtra a base online pela Janela Selecionada e Status da Atividade (Iniciado ou Concluido)
        df_base_filtrada = df_base_online[
            (df_base_online['Janela de Serviço'] == janela_sel) & 
            (df_base_online['Status da Atividade'].fillna('').astype(str).str.upper().isin(['INICIADO', 'CONCLUIDO', 'CONCLUÍDO']))
        ]
        
        # Filtra para exibir apenas os contratos que estão marcados como NOK no nosso banco local
        lista_contratos_nok = df_nok_local["Contrato"].tolist()
        df_exibir_pendentes = df_base_filtrada[df_base_filtrada['Contrato_Limpo'].isin(lista_contratos_nok)]
        
        if not df_exibir_pendentes.empty:
            # Separa e exibe em cartões dinâmicos divididos por supervisor
            supervisores_na_tela = sorted(df_exibir_pendentes['SUPERVISOR'].dropna().unique())
            
            # Cria colunas responsivas para os supervisores aparecerem organizados
            cols_supervisores = st.columns(len(supervisores_na_tela) if len(supervisores_na_tela) > 0 else 1)
            
            for idx_sup, super_nome in enumerate(supervisores_na_tela):
                with cols_supervisores[idx_sup % len(cols_supervisores)]:
                    with st.container(border=True):
                        df_cards_sup = df_exibir_pendentes[df_exibir_pendentes['SUPERVISOR'] == super_nome]
                        total_sup_nok = len(df_cards_sup)
                        
                        st.markdown(f"##### **{str(super_nome).upper()}** <span style='float:right; background-color:#ffe6e6; color:#b30000; padding:1px 6px; border-radius:4px; font-size:12px;'>Pendentes: {total_sup_nok}</span>", unsafe_allow_html=True)
                        
                        for _, row_p in df_cards_sup.iterrows():
                            c_num = str(row_p['Contrato_Limpo'])
                            status_ativ = str(row_p['Status da Atividade']).upper()
                            
                            # Cor do marcador de acordo com o status operacional da atividade
                            badge_color = "#4caf50" if "CONCLU" in status_ativ else "#ff9800"
                            
                            st.markdown(f"""
                                <div style="display:flex; justify-content:space-between; align-items:center; background-color:#f9f9f9; padding:6px; border:1px solid #e0e0e0; border-radius:4px; margin-bottom:4px;">
                                    <span style="font-weight:bold; color:#333; font-size:13px;">📄 {c_num}</span>
                                    <span style="background-color:{badge_color}; color:white; font-size:10px; padding:2px 6px; border-radius:3px; font-weight:bold;">{status_ativ}</span>
                                </div>
                            """, unsafe_allow_html=True)
        else:
            st.info(f"✨ Nenhuma certidão pendente (NOK) com atividade Iniciada ou Concluída para a janela: **{janela_sel}**.")
    else:
        st.info("ℹ️ Não existem contratos salvos com o status 'NOK' até o momento.")
else:
    st.info("ℹ️ Aguardando registros no sistema ou carregamento das rotas online.")

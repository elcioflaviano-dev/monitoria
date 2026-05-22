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
            
        conteudo_bruto = resposta.text
        linhas_puras = conteudo_bruto.splitlines()
        linha_do_cabecalho_real = 0
        encontrou_cabecalho = False
        
        for i, Web_linha in enumerate(linhas_puras[:50]):
            linha_upper = Web_linha.upper()
            if 'SUPERVISOR' in Web_linha or 'STATUS' in linha_upper or 'INTERVALO' in linha_upper or 'CONTRATO' in linha_upper or 'TEMPO' in linha_upper:
                linha_do_cabecalho_real = i
                encontrou_cabecalho = True
                break

        if encontrou_cabecalho:
            texto_corrigido = "\n".join(linhas_puras[linha_do_cabecalho_real:])
            df_sheets = pd.read_csv(io.StringIO(texto_corrigido), dtype=str, on_bad_lines='skip')
        else:
            df_sheets = pd.read_csv(io.StringIO(conteudo_bruto), dtype=str, on_bad_lines='skip')
            
        if df_sheets is None or df_sheets.empty:
            return None

        # Limpa nomes originais das colunas
        df_sheets.columns = [str(c).strip().replace('\xa0', ' ') for c in df_sheets.columns]
        
        # Cria um clone para trabalhar de forma ultra segura
        df_final = df_sheets.copy()
        
        # MAPEAMENTO DIRECIONADO COMPATÍVEL COM O SEU BANCO DE DADOS
        colunas_mapeadas = {}
        for col in df_sheets.columns:
            col_upper = col.upper()
            if 'SUPERVISOR' in col_upper: colunas_mapeadas[col] = 'SUPERVISOR'
            elif 'INTERVALO' in col_upper or 'TEMPO' in col_upper or 'JANELA' in col_upper: colunas_mapeadas[col] = 'Intervalo de Tempo'
            elif 'STATUS DA ATIVIDADE' in col_upper or ('STATUS' in col_upper and 'ATIVIDADE' in col_upper): colunas_mapeadas[col] = 'Status da Atividade'
            elif 'STATUS DA O.S 1' in col_upper or 'O.S 1' in col_upper or 'OS 1' in col_upper: colunas_mapeadas[col] = 'Status da O.S 1'
            elif 'CONTRATO' in col_upper: colunas_mapeadas[col] = 'Contrato'
        
        df_final = df_final.rename(columns=colunas_mapeadas)

        # 🚨 BLINDAGEM CONTRA ATTRIBUTE_ERROR (Força a criação física se não vier do Excel)
        if 'Intervalo de Tempo' not in df_final.columns:
            df_final['Intervalo de Tempo'] = 'Padrão / Sem Janela'
        if 'Status da Atividade' not in df_final.columns:
            df_final['Status da Atividade'] = 'PENDENTE'
        if 'Status da O.S 1' not in df_final.columns:
            df_final['Status da O.S 1'] = 'NÃO EXECUTADO'
        if 'SUPERVISOR' not in df_final.columns:
            df_final['SUPERVISOR'] = 'N/A'
        if 'Contrato' not in df_final.columns:
            if len(df_final.columns) > 0:
                df_final = df_final.rename(columns={df_final.columns[0]: 'Contrato'})
            else:
                df_final['Contrato'] = 'N/A'
            
        return df_final
    except:
        return None

# Inicializa banco local em memória
if "historico_certidoes" not in st.session_state:
    st.session_state["historico_certidoes"] = carregar_banco_historico()

df_base_online = buscar_base_rotas_online()

# --- TRATAMENTO SEGURO DOS FILTROS OPERACIONAIS ---
if df_base_online is not None and 'Intervalo de Tempo' in df_base_online.columns:
    opcoes_janela = sorted(df_base_online['Intervalo de Tempo'].dropna().astype(str).unique())
    if not opcoes_janela:
        opcoes_janela = ["Padrão / Sem Janela"]
    janela_sel = st.sidebar.selectbox("Intervalo de Tempo Ativo:", opcoes_janela)
else:
    janela_sel = "Padrão / Sem Janela"
    st.warning("⚠️ Aguardando resposta estável da planilha... A página continuará funcional.")

# === FORMULÁRIO DE ENTRADA COM ANÁLISE AUTOMÁTICA DE CRITÉRIOS ===
st.markdown("### 🔍 Verificar e Registrar Contrato")

col1, col2, col3 = st.columns([2, 2, 3])

with col1:
    contrato_input = st.text_input("Número do Contrato:", placeholder="Digite o contrato para checar...").strip()

status_sugerido = "NOK"
supervisor_detectado = "N/A"
detalhes_validacao = ""

if contrato_input and df_base_online is not None and 'Contrato' in df_base_online.columns:
    df_base_online['Contrato_Limpo'] = df_base_online['Contrato'].fillna('').astype(str).apply(lambda x: x.split('.')[0].strip())
    contrato_encontrado = df_base_online[df_base_online['Contrato_Limpo'] == contrato_input]
    
    if not contrato_encontrado.empty:
        linha_contrato = contrato_encontrado.iloc[0]
        supervisor_detectado = str(linha_contrato.get('SUPERVISOR', 'N/A')).upper()
        status_os1 = str(linha_contrato.get('Status da O.S 1', '')).upper().strip()
        
        if "EXECUTADO" in status_os1 and "NÃO" not in status_os1:
            status_sugerido = "NOK"
            detalhes_validacao = f"🎯 Aderente (O.S 1 Executada). Padrão definido: NOK (Aguardando digitação)."
        else:
            status_sugerido = "NÃO ADERENTE"
            detalhes_validacao = f"⚠️ Contrato encontrado, mas Status da O.S 1 é '{status_os1}' (Não Aderente)."
    else:
        detalhes_validacao = "❌ Contrato não localizado na base de rotas online."
elif contrato_input and df_base_online is None:
    detalhes_validacao = "⏳ Não foi possível consultar a base online neste momento. Preenchimento manual ativado."

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
        
        st.session_state["historico_certidoes"] = pd.concat([nova_linha, st.session_state["historico_certidoes"]], ignore_index=True)
        st.session_state["historico_certidoes"].to_csv(ARQUIVO_BANCO, index=False)
        
        st.success(f"✅ Contrato {contrato_input} registrado como {status_final}!")
        st.rerun()

st.markdown("---")

# === SEÇÃO: CERTIDÃO PENDENTES AGRUPADOS POR SUPERVISOR ===
st.markdown("### 🗂️ CERTIDÃO PENDENTES")

df_banco_atual = st.session_state["historico_certidoes"]

if df_base_online is not None and not df_banco_atual.empty:
    df_nok_local = df_banco_atual[df_banco_atual["Status"] == "NOK"]
    
    if not df_nok_local.empty and 'Status da Atividade' in df_base_online.columns and 'Contrato' in df_base_online.columns:
        df_base_online['Contrato_Limpo'] = df_base_online['Contrato'].fillna('').astype(str).apply(lambda x: x.split('.')[0].strip())
        
        df_base_filtrada = df_base_online[
            (df_base_online['Intervalo de Tempo'] == janela_sel) & 
            (df_base_online['Status da Atividade'].fillna('').astype(str).str.upper().isin(['INICIADO', 'CONCLUIDO', 'CONCLUÍDO']))
        ]
        
        lista_contratos_nok = df_nok_local["Contrato"].tolist()
        df_exibir_pendentes = df_base_filtrada[df_base_filtrada['Contrato_Limpo'].isin(lista_contratos_nok)]
        
        if not df_exibir_pendentes.empty:
            supervisores_na_tela = sorted(df_exibir_pendentes['SUPERVISOR'].dropna().unique())
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
                            badge_color = "#4caf50" if "CONCLU" in status_ativ else "#ff9800"
                            
                            st.markdown(f"""
                                <div style="display:flex; justify-content:space-between; align-items:center; background-color:#f9f9f9; padding:6px; border:1px solid #e0e0e0; border-radius:4px; margin-bottom:4px;">
                                    <span style="font-weight:bold; color:#333; font-size:13px;">📄 {c_num}</span>
                                    <span style="background-color:{badge_color}; color:white; font-size:10px; padding:2px 6px; border-radius:3px; font-weight:bold;">{status_ativ}</span>
                                </div>
                            """, unsafe_allow_html=True)
        else:
            st.info(f"✨ Nenhuma certidão pendente (NOK) com atividade Iniciada ou Concluída para o intervalo: **{janela_sel}**.")
    else:
        st.info("ℹ️ Não existem contratos salvos com o status 'NOK' neste intervalo até ao momento.")
else:
    st.info("ℹ️ Aguardando registros no sistema ou sincronização com a base de rotas online.")

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
            return pd.DataFrame(columns=["Data/Hora", "Contrato", "Status", "Supervisor", "Observação", "Intervalo de Tempo"])
    return pd.DataFrame(columns=["Data/Hora", "Contrato", "Status", "Supervisor", "Observação", "Intervalo de Tempo"])

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
        for i, texto_linha in enumerate(linhas_puras[:30]):
            linha_upper = texto_linha.upper()
            if 'SUPERVISOR' in linha_upper or 'CONTRATO' in linha_upper or 'INTERVALO' in linha_upper or 'STATUS' in linha_upper:
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

        df_sheets.columns = [str(c).strip().replace('\xa0', ' ') for c in df_sheets.columns]
        df_final = df_sheets.copy()
        
        colunas_mapeadas = {}
        for col in df_sheets.columns:
            col_upper = col.upper()
            if 'SUPERVISOR' in col_upper: colunas_mapeadas[col] = 'SUPERVISOR'
            elif 'INTERVALO' in col_upper or 'TEMPO' in col_upper: colunas_mapeadas[col] = 'Intervalo de Tempo'
            elif 'STATUS DA ATIVIDADE' in col_upper or ('STATUS' in col_upper and 'ATIVIDADE' in col_upper): colunas_mapeadas[col] = 'Status da Atividade'
            elif 'STATUS DA O.S 1' in col_upper or 'O.S 1' in col_upper or 'OS 1' in col_upper: colunas_mapeadas[col] = 'Status da O.S 1'
            elif 'CONTRATO' in col_upper: colunas_mapeadas[col] = 'Contrato'
        
        df_final = df_final.rename(columns=colunas_mapeadas)

        if 'Intervalo de Tempo' not in df_final.columns and len(df_final.columns) >= 3:
            for idx_c, nome_c in enumerate(df_final.columns):
                if idx_c in [1, 2, 3] and nome_c not in ['SUPERVISOR', 'Contrato']:
                    df_final = df_final.rename(columns={nome_c: 'Intervalo de Tempo'})
                    break

        if 'Intervalo de Tempo' not in df_final.columns: df_final['Intervalo de Tempo'] = 'Padrão / Sem Janela'
        if 'Status da Atividade' not in df_final.columns: df_final['Status da Atividade'] = 'PENDENTE'
        if 'Status da O.S 1' not in df_final.columns: df_final['Status da O.S 1'] = 'NÃO EXECUTADO'
        if 'SUPERVISOR' not in df_final.columns: df_final['SUPERVISOR'] = 'N/A'
        if 'Contrato' not in df_final.columns: df_final = df_final.rename(columns={df_final.columns[0]: 'Contrato'})
            
        return df_final
    except:
        return None

if "historico_certidoes" not in st.session_state:
    st.session_state["historico_certidoes"] = carregar_banco_historico()

df_base_online = buscar_base_rotas_online()

# --- SELETOR DE INTERVALO NA BARRA LATERAL ---
janela_sel = "Padrão / Sem Janela"
if df_base_online is not None:
    try:
        opcoes_janela = sorted(df_base_online['Intervalo de Tempo'].dropna().astype(str).unique())
        if opcoes_janela:
            janela_sel = st.sidebar.selectbox("Intervalo de Tempo Ativo:", opcoes_janela)
    except:
        pass

# ==========================================
# BLOCO 1: FORMULÁRIO DE ENTRADA (AÇÕES)
# ==========================================
with st.container(border=True):
    st.markdown("#### 📥 Verificar e Registrar Contrato")
    col1, col2, col3 = st.columns([2, 2, 3])

    with col1:
        contrato_input = st.text_input("Número do Contrato:", placeholder="Digite o contrato...").strip()

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
                detalhes_validacao = f"🎯 Aderente (O.S 1 Executada). Padrão definido: NOK."
            else:
                status_sugerido = "NÃO ADERENTE"
                detalhes_validacao = f"⚠️ Status da O.S 1 é '{status_os1}' (Não Aderente)."
        else:
            detalhes_validacao = "❌ Contrato não localizado na base online."

    if contrato_input:
        st.caption(detalhes_validacao)

    with col2:
        opcoes_status = ["NOK", "OK", "NÃO ADERENTE"]
        idx_default = opcoes_status.index(status_sugerido) if status_sugerido in opcoes_status else 0
        status_final = st.selectbox("Resultado da Verificação:", opcoes_status, index=idx_default)

    with col3:
        obs_input = st.text_input("Observações / Motivo:", placeholder="Insira notas adicionais...")

    if st.button("💾 Gravar e Certificar Contrato", type="primary"):
        if contrato_input != "":
            agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            nova_linha = pd.DataFrame([{
                "Data/Hora": agora, "Contrato": contrato_input, "Status": status_final,
                "Supervisor": supervisor_detectado, "Observação": obs_input if obs_input else "OK",
                "Intervalo de Tempo": janela_sel
            }])
            st.session_state["historico_certidoes"] = pd.concat([nova_linha, st.session_state["historico_certidoes"]], ignore_index=True)
            st.session_state["historico_certidoes"].to_csv(ARQUIVO_BANCO, index=False)
            st.success(f"✅ Contrato {contrato_input} salvo!")
            st.rerun()

st.markdown("---")

# ==========================================
# BLOCO 2: PAINEL OPERACIONAL (VISUAL TV)
# ==========================================
st.markdown("### 🗂️ CERTIDÃO PENDENTES")

df_banco_atual = st.session_state["historico_certidoes"]

if df_base_online is not None and not df_banco_atual.empty:
    df_nok_local = df_banco_atual[df_banco_atual["Status"].fillna('').astype(str).str.upper() == "NOK"]
    
    if not df_nok_local.empty and 'Status da Atividade' in df_base_online.columns:
        df_base_online['Contrato_Limpo'] = df_base_online['Contrato'].fillna('').astype(str).apply(lambda x: x.split('.')[0].strip())
        
        df_base_filtrada = df_base_online[
            (df_base_online['Intervalo de Tempo'].fillna('').astype(str) == janela_sel) & 
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
                        st.markdown(f"##### **{str(super_nome).upper()}** <span style='float:right; background-color:#ffe6e6; color:#b30000; padding:1px 6px; border-radius:4px; font-size:12px;'>Contratos: {len(df_cards_sup)}</span>", unsafe_allow_html=True)
                        
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
            st.info(f"✨ Nenhuma certidão pendente (NOK) Iniciada/Concluída no intervalo: **{janela_sel}**.")
    else:
        st.info("ℹ️ Nenhum contrato NOK registrado no sistema.")
else:
    st.info("ℹ️ Aguardando dados operacionais.")

st.markdown("---")

# ==========================================
# BLOCO 3: HISTÓRICO COMPLETO ACUMULADO (Aba/Expander Ocultável)
# ==========================================
with st.expander("📊 Clique aqui para abrir o Histórico Completo de Auditoria"):
    if not df_banco_atual.empty:
        busca_historico = st.text_input("🔍 Buscar no histórico (por Contrato):", key="search_hist")
        df_hist_tela = df_banco_atual[df_banco_atual["Contrato"].str.contains(busca_historico, case=False, na=False)] if busca_historico else df_banco_atual
        
        st.dataframe(df_hist_tela, use_container_width=True, hide_index=True)
        
        csv_download = df_banco_atual.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Planilha de Auditoria (CSV)", data=csv_download, file_name="auditoria_certidoes.csv", mime="text/csv")
    else:
        st.info("Nenhum registro gravado no banco de dados local.")

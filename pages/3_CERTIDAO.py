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

st.markdown('<h1 style="font-size: 38px; font-weight: 900; color: #008080; text-align: center; margin-top: 25px; margin-bottom: 5px;">📜 SISTEMA DE CERTIDÃO</h1>', unsafe_allow_html=True)

# === BANCO DE DADOS LOCAL (ARQUIVO PERMANENTE DE REGISTROS) ===
ARQUIVO_BANCO = "banco_certidoes.csv"

def carregar_banco_historico():
    colunas_padrao = ["Data/Hora", "Contrato", "Status", "Supervisor", "Recurso", "Intervalo de Tempo"]
    if os.path.exists(ARQUIVO_BANCO):
        try:
            df_hist = pd.read_csv(ARQUIVO_BANCO, dtype=str)
            df_hist = df_hist[[c for c in df_hist.columns if c in colunas_padrao]]
            for col in colunas_padrao:
                if col not in df_hist.columns:
                    df_hist[col] = "N/A"
            return df_hist
        except:
            return pd.DataFrame(columns=colunas_padrao)
    return pd.DataFrame(columns=colunas_padrao)

# === FUNÇÃO DE CARGA OPERACIONAL ONLINE ===
def buscar_base_rotas_online():
    try:
        url = st.secrets.get('public_gsheets_url', "https://docs.google.com/spreadsheets/d/1kB1YmUuhzHpfN1dLv8PaQn0ipXcHcd6kGKnI3nguT14/edit?gid=208394608#gid=208394608").strip()
        if 'spreadsheets/d/' in url:
            id_planilha = url.split('/spreadsheets/d/')[1].split('/')[0].strip()
            csv_url = f"https://docs.google.com/spreadsheets/d/{id_planilha}/export?format=csv"
            if 'gid=' in url:
                gid = url.split('gid=')[1].split('#')[0].split('&')[0].strip()
                csv_url += f"&gid={gid}"
        else:
            csv_url = url

        headers = {'User-Agent': 'Mozilla/5.0'}
        resposta = requests.get(csv_url, headers=headers, timeout=15)
        if resposta.status_code != 200:
            return None
            
        data_header = resposta.headers.get('Date')
        if data_header:
            try:
                dt_gmt = pd.to_datetime(data_header)
                if dt_gmt.tz is None:
                    dt_brasil = dt_gmt.tz_localize('UTC').tz_convert('America/Sao_Paulo')
                else:
                    dt_brasil = dt_gmt.tz_convert('America/Sao_Paulo')
                st.session_state['data_da_rota'] = dt_brasil.strftime('%d/%m/%Y às %H:%M:%S')
            except:
                st.session_state['data_da_rota'] = datetime.now().strftime('%d/%m/%Y às %H:%M:%S')
        else:
            st.session_state['data_da_rota'] = datetime.now().strftime('%d/%m/%Y às %H:%M:%S')

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
            if 'SUPERVISOR' in col_upper and 'SUPERVISOR' not in colunas_mapeadas.values(): 
                colunas_mapeadas[col] = 'SUPERVISOR'
            elif ('INTERVALO' in col_upper or 'TEMPO' in col_upper) and 'Intervalo de Tempo' not in colunas_mapeadas.values(): 
                colunas_mapeadas[col] = 'Intervalo de Tempo'
            elif 'STATUS DA ATIVIDADE' in col_upper or ('STATUS' in col_upper and 'ATIVIDADE' in col_upper) and 'Status da Atividade' not in colunas_mapeadas.values(): 
                colunas_mapeadas[col] = 'Status da Atividade'
            elif ('STATUS DA O.S 1' in col_upper or 'O.S 1' in col_upper or 'OS 1' in col_upper) and 'Status da O.S 1' not in colunas_mapeadas.values(): 
                colunas_mapeadas[col] = 'Status da O.S 1'
            elif 'CONTRATO' in col_upper and 'Contrato' not in colunas_mapeadas.values(): 
                colunas_mapeadas[col] = 'Contrato'
            elif ('RECURSO' in col_upper or 'TECNICO' in col_upper or 'TÉCNICO' in col_upper) and 'Recurso' not in colunas_mapeadas.values():
                colunas_mapeadas[col] = 'Recurso'
        
        df_final = df_final.rename(columns=colunas_mapeadas)
        df_final = df_final.loc[:, ~df_final.columns.duplicated()]

        if 'Intervalo de Tempo' not in df_final.columns: df_final['Intervalo de Tempo'] = 'Padrão / Sem Janela'
        if 'Status da Atividade' not in df_final.columns: df_final['Status da Atividade'] = 'PENDENTE'
        if 'Status da O.S 1' not in df_final.columns: df_final['Status da O.S 1'] = 'NÃO EXECUTADO'
        if 'SUPERVISOR' not in df_final.columns: df_final['SUPERVISOR'] = 'N/A'
        if 'Recurso' not in df_final.columns: df_final['Recurso'] = 'Técnico Não Identificado'
        if 'Contrato' not in df_final.columns: df_final = df_final.rename(columns={df_final.columns[0]: 'Contrato'})
            
        return df_final
    except:
        return None

if "historico_certidoes" not in st.session_state:
    st.session_state["historico_certidoes"] = carregar_banco_historico()

if "input_contrato_value" not in st.session_state:
    st.session_state["input_contrato_value"] = ""

df_base_online = buscar_base_rotas_online()

# --- EXIBIÇÃO DA DATA DE ATUALIZAÇÃO SINCADA ---
data_rota_texto = st.session_state.get('data_da_rota', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
st.markdown(f'<div style="text-align: center; color: #555; font-size: 13px; font-weight: bold; margin-bottom: 20px;">🔄 Base sincronizada em: <span style="color: #008080;">{data_rota_texto}</span></div>', unsafe_allow_html=True)

# --- MONTAGEM DO FILTRO LATERAL ---
janela_sel = "Padrão / Sem Janela"
if df_base_online is not None:
    try:
        opcoes_janela = sorted(df_base_online['Intervalo de Tempo'].dropna().astype(str).unique())
        if opcoes_janela:
            janela_sel = st.sidebar.selectbox("Intervalo de Tempo Ativo:", opcoes_janela)
    except:
        pass

# ==========================================
# BLOCO 1: FORMULÁRIO DE ENTRADA
# ==========================================
with st.container(border=True):
    st.markdown("#### 📥 Verificar e Registrar Contrato")
    col1, col2 = st.columns([3, 2])

    with col1:
        contrato_input = st.text_input(
            "Número do Contrato:", 
            value=st.session_state["input_contrato_value"],
            placeholder="Digite o contrato e pressione Enter..."
        ).strip()

    status_sugerido = "OK"  
    supervisor_detectado = "N/A"
    tecnico_detectado = "N/A"
    detalhes_validacao = ""

    if contrato_input and df_base_online is not None and 'Contrato' in df_base_online.columns:
        df_base_online['Contrato_Limpo'] = df_base_online['Contrato'].fillna('').astype(str).apply(lambda x: x.split('.')[0].strip())
        contrato_encontrado = df_base_online[df_base_online['Contrato_Limpo'] == contrato_input]
        
        if not contrato_encontrado.empty:
            linha_contrato = contrato_encontrado.iloc[0]
            supervisor_detectado = str(linha_contrato.get('SUPERVISOR', 'N/A')).upper()
            tecnico_detectado = str(linha_contrato.get('Recurso', 'N/A')).upper()
            status_os1 = str(linha_contrato.get('Status da O.S 1', '')).upper().strip()
            detalhes_validacao = f"📋 Encontrado | Técnico: {tecnico_detectado} | Posição O.S 1: {status_os1}"
        else:
            detalhes_validacao = "❌ Contrato não localizado na base online de hoje."

    if contrato_input:
        st.caption(detalhes_validacao)

    with col2:
        opcoes_status = ["OK", "NOK", "NÃO ADERENTE"]
        status_final = st.selectbox("Resultado da Verificação:", opcoes_status)

    if st.button("💾 Gravar e Certificar Contrato", type="primary", use_container_width=True):
        if contrato_input != "":
            agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            nova_linha = pd.DataFrame([{
                "Data/Hora": agora, "Contrato": contrato_input, "Status": status_final,
                "Supervisor": supervisor_detectado, "Recurso": tecnico_detectado,
                "Intervalo de Tempo": janela_sel
            }])
            
            df_total = pd.concat([nova_linha, st.session_state["historico_certidoes"]], ignore_index=True)
            df_total = df_total.drop_duplicates(subset=["Contrato"], keep="first")
            
            st.session_state["historico_certidoes"] = df_total
            st.session_state["historico_certidoes"].to_csv(ARQUIVO_BANCO, index=False)
            
            st.session_state["input_contrato_value"] = ""
            
            st.success(f"✅ Contrato {contrato_input} atualizado como {status_final}!")
            st.rerun()
        else:
            st.warning("⚠️ Digite um contrato válido antes de salvar.")

st.markdown("---")

# ==========================================
# BLOCO 2: PAINEL DE PENDENTES
# ==========================================
st.markdown("### 🗂️ CERTIDÃO PENDENTES")

df_banco_atual = st.session_state["historico_certidoes"]

if df_base_online is not None:
    df_base_online['Contrato_Limpo'] = df_base_online['Contrato'].fillna('').astype(str).apply(lambda x: x.split('.')[0].strip())
    df_base_online['Intervalo_Limpo'] = df_base_online['Intervalo de Tempo'].fillna('').astype(str).str.strip()
    df_base_online['Status_Atividade_Limpo'] = df_base_online['Status da Atividade'].fillna('').astype(str).str.upper().str.strip()
    
    cond_janela = df_base_online['Intervalo_Limpo'] == janela_sel.strip()
    cond_ativ = df_base_online['Status_Atividade_Limpo'].isin(['INICIADO', 'CONCLUIDO', 'CONCLUÍDO'])
    
    df_base_filtrada = df_base_online[cond_janela & cond_ativ]
    
    if not df_banco_atual.empty:
        contratos_validados = df_banco_atual[df_banco_atual["Status"].str.upper().isin(["OK", "NÃO ADERENTE"])]["Contrato"].tolist()
        df_exibir_pendentes = df_base_filtrada[~df_base_filtrada['Contrato_Limpo'].isin(contratos_validados)]
    else:
        df_exibir_pendentes = df_base_filtrada

    if not df_exibir_pendentes.empty:
        supervisores_na_tela = sorted(df_exibir_pendentes['SUPERVISOR'].dropna().unique())
        cols_supervisores = st.columns(len(supervisores_na_tela) if len(supervisores_na_tela) > 0 else 1)
        
        for idx_sup, super_nome in enumerate(supervisores_na_tela):
            with cols_supervisores[idx_sup % len(cols_supervisores)]:
                with st.container(border=True):
                    df_cards_sup = df_exibir_pendentes[df_exibir_pendentes['SUPERVISOR'] == super_nome]
                    st.markdown(f"##### **{str(super_nome).upper()}** <span style='float:right; background-color:#ffe6e6; color:#b30000; padding:1px 6px; border-radius:4px; font-size:12px;'>Pendentes: {len(df_cards_sup)}</span>", unsafe_allow_html=True)
                    
                    for _, row_p in df_cards_sup.iterrows():
                        c_num = str(row_p['Contrato_Limpo'])
                        status_real_campo = str(row_p['Status_Atividade_Limpo'])
                        nome_tec = str(row_p['Recurso'])[:12].upper()
                        
                        if "CONCLU" in status_real_campo:
                            bg_color = "#2e7d32"     
                            txt_status = "CONCLUÍDO"
                        else:
                            bg_color = "#ff9800"     
                            txt_status = "INICIADO"
                        
                        st.markdown(f"""
                            <div style="display:flex; justify-content:space-between; align-items:center; background-color:#f9f9f9; padding:5px 8px; border:1px solid #e0e0e0; border-radius:4px; margin-bottom:4px;">
                                <div style="display:flex; align-items:center; gap:6px;">
                                    <span style="font-weight:900; color:#333; font-size:13px;">📄 {c_num}</span>
                                    <span style="background-color:{bg_color}; color:white; font-size:9px; font-weight:900; padding:2px 6px; border-radius:4px; letter-spacing:0.3px;">{txt_status}</span>
                                </div>
                                <span style="color:#555; font-size:11px; font-weight:700; text-transform:uppercase;">👤 {nome_tec}</span>
                            </div>
                        """, unsafe_allow_html=True)
    else:
        st.info(f"✨ Todas as certidões deste intervalo foram validadas! Nenhuma pendência encontrada para: **{janela_sel}**.")
else:
    st.info("ℹ️ Aguardando conexão com os dados online.")

st.markdown("---")

# ==========================================
# BLOCO 3: HISTÓRICO
# ==========================================
with st.expander("📊 Histórico Base de Auditoria (Última Posição dos Contratos Verificados)"):
    if not df_banco_atual.empty:
        df_historico_clean = df_banco_atual[["Contrato", "Recurso", "Supervisor", "Status", "Data/Hora"]]
        df_historico_clean.columns = ["Contrato", "Técnico", "Supervisor", "Status da Certidão", "Data/Hora Registro"]
        
        st.dataframe(df_historico_clean, use_container_width=True, hide_index=True)
        
        csv_download = df_banco_atual.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Planilha de Auditoria (CSV)", data=csv_download, file_name="auditoria_certidoes.csv", mime="text/csv")
    else:
        st.info("Nenhum registro gravado no banco de dados local.")

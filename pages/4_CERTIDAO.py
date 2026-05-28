import streamlit as st
import pandas as pd
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
    colunas_padrao = ["Data/Hora", "Contrato", "Status", "Supervisor", "Recurso", "Intervalo de Tempo", "Observação"]
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

if "historico_certidoes" not in st.session_state:
    st.session_state["historico_certidoes"] = carregar_banco_historico()

if "input_contrato_value" not in st.session_state:
    st.session_state["input_contrato_value"] = ""

# 🔄 HERANÇA INTELIGENTE
df_master = st.session_state.get('df_rota_ativa', None)

df_base_online = None
if df_master is not None and not df_master.empty:
    # 🌟 CORREÇÃO CRÍTICA: Força o Pandas a criar um objeto 100% novo na memória, evitando o ValueError
    df_base_online = df_master.copy(deep=True)
    
    # Padronização e mapeamento seguro das colunas internas
    df_base_online['Contrato'] = df_base_online['Contrato'].fillna('').astype(str).str.strip()
    
    col_janela = 'Janela de Serviço' if 'Janela de Serviço' in df_base_online.columns else 'Intervalo de Tempo'
    df_base_online['Intervalo de Tempo'] = df_base_online[col_janela].fillna('Padrão / Sem Janela').astype(str).str.strip()
    
    col_status_at = 'STATUS_ATIVIDADE' if 'STATUS_ATIVIDADE' in df_base_online.columns else 'Status da Atividade'
    df_base_online['Status da Atividade'] = df_base_online[col_status_at].fillna('PENDENTE').astype(str).str.upper().str.strip()
    
    # Criação segura usando indexação direta do Pandas
    if 'STATUS_OS1' in df_base_online.columns:
        df_base_online['Status da O.S 1'] = df_base_online['STATUS_OS1'].fillna('NÃO EXECUTADO')
    else:
        df_base_online['Status da O.S 1'] = 'NÃO EXECUTADO'
        
    df_base_online['Recurso'] = df_base_online['Recurso'].fillna('Técnico Não Identificado')

# --- EXIBIÇÃO DA DATA DE ATUALIZAÇÃO SINCADA ---
data_rota_texto = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
if df_base_online is not None:
    st.markdown(f'<div style="text-align: center; color: #555; font-size: 13px; font-weight: bold; margin-bottom: 20px;">🔄 Base sincronizada em tempo real via Upload de hoje</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div style="text-align: center; color: #555; font-size: 13px; font-weight: bold; margin-bottom: 20px;">⚠️ Aguardando upload dos arquivos na página inicial</div>', unsafe_allow_html=True)

# --- MONTAGEM DO FILTRO LATERAL ---
janela_sel = "Padrão / Sem Janela"
if df_base_online is not None:
    try:
        opcoes_janela = sorted([j for j in df_base_online['Intervalo de Tempo'].unique() if len(j) <= 15])
        if opcoes_janela:
            janela_sel = st.sidebar.selectbox("Intervalo de Tempo Ativo:", opcoes_janela)
    except:
        pass

# ==========================================
# BLOCO 1: FORMULÁRIO DE ENTRADA
# ==========================================
with st.container(border=True):
    st.markdown("#### 📥 Verificar e Registrar Contrato")
    col1, col2, col3 = st.columns([2, 2, 3])

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
            supervisor_detectado = str(linha_contrato.get('SUPERVISOR', 'N/A')).upper().strip()
            tecnico_detectado = str(linha_contrato.get('Recurso', 'N/A')).upper().strip()
            status_os1 = str(linha_contrato.get('Status da O.S 1', '')).upper().strip()
            
            if "NAME:" in status_os1:
                status_os1 = status_os1.split("NAME:")[0].strip()
            detalhes_validacao = f"📋 Encontrado | Técnico: {tecnico_detectado} | Status de Campo: {status_os1}"
        else:
            detalhes_validacao = "❌ Contrato não localizado na base de upload de hoje."

    if contrato_input:
        st.caption(detalhes_validacao)

    with col2:
        opcoes_status = ["OK", "NOK", "NÃO ADERENTE"]
        status_final = st.selectbox("Resultado da Verificação:", opcoes_status)
        
    with col3:
        obs_input = st.text_input("Observações / Motivo:", placeholder="Insira notas adicionais aqui...").strip()

    if st.button("💾 Gravar e Certificar Contrato", type="primary", use_container_width=True):
        if contrato_input != "":
            agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            nova_linha = pd.DataFrame([{
                "Data/Hora": agora, "Contrato": contrato_input, "Status": status_final,
                "Supervisor": supervisor_detectado, "Recurso": tecnico_detectado,
                "Intervalo de Tempo": janela_sel, "Observação": obs_input if obs_input != "" else "OK"
            }])
            
            df_total = pd.concat([nova_linha, st.session_state["historico_certidoes"]], ignore_index=True)
            df_total = df_total.drop_duplicates(subset=["Contrato"], keep="first")
            
            st.session_state["historico_certidoes"] = df_total
            st.session_state["historico_certidoes"].to_csv(ARQUIVO_BANCO, index=False)
            
            st.session_state["input_contrato_value"] = ""
            
            st.success(f"✅ Contrato {contrato_input} updated como {status_final}!")
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
    cond_ativ = df_base_online['Status_Atividade_Limpo'].str.contains("CONCLU") | df_base_online['Status_Atividade_Limpo'].str.contains("INIC")
    
    df_base_filtrada = df_base_online[cond_janela & cond_ativ]
    
    if not df_banco_atual.empty:
        contratos_validados = df_banco_atual[df_banco_atual["Status"].str.upper().isin(["OK", "NÃO ADERENTE"])]["Contrato"].tolist()
        df_exibir_pendentes = df_base_filtrada[~df_base_filtrada['Contrato_Limpo'].isin(contratos_validados)]
    else:
        df_exibir_pendentes = df_base_filtrada

    if not df_exibir_pendentes.empty:
        df_exibir_pendentes = df_exibir_pendentes[df_exibir_pendentes['SUPERVISOR'].fillna('').astype(str).str.strip() != ''].copy()
        supervisores_na_tela = sorted(df_exibir_pendentes['SUPERVISOR'].dropna().unique())
        
        cols_supervisores = st.columns(len(supervisores_na_tela) if len(supervisores_na_tela) > 0 else 1)
        
        for idx_sup, super_nome in enumerate(supervisores_na_tela):
            with cols_supervisores[idx_sup % len(cols_supervisores)]:
                with st.container(border=True):
                    df_cards_sup = df_exibir_pendentes[df_exibir_pendentes['SUPERVISOR'] == super_nome]
                    st.markdown(f"##### **{str(super_nome).upper()}** <span style='float:right; background-color:#ffe6e6; color:#b30000; padding:1px 6px; border-radius:4px; font-size:12px;'>Pendentes: {len(df_cards_sup)}</span>", unsafe_allow_html=True)
                    
                    lista_contratos_reais = [str(c) for c in df_cards_sup['Contrato_Limpo'].unique() if str(c) != '']
                    texto_copia_em_lote = ", ".join(lista_contratos_reais)
                    
                    st.code(texto_copia_em_lote, language="text")
                    st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)
                    
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
                            <div style="display:flex; justify-content:space-between; align-items:center; background-color:#f9f9f9; padding:6px 10px; border:1px solid #e0e0e0; border-radius:4px; margin-bottom:4px;">
                                <div style="font-size:13px; color:#333; font-weight:700;">
                                    <span style="font-family:monospace; color:#111; font-size:13px; font-weight:bold;">{c_num}</span>
                                    <span> - 👤 {nome_tec}</span>
                                </div>
                                <span style="background-color:{bg_color}; color:white; font-size:9px; font-weight:900; padding:2px 6px; border-radius:4px;">{txt_status}</span>
                            </div>
                        """, unsafe_allow_html=True)
    else:
        st.info(f"✨ Todas as certidões deste intervalo foram validadas! Nenhuma pendência encontrada para: **{janela_sel}**.")
else:
    st.info("ℹ️ Aguardando o upload dos dados operacionais na página inicial.")

st.markdown("---")

# ==========================================
# BLOCO 3: HISTÓRICO
# ==========================================
with st.expander("📊 Histórico Base de Auditoria (Última Posição dos Contratos Verificados)"):
    if not df_banco_atual.empty:
        st.dataframe(df_banco_atual, use_container_width=True, hide_index=True)
        
        csv_download = df_banco_atual.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Planilha de Auditoria (CSV)", data=csv_download, file_name="auditoria_certidoes.csv", mime="text/csv")
    else:
        st.info("Nenhum registro gravado no banco de dados local.")

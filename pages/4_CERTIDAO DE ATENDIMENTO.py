import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_gsheets_connection import GSheetsConnection

# 1. Configuração da página
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 2. Carregar Estilos Globais
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

st.markdown('<h1 style="font-size: 38px; font-weight: 900; color: #008080; text-align: center; margin-top: 25px; margin-bottom: 5px;">📜 CERTIDÃO DE ATENDIMENTO</h1>', unsafe_allow_html=True)

# === CONEXÃO DIRETA COM O GOOGLE SHEETS (NUVEM) ===
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("⚠️ Erro de conexão com o Google Sheets. Verifique se configurou o Secrets corretamente.")
    st.stop()

def carregar_banco_historico_sheets():
    colunas_padrao = ["Data/Hora", "Contrato", "Status", "Supervisor", "Recurso", "Intervalo de Tempo", "Observação"]
    try:
        # Lê os dados em tempo real da aba 'Certidoes'
        df_hist = conn.read(worksheet="Certidoes", ttl="0d", dtype=str)
        if df_hist is not None and not df_hist.empty:
            df_hist = df_hist[[c for c in df_hist.columns if c in colunas_padrao]]
            for col in colunas_padrao:
                if col not in df_hist.columns:
                    df_hist[col] = "N/A"
            return df_hist
    except:
        pass
    return pd.DataFrame(columns=colunas_padrao)

# Carrega sempre a versão mais recente da nuvem para o estado da sessão
st.session_state["historico_certidoes"] = carregar_banco_historico_sheets()

# 🌟 Estado para controle de limpeza do input
if "limpar_input_proxima" not in st.session_state:
    st.session_state["limpar_input_proxima"] = False

# 🔄 HERANÇA INTELIGENTE
df_master = st.session_state.get('df_rota_ativa', None)

df_base_online = None
if df_master is not None and not df_master.empty:
    col_janela = 'Janela de Serviço' if 'Janela de Serviço' in df_master.columns else 'Intervalo de Tempo'
    col_status_at = 'STATUS_ATIVIDADE' if 'STATUS_ATIVIDADE' in df_master.columns else 'Status da Atividade'
    
    lista_contrato = [str(x).strip() for x in pd.DataFrame(df_master['Contrato']).iloc[:, 0].fillna('').tolist()]
    
    if col_janela in df_master.columns:
        lista_janela = [str(x).strip() for x in pd.DataFrame(df_master[col_janela]).iloc[:, 0].fillna('Padrão / Sem Janela').tolist()]
    else:
        lista_janela = ['Padrão / Sem Janela'] * len(df_master)
        
    if col_status_at in df_master.columns:
        lista_status_at = [str(x).upper().strip() for x in pd.DataFrame(df_master[col_status_at]).iloc[:, 0].fillna('PENDENTE').tolist()]
    else:
        lista_status_at = ['PENDENTE'] * len(df_master)
        
    if 'STATUS_OS1' in df_master.columns:
        lista_status_os1 = [str(x).strip() for x in pd.DataFrame(df_master['STATUS_OS1']).iloc[:, 0].fillna('NÃO EXECUTADO').tolist()]
    else:
        lista_status_os1 = ['NÃO EXECUTADO'] * len(df_master)
        
    lista_recurso = [str(x).strip() for x in pd.DataFrame(df_master['Recurso']).iloc[:, 0].fillna('Técnico Não Identificado').tolist()] if 'Recurso' in df_master.columns else ['Técnico Não Identificado'] * len(df_master)
    lista_supervisor = [str(x).strip() for x in pd.DataFrame(df_master['SUPERVISOR']).iloc[:, 0].fillna('N/A').tolist()] if 'SUPERVISOR' in df_master.columns else ['N/A'] * len(df_master)

    df_base_online = pd.DataFrame({
        'Contrato': lista_contrato,
        'Intervalo de Tempo': lista_janela,
        'Status da Atividade': lista_status_at,
        'Status da O.S 1': lista_status_os1,
        'Recurso': lista_recurso,
        'SUPERVISOR': lista_supervisor
    })

# === AUTOMATIZAÇÃO DAS JANELAS (FUSO BRASÍLIA) ===
hora_brasilia = (datetime.utcnow() - timedelta(hours=3)).hour

if hora_brasilia < 11:
    janelas_automaticas = ['08 - 10', '08 - 11', '08 - 12', '08:00 - 08:03']
    texto_status_janela = f"⏰ [Hora Local: {hora_brasilia:02d}h] - Focado: Janelas da Manhã"
elif 11 <= hora_brasilia < 15:
    janelas_automaticas = ['08 - 10', '08 - 11', '08 - 12', '08:00 - 08:03', '11 - 14', '11:50 - 14:50', '12:00 - 15:00']
    texto_status_janela = f"⏰ [Hora Local: {hora_brasilia:02d}h] - Janela do Meio do Dia + Pendências da Manhã"
else:
    janelas_automaticas = ['08 - 10', '08 - 11', '08 - 12', '08:00 - 08:03', '11 - 14', '11:50 - 14:50', '12:00 - 15:00', '15 - 18']
    texto_status_janela = f"⏰ [Hora Local: {hora_brasilia:02d}h] - Tarde Ativa + Tudo Acumulado Pendente do Dia"

# --- EXIBIÇÃO DA DATA DE ATUALIZAÇÃO SINCADA ---
if df_base_online is not None:
    st.markdown(f'<div style="text-align: center; color: #cc6600; font-size: 14px; font-weight: bold; margin-bottom: 20px;">{texto_status_janela}</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div style="text-align: center; color: #cc6600; font-size: 13px; font-weight: bold; margin-bottom: 20px;">⚠️ Aguardando upload dos arquivos na página inicial</div>', unsafe_allow_html=True)

janela_sel = "AUTOMÁTICO"

# ==========================================
# BLOCO 1: FORMULÁRIO DE ENTRADA
# ==========================================
with st.container(border=True):
    st.markdown("#### 📥 Verificar e Registrar Contrato")
    col1, col2, col3 = st.columns([2, 2, 3])

    with col1:
        valor_padrao_input = "" if st.session_state["limpar_input_proxima"] else st.session_state.get("contrato_antigo_digitado", "")
        
        contrato_input = st.text_input(
            "Número do Contrato:", 
            value=valor_padrao_input,
            placeholder="Digite o contrato e pressione Enter..."
        ).strip()
        
        st.session_state["limpar_input_proxima"] = False
        st.session_state["contrato_antigo_digitado"] = contrato_input

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
                "Intervalo de Tempo": "AUTOMÁTICO", "Observação": obs_input if obs_input != "" else "OK"
            }])
            
            # Combina o novo registro com o histórico vindo direto do Google Sheets
            df_total = pd.concat([nova_linha, st.session_state["historico_certidoes"]], ignore_index=True)
            df_total = df_total.drop_duplicates(subset=["Contrato"], keep="first")
            
            try:
                # GRAVAÇÃO NA PLANILHA DA NUVEM (Aba Certidoes)
                conn.update(worksheet="Certidoes", data=df_total)
                st.session_state["historico_certidoes"] = df_total
                
                st.session_state["limpar_input_proxima"] = True
                st.session_state["contrato_antigo_digitado"] = ""
                
                st.success(f"✅ Contrato {contrato_input} gravado com sucesso na nuvem!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro ao salvar dados na planilha do Google: {e}")
        else:
            st.warning("⚠️ Digite um contrato válido antes de salvar.")

st.markdown("---")

# ==========================================
# BLOCO 2: PAINEL DE PENDENTES AUTOMÁTICO
# ==========================================
st.markdown("### 🗂️ CERTIDÃO PENDENTES")

df_banco_atual = st.session_state["historico_certidoes"]

if df_base_online is not None:
    df_base_online['Contrato_Limpo'] = df_base_online['Contrato'].fillna('').astype(str).apply(lambda x: x.split('.')[0].strip())
    df_base_online['Intervalo_Limpo'] = df_base_online['Intervalo de Tempo'].fillna('').astype(str).str.strip()
    df_base_online['Status_Atividade_Limpo'] = df_base_online['Status da Atividade'].fillna('').astype(str).str.upper().str.strip()
    
    cond_janela = df_base_online['Intervalo_Limpo'].isin(janelas_automaticas)
    cond_ativ = (
        df_base_online['Status_Atividade_Limpo'].str.contains("CONCLU", na=False) | 
        df_base_online['Status_Atividade_Limpo'].str.contains("INIC", na=False)
    )
    
    df_base_filtrada = df_base_online[cond_janela & cond_ativ]
    
    if not df_banco_atual.empty:
        # Garante a filtragem correta tratando os números como string pura
        df_banco_atual['Contrato_Str'] = df_banco_atual['Contrato'].fillna('').astype(str).apply(lambda x: x.split('.')[0].strip())
        contratos_validados = df_banco_atual[df_banco_atual["Status"].str.upper().isin(["OK", "NÃO ADERENTE"])]["Contrato_Str"].tolist()
        df_exibir_pendentes = df_base_filtrada[~df_base_filtrada['Contrato_Limpo'].isin(contratos_validados)]
    else:
        df_exibir_pendentes = df_base_filtrada

    if not df_exibir_pendentes.empty:
        df_exibir_pendentes = df_exibir_pendentes[~df_exibir_pendentes['SUPERVISOR'].fillna('').astype(str).str.upper().str.strip().isin(['', 'N/A', 'NAN', '#N/A'])].copy()
        supervisores_na_tela = sorted(df_exibir_pendentes['SUPERVISOR'].dropna().unique())
        
        cols_supervisores = st.columns(len(supervisores_na_tela) if len(supervisores_na_tela) > 0 else 1)
        
        for idx_sup, super_nome in enumerate(supervisores_na_tela):
            with cols_supervisores[idx_sup % len(cols_supervisores)]:
                with st.container(border=True):
                    df_cards_sup = df_exibir_pendentes[df_exibir_pendentes['SUPERVISOR'] == super_nome]
                    st.markdown(f"##### **{str(super_nome).upper()}** <span style='float:right; background-color:#ffe6e6; color:#b30000; padding:1px 6px; border-radius:4px; font-size:12px;'>Pendentes: {len(df_cards_sup)}</span>", unsafe_allow_html=True)
                    
                    lista_elementos_copia = []
                    for _, row_c in df_cards_sup.iterrows():
                        c_num_c = str(row_c['Contrato_Limpo'])
                        nome_tec_c = str(row_c['Recurso']).strip().split()[0].upper()
                        if c_num_c != '':
                            lista_elementos_copia.append(f"{c_num_c} {nome_tec_c}")
                    
                    texto_copia_em_lote = "\n".join(lista_elementos_copia)
                    
                    st.code(texto_copia_em_lote, language="text", height=100)
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
        st.info("✨ Todas as certidões produzidas (Iniciadas/Concluídas) até o momento foram validadas!")
else:
    st.info("ℹ️ Aguardando o upload dos dados operacionais na página inicial.")

st.markdown("---")

# ==========================================
# BLOCO 3: HISTÓRICO VIA GOOGLE SHEETS
# ==========================================
with st.expander("📊 Histórico Base de Auditoria Nuvem (Planilha Google Sheets)"):
    if not df_banco_atual.empty:
        st.dataframe(df_banco_atual, use_container_width=True, hide_index=True)
        
        csv_download = df_banco_atual.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Planilha de Auditoria (CSV)", data=csv_download, file_name="auditoria_certidoes.csv", mime="text/csv")
    else:
        st.info("Nenhum registro gravado na planilha em nuvem ainda.")

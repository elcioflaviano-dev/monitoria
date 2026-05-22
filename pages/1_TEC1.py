import streamlit as st
import pandas as pd
from urllib.parse import quote, unquote

# 1. Configuração da página
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# 2. Carregar CSS de forma segura
css_conteudo = ""
try:
    with open("style.css", "r") as f:
        css_conteudo = f.read()
except:
    pass

if css_conteudo:
    st.markdown(f"<style>{css_conteudo}</style>", unsafe_allow_html=True)

st.markdown('<h1 style="font-size: 42px; font-weight: 900; color: #006677; text-align: center; margin-top: 25px; margin-bottom: 20px;">TEC1</h1>', unsafe_allow_html=True)

# === MÓDULO DE CARGA OPERACIONAL ===
def carregar_dados_sheets():
    try:
        url = st.secrets["public_gsheets_url"]
        
        if "/edit" in url:
            csv_url = url.split("/edit")[0] + "/gviz/tq?tqx=out:csv"
            if "gid=" in url:
                gid = url.split("gid=")[1].split("&")[0]
                csv_url += "&gid=" + gid
        else:
            csv_url = url

        df_sheets = pd.read_csv(csv_url)
        
        # CORREÇÃO INTEGRAL: Limpa nomes de colunas de forma nativa e segura
        df_sheets.columns = [str(c).strip() for c in df_sheets.columns]
        
        colunas_mapeadas = {}
        for col in df_sheets.columns:
            col_upper = col.upper()
            if "SUPERVISOR" in col_upper: colunas_mapeadas[col] = "SUPERVISOR"
            elif "JANELA" in col_upper: colunas_mapeadas[col] = "JANELA_SERVICO"
            elif "STATUS" in col_upper: colunas_mapeadas[col] = "STATUS_ATIVIDADE"
            elif "CONTRATO" in col_upper: colunas_mapeadas[col] = "CONTRATO"
            elif "RECURSO" in col_upper: colunas_mapeadas[col] = "RECURSO"
            
        df = df_sheets.rename(columns=colunas_mapeadas)
        
        for col_obrigatoria in ["SUPERVISOR", "JANELA_SERVICO", "STATUS_ATIVIDADE"]:
            if col_obrigatoria not in df.columns:
                df[col_obrigatoria] = "N/A"
                
        df["STATUS_ATIVIDADE"] = df["STATUS_ATIVIDADE"].astype(str).str.strip().str.upper()
        return df
    except Exception as e:
        st.error("Erro na leitura do link: " + str(e))
        return None

df = carregar_dados_sheets()

if df is not None:
    # --- FILTRO DE JANELA ---
    col_janela = 'JANELA_SERVICO'
    janela_selecionada = unquote(st.query_params.get("janela", ""))

    if col_janela in df.columns and not df.empty:
        opcoes_janela = sorted(df[col_janela].dropna().astype(str).unique())
        if not opcoes_janela:
            opcoes_janela = ["Sem Janelas"]
            
        default_index = 0
        if janela_selecionada in opcoes_janela:
            default_index = opcoes_janela.index(janela_selecionada)
        
        st.sidebar.markdown("### Filtros Operacionais")
        janela_sel = st.sidebar.selectbox(
            "Janela de Serviço Ativa:", 
            opcoes_janela, 
            index=default_index,
            key="sb_janela"
        )
        
        st.query_params["janela"] = janela_sel
        df_tela = df[df[col_janela] == janela_sel]
    else:
        df_tela = df.copy()

    # --- LÓGICA DE SUPERVISORES (ABC | SP) ---
    col_supervisor = 'SUPERVISOR'
    df_abc_lista, df_sp_lista = [], []
    
    if col_supervisor in df_tela.columns and not df_tela.empty:
        for idx, linha in df_tela.iterrows():
            nome_super = str(linha[col_supervisor]).upper()
            if "FRANCISCO" in nome_super or "ALAN" in nome_super: 
                df_sp_lista.append(linha)
            else: 
                df_abc_lista.append(linha)
                
        df_abc = pd.DataFrame(df_abc_lista) if df_abc_lista else pd.DataFrame(columns=df_tela.columns)
        df_sp = pd.DataFrame(df_sp_lista) if df_sp_lista else pd.DataFrame(columns=df_tela.columns)
    else:
        df_abc, df_sp = pd.DataFrame(columns=df.columns), pd.DataFrame(columns=df.columns)

    # --- CORPO VISUAL ---
    c_abc, c_sp = st.columns(2)
    with c_abc:
        st.markdown('<div class="title-abc-sp">ABC</div>', unsafe_allow_html=True)
        if not df_abc.empty:
            for supervisor in sorted(df_abc[col_supervisor].dropna().unique()):
                df_super = df_abc[df_abc[col_supervisor] == supervisor]
                p = len(df_super[df_super['STATUS_ATIVIDADE'] == 'PENDENTE']) if 'STATUS_ATIVIDADE' in df_super.columns else 0
                r = len(df_super[df_super['STATUS_ATIVIDADE'] == 'EM ROTA']) if 'STATUS_ATIVIDADE' in df_super.columns else 0
                i = len(df_super[df_super['STATUS_ATIVIDADE'] == 'INICIADO']) if 'STATUS_ATIVIDADE' in df_super.columns else 0
                t = len(df_super)
                
                with st.container(border=True):
                    header_texto = "#### **" + str(supervisor).upper() + "** <span style='float:right; font-size:14px; background-color:#e1f5fe; padding:2px 8px; border-radius:4px; color:#0288d1;'>Total: " + str(t) + "</span>"
                    st.markdown(header_texto, unsafe_allow_html=True)
                    m1, m2, m3 = st.columns(3)
                    with m1: 
                        html_box = '<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 PENDENTES</div><div class="custom-pendente-value">' + str(p) + '</div></div>'
                        st.markdown(html_box, unsafe_allow_html=True)
                    with m2: st.metric(label="🟣 EM ROTA", value=r)
                    with m3: st.metric(label="🟢 INICIADO", value=i)

    with c_sp:
        st.markdown('<div class="title-abc-sp">SP</div>', unsafe_allow_html=True)
        if not df_sp.empty:
            for supervisor in sorted(df_sp[col_supervisor].dropna().unique()):
                df_super = df_sp[df_sp[col_supervisor] == supervisor]
                p = len(df_super[df_super['STATUS_ATIVIDADE'] == 'PENDENTE']) if 'STATUS_ATIVIDADE' in df_super.columns else 0
                r = len(df_super[df_super['STATUS_ATIVIDADE'] == 'EM ROTA']) if 'STATUS_ATIVIDADE' in df_super.columns else 0
                i = len(df_super[df_super['STATUS_ATIVIDADE'] == 'INICIADO']) if 'STATUS_ATIVIDADE' in df_super.columns else 0
                t = len(df_super)
                
                with st.container(border=True):
                    header_texto = "#### **" + str(supervisor).upper() + "** <span style='float:right; font-size:14px; background-color:#e1f5fe; padding:2px 8px; border-radius:4px; color:#0288d1;'>Total: " + str(t) + "</span>"
                    st.markdown(header_texto, unsafe_allow_html=True)
                    m1, m2, m3 = st.columns(3)
                    with m1: 
                        html_box = '<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 PENDENTES</div><div class="custom-pendente-value">' + str(p) + '</div></div>'
                        st.markdown(html_box, unsafe_allow_html=True)
                    with m2: st.metric(label="🟣 EM ROTA", value=r)
                    with m3: st.metric(label="🟢 INICIADO", value=i)
else:
    st.error("⚠️ Não foi possível processar a tabela.")

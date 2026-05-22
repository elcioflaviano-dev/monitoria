import streamlit as st
import pandas as pd
from urllib.parse import quote, unquote

# 1. Configuração da página - Mantém expandido para ver o menu se necessário
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# 2. Carregar CSS
try:
    with open("style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass

st.markdown('<h1 style="font-size: 42px; font-weight: 900; color: #006677; text-align: center; margin-top: 25px; margin-bottom: 20px;">TEC1</h1>', unsafe_allow_html=True)

# === MÓDULO DE CARGA (DIRETO DO SHEETS) ===
def carregar_dados_sheets():
    url = st.secrets["public_gsheets_url"]
    csv_url = url.replace("/edit?usp=sharing", "/gviz/tq?tqx=out:csv").replace("/edit#gid=", "/gviz/tq?tqx=out:csv&gid=")
    try:
        df_sheets = pd.read_csv(csv_url)
        # Padronização de colunas
        df_sheets.columns = df_sheets.columns.str.strip()
        colunas_mapeadas = {}
        for col in df_sheets.columns:
            col_upper = col.upper()
            if "SUPERVISOR" in col_upper: colunas_mapeadas[col] = "SUPERVISOR"
            elif "JANELA" in col_upper: colunas_mapeadas[col] = "JANELA_SERVICO"
            elif "STATUS" in col_upper: colunas_mapeadas[col] = "STATUS_ATIVIDADE"
        df = df_sheets.rename(columns=colunas_mapeadas)
        # Padronização de status internos
        if "STATUS_ATIVIDADE" in df.columns:
            df["STATUS_ATIVIDADE"] = df["STATUS_ATIVIDADE"].astype(str).str.strip().str.upper()
        return df
    except:
        return None

df = carregar_dados_sheets()

if df is not None:
    # --- FILTRO DE JANELA INTELIGENTE (COM MEMÓRIA NA URL) ---
    col_janela = 'JANELA_SERVICO'
    janela_selecionada = unquote(st.query_params.get("janela", "")) # Tenta pegar da URL

    if col_janela in df.columns:
        opcoes_janela = sorted(df[col_janela].dropna().astype(str).unique())
        
        # Define o índice padrão baseado na URL ou na primeira opção
        default_index = 0
        if janela_selecionada in opcoes_janela:
            default_index = opcoes_janela.index(janela_selecionada)
        
        # Cria o selectbox na barra lateral
        st.sidebar.markdown("### Filtros Operacionais")
        janela_sel = st.sidebar.selectbox(
            "Janela de Serviço Ativa:", 
            opcoes_janela, 
            index=default_index,
            key="sb_janela"
        )
        
        # Atualiza a URL se a janela mudar manualmente
        st.query_params["janela"] = janela_sel
        df_tela = df[df[col_janela] == janela_sel]
    else:
        df_tela = df.copy()
        janela_sel = ""

    # --- LÓGICA DE SUPERVISORES (ABC | SP) ---
    col_supervisor = 'SUPERVISOR'
    df_abc_lista, df_sp_lista = [], []
    if col_supervisor in df_tela.columns:
        for idx, linha in df_tela.iterrows():
            nome_super = str(linha[col_supervisor]).upper()
            if "FRANCISCO" in nome_super or "ALAN" in nome_super: df_sp_lista.append(linha)
            else: df_abc_lista.append(linha)
        df_abc = pd.DataFrame(df_abc_lista) if df_abc_lista else pd.DataFrame(columns=df_tela.columns)
        df_sp = pd.DataFrame(df_sp_lista) if df_sp_lista else pd.DataFrame(columns=df_tela.columns)
    else:
        df_abc, df_sp = pd.DataFrame(), pd.DataFrame()

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
                    st.markdown(f"#### **{str(supervisor).upper()}** <span style='float:right; font-size:14px; background-color:#e1f5fe; padding:2px 8px; border-radius:4px; color:#0288d1;'>Total: {t}</span>", unsafe_allow_html=True)
                    m1, m2, m3 = st.columns(3)
                    with m1: st.markdown(f'<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 PENDENTES</div><div class="custom-pendente-value">{p}</div></div>', unsafe_allow_html=True)
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
                    st.markdown(f"#### **{str(supervisor).upper()}** <span style='float:right; font-size:14px; background-color:#e1f5fe; padding:2px 8px; border-radius:4px; color:#0288d1;'>Total: {t}</span>", unsafe_allow_html=True)
                    m1, m2, m3 = st.columns(3)
                    with m1: st.markdown(f'<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 PENDENTES</div><div class="custom-pendente-value">{p}</div></div>', unsafe_allow_html=True)
                    with m2: st.metric(label="🟣 EM ROTA", value=r)
                    with m3: st.metric(label="🟢 INICIADO", value=i)

    # === SISTEMA DE LOOP TV CORRIGIDO (PASSA A JANELA PELA URL) ===
    # Prepara o parâmetro da janela para o link
    janela_param = quote(janela_sel)
    next_page_url = f"/2_TEC1_PENDENTES?janela={janela_param}"
    
    st.components.v1.html(f"""
        <script>
        setTimeout(function(){
            // Recarrega a página inteira mudando a URL para passar o filtro
            window.parent.location.href = unescape("{next_page_url}");
        }, 30000);
        </script>
    """, height=0)
else:
    st.error("⚠️ Erro ao carregar dados do Google Sheets.")

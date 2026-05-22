import streamlit as st
import pandas as pd

# Configuração da página e remoção de espaços
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

try:
    with open("style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass

st.markdown("""
    <style>
    .item-pendente-tv { background-color: #ffe6e6 !important; border: 2px solid #ff9999 !important; border-radius: 6px; padding: 6px 12px !important; margin-bottom: 6px !important; display: flex !important; justify-content: space-between !important; align-items: center !important; width: 100% !important; }
    .tecnico-nome-tv { color: #b30000 !important; font-size: 14px !important; font-weight: 900 !important; text-transform: uppercase !important; }
    .contrato-numero-tv { background-color: #b30000 !important; color: white !important; padding: 3px 10px !important; border-radius: 4px !important; font-weight: bold !important; font-size: 14px !important; }
    .no-pendente-tv { color: #2e7d32; font-weight: bold; font-size: 14px; text-align: center; padding: 5px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="font-size: 38px; font-weight: 900; color: #b30000; text-align: center; margin-top: 25px; margin-bottom: 10px;">⚠️ TEC1 - PENDENTES</h1>', unsafe_allow_html=True)

# Puxa e revalida direto da nuvem também nesta página
url = st.secrets["public_gsheets_url"]
csv_url = url.replace("/edit?usp=sharing", "/gviz/tq?tqx=out:csv").replace("/edit#gid=", "/gviz/tq?tqx=out:csv&gid=")

try:
    df_sheets = pd.read_csv(csv_url)
    df_sheets.columns = df_sheets.columns.str.strip()
    colunas_mapeadas = {}
    for col in df_sheets.columns:
        col_upper = col.upper()
        if "SUPERVISOR" in col_upper: colunas_mapeadas[col] = "SUPERVISOR"
        elif "JANELA" in col_upper: colunas_mapeadas[col] = "JANELA_SERVICO"
        elif "STATUS" in col_upper: colunas_mapeadas[col] = "STATUS_ATIVIDADE"
        elif "CONTRATO" in col_upper: colunas_mapeadas[col] = "CONTRATO"
        elif "RECURSO" in col_upper: colunas_mapeadas[col] = "RECURSO"
    df = df_sheets.rename(columns=colunas_mapeadas)
    if "STATUS_ATIVIDADE" in df.columns:
        df["STATUS_ATIVIDADE"] = df["STATUS_ATIVIDADE"].astype(str).str.strip().str.upper()
except:
    df = st.session_state.get('dados_rota', None)

if df is not None:
    # Filtro de Janela
    col_janela = 'JANELA_SERVICO'
    if col_janela in df.columns:
        opcoes_janela = sorted(df[col_janela].dropna().astype(str).unique())
        janela_sel = st.sidebar.selectbox("Janela Ativa:", opcoes_janela)
        df_tela = df[df[col_janela] == janela_sel]
    else:
        df_tela = df.copy()

    # Filtro de Status: APENAS PENDENTES
    df_pendentes_geral = df_tela[df_tela['STATUS_ATIVIDADE'] == 'PENDENTE'] if 'STATUS_ATIVIDADE' in df_tela.columns else pd.DataFrame()

    # Lógica de Separação (ABC | SP)
    col_supervisor = 'SUPERVISOR'
    df_abc_lista, df_sp_lista = [], []
    for _, linha in df_pendentes_geral.iterrows():
        nome_super = str(linha[col_supervisor]).upper()
        if "FRANCISCO" in nome_super or "ALAN" in nome_super: df_sp_lista.append(linha)
        else: df_abc_lista.append(linha)
            
    df_abc = pd.DataFrame(df_abc_lista) if df_abc_lista else pd.DataFrame(columns=df_tela.columns)
    df_sp = pd.DataFrame(df_sp_lista) if df_sp_lista else pd.DataFrame(columns=df_tela.columns)

    def desenhar_alertas(df_regiao, titulo_regiao):
        st.markdown(f'<div class="title-abc-sp">{titulo_regiao}</div>', unsafe_allow_html=True)
        todos_supervisores = sorted(df_tela[col_supervisor].dropna().unique()) if col_supervisor in df_tela.columns else []
        
        if titulo_regiao == "SP": meus_supers = [s for s in todos_supervisores if "FRANCISCO" in s.upper() or "ALAN" in s.upper()]
        else: meus_supers = [s for s in todos_supervisores if "FRANCISCO" not in s.upper() and "ALAN" not in s.upper()]

        for super_nome in meus_supers:
            df_super_p = df_regiao[df_regiao[col_supervisor] == super_nome] if not df_regiao.empty else pd.DataFrame()
            with st.container(border=True):
                st.markdown(f"##### **{super_nome.upper()}**")
                if not df_super_p.empty:
                    for _, r in df_super_p.iterrows():
                        contrato_limpo = str(r['CONTRATO']).split('.')[0] if 'CONTRATO' in r else "N/A"
                        nome_tecnico = str(r['RECURSO'])[:25] if 'RECURSO' in r else "N/A"
                        st.markdown(f'<div class="item-pendente-tv"><span class="tecnico-nome-tv">{nome_tecnico}</span><span class="contrato-numero-tv">{contrato_limpo}</span></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="no-pendente-tv">✅ Sem pendências nesta janela</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1: desenhar_alertas(df_abc, "ABC")
    with c2: desenhar_alertas(df_sp, "SP")

    # === MODO TV: RETORNA PARA A PÁGINA 1 EM 30 SEGUNDOS ===
    st.components.v1.html("""
        <script>
        setTimeout(function(){ window.parent.location.hash = "#tec1"; }, 30000);
        </script>
    """, height=0)
else:
    st.warning("⚠️ Aguardando sincronização com o Google Sheets...")

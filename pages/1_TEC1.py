import streamlit as st
import pandas as pd

# Configura a página para ocupar toda a largura da tela
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

try:
    with open("style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass

st.markdown('<h1 style="font-size: 42px; font-weight: 900; color: #006677; text-align: center; margin-top: 25px; margin-bottom: 20px;">TEC1</h1>', unsafe_allow_html=True)

# === FUNÇÃO DE LEITURA DIRETO DO GOOGLE SHEETS ===
def carregar_dados_sheets():
    # Puxa a URL configurada no secrets.toml
    url = st.secrets["public_gsheets_url"]
    
    # Transforma o link normal do Sheets em um link de download direto de CSV
    csv_url = url.replace("/edit?usp=sharing", "/gviz/tq?tqx=out:csv").replace("/edit#gid=", "/gviz/tq?tqx=out:csv&gid=")
    
    try:
        # Lê os dados em tempo real da nuvem
        df_sheets = pd.read_csv(csv_url)
        
        # --- BLINDAGEM OPERACIONAL DE COLUNAS ---
        df_sheets.columns = df_sheets.columns.str.strip()
        colunas_mapeadas = {}
        for col in df_sheets.columns:
            col_upper = col.upper()
            if "SUPERVISOR" in col_upper: colunas_mapeadas[col] = "SUPERVISOR"
            elif "JANELA" in col_upper: colunas_mapeadas[col] = "JANELA_SERVICO"
            elif "STATUS" in col_upper: colunas_mapeadas[col] = "STATUS_ATIVIDADE"
            elif "CONTRATO" in col_upper: colunas_mapeadas[col] = "CONTRATO"
            elif "RECURSO" in col_upper: colunas_mapeadas[col] = "RECURSO"
        
        df_final = df_sheets.rename(columns=colunas_mapeadas)
        if "STATUS_ATIVIDADE" in df_final.columns:
            df_final["STATUS_ATIVIDADE"] = df_final["STATUS_ATIVIDADE"].astype(str).str.strip().str.upper()
            
        # Salva na sessão para a outra página também usar se quiser
        st.session_state['dados_rota'] = df_final
        return df_final
    except Exception as e:
        # Se falhar, tenta usar o que sobrou na memória anterior
        if 'dados_rota' in st.session_state:
            return st.session_state['dados_rota']
        return None

# Executa a carga em tempo real da nuvem
df = carregar_dados_sheets()

if df is not None:
    # --- FILTRO DA JANELA GLOBAL ---
    col_janela = 'JANELA_SERVICO'
    if col_janela in df.columns:
        opcoes_janela = sorted(df[col_janela].dropna().astype(str).unique())
        janela_sel = st.sidebar.selectbox("Janela de Serviço:", opcoes_janela)
        df_tela = df[df[col_janela] == janela_sel]
    else:
        df_tela = df.copy()

    # --- SEPARAÇÃO LÓGICA DOS SUPERVISORES ---
    col_supervisor = 'SUPERVISOR'
    df_abc_lista, df_sp_lista = [], []
    
    if col_supervisor in df_tela.columns:
        for idx, linha in df_tela.iterrows():
            nome_super = str(linha[col_supervisor]).upper()
            if "FRANCISCO" in nome_super or "ALAN" in nome_super:
                df_sp_lista.append(linha)
            else:
                df_abc_lista.append(linha)
                
        df_abc = pd.DataFrame(df_abc_lista) if df_abc_lista else pd.DataFrame(columns=df_tela.columns)
        df_sp = pd.DataFrame(df_sp_lista) if df_sp_lista else pd.DataFrame(columns=df_tela.columns)
    else:
        df_abc, df_sp = pd.DataFrame(), pd.DataFrame()

    # --- CORPO VISUAL LADO A LADO ---
    col_coluna_abc, col_coluna_sp = st.columns(2)
    
    with col_coluna_abc:
        st.markdown('<div class="title-abc-sp">ABC</div>', unsafe_allow_html=True)
        if not df_abc.empty:
            supervisores_abc = df_abc[col_supervisor].dropna().unique()
            for supervisor in sorted(supervisores_abc):
                df_super = df_abc[df_abc[col_supervisor] == supervisor]
                
                pendentes = len(df_super[df_super['STATUS_ATIVIDADE'] == 'PENDENTE']) if 'STATUS_ATIVIDADE' in df_super.columns else 0
                em_rota = len(df_super[df_super['STATUS_ATIVIDADE'] == 'EM ROTA']) if 'STATUS_ATIVIDADE' in df_super.columns else 0
                iniciados = len(df_super[df_super['STATUS_ATIVIDADE'] == 'INICIADO']) if 'STATUS_ATIVIDADE' in df_super.columns else 0
                total = len(df_super)
                
                with st.container(border=True):
                    st.markdown(f"#### **{str(supervisor).upper()}** <span style='float:right; font-size:14px; background-color:#e1f5fe; padding:2px 8px; border-radius:4px; color:#0288d1;'>Total: {total}</span>", unsafe_allow_html=True)
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.markdown(f'<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 PENDENTES</div><div class="custom-pendente-value">{pendentes}</div></div>', unsafe_allow_html=True)
                    with m2: st.metric(label="🟣 EM ROTA", value=em_rota)
                    with m3: st.metric(label="🟢 INICIADO", value=iniciados)

    with col_coluna_sp:
        st.markdown('<div class="title-abc-sp">SP</div>', unsafe_allow_html=True)
        if not df_sp.empty:
            supervisores_sp = df_sp[col_supervisor].dropna().unique()
            for supervisor in sorted(supervisores_sp):
                df_super = df_sp[df_sp[col_supervisor] == supervisor]
                
                pendentes = len(df_super[df_super['STATUS_ATIVIDADE'] == 'PENDENTE']) if 'STATUS_ATIVIDADE' in df_super.columns else 0
                em_rota = len(df_super[df_super['STATUS_ATIVIDADE'] == 'EM ROTA']) if 'STATUS_ATIVIDADE' in df_super.columns else 0
                iniciados = len(df_super[df_super['STATUS_ATIVIDADE'] == 'INICIADO']) if 'STATUS_ATIVIDADE' in df_super.columns else 0
                total = len(df_super)
                
                with st.container(border=True):
                    st.markdown(f"#### **{str(supervisor).upper()}** <span style='float:right; font-size:14px; background-color:#e1f5fe; padding:2px 8px; border-radius:4px; color:#0288d1;'>Total: {total}</span>", unsafe_allow_html=True)
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.markdown(f'<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 PENDENTES</div><div class="custom-pendente-value">{pendentes}</div></div>', unsafe_allow_html=True)
                    with m2: st.metric(label="🟣 EM ROTA", value=em_rota)
                    with m3: st.metric(label="🟢 INICIADO", value=iniciados)

    # === AUTOMATIZAÇÃO DA ALTERNÂNCIA (MODO TV) ===
    # Força a limpeza do cache de rotação interna e pula de página em 30 segundos
    st.components.v1.html("""
        <script>
        setTimeout(function(){
            window.parent.location.hash = "#2-tec1-pendentes";
        }, 30000);
        </script>
    """, height=0)
else:
    st.error("⚠️ Não foi possível carregar os dados do Google Sheets. Verifique o link e as permissões de compartilhamento.")

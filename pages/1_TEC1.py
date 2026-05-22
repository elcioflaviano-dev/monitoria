import streamlit as st
import pandas as pd
import os

# Configura a página para ocupar toda a largura da tela
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Abre e injeta o arquivo style.css externo
try:
    with open("style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass

# Título TEC1 Centralizado e ajustado
st.markdown(
    '<h1 style="font-size: 42px; font-weight: 900; color: #006677; text-align: center; margin-top: 25px; margin-bottom: 20px;">TEC1</h1>', 
    unsafe_allow_html=True
)

# === FUNÇÃO DE CARGA OPERACIONAL AUTOMÁTICA BLINDADA ===
def carregar_dados_automatico():
    if 'dados_rota' in st.session_state:
        return st.session_state['dados_rota']
    
    caminho_planilha = "base_rotas.xlsx" 
    
    if os.path.exists(caminho_planilha):
        df_automatico = pd.read_excel(caminho_planilha)
        
        # --- BLINDAGEM CONTRA ERROS DE COLUNA ---
        # 1. Remove espaços invisíveis antes ou depois dos nomes das colunas
        df_automatico.columns = df_automatico.columns.str.strip()
        # 2. Converte todas as colunas para MAIÚSCULAS (evita erro de 'Supervisor' vs 'SUPERVISOR')
        df_automatico.columns = df_automatico.columns.str.upper()
        
        # Faz o mesmo tratamento para a coluna de Status interno da planilha para não quebrar
        if 'STATUS DA ATIVIDADE' in df_automatico.columns:
            df_automatico['STATUS DA ATIVIDADE'] = df_automatico['STATUS DA ATIVIDADE'].astype(str).str.strip().str.upper()
            
        st.session_state['dados_rota'] = df_automatico
        return df_automatico
    return None

# Executa a carga inteligente
df_planilha = carregar_dados_automatico()

if df_planilha is not None:
    df = df_planilha.copy()
    
    # --- FILTRO DA JANELA GLOBAL (BARRA LATERAL) ---
    col_janela = 'JANELA DE SERVIÇO'  # Atualizado para maiúsculo devido à blindagem
    if col_janela in df.columns:
        opcoes_janela = sorted(df[col_janela].dropna().astype(str).unique())
        janela_sel = st.sidebar.selectbox("Janela de Serviço:", opcoes_janela)
        df_tela = df[df[col_janela] == janela_sel]
    else:
        # Tenta procurar sem o 'Ç' e 'Ó' caso a planilha mude o texto
        col_janela_alt = 'JANELA DE SERVICO'
        if col_janela_alt in df.columns:
            opcoes_janela = sorted(df[col_janela_alt].dropna().astype(str).unique())
            janela_sel = st.sidebar.selectbox("Janela de Serviço:", opcoes_janela)
            df_tela = df[df[col_janela_alt] == janela_sel]
        else:
            df_tela = df.copy()
            janela_sel = "N/A"

    # --- SEPARAÇÃO LÓGICA DOS SUPERVISORES ---
    col_supervisor = 'SUPERVISOR'  # Agora garantido em maiúsculo
    df_abc_lista, df_sp_lista = [], []
    
    if col_supervisor in df_tela.columns:
        for idx, Server_linha in df_tela.iterrows():
            nome_super = str(Server_linha[col_supervisor]).upper()
            if "FRANCISCO" in nome_super or "ALAN" in nome_super:
                df_sp_lista.append(Server_linha)
            else:
                df_abc_lista.append(Server_linha)
                
        df_abc = pd.DataFrame(df_abc_lista) if df_abc_lista else pd.DataFrame(columns=df_tela.columns)
        df_sp = pd.DataFrame(df_sp_lista) if df_sp_lista else pd.DataFrame(columns=df_tela.columns)
    else:
        df_abc, df_sp = pd.DataFrame(), pd.DataFrame()

    # --- CORPO VISUAL (COLUNAS LADO A LADO) ---
    col_coluna_abc, col_coluna_sp = st.columns(2)
    
    # --- COLUNA ESQUERDA: ABC ---
    with col_coluna_abc:
        st.markdown('<div class="title-abc-sp">ABC</div>', unsafe_allow_html=True)
        
        if not df_abc.empty:
            supervisores_abc = df_abc[col_supervisor].dropna().unique()
            for supervisor in sorted(supervisores_abc):
                df_super = df_abc[df_abc[col_supervisor] == supervisor]
                
                # Buscas tratadas em maiúsculo
                pendentes = len(df_super[df_super['STATUS DA ATIVIDADE'] == 'PENDENTE'])
                em_rota = len(df_super[df_super['STATUS DA ATIVIDADE'] == 'EM ROTA'])
                iniciados = len(df_super[df_super['STATUS DA ATIVIDADE'] == 'INICIADO'])
                total = len(df_super)
                
                with st.container(border=True):
                    st.markdown(f"#### **{str(supervisor).upper()}** <span style='float:right; font-size:14px; background-color:#e1f5fe; padding:2px 8px; border-radius:4px; color:#0288d1;'>Total: {total}</span>", unsafe_allow_html=True)
                    
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.markdown(f"""
                            <div class="custom-pendente-box">
                                <div class="custom-pendente-label">🔴 PENDENTES</div>
                                <div class="custom-pendente-value">{pendentes}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    with m2:
                        st.metric(label="🟣 EM ROTA", value=em_rota)
                    with m3:
                        st.metric(label="🟢 INICIADO", value=iniciados)
        else:
            st.info("Nenhum supervisor ativo no ABC nesta janela.")

    # --- COLUNA DIREITA: SP ---
    with col_coluna_sp:
        st.markdown('<div class="title-abc-sp">SP</div>', unsafe_allow_html=True)
        
        if not df_sp.empty:
            supervisores_sp = df_sp[col_supervisor].dropna().unique()
            for supervisor in sorted(supervisores_sp):
                df_super = df_sp[df_sp[col_supervisor] == supervisor]
                
                pendentes = len(df_super[df_super['STATUS DA ATIVIDADE'] == 'PENDENTE'])
                em_rota = len(df_super[df_super['STATUS DA ATIVIDADE'] == 'EM ROTA'])
                iniciados = len(df_super[df_super['STATUS DA ATIVIDADE'] == 'INICIADO'])
                total = len(df_super)
                
                with st.container(border=True):
                    st.markdown(f"#### **{str(supervisor).upper()}** <span style='float:right; font-size:14px; background-color:#e1f5fe; padding:2px 8px; border-radius:4px; color:#0288d1;'>Total: {total}</span>", unsafe_allow_html=True)
                    
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.markdown(f"""
                            <div class="custom-pendente-box">
                                <div class="custom-pendente-label">🔴 PENDENTES</div>
                                <div class="custom-pendente-value">{pendentes}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    with m2:
                        st.metric(label="🟣 EM ROTA", value=em_rota)
                    with m3:
                        st.metric(label="🟢 INICIADO", value=iniciados)
        else:
            st.info("Nenhum supervisor ativo em SP nesta janela.")

    # === AUTOMAÇÃO MODO TV (TROCA APÓS 30 SEGUNDOS) ===
    st.components.v1.html("""
        <script>
        setTimeout(function(){
            window.parent.location.hash = "#2-tec1-pendentes";
        }, 30000);
        </script>
    """, height=0)

else:
    st.error("⚠️ Planilha 'base_rotas.xlsx' não encontrada na pasta do projeto.")

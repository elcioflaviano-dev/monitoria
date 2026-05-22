import streamlit as st
import pandas as pd

# 1. Configuração da página e remoção de espaços inúteis
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

try:
    with open("style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass

# 2. Título Centralizado Ajustado
st.markdown('<h1 style="font-size: 38px; font-weight: 900; color: #006677; text-align: center; margin-top: 25px; margin-bottom: 20px;">TEC1 - CONTRATOS</h1>', unsafe_allow_html=True)

# === SISTEMA DE TROCA DE PÁGINA ULTRA SEGURO (MODO TV) ===
# Aguarda 30 segundos e força o navegador a mudar para a página 1 (TEC1)
st.components.v1.html("""
    <script>
    setTimeout(function(){
        window.parent.location.hash = "#tec1";
    }, 30000);
    </script>
""", height=0)

if 'dados_rota' in st.session_state:
    df = st.session_state['dados_rota'].copy()
    
    # Filtro de Janela Automático
    col_janela = 'Janela de Serviço'
    if col_janela in df.columns:
        opcoes_janela = sorted(df[col_janela].dropna().astype(str).unique())
        janela_sel = st.sidebar.selectbox("Janela:", opcoes_janela)
        df_tela = df[df[col_janela] == janela_sel]
    else:
        df_tela = df.copy()

    # Lógica de Separação de Supervisores (Idêntica ao TEC1)
    col_supervisor = 'SUPERVISOR'
    df_abc_lista, df_sp_lista = [], []
    for _, linha in df_tela.iterrows():
        nome_super = str(linha[col_supervisor]).upper()
        if "FRANCISCO" in nome_super or "ALAN" in nome_super:
            df_sp_lista.append(linha)
        else:
            df_abc_lista.append(linha)
            
    df_abc = pd.DataFrame(df_abc_lista) if df_abc_lista else pd.DataFrame(columns=df_tela.columns)
    df_sp = pd.DataFrame(df_sp_lista) if df_sp_lista else pd.DataFrame(columns=df_tela.columns)

    # Função Inteligente para gerar a tabela ordenada sem usar HTML quebrado
    def exibir_tabela_priorizada(df_input):
        if df_input.empty:
            st.info("Sem atividades para esta janela.")
            return

        supervisores = sorted(df_input[col_supervisor].dropna().unique())
        for super_nome in supervisores:
            df_super = df_input[df_input[col_supervisor] == super_nome].copy()
            
            # Garante que as colunas essenciais existem
            colunas_necessarias = ['Recurso', 'Contrato', 'Status da Atividade']
            colunas_validas = [c for c in colunas_necessarias if c in df_super.columns]
            
            df_resumo = df_super[colunas_validas].copy()
            
            # Cria a regra de prioridade numérica (Pendente ganha)
            if 'Status da Atividade' in df_resumo.columns:
                prioridade = {'PENDENTE': 1, 'EM ROTA': 2, 'INICIADO': 3}
                df_resumo['Ordem'] = df_resumo['Status da Atividade'].str.upper().map(prioridade).fillna(4)
                df_resumo = df_resumo.sort_values('Ordem')
                df_resumo = df_resumo.drop(columns=['Ordem']) # Remove a coluna auxiliar do visual
            
            # Renomeia as colunas para o painel ficar bonito na TV
            df_resumo.columns = [c.upper() for c in df_resumo.columns]
            
            # Desenha o Card do Supervisor com a tabela limpa dentro dele
            with st.container(border=True):
                st.markdown(f"##### **{super_nome.upper()}**")
                st.dataframe(
                    df_resumo, 
                    use_container_width=True, 
                    hide_index=True,
                    height=140 # Altura controlada para caber todo mundo na tela sem estourar
                )

    # Divisão da Tela Lado a Lado (ABC | SP)
    c_abc, c_sp = st.columns(2)
    with c_abc:
        st.markdown('<div class="title-abc-sp">ABC</div>', unsafe_allow_html=True)
        exibir_tabela_priorizada(df_abc)
    with c_sp:
        st.markdown('<div class="title-abc-sp">SP</div>', unsafe_allow_html=True)
        exibir_tabela_priorizada(df_sp)
else:
    st.warning("⚠️ Dados não encontrados. Por favor, carregue a planilha na página inicial.")

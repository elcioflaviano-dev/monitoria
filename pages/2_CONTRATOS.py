import streamlit as st
import pandas as pd

# 1. Configuração da página e remoção de espaços
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 2. Carregar Estilos
try:
    with open("style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass

# 3. Estilo específico para Alerta de Contratos Pendentes
st.markdown("""
    <style>
    .card-pendente-detalhe {
        background-color: #ffe6e6;
        border: 2px solid #ff9999;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .tecnico-nome {
        color: #b30000;
        font-size: 16px;
        font-weight: 900;
        text-transform: uppercase;
    }
    .contrato-numero {
        background-color: #b30000;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 15px;
        float: right;
    }
    .item-pendente {
        border-bottom: 1px solid #ffcccc;
        padding: 5px 0;
    }
    .item-pendente:last-child {
        border-bottom: none;
    }
    .no-pendente {
        color: #2e7d32;
        font-weight: bold;
        font-size: 14px;
        text-align: center;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# 4. Título de Alerta
st.markdown('<h1 style="font-size: 38px; font-weight: 900; color: #b30000; text-align: center; margin-top: 25px; margin-bottom: 10px;">⚠️ TEC1 - CONTRATOS PENDENTES</h1>', unsafe_allow_html=True)

# === MODO TV: VOLTA PARA A PÁGINA 1 APÓS 30 SEGUNDOS ===
st.components.v1.html("""
    <script>
    setTimeout(function(){
        window.parent.location.hash = "#tec1";
    }, 30000);
    </script>
""", height=0)

if 'dados_rota' in st.session_state:
    df = st.session_state['dados_rota'].copy()
    
    # Filtro de Janela
    col_janela = 'Janela de Serviço'
    if col_janela in df.columns:
        opcoes_janela = sorted(df[col_janela].dropna().astype(str).unique())
        janela_sel = st.sidebar.selectbox("Janela Ativa:", opcoes_janela)
        df_tela = df[df[col_janela] == janela_sel]
    else:
        df_tela = df.copy()

    # Filtro de Status: APENAS PENDENTES
    df_pendentes_geral = df_tela[df_tela['Status da Atividade'].str.upper() == 'PENDENTE']

    # Lógica de Separação (ABC | SP)
    col_supervisor = 'SUPERVISOR'
    df_abc_lista, df_sp_lista = [], []
    
    for _, linha in df_pendentes_geral.iterrows():
        nome_super = str(linha[col_supervisor]).upper()
        if "FRANCISCO" in nome_super or "ALAN" in nome_super:
            df_sp_lista.append(linha)
        else:
            df_abc_lista.append(linha)
            
    df_abc = pd.DataFrame(df_abc_lista) if df_abc_lista else pd.DataFrame(columns=df_tela.columns)
    df_sp = pd.DataFrame(df_sp_lista) if df_sp_lista else pd.DataFrame(columns=df_tela.columns)

    # Função para desenhar a lista de pendentes em destaque
    def desenhar_alertas(df_regiao, titulo_regiao):
        st.markdown(f'<div class="title-abc-sp">{titulo_regiao}</div>', unsafe_allow_html=True)
        
        # Precisamos pegar todos os supervisores da janela (mesmo os que não tem pendentes agora)
        # para manter o layout da TV consistente
        todos_supervisores = sorted(df_tela[col_supervisor].dropna().unique())
        
        # Filtrar supervisores que pertencem a esta região
        if titulo_regiao == "SP":
            meus_supers = [s for s in todos_supervisores if "FRANCISCO" in s.upper() or "ALAN" in s.upper()]
        else:
            meus_supers = [s for s in todos_supervisores if "FRANCISCO" not in s.upper() and "ALAN" not in s.upper()]

        for super_nome in meus_supers:
            df_super_p = df_regiao[df_regiao[col_supervisor] == super_nome]
            
            with st.container(border=True):
                st.markdown(f"##### **{super_nome.upper()}**")
                
                if not df_super_p.empty:
                    html_lista = '<div class="card-pendente-detalhe">'
                    for _, r in df_super_p.iterrows():
                        html_lista += f"""
                            <div class="item-pendente">
                                <span class="tecnico-nome">{str(r['Recurso'])[:25]}</span>
                                <span class="contrato-numero">{r['Contrato']}</span>
                            </div>
                        """
                    html_lista += '</div>'
                    st.markdown(html_lista, unsafe_allow_html=True)
                else:
                    st.markdown('<div class="no-pendente">✅ Sem pendências nesta janela</div>', unsafe_allow_html=True)

    # Divisão em Colunas
    c1, c2 = st.columns(2)
    with c1:
        desenhar_alertas(df_abc, "ABC")
    with c2:
        desenhar_alertas(df_sp, "SP")

else:
    st.warning("⚠️ Carregue a planilha na página inicial.")

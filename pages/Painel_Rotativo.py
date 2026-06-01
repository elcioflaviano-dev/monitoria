import streamlit as st
import pandas as pd
import os
import time

# 1. Configuração de tela para TV
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"
TEMPO_ROTACAO_SEGUNDOS = 5  # Tempo solicitado

# Carregamento
df_master = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str) if os.path.exists(ARQUIVO_ROTA_DISCO) else None

# Controle de Sessão
if "index_sup_tv" not in st.session_state: st.session_state["index_sup_tv"] = 0
if "last_rotacao_tv" not in st.session_state: st.session_state["last_rotacao_tv"] = time.time()

SUPERVISORES = ["MAICON", "NELSON", "MARCOS ROBERTO", "ALAN", "FRANCISCO GERALDO CARVALHO JUNIOR"]

# Lógica de Rotação (5 segundos)
if time.time() - st.session_state["last_rotacao_tv"] >= TEMPO_ROTACAO_SEGUNDOS:
    st.session_state["index_sup_tv"] = (st.session_state["index_sup_tv"] + 1) % len(SUPERVISORES)
    st.session_state["last_rotacao_tv"] = time.time()
    st.rerun()

supervisor_atual = SUPERVISORES[st.session_state["index_sup_tv"]]

# CSS para TV (Sem menu lateral)
st.markdown("""<style>
    section[data-testid="stSidebar"] { display: none !important; }
    .header-tv { background: #111; color: #fff; padding: 10px; display: flex; justify-content: space-between; align-items: center; }
    .btn-home { background: #cc6600; color: white; padding: 5px 15px; border-radius: 5px; text-decoration: none; font-weight: bold; }
    .box-pendente { background: #ffcccc; padding: 20px; border-radius: 10px; text-align: center; border: 2px solid #b30000; }
    .valor-pendente { font-size: 80px; font-weight: 900; color: #b30000; }
</style>""", unsafe_allow_html=True)

# Barra Superior
st.markdown(f'''
    <div class="header-tv">
        <div><a href="/" target="_self" class="btn-home">🏠 HOME</a></div>
        <div>📺 TV MODE • SUPERVISOR: <b>{supervisor_atual}</b></div>
        <div>🔄 {TEMPO_ROTACAO_SEGUNDOS}s</div>
    </div>
''', unsafe_allow_html=True)

# Processamento
if df_master is not None:
    df = df_master.copy()
    # Filtra pelo supervisor atual
    df_sup = df[df['SUPERVISOR'].str.contains(supervisor_atual, case=False, na=False)]
    p_total = int(df_sup['Status da Atividade'].fillna('').str.contains('PENDENTE', case=False, na=False).sum())

    st.markdown(f"<h1 style='text-align:center'>EQUIPE: {supervisor_atual}</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f'<div class="box-pendente"><div class="valor-pendente">{p_total}</div>PENDENTES</div>', unsafe_allow_html=True)
        
        # Gatilho de Fala (Apenas Pendentes)
        st.components.v1.html(f"""
            <script>
                var msg = new SpeechSynthesisUtterance("Supervisor {supervisor_atual}, possui {p_total} pendentes.");
                msg.lang = "pt-BR";
                window.speechSynthesis.speak(msg);
            </script>
        """, height=0)

    with col2:
        st.subheader("Lista de Pendentes:")
        st.dataframe(df_sup[df_sup['Status da Atividade'].str.contains('PENDENTE', case=False, na=False)][['Contrato', 'Recurso']], use_container_width=True)

else:
    st.warning("Arquivo não encontrado.")

time.sleep(1)
st.rerun()

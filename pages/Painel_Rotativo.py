import streamlit as st
import pandas as pd
import os
import time

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

# Carregamento
df = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str) if os.path.exists(ARQUIVO_ROTA_DISCO) else None
if df is not None and 'Contrato' in df.columns:
    df['Contrato'] = df['Contrato'].str.replace('.0', '', regex=False)

SUPERVISORES = ["MAICON", "NELSON", "MARCOS ROBERTO", "ALAN", "FRANCISCO GERALDO CARVALHO JUNIOR"]

# Controle de Sessão
if "idx" not in st.session_state: st.session_state.idx = 0
if "last_move" not in st.session_state: st.session_state.last_move = time.time()

# Troca de Supervisor a cada 5 segundos
if time.time() - st.session_state.last_move > 5:
    st.session_state.idx = (st.session_state.idx + 1) % len(SUPERVISORES)
    st.session_state.last_move = time.time()
    st.rerun()

sup = SUPERVISORES[st.session_state.idx]

# Estilo para TV
st.markdown("""<style>
    .header-tv { background: #000; color: #fff; padding: 20px; text-align: center; font-size: 30px; font-weight: 900; }
    .card-sup { background: #005088; color: #fff; padding: 15px; border-radius: 10px; text-align: center; font-size: 24px; margin-bottom: 20px; }
    .box-pendente { background: #ffcccc; padding: 20px; border-radius: 10px; text-align: center; border: 4px solid #b30000; }
    .valor { font-size: 80px; font-weight: 900; color: #b30000; }
    .card-contrato { background: #f8f9fa; border-left: 10px solid #cc6600; padding: 15px; margin: 10px 0; display: flex; justify-content: space-between; align-items: center; }
</style>""", unsafe_allow_html=True)

st.markdown(f'<div class="header-tv">EQUIPE EM FOCO: {sup}</div>', unsafe_allow_html=True)

if df is not None:
    df_sup = df[df['SUPERVISOR'].str.contains(sup, case=False, na=False)]
    pendentes = df_sup[df_sup['Status da Atividade'].fillna('').str.contains('PENDENTE', case=False, na=False)]
    
    # Exibe Informações
    st.markdown(f'<div class="card-sup">SUPERVISOR: {sup}</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f'<div class="box-pendente"><div class="valor">{len(pendentes)}</div>PENDENTES</div>', unsafe_allow_html=True)
    
    with col2:
        for _, row in pendentes.iterrows():
            st.markdown(f'''
                <div class="card-contrato">
                    <span style="font-size:24px; font-weight:bold;">📄 {row.get("Contrato")}</span>
                    <span style="font-size:20px; color:#555;">👤 {row.get("Recurso", "Técnico").upper()}</span>
                </div>
            ''', unsafe_allow_html=True)

    # Fala Automática (Dispara uma vez por supervisor)
    fala = f"Supervisor {sup}, possui {len(pendentes)} contratos pendentes."
    st.components.v1.html(f"""<script>
        var msg = new SpeechSynthesisUtterance("{fala}");
        msg.lang = 'pt-BR';
        window.speechSynthesis.speak(msg);
    </script>""", height=0)

else:
    st.warning("Carregando...")

time.sleep(1)
st.rerun()

import streamlit as st
import time
from datetime import datetime

# 1. Configuração da página ampla para a TV
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

TEMPO_ROTACAO_SEGUNDOS = 15  # Tempo exato de cada tela na TV

# --- REFRESH NATIVO VIA HTML METATAG (Dá o F5 a cada 15s para forçar a troca) ---
st.markdown(f'<meta http-equiv="refresh" content="{TEMPO_ROTACAO_SEGUNDOS}">', unsafe_allow_html=True)

# 🔥 INJEÇÃO DE CSS PARA SUMIR COM O MENU LATERAL NESTA PÁGINA
st.markdown("""
    <style>
        section[data-testid="stSidebar"], 
        [data-testid="stSidebar"], 
        div[data-testid="stSidebarCollapseButton"],
        button[data-testid="stSidebarCollapseButton"] {
            display: none !important;
            visibility: hidden !important;
            width: 0px !important;
        }
        .block-container { padding-top: 80px !important; }
        .stDeployButton { display:none; }
        .barra-status-tv {
            position: fixed; top: 0; left: 0; right: 0; z-index: 999995;
            background-color: #111; color: #fff; padding: 10px 20px;
            font-size: 13px; font-weight: bold; display: flex; justify-content: space-between; align-items: center;
            font-family: sans-serif; box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        }
        .btn-voltar-home {
            background-color: #cc6600; color: white !important; padding: 5px 12px;
            border-radius: 4px; text-decoration: none !important; font-size: 12px; font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# Barra fixa superior de aviso
st.markdown(f'''
    <div class="barra-status-tv">
        <div>
            <a href="/" target="_self" class="btn-voltar-home">🏠 VOLTAR PARA A HOME</a>
            <span style="margin-left: 15px;">📺 INICIANDO MODO TV (TEC1 ↔️ TEC1 PENDENTES)</span>
        </div>
        <span>🔄 Alternando a cada {TEMPO_ROTACAO_SEGUNDOS}s</span>
    </div>
''', unsafe_allow_html=True)

# --- ⏱️ MOTOR DE REDIRECIONAMENTO POR RELÓGIO (PULA DE PÁGINA DE VERDADE) ---
segundos_atuais = datetime.now().second

# Divide o minuto em blocos de 15 segundos para decidir para onde mandar o Chrome da TV
# Se estiver nos primeiros 15s ou de 30s a 45s -> Vai para a página TEC1
if segundos_atuais < 15 or (segundos_atuais >= 30 and segundos_atuais < 45):
    st.markdown('<h2 style="text-align:center; color:#555;">Direcionando para: TEC1...</h2>', unsafe_allow_html=True)
    st.components.v1.html("""
        <script>
        window.parent.location.pathname = "/TEC1";
        </script>
    """, height=0)

# Se estiver de 15s a 30s ou de 45s a 60s -> Vai para a página TEC1 PENDENTES
else:
    st.markdown('<h2 style="text-align:center; color:#555;">Direcionando para: TEC1 PENDENTES...</h2>', unsafe_allow_html=True)
    st.components.v1.html("""
        <script>
        window.parent.location.pathname = "/TEC1_PENDENTES";
        </script>
    """, height=0)

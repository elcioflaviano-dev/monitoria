import streamlit as st
import pandas as pd
import os
import time

# 1. Configuração (Ajustado para 8 segundos)
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"
TEMPO_ROTACAO_SEGUNDOS = 8 

# ... (Mantenha o carregamento do df_master e controladores de sessão iguais)
# ... (Certifique-se de que o id_unico_fala e o bloco st.components.v1.html estejam presentes na tela CENARIO)

    if sub_tela_atual == "CENARIO":
        st.markdown(f'<div class="title-supervisor-tv">👤 SUPERVISÃO: {supervisor_titulo}</div>', unsafe_allow_html=True)
        
        # [Cards de KPI aqui...]

        # 🔥 GATILHO DA VOZ REATIVADO
        id_unico_fala = f"{supervisor_titulo}_{p_total}_{r_total}_{i_total}"
        if st.session_state["chave_fala_gatilho"] != id_unico_fala:
            frase_narracao = f"Supervisor {supervisor_titulo}, possui {p_total} pendentes."
            st.components.v1.html(f"""
                <script>
                    var msg = new SpeechSynthesisUtterance("{frase_narracao}");
                    msg.lang = "pt-BR";
                    window.speechSynthesis.speak(msg);
                </script>
            """, height=0, width=0)
            st.session_state["chave_fala_gatilho"] = id_unico_fala

# [Restante do código...]

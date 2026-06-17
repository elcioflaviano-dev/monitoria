import streamlit as st
import pandas as pd
import os
import time
import base64
from datetime import datetime, timedelta

# [MANTENHA TODAS AS SUAS CONFIGURAÇÕES DE CAMINHOS E CSS COMO ESTÃO]
# ... (O cabeçalho e CSS que você já tem funcionam bem) ...

# ... [MANTENHA AS LISTAS FIXAS E A LÓGICA DE CARREGAMENTO] ...

# =========================================================================
# ⚙️ MÁQUINA DE TEMPO E ESTADOS (CONFIGURADA PARA O CICLO PEDIDO)
# =========================================================================
if "idx" not in st.session_state: 
    st.session_state.idx = 0
    st.session_state.last_time = time.time()
    st.session_state.novo_ciclo = True

agora_br = datetime.utcnow() - timedelta(hours=3)
antes_0830 = (agora_br.hour < 8) or (agora_br.hour == 8 and agora_br.minute < 30)
depois_0900 = (agora_br.hour >= 9)

# ⏳ TEMPOS DE EXIBIÇÃO (Relógio com 60s, outros com 30s)
esperas = {0: 60, 1: 30, 2: 60, 3: 30, 4: 1}

tempo_passado = time.time() - st.session_state.last_time

if tempo_passado > esperas.get(st.session_state.idx, 10):
    if antes_0830:
        st.session_state.idx = 0 # Fixo nos técnicos
    else:
        # CICLO: Relógio(2) -> Branca(4) -> TEC1(1) -> Branca(4) -> Relógio(2) -> Branca(4) -> Indicadores(3) -> Branca(4)
        fluxo = {2: 4, 4: 1, 1: 4, 4: 2, 2: 4, 4: 3, 3: 4, 4: 2}
        # Se for antes das 09:00, pula os indicadores (3)
        if not depois_0900 and st.session_state.idx == 2:
            st.session_state.idx = 1
        else:
            st.session_state.idx = fluxo.get(st.session_state.idx, 2)
            
    st.session_state.last_time = time.time()
    st.session_state.novo_ciclo = True
    st.rerun()

# =========================================================================
# TELA 4: TELA BRANCA (LIMPEZA)
# =========================================================================
if st.session_state.idx == 4:
    st.markdown('<div style="height: 100vh; background-color: #ffffff;"></div>', unsafe_allow_html=True)

# =========================================================================
# TELA 0: TÉCNICOS NA BASE
# =========================================================================
elif st.session_state.idx == 0:
    # ... [MANTER O CÓDIGO DA TELA 0 QUE VOCÊ JÁ TEM] ...

# =========================================================================
# TELA 1: CONTRATOS PENDENTES (TEC1)
# =========================================================================
elif st.session_state.idx == 1:
    # ... [MANTER O CÓDIGO DA TELA 1 QUE VOCÊ JÁ TEM] ...

# =========================================================================
# TELA 2: RELÓGIO
# =========================================================================
elif st.session_state.idx == 2:
    st.markdown('<div class="relogio-container"><div class="hora-gigante">{}</div></div>'.format(datetime.now().strftime("%H:%M:%S")), unsafe_allow_html=True)

# =========================================================================
# TELA 3: INDICADORES (NR35/CERT/BST)
# =========================================================================
elif st.session_state.idx == 3:
    st.markdown('<h1 style="text-align:center;">📊 INDICADORES OPERACIONAIS</h1>', unsafe_allow_html=True)
    df_ind = pd.read_csv(ARQUIVO_INDICADORES) if os.path.exists(ARQUIVO_INDICADORES) else pd.DataFrame()
    
    if not df_ind.empty:
        c1, c2 = st.columns(2)
        # --- FUNÇÃO DE RENDERIZAÇÃO DOS BLOCOS (IDÊNTICA AO TEC1) ---
        def renderizar_bloco(base, col):
            df_base = df_ind[df_ind["BASE"] == base]
            for sup in sorted(df_base['SUPERVISOR'].unique()):
                d = df_base[df_base['SUPERVISOR'] == sup]
                f_nr = int(d[d["INDICADOR"]=="NR35"]["VALOR"].sum())
                f_ct = int(d[d["INDICADOR"]=="Certidão"]["VALOR"].sum())
                f_bt = int(d[d["INDICADOR"]=="BST"]["VALOR"].sum())
                
                with col:
                    st.markdown(f'''
                        <div class="box-contagem">
                            <div class="box-nome">📋 {sup}</div>
                            <div style="display:flex; justify-content:space-around;">
                                <div class="falta-box"><div class="falta-label">NR35</div><div class="box-num">{f_nr}</div></div>
                                <div class="falta-box"><div class="falta-label">CERT</div><div class="box-num">{f_ct}</div></div>
                                <div class="falta-box"><div class="falta-label">BST</div><div class="box-num">{f_bt}</div></div>
                            </div>
                        </div>
                    ''', unsafe_allow_html=True)

        renderizar_bloco(df_ind[df_ind["BASE"] == "ABC"], c1)
        renderizar_bloco(df_ind[df_ind["BASE"] == "SP"], c2)

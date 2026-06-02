import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

st.markdown("""<style>
    [data-testid="stSidebar"] { display: none !important; }
    .topo-container { background: #003366; color: white; padding: 25px; border-radius: 0 0 15px 15px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;}
    .nome-sup { font-size: 45px; font-weight: 900; }
    
    /* Estilos das Contagens (Supervisores e Bases) */
    .box-contagem { background: #f0f2f6; border-left: 8px solid #cc6600; padding: 25px 10px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); height: 100%;}
    .box-nome { font-size: 22px; font-weight: 900; color: #003366; text-transform: uppercase;}
    .box-num { font-size: 80px; font-weight: 900; color: #cc6600; margin-top: 15px; line-height: 1; }
    
    .hora-gigante { font-size: 150px; text-align:center; margin-top: 100px; color: #333; }
</style>""", unsafe_allow_html=True)

SUPERVISORES = ["MAICON", "NELSON", "MARCOS ROBERTO", "ALAN", "FRANCISCO GERALDO CARVALHO JUNIOR"]

# Nomes mais curtos apenas para visualização amigável na tela
NOMES_VISUAIS = {
    "MAICON": "MAICON", 
    "NELSON": "NELSON", 
    "MARCOS ROBERTO": "MARCOS ROBERTO", 
    "ALAN": "ALAN", 
    "FRANCISCO GERALDO CARVALHO JUNIOR": "FRANCISCO"
}

if "idx" not in st.session_state: st.session_state.idx = 0
if "last_time" not in st.session_state: st.session_state.last_time = time.time()
if "falar" not in st.session_state: st.session_state.falar = True

# Lógica de Telas (0 = Supervisores, 1 = Bases, 2 = Relógio)
if st.session_state.idx == 0: 
    espera = 38 # 7 segundos x 5 supervisores + folga
elif st.session_state.idx == 1: 
    espera = 18 # 8 segundos x 2 bases + folga
else: 
    espera = 20 # Tempo do relógio na tela

tempo_passado = time.time() - st.session_state.last_time

if tempo_passado > espera:
    st.session_state.idx = (st.session_state.idx + 1) % 3 # Alterna entre 0, 1 e 2
    st.session_state.last_time = time.time()
    st.session_state.falar = True
    st.rerun()

# --- SCRIPT JAVASCRIPT BASE PARA O APITO DE CRUZEIRO E VOZ LUCIANA ---
JS_MOTOR_AUDIO = """
function tocarApitoCruzeiro() {
    try {
        let ctx = new (window.AudioContext || window.webkitAudioContext)();
        let osc = ctx.createOscillator();
        let gain = ctx.createGain();
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.type = 'triangle'; // Onda mais encorpada e grave
        osc.frequency.setValueAtTime(110, ctx.currentTime); // Frequência grave de navio
        
        gain.gain.setValueAtTime(0, ctx.currentTime);
        gain.gain.linearRampToValueAtTime(0.8, ctx.currentTime + 0.2); // Ataque
        gain.gain.setValueAtTime(0.8, ctx.currentTime + 1.2); // Sustentação
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 2.0); // Fim
        
        osc.start(ctx.currentTime);
        osc.stop(ctx.currentTime + 2.0);
    } catch(e) {}
}

function anunciar(texto, delay) {
    setTimeout(() => {
        tocarApitoCruzeiro();
        // A voz fala 1.8 segundos após o apito começar, para não embolar os sons
        setTimeout(() => {
            let m = new SpeechSynthesisUtterance(texto);
            m.lang = 'pt-BR';
            m.rate = 1.0;
            
            // Busca as vozes do sistema e prioriza a Luciana
            let voices = window.speechSynthesis.getVoices();
            let vozLuciana = voices.find(v => v.name.includes('Luciana'));
            let vozAlternativa = voices.find(v => v.lang.includes('pt-BR') && v.name.includes('Google')) || voices.find(v => v.lang.includes('pt-BR'));
            
            if(vozLuciana) { m.voice = vozLuciana; } 
            else if(vozAlternativa) { m.voice = vozAlternativa; }
            
            window.speechSynthesis.speak(m);
        }, 1800); 
    }, delay);
}
"""

# Limpeza total forçada da tela
placeholder = st.empty()

with placeholder.container():
    if st.session_state.idx == 0: titulo_topo = "RESUMO POR SUPERVISOR"
    elif st.session_state.idx == 1: titulo_topo = "RESUMO POR BASE REGIONAL"
    else: titulo_topo = "PAUSA"
    
    st.markdown(f'''<div class="topo-container">
        <div class="nome-sup">{titulo_topo}</div>
        <a href="/" style="color:#fff; font-size:18px; font-weight:bold; border:2px solid #fff; padding:8px 15px; border-radius:5px; text-decoration:none;">🏠 HOME</a>
    </div>''', unsafe_allow_html=True)

    # PROCESSAMENTO DE DADOS (Comum para a Tela 0 e Tela 1)
    if st.session_state.idx in [0, 1]:
        if os.path.exists("rota_sincronizada.csv"):
            df = pd.read_csv("rota_sincronizada.csv", dtype=str)
            df.columns = [str(c).strip() for c in df.columns]
            
            def padronizar_supervisor(nome):
                n = str(nome).upper().strip()
                if 'ALAN' in n: return 'ALAN'
                if 'MARCOS' in n: return 'MARCOS ROBERTO'
                if 'FRANCISCO' in n: return 'FRANCISCO GERALDO CARVALHO JUNIOR'
                if 'MAICON' in n: return 'MAICON'
                if 'NELSON' in n: return 'NELSON'
                return n
            
            df['SUPERVISOR_CLEAN'] = df['SUPERVISOR'].apply(padronizar_supervisor)
            
            col_status_real = 'Status da Atividade' if 'Status da Atividade' in df.columns else 'STATUS_ATIVIDADE'
            df['Status_Atividade_Upper'] = df[col_status_real].fillna('').astype(str).str.upper().str.strip()
            df_limpo = df[df['Status_Atividade_Upper'] != 'SUSPENSO'].copy()
            
            df_limpo['P_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('PENDENTE|EM ABERTO|ABERTO|PEND', na=False).astype(int)
            df_limpo['R_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('ROTA|DESLOC|DESLOCAMENTO', na=False).astype(int)
            df_limpo['I_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('INICIADO|PRODUTIVO|EXECUCAO|INIC', na=False).astype(int)
            
            df_validos = df_limpo[(df_limpo['P_COUNT'] > 0) | (df_limpo['R_COUNT'] > 0) | (df_limpo['I_COUNT'] > 0)].copy()
            
            col_janela = None
            for c in df_validos.columns:
                if 'JANELA' in str(c).upper() or 'INTERVALO' in str(c).upper():
                    col_janela = c
                    break

            hora_atual = (datetime.utcnow() - timedelta(hours=3)).hour
            df_pendentes_geral = pd.DataFrame()

            if col_janela is not None and not df_validos.empty:
                df_validos['Intervalo_Tratado'] = df_validos[col_janela].fillna('').astype(str).str.strip()
                def extrair_hora_limite(janela_str):
                    try: return int(janela_str.replace(':', '').split('-')[1].strip()[:2])
                    except: return 24
                df_validos['Hora_Limite_Janela'] = df_validos['Intervalo_Tratado'].apply(extrair_hora_limite)
                
                if hora_atual < 12: condicao_horario = (df_validos['Hora_Limite_Janela'] <= 12)
                elif 12 <= hora_atual < 15: condicao_horario = (df_validos['Hora_Limite_Janela'] <= 15)
                else: condicao_horario = (df_validos['Hora_Limite_Janela'] <= 24)

                df_base_janela = df_validos[condicao_horario | (df_validos['R_COUNT'] > 0) | (df_validos['I_COUNT'] > 0)].copy()
                df_pendentes_geral = df_base_janela[df_base_janela['P_COUNT'] > 0].copy()
                
                if df_pendentes_geral.empty and df_base_janela.empty: 
                    df_pendentes_geral = df_validos[df_validos['P_COUNT'] > 0].copy()
            else:
                df_pendentes_geral = df_validos[df_validos['P_COUNT'] > 0].copy()

            if 'Contrato' in df_pendentes_geral.columns and not df_pendentes_geral.empty:
                df_pendentes_geral['Contrato'] = df_pendentes_geral['Contrato'].astype(str).apply(lambda x: x.split('.')[0] if '.' in x else x)
                df_pendentes_geral = df_pendentes_geral.drop_duplicates(subset=['Contrato'])


            # --- TELA 0: SUPERVISORES ---
            if st.session_state.idx == 0:
                cols = st.columns(len(SUPERVISORES))
                script_cenario = f"<script>{JS_MOTOR_AUDIO}"
                
                for i, sup_full in enumerate(SUPERVISORES):
                    qtd_pendentes = len(df_pendentes_geral[df_pendentes_geral['SUPERVISOR_CLEAN'] == sup_full])
                    nome_visual = NOMES_VISUAIS.get(sup_full, sup_full)
                    
                    with cols[i]:
                        st.markdown(f'''<div class="box-contagem">
                            <div class="box-nome">{nome_visual}</div>
                            <div class="box-num">{qtd_pendentes}</div>
                        </div>''', unsafe_allow_html=True)
                    
                    texto_fala = f"Supervisor {nome_visual}, {qtd_pendentes} pendentes."
                    script_cenario += f"anunciar('{texto_fala}', {i * 7000});\n"
                
                script_cenario += "</script>"
                
                if st.session_state.falar:
                    st.components.v1.html(script_cenario, height=0)
                    st.session_state.falar = False

            # --- TELA 1: BASES (ABC e SP) ---
            elif st.session_state.idx == 1:
                # Regras de separação de bases
                cond_sp = df_pendentes_geral['SUPERVISOR_CLEAN'].str.contains('FRANCISCO|ALAN', na=False)
                qtd_sp = len(df_pendentes_geral[cond_sp])
                qtd_abc = len(df_pendentes_geral[~cond_sp])

                c_abc, c_sp = st.columns(2)
                
                with c_abc:
                    st.markdown(f'''<div class="box-contagem" style="border-left-color: #008080;">
                        <div class="box-nome" style="color: #008080;">ABC PENDENTES</div>
                        <div class="box-num">{qtd_abc}</div>
                    </div>''', unsafe_allow_html=True)
                    
                with c_sp:
                    st.markdown(f'''<div class="box-contagem" style="border-left-color: #b30000;">
                        <div class="box-nome" style="color: #b30000;">SÃO PAULO PENDENTES</div>
                        <div class="box-num">{qtd_sp}</div>
                    </div>''', unsafe_allow_html=True)

                script_cenario = f"<script>{JS_MOTOR_AUDIO}"
                script_cenario += f"anunciar('Base A B C. Total, {qtd_abc} pendentes.', 0);\n"
                script_cenario += f"anunciar('Base São Paulo. Total, {qtd_sp} pendentes.', 8000);\n"
                script_cenario += "</script>"

                if st.session_state.falar:
                    st.components.v1.html(script_cenario, height=0)
                    st.session_state.falar = False

        else:
            st.error("Arquivo rota_sincronizada.csv não encontrado.")
            
    # --- TELA 2: PAUSA / HORA ---
    elif st.session_state.idx == 2:
        tempo_real = datetime.utcnow() - timedelta(hours=3)
        hora_str = tempo_real.strftime("%H:%M:%S")
        hora_fala = tempo_real.strftime("%H e %M") 
        
        st.markdown(f'<div class="hora-gigante">{hora_str}</div>', unsafe_allow_html=True)
        
        if st.session_state.falar:
            script_cenario = f"<script>{JS_MOTOR_AUDIO}"
            script_cenario += f"anunciar('Atenção. Hora certa: {hora_fala}.', 0);\n"
            script_cenario += "</script>"
            
            st.components.v1.html(script_cenario, height=0)
            st.session_state.falar = False

time.sleep(1); st.rerun()

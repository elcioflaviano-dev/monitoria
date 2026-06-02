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
    
    /* Estilos da Tela 1 (Contagem) */
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

# Lógica de Telas (0 = Resumo Quantidades, 1 = Relógio)
if st.session_state.idx == 0: 
    espera = 36 # 7 segundos x 5 supervisores = ~35s
else: 
    espera = 20 # Tempo do relógio na tela

tempo_passado = time.time() - st.session_state.last_time

if tempo_passado > espera:
    st.session_state.idx = (st.session_state.idx + 1) % 2 
    st.session_state.last_time = time.time()
    st.session_state.falar = True
    st.rerun()

# APAGADOR DE TELA
conteudo = st.empty()
conteudo.empty()

with conteudo.container():
    titulo_topo = "RESUMO DE PENDENTES" if st.session_state.idx == 0 else "PAUSA"
    
    st.markdown(f'''<div class="topo-container">
        <div class="nome-sup">{titulo_topo}</div>
        <a href="/" style="color:#fff; font-size:18px; font-weight:bold; border:2px solid #fff; padding:8px 15px; border-radius:5px; text-decoration:none;">🏠 HOME</a>
    </div>''', unsafe_allow_html=True)

    # --- TELA 1: RESUMO DE QUANTIDADES ---
    if st.session_state.idx == 0:
        if os.path.exists("rota_sincronizada.csv"):
            df = pd.read_csv("rota_sincronizada.csv", dtype=str)
            df.columns = [str(c).strip() for c in df.columns]
            
            # --- PADRONIZADOR FLEXÍVEL DE SUPERVISORES ---
            def padronizar_supervisor(nome):
                n = str(nome).upper().strip()
                if 'ALAN' in n: return 'ALAN'
                if 'MARCOS' in n: return 'MARCOS ROBERTO'
                if 'FRANCISCO' in n: return 'FRANCISCO GERALDO CARVALHO JUNIOR'
                if 'MAICON' in n: return 'MAICON'
                if 'NELSON' in n: return 'NELSON'
                return n
            
            df['SUPERVISOR_CLEAN'] = df['SUPERVISOR'].apply(padronizar_supervisor)
            
            # --- MOTOR DE JANELAS CUMULATIVAS (TEC1) ---
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

            cols = st.columns(len(SUPERVISORES))
            
            # === CÓDIGO JAVASCRIPT: SINO + VOZ PERSONALIZADA ===
            script_voz = """<script>
            function anunciarComSino(texto, delay) {
                setTimeout(() => {
                    // 1. Sintetiza um som de "Sino de Aeroporto"
                    try {
                        let ctx = new (window.AudioContext || window.webkitAudioContext)();
                        let osc = ctx.createOscillator();
                        let gain = ctx.createGain();
                        osc.connect(gain);
                        gain.connect(ctx.destination);
                        osc.type = 'sine'; // Som suave e arredondado
                        osc.frequency.setValueAtTime(880, ctx.currentTime); // Frequência do sino
                        gain.gain.setValueAtTime(0.3, ctx.currentTime);
                        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 1.2);
                        osc.start(ctx.currentTime);
                        osc.stop(ctx.currentTime + 1.2);
                    } catch(e) { console.log(e); }

                    // 2. Falar o texto 0.8 segundos após o sino tocar
                    setTimeout(() => {
                        let m = new SpeechSynthesisUtterance(texto);
                        m.lang = 'pt-BR';
                        m.rate = 1.0;  // VELOCIDADE DA VOZ: (0.5 lento, 1.0 normal, 1.5 rápido)
                        m.pitch = 1.0; // TOM DA VOZ: (0 baixo, 1.0 normal, 2.0 agudo)
                        
                        // Busca uma voz feminina agradável (Google, Maria, Luciana) se disponível na TV
                        let voices = window.speechSynthesis.getVoices();
                        let ptVoice = voices.find(v => v.lang.includes('pt-BR') && (v.name.includes('Google') || v.name.includes('Maria') || v.name.includes('Luciana'))) || voices.find(v => v.lang.includes('pt-BR'));
                        if(ptVoice) { m.voice = ptVoice; }
                        
                        window.speechSynthesis.speak(m);
                    }, 800);
                }, delay);
            }
            """
            
            for i, sup_full in enumerate(SUPERVISORES):
                qtd_pendentes = len(df_pendentes_geral[df_pendentes_geral['SUPERVISOR_CLEAN'] == sup_full])
                nome_visual = NOMES_VISUAIS.get(sup_full, sup_full)
                
                with cols[i]:
                    st.markdown(f'''<div class="box-contagem">
                        <div class="box-nome">{nome_visual}</div>
                        <div class="box-num">{qtd_pendentes}</div>
                    </div>''', unsafe_allow_html=True)
                
                texto_fala = f"Supervisor {nome_visual}, {qtd_pendentes} pendentes."
                script_voz += f"anunciarComSino('{texto_fala}', {i * 7000});\n"
            
            script_voz += "</script>"
            
            if st.session_state.falar:
                st.components.v1.html(script_voz, height=0)
                st.session_state.falar = False

        else:
            st.error("Arquivo rota_sincronizada.csv não encontrado.")
            
    # --- TELA 2: PAUSA / HORA (Com Sino e Voz) ---
    elif st.session_state.idx == 1:
        tempo_real = datetime.utcnow() - timedelta(hours=3)
        hora_str = tempo_real.strftime("%H:%M:%S")
        hora_fala = tempo_real.strftime("%H e %M") 
        
        st.markdown(f'<div class="hora-gigante">{hora_str}</div>', unsafe_allow_html=True)
        
        if st.session_state.falar:
            script_hora = f"""<script>
            // Sino para a hora certa
            try {{
                let ctx = new (window.AudioContext || window.webkitAudioContext)();
                let osc = ctx.createOscillator();
                let gain = ctx.createGain();
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.type = 'sine';
                osc.frequency.setValueAtTime(880, ctx.currentTime);
                gain.gain.setValueAtTime(0.3, ctx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 1.2);
                osc.start(ctx.currentTime);
                osc.stop(ctx.currentTime + 1.2);
            }} catch(e) {{}}

            setTimeout(() => {{
                let m = new SpeechSynthesisUtterance('Atenção. Hora certa: {hora_fala}.');
                m.lang = 'pt-BR';
                m.rate = 1.0; 
                m.pitch = 1.0;
                let voices = window.speechSynthesis.getVoices();
                let ptVoice = voices.find(v => v.lang.includes('pt-BR') && (v.name.includes('Google') || v.name.includes('Maria') || v.name.includes('Luciana'))) || voices.find(v => v.lang.includes('pt-BR'));
                if(ptVoice) {{ m.voice = ptVoice; }}
                window.speechSynthesis.speak(m);
            }}, 800);
            </script>"""
            st.components.v1.html(script_hora, height=0)
            st.session_state.falar = False

time.sleep(1); st.rerun()

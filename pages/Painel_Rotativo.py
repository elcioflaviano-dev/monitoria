import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta

# Configuração da Página
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

st.markdown("""<style>
    [data-testid="stSidebar"] { display: none !important; }
    .topo-container { background: #003366; color: white; padding: 25px; border-radius: 0 0 15px 15px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;}
    .nome-sup { font-size: 45px; font-weight: 900; }
    
    /* Estilos das Bases (Topo) */
    .box-base { background: #e8f5e9; border-left: 10px solid #2e7d32; padding: 15px 10px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.15); margin-bottom: 10px; }
    .box-base-sp { background: #ffebee; border-left: 10px solid #c62828; padding: 15px 10px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.15); margin-bottom: 10px; }
    .nome-base { font-size: 28px; font-weight: 900; color: #333; text-transform: uppercase;}
    .num-base { font-size: 85px; font-weight: 900; color: #111; line-height: 1.1; }
    
    /* Estilos dos Supervisores (Inferior) com Animação Suave */
    .box-contagem { 
        background: #f0f2f6; border-left: 8px solid #cc6600; padding: 15px 5px; 
        text-align: center; border-radius: 8px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); 
        margin-top: 5px; margin-left: 5px; margin-right: 5px;
        transition: transform 0.5s ease, box-shadow 0.5s ease, background 0.5s ease, border-left 0.5s ease, z-index 0.5s ease; 
        position: relative; z-index: 1; 
    }
    .box-nome { font-size: 18px; font-weight: 900; color: #003366; text-transform: uppercase;}
    .box-num { font-size: 65px; font-weight: 900; color: #cc6600; line-height: 1; }
    
    /* CLASSE MÁGICA: Destaque com Z-index para não cortar */
    .destaque-ativo {
        transform: scale(1.35) !important;
        box-shadow: 0px 25px 45px rgba(204, 102, 0, 0.6) !important;
        border-left: 20px solid #ff8800 !important;
        background: #fff8e1 !important;
        z-index: 9999 !important; 
    }
    
    /* Estilos do Relógio Moderno */
    .relogio-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 60vh; }
    .hora-gigante { font-size: 180px; font-weight: 900; color: #003366; text-shadow: 4px 4px 10px rgba(0,0,0,0.1); line-height: 1; letter-spacing: 5px; }
    .data-media { font-size: 40px; color: #666; font-weight: bold; margin-top: -20px; }
</style>""", unsafe_allow_html=True)

SUPERVISORES = ["MAICON", "NELSON", "MARCOS ROBERTO", "ALAN", "FRANCISCO GERALDO CARVALHO JUNIOR"]

NOMES_VISUAIS = {
    "MAICON": "MAICON", "NELSON": "NELSON", "MARCOS ROBERTO": "MARCOS ROBERTO", 
    "ALAN": "ALAN", "FRANCISCO GERALDO CARVALHO JUNIOR": "FRANCISCO"
}

# Inicialização de Variáveis e Agendadores
if "idx" not in st.session_state: st.session_state.idx = 0
if "last_time" not in st.session_state: st.session_state.last_time = time.time()

# Controles de Frequência de Áudio
if "falar_dados" not in st.session_state: st.session_state.falar_dados = False
if "falar_hora" not in st.session_state: st.session_state.falar_hora = False
if "ultimo_aviso_dados" not in st.session_state: st.session_state.ultimo_aviso_dados = 0
if "ultima_hora_falada" not in st.session_state: st.session_state.ultima_hora_falada = -1

# Tempos de ecrã (O ciclo completo leva cerca de 75 segundos)
if st.session_state.idx == 0: espera = 55 
else: espera = 20 

tempo_passado = time.time() - st.session_state.last_time

# === MOTOR DE TRANSIÇÃO E AGENDAMENTO ===
if tempo_passado > espera:
    st.session_state.idx = (st.session_state.idx + 1) % 2 
    st.session_state.last_time = time.time()
    
    agora_br = datetime.utcnow() - timedelta(hours=3)
    minutos_agora = agora_br.hour * 60 + agora_br.minute
    
    # Avaliação das Regras de Áudio ao entrar na Tela Principal (0)
    if st.session_state.idx == 0:
        # Array com o fim das janelas em minutos do dia
        finais_janela_minutos = [11*60, 12*60, 14*60, 15*60, 17*60, 18*60]
        freq_segundos = None
        
        # Encontra a janela atual/mais próxima
        for fim in finais_janela_minutos:
            dif = fim - minutos_agora
            if 0 < dif <= 60: # Estamos na "Hora de Ouro" (últimos 60 min)
                if dif <= 10:
                    freq_segundos = 150 # Zona de Perigo (A cada 2.5 min)
                else:
                    freq_segundos = 600 # Modo Alerta (A cada 10 min)
                break
        
        # Se estivermos dentro de uma janela de alerta, verificamos o cronômetro
        if freq_segundos is not None:
            if time.time() - st.session_state.ultimo_aviso_dados >= (freq_segundos - 10):
                st.session_state.falar_dados = True
                st.session_state.ultimo_aviso_dados = time.time()
            else:
                st.session_state.falar_dados = False
        else:
            st.session_state.falar_dados = False # Silêncio total fora dos horários de pico
            
    # Avaliação das Regras de Áudio ao entrar na Tela do Relógio (1)
    elif st.session_state.idx == 1:
        # Falar a hora apenas aos 00 ou 30 minutos (Ex: 14:00, 14:30, 15:00)
        if agora_br.minute in [0, 30] and st.session_state.ultima_hora_falada != agora_br.minute:
            st.session_state.falar_hora = True
            st.session_state.ultima_hora_falada = agora_br.minute
        else:
            st.session_state.falar_hora = False
            
    st.rerun()

# --- SCRIPT JAVASCRIPT: ALERTA E VOZ FEMININA ---
JS_MOTOR_AUDIO = """
function tocarAlertaChamaAtencao() {
    try {
        let ctx = new (window.AudioContext || window.webkitAudioContext)();
        let tempo = ctx.currentTime;
        let osc1 = ctx.createOscillator(); let gain1 = ctx.createGain();
        osc1.type = 'triangle'; osc1.frequency.setValueAtTime(880, tempo);
        gain1.gain.setValueAtTime(0, tempo); gain1.gain.linearRampToValueAtTime(1.0, tempo + 0.05); gain1.gain.exponentialRampToValueAtTime(0.01, tempo + 0.6);
        osc1.connect(gain1); gain1.connect(ctx.destination); osc1.start(tempo); osc1.stop(tempo + 0.6);
        
        let osc2 = ctx.createOscillator(); let gain2 = ctx.createGain();
        osc2.type = 'triangle'; osc2.frequency.setValueAtTime(659.25, tempo + 0.4);
        gain2.gain.setValueAtTime(0, tempo + 0.4); gain2.gain.linearRampToValueAtTime(1.0, tempo + 0.45); gain2.gain.exponentialRampToValueAtTime(0.01, tempo + 1.5);
        osc2.connect(gain2); gain2.connect(ctx.destination); osc2.start(tempo + 0.4); osc2.stop(tempo + 1.5);
    } catch(e) {}
}

function anunciar(texto, delay) {
    setTimeout(() => {
        tocarAlertaChamaAtencao();
        setTimeout(() => {
            let m = new SpeechSynthesisUtterance(texto);
            m.lang = 'pt-BR'; m.rate = 1.0;
            function setVoiceAndSpeak() {
                let voices = window.speechSynthesis.getVoices();
                let vozLuciana = voices.find(v => v.name.includes('Luciana')) || voices.find(v => v.name.includes('Maria')) || voices.find(v => v.lang.includes('pt-BR'));
                if(vozLuciana) { m.voice = vozLuciana; } 
                window.speechSynthesis.speak(m);
            }
            if (window.speechSynthesis.getVoices().length === 0) { window.speechSynthesis.onvoiceschanged = setVoiceAndSpeak; } 
            else { setVoiceAndSpeak(); }
        }, 1500); 
    }, delay);
}

// Limpar o destaque de todos os supervisores
function limparDestaques(total) {
    for(let j=0; j<total; j++) {
        let el = window.parent.document.getElementById('sup-box-' + j);
        if(el) { el.classList.remove('destaque-ativo'); }
    }
}

// Focar na caixa do supervisor e acionar a voz
function anunciarSupervisor(texto, delay, index, totalSup) {
    setTimeout(() => {
        limparDestaques(totalSup);
        let elAtual = window.parent.document.getElementById('sup-box-' + index);
        if(elAtual) { elAtual.classList.add('destaque-ativo'); }
        
        tocarAlertaChamaAtencao();
        setTimeout(() => {
            let m = new SpeechSynthesisUtterance(texto);
            m.lang = 'pt-BR'; m.rate = 1.0;
            let voices = window.speechSynthesis.getVoices();
            let vozLuciana = voices.find(v => v.name.includes('Luciana')) || voices.find(v => v.name.includes('Maria')) || voices.find(v => v.lang.includes('pt-BR'));
            if(vozLuciana) { m.voice = vozLuciana; }
            window.speechSynthesis.speak(m);
        }, 1500);
    }, delay);
}
"""

# Limpeza da tela antes de desenhar a nova versão
placeholder = st.empty()

with placeholder.container():

    # === RENDERIZAÇÃO DA TELA 0: VISÃO GERAL ===
    if st.session_state.idx == 0: 
        st.markdown(f'''<div class="topo-container">
            <div class="nome-sup">RESUMO GERAL DA OPERAÇÃO</div>
            <a href="/" style="color:#fff; font-size:18px; font-weight:bold; border:2px solid #fff; padding:8px 15px; border-radius:5px; text-decoration:none;">🏠 HOME</a>
        </div>''', unsafe_allow_html=True)

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
                df_pendentes_geral['Contrato'] = df_pendentes_geral['Contrato'].fillna('').astype(str).apply(lambda x: str(x).split('.')[0])
                df_pendentes_geral = df_pendentes_geral.drop_duplicates(subset=['Contrato'])

            # 1. LINHA DE CIMA: BASES
            cond_sp = df_pendentes_geral['SUPERVISOR_CLEAN'].str.contains('FRANCISCO|ALAN', na=False)
            qtd_sp = len(df_pendentes_geral[cond_sp])
            qtd_abc = len(df_pendentes_geral[~cond_sp])

            c_abc, c_sp = st.columns(2)
            with c_abc:
                st.markdown(f'''<div class="box-base">
                    <div class="nome-base" style="color: #2e7d32;">ABC PENDENTES</div>
                    <div class="num-base">{qtd_abc}</div>
                </div>''', unsafe_allow_html=True)
                
            with c_sp:
                st.markdown(f'''<div class="box-base-sp">
                    <div class="nome-base" style="color: #c62828;">SÃO PAULO PENDENTES</div>
                    <div class="num-base">{qtd_sp}</div>
                </div>''', unsafe_allow_html=True)

            # 2. LINHA DE BAIXO: SUPERVISORES
            cols_sup = st.columns(len(SUPERVISORES))
            script_cenario = f"<script>{JS_MOTOR_AUDIO}"
            
            # Só preenchemos o script de áudio se for a hora certa de falar (Agendamento)
            if st.session_state.falar_dados:
                script_cenario += f"anunciar('Resumo geral da operação. Base A B C: {qtd_abc} pendentes.', 0);\n"
                script_cenario += f"anunciar('Base São Paulo: {qtd_sp} pendentes.', 7000);\n"
            
            for i, sup_full in enumerate(SUPERVISORES):
                qtd_pendentes = len(df_pendentes_geral[df_pendentes_geral['SUPERVISOR_CLEAN'] == sup_full])
                nome_visual = NOMES_VISUAIS.get(sup_full, sup_full)
                
                with cols_sup[i]:
                    st.markdown(f'''<div id="sup-box-{i}" class="box-contagem">
                        <div class="box-nome">{nome_visual}</div>
                        <div class="box-num">{qtd_pendentes}</div>
                    </div>''', unsafe_allow_html=True)
                
                # Só programa as falas e os zooms se o modo "Falar" estiver ativado nesta rodada
                if st.session_state.falar_dados:
                    texto_fala = f"Supervisor {nome_visual}: {qtd_pendentes} pendentes."
                    script_cenario += f"anunciarSupervisor('{texto_fala}', {14000 + i * 7000}, {i}, {len(SUPERVISORES)});\n"
            
            if st.session_state.falar_dados:
                script_cenario += f"setTimeout(() => limparDestaques({len(SUPERVISORES)}), {14000 + len(SUPERVISORES) * 7000});\n"
                script_cenario += f"\n// TIMESTAMP_RUN: {time.time()}\n</script>"
                st.components.v1.html(script_cenario, height=0)
                st.session_state.falar_dados = False # Desliga o flag até o agendador reativá-lo
            else:
                # Mantém a tela totalmente muda
                st.components.v1.html("<script>// Modo Silencioso Ativo</script>", height=0)

        else:
            st.error("Ficheiro rota_sincronizada.csv não encontrado.")
            
    # --- RENDERIZAÇÃO DA TELA 1: PAUSA / HORA ---
    elif st.session_state.idx == 1:
        st.markdown(f'''<div class="topo-container">
            <div class="nome-sup">PAUSA</div>
            <a href="/" style="color:#fff; font-size:18px; font-weight:bold; border:2px solid #fff; padding:8px 15px; border-radius:5px; text-decoration:none;">🏠 HOME</a>
        </div>''', unsafe_allow_html=True)

        tempo_real = datetime.utcnow() - timedelta(hours=3)
        hora_str = tempo_real.strftime("%H:%M:%S")
        data_str = tempo_real.strftime("%d/%m/%Y")
        hora_fala = tempo_real.strftime("%H e %M") 
        
        st.markdown(f'''
        <div class="relogio-container">
            <div class="hora-gigante">{hora_str}</div>
            <div class="data-media">{data_str}</div>
        </div>
        ''', unsafe_allow_html=True)
        
        if st.session_state.falar_hora:
            script_cenario = f"<script>{JS_MOTOR_AUDIO}"
            script_cenario += f"anunciar('Atenção. Hora certa: {hora_fala}.', 0);\n"
            script_cenario += f"\n// TIMESTAMP_RUN: {time.time()}\n</script>"
            st.components.v1.html(script_cenario, height=0)
            st.session_state.falar_hora = False

time.sleep(1); st.rerun()

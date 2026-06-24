import streamlit as st
import pandas as pd
import os
import time
import base64
import calendar
from datetime import datetime, timedelta

# =========================================================================
# CONFIGURAÇÕES E PARÂMETROS OPERACIONAIS 🚀
# =========================================================================
ROOT_DIR = os.getcwd()
ARQUIVO_ROTA_DISCO = os.path.join(ROOT_DIR, "rota_sincronizada.csv")
ARQUIVO_CONSULTIVO = os.path.join(ROOT_DIR, "consultivo_sincronizado.csv")

ARQUIVO_LOGO = os.path.join(ROOT_DIR, "logo.png")
if not os.path.exists(ARQUIVO_LOGO):
    ARQUIVO_LOGO = os.path.join(ROOT_DIR, "pages", "logo.png")

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

def carregar_logo_html(caminho_imagem):
    if os.path.exists(caminho_imagem):
        try:
            with open(caminho_imagem, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f'<img src="data:image/png;base64,{encoded_string}" style="height: 100px; width: auto; object-fit: contain; display: block;">'
        except: return '<div></div>'
    return '<div></div>'

logo_html = carregar_logo_html(ARQUIVO_LOGO)

st.markdown("""<style>
    [data-testid="stHeader"] { visibility: hidden !important; }
    .stDeployButton { display: none !important; }
    footer { visibility: hidden !important; }
    #MainMenu { visibility: hidden !important; }
    [data-testid="stSidebar"] { display: none !important; }
    
    .stApp { background-color: #ffffff !important; }
    .topo-container { background: #003366; color: white; padding: 0px 30px; border-radius: 0 0 15px 15px; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; margin-bottom: 10px; height: 100px; }
    .topo-esquerda { display: flex; justify-content: flex-start; align-items: center; height: 100%; }
    .topo-centro { font-size: 45px; font-weight: 900; text-align: center; white-space: nowrap; }
    .topo-direita { display: flex; justify-content: flex-end; align-items: center; }
    .botao-home { color: #fff; font-size: 18px; font-weight: bold; border: 2px solid #fff; padding: 8px 15px; border-radius: 5px; text-decoration: none; }
    
    .box-base { background: #e8f5e9; border-left: 10px solid #2e7d32; padding: 15px 10px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.15); margin-bottom: 25px; }
    .box-base-sp { background: #e0f2f1; border-left: 10px solid #00897b; padding: 15px 10px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.15); margin-bottom: 25px; }
    .nome-base { font-size: 22px; font-weight: 900; color: #333; text-transform: uppercase;}
    .num-base { font-size: 85px; font-weight: 900; color: #111; line-height: 1.1; }
    
    .box-contagem { background: #f0f2f6; border-left: 8px solid #cc6600; padding: 10px 5px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); margin-bottom: 10px; position: relative; z-index: 1; transition: 0.3s; }
    .box-nome { font-size: 15px; font-weight: 900; color: #003366; text-transform: uppercase; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .box-num { font-size: 50px; font-weight: 900; color: #cc6600; line-height: 1; margin-top: 5px; }
    
    .destaque-ativo { transform: scale(1.15) !important; box-shadow: 0px 15px 30px rgba(204, 102, 0, 0.5) !important; border-left: 12px solid #ff8800 !important; background: #fff8e1 !important; z-index: 9999 !important; }
    .ind-base-title { font-size: 26px; font-weight: 900; text-align: center; margin-bottom: 15px; margin-top: 5px; text-transform: uppercase; }
    .ind-base-title.abc { color: #2e7d32; }
    .ind-base-title.sp { color: #00695c; }
    
    .sup-card { background: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .sup-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 10px; }
    .sup-name { font-size: 24px; font-weight: 900; color: #333; text-transform: uppercase; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}
    .badge-faltas { background: #ffebee; color: #c62828; padding: 6px 12px; border-radius: 6px; font-size: 14px; font-weight: bold; border: 1px solid #ffcdd2; }
    
    .faltas-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }
    .falta-box { background-color: #ffebee; border: 1px solid #ffcdd2; border-radius: 6px; padding: 12px 5px; text-align: center; margin-bottom: 5px; }
    .falta-label { font-size: 11px; font-weight: bold; color: #c62828; text-transform: uppercase; margin-bottom: 6px; }
    .falta-value { font-size: 32px; font-weight: 900; color: #b30000; line-height: 1; }
    
    /* 🔥 RESTAURADO: ESTILOS MAJESTOSOS DO RELÓGIO DA TV GIGANTE 🔥 */
    .relogio-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 70vh; background-color: #ffffff; width: 100%; }
    .hora-gigante { font-size: 180px; font-weight: 900; color: #003366; text-shadow: 4px 4px 10px rgba(0,0,0,0.1); line-height: 1; letter-spacing: 5px; }
    .data-media { font-size: 40px; color: #666; font-weight: bold; margin-top: -20px; }
    .tec-base-nome { background: #f8f9fa; padding: 8px 12px; border-left: 5px solid #008080; border-radius: 4px; margin-bottom: 8px; font-weight: bold; font-size: 16px; color: #333; box-shadow: 1px 1px 3px rgba(0,0,0,0.1); }
</style>""", unsafe_allow_html=True)

SUPS_ABC = ["EDSON MARCO", "MARCOS ROBERTO", "NELSON"]
SUPS_SP = ["ALAN", "FRANCISCO", "JOAO CARLOS MIRON"]
SUPERVISORES_ORDENADOS = SUPS_ABC + SUPS_SP

def obter_nome_visual(nome_completo):
    n = str(nome_completo).upper()
    if 'FRANCISCO' in n: return "FRANCISCO"
    if 'MARCOS' in n: return "MARCOS ROBERTO"
    if 'EDSON' in n: return "EDSON MARCO"
    if 'JOAO' in n or 'MIRON' in n: return "JOÃO CARLOS"
    if 'NELSON' in n: return "NELSON"
    if 'ALAN' in n: return "ALAN"
    return n.split()[0]

if "idx" not in st.session_state: 
    st.session_state.idx = 0          
    st.session_state.last_main = 0   
    st.session_state.last_time = time.time()
    st.session_state.novo_ciclo = True
    st.session_state.script_audio_atual = ""

agora_br = datetime.utcnow() - timedelta(hours=3)
alerta_fim_janela = False
if agora_br.hour in [11, 14, 17] and agora_br.minute >= 40: alerta_fim_janela = True
minutos_agora = agora_br.hour * 60 + agora_br.minute

antes_0830 = (agora_br.hour < 8) or (agora_br.hour == 8 and agora_br.minute < 30)

permitir_audio_base = False
frase_incisiva_base = ""
regras_audio_base = [
    {"inicio": 7*60 + 50, "fim": 7*60 + 59, "frase": "Atenção. Horário para concluir base."},
    {"inicio": 8*60,      "fim": 8*60 + 15, "frase": "Atenção. Iniciar rota."},
    {"inicio": 8*60 + 20, "fim": 8*60 + 30, "frase": "Atenção. Fim do horário para concluir base."}
]
for regra in regras_audio_base:
    if regra["inicio"] <= minutos_agora <= regra["fim"]:
        permitir_audio_base = True
        frase_incisiva_base = regra["frase"]
        break

permitir_audio_tec1 = False
frase_incisiva_tec1 = ""
regras_audio_tec1 = [
    {"inicio": 11*60,      "fim": 11*60 + 15, "frase": "Atenção. Horário de início de monitoria de rota."},
    {"inicio": 12*60,      "fim": 12*60 + 15, "frase": "Atenção. Fechamento de janela."},
    {"inicio": 12*60 + 30, "fim": 12*60 + 45, "frase": "Atenção. Monitoria após o fechamento da janela."},
    {"inicio": 14*60,      "fim": 14*60 + 15, "frase": "Atenção. Horário de início de monitoria de rota."},
    {"inicio": 15*60,      "fim": 15*60 + 15, "frase": "Atenção. Fechamento de janela."},
    {"inicio": 15*60 + 30, "fim": 15*60 + 45, "frase": "Atenção. Monitoria após o fechamento da janela."},
    {"inicio": 16*60,      "fim": 16*60 + 15, "frase": "Atenção. Horário de início de monitoria de rota."},
    {"inicio": 17*60,      "fim": 17*60 + 15, "frase": "Atenção. Fechamento de janela."},
    {"inicio": 17*60 + 30, "fim": 17*60 + 45, "frase": "Atenção. Monitoria após o fechamento da janela."}
]
for regra in regras_audio_tec1:
    if regra["inicio"] <= minutos_agora <= regra["fim"]:
        permitir_audio_tec1 = True
        frase_incisiva_tec1 = regra["frase"]
        break

permitir_audio_ind = False
regras_audio_ind = [(13*60, 13*60 + 15), (16*60, 16*60 + 15)]
for inicio, f in regras_audio_ind:
    if inicio <= minutos_agora <= f:
        permitir_audio_ind = True
        break

badge_mudo = '<span style="font-size: 14px; vertical-align: middle; background: #c62828; color: #fff; padding: 4px 10px; border-radius: 10px; margin-left: 15px;">🔇 ÁUDIO EM ESPERA</span>'
badge_ativo = '<span style="font-size: 14px; vertical-align: middle; background: #2e7d32; color: #fff; padding: 4px 10px; border-radius: 10px; margin-left: 15px;">🔊 ÁUDIO ATIVO</span>'

html_audio_base = badge_ativo if permitir_audio_base else badge_mudo
html_audio_tec1 = badge_ativo if permitir_audio_tec1 else badge_mudo
html_audio_ind = badge_ativo if permitir_audio_ind else badge_mudo

if st.session_state.idx == 0: espera = 60 
elif st.session_state.idx == 1: espera = 30 if alerta_fim_janela else 60 
elif st.session_state.idx == 5: espera = 60 
elif st.session_state.idx == 3: espera = 45 
elif st.session_state.idx == 2: espera = 30 if alerta_fim_janela else 60 
elif st.session_state.idx == 4: espera = 2  

tempo_passado = time.time() - st.session_state.last_time

if tempo_passado > espera:
    if antes_0830:
        if st.session_state.idx == 0:
            st.session_state.last_main = 0; prox_idx = 4
        elif st.session_state.idx == 4: prox_idx = 2
        else: prox_idx = 0
    else:
        if st.session_state.idx == 1:
            st.session_state.last_main = 1; prox_idx = 4
        elif st.session_state.idx == 5:
            st.session_state.last_main = 5; prox_idx = 4
        elif st.session_state.idx == 3:
            st.session_state.last_main = 3; prox_idx = 4
        elif st.session_state.idx == 4: 
            if st.session_state.last_main == 1: prox_idx = 5
            elif st.session_state.last_main == 5: prox_idx = 3
            elif st.session_state.last_main == 3: prox_idx = 2
            else: prox_idx = 1
        elif st.session_state.idx == 2:
            prox_idx = 1
        else:
            prox_idx = 1
            
    st.session_state.idx = prox_idx
    st.session_state.last_time = time.time()
    st.session_state.novo_ciclo = True
    st.rerun()

JS_MOTOR_AUDIO = """
function tocarAlertaChamaAtencao() {
    try {
        let ctx = new (window.parent.AudioContext || window.AudioContext)();
        let tempo = ctx.currentTime;
        let osc1 = ctx.createOscillator(); let gain1 = ctx.createGain();
        osc1.type = 'triangle'; osc1.frequency.setValueAtTime(880, tempo);
        gain1.gain.setValueAtTime(0, tempo); gain1.gain.linearRampToValueAtTime(0.4, tempo + 0.05); gain1.gain.exponentialRampToValueAtTime(0.01, tempo + 0.6);
        osc1.connect(gain1); gain1.connect(ctx.destination); osc1.start(tempo); osc1.stop(tempo + 0.6);
        let osc2 = ctx.createOscillator(); let gain2 = ctx.createGain();
        osc2.type = 'triangle'; osc2.frequency.setValueAtTime(659.25, tempo + 0.4);
        gain2.gain.setValueAtTime(0, tempo + 0.4); gain2.gain.linearRampToValueAtTime(0.4, tempo + 0.45); gain2.gain.exponentialRampToValueAtTime(0.01, tempo + 1.5);
        osc2.connect(gain2); gain2.connect(ctx.destination); osc2.start(tempo + 0.4); osc2.stop(tempo + 1.5);
    } catch(e) {}
}
function anunciarBase(texto, delay) {
    setTimeout(() => {
        tocarAlertaChamaAtencao();
        setTimeout(() => {
            let synth = window.parent.speechSynthesis || window.speechSynthesis;
            let m = new SpeechSynthesisUtterance(texto);
            m.lang = 'pt-BR'; m.rate = 1.0; m.volume = 1.0; 
            function setVoiceAndSpeak() {
                let voices = synth.getVoices();
                let vozLuciana = voices.find(v => v.name.includes('Luciana')) || voices.find(v => v.name.includes('Maria')) || voices.find(v => v.lang.includes('pt-BR'));
                if(vozLuciana) { m.voice = vozLuciana; } 
                synth.speak(m);
            }
            if (synth.getVoices().length === 0) { synth.onvoiceschanged = setVoiceAndSpeak; } 
            else { setVoiceAndSpeak(); }
        }, 1500); 
    }, delay);
}
function limparDestaques(total) {
    for(let j=0; j<total; j++) {
        let el = window.parent.document.getElementById('sup-box-' + j);
        if(el) { el.classList.remove('destaque-ativo'); }
    }
}
function animarSupervisor(texto, delay, index, totalSup) {
    setTimeout(() => {
        limparDestaques(totalSup);
        let elAtual = window.parent.document.getElementById('sup-box-' + index);
        if(elAtual) { elAtual.classList.add('destaque-ativo'); }
        tocarAlertaChamaAtencao();
        setTimeout(() => {
            let synth = window.parent.speechSynthesis || window.speechSynthesis;
            let m = new SpeechSynthesisUtterance(texto);
            m.lang = 'pt-BR'; m.rate = 1.0; m.volume = 1.0; 
            let voices = synth.getVoices();
            let vozLuciana = voices.find(v => v.name.includes('Luciana')) || voices.find(v => v.name.includes('Maria')) || voices.find(v => v.lang.includes('pt-BR'));
            if(vozLuciana) { m.voice = vozLuciana; }
            synth.speak(m);
        }, 1500);
    }, delay);
}
"""

CONTEUDO_TV = st.empty()

with CONTEUDO_TV.container():
    if st.session_state.idx == 4:
        st.markdown('<div style="height: 100vh; width: 100vw; background-color: #ffffff;"></div>', unsafe_allow_html=True)
        st.components.v1.html("", height=0)
        time.sleep(1.5)
        st.rerun()

    # -------------------------------------------------------------------------
    # TELA 0: TÉCNICOS NA BASE
    # -------------------------------------------------------------------------
    elif st.session_state.idx == 0:
        st.markdown(f'''<div class="topo-container">
            <div class="topo-esquerda">{logo_html}</div>
            <div class="topo-centro">🚀 TÉCNICOS EM BASE {html_audio_base}</div>
            <div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div>
        </div>''', unsafe_allow_html=True)

        if os.path.exists(ARQUIVO_ROTA_DISCO):
            df = pd.read_csv(ARQUIVO_ROTA_DISCO, sep=None, engine='python', dtype=str)
            df.columns = [str(c).strip().upper() for c in df.columns]
            col_recurso = next((c for c in df.columns if 'RECURSO' in c or 'NOME' in c), df.columns[0])
            col_sup = next((c for c in df.columns if 'SUPERVISOR' in c), None)
            col_status = next((c for c in df.columns if 'STATUS' in c), None)
            col_tipo_exata = next((c for c in df.columns if 'TIPO DE ATIVIDADE3' in c or 'TIPO DE ATIVIDADE 3' in c), None)

            if col_status:
                mask_status = df[col_status].fillna('').astype(str).str.lower().str.contains('pend')
                if col_tipo_exata: mask_base = df[col_tipo_exata].fillna('').astype(str).str.strip().str.lower() == 'na base'
                else:
                    cols_tipo = [c for c in df.columns if 'TIPO' in c]
                    mask_base = df[cols_tipo].apply(lambda col: col.astype(str).str.strip().str.lower() == 'na base').any(axis=1)

                mapa_tecnico_sup = {}
                if col_sup and col_recurso:
                    for _, row in df.dropna(subset=[col_recurso, col_sup]).iterrows():
                        tec = str(row[col_recurso]).upper().strip()
                        sup = str(row[col_sup]).upper().strip()
                        for oficial in SUPERVISORES_ORDENADOS:
                            if oficial in sup:
                                mapa_tecnico_sup[tec] = oficial
                                break

                def resolver_supervisor(row):
                    tec = str(row.get(col_recurso, '')).upper().strip()
                    sup = str(row.get(col_sup, '')).upper().strip() if col_sup else ''
                    for oficial in SUPERVISORES_ORDENADOS:
                        if oficial in sup: return oficial
                    return mapa_tecnico_sup.get(tec, "NÃO IDENTIFICADO")

                df_tela = df[mask_base & mask_status].copy()
                df_tela['SUPERVISOR_CLEAN'] = df_tela.apply(resolver_supervisor, axis=1)
                
                col_cidade = next((c for c in df.columns if 'CIDADE' in c), None)
                col_regiao = next((c for c in df.columns if 'REGIAO' in c or 'REGIÃO' in c or 'BASE' in c), None)

                def definir_regiao(row):
                    sup = row.get('SUPERVISOR_CLEAN', '')
                    if sup in SUPS_SP: return "SP"
                    if sup in SUPS_ABC: return "ABC"
                    cid = str(row.get(col_cidade, '')).upper() if col_cidade else ''
                    reg = str(row.get(col_regiao, '')).upper() if col_regiao else ''
                    if 'SP' in cid or 'SÃO PAULO' in cid or 'SAO PAULO' in cid: return "SP"
                    if 'SP' == reg or 'SÃO PAULO' in reg or 'SAO PAULO' in reg: return "SP"
                    return "ABC"
                
                df_tela['BASE_REGIAO'] = df_tela.apply(definir_regiao, axis=1)
                
                nomes_sp = sorted([str(n).strip().upper() for n in df_tela[df_tela['BASE_REGIAO'] == 'SP'][col_recurso].dropna().unique()])
                nomes_abc = sorted([str(n).strip().upper() for n in df_tela[df_tela['BASE_REGIAO'] == 'ABC'][col_recurso].dropna().unique()])

                c1, c2, c3, c4 = st.columns(4)
                mid_abc = (len(nomes_abc) + 1) // 2
                mid_sp = (len(nomes_sp) + 1) // 2
                
                with c1:
                    st.markdown('<div class="tec-base-nome">🏃‍♂️ ' + n + '</div>' if 'n' in dir() else f'<div class="tec-base-nome">🏃‍♂️ {nomes_abc[0] if nomes_abc else ""}</div>', unsafe_allow_html=True)
                    for n in nomes_abc[:mid_abc]: st.markdown(f'<div class="tec-base-nome">🏃‍♂️ {n}</div>', unsafe_allow_html=True)
                with c2:
                    for n in nomes_abc[mid_abc:]: st.markdown(f'<div class="tec-base-nome">🏃‍♂️ {n}</div>', unsafe_allow_html=True)
                with c3:
                    for n in nomes_sp[:mid_sp]: st.markdown(f'<div class="tec-base-nome" style="border-left-color:#c62828;">🏃‍♂️ {n}</div>', unsafe_allow_html=True)
                with c4:
                    for n in nomes_sp[mid_sp:]: st.markdown(f'<div class="tec-base-nome" style="border-left-color:#c62828;">🏃‍♂️ {n}</div>', unsafe_allow_html=True)

                if st.session_state.novo_ciclo:
                    if permitir_audio_base:
                        script_cenario = f"<script>{JS_MOTOR_AUDIO}anunciarBase('{frase_incisiva_base} Existem {len(nomes_abc)} técnicos pendentes na base A B C, e {len(nomes_sp)} na base São Paulo.', 0);</script>"
                    else:
                        script_cenario = ""
                    st.session_state.script_audio_atual = script_cenario
                    st.session_state.novo_ciclo = False 
                st.components.v1.html(st.session_state.script_audio_atual, height=0)
            else: st.error("Coluna Status não encontrada.")
        else: st.error("Ficheiro rota_sincronizada.csv não encontrado.")
        time.sleep(1)
        st.rerun()

    # -------------------------------------------------------------------------
    # TELA 1: TEC1 (SUPERVISORES PENDENTES)
    # -------------------------------------------------------------------------
    elif st.session_state.idx == 1: 
        if os.path.exists(ARQUIVO_ROTA_DISCO):
            df = pd.read_csv(ARQUIVO_ROTA_DISCO, sep=None, engine='python', dtype=str)
            df.columns = [str(c).strip().upper() for c in df.columns]
            col_tecnico = 'RECURSO' if 'RECURSO' in df.columns else df.columns[0]
            col_sup = next((c for c in df.columns if 'SUPERVISOR' in c), None)
            
            mapa_tecnico_sup = {}
            if col_sup and col_tecnico:
                for _, row in df.dropna(subset=[col_tecnico, col_sup]).iterrows():
                    tec = str(row[col_tecnico]).upper().strip()
                    sup = str(row[col_sup]).upper().strip()
                    for oficial in SUPERVISORES_ORDENADOS:
                        if oficial in sup:
                            mapa_tecnico_sup[tec] = oficial
                            break

            def resolver_supervisor(row):
                tec = str(row.get(col_tecnico, '')).upper().strip()
                sup = str(row.get(col_sup, '')).upper().strip() if col_sup else ''
                for oficial in SUPERVISORES_ORDENADOS:
                    if oficial in sup: return oficial
                return mapa_tecnico_sup.get(tec, "NÃO IDENTIFICADO")

            df['SUPERVISOR_CLEAN'] = df.apply(resolver_supervisor, axis=1)
            col_status_real = next((c for c in df.columns if 'STATUS' in c), None)
            
            hora_atual = (datetime.utcnow() - timedelta(hours=3)).hour
            if hora_atual < 12: 
                label_janela = "ATÉ 12:00"
                fala_janela = "até as 12 horas"
            elif 12 <= hora_atual < 15: 
                label_janela = "ATÉ 15:00"
                fala_janela = "até as 15 horas"
            else: 
                label_janela = "TURNO COMPLETO"
                fala_janela = "do turno completo"
            
            st.markdown(f'''<div class="topo-container">
                <div class="topo-esquerda">{logo_html}</div>
                <div class="topo-centro">TEC1 <span style="font-size: 32px; vertical-align: middle; background: #ff9800; color: #fff; padding: 6px 18px; border-radius: 30px; margin-left: 15px;">{label_janela}</span> {html_audio_tec1}</div>
                <div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div>
            </div>''', unsafe_allow_html=True)
            
            df_pendentes_geral = pd.DataFrame()
            
            if col_status_real:
                df['Status_Atividade_Upper'] = df[col_status_real].fillna('').astype(str).str.upper().str.strip()
                df_limpo = df[df['Status_Atividade_Upper'] != 'SUSPENSO'].copy()
                df_limpo['P_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('PENDENTE|EM ABERTO|ABERTO|PEND', na=False).astype(int)
                df_validos = df_limpo.copy()

                col_janela = None
                for c in df_validos.columns:
                    if 'JANELA' in str(c) or 'INTERVALO' in str(c):
                        col_janela = c
                        break

                if col_janela is not None and not df_validos.empty:
                    df_validos['Intervalo_Tratado'] = df_validos[col_janela].fillna('').astype(str).str.strip()
                    def extrair_hora_limite(janela_str):
                        try: return int(str(janela_str).replace(':', '').split('-')[1].strip()[:2])
                        except: return 24
                    df_validos['Hora_Limite_Janela'] = df_validos['Intervalo_Tratado'].apply(extrair_hora_limite)
                    
                    if hora_atual < 12: condicao_horario = (df_validos['Hora_Limite_Janela'] <= 12)
                    elif 12 <= hora_atual < 15: condicao_horario = (df_validos['Hora_Limite_Janela'] <= 15)
                    else: condicao_horario = (df_validos['Hora_Limite_Janela'] <= 24)
                    
                    df_pendentes_geral = df_validos[condicao_horario & (df_validos['P_COUNT'] > 0)].copy()
                else:
                    if not df_validos.empty:
                        df_pendentes_geral = df_validos[df_validos['P_COUNT'] > 0].copy()

                col_contrato = next((c for c in df_pendentes_geral.columns if 'CONTRATO' in c), None)
                if col_contrato and not df_pendentes_geral.empty:
                    df_pendentes_geral[col_contrato] = df_pendentes_geral[col_contrato].fillna('').astype(str).apply(lambda x: str(x).split('.')[0])
                    df_pendentes_geral = df_pendentes_geral.drop_duplicates(subset=[col_contrato])

                qtd_sp = len(df_pendentes_geral[df_pendentes_geral['SUPERVISOR_CLEAN'].isin(SUPS_SP)]) if not df_pendentes_geral.empty else 0
                qtd_abc = len(df_pendentes_geral[df_pendentes_geral['SUPERVISOR_CLEAN'].isin(SUPS_ABC)]) if not df_pendentes_geral.empty else 0

                c_abc, c_sp = st.columns(2)
                with c_abc:
                    st.markdown(f'''<div class="box-base"><div class="nome-base" style="color: #2e7d32;">ABC PENDENTES</div><div class="num-base">{qtd_abc}</div></div>''', unsafe_allow_html=True)
                    cols_sub_abc = st.columns(len(SUPS_ABC))
                    for k, sup in enumerate(SUPS_ABC):
                        qtd = len(df_pendentes_geral[df_pendentes_geral['SUPERVISOR_CLEAN'] == sup]) if not df_pendentes_geral.empty else 0
                        with cols_sub_abc[k]:
                            st.markdown(f'''<div id="sup-box-{k}" class="box-contagem"><div class="box-nome">{obter_nome_visual(sup)}</div><div class="box-num">{qtd}</div></div>''', unsafe_allow_html=True)

                with c_sp:
                    st.markdown(f'''<div class="box-base-sp"><div class="nome-base" style="color: #00695c;">SÃO PAULO PENDENTES</div><div class="num-base">{qtd_sp}</div></div>''', unsafe_allow_html=True)
                    cols_sub_sp = st.columns(len(SUPS_SP))
                    for k, sup in enumerate(SUPS_SP):
                        idx_global = len(SUPS_ABC) + k 
                        qtd = len(df_pendentes_geral[df_pendentes_geral['SUPERVISOR_CLEAN'] == sup]) if not df_pendentes_geral.empty else 0
                        with cols_sub_sp[k]:
                            st.markdown(f'''<div id="sup-box-{idx_global}" class="box-contagem"><div class="box-nome">{obter_nome_visual(sup)}</div><div class="box-num">{qtd}</div></div>''', unsafe_allow_html=True)

                if st.session_state.novo_ciclo:
                    if permitir_audio_tec1:
                        script_cenario = f"<script>{JS_MOTOR_AUDIO}limparDestaques({len(SUPERVISORES_ORDENADOS)});\n"
                        delay_atual = 0
                        script_cenario += f"anunciarBase('{frase_incisiva_tec1} Contratos pendentes {fala_janela}. A B C: {qtd_abc} pendentes.', {delay_atual});\n"
                        delay_atual += 7000
                        for i, sup_full in enumerate(SUPS_ABC):
                            qtd_p = len(df_pendentes_geral[df_pendentes_geral['SUPERVISOR_CLEAN'] == sup_full]) if not df_pendentes_geral.empty else 0
                            script_cenario += f"animarSupervisor('{obter_nome_visual(sup_full)}: {qtd_p} pendentes.', {delay_atual}, {i}, {len(SUPERVISORES_ORDENADOS)});\n"
                            delay_atual += 7000
                        script_cenario += f"anunciarBase('São Paulo: {qtd_sp} pendentes.', {delay_atual});\n"
                        delay_atual += 7000
                        for i, sup_full in enumerate(SUPS_SP):
                            idx = len(SUPS_ABC) + i
                            qtd_p = len(df_pendentes_geral[df_pendentes_geral['SUPERVISOR_CLEAN'] == sup_full]) if not df_pendentes_geral.empty else 0
                            script_cenario += f"animarSupervisor('{obter_nome_visual(sup_full)}: {qtd_p} pendentes.', {delay_atual}, {idx}, {len(SUPERVISORES_ORDENADOS)});\n"
                            delay_atual += 7000
                        script_cenario += f"setTimeout(() => limparDestaques({len(SUPERVISORES_ORDENADOS)}) , {delay_atual});\n</script>"
                    else:
                        script_cenario = ""
                        
                    st.session_state.script_audio_atual = script_cenario
                    st.session_state.novo_ciclo = False 
                st.components.v1.html(st.session_state.script_audio_atual, height=0)
            else: st.error("Coluna Status não encontrada.")
        else: st.error("Ficheiro rota_sincronizada.csv não encontrado.")
        time.sleep(1)
        st.rerun()

    # -------------------------------------------------------------------------
    # TELA 5: PAINEL DO CONSULTIVO OPERACIONAL 🚀 (BASE INDEPENDENTE DO SUPERVISOR)
    # -------------------------------------------------------------------------
    elif st.session_state.idx == 5:
        st.markdown(f'''<div class="topo-container">
            <div class="topo-esquerda">{logo_html}</div>
            <div class="topo-centro">PERFORMANCE CONSULTIVO</div>
            <div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div>
        </div>''', unsafe_allow_html=True)

        if os.path.exists(ARQUIVO_CONSULTIVO):
            try:
                import unicodedata
                
                df_cons = pd.read_csv(ARQUIVO_CONSULTIVO, sep=None, engine='python', dtype=str)
                df_cons.columns = [unicodedata.normalize('NFKD', str(c)).encode('ASCII', 'ignore').decode('utf-8').strip().upper().replace(' ', '_') for c in df_cons.columns]

                def limpar_texto(txt):
                    if pd.isna(txt): return ''
                    return unicodedata.normalize('NFKD', str(txt).strip().upper()).encode('ASCII', 'ignore').decode('utf-8')

                if 'BASE' in df_cons.columns:
                    df_cons['BASE'] = df_cons['BASE'].apply(limpar_texto)
                else:
                    df_cons['BASE'] = 'N/D'

                col_qtd = next((c for c in df_cons.columns if 'QTD' in c and 'PRODUTO' in c), None)
                if col_qtd:
                    df_cons['QTD_PRODUTOS_CALC'] = pd.to_numeric(df_cons[col_qtd].astype(str).str.replace(',', '.'), errors='coerce').fillna(0).astype(int)
                else:
                    df_cons['QTD_PRODUTOS_CALC'] = 0

                # 🔥 1. SOMA TOTAL DA BASE (EXATO DA PLANILHA, ANTES DE QUALQUER FILTRO) 🔥
                total_realizado_abc = df_cons[df_cons['BASE'] == 'ABC']['QTD_PRODUTOS_CALC'].sum()
                total_realizado_sp  = df_cons[df_cons['BASE'] == 'SP']['QTD_PRODUTOS_CALC'].sum()

                # -------------------------------------------------------------------------
                # Agora tratamos os Supervisores para preencher os Cards Individuais
                # -------------------------------------------------------------------------
                df_cons['SUPERVISOR'] = df_cons['SUPERVISOR'].apply(limpar_texto) if 'SUPERVISOR' in df_cons.columns else ''

                def classificar_supervisor_limpo(row):
                    texto_celula = row.get('SUPERVISOR', '')
                    for oficial in SUPERVISORES_ORDENADOS:
                        primeiro_nome = limpar_texto(oficial.split()[0])
                        if primeiro_nome in texto_celula:
                            return oficial
                    return "DESCARTADO"

                df_cons['SUPERVISOR_CLEAN'] = df_cons.apply(classificar_supervisor_limpo, axis=1)
                
                # Para os cards, ficamos apenas com as linhas que têm supervisor válido
                df_cards = df_cons[df_cons['SUPERVISOR_CLEAN'] != "DESCARTADO"].copy()

                hoje = datetime.utcnow() - timedelta(hours=3)
                ano, mes = hoje.year, hoje.month
                
                _, num_dias = calendar.monthrange(ano, mes)
                dias_uteis_totais = sum(1 for d in range(1, num_dias + 1) if calendar.weekday(ano, mes, d) != 6)
                dias_restantes = sum(1 for d in range(hoje.day, num_dias + 1) if calendar.weekday(ano, mes, d) != 6)
                if dias_restantes == 0: dias_restantes = 1

                meta_mensal_abc = len(SUPS_ABC) * 350
                meta_mensal_sp = len(SUPS_SP) * 350

                ritmo_diario_base_abc = int(meta_mensal_abc / dias_uteis_totais) if dias_uteis_totais > 0 else 0
                ritmo_diario_base_sp = int(meta_mensal_sp / dias_uteis_totais) if dias_uteis_totais > 0 else 0

                col_abc, col_sp = st.columns(2)
                
                with col_abc:
                    st.markdown(f'''<div class="box-base">
                        <div class="nome-base" style="color: #2e7d32;">🏢 BASE ABC TOTAL (Meta: {meta_mensal_abc} | Ritmo: {ritmo_diario_base_abc}/dia)</div>
                        <div class="num-base">{total_realizado_abc}</div>
                    </div>''', unsafe_allow_html=True)
                    
                    for sup in SUPS_ABC:
                        # Puxa do df_cards, que já descartou os "N/D"
                        qtd_sup = df_cards[df_cards['SUPERVISOR_CLEAN'] == sup]['QTD_PRODUTOS_CALC'].sum()
                        
                        meta_individual = 350
                        falta_individual = meta_individual - qtd_sup
                        if falta_individual < 0: falta_individual = 0
                        ritmo_diario_individual = round(falta_individual / dias_restantes, 1)

                        st.markdown(f'''
                        <div class="sup-card">
                            <div class="sup-header">
                                <div class="sup-name">📋 {obter_nome_visual(sup)}</div>
                                <div class="badge-faltas" style="background: #e8f5e9; color: #2e7d32; border-color: #a5d6a7;">Alvo: 350</div>
                            </div>
                            <div class="faltas-grid">
                                <div class="falta-box" style="background-color: #e8f5e9; border-color: #a5d6a7;">
                                    <div class="falta-label" style="color: #2e7d32;">📦 TOTAL PRODUTOS</div>
                                    <div class="falta-value" style="color: #1b5e20;">{qtd_sup}</div>
                                </div>
                                <div class="falta-box">
                                    <div class="falta-label">📉 FALTA PARA META</div>
                                    <div class="falta-value">{falta_individual}</div>
                                </div>
                                <div class="falta-box" style="background-color: #fff8e1; border-color: #ffe082;">
                                    <div class="falta-label" style="color: #b78103;">🎯 META DIÁRIA</div>
                                    <div class="falta-value" style="color: #b78103;">{ritmo_diario_individual}</div>
                                </div>
                            </div>
                        </div>''', unsafe_allow_html=True)

                with col_sp:
                    st.markdown(f'''<div class="box-base-sp">
                        <div class="nome-base" style="color: #00695c;">🏙️ BASE SÃO PAULO TOTAL (Meta: {meta_mensal_sp} | Ritmo: {ritmo_diario_base_sp}/dia)</div>
                        <div class="num-base">{total_realizado_sp}</div>
                    </div>''', unsafe_allow_html=True)
                    
                    for sup in SUPS_SP:
                        # Puxa do df_cards, que já descartou os "N/D"
                        qtd_sup = df_cards[df_cards['SUPERVISOR_CLEAN'] == sup]['QTD_PRODUTOS_CALC'].sum()
                        
                        meta_individual = 350
                        falta_individual = meta_individual - qtd_sup
                        if falta_individual < 0: falta_individual = 0
                        ritmo_diario_individual = round(falta_individual / dias_restantes, 1)

                        st.markdown(f'''
                        <div class="sup-card">
                            <div class="sup-header">
                                <div class="sup-name">📋 {obter_nome_visual(sup)}</div>
                                <div class="badge-faltas" style="background: #e0f2f1; color: #00695c; border-color: #b2dfdb;">Alvo: 350</div>
                            </div>
                            <div class="faltas-grid">
                                <div class="falta-box" style="background-color: #e0f2f1; border-color: #b2dfdb;">
                                    <div class="falta-label" style="color: #00695c;">📦 TOTAL PRODUTOS</div>
                                    <div class="falta-value" style="color: #004d40;">{qtd_sup}</div>
                                </div>
                                <div class="falta-box">
                                    <div class="falta-label">📉 FALTA PARA META</div>
                                    <div class="falta-value">{falta_individual}</div>
                                </div>
                                <div class="falta-box" style="background-color: #fff8e1; border-color: #ffe082;">
                                    <div class="falta-label" style="color: #b78103;">🎯 META DIÁRIA</div>
                                    <div class="falta-value" style="color: #b78103;">{ritmo_diario_individual}</div>
                                </div>
                            </div>
                        </div>''', unsafe_allow_html=True)

                if st.session_state.novo_ciclo:
                    st.session_state.script_audio_atual = ""
                    st.session_state.novo_ciclo = False
                st.components.v1.html(st.session_state.script_audio_atual, height=0)

            except Exception as e:
                st.error(f"Erro ao processar colunas do Consultivo. Detalhes: {e}")
        else: 
            st.warning("Aguardando sincronização da planilha master para carregar o Consultivo...")
        time.sleep(1)
        st.rerun()
    # -------------------------------------------------------------------------
    # TELA 3: PRINT DOS INDICADORES
    # -------------------------------------------------------------------------
    elif st.session_state.idx == 3:
        st.markdown(f'''<div class="topo-container">
            <div class="topo-esquerda">{logo_html}</div>
            <div class="topo-centro">PRINT DOS INDICADORES {html_audio_ind}</div>
            <div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div>
        </div>''', unsafe_allow_html=True)

        if os.path.exists(ARQUIVO_ROTA_DISCO):
            df_ind = pd.read_csv(ARQUIVO_ROTA_DISCO, sep=None, engine='python', dtype=str)
            df_ind.columns = [str(c).strip().upper() for c in df_ind.columns]
            col_status = next((c for c in df_ind.columns if 'STATUS' in c), None)
            col_recurso = 'RECURSO' if 'RECURSO' in df_ind.columns else df_ind.columns[0]
            col_sup = next((c for c in df_ind.columns if 'SUPERVISOR' in c), None)
            
            col_nr35 = next((c for c in reversed(df_ind.columns) if 'NR35' in c or 'NR-35' in c), None)
            col_cert = next((c for c in reversed(df_ind.columns) if 'CERTID' in c or 'ELEGIVEL' in c or 'ELEGÍVEL' in c), None)
            col_bst  = next((c for c in reversed(df_ind.columns) if 'BST' in c or 'STEERING' in c or 'BAND' in c), None)

            if col_status:
                df_ind['Status_Atividade_Upper'] = df_ind[col_status].fillna('').astype(str).str.upper().str.strip()
                df_produtivo = df_ind[df_ind['Status_Atividade_Upper'].str.contains('CONCL|PRODUTIVO|INIC|EXEC', na=False)].copy()
                
                if 'CONTRATO' in df_produtivo.columns and not df_produtivo.empty:
                    df_produtivo['CONTRATO'] = df_produtivo['CONTRATO'].fillna('').astype(str).apply(lambda x: x.split('.')[0] if '.' in x else x).str.strip()
                    df_produtivo = df_produtivo[df_produtivo['CONTRATO'] != ''].drop_duplicates(subset=['CONTRATO'])

                df_produtivo['FALTA_NR35'] = 0
                if col_nr35: df_produtivo['FALTA_NR35'] = df_produtivo[col_nr35].fillna('').astype(str).str.upper().str.contains('NÃO|NAO|FALTA', na=False).astype(int)
                df_produtivo['FALTA_CERT'] = 0
                if col_cert: df_produtivo['FALTA_CERT'] = df_produtivo[col_cert].fillna('').astype(str).str.upper().str.contains('NÃO|NAO|FALTA', na=False).astype(int)
                df_produtivo['FALTA_BST'] = 0
                if col_bst: df_produtivo['FALTA_BST'] = df_produtivo[col_bst].fillna('').astype(str).str.upper().str.contains('NÃO|NAO|FALTA', na=False).astype(int)

                mapa_tecnico_sup = {}
                if col_sup and col_recurso:
                    for _, row in df_ind.dropna(subset=[col_recurso, col_sup]).iterrows():
                        tec = str(row[col_recurso]).upper().strip()
                        sup = str(row[col_sup]).upper().strip()
                        for oficial in SUPERVISORES_ORDENADOS:
                            if oficial in sup:
                                mapa_tecnico_sup[tec] = oficial
                                break

                def resolver_supervisor(row):
                    tec = str(row.get(col_recurso, '')).upper().strip()
                    sup = str(row.get(col_sup, '')).upper().strip() if col_sup else ''
                    for oficial in SUPERVISORES_ORDENADOS:
                        if oficial in sup: return oficial
                    return mapa_tecnico_sup.get(tec, "NÃO IDENTIFICADO")

                df_produtivo['SUPERVISOR_CLEAN'] = df_produtivo.apply(resolver_supervisor, axis=1)

                c_abc, c_sp = st.columns(2)
                with c_abc:
                    st.markdown('<div class="ind-base-title abc">ABC</div>', unsafe_allow_html=True)
                    for sup in SUPS_ABC:
                        df_sup = df_produtivo[df_produtivo['SUPERVISOR_CLEAN'] == sup]
                        f_35, f_ce, f_bs = int(df_sup['FALTA_NR35'].sum()), int(df_sup['FALTA_CERT'].sum()), int(df_sup['FALTA_BST'].sum())
                        st.markdown(f'''<div class="sup-card"><div class="sup-header"><div class="sup-name">📋 {obter_nome_visual(sup)}</div><div class="badge-faltas">Total Faltas: {f_35+f_ce+f_bs}</div></div>
                            <div class="faltas-grid"><div class="falta-box"><div class="falta-label">🪜 FALTAM NR35</div><div class="falta-value">{f_35}</div></div>
                            <div class="falta-box"><div class="falta-label">📜 FALTA CERTIDÃO</div><div class="falta-value">{f_ce}</div></div>
                            <div class="falta-box"><div class="falta-label">📶 FALTA BST</div><div class="falta-value">{f_bs}</div></div></div></div>''', unsafe_allow_html=True)

                with c_sp:
                    st.markdown('<div class="ind-base-title sp">SÃO PAULO</div>', unsafe_allow_html=True)
                    for sup in SUPS_SP:
                        df_sup = df_produtivo[df_produtivo['SUPERVISOR_CLEAN'] == sup]
                        f_35, f_ce, f_bs = int(df_sup['FALTA_NR35'].sum()), int(df_sup['FALTA_CERT'].sum()), int(df_sup['FALTA_BST'].sum())
                        st.markdown(f'''<div class="sup-card"><div class="sup-header"><div class="sup-name">📋 {obter_nome_visual(sup)}</div><div class="badge-faltas">Total Faltas: {f_35+f_ce+f_bs}</div></div>
                            <div class="faltas-grid"><div class="falta-box"><div class="falta-label">🪜 FALTAM NR35</div><div class="falta-value">{f_35}</div></div>
                            <div class="falta-box"><div class="falta-label">📜 FALTA CERTIDÃO</div><div class="falta-value">{f_ce}</div></div>
                            <div class="falta-box"><div class="falta-label">📶 FALTA BST</div><div class="falta-value">{f_bs}</div></div></div></div>''', unsafe_allow_html=True)

                if st.session_state.novo_ciclo:
                    if permitir_audio_ind:
                        st.session_state.script_audio_atual = f"<script>{JS_MOTOR_AUDIO}anunciarBase('Monitores, enviem os prints pendentes do N R 35, Band Steering e certidão de atendimento.', 0);</script>"
                    else:
                        st.session_state.script_audio_atual = ""
                    st.session_state.novo_ciclo = False
                st.components.v1.html(st.session_state.script_audio_atual, height=0)
            else: st.error("Coluna Status não encontrada.")
        else: st.error("Ficheiro rota_sincronizada.csv não encontrado.")
        time.sleep(1)
        st.rerun()

    # -------------------------------------------------------------------------
    # TELA 2: HORÁRIO ⏱️ (CENTRALIZAÇÃO COMPLETA RESTAURADA)
    # -------------------------------------------------------------------------
    elif st.session_state.idx == 2:
        st.markdown(f'''<div class="topo-container">
            <div class="topo-esquerda">{logo_html}</div>
            <div class="topo-centro">HORÁRIO</div>
            <div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div>
        </div>''', unsafe_allow_html=True)

        tempo_real = datetime.utcnow() - timedelta(hours=3)
        st.markdown(f'<div class="relogio-container"><div class="hora-gigante">{tempo_real.strftime("%H:%M:%S")}</div><div class="data-media">{tempo_real.strftime("%d/%m/%Y")}</div></div>', unsafe_allow_html=True)
        
        if st.session_state.novo_ciclo:
            st.session_state.script_audio_atual = f"<script>{JS_MOTOR_AUDIO}anunciarBase('Hora certa: {tempo_real.strftime('%H e %M')}.', 0);</script>"
            st.session_state.novo_ciclo = False
        st.components.v1.html(st.session_state.script_audio_atual, height=0)
        time.sleep(1)
        st.rerun()

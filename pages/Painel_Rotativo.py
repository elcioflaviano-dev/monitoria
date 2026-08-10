import streamlit as st
import pandas as pd
import numpy as np
import os
import time
import base64
import calendar
import unicodedata
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

# --- FUNÇÕES GLOBAIS E CSS ---
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
    /* Ajuste do container principal para caber tudo na tela da TV e dar espaço pro ticker */
    .block-container { padding-top: 1rem !important; padding-bottom: 70px !important; max-width: 98% !important; }

    /* ESCONDE A BARRA DE ROLAGEM MAS MANTÉM A TELA INTEIRA INTACTA */
    ::-webkit-scrollbar { display: none !important; }
    html, body { -ms-overflow-style: none !important; scrollbar-width: none !important; overflow: hidden !important; }

    /* ESTILOS DE INTERFACE */
    .viewerBadge_container, .viewerBadge_link, [data-testid="viewerBadge"], #viewerBadge { display: none !important; }
    [data-testid="stHeader"], .stDeployButton, footer, #MainMenu, [data-testid="stSidebar"] { display: none !important; visibility: hidden !important; }
    .stApp { background-color: #ffffff !important; }
    .topo-container { background: #003366; color: white; padding: 0px 30px; border-radius: 0 0 15px 15px; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; margin-bottom: 10px; height: 80px; }
    .topo-esquerda { display: flex; justify-content: flex-start; align-items: center; height: 100%; }
    .topo-centro { font-size: 40px; font-weight: 900; text-align: center; white-space: nowrap; }
    .topo-direita { display: flex; justify-content: flex-end; align-items: center; }
    .botao-home { color: #fff; font-size: 18px; font-weight: bold; border: 2px solid #fff; padding: 8px 15px; border-radius: 5px; text-decoration: none; }
    
    /* BOTÃO PRÓXIMA "FANTASMA" NO CANTO DIREITO INFERIOR */
    div[data-testid="stButton"] {
        position: fixed !important;
        bottom: 75px !important; /* Acima do ticker financeiro */
        right: 20px !important;
        z-index: 999999 !important;
        display: flex !important;
        justify-content: flex-end !important;
        width: auto !important;
    }
    div[data-testid="stButton"] > button {
        background-color: #003366 !important;
        color: #ffffff !important;
        border: 2px solid #ffffff !important;
        border-radius: 30px !important;
        padding: 8px 20px !important;
        font-size: 18px !important;
        font-weight: bold !important;
        opacity: 0.03 !important; /* Quase 100% transparente para ficar despercebido */
        transition: all 0.4s ease-in-out !important;
        box-shadow: none !important;
    }
    div[data-testid="stButton"] > button:hover {
        opacity: 1.0 !important; /* Mostra totalmente ao passar o mouse */
        background-color: #ff9800 !important; /* Fica laranja para mostrar que está ativo */
        border-color: #ffffff !important;
        box-shadow: 0px 5px 15px rgba(0,0,0,0.5) !important;
        transform: scale(1.05) !important;
    }

    /* CAIXA BASE GERAL - COMPACTADA */
    .box-base { background: #e8f5e9; border-left: 15px solid #2e7d32; padding: 10px 10px; text-align: center; border-radius: 12px; box-shadow: 2px 2px 10px rgba(0,0,0,0.15); margin-bottom: 15px; }
    .nome-base { font-size: 35px !important; font-weight: 900; color: #2e7d32; text-transform: uppercase; margin-bottom: 5px; }
    .num-base { font-size: 110px !important; font-weight: 900; color: #111; line-height: 1; }
    
    /* CAIXA DOS SUPERVISORES */
    .box-contagem { background: #f0f2f6; border-left: 12px solid #cc6600; padding: 15px; text-align: center; border-radius: 12px; box-shadow: 2px 2px 8px rgba(0,0,0,0.1); margin-bottom: 15px; position: relative; z-index: 1; transition: 0.3s; }
    .box-nome { font-size: 35px !important; font-weight: 900; color: #003366; text-transform: uppercase; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .box-num { font-size: 90px !important; font-weight: 900; color: #cc6600; line-height: 1; margin-top: 10px; }
    .destaque-ativo { transform: scale(1.05) !important; box-shadow: 0px 20px 40px rgba(204, 102, 0, 0.5) !important; border-left: 18px solid #ff8800 !important; background: #fff8e1 !important; z-index: 9999 !important; }
    
    /* CAIXAS CARDS SUPERVISORES - COMPACTADA */
    .ind-base-title { font-size: 50px !important; font-weight: 900; text-align: center; margin-bottom: 15px; margin-top: 5px; text-transform: uppercase; color: #2e7d32; }
    .sup-card { background: #ffffff; border: 2px solid #e0e0e0; border-radius: 12px; padding: 15px; margin-bottom: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.08); }
    .sup-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-bottom: 15px; }
    .sup-name { font-size: 35px !important; font-weight: 900; color: #333; text-transform: uppercase; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}
    .badge-faltas { background: #ffebee; color: #c62828; padding: 8px 20px; border-radius: 10px; font-size: 26px !important; font-weight: 900; border: 3px solid #ffcdd2; }
    .faltas-grid { display: flex; justify-content: space-between; gap: 10px; }
    .falta-box { background-color: #ffebee; border: 2px solid #ffcdd2; border-radius: 10px; padding: 10px 5px; text-align: center; margin-bottom: 5px; flex: 1; }
    .falta-label { font-size: 18px !important; font-weight: bold; color: #c62828; text-transform: uppercase; margin-bottom: 5px; }
    .falta-value { font-size: 65px !important; font-weight: 900; color: #b30000; line-height: 1; }
    
    /* HORA E RELÓGIO */
    .relogio-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 70vh; background-color: #ffffff; width: 100%; }
    .hora-gigante { font-size: 220px; font-weight: 900; color: #003366; text-shadow: 4px 4px 10px rgba(0,0,0,0.1); line-height: 1; letter-spacing: 5px; }
    .data-media { font-size: 50px; color: #666; font-weight: bold; margin-top: -20px; }
    .tec-base-nome { background: #f8f9fa; padding: 15px 20px; border-left: 8px solid #008080; border-radius: 6px; margin-bottom: 12px; font-weight: bold; font-size: 28px !important; color: #333; box-shadow: 1px 1px 5px rgba(0,0,0,0.1); }

    /* TICKER FINANCEIRO (RODAPÉ) */
    .ticker-wrap {
        position: fixed; bottom: 0; left: 0; width: 100%; overflow: hidden; height: 55px; background-color: #002244; box-sizing: border-box; z-index: 99999; border-top: 3px solid #ff8800; display: flex; align-items: center; box-shadow: 0px -5px 15px rgba(0,0,0,0.3);
    }
    .ticker { display: inline-block; white-space: nowrap; padding-right: 100%; box-sizing: content-box; animation: ticker 45s linear infinite; }
    .ticker__item { display: inline-block; padding: 0 15px; font-size: 22px; color: #ffffff; font-weight: 900; text-transform: uppercase; letter-spacing: 1px; }
    @keyframes ticker { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
</style>""", unsafe_allow_html=True)

# --- REGRAS GLOBAIS ---
SUPS_ABC = ["EDSON MARCO", "MAICON", "NELSON"]
SUPERVISORES_ORDENADOS = SUPS_ABC

def obter_nome_visual(nome_completo):
    n = str(nome_completo).upper()
    if 'MAICON' in n: return "MAICON"
    if 'NELSON' in n: return "NELSON"
    if 'EDSON MARCO' in n: return "EDSON MARCO"
    return n.split()[0]

def limpar_texto(txt):
    if pd.isna(txt): return ''
    return unicodedata.normalize('NFKD', str(txt).strip().upper()).encode('ASCII', 'ignore').decode('utf-8')

def padronizar_status(val):
    val_clean = limpar_texto(str(val))
    
    if 'NE' in val_clean or 'NAO CONCLUIDO' in val_clean or 'QUEBRA' in val_clean or 'CANCEL' in val_clean or 'O.S NE' in val_clean: 
        return 'O.S NE'
        
    if 'PRODUTIVO' in val_clean or 'CONCL' in val_clean or 'EXEC' in val_clean: 
        return 'Produtivo'
        
    return 'Em aberto'

# Inicialização do estado da sessão
if "idx" not in st.session_state: 
    st.session_state.idx = 0          
    st.session_state.novo_ciclo = True
    st.session_state.script_audio_atual = ""
    st.session_state.prox_idx = 0

# Cofre do Ticker Financeiro
if "ticker_data" not in st.session_state:
    st.session_state.ticker_data = {}

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
    {"inicio": 11*60 + 50, "fim": 11*60 + 59, "frase": "Atenção. Término de janela. É necessário baixar os contratos."},
    {"inicio": 14*60 + 50, "fim": 14*60 + 59, "frase": "Atenção. Término de janela. É necessário baixar os contratos."},
    {"inicio": 17*60 + 50, "fim": 17*60 + 59, "frase": "Atenção. Término de janela. É necessário baixar os contratos."}
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

icone_mudo = '''<div style="position: fixed; bottom: 75px; left: 20px; z-index: 9999; opacity: 0.25;" title="Áudio em Espera">
    <svg width="35" height="35" viewBox="0 0 24 24" fill="none" stroke="#666666" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
        <line x1="23" y1="1" x2="1" y2="23"></line>
    </svg>
</div>'''

icone_ativo = '''<div style="position: fixed; bottom: 75px; left: 20px; z-index: 9999; opacity: 0.8;" title="Áudio Ativo">
    <svg width="35" height="35" viewBox="0 0 24 24" fill="none" stroke="#2e7d32" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
        <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
    </svg>
</div>'''

html_audio_base = icone_ativo if permitir_audio_base else icone_mudo
html_audio_tec1 = icone_ativo if permitir_audio_tec1 else icone_mudo
html_audio_ind = icone_ativo if permitir_audio_ind else icone_mudo

JS_MOTOR_AUDIO = """
function tocarAlertaChamaAtencao() {
    try {
        let ctx = new (window.parent.AudioContext || window.AudioContext)();
        let tempo = ctx.currentTime;
        
        function tocarSino(frequencia, inicio, duracao) {
            let osc = ctx.createOscillator();
            let gain = ctx.createGain();
            
            osc.type = 'triangle';
            osc.frequency.setValueAtTime(frequencia, inicio);
            
            gain.gain.setValueAtTime(0, inicio);
            gain.gain.linearRampToValueAtTime(3.0, inicio + 0.05); 
            gain.gain.exponentialRampToValueAtTime(0.01, inicio + duracao);
            
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start(inicio);
            osc.stop(inicio + duracao + 0.1);
        }

        tocarSino(659.25, tempo, 1.5);       
        tocarSino(523.25, tempo + 0.4, 1.5); 
        tocarSino(784.00, tempo + 0.8, 2.5); 
    } catch(e) {}
}

function anunciarBase(texto, delay) {
    setTimeout(() => {
        tocarAlertaChamaAtencao();
        setTimeout(() => {
            let synth = window.parent.speechSynthesis || window.speechSynthesis;
            try { synth.cancel(); } catch(e) {} 
            let m = new SpeechSynthesisUtterance(texto);
            m.lang = 'pt-BR'; m.rate = 1.0; m.volume = 1.0; 
            function setVoiceAndSpeak() {
                let voices = synth.getVoices();
                let voz = voices.find(v => v.name.includes('Luciana')) || voices.find(v => v.name.includes('Maria')) || voices.find(v => v.name.includes('Francisca')) || voices.find(v => v.lang.includes('pt-BR'));
                if(voz) { m.voice = voz; } 
                synth.speak(m);
            }
            if (synth.getVoices().length === 0) { synth.onvoiceschanged = setVoiceAndSpeak; } 
            else { setVoiceAndSpeak(); }
        }, 2000); 
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
            try { synth.cancel(); } catch(e) {}
            let m = new SpeechSynthesisUtterance(texto);
            m.lang = 'pt-BR'; m.rate = 1.0; m.volume = 1.0; 
            let voices = synth.getVoices();
            let voz = voices.find(v => v.name.includes('Luciana')) || voices.find(v => v.name.includes('Maria')) || voices.find(v => v.name.includes('Francisca')) || voices.find(v => v.lang.includes('pt-BR'));
            if(voz) { m.voice = voz; }
            synth.speak(m);
        }, 2000); 
    }, delay);
}
"""

CONTEUDO_TV = st.empty()

with CONTEUDO_TV.container():

    # -------------------------------------------------------------------------
    # TELA 4: TRANSIÇÃO
    # -------------------------------------------------------------------------
    if st.session_state.idx == 4:
        st.markdown(
            """
            <div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: #ffffff; z-index: 999999; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                <h1 style="color: #003366; font-size: 50px;">🔄 Atualizando Indicadores...</h1>
            </div>
            """, unsafe_allow_html=True
        )

    # -------------------------------------------------------------------------
    # TELA 0: BASE
    # -------------------------------------------------------------------------
    elif st.session_state.idx == 0:
        st.markdown(f'''<div class="topo-container">
            <div class="topo-esquerda">{logo_html}</div>
            <div class="topo-centro">🚀 TÉCNICOS COM STATUS BASE PENDENTE</div>
            <div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div>
        </div>
        {html_audio_base}''', unsafe_allow_html=True)

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
                
                nomes_abc = sorted([str(n).strip().upper() for n in df_tela[col_recurso].dropna().unique()])
                qtd_abc_base = len(nomes_abc)

                st.session_state.ticker_data[0] = f"🚀 BASE: {qtd_abc_base} TÉCS PENDENTES"

                cols_tec = st.columns(4)
                for i, n in enumerate(nomes_abc):
                    with cols_tec[i % 4]:
                        st.markdown(f'<div class="tec-base-nome">🏃‍♂️ {n}</div>', unsafe_allow_html=True)

                if st.session_state.novo_ciclo:
                    if permitir_audio_base:
                        script_cenario = f"<script>{JS_MOTOR_AUDIO}anunciarBase('{frase_incisiva_base} Existem {len(nomes_abc)} técnicos pendentes', 0);</script>"
                    else: script_cenario = ""
                    st.session_state.script_audio_atual = script_cenario
                    st.session_state.novo_ciclo = False 
                st.components.v1.html(st.session_state.script_audio_atual, height=0)
            else: st.error("Coluna Status não encontrada.")
        else: st.error("Ficheiro rota_sincronizada.csv não encontrado.")

    # -------------------------------------------------------------------------
    # TELA 1: TEC1
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
            if hora_atual < 12: label_janela = "ATÉ 12:00"
            elif 12 <= hora_atual < 15: label_janela = "ATÉ 15:00"
            else: label_janela = "ATÉ 18:00"
            
            st.markdown(f'''<div class="topo-container">
                <div class="topo-esquerda">{logo_html}</div>
                <div class="topo-centro">TEC1 <span style="font-size: 32px; vertical-align: middle; background: #ff9800; color: #fff; padding: 6px 18px; border-radius: 30px; margin-left: 15px;">{label_janela}</span></div>
                <div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div>
            </div>
            {html_audio_tec1}''', unsafe_allow_html=True)
            
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

                qtd_abc = len(df_pendentes_geral[df_pendentes_geral['SUPERVISOR_CLEAN'].isin(SUPS_ABC)]) if not df_pendentes_geral.empty else 0

                st.session_state.ticker_data[1] = f"⏰ TEC1: {qtd_abc} PENDENTES"

                st.markdown(f'''<div class="box-base"><div class="nome-base">PENDENTES</div><div class="num-base">{qtd_abc}</div></div>''', unsafe_allow_html=True)
                
                for i in range(0, len(SUPS_ABC), 2):
                    cols_sub_abc = st.columns(2)
                    for j in range(2):
                        if i + j < len(SUPS_ABC):
                            idx_global = i + j
                            sup = SUPS_ABC[idx_global]
                            qtd = len(df_pendentes_geral[df_pendentes_geral['SUPERVISOR_CLEAN'] == sup]) if not df_pendentes_geral.empty else 0
                            with cols_sub_abc[j]:
                                st.markdown(f'''<div id="sup-box-{idx_global}" class="box-contagem"><div class="box-nome">{obter_nome_visual(sup)}</div><div class="box-num">{qtd}</div></div>''', unsafe_allow_html=True)

                if st.session_state.novo_ciclo:
                    if permitir_audio_tec1:
                        script_cenario = f"<script>{JS_MOTOR_AUDIO}limparDestaques({len(SUPERVISORES_ORDENADOS)});\n"
                        delay_atual = 0
                        script_cenario += f"anunciarBase('{frase_incisiva_tec1} Base: {qtd_abc} pendentes.', {delay_atual});\n"
                        delay_atual += 8500 
                        for i, sup_full in enumerate(SUPS_ABC):
                            qtd_p = len(df_pendentes_geral[df_pendentes_geral['SUPERVISOR_CLEAN'] == sup_full]) if not df_pendentes_geral.empty else 0
                            script_cenario += f"animarSupervisor('{obter_nome_visual(sup_full)}: {qtd_p} pendentes.', {delay_atual}, {i}, {len(SUPERVISORES_ORDENADOS)});\n"
                            delay_atual += 8500 
                        script_cenario += f"setTimeout(() => limparDestaques({len(SUPERVISORES_ORDENADOS)}) , {delay_atual});\n</script>"
                    else: script_cenario = ""
                    st.session_state.script_audio_atual = script_cenario
                    st.session_state.novo_ciclo = False 
                st.components.v1.html(st.session_state.script_audio_atual, height=0)
            else: st.error("Coluna Status não encontrada.")
        else: st.error("Ficheiro rota_sincronizada.csv não encontrado.")

    # -------------------------------------------------------------------------
    # TELA 7: MIGRAÇÃO GPON
    # -------------------------------------------------------------------------
    elif st.session_state.idx == 7:
        st.markdown(f'''<div class="topo-container">
            <div class="topo-esquerda">{logo_html}</div>
            <div class="topo-centro">MIGRAÇÃO GPON</div>
            <div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div>
        </div>
        {icone_mudo}''', unsafe_allow_html=True)

        if os.path.exists(ARQUIVO_ROTA_DISCO):
            df = pd.read_csv(ARQUIVO_ROTA_DISCO, sep=None, engine='python', dtype=str)
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            col_sup = next((c for c in df.columns if 'SUPERVISOR' in c), None)
            
            col_gpon = next((c for c in df.columns if 'GPON' in c), None)
            cols_os = [c for c in df.columns if 'TIPO O.S' in c or 'TIPO OS' in c or 'ATIVIDADE' in c]
            
            col_status = next((c for c in df.columns if 'STATUS CONTRATO' in c or 'STATUS_TV' in c), None)
            if not col_status: col_status = next((c for c in df.columns if 'STATUS' in c), None)
            
            def class_sup(row):
                sup = str(row.get(col_sup, '')).upper().strip() if col_sup else ''
                for oficial in SUPERVISORES_ORDENADOS:
                    if oficial in sup: return oficial
                return "DESCARTADO"
            
            df['SUPERVISOR_CLEAN'] = df.apply(class_sup, axis=1)
            df_abc = df[df['SUPERVISOR_CLEAN'] != "DESCARTADO"].copy()
            
            if col_gpon and len(cols_os) > 0 and col_status:
                cond_gpon = df_abc[col_gpon].astype(str).str.strip().str.upper() == 'SIM'
                df_gpon = df_abc[cond_gpon].copy()
                
                if df_gpon.empty:
                    st.warning("Nenhum contrato marcado como SIM na coluna GPON encontrado para os supervisores atuais.")
                else:
                    df_gpon['TODAS_OS_JUNTAS'] = df_gpon[cols_os].fillna('').astype(str).agg('  '.join, axis=1).str.upper()
                    
                    count_24 = df_gpon['TODAS_OS_JUNTAS'].str.count('24 -')
                    count_191 = df_gpon['TODAS_OS_JUNTAS'].str.count('191 -')
                    df_gpon['QTD_MIGRACAO_CALC'] = count_24 + count_191
                    
                    df_mig = df_gpon[df_gpon['QTD_MIGRACAO_CALC'] > 0].copy()
                    
                    if df_mig.empty:
                        st.warning("Nenhuma O.S do tipo '24 -' ou '191 -' encontrada na base GPON.")
                    else:
                        df_mig['STATUS_PADRAO'] = df_mig[col_status].apply(padronizar_status)
                        df_mig['QTD_TAREFAS_NUM'] = df_mig['QTD_MIGRACAO_CALC']
                        
                        total_geral_mig = int(df_mig['QTD_TAREFAS_NUM'].sum())
                        total_ne_mig = int(df_mig.loc[df_mig['STATUS_PADRAO'] == 'O.S NE', 'QTD_TAREFAS_NUM'].sum())
                        total_prod_mig = int(df_mig.loc[df_mig['STATUS_PADRAO'] == 'Produtivo', 'QTD_TAREFAS_NUM'].sum())
                        
                        soma_valida_mig = total_ne_mig + total_prod_mig
                        quebra_global_mig = (total_ne_mig / soma_valida_mig) * 100 if soma_valida_mig > 0 else 0
                        
                        teto_ne_global = int(np.floor(total_geral_mig * 0.25))
                        cor_limite = "#2e7d32" if total_ne_mig <= teto_ne_global else "#c62828"
                        cor_quebra_global = "#2e7d32" if quebra_global_mig <= 25 else "#c62828"

                        st.session_state.ticker_data[7] = f"📊 GPON: {total_geral_mig} OS | QUEBRAS: {quebra_global_mig:.1f}%"

                        st.markdown(f'''<div class="box-base" style="padding: 10px; margin-bottom: 25px;">
                            <div style="font-size: 35px; font-weight: bold; color: #111;">
                                Total OS: <span style="color:#003366">{total_geral_mig}</span> | 
                                Quebras Geral: <span style="color:{cor_quebra_global}">{quebra_global_mig:.1f}%</span> | 
                                Quebras Permitido: <span style="color:#2e7d32">{teto_ne_global}</span> | 
                                Quebras Atuais: <span style="color:{cor_limite}">{total_ne_mig}</span>
                            </div>
                        </div>''', unsafe_allow_html=True)
                        
                        for i in range(0, len(SUPS_ABC), 2):
                            cols_sup = st.columns(2)
                            for j in range(2):
                                if i + j < len(SUPS_ABC):
                                    sup = SUPS_ABC[i + j]
                                    with cols_sup[j]:
                                        df_sup = df_mig[df_mig['SUPERVISOR_CLEAN'] == sup]
                                        
                                        qtd_aberto = int(df_sup.loc[df_sup['STATUS_PADRAO'] == 'Em aberto', 'QTD_TAREFAS_NUM'].sum())
                                        qtd_produtivo = int(df_sup.loc[df_sup['STATUS_PADRAO'] == 'Produtivo', 'QTD_TAREFAS_NUM'].sum())
                                        qtd_ne = int(df_sup.loc[df_sup['STATUS_PADRAO'] == 'O.S NE', 'QTD_TAREFAS_NUM'].sum())
                                        
                                        soma_base = qtd_ne + qtd_produtivo
                                        quebra = (qtd_ne / soma_base) * 100 if soma_base > 0 else 0
                                        cor_quebra = "#2e7d32" if quebra <= 25 else "#c62828"
                                        
                                        st.markdown(f'''
                                        <div class="sup-card">
                                            <div class="sup-header" style="margin-bottom: 5px;">
                                                <div class="sup-name">📋 {obter_nome_visual(sup)}</div>
                                                <div style="background: #f3f3f3; color: {cor_quebra}; border: 3px solid {cor_quebra}; padding: 10px 20px; border-radius: 8px; font-size: 26px; font-weight: 900; white-space: nowrap;">Quebra: {quebra:.1f}%</div>
                                            </div>
                                            <div class="faltas-grid">
                                                <div class="falta-box" style="background-color: #fff8e1; border-color: #ffe082;">
                                                    <div class="falta-label" style="color: #b78103;">⏳ ABERTO</div>
                                                    <div class="falta-value" style="color: #b78103;">{qtd_aberto}</div>
                                                </div>
                                                <div class="falta-box" style="background-color: #e8f5e9; border-color: #a5d6a7;">
                                                    <div class="falta-label" style="color: #2e7d32;">✅ PRODUTIVO</div>
                                                    <div class="falta-value" style="color: #1b5e20;">{qtd_produtivo}</div>
                                                </div>
                                                <div class="falta-box" style="background-color: #ffebee; border-color: #ffcdd2;">
                                                    <div class="falta-label" style="color: #c62828;">❌ QUEBRAS</div>
                                                    <div class="falta-value" style="color: #b30000;">{qtd_ne}</div>
                                                </div>
                                            </div>
                                        </div>''', unsafe_allow_html=True)
                                        
                        if st.session_state.novo_ciclo:
                            texto_audio = f"Atenção para a Migração G PON. A quebra geral está em {quebra_global_mig:.1f} por cento. O limite é de 25 por cento. Podemos ter até {teto_ne_global} OS quebrados, e no momento temos {total_ne_mig}."
                            st.session_state.script_audio_atual = f"<script>{JS_MOTOR_AUDIO}anunciarBase('{texto_audio}', 0);</script>"

            else: st.error("Colunas necessárias (GPON, TIPO OS, Status) não encontradas no arquivo.")
        else: st.error("Ficheiro rota_sincronizada.csv não encontrado.")
            
        if st.session_state.novo_ciclo: st.session_state.novo_ciclo = False
        st.components.v1.html(st.session_state.script_audio_atual, height=0)

    # -------------------------------------------------------------------------
    # TELA 8: PME 
    # -------------------------------------------------------------------------
    elif st.session_state.idx == 8:
        st.markdown(f'''<div class="topo-container">
            <div class="topo-esquerda">{logo_html}</div>
            <div class="topo-centro">PME</div>
            <div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div>
        </div>
        {icone_mudo}''', unsafe_allow_html=True)

        if os.path.exists(ARQUIVO_ROTA_DISCO):
            df = pd.read_csv(ARQUIVO_ROTA_DISCO, sep=None, engine='python', dtype=str)
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            col_sup = next((c for c in df.columns if 'SUPERVISOR' in c), None)
            col_cat = next((c for c in df.columns if 'CATEGORIAS DA CAPACIDADE' in c or 'CAPACIDADE' in c), None)
            col_os = next((c for c in df.columns if 'TIPO O.S 1' in c or 'TIPO O.S' in c or 'TIPO OS' in c), None)
            
            col_tarefas = None
            for c in df.columns:
                c_clean = unicodedata.normalize('NFKD', str(c)).encode('ASCII', 'ignore').decode('utf-8').upper().strip()
                if 'TAREFA' in c_clean or 'QTD' in c_clean:
                    if 'GERAL' not in c_clean and 'TECNICO' not in c_clean:
                        col_tarefas = c
                        break
            
            col_status = next((c for c in df.columns if 'STATUS CONTRATO' in c or 'STATUS_TV' in c), None)
            if not col_status: col_status = next((c for c in df.columns if 'STATUS' in c), None)
            
            def class_sup(row):
                sup = str(row.get(col_sup, '')).upper().strip() if col_sup else ''
                for oficial in SUPERVISORES_ORDENADOS:
                    if oficial in sup: return oficial
                return "DESCARTADO"
            
            df['SUPERVISOR_CLEAN'] = df.apply(class_sup, axis=1)
            df_abc = df[df['SUPERVISOR_CLEAN'] != "DESCARTADO"].copy()
            
            if col_cat and col_os and col_status:
                cond_cat = df_abc[col_cat].astype(str).str.upper().str.contains('PME', na=False)
                str_os = df_abc[col_os].astype(str).str.upper()
                cond_os = str_os.str.contains('1 - ADES', na=False) | str_os.str.contains('51 - ADES', na=False) | str_os.str.contains('516 - ADES', na=False)
                          
                df_pme = df_abc[cond_cat & cond_os].copy()
                
                if df_pme.empty:
                    st.warning("Nenhum contrato PME encontrado para os filtros atuais.")
                else:
                    df_pme['STATUS_PADRAO'] = df_pme[col_status].apply(padronizar_status)
                    
                    if col_tarefas:
                        df_pme['QTD_TAREFAS_NUM'] = pd.to_numeric(df_pme[col_tarefas].astype(str).str.replace(',', '.').str.strip(), errors='coerce').fillna(0)
                        if df_pme['QTD_TAREFAS_NUM'].sum() == 0 and len(df_pme) > 0: df_pme['QTD_TAREFAS_NUM'] = 1
                    else: df_pme['QTD_TAREFAS_NUM'] = 1
                    
                    total_geral_pme = int(df_pme['QTD_TAREFAS_NUM'].sum())
                    total_ne_pme = int(df_pme.loc[df_pme['STATUS_PADRAO'] == 'O.S NE', 'QTD_TAREFAS_NUM'].sum())
                    total_prod_pme = int(df_pme.loc[df_pme['STATUS_PADRAO'] == 'Produtivo', 'QTD_TAREFAS_NUM'].sum())
                    
                    soma_valida_pme = total_ne_pme + total_prod_pme
                    quebra_global_pme = (total_ne_pme / soma_valida_pme) * 100 if soma_valida_pme > 0 else 0
                    
                    teto_ne_global = int(np.floor(total_geral_pme * 0.20))
                    cor_limite = "#2e7d32" if total_ne_pme <= teto_ne_global else "#c62828"
                    cor_quebra_global = "#2e7d32" if quebra_global_pme <= 20 else "#c62828"

                    st.session_state.ticker_data[8] = f"📊 PME: {total_geral_pme} OS | QUEBRAS: {quebra_global_pme:.1f}%"

                    st.markdown(f'''<div class="box-base" style="padding: 10px; margin-bottom: 25px;">
                        <div style="font-size: 35px; font-weight: bold; color: #111;">
                            Total OS: <span style="color:#003366">{total_geral_pme}</span> | 
                            Quebra Geral: <span style="color:{cor_quebra_global}">{quebra_global_pme:.1f}%</span> | 
                            Quebras Permitido: <span style="color:#2e7d32">{teto_ne_global}</span> | 
                            Quebras Atuais: <span style="color:{cor_limite}">{total_ne_pme}</span>
                        </div>
                    </div>''', unsafe_allow_html=True)
                    
                    for i in range(0, len(SUPS_ABC), 2):
                        cols_sup = st.columns(2)
                        for j in range(2):
                            if i + j < len(SUPS_ABC):
                                sup = SUPS_ABC[i + j]
                                with cols_sup[j]:
                                    df_sup = df_pme[df_pme['SUPERVISOR_CLEAN'] == sup]
                                    
                                    qtd_aberto = int(df_sup.loc[df_sup['STATUS_PADRAO'] == 'Em aberto', 'QTD_TAREFAS_NUM'].sum())
                                    qtd_produtivo = int(df_sup.loc[df_sup['STATUS_PADRAO'] == 'Produtivo', 'QTD_TAREFAS_NUM'].sum())
                                    qtd_ne = int(df_sup.loc[df_sup['STATUS_PADRAO'] == 'O.S NE', 'QTD_TAREFAS_NUM'].sum())
                                    
                                    soma_base = qtd_ne + qtd_produtivo
                                    quebra = (qtd_ne / soma_base) * 100 if soma_base > 0 else 0
                                    cor_quebra = "#2e7d32" if quebra <= 20 else "#c62828"
                                    
                                    st.markdown(f'''
                                    <div class="sup-card">
                                        <div class="sup-header" style="margin-bottom: 5px;">
                                            <div class="sup-name">📋 {obter_nome_visual(sup)}</div>
                                            <div style="background: #f3f3f3; color: {cor_quebra}; border: 3px solid {cor_quebra}; padding: 10px 20px; border-radius: 8px; font-size: 26px; font-weight: 900; white-space: nowrap;">Quebra: {quebra:.1f}%</div>
                                        </div>
                                        <div class="faltas-grid">
                                            <div class="falta-box" style="background-color: #fff8e1; border-color: #ffe082;">
                                                <div class="falta-label" style="color: #b78103;">⏳ ABERTO</div>
                                                <div class="falta-value" style="color: #b78103;">{qtd_aberto}</div>
                                            </div>
                                            <div class="falta-box" style="background-color: #e8f5e9; border-color: #a5d6a7;">
                                                <div class="falta-label" style="color: #2e7d32;">✅ PRODUTIVO</div>
                                                <div class="falta-value" style="color: #1b5e20;">{qtd_produtivo}</div>
                                            </div>
                                            <div class="falta-box" style="background-color: #ffebee; border-color: #ffcdd2;">
                                                <div class="falta-label" style="color: #c62828;">❌ QUEBRAS</div>
                                                <div class="falta-value" style="color: #b30000;">{qtd_ne}</div>
                                            </div>
                                        </div>
                                    </div>''', unsafe_allow_html=True)
                                    
                    if st.session_state.novo_ciclo:
                        texto_audio = f"Atenção para a P M E. A quebra geral está em {quebra_global_pme:.1f} por cento. O limite é de 20 por cento. Podemos ter até {teto_ne_global} OS quebrados, e no momento temos {total_ne_pme}."
                        st.session_state.script_audio_atual = f"<script>{JS_MOTOR_AUDIO}anunciarBase('{texto_audio}', 0);</script>"

            else: st.error("Colunas necessárias (Categorias, Tipo OS, Status) não encontradas no arquivo.")
                
        if st.session_state.novo_ciclo: st.session_state.novo_ciclo = False
        st.components.v1.html(st.session_state.script_audio_atual, height=0)

    # -------------------------------------------------------------------------
    # TELA 9: VISÃO GERAL DA ROTA E PROJEÇÃO (NOVA TELA) 🚀
    # -------------------------------------------------------------------------
    elif st.session_state.idx == 9:
        st.markdown(f'''<div class="topo-container">
            <div class="topo-esquerda">{logo_html}</div>
            <div class="topo-centro">VISÃO GERAL DA ROTA E PROJEÇÃO</div>
            <div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div>
        </div>
        {html_audio_ind}''', unsafe_allow_html=True)

        if os.path.exists(ARQUIVO_ROTA_DISCO):
            df_rota = pd.read_csv(ARQUIVO_ROTA_DISCO, sep=None, engine='python', dtype=str)
            df_rota.columns = [str(c).strip().upper() for c in df_rota.columns]

            col_tecnico = next((c for c in df_rota.columns if 'RECURSO' in c or 'NOME' in c), df_rota.columns[0])
            col_sup = next((c for c in df_rota.columns if 'SUPERVISOR' in c), None)
            
            # ---> INTELIGÊNCIA DOS FILTROS DA TABELA DINÂMICA <---
            
            # 1. Filtro Cidade (Apenas DIADEMA, SANTO ANDRE, SAO BERNARDO DO CAMPO)
            col_cidade = next((c for c in df_rota.columns if 'CIDADE' in c), None)
            if col_cidade:
                df_rota = df_rota[df_rota[col_cidade].notna()]
                df_rota = df_rota[df_rota[col_cidade].astype(str).str.strip() != '']
                cond_cidade = df_rota[col_cidade].astype(str).str.upper().str.contains('DIADEMA|SANTO ANDRE|BERNARDO|SBC', regex=True)
                df_rota = df_rota[cond_cidade]

            # 2. Filtro de Cancelados e Suspensos (Coluna Status da Atividade)
            col_status_ativ = next((c for c in df_rota.columns if 'STATUS DA ATIVIDADE' in c), None)
            if col_status_ativ:
                df_rota = df_rota[df_rota[col_status_ativ].notna()]
                df_rota = df_rota[df_rota[col_status_ativ].astype(str).str.strip() != '']
                str_status_ativ = df_rota[col_status_ativ].astype(str).str.upper()
                df_rota = df_rota[~str_status_ativ.str.contains('CANCELADO|SUSPENSO', na=False)]

            # 3. Filtro Tipo de Atividade (Remover Retorno Credenciada)
            col_tipo_os = next((c for c in df_rota.columns if 'TIPO DE ATIVIDADE3' in c or 'TIPO DE ATIVIDADE 3' in c or 'ATIVIDADE3' in c), None)
            if not col_tipo_os: col_tipo_os = next((c for c in df_rota.columns if 'TIPO O.S' in c or 'ATIVIDADE' in c), None)
            if col_tipo_os:
                df_rota = df_rota[df_rota[col_tipo_os].notna()]
                df_rota = df_rota[df_rota[col_tipo_os].astype(str).str.strip() != '']
                df_rota = df_rota[~df_rota[col_tipo_os].astype(str).str.upper().str.contains('RETORNO CREDENCIADA', na=False)]

            # 4. Define a coluna oficial de leitura do agrupamento (A absoluta é a STATUS CONTRATO)
            col_status = next((c for c in df_rota.columns if 'STATUS CONTRATO' in c or 'STATUS_TV' in c), None)
            if not col_status: col_status = col_status_ativ
            if not col_status: col_status = next((c for c in df_rota.columns if 'STATUS' in c), None)

            # --- BUSCA BLINDADA DA COLUNA DE TAREFAS ---
            col_tarefas = None
            for c in df_rota.columns:
                c_clean = unicodedata.normalize('NFKD', str(c)).encode('ASCII', 'ignore').decode('utf-8').upper().strip()
                if 'TAREFA' in c_clean or 'QTD' in c_clean:
                    if 'GERAL' not in c_clean and 'TECNICO' not in c_clean:
                        col_tarefas = c
                        break

            def class_sup_9(row):
                sup = str(row.get(col_sup, '')).upper().strip() if col_sup else ''
                for oficial in SUPERVISORES_ORDENADOS:
                    if oficial in sup: return oficial
                return "DESCARTADO"

            if col_status:
                df_rota['SUPERVISOR_CLEAN'] = df_rota.apply(class_sup_9, axis=1)
                df_proj = df_rota[df_rota['SUPERVISOR_CLEAN'] != "DESCARTADO"].copy()

                # *** TIRANDO OS RETORNOS DA PROJEÇÃO GERAL ***
                if col_tipo_os:
                    df_proj = df_proj[~df_proj[col_tipo_os].astype(str).str.upper().str.contains('RETORNO', na=False)]

                df_proj['STATUS_PADRAO'] = df_proj[col_status].apply(padronizar_status)

                # Garantindo soma de TAREFAS e não contagem de linhas
                if col_tarefas:
                    df_proj['VALOR_TAREFA'] = pd.to_numeric(df_proj[col_tarefas].astype(str).str.replace(',', '.').str.strip(), errors='coerce').fillna(0)
                    if df_proj['VALOR_TAREFA'].sum() == 0 and len(df_proj) > 0:
                        df_proj['VALOR_TAREFA'] = 1
                else:
                    df_proj['VALOR_TAREFA'] = 1
                    st.error(f"⚠️ COLUNA DE TAREFAS NÃO ENCONTRADA! Contando 1 por linha. Colunas lidas: {', '.join(df_rota.columns)}")

                # ---> INÍCIO DO BANNER TOTAL GERAL <---
                df_abc_proj = df_proj[df_proj['SUPERVISOR_CLEAN'].isin(SUPS_ABC)]
                
                # BLINDAGEM MATEMÁTICA: O Total dita a regra, o resto se ajusta!
                total_tarefas_op = df_abc_proj['VALOR_TAREFA'].sum()
                os_ne_op = df_abc_proj.loc[df_abc_proj['STATUS_PADRAO'] == 'O.S NE', 'VALOR_TAREFA'].sum()
                produtivo_op = df_abc_proj.loc[df_abc_proj['STATUS_PADRAO'] == 'Produtivo', 'VALOR_TAREFA'].sum()
                
                # Tudo que sobrar cai automaticamente como Aberto/Pendente
                em_aberto_op = total_tarefas_op - os_ne_op - produtivo_op 

                total_tecnicos_op = df_abc_proj[col_tecnico].nunique() if col_tecnico in df_abc_proj.columns else 1
                if total_tecnicos_op == 0: total_tecnicos_op = 1

                denom_quebra_op = os_ne_op + produtivo_op
                quebra_op = (os_ne_op / denom_quebra_op) * 100 if denom_quebra_op > 0 else 0
                eficiencia_op = (produtivo_op / denom_quebra_op) * 100 if denom_quebra_op > 0 else 100
                projecao_op = produtivo_op + (em_aberto_op * (eficiencia_op / 100))
                media_equipe_op = total_tarefas_op / total_tecnicos_op

                cor_q_op = "#c62828" if quebra_op > 20.0 else "#2e7d32"

                st.session_state.ticker_data[9] = f"🌍 GERAL: {int(total_tarefas_op)} OS | PROJ: {int(round(projecao_op))} | QUEBRAS: {quebra_op:.1f}% | EFIC: {eficiencia_op:.1f}%"

                st.markdown(f'''
                <div class="box-base" style="padding: 10px 10px; margin-bottom: 15px; border-left: 15px solid #003366; background: #e3f2fd;">
                    <div class="nome-base" style="font-size: 30px !important; margin-bottom: 10px; color: #003366; text-shadow: 1px 1px 2px rgba(0,0,0,0.1);">🌍 ROTA ATUAL</div>
                    <div style="display: flex; justify-content: space-around; align-items: center; background: #ffffff; padding: 10px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 10px;">
                        <div style="text-align: center;">
                            <div style="font-size: 18px; font-weight: bold; color: #666;">TOTAL TAREFAS</div>
                            <div style="font-size: 40px; font-weight: 900; color: #003366; line-height: 1;">{int(total_tarefas_op)}</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 18px; font-weight: bold; color: #666;">PROJEÇÃO</div>
                            <div style="font-size: 40px; font-weight: 900; color: #00838f; line-height: 1;">{int(round(projecao_op))}</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 18px; font-weight: bold; color: #666;">EFICIÊNCIA</div>
                            <div style="font-size: 40px; font-weight: 900; color: #2e7d32; line-height: 1;">{eficiencia_op:.1f}%</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 18px; font-weight: bold; color: #666;">QUEBRAS</div>
                            <div style="font-size: 40px; font-weight: 900; color: {cor_q_op}; line-height: 1;">{quebra_op:.1f}%</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 18px; font-weight: bold; color: #666;">MÉDIA / TÉC</div>
                            <div style="font-size: 40px; font-weight: 900; color: #e65100; line-height: 1;">{media_equipe_op:.2f}</div>
                        </div>
                    </div>
                    <div style="font-size: 22px; color: #444; font-weight: bold; display: flex; justify-content: center; gap: 40px; text-transform: uppercase;">
                        <span>⏳ ABERTO: <span style="color:#b78103;">{int(em_aberto_op)}</span></span>
                        <span>✅ PRODUTIVO: <span style="color:#1b5e20;">{int(produtivo_op)}</span></span>
                        <span>❌ QUEBRAS: <span style="color:#b30000;">{int(os_ne_op)}</span></span>
                        <span>👷 TÉCNICOS: <span style="color:#003366;">{total_tecnicos_op}</span></span>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                # ---> FIM DO BANNER TOTAL GERAL <---

                for i in range(0, len(SUPS_ABC), 2):
                    cols_sup = st.columns(2)
                    for j in range(2):
                        if i + j < len(SUPS_ABC):
                            sup = SUPS_ABC[i + j]
                            with cols_sup[j]:
                                df_sup = df_proj[df_proj['SUPERVISOR_CLEAN'] == sup]

                                total_tarefas = df_sup['VALOR_TAREFA'].sum()
                                os_ne = df_sup.loc[df_sup['STATUS_PADRAO'] == 'O.S NE', 'VALOR_TAREFA'].sum()
                                produtivo = df_sup.loc[df_sup['STATUS_PADRAO'] == 'Produtivo', 'VALOR_TAREFA'].sum()
                                em_aberto = total_tarefas - os_ne - produtivo

                                total_tecnicos = df_sup[col_tecnico].nunique() if col_tecnico in df_sup.columns else 1
                                if total_tecnicos == 0: total_tecnicos = 1

                                denom_quebra = os_ne + produtivo
                                quebra = (os_ne / denom_quebra) * 100 if denom_quebra > 0 else 0
                                eficiencia = (produtivo / denom_quebra) * 100 if denom_quebra > 0 else 100
                                projecao = produtivo + (em_aberto * (eficiencia / 100))
                                media_equipe = total_tarefas / total_tecnicos

                                cor_q = "#c62828" if quebra > 20.0 else "#2e7d32"

                                st.markdown(f'''
                                <div class="sup-card">
                                    <div class="sup-header">
                                        <div class="sup-name">📋 {obter_nome_visual(sup)}</div>
                                        <div style="display: flex; gap: 15px; align-items: center;">
                                            <div style="background: #e3f2fd; color: #006064; border: 3px solid #006064; padding: 8px 15px; border-radius: 8px; font-size: 20px; font-weight: bold; white-space: nowrap;">Técnicos: {total_tecnicos} | Média: {media_equipe:.2f}</div>
                                        </div>
                                    </div>
                                    <div style="font-size: 16px; color: #666; text-align: center; margin-bottom: 10px; font-weight: bold; text-transform: uppercase;">
                                        TOTAL TAREFAS: {int(total_tarefas)} &nbsp;|&nbsp; QUEBRA: <span style="color:{cor_q}">{quebra:.1f}%</span> &nbsp;|&nbsp; EFICIÊNCIA: <span style="color:#2e7d32">{eficiencia:.1f}%</span>
                                    </div>
                                    <div class="faltas-grid">
                                        <div class="falta-box" style="background-color: #fff8e1; border-color: #ffe082;">
                                            <div class="falta-label" style="color: #b78103;">⏳ ABERTO</div>
                                            <div class="falta-value" style="color: #b78103;">{int(em_aberto)}</div>
                                        </div>
                                        <div class="falta-box" style="background-color: #e8f5e9; border-color: #a5d6a7;">
                                            <div class="falta-label" style="color: #2e7d32;">✅ PRODUTIVO</div>
                                            <div class="falta-value" style="color: #1b5e20;">{int(produtivo)}</div>
                                        </div>
                                        <div class="falta-box" style="background-color: #ffebee; border-color: #ffcdd2;">
                                            <div class="falta-label" style="color: #c62828;">❌ QUEBRAS</div>
                                            <div class="falta-value" style="color: #b30000;">{int(os_ne)}</div>
                                        </div>
                                        <div class="falta-box" style="background-color: #e0f7fa; border-color: #80deea;">
                                            <div class="falta-label" style="color: #00838f;">🚀 PROJEÇÃO</div>
                                            <div class="falta-value" style="color: #00838f;">{int(round(projecao))}</div>
                                        </div>
                                    </div>
                                </div>''', unsafe_allow_html=True)
                if st.session_state.novo_ciclo:
                    texto_audio_9 = f"Atenção para a Visão Geral da Rota. Temos um total de {int(total_tarefas_op)} tarefas. A projeção da operação está em {int(round(projecao_op))}, com um total de {int(os_ne_op)} quebras no momento."
                    st.session_state.script_audio_atual = f"<script>{JS_MOTOR_AUDIO}anunciarBase('{texto_audio_9}', 0);</script>"
                    st.session_state.novo_ciclo = False
                st.components.v1.html(st.session_state.script_audio_atual, height=0)
            else: st.error("Coluna Status não encontrada na base de dados da rota.")
        else: st.error("Ficheiro rota_sincronizada.csv não encontrado.")

    # -------------------------------------------------------------------------
    # TELA 5: CONSULTIVO GERAL
    # -------------------------------------------------------------------------
    elif st.session_state.idx == 5:
        st.markdown(f'''<div class="topo-container">
            <div class="topo-esquerda">{logo_html}</div>
            <div class="topo-centro">CONSULTIVO GERAL</div>
            <div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div>
        </div>
        {icone_mudo}''', unsafe_allow_html=True)

        if os.path.exists(ARQUIVO_CONSULTIVO):
            try:
                df_cons = pd.read_csv(ARQUIVO_CONSULTIVO, sep=None, engine='python', dtype=str)
                df_cons.columns = [unicodedata.normalize('NFKD', str(c)).encode('ASCII', 'ignore').decode('utf-8').strip().upper().replace(' ', '_') for c in df_cons.columns]

                col_qtd = next((c for c in df_cons.columns if 'QTD' in c and 'PRODUTO' in c), None)
                df_cons['QTD_PRODUTOS_CALC'] = pd.to_numeric(df_cons[col_qtd].astype(str).str.replace(',', '.'), errors='coerce').fillna(0).astype(int) if col_qtd else 0
                df_cons['SUPERVISOR'] = df_cons['SUPERVISOR'].apply(limpar_texto) if 'SUPERVISOR' in df_cons.columns else ''

                def class_sup(row):
                    for oficial in SUPERVISORES_ORDENADOS:
                        if limpar_texto(oficial.split()[0]) in row.get('SUPERVISOR', ''): return oficial
                    return "DESCARTADO"

                df_cons['SUPERVISOR_CLEAN'] = df_cons.apply(class_sup, axis=1)
                df_cards = df_cons[df_cons['SUPERVISOR_CLEAN'] != "DESCARTADO"].copy()

                total_realizado_abc = df_cards['QTD_PRODUTOS_CALC'].sum()

                hoje = datetime.utcnow() - timedelta(hours=3)
                ano = hoje.year
                mes = hoje.month
                _, num_dias = calendar.monthrange(ano, mes)
                dias_restantes = sum(1 for d in range(hoje.day, num_dias + 1) if calendar.weekday(ano, mes, d) != 6)
                if dias_restantes == 0: dias_restantes = 1

                meta_mensal_abc = len(SUPS_ABC) * 350

                st.session_state.ticker_data[5] = f"📈 CONSULTIVO MÊS: {total_realizado_abc} (META: {meta_mensal_abc})"

                st.markdown(f'''<div style="text-align: center; margin-top: -10px; margin-bottom: 20px;">
                    <span style="font-size: 24px; font-weight: bold; color: #555;">Dias úteis restantes no mês: </span>
                    <span style="font-size: 32px; font-weight: 900; color: #cc6600;">{dias_restantes}</span>
                </div>''', unsafe_allow_html=True)

                st.markdown(f'''<div class="box-base">
                    <div class="nome-base">🏢 TOTAL (Meta: {meta_mensal_abc})</div>
                    <div class="num-base">{total_realizado_abc}</div>
                </div>''', unsafe_allow_html=True)
                
                for i in range(0, len(SUPS_ABC), 2):
                    cols_sup = st.columns(2)
                    for j in range(2):
                        if i + j < len(SUPS_ABC):
                            sup = SUPS_ABC[i + j]
                            with cols_sup[j]:
                                qtd_sup = df_cards[df_cards['SUPERVISOR_CLEAN'] == sup]['QTD_PRODUTOS_CALC'].sum()
                                falta_individual = max(0, 350 - qtd_sup)
                                ritmo_diario_individual = int(round(falta_individual / dias_restantes))

                                st.markdown(f'''
                                <div class="sup-card">
                                    <div class="sup-header">
                                        <div class="sup-name">📋 {obter_nome_visual(sup)}</div>
                                        <div class="badge-faltas" style="background: #e8f5e9; color: #2e7d32; border-color: #a5d6a7;">Alvo: 350</div>
                                    </div>
                                    <div class="faltas-grid">
                                        <div class="falta-box" style="background-color: #e8f5e9; border-color: #a5d6a7;">
                                            <div class="falta-label" style="color: #2e7d32;">📦 TOTAL</div>
                                            <div class="falta-value" style="color: #1b5e20;">{qtd_sup}</div>
                                        </div>
                                        <div class="falta-box" style="background-color: #ffebee; border-color: #ffcdd2;">
                                            <div class="falta-label" style="color: #c62828;">📉 FALTA</div>
                                            <div class="falta-value" style="color: #b30000;">{falta_individual}</div>
                                        </div>
                                        <div class="falta-box" style="background-color: #fff8e1; border-color: #ffe082;">
                                            <div class="falta-label" style="color: #b78103;">🎯 DIÁRIA</div>
                                            <div class="falta-value" style="color: #b78103;">{ritmo_diario_individual}</div>
                                        </div>
                                    </div>
                                </div>''', unsafe_allow_html=True)

                if st.session_state.novo_ciclo:
                    st.session_state.script_audio_atual = ""
                    st.session_state.novo_ciclo = False
                st.components.v1.html(st.session_state.script_audio_atual, height=0)

            except Exception as e: st.error(f"Erro ao processar colunas do Consultivo. Detalhes: {e}")
        else: st.warning("Aguardando sincronização da planilha master para carregar o Consultivo...")

    # -------------------------------------------------------------------------
    # TELA 6: CONSULTIVO DIÁRIO 
    # -------------------------------------------------------------------------
    elif st.session_state.idx == 6:
        st.markdown(f'''<div class="topo-container">
            <div class="topo-esquerda">{logo_html}</div>
            <div class="topo-centro">CONSULTIVO DIÁRIO</div>
            <div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div>
        </div>
        {icone_mudo}''', unsafe_allow_html=True)

        if os.path.exists(ARQUIVO_CONSULTIVO):
            try:
                df_cons = pd.read_csv(ARQUIVO_CONSULTIVO, sep=None, engine='python', dtype=str)
                df_cons.columns = [str(c).upper().strip().replace(' ', '_') for c in df_cons.columns]

                col_qtd = next((c for c in df_cons.columns if 'QTD' in c and 'PRODUTO' in c), None)
                df_cons['QTD_PRODUTOS_CALC'] = pd.to_numeric(df_cons[col_qtd].astype(str).str.replace(',', '.'), errors='coerce').fillna(0).astype(int) if col_qtd else 0
                df_cons['SUPERVISOR'] = df_cons['SUPERVISOR'].apply(limpar_texto) if 'SUPERVISOR' in df_cons.columns else ''

                def class_sup(row):
                    for oficial in SUPERVISORES_ORDENADOS:
                        if limpar_texto(oficial.split()[0]) in row.get('SUPERVISOR', ''): return oficial
                    return "DESCARTADO"

                df_cons['SUPERVISOR_CLEAN'] = df_cons.apply(class_sup, axis=1)
                df_cards = df_cons[df_cons['SUPERVISOR_CLEAN'] != "DESCARTADO"].copy()

                hoje_br = datetime.utcnow() - timedelta(hours=3)
                hoje_str_br = hoje_br.strftime('%d/%m/%Y')
                hoje_str_us = hoje_br.strftime('%Y-%m-%d')

                col_data = next((c for c in df_cards.columns if 'DATA' in c), None)
                if col_data:
                    df_cards['DATA_TXT'] = df_cards[col_data].astype(str).str.strip().str[:10]
                    mask_hoje = (df_cards['DATA_TXT'] == hoje_str_br) | (df_cards['DATA_TXT'] == hoje_str_us)
                    df_hoje = df_cards[mask_hoje].copy()
                else:
                    df_hoje = pd.DataFrame() 
                
                ano = hoje_br.year
                mes = hoje_br.month
                _, num_dias = calendar.monthrange(ano, mes)
                dias_restantes = sum(1 for d in range(hoje_br.day, num_dias + 1) if calendar.weekday(ano, mes, d) != 6)
                if dias_restantes <= 0: dias_restantes = 1

                if df_hoje.empty: st.warning(f"⚠️ Atenção: Nenhum consultivo lançado para a data de hoje ({hoje_str_br}).")

                total_hoje_abc = df_hoje['QTD_PRODUTOS_CALC'].sum() if not df_hoje.empty else 0

                meta_dia_base_abc = 0
                for sup in SUPS_ABC:
                    qtd_m = df_cards[df_cards['SUPERVISOR_CLEAN'] == sup]['QTD_PRODUTOS_CALC'].sum()
                    meta_dia_base_abc += int(round(max(0, 350 - qtd_m) / dias_restantes))

                st.session_state.ticker_data[6] = f"📉 CONSULTIVO HOJE: {total_hoje_abc} (META: {meta_dia_base_abc})"

                st.markdown(f'''<div style="text-align: center; margin-top: -10px; margin-bottom: 20px;">
                    <span style="font-size: 24px; font-weight: bold; color: #555;">Resultados Isolados de Hoje ({hoje_str_br}) - Dias úteis restantes: </span>
                    <span style="font-size: 32px; font-weight: 900; color: #cc6600;">{dias_restantes}</span>
                </div>''', unsafe_allow_html=True)

                st.markdown(f'''<div class="box-base">
                    <div class="nome-base">🏢 HOJE (Meta Diária: {meta_dia_base_abc})</div>
                    <div class="num-base">{total_hoje_abc}</div>
                </div>''', unsafe_allow_html=True)
                
                for i in range(0, len(SUPS_ABC), 2):
                    cols_sup = st.columns(2)
                    for j in range(2):
                        if i + j < len(SUPS_ABC):
                            sup = SUPS_ABC[i + j]
                            with cols_sup[j]:
                                qtd_mes = df_cards[df_cards['SUPERVISOR_CLEAN'] == sup]['QTD_PRODUTOS_CALC'].sum()
                                qtd_hoje = df_hoje[df_hoje['SUPERVISOR_CLEAN'] == sup]['QTD_PRODUTOS_CALC'].sum() if not df_hoje.empty else 0
                                
                                meta_dia = int(round(max(0, 350 - qtd_mes) / dias_restantes))
                                falta_hoje = int(round(max(0, meta_dia - qtd_hoje)))

                                st.markdown(f'''
                                <div class="sup-card">
                                    <div class="sup-header">
                                        <div class="sup-name">📋 {obter_nome_visual(sup)}</div>
                                        <div class="badge-faltas" style="background: #e8f5e9; color: #2e7d32; border-color: #a5d6a7;">Acumulado: {int(qtd_mes)}</div>
                                    </div>
                                    <div class="faltas-grid">
                                        <div class="falta-box" style="background-color: #e8f5e9; border-color: #a5d6a7;">
                                            <div class="falta-label" style="color: #2e7d32;">📦 HOJE</div>
                                            <div class="falta-value" style="color: #1b5e20;">{int(qtd_hoje)}</div>
                                        </div>
                                        <div class="falta-box" style="background-color: #ffebee; border-color: #ffcdd2;">
                                            <div class="falta-label" style="color: #c62828;">📉 FALTAM</div>
                                            <div class="falta-value" style="color: #b30000;">{falta_hoje}</div>
                                        </div>
                                        <div class="falta-box" style="background-color: #fff8e1; border-color: #ffe082;">
                                            <div class="falta-label" style="color: #b78103;">🎯 DIÁRIA</div>
                                            <div class="falta-value" style="color: #b78103;">{meta_dia}</div>
                                        </div>
                                    </div>
                                </div>''', unsafe_allow_html=True)

                if st.session_state.novo_ciclo:
                    st.session_state.script_audio_atual = ""
                    st.session_state.novo_ciclo = False
                st.components.v1.html(st.session_state.script_audio_atual, height=0)

            except Exception as e: st.error(f"Erro ao processar colunas do Consultivo. Detalhes: {e}")
        else: st.warning("Aguardando sincronização da planilha master para carregar o Consultivo...")

    # -------------------------------------------------------------------------
    # TELA 3: PRINT DOS INDICADORES
    # -------------------------------------------------------------------------
    elif st.session_state.idx == 3:
        st.markdown(f'''<div class="topo-container">
            <div class="topo-esquerda">{logo_html}</div>
            <div class="topo-centro">PRINT DOS INDICADORES</div>
            <div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div>
        </div>
        {html_audio_ind}''', unsafe_allow_html=True)

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

                total_faltas_ind = df_produtivo['FALTA_NR35'].sum() + df_produtivo['FALTA_CERT'].sum() + df_produtivo['FALTA_BST'].sum()
                st.session_state.ticker_data[3] = f"📋 INDICADORES: {int(total_faltas_ind)} FALTAS"

                st.markdown('<div class="ind-base-title abc">PENDÊNCIAS INDICADORES</div>', unsafe_allow_html=True)
                
                for i in range(0, len(SUPS_ABC), 2):
                    cols_sup = st.columns(2)
                    for j in range(2):
                        if i + j < len(SUPS_ABC):
                            sup = SUPS_ABC[i + j]
                            with cols_sup[j]:
                                df_sup = df_produtivo[df_produtivo['SUPERVISOR_CLEAN'] == sup]
                                f_35, f_ce, f_bs = int(df_sup['FALTA_NR35'].sum()), int(df_sup['FALTA_CERT'].sum()), int(df_sup['FALTA_BST'].sum())
                                st.markdown(f'''<div class="sup-card"><div class="sup-header"><div class="sup-name">📋 {obter_nome_visual(sup)}</div><div class="badge-faltas">Total Faltas: {f_35+f_ce+f_bs}</div></div>
                                    <div class="faltas-grid"><div class="falta-box"><div class="falta-label">🪜 NR35</div><div class="falta-value">{f_35}</div></div>
                                    <div class="falta-box"><div class="falta-label">📜 CERT.</div><div class="falta-value">{f_ce}</div></div>
                                    <div class="falta-box"><div class="falta-label">📶 BST</div><div class="falta-value">{f_bs}</div></div></div></div>''', unsafe_allow_html=True)

                if st.session_state.novo_ciclo:
                    if permitir_audio_ind:
                        st.session_state.script_audio_atual = f"<script>{JS_MOTOR_AUDIO}anunciarBase('Monitores, enviem os prints pendentes do N R 35, Band Steering e certidão de atendimento.', 0);</script>"
                    else: st.session_state.script_audio_atual = ""
                    st.session_state.novo_ciclo = False
                st.components.v1.html(st.session_state.script_audio_atual, height=0)
            else: st.error("Coluna Status não encontrada.")
        else: st.error("Ficheiro rota_sincronizada.csv não encontrado.")

    # -------------------------------------------------------------------------
    # TELA 2: HORÁRIO
    # -------------------------------------------------------------------------
    elif st.session_state.idx == 2:
        st.markdown(f'''<div class="topo-container">
            <div class="topo-esquerda">{logo_html}</div>
            <div class="topo-centro">HORÁRIO</div>
            <div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div>
        </div>
        {icone_ativo}''', unsafe_allow_html=True)

        tempo_real = datetime.utcnow() - timedelta(hours=3)
        
        st.markdown(f'''
        <div class="relogio-container">
            <div id="relogio-dinamico" class="hora-gigante">{tempo_real.strftime("%H:%M:%S")}</div>
            <div class="data-media">{tempo_real.strftime("%d/%m/%Y")}</div>
        </div>
        ''', unsafe_allow_html=True)
        
        if st.session_state.novo_ciclo:
            st.session_state.script_audio_atual = f"<script>{JS_MOTOR_AUDIO}anunciarBase('Hora certa: {tempo_real.strftime('%H e %M')}.', 0);</script>"
            st.session_state.novo_ciclo = False
        
        script_relogio_dinamico = """
        <script>
            setInterval(function() {
                var el = window.parent.document.getElementById('relogio-dinamico');
                if (el) {
                    var data = new Date();
                    var h = String(data.getHours()).padStart(2, '0');
                    var m = String(data.getMinutes()).padStart(2, '0');
                    var s = String(data.getSeconds()).padStart(2, '0');
                    el.innerText = h + ":" + m + ":" + s;
                }
            }, 1000);
        </script>
        """
        
        st.components.v1.html(st.session_state.script_audio_atual + script_relogio_dinamico, height=0)

    # ---> RENDERIZADOR DO TICKER FINANCEIRO <---
    if st.session_state.idx != 4:  
        ticker_items = []
        for k, v in st.session_state.ticker_data.items():
            if k != st.session_state.idx:
                ticker_items.append(f'<span class="ticker__item">{v}</span>')
        
        if ticker_items:
            separator = '<span style="color:#ff9800; font-weight:bold; font-size:24px;">&nbsp;&nbsp;•&nbsp;&nbsp;</span>'
            joined_items = separator.join(ticker_items)
            ticker_content = f"{joined_items}{separator}{joined_items}{separator}{joined_items}"
            
            st.markdown(f'''
            <div class="ticker-wrap">
                <div class="ticker">
                    {ticker_content}
                </div>
            </div>
            ''', unsafe_allow_html=True)

# =========================================================================
# MOTOR DE TRANSIÇÃO E LOOP INFINITO 🔄
# =========================================================================

if st.session_state.idx == 0: espera = 60 
elif st.session_state.idx == 1: espera = 30 if alerta_fim_janela else 60 
elif st.session_state.idx == 7: espera = 60 
elif st.session_state.idx == 8: espera = 60 
elif st.session_state.idx == 9: espera = 60 
elif st.session_state.idx == 5: espera = 60 
elif st.session_state.idx == 6: espera = 60 
elif st.session_state.idx == 3: espera = 45 
elif st.session_state.idx == 2: espera = 30 if alerta_fim_janela else 60 
elif st.session_state.idx == 4: espera = 2 

# Controle interativo (JS + Python)
pular = st.button("PRÓXIMA ➡️")

if not pular:
    js_timer = f"""
    <script>
    setTimeout(function() {{
        var buttons = window.parent.document.querySelectorAll('button');
        for (var i=0; i<buttons.length; i++) {{
            if (buttons[i].innerText.includes('PRÓXIMA ➡️')) {{
                buttons[i].click();
                break;
            }}
        }}
    }}, {espera * 1000});
    </script>
    """
    st.components.v1.html(js_timer, height=0)
    st.stop()

if st.session_state.idx == 4:
    st.session_state.idx = st.session_state.prox_idx
    st.session_state.novo_ciclo = True
else:
    if antes_0830:
        if st.session_state.idx == 0: prox_idx = 2
        elif st.session_state.idx == 2: prox_idx = 0
        else: prox_idx = 0
    else:
        if st.session_state.idx == 1: prox_idx = 7
        elif st.session_state.idx == 7: prox_idx = 8
        elif st.session_state.idx == 8: prox_idx = 9
        elif st.session_state.idx == 9: prox_idx = 5
        elif st.session_state.idx == 5: prox_idx = 6 
        elif st.session_state.idx == 6: prox_idx = 3 
        elif st.session_state.idx == 3: prox_idx = 2
        elif st.session_state.idx == 2: prox_idx = 1
        else: prox_idx = 1
        
    st.session_state.prox_idx = prox_idx
    st.session_state.idx = 4 

CONTEUDO_TV.empty()
st.rerun()

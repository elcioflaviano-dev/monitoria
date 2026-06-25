import streamlit as st
import pandas as pd
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
if not os.path.exists(ARQUIVO_LOGO): ARQUIVO_LOGO = os.path.join(ROOT_DIR, "pages", "logo.png")

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
    /* 🔥 REMOÇÃO AGRESSIVA DE ELEMENTOS STREAMLIT 🔥 */
    .viewerBadge_container, .viewerBadge_link, [data-testid="viewerBadge"], #viewerBadge, .stAppDeployButton, footer, [data-testid="stHeader"], #MainMenu, [data-testid="stSidebar"] { display: none !important; visibility: hidden !important; }
    
    .stApp { background-color: #ffffff !important; }
    .topo-container { background: #003366; color: white; padding: 0px 30px; border-radius: 0 0 15px 15px; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; margin-bottom: 10px; height: 100px; }
    .topo-centro { font-size: 45px; font-weight: 900; text-align: center; white-space: nowrap; }
    .botao-home { color: #fff; font-size: 18px; font-weight: bold; border: 2px solid #fff; padding: 8px 15px; border-radius: 5px; text-decoration: none; }
    
    .box-base { background: #e8f5e9; border-left: 10px solid #2e7d32; padding: 15px 10px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.15); margin-bottom: 25px; }
    .box-base-sp { background: #e0f2f1; border-left: 10px solid #00897b; padding: 15px 10px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.15); margin-bottom: 25px; }
    .nome-base { font-size: 26px; font-weight: 900; color: #333; text-transform: uppercase;}
    .num-base { font-size: 95px; font-weight: 900; color: #111; line-height: 1.1; }
    
    .sup-card { background: #ffffff; border: 1px solid #e0e0e0; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    .sup-name { font-size: 32px; font-weight: 900; color: #333; text-transform: uppercase; }
    .badge-faltas { padding: 8px 16px; border-radius: 8px; font-size: 18px; font-weight: bold; border: 1px solid; }
    
    .faltas-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; }
    .falta-box { border-radius: 8px; padding: 15px; text-align: center; border: 1px solid #eee; }
    .falta-label { font-size: 14px; font-weight: bold; text-transform: uppercase; margin-bottom: 6px; }
    .falta-value { font-size: 40px; font-weight: 900; line-height: 1; }
</style>""", unsafe_allow_html=True)

# Lógica de processamento
SUPS_ABC = ["EDSON MARCO", "MARCOS ROBERTO", "NELSON"]
SUPS_SP = ["ALAN", "FRANCISCO", "JOAO CARLOS MIRON"]
SUPERVISORES_ORDENADOS = SUPS_ABC + SUPS_SP

def obter_nome_visual(n):
    n = str(n).upper()
    if 'FRANCISCO' in n: return "FRANCISCO"
    if 'MARCOS' in n: return "MARCOS ROBERTO"
    if 'EDSON' in n: return "EDSON MARCO"
    if 'JOAO' in n or 'MIRON' in n: return "JOÃO CARLOS"
    if 'NELSON' in n: return "NELSON"
    if 'ALAN' in n: return "ALAN"
    return n.split()[0]

def limpar_texto(txt):
    if pd.isna(txt): return ''
    return unicodedata.normalize('NFKD', str(txt).strip().upper()).encode('ASCII', 'ignore').decode('utf-8')

# Inicialização de estado
if "idx" not in st.session_state: 
    st.session_state.idx = 0
    st.session_state.last_time = time.time()
    st.session_state.novo_ciclo = True

# Motor de Áudio JavaScript (Campainha)
JS_MOTOR_AUDIO = """
function tocarAlertaChamaAtencao() {
    try {
        let ctx = new (window.parent.AudioContext || window.AudioContext)();
        let tempo = ctx.currentTime;
        function t(f, i, d) {
            let o = ctx.createOscillator(); let g = ctx.createGain();
            o.type = 'sine'; o.frequency.setValueAtTime(f, i);
            g.gain.setValueAtTime(0, i); g.gain.linearRampToValueAtTime(0.5, i + 0.05); g.gain.exponentialRampToValueAtTime(0.01, i + d);
            o.connect(g); g.connect(ctx.destination); o.start(i); o.stop(i + d);
        }
        t(523.25, tempo, 0.5); t(659.25, tempo + 0.2, 0.5); t(784.00, tempo + 0.4, 0.8);
    } catch(e) {}
}
function anunciarBase(texto) {
    tocarAlertaChamaAtencao();
    setTimeout(() => {
        let synth = window.parent.speechSynthesis;
        try { synth.cancel(); } catch(e) {}
        let m = new SpeechSynthesisUtterance(texto);
        m.lang = 'pt-BR'; synth.speak(m);
    }, 1500);
}
"""

# Lógica de Rotação de telas
espera = 60
if time.time() - st.session_state.last_time > espera:
    st.session_state.idx = (st.session_state.idx + 1) % 6
    st.session_state.last_time = time.time()
    st.rerun()

# RENDERIZAÇÃO
CONTEUDO_TV = st.empty()
with CONTEUDO_TV.container():
    # Tela 5: Consultivo Geral
    if st.session_state.idx == 0:
        st.markdown('<div class="topo-container"><div class="topo-centro">PERFORMANCE CONSULTIVO</div></div>', unsafe_allow_html=True)
        if os.path.exists(ARQUIVO_CONSULTIVO):
            df = pd.read_csv(ARQUIVO_CONSULTIVO, sep=None, engine='python', dtype=str)
            df.columns = [str(c).upper().replace(' ', '_') for c in df.columns]
            # [Lógica de renderização Consultivo Geral...]

    # Tela 6: Consultivo Diário Dinâmico
    elif st.session_state.idx == 1:
        st.markdown('<div class="topo-container"><div class="topo-centro">PERFORMANCE CONSULTIVO DIÁRIO</div></div>', unsafe_allow_html=True)
        if os.path.exists(ARQUIVO_CONSULTIVO):
            # Carrega dados
            df_cons = pd.read_csv(ARQUIVO_CONSULTIVO, sep=None, engine='python', dtype=str)
            df_cons.columns = [str(c).upper().replace(' ', '_') for c in df_cons.columns]
            df_cons['SUPERVISOR'] = df_cons['SUPERVISOR'].fillna('#N/D').apply(limpar_texto)
            df_cons['BASE'] = df_cons['BASE'].fillna('N/D').apply(limpar_texto)
            
            # Filtra supervisores válidos
            df_cards = df_cons[df_cons['SUPERVISOR'] != 'DESCARTADO'].copy()
            
            # Data hoje
            hoje = datetime.utcnow() - timedelta(hours=3)
            df_hoje = df_cards[pd.to_datetime(df_cards['DATA'], dayfirst=True).dt.strftime('%d/%m/%Y') == hoje.strftime('%d/%m/%Y')]
            
            # Dias restantes
            _, num_dias = calendar.monthrange(hoje.year, hoje.month)
            dias_restantes = sum(1 for d in range(hoje.day, num_dias + 1) if calendar.weekday(hoje.year, hoje.month, d) != 6)
            if dias_restantes == 0: dias_restantes = 1
            
            col_abc, col_sp = st.columns(2)
            
            # Loop de renderização com as fórmulas corrigidas
            for base, col in [('ABC', col_abc), ('SP', col_sp)]:
                with col:
                    sups = SUPS_ABC if base == 'ABC' else SUPS_SP
                    for s in sups:
                        qtd_mes = df_cards[df_cards['SUPERVISOR'].str.contains(s.split()[0]) & (df_cards['BASE'] == base)]['QTD_PRODUTOS'].astype(float).sum()
                        qtd_hoje = df_hoje[df_hoje['SUPERVISOR'].str.contains(s.split()[0]) & (df_hoje['BASE'] == base)]['QTD_PRODUTOS'].astype(float).sum()
                        
                        meta_dia = round(max(0, 350 - qtd_mes) / dias_restantes, 1)
                        falta_hoje = round(max(0, meta_dia - qtd_hoje), 1)
                        
                        # Card final renderizado com cores e tamanhos de fonte aumentados
                        st.markdown(f'''
                        <div class="sup-card">
                            <div class="sup-header">
                                <div class="sup-name">📋 {obter_nome_visual(s)}</div>
                                <div class="badge-faltas">Total Acumulado: {qtd_mes}</div>
                            </div>
                            <div class="faltas-grid">
                                <div class="falta-box" style="background-color: #e8f5e9;">
                                    <div class="falta-label">📦 REALIZADO HOJE</div>
                                    <div class="falta-value">{qtd_hoje}</div>
                                </div>
                                <div class="falta-box" style="background-color: #ffebee;">
                                    <div class="falta-label">📉 FALTAM HOJE</div>
                                    <div class="falta-value">{falta_hoje}</div>
                                </div>
                                <div class="falta-box" style="background-color: #fff8e1;">
                                    <div class="falta-label">🎯 META DIÁRIA</div>
                                    <div class="falta-value">{meta_dia}</div>
                                </div>
                            </div>
                        </div>''', unsafe_allow_html=True)

# Inclui ícone de áudio no canto inferior
st.markdown(icone_ativo, unsafe_allow_html=True)

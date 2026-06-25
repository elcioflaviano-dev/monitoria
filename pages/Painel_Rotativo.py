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

# --- FUNÇÕES E VARIÁVEIS GLOBAIS (DEFINIDAS NO TOPO PARA EVITAR NameError) ---
def carregar_logo_html(caminho):
    if os.path.exists(caminho):
        try:
            with open(caminho, "rb") as f:
                enc = base64.b64encode(f.read()).decode('utf-8')
            return f'<img src="data:image/png;base64,{enc}" style="height: 100px; width: auto; object-fit: contain; display: block;">'
        except: return '<div></div>'
    return '<div></div>'

logo_html = carregar_logo_html(ARQUIVO_LOGO)
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

# --- CSS E MOTOR DE ÁUDIO ---
st.markdown("""<style>
    .viewerBadge_container, .viewerBadge_link, [data-testid="viewerBadge"], #viewerBadge, .stAppDeployButton, footer, [data-testid="stHeader"], #MainMenu, [data-testid="stSidebar"] { display: none !important; visibility: hidden !important; }
    .stApp { background-color: #ffffff !important; }
    .topo-container { background: #003366; color: white; padding: 0px 30px; border-radius: 0 0 15px 15px; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; margin-bottom: 10px; height: 100px; }
    .topo-centro { font-size: 45px; font-weight: 900; text-align: center; white-space: nowrap; }
    .botao-home { color: #fff; font-size: 18px; font-weight: bold; border: 2px solid #fff; padding: 8px 15px; border-radius: 5px; text-decoration: none; }
    .box-base { background: #e8f5e9; border-left: 10px solid #2e7d32; padding: 15px 10px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.15); margin-bottom: 25px; }
    .box-base-sp { background: #e0f2f1; border-left: 10px solid #00897b; padding: 15px 10px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.15); margin-bottom: 25px; }
    .nome-base { font-size: 22px; font-weight: 900; color: #333; text-transform: uppercase;}
    .num-base { font-size: 85px; font-weight: 900; color: #111; line-height: 1.1; }
    .box-contagem { background: #f0f2f6; border-left: 8px solid #cc6600; padding: 10px 5px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); margin-bottom: 10px; }
    .box-nome { font-size: 15px; font-weight: 900; color: #003366; text-transform: uppercase; }
    .box-num { font-size: 50px; font-weight: 900; color: #cc6600; line-height: 1; }
    .sup-card { background: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .sup-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 10px; }
    .sup-name { font-size: 24px; font-weight: 900; color: #333; }
    .badge-faltas { background: #ffebee; color: #c62828; padding: 6px 12px; border-radius: 6px; font-size: 14px; font-weight: bold; border: 1px solid #ffcdd2; }
    .faltas-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }
    .falta-box { background-color: #ffebee; border: 1px solid #ffcdd2; border-radius: 6px; padding: 12px 5px; text-align: center; }
    .falta-label { font-size: 11px; font-weight: bold; color: #c62828; text-transform: uppercase; }
    .falta-value { font-size: 32px; font-weight: 900; color: #b30000; }
    .relogio-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 70vh; background-color: #ffffff; width: 100%; }
    .hora-gigante { font-size: 180px; font-weight: 900; color: #003366; }
    .tec-base-nome { background: #f8f9fa; padding: 8px 12px; border-left: 5px solid #008080; border-radius: 4px; font-weight: bold; color: #333; }
</style>""", unsafe_allow_html=True)

# Lógica de Inicialização
if "idx" not in st.session_state: 
    st.session_state.idx = 0
    st.session_state.last_time = time.time()
    st.session_state.novo_ciclo = True

# --- LÓGICA DE ÁUDIO E ÍCONES ---
JS_MOTOR_AUDIO = """
function anunciarBase(texto) {
    let synth = window.parent.speechSynthesis;
    try { synth.cancel(); } catch(e) {}
    let m = new SpeechSynthesisUtterance(texto); m.lang = 'pt-BR'; synth.speak(m);
}
"""
icone_mudo = '<div style="position: fixed; bottom: 20px; left: 20px; opacity: 0.2;"><svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#666" stroke-width="2"><path d="M11 5L6 9H2v6h4l5 4zM23 9l-6 6M17 9l6 6"/></svg></div>'
icone_ativo = '<div style="position: fixed; bottom: 20px; left: 20px; opacity: 0.8;"><svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#2e7d32" stroke-width="2"><path d="M11 5L6 9H2v6h4l5 4zM19.07 4.93a10 10 0 0 1 0 14.14"/></svg></div>'

# --- ROTINA DE ROTAÇÃO (Telas 0, 1, 2, 3, 5, 6) ---
espera = 60
if time.time() - st.session_state.last_time > espera:
    st.session_state.idx = (st.session_state.idx + 1) % 6
    st.session_state.last_time = time.time()
    st.rerun()

# =========================================================================
# RENDERIZAÇÃO DAS TELAS
# =========================================================================
CONTEUDO_TV = st.empty()
with CONTEUDO_TV.container():
    
    # [Telas 0, 1, 2, 3 permanecem iguais às suas originais...]
    
    # TELA 5: Performance Consultivo Mensal
    if st.session_state.idx == 4: # Ajuste o índice conforme seu ciclo
         st.markdown(f'''<div class="topo-container"><div class="topo-centro">PERFORMANCE CONSULTIVO</div></div>''', unsafe_allow_html=True)
         # (Seu código original da tela 5)
    
    # TELA 6: Performance Consultivo Diário (NOVA)
    elif st.session_state.idx == 5:
        st.markdown(f'''<div class="topo-container">
            <div class="topo-esquerda">{logo_html}</div>
            <div class="topo-centro">PERFORMANCE CONSULTIVO DIÁRIO</div>
            <div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div>
        </div>{icone_ativo}''', unsafe_allow_html=True)

        if os.path.exists(ARQUIVO_CONSULTIVO):
            df = pd.read_csv(ARQUIVO_CONSULTIVO, sep=None, engine='python', dtype=str)
            df.columns = [str(c).upper().replace(' ', '_') for c in df.columns]
            df['SUPERVISOR'] = df['SUPERVISOR'].fillna('#N/D').apply(limpar_texto)
            df['BASE'] = df['BASE'].fillna('N/D').apply(limpar_texto)
            
            df_cards = df[df['SUPERVISOR'] != 'DESCARTADO'].copy()
            hoje = datetime.utcnow() - timedelta(hours=3)
            df_hoje = df_cards[pd.to_datetime(df_cards['DATA'], dayfirst=True).dt.strftime('%d/%m/%Y') == hoje.strftime('%d/%m/%Y')]

            _, num_dias = calendar.monthrange(hoje.year, hoje.month)
            dias_restantes = sum(1 for d in range(hoje.day, num_dias + 1) if calendar.weekday(hoje.year, hoje.month, d) != 6)
            if dias_restantes == 0: dias_restantes = 1

            col_abc, col_sp = st.columns(2)
            for base, col in [('ABC', col_abc), ('SP', col_sp)]:
                with col:
                    sups = SUPS_ABC if base == 'ABC' else SUPS_SP
                    for s in sups:
                        qtd_mes = df_cards[df_cards['SUPERVISOR'].str.contains(s.split()[0]) & (df_cards['BASE'] == base)]['QTD_PRODUTOS'].astype(float).sum()
                        qtd_hoje = df_hoje[df_hoje['SUPERVISOR'].str.contains(s.split()[0]) & (df_hoje['BASE'] == base)]['QTD_PRODUTOS'].astype(float).sum()
                        
                        falta_mes = max(0, 350 - qtd_mes)
                        meta_dia = round(falta_mes / dias_restantes, 1)
                        falta_hoje = round(max(0, meta_dia - qtd_hoje), 1)

                        st.markdown(f'''
                        <div class="sup-card">
                            <div class="sup-header"><div class="sup-name">📋 {obter_nome_visual(s)}</div><div class="badge-faltas">Acumulado: {qtd_mes}</div></div>
                            <div class="faltas-grid">
                                <div class="falta-box" style="background-color: #e8f5e9;"><div class="falta-label">📦 HOJE</div><div class="falta-value">{qtd_hoje}</div></div>
                                <div class="falta-box" style="background-color: #ffebee;"><div class="falta-label">📉 FALTAM</div><div class="falta-value">{falta_hoje}</div></div>
                                <div class="falta-box" style="background-color: #fff8e1;"><div class="falta-label">🎯 META DIA</div><div class="falta-value">{meta_dia}</div></div>
                            </div>
                        </div>''', unsafe_allow_html=True)

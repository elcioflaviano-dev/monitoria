import streamlit as st
import pandas as pd
import numpy as np
import os
import time
import base64
import calendar
import unicodedata
import requests
import io
import pydeck as pdk
from datetime import datetime, timedelta

# =========================================================================
# CONFIGURAÇÕES E PARÂMETROS OPERACIONAIS 🚀
# =========================================================================
ROOT_DIR = os.getcwd()
ARQUIVO_ROTA_DISCO = os.path.join(ROOT_DIR, "rota_sincronizada.csv")
ARQUIVO_CONSULTIVO = os.path.join(ROOT_DIR, "consultivo_sincronizado.csv")
URL_PLANILHA_MASTER = "https://totaltecnologia-my.sharepoint.com/:x:/g/personal/elcio_nunes_totaltecnologia_onmicrosoft_com/IQBPzXoLVti8RJTgULiXf-nQAcrWXLiLMfks1IgJPO4nJeg?download=1"

ARQUIVO_LOGO = os.path.join(ROOT_DIR, "logo.png")
if not os.path.exists(ARQUIVO_LOGO):
    ARQUIVO_LOGO = os.path.join(ROOT_DIR, "pages", "logo.png")

# 📌 QUANTIDADE FIXA DE TÉCNICOS DA ROTA DOS MONTADOS (TELA 10)
QTD_TECNICOS_MONTADOS = {
    "EDSON MARCO": 24,
    "MAICON": 23,
    # "MARCOS ROBERTO": 15,
    "NELSON": 24
}

# --- REGRAS GLOBAIS DE SUPERVISORES ---
SUPS_ABC = ["EDSON MARCO", "MAICON", "NELSON"]
SUPERVISORES_ORDENADOS = SUPS_ABC

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Inicialização segura dos estados da sessão
if "idx" not in st.session_state: 
    st.session_state.idx = 0          
    st.session_state.prox_idx = 0

if "ultimo_audio_base" not in st.session_state:
    st.session_state.ultimo_audio_base = 0

# =========================================================================
# 🧭 SISTEMA DE ROTEAMENTO POR URL (LINKS ESPECÍFICOS)
# =========================================================================
modo_estatico = False
try:
    params = st.query_params
    tela_url = params.get("tela", None)
except AttributeError:
    params = st.experimental_get_query_params()
    tela_url = params.get("tela", [None])[0]

if tela_url:
    tela_url = str(tela_url).lower()
    if tela_url == "geral": st.session_state.idx = 9
    elif tela_url == "fixa": st.session_state.idx = 10
    elif tela_url == "pme": st.session_state.idx = 8
    elif tela_url == "gpon": st.session_state.idx = 7
    elif tela_url == "tec1": st.session_state.idx = 1
    elif tela_url == "consultivo": st.session_state.idx = 5
    elif tela_url == "diario": st.session_state.idx = 6
    modo_estatico = True

if "ticker_data" not in st.session_state:
    st.session_state.ticker_data = {}

if "ultima_sincronizacao" not in st.session_state:
    st.session_state.ultima_sincronizacao = time.time()

# =========================================================================
# MOTOR DE SINCRONIZAÇÃO AUTÔNOMA DA TV (5 EM 5 MINUTOS) ☁️
# =========================================================================
def baixar_dados_nuvem_background():
    try:
        headers = {'User-Agent': 'Mozilla/5.0', 'Accept': '*/*'}
        sessao = requests.Session()
        resposta = sessao.get(URL_PLANILHA_MASTER, headers=headers, allow_redirects=True, timeout=20)
        
        if resposta.status_code == 200:
            ficheiro_excel = io.BytesIO(resposta.content)
            try:
                df_cons_bruto = pd.read_excel(ficheiro_excel, sheet_name='CONSULTIVO', engine='openpyxl')
                if not df_cons_bruto.empty:
                    df_cons_bruto.columns = [str(c).strip().replace('\xa0', ' ') for c in df_cons_bruto.columns]
                    df_cons_bruto.to_csv(ARQUIVO_CONSULTIVO, index=False)
            except: pass

            ficheiro_excel.seek(0)
            try:
                df_bruto = pd.read_excel(ficheiro_excel, sheet_name='ROTA', engine='openpyxl')
                if not df_bruto.empty:
                    df_bruto.columns = [str(c).strip().replace('\xa0', ' ') for c in df_bruto.columns]
                    cols_sup = [c for c in df_bruto.columns if 'SUPERV' in str(c).upper()]
                    valores_supervisor = df_bruto[cols_sup[-1]].values if cols_sup else None
                    
                    colunas_mapeadas = {}
                    for col in list(df_bruto.columns):
                        col_upper = str(col).upper()
                        if col_upper in ['LOGIN DO TÉCNICO', 'LOGIN DO TECNICO', 'LOGIN']: colunas_mapeadas[col] = 'Login do Técnico'
                        elif 'STATUS' in col_upper and 'ATIVIDADE' in col_upper: colunas_mapeadas[col] = 'Status da Atividade'
                        elif 'TIPO' in col_upper and 'ATIVIDADE' in col_upper:
                            if '3' in col_upper: colunas_mapeadas[col] = 'Tipo de Atividade3'
                            else: colunas_mapeadas[col] = 'Tipo de Atividade'
                        elif col_upper in ['RECURSO', 'RECURS', 'TECNICO', 'NOME', 'TÉCNICO']: colunas_mapeadas[col] = 'Recurso'
                        elif 'TOTAL DE TAREFAS' in col_upper: colunas_mapeadas[col] = 'QTD_OS_COL'
                    
                    df_final = df_bruto.rename(columns=colunas_mapeadas)
                    df_final = df_final.loc[:, ~df_final.columns.duplicated(keep='first')]
                    
                    if valores_supervisor is not None: df_final['SUPERVISOR'] = valores_supervisor
                    else: df_final['SUPERVISOR'] = 'NÃO IDENTIFICADO'

                    df_final['SUPERVISOR'] = df_final['SUPERVISOR'].fillna('NÃO IDENTIFICADO').astype(str).str.strip().str.upper()
                    df_final['SUPERVISOR'] = df_final['SUPERVISOR'].replace(['NAN', 'N/A', 'NULL', '', '-', '0', '0.0'], 'NÃO IDENTIFICADO')

                    if 'Recurso' not in df_final.columns and 'Login do Técnico' in df_final.columns:
                        df_final['Recurso'] = df_final['Login do Técnico']

                    df_final.to_csv(ARQUIVO_ROTA_DISCO, index=False)
            except: pass
    except: pass


def carregar_logo_html(caminho_imagem):
    if os.path.exists(caminho_imagem):
        try:
            with open(caminho_imagem, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f'<img src="data:image/png;base64,{encoded_string}" style="height: 100px; width: auto; object-fit: contain; display: block;">'
        except: return '<div></div>'
    return '<div></div>'

logo_html = carregar_logo_html(ARQUIVO_LOGO)

def render_topo(titulo):
    return f'''<div class="topo-container">
        <div class="topo-esquerda">{logo_html}</div>
        <div class="topo-centro">{titulo}</div>
        <div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div>
    </div>'''

st.markdown("""<style>
    .block-container { padding-top: 0.5rem !important; padding-bottom: 50px !important; max-width: 98% !important; }
    ::-webkit-scrollbar { display: none !important; }
    html, body { -ms-overflow-style: none !important; scrollbar-width: none !important; overflow: hidden !important; }

    .viewerBadge_container, .viewerBadge_link, [data-testid="viewerBadge"], #viewerBadge { display: none !important; }
    [data-testid="stHeader"], .stDeployButton, footer, #MainMenu, [data-testid="stSidebar"] { display: none !important; visibility: hidden !important; }
    .stApp { background-color: #ffffff !important; }
    
    .topo-container { background: #003366; color: white; padding: 0px 20px; border-radius: 0 0 10px 10px; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; margin-bottom: 10px; height: 75px; }
    .topo-esquerda { display: flex; justify-content: flex-start; align-items: center; height: 100%; }
    .topo-centro { font-size: 35px; font-weight: 900; text-align: center; white-space: nowrap; }
    .topo-direita { display: flex; justify-content: flex-end; align-items: center; }
    .botao-home { color: #fff; font-size: 16px; font-weight: bold; border: 2px solid #fff; padding: 6px 12px; border-radius: 5px; text-decoration: none; }
    
    .st-key-btn_anterior { position: fixed !important; bottom: 65px !important; left: 20px !important; z-index: 999999 !important; width: auto !important; }
    .st-key-btn_proxima, .st-key-btn_atualizar_estatico { position: fixed !important; bottom: 65px !important; right: 20px !important; z-index: 999999 !important; width: auto !important; }
    
    .st-key-btn_anterior button, .st-key-btn_proxima button, .st-key-btn_atualizar_estatico button { 
        background-color: #003366 !important; color: #ffffff !important; border: 2px solid #ffffff !important; border-radius: 30px !important; padding: 6px 15px !important; font-size: 15px !important; font-weight: bold !important; opacity: 0.03 !important; transition: all 0.4s ease-in-out !important; 
    }
    .st-key-btn_anterior button:hover, .st-key-btn_proxima button:hover, .st-key-btn_atualizar_estatico button:hover { 
        opacity: 1.0 !important; background-color: #ff9800 !important; border-color: #ffffff !important; transform: scale(1.05) !important; 
    }

    [data-testid="stDeckGlJsonChart"] { height: 72vh !important; min-height: 550px !important; border-radius: 12px; box-shadow: 2px 2px 10px rgba(0,0,0,0.15); }

    .box-base { background: #e8f5e9; border-left: 10px solid #2e7d32; padding: 8px 10px; text-align: center; border-radius: 10px; box-shadow: 2px 2px 8px rgba(0,0,0,0.15); margin-bottom: 10px; }
    .nome-base { font-size: 28px !important; font-weight: 900; color: #2e7d32; text-transform: uppercase; margin-bottom: 2px; }
    .num-base { font-size: 80px !important; font-weight: 900; color: #111; line-height: 1; }
    
    .sup-card { background: #ffffff; border: 2px solid #e0e0e0; border-radius: 10px; padding: 15px; margin-bottom: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.08); }
    .sup-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-bottom: 15px; }
    .sup-name { font-size: 30px !important; font-weight: 900; color: #333; text-transform: uppercase; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}
    .badge-faltas { background: #ffebee; color: #c62828; padding: 6px 15px; border-radius: 8px; font-size: 20px !important; font-weight: 900; border: 2px solid #ffcdd2; }
    .faltas-grid { display: flex; justify-content: space-between; gap: 12px; }
    .falta-box { background-color: #ffebee; border: 2px solid #ffcdd2; border-radius: 8px; padding: 10px 5px; text-align: center; margin-bottom: 0px; flex: 1; }
    .falta-label { font-size: 15px !important; font-weight: bold; color: #c62828; text-transform: uppercase; margin-bottom: 5px; }
    .falta-value { font-size: 55px !important; font-weight: 900; color: #b30000; line-height: 1; }
    
    .box-contagem { background: #ffffff; border: 2px solid #e0e0e0; border-left: 12px solid #cc6600; padding: 15px; border-radius: 12px; box-shadow: 2px 2px 8px rgba(0,0,0,0.1); margin-bottom: 15px; position: relative; z-index: 1; transition: 0.3s; }
    .box-nome { font-size: 35px !important; font-weight: 900; color: #003366; text-transform: uppercase; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; text-align: center; }
    .destaque-ativo { transform: scale(1.05) !important; box-shadow: 0px 15px 30px rgba(204, 102, 0, 0.4) !important; border-left: 18px solid #ff8800 !important; background: #fff8e1 !important; z-index: 9999 !important; }
    
    .relogio-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 70vh; background-color: #ffffff; width: 100%; }
    .hora-gigante { font-size: 220px; font-weight: 900; color: #003366; text-shadow: 4px 4px 10px rgba(0,0,0,0.1); line-height: 1; letter-spacing: 5px; }
    .data-media { font-size: 50px; color: #666; font-weight: bold; margin-top: -20px; }
    .tec-base-nome { background: #f8f9fa; padding: 12px 15px; border-left: 6px solid #008080; border-radius: 6px; margin-bottom: 10px; font-weight: bold; font-size: 24px !important; color: #333; box-shadow: 1px 1px 4px rgba(0,0,0,0.1); }

    .ticker-wrap { position: fixed; bottom: 0; left: 0; width: 100%; overflow: hidden; height: 50px; background-color: #002244; box-sizing: border-box; z-index: 99999; border-top: 3px solid #ff8800; display: flex; align-items: center; }
    .ticker { display: inline-block; white-space: nowrap; padding-right: 100%; box-sizing: content-box; animation: ticker 45s linear infinite; }
    .ticker__item { display: inline-block; padding: 0 15px; font-size: 20px; color: #ffffff; font-weight: 900; text-transform: uppercase; }
    @keyframes ticker { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
</style>""", unsafe_allow_html=True)

def obter_nome_visual(nome_completo):
    n = str(nome_completo).upper()
    if 'MARCOS' in n: return "MARCOS ROBERTO"
    if 'MAICON' in n: return "MAICON"
    if 'NELSON' in n: return "NELSON"
    if 'EDSON' in n: return "EDSON MARCO"
    return n.split()[0]

def limpar_texto(txt):
    if pd.isna(txt): return ''
    return unicodedata.normalize('NFKD', str(txt).strip().upper()).encode('ASCII', 'ignore').decode('utf-8')

# =========================================================================
# ⚙️ LÓGICA DE STATUS BLINDADA COM A FÓRMULA DO SEU EXCEL
# =========================================================================
def padronizar_status(row):
    status_raw = ""
    for col in ['STATUS CONTRATO', 'STATUS_TV', 'STATUS DA ATIVIDADE', 'STATUS']:
        if col in row and pd.notna(row[col]):
            status_raw = row[col]
            break
            
    val_status = limpar_texto(status_raw)
    
    col_inicio = next((c for c in row.index if c in ['INICIO', 'INÍCIO', 'HORA INICIO', 'HORA INÍCIO', 'INICIO DO DESLOCAMENTO']), None)
    tem_inicio = False
    if col_inicio and pd.notna(row[col_inicio]):
        txt_inicio = str(row[col_inicio]).strip()
        if txt_inicio not in ['', 'NAN', 'NULL', 'NONE', '-', '0', '00:00', '00:00:00']:
            tem_inicio = True
            
    col_sistema = next((c for c in row.index if 'NETSMS' in c or 'SISTEMA' in c), None)
    val_sistema = limpar_texto(row[col_sistema]) if col_sistema and pd.notna(row[col_sistema]) else ""

    eh_cancelado_liberado_sistema = ('LIBERADO' in val_sistema or 'CANCELADO' in val_sistema or 'CANCEL' in val_status or 'LIBERADO' in val_status)
    if eh_cancelado_liberado_sistema:
        if tem_inicio:
            return 'O.S NE'
        else:
            return 'Descartar'
            
    if 'NAO CONCLUIDO' in val_status or 'QUEBRA' in val_status or 'O.S NE' in val_status or val_status == 'NE':
        return 'O.S NE'
        
    if 'CANCEL' in val_status or 'SUSP' in val_status:
        return 'Descartar'
        
    if val_status in ['', 'NAN', 'NULL', 'NONE', 'VAZIO']:
        return 'Descartar'
        
    if 'PRODUTIVO' in val_status or 'CONCL' in val_status or 'EXEC' in val_status:
        return 'Produtivo'
        
    return 'Em aberto'

# =========================================================================
# LÓGICA DE ÁUDIOS E REGRAS DE HORÁRIO (FUSO BLINDADO UTC-3)
# =========================================================================
agora_br = datetime.utcnow() - timedelta(hours=3)
minutos_agora = agora_br.hour * 60 + agora_br.minute

# --- REGRAS DO HORÁRIO DA BASE (07:00 ÀS 08:30) ---
permitir_audio_base = False
frase_incisiva_base = ""
if 7*60 <= minutos_agora < 8*60 + 30:
    permitir_audio_base = True
    if minutos_agora < 7*60 + 50:
        frase_incisiva_base = "Técnicos no aguardo para conclusão de base."
    elif 7*60 + 50 <= minutos_agora < 8*60:
        frase_incisiva_base = "Horário para concluir base."
    elif 8*60 <= minutos_agora < 8*60 + 15:
        frase_incisiva_base = "Atenção para iniciar a rota."
    else:
        frase_incisiva_base = "Fim do horário para concluir base."

# --- CORREÇÃO TEC1: ÁUDIO DINÂMICO E PERSISTENTE NAS 3 JANELAS (APÓS 08:30) ---
permitir_audio_tec1 = False
frase_incisiva_tec1 = ""
for janela in [12, 15, 18]:
    inicio_aviso = (janela - 1) * 60      # 1h antes (11:00, 14:00, 17:00)
    fim_janela = janela * 60             # Término (12:00, 15:00, 18:00)
    fim_aviso_pos = janela * 60 + 59     # 1h depois (12:59, 15:59, 18:59)
    
    # 1. Avisos dinâmicos de minutos restantes (1h antes até o fechamento da janela)
    if inicio_aviso <= minutos_agora < fim_janela:
        permitir_audio_tec1 = True
        minutos_restantes = fim_janela - minutos_agora
        if minutos_restantes == 1:
            frase_incisiva_tec1 = f"Atenção. Falta 1 minuto para o término da janela das {janela} horas. Verifiquem os contratos."
        else:
            frase_incisiva_tec1 = f"Atenção. Faltam {minutos_restantes} minutos para o término da janela das {janela} horas. Verifiquem os contratos pendentes."
        break
        
    # 2. Avisos de janela estourada (1h após o término)
    elif fim_janela <= minutos_agora <= fim_aviso_pos:
        permitir_audio_tec1 = True
        frase_incisiva_tec1 = f"Atenção. O horário para baixa dos contratos da janela das {janela} horas já passou, e ainda temos contratos sem conclusão. Atenção para não perder o TEC 1."
        break

permitir_audio_ind = False
for inicio, f in [(13*60, 13*60 + 15), (16*60, 16*60 + 15)]:
    if inicio <= minutos_agora <= f:
        permitir_audio_ind = True
        break

icone_mudo = '''<div style="position: fixed; bottom: 120px; left: 20px; z-index: 9999; opacity: 0.25;" title="Áudio em Espera"><svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#666666" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><line x1="23" y1="1" x2="1" y2="23"></line></svg></div>'''
icone_ativo = '''<div style="position: fixed; bottom: 120px; left: 20px; z-index: 9999; opacity: 0.8;" title="Áudio Ativo"><svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#2e7d32" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg></div>'''
html_audio_base = icone_ativo if permitir_audio_base else icone_mudo
html_audio_tec1 = icone_ativo if permitir_audio_tec1 else icone_mudo
html_audio_ind = icone_ativo if permitir_audio_ind else icone_mudo

JS_MOTOR_AUDIO = """
function tocarAlertaChamaAtencao() {
    try { let ctx = new (window.parent.AudioContext || window.AudioContext)(); let tempo = ctx.currentTime;
        function tocarSino(f, i, d) { let osc = ctx.createOscillator(); let gain = ctx.createGain(); osc.type = 'triangle'; osc.frequency.setValueAtTime(f, i); gain.gain.setValueAtTime(0, i); gain.gain.linearRampToValueAtTime(3.0, i + 0.05); gain.gain.exponentialRampToValueAtTime(0.01, i + d); osc.connect(gain); gain.connect(ctx.destination); osc.start(i); osc.stop(i + d + 0.1); }
        tocarSino(659.25, tempo, 1.5); tocarSino(523.25, tempo + 0.4, 1.5); tocarSino(784.00, tempo + 0.8, 2.5); 
    } catch(e) {}
}
function anunciarBase(texto, delay) { setTimeout(() => { tocarAlertaChamaAtencao(); setTimeout(() => { let synth = window.parent.speechSynthesis || window.speechSynthesis; try { synth.cancel(); } catch(e) {} let m = new SpeechSynthesisUtterance(texto); m.lang = 'pt-BR'; m.rate = 1.0; m.volume = 1.0; function setVoiceAndSpeak() { let voices = synth.getVoices(); let voz = voices.find(v => v.name.includes('Luciana')) || voices.find(v => v.lang.includes('pt-BR')); if(voz) { m.voice = voz; } synth.speak(m); } if (synth.getVoices().length === 0) { synth.onvoiceschanged = setVoiceAndSpeak; } else { setVoiceAndSpeak(); } }, 2000); }, delay); }
function limparDestaques(total) { for(let j=0; j<total; j++) { let el = window.parent.document.getElementById('sup-box-' + j); if(el) { el.classList.remove('destaque-ativo'); } } }
function animarSupervisor(texto, delay, index, totalSup) { setTimeout(() => { limparDestaques(totalSup); let elAtual = window.parent.document.getElementById('sup-box-' + index); if(elAtual) { elAtual.classList.add('destaque-ativo'); } tocarAlertaChamaAtencao(); setTimeout(() => { let synth = window.parent.speechSynthesis || window.speechSynthesis; try { synth.cancel(); } catch(e) {} let m = new SpeechSynthesisUtterance(texto); m.lang = 'pt-BR'; m.rate = 1.0; m.volume = 1.0; let voices = synth.getVoices(); let voz = voices.find(v => v.name.includes('Luciana')) || voices.find(v => v.lang.includes('pt-BR')); if(voz) { m.voice = voz; } synth.speak(m); }, 2000); }, delay); }
"""

CONTEUDO_TV = st.empty()

with CONTEUDO_TV.container():

    # -------------------------------------------------------------------------
    # TELA 4: TRANSIÇÃO E SINCRONIZAÇÃO AUTOMÁTICA
    # -------------------------------------------------------------------------
    if st.session_state.idx == 4:
        st.markdown(
            """
            <div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: #ffffff; z-index: 999999; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                <h1 style="color: #003366; font-size: 50px;">🔄 Atualizando Indicadores...</h1>
            </div>
            """, unsafe_allow_html=True
        )
        if time.time() - st.session_state.ultima_sincronizacao > 300:
            st.markdown('<div style="position: fixed; top: 60%; left: 0; width: 100%; text-align: center; color: #ff9800; font-size: 24px; font-weight: bold; z-index: 999999;">Baixando dados da nuvem... ☁️</div>', unsafe_allow_html=True)
            baixar_dados_nuvem_background()
            st.session_state.ultima_sincronizacao = time.time()

    # -------------------------------------------------------------------------
    # TELA 0: BASE
    # -------------------------------------------------------------------------
    elif st.session_state.idx == 0:
        st.markdown(render_topo("🚀 TÉCNICOS COM STATUS BASE PENDENTE") + html_audio_base, unsafe_allow_html=True)
        if os.path.exists(ARQUIVO_ROTA_DISCO):
            df = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str, on_bad_lines='skip')
            df.columns = [str(c).strip().upper() for c in df.columns]
            col_recurso = next((c for c in df.columns if 'RECURSO' in c or 'NOME' in c), df.columns[0])
            col_status = next((c for c in df.columns if 'STATUS' in c), None)
            col_sup = next((c for c in df.columns if 'SUPERVISOR' in c), None)
            col_tipo_exata = next((c for c in df.columns if 'TIPO DE ATIVIDADE3' in c or 'TIPO DE ATIVIDADE 3' in c), None)

            if col_status:
                def resolver_sup_base(row):
                    sup = str(row.get(col_sup, '')).upper().strip() if col_sup else ''
                    for oficial in SUPERVISORES_ORDENADOS:
                        if oficial in sup: return oficial
                    return "DESCARTADO"

                df['SUPERVISOR_CLEAN'] = df.apply(resolver_sup_base, axis=1)
                mask_status = df[col_status].fillna('').astype(str).str.lower().str.contains('pend|aberto')
                
                if col_tipo_exata: 
                    mask_base = df[col_tipo_exata].fillna('').astype(str).str.lower().str.contains('base')
                else:
                    cols_tipo = [c for c in df.columns if 'TIPO' in c]
                    mask_base = df[cols_tipo].apply(lambda col: col.astype(str).str.lower().str.contains('base')).any(axis=1)

                df_tela = df[mask_base & mask_status & (df['SUPERVISOR_CLEAN'].isin(SUPS_ABC))].copy()
                nomes_abc = sorted([str(n).strip().upper() for n in df_tela[col_recurso].dropna().unique()])
                
                st.session_state.ticker_data[0] = f"🚀 BASE: {len(nomes_abc)} TÉCS PENDENTES"

                if len(nomes_abc) > 0:
                    cols_tec = st.columns(4)
                    for i, n in enumerate(nomes_abc):
                        with cols_tec[i % 4]: st.markdown(f'<div class="tec-base-nome">🏃‍♂️ {n}</div>', unsafe_allow_html=True)
                else:
                    st.success("✅ Excelente! Nenhum técnico pendente na base neste momento.")

                if st.session_state.novo_ciclo:
                    script_cenario = ""
                    tempo_atual = time.time()
                    if permitir_audio_base and len(nomes_abc) > 0:
                        # Define a frequência do alerta na base:
                        # Se já for depois das 07:50, alerta a cada 5 min. Antes das 07:50, alerta a cada 10 min.
                        intervalo_minimo = 300 if minutos_agora >= (7*60 + 50) else 600
                        if (tempo_atual - st.session_state.ultimo_audio_base) >= intervalo_minimo:
                            hora_texto = agora_br.strftime('%H e %M')
                            texto_final = f"Atenção. São {hora_texto}. {frase_incisiva_base} Temos {len(nomes_abc)} técnicos pendentes."
                            script_cenario = f"<script>/*{tempo_atual}*/ {JS_MOTOR_AUDIO}anunciarBase('{texto_final}', 0);</script>"
                            st.session_state.ultimo_audio_base = tempo_atual
                    
                    st.session_state.script_audio_atual = script_cenario
                    st.session_state.novo_ciclo = False 
                st.components.v1.html(st.session_state.script_audio_atual, height=0)
            else: st.error("Coluna Status não encontrada.")
        else: st.error("Ficheiro rota_sincronizada.csv não encontrado.")

    # -------------------------------------------------------------------------
    # TELA 1: TEC1 (VISÃO DIVIDIDA PENDENTES / EM ROTA / INICIADOS)
    # -------------------------------------------------------------------------
    elif st.session_state.idx == 1: 
        hora_atual = agora_br.hour
        
        if hora_atual < 13:
            label_janela = "ATÉ 12:00"
        elif 13 <= hora_atual < 16:
            label_janela = "ATÉ 15:00"
        else:
            label_janela = "ATÉ 18:00"
        
        titulo_tec1 = f'''
        <div style="display: flex; align-items: center; justify-content: center; gap: 15px;">
            <span>TEC1</span>
            <div style="background: linear-gradient(135deg, #d84315, #f57c00); border: 2px solid #ffcc80; padding: 4px 20px; border-radius: 30px; font-size: 24px; font-weight: 900; color: #ffffff; box-shadow: 0px 4px 10px rgba(0,0,0,0.2); display: flex; align-items: center; line-height: 1.2;">
                ⏳ {label_janela}
            </div>
        </div>
        '''
        
        st.markdown(render_topo(titulo_tec1) + html_audio_tec1, unsafe_allow_html=True)
        if os.path.exists(ARQUIVO_ROTA_DISCO):
            df = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str, on_bad_lines='skip')
            df.columns = [str(c).strip().upper() for c in df.columns]
            col_tecnico = 'RECURSO' if 'RECURSO' in df.columns else df.columns[0]
            col_sup = next((c for c in df.columns if 'SUPERVISOR' in c), None)
            
            def resolver_supervisor(row):
                sup = str(row.get(col_sup, '')).upper().strip() if col_sup else ''
                for oficial in SUPERVISORES_ORDENADOS:
                    if oficial in sup: return oficial
                return "DESCARTADO"

            df['SUPERVISOR_CLEAN'] = df.apply(resolver_supervisor, axis=1)
            col_status_real = next((c for c in df.columns if 'STATUS' in c), None)
            
            df_pendentes_geral = pd.DataFrame()
            if col_status_real:
                df['Status_Atividade_Upper'] = df[col_status_real].fillna('').astype(str).str.upper().str.strip()
                df_limpo = df[df['Status_Atividade_Upper'] != 'SUSPENSO'].copy()
                
                df_limpo['IS_PENDENTE'] = df_limpo['Status_Atividade_Upper'].str.contains('PENDENTE|EM ABERTO|ABERTO|PEND', na=False)
                df_limpo['IS_EM_ROTA']  = df_limpo['Status_Atividade_Upper'].str.contains('EM ROTA', na=False)
                df_limpo['IS_INICIADO'] = df_limpo['Status_Atividade_Upper'].str.contains('INICIADO', na=False)
                df_limpo['P_COUNT'] = (df_limpo['IS_PENDENTE'] | df_limpo['IS_EM_ROTA'] | df_limpo['IS_INICIADO']).astype(int)
                
                df_validos = df_limpo.copy()

                col_janela = next((c for c in df_validos.columns if 'JANELA' in str(c) or 'INTERVALO' in str(c)), None)
                if col_janela is not None and not df_validos.empty:
                    df_validos['Intervalo_Tratado'] = df_validos[col_janela].fillna('').astype(str).str.strip()
                    df_validos['Hora_Limite_Janela'] = df_validos['Intervalo_Tratado'].apply(lambda x: int(str(x).replace(':', '').split('-')[1].strip()[:2]) if '-' in str(x) else 24)
                    
                    if hora_atual < 13:
                        condicao_horario = df_validos['Hora_Limite_Janela'] <= 12
                    elif 13 <= hora_atual < 16:
                        condicao_horario = df_validos['Hora_Limite_Janela'] <= 15
                    else:
                        condicao_horario = df_validos['Hora_Limite_Janela'] <= 24
                        
                    df_pendentes_geral = df_validos[condicao_horario & (df_validos['P_COUNT'] > 0)].copy()
                else:
                    df_pendentes_geral = df_validos[df_validos['P_COUNT'] > 0].copy()

                col_contrato = next((c for c in df_pendentes_geral.columns if 'CONTRATO' in c), None)
                if col_contrato and not df_pendentes_geral.empty:
                    df_pendentes_geral[col_contrato] = df_pendentes_geral[col_contrato].fillna('').astype(str).apply(lambda x: str(x).split('.')[0])
                    df_pendentes_geral = df_pendentes_geral.drop_duplicates(subset=[col_contrato])

                df_pendentes_geral = df_pendentes_geral[df_pendentes_geral['SUPERVISOR_CLEAN'].isin(SUPS_ABC)]
                
                total_pendentes = int(df_pendentes_geral['IS_PENDENTE'].sum())
                total_em_rota   = int(df_pendentes_geral['IS_EM_ROTA'].sum())
                total_iniciados = int(df_pendentes_geral['IS_INICIADO'].sum())
                
                st.session_state.ticker_data[1] = f"⏰ TEC1: {total_pendentes} PENDENTES | {total_em_rota} EM ROTA | {total_iniciados} INICIADOS"

                st.markdown(f'''
                <div class="box-base" style="padding: 10px; display: flex; justify-content: space-around; align-items: center;">
                    <div>
                        <div class="nome-base" style="font-size: 14px !important; color: #cc6600;">PENDENTES</div>
                        <div class="num-base" style="color: #cc6600;">{total_pendentes}</div>
                    </div>
                    <div>
                        <div class="nome-base" style="font-size: 14px !important; color: #0277bd;">EM ROTA</div>
                        <div class="num-base" style="color: #0277bd;">{total_em_rota}</div>
                    </div>
                    <div>
                        <div class="nome-base" style="font-size: 14px !important; color: #2e7d32;">INICIADOS</div>
                        <div class="num-base" style="color: #2e7d32;">{total_iniciados}</div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
                for i in range(0, len(SUPS_ABC), 2):
                    cols_sub_abc = st.columns(2)
                    for j in range(2):
                        if i + j < len(SUPS_ABC):
                            idx_global = i + j
                            sup = SUPS_ABC[idx_global]
                            
                            df_sup = df_pendentes_geral[df_pendentes_geral['SUPERVISOR_CLEAN'] == sup]
                            qtd_pend = int(df_sup['IS_PENDENTE'].sum())
                            qtd_rota = int(df_sup['IS_EM_ROTA'].sum())
                            qtd_inic = int(df_sup['IS_INICIADO'].sum())
                            
                            with cols_sub_abc[j]:
                                st.markdown(f'''
                                <div id="sup-box-{idx_global}" class="box-contagem" style="padding: 15px;">
                                    <div class="box-nome" style="border-bottom: 2px solid #eee; padding-bottom: 8px; margin-bottom: 12px;">{obter_nome_visual(sup)}</div>
                                    <div style="display:flex; justify-content:space-around; align-items: center;">
                                        <div style="text-align: center;">
                                            <div style="font-size:14px; font-weight:bold; color:#cc6600;">PENDENTES</div>
                                            <div style="font-size: 45px; font-weight: 900; color: #cc6600; line-height: 1;">{qtd_pend}</div>
                                        </div>
                                        <div style="text-align: center;">
                                            <div style="font-size:14px; font-weight:bold; color:#0277bd;">EM ROTA</div>
                                            <div style="font-size: 45px; font-weight: 900; color: #0277bd; line-height: 1;">{qtd_rota}</div>
                                        </div>
                                        <div style="text-align: center;">
                                            <div style="font-size:14px; font-weight:bold; color:#2e7d32;">INICIADOS</div>
                                            <div style="font-size: 45px; font-weight: 900; color: #1b5e20; line-height: 1;">{qtd_inic}</div>
                                        </div>
                                    </div>
                                </div>''', unsafe_allow_html=True)

                if permitir_audio_tec1:
                    script_cenario = f"<script>/*{time.time()}*/\n{JS_MOTOR_AUDIO}limparDestaques({len(SUPS_ABC)});\n"
                    delay_atual = 0
                    script_cenario += f"anunciarBase('{frase_incisiva_tec1} Total de Ó S: {total_pendentes} pendentes, {total_em_rota} em rota e {total_iniciados} iniciados.', {delay_atual});\n"
                    delay_atual += 24000
                    for i, sup_full in enumerate(SUPS_ABC):
                        df_s = df_pendentes_geral[df_pendentes_geral['SUPERVISOR_CLEAN'] == sup_full]
                        q_pe = int(df_s['IS_PENDENTE'].sum())
                        q_ro = int(df_s['IS_EM_ROTA'].sum())
                        q_in = int(df_s['IS_INICIADO'].sum())
                        script_cenario += f"animarSupervisor('{obter_nome_visual(sup_full)}: {q_pe} pendentes, {q_ro} em rota e {q_in} iniciados.', {delay_atual}, {i}, {len(SUPS_ABC)});\n"
                        delay_atual += 18000
                    script_cenario += f"setTimeout(() => limparDestaques({len(SUPS_ABC)}) , {delay_atual});\n</script>"
                else:
                    script_cenario = ""
                st.components.v1.html(script_cenario, height=0)
            else: st.error("Coluna Status não encontrada.")
        else: st.error("Ficheiro rota_sincronizada.csv não encontrado.")

    # -------------------------------------------------------------------------
    # TELAS 11, 12, 13, 14, 15, 16: MAPAS DA OPERAÇÃO 🗺️
    # -------------------------------------------------------------------------
    elif st.session_state.idx in [11, 12, 13, 14, 15, 16]:
        titulos_mapa = {
            11: "MAPA DA ROTA - SÃO BERNARDO DO CAMPO",
            12: "MAPA DA ROTA - SANTO ANDRÉ",
            13: "MAPA DA ROTA - DIADEMA",
            14: "MAPA DA ROTA - EDSON MARCO",
            15: "MAPA DA ROTA - MAICON",
            16: "MAPA DA ROTA - NELSON"
        }
        
        st.markdown(render_topo(titulos_mapa[st.session_state.idx]) + icone_mudo, unsafe_allow_html=True)

        if os.path.exists(ARQUIVO_ROTA_DISCO):
            df_rota = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str, on_bad_lines='skip')
            df_rota.columns = [str(c).strip().upper() for c in df_rota.columns]
            
            col_sup = next((c for c in df_rota.columns if 'SUPERVISOR' in c), None)
            col_x = next((c for c in df_rota.columns if 'COORDENADA X' in c or 'LONG' in c), None)
            col_y = next((c for c in df_rota.columns if 'COORDENADA Y' in c or 'LATI' in c), None)
            col_tec = next((c for c in df_rota.columns if 'RECURSO' in c or 'NOME' in c), df_rota.columns[0])
            col_cidade = next((c for c in df_rota.columns if 'CIDADE' in c), None)
            
            if col_sup and col_x and col_y:
                if col_cidade:
                    df_rota = df_rota[df_rota[col_cidade].notna()]
                    cond_cidade_base = df_rota[col_cidade].astype(str).str.upper().str.contains('DIADEMA|SANTO ANDRE|BERNARDO|SBC', regex=True)
                    df_rota = df_rota[cond_cidade_base]

                df_rota['STATUS_PADRAO'] = df_rota.apply(padronizar_status, axis=1)
                df_rota = df_rota[df_rota['STATUS_PADRAO'] == 'Em aberto']

                def class_sup_mapa(row):
                    sup = str(row.get(col_sup, '')).upper().strip() if col_sup else ''
                    for oficial in SUPERVISORES_ORDENADOS:
                        if oficial in sup: return oficial
                    return "DESCARTADO"
                
                df_rota['SUPERVISOR_CLEAN'] = df_rota.apply(class_sup_mapa, axis=1)
                df_mapa = df_rota[df_rota['SUPERVISOR_CLEAN'] != "DESCARTADO"].copy()
                
                df_mapa['LAT'] = pd.to_numeric(df_mapa[col_y].astype(str).str.replace(',', '.'), errors='coerce')
                df_mapa['LON'] = pd.to_numeric(df_mapa[col_x].astype(str).str.replace(',', '.'), errors='coerce')
                df_mapa = df_mapa.dropna(subset=['LAT', 'LON'])
                df_mapa['NOME_TECNICO'] = df_mapa[col_tec].fillna('Desconhecido').astype(str).apply(lambda x: x.split()[0].upper())
                
                def cor_sup_rgb(sup):
                    if sup == "MAICON": return [255, 20, 147] 
                    if sup == "NELSON": return [0, 128, 0]    
                    if sup == "EDSON MARCO": return [128, 0, 128] 
                    return [0, 0, 0]
                    
                df_mapa['COLOR_RGB'] = df_mapa['SUPERVISOR_CLEAN'].apply(cor_sup_rgb)
                
                if st.session_state.idx == 11: df_mapa = df_mapa[df_mapa[col_cidade].astype(str).str.upper().str.contains('BERNARDO|SBC', regex=True)]
                elif st.session_state.idx == 12: df_mapa = df_mapa[df_mapa[col_cidade].astype(str).str.upper().str.contains('SANTO ANDRE', regex=True)]
                elif st.session_state.idx == 13: df_mapa = df_mapa[df_mapa[col_cidade].astype(str).str.upper().str.contains('DIADEMA', regex=True)]
                elif st.session_state.idx == 14: df_mapa = df_mapa[df_mapa['SUPERVISOR_CLEAN'] == "EDSON MARCO"]
                elif st.session_state.idx == 15: df_mapa = df_mapa[df_mapa['SUPERVISOR_CLEAN'] == "MAICON"]
                elif st.session_state.idx == 16: df_mapa = df_mapa[df_mapa['SUPERVISOR_CLEAN'] == "NELSON"]
                    
                if not df_mapa.empty:
                    base_style = "display: flex; justify-content: center; gap: 30px; margin-bottom: 5px; font-size: 24px; font-weight: 900; color: #000000 !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);"
                    edson_html = '<div style="display: flex; align-items: center; gap: 8px;"><span style="display:inline-block; width: 20px; height: 20px; background-color: #800080; border-radius: 50%; border: 1px solid #000;"></span> EDSON MARCO</div>'
                    maicon_html = '<div style="display: flex; align-items: center; gap: 8px;"><span style="display:inline-block; width: 20px; height: 20px; background-color: #FF1493; border-radius: 50%; border: 1px solid #000;"></span> MAICON</div>'
                    nelson_html = '<div style="display: flex; align-items: center; gap: 8px;"><span style="display:inline-block; width: 20px; height: 20px; background-color: #008000; border-radius: 50%; border: 1px solid #000;"></span> NELSON</div>'

                    if st.session_state.idx in [11, 12, 13]:
                        legenda_html = '<div style="' + base_style + '">' + edson_html + maicon_html + nelson_html + '</div>'
                    elif st.session_state.idx == 14:
                        legenda_html = '<div style="' + base_style + '">' + edson_html + '</div>'
                    elif st.session_state.idx == 15:
                        legenda_html = '<div style="' + base_style + '">' + maicon_html + '</div>'
                    elif st.session_state.idx == 16:
                        legenda_html = '<div style="' + base_style + '">' + nelson_html + '</div>'
                    else:
                        legenda_html = ''

                    st.markdown(legenda_html, unsafe_allow_html=True)
                    
                    scatter_layer = pdk.Layer(
                        'ScatterplotLayer',
                        data=df_mapa,
                        get_position='[LON, LAT]',
                        get_color='COLOR_RGB',
                        get_radius=120,
                        pickable=True,
                        opacity=0.8
                    )
                    text_layer = pdk.Layer(
                        "TextLayer",
                        data=df_mapa,
                        get_position="[LON, LAT]",
                        get_text="NOME_TECNICO",
                        get_size=16,
                        get_color=[0, 0, 0],
                        get_alignment_baseline="'bottom'",
                        get_offset="[0, -15]"
                    )
                    
                    lat_min, lat_max = df_mapa['LAT'].min(), df_mapa['LAT'].max()
                    lon_min, lon_max = df_mapa['LON'].min(), df_mapa['LON'].max()
                    max_diff = max(lat_max - lat_min, lon_max - lon_min)
                    
                    if max_diff <= 0.05: zoom_dinamico = 13.5
                    elif max_diff <= 0.1: zoom_dinamico = 12.5
                    elif max_diff <= 0.2: zoom_dinamico = 11.5
                    else: zoom_dinamico = 10.5
                        
                    view_state = pdk.ViewState(
                        latitude=df_mapa['LAT'].mean(), 
                        longitude=df_mapa['LON'].mean(), 
                        zoom=zoom_dinamico, 
                        pitch=0
                    )
                    
                    r = pdk.Deck(
                        layers=[scatter_layer, text_layer], 
                        initial_view_state=view_state, 
                        map_provider='carto',
                        map_style='light',
                        tooltip={"text": "{NOME_TECNICO}\\nSupervisor: {SUPERVISOR_CLEAN}"}
                    )
                    st.pydeck_chart(r, use_container_width=True)
                else:
                    st.warning("Nenhum contrato pendente com coordenada válida encontrada para este filtro.")
            else:
                st.error("Colunas de Coordenada X, Coordenada Y ou Supervisor não encontradas.")
            st.components.v1.html("", height=0)

    # -------------------------------------------------------------------------
    # TELA 7: MIGRAÇÃO GPON
    # -------------------------------------------------------------------------
    elif st.session_state.idx == 7:
        st.markdown(render_topo("MIGRAÇÃO GPON") + icone_mudo, unsafe_allow_html=True)
        if os.path.exists(ARQUIVO_ROTA_DISCO):
            df = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str, on_bad_lines='skip')
            df.columns = [str(c).strip().upper() for c in df.columns]
            col_sup = next((c for c in df.columns if 'SUPERVISOR' in c), None)
            col_gpon = next((c for c in df.columns if 'GPON' in c), None)
            cols_os = [c for c in df.columns if 'TIPO O.S' in c or 'TIPO OS' in c or 'ATIVIDADE' in c]
            
            def class_sup(row):
                sup = str(row.get(col_sup, '')).upper().strip() if col_sup else ''
                for oficial in SUPERVISORES_ORDENADOS:
                    if oficial in sup: return oficial
                return "DESCARTADO"
            
            df['SUPERVISOR_CLEAN'] = df.apply(class_sup, axis=1)
            df_abc = df[df['SUPERVISOR_CLEAN'].isin(SUPS_ABC)].copy()
            
            if col_gpon and len(cols_os) > 0:
                df_gpon = df_abc[df_abc[col_gpon].astype(str).str.strip().str.upper() == 'SIM'].copy()
                if not df_gpon.empty:
                    df_gpon['TODAS_OS_JUNTAS'] = df_gpon[cols_os].fillna('').astype(str).agg('  '.join, axis=1).str.upper()
                    df_gpon['QTD_MIGRACAO_CALC'] = df_gpon['TODAS_OS_JUNTAS'].str.count('24 -') + df_gpon['TODAS_OS_JUNTAS'].str.count('191 -')
                    df_mig = df_gpon[df_gpon['QTD_MIGRACAO_CALC'] > 0].copy()
                    
                    if not df_mig.empty:
                        df_mig['STATUS_PADRAO'] = df_mig.apply(padronizar_status, axis=1)
                        df_mig = df_mig[df_mig['STATUS_PADRAO'] != 'Descartar'].copy()

                        df_mig['QTD_TAREFAS_NUM'] = df_mig['QTD_MIGRACAO_CALC']
                        total_geral_mig = int(df_mig['QTD_TAREFAS_NUM'].sum())
                        total_ne_mig = int(df_mig.loc[df_mig['STATUS_PADRAO'] == 'O.S NE', 'QTD_TAREFAS_NUM'].sum())
                        total_prod_mig = int(df_mig.loc[df_mig['STATUS_PADRAO'] == 'Produtivo', 'QTD_TAREFAS_NUM'].sum())
                        
                        soma_valida_mig = total_ne_mig + total_prod_mig
                        quebra_global_mig = (total_ne_mig / soma_valida_mig) * 100 if soma_valida_mig > 0 else 0
                        teto_ne_global = int(np.floor(total_geral_mig * 0.25))
                        cor_limite = "#2e7d32" if total_ne_mig <= teto_ne_global else "#c62828"
                        cor_quebra_global = "#2e7d32" if quebra_global_mig <= 25 else "#c62828"

                        st.session_state.ticker_data[7] = f"📊 GPON: {total_geral_mig} O.S. | QUEBRAS: {quebra_global_mig:.1f}%"

                        st.markdown(f'''<div class="box-base">
                            <div style="font-size: 30px; font-weight: bold; color: #111;">
                                Total de O.S.: <span style="color:#003366">{total_geral_mig}</span> | Quebras Geral: <span style="color:{cor_quebra_global}">{quebra_global_mig:.1f}%</span> | Permitido: <span style="color:#2e7d32">{teto_ne_global}</span> | Atuais: <span style="color:{cor_limite}">{total_ne_mig}</span>
                            </div></div>''', unsafe_allow_html=True)
                        
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
                                        
                                        st.markdown(f'''<div class="sup-card"><div class="sup-header"><div class="sup-name">📋 {obter_nome_visual(sup)}</div>
                                        <div style="background: #f3f3f3; color: {cor_quebra}; border: 3px solid {cor_quebra}; padding: 5px 15px; border-radius: 8px; font-size: 22px; font-weight: 900;">Quebra: {quebra:.1f}%</div></div>
                                        <div class="faltas-grid"><div class="falta-box"><div class="falta-label">⏳ ABERTO</div><div class="falta-value" style="color: #b78103;">{qtd_aberto}</div></div>
                                        <div class="falta-box" style="border-color: #a5d6a7;"><div class="falta-label" style="color: #2e7d32;">✅ PROD.</div><div class="falta-value" style="color: #1b5e20;">{qtd_produtivo}</div></div>
                                        <div class="falta-box"><div class="falta-label">❌ QUEBRA</div><div class="falta-value">{qtd_ne}</div></div></div></div>''', unsafe_allow_html=True)
                                        
                        if st.session_state.novo_ciclo:
                            texto_audio = f"Atenção para a Migração G PON. A quebra geral está em {quebra_global_mig:.1f} por cento. O limite é de 25 por cento. Podemos ter até {teto_ne_global} quebras de O.S., e no momento temos {total_ne_mig}."
                            st.session_state.script_audio_atual = f"<script>/*{time.time()}*/ {JS_MOTOR_AUDIO}anunciarBase('{texto_audio}', 0);</script>"
                            st.session_state.novo_ciclo = False 
                        st.components.v1.html(st.session_state.script_audio_atual, height=0)
        else: st.error("Ficheiro rota_sincronizada.csv não encontrado.")

    # -------------------------------------------------------------------------
    # TELA 8: PME 
    # -------------------------------------------------------------------------
    elif st.session_state.idx == 8:
        st.markdown(render_topo("P M E") + icone_mudo, unsafe_allow_html=True)
        if os.path.exists(ARQUIVO_ROTA_DISCO):
            df = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str, on_bad_lines='skip')
            df.columns = [str(c).strip().upper() for c in df.columns]
            col_sup = next((c for c in df.columns if 'SUPERVISOR' in c), None)
            col_cat = next((c for c in df.columns if 'CATEGORIAS DA CAPACIDADE' in c or 'CAPACIDADE' in c), None)
            col_os = next((c for c in df.columns if 'TIPO O.S 1' in c or 'TIPO O.S' in c or 'TIPO OS' in c), None)
            col_tarefas = next((c for c in df.columns if 'TAREFA' in c.upper() or 'QTD' in c.upper()), None)
            
            def class_sup(row):
                sup = str(row.get(col_sup, '')).upper().strip() if col_sup else ''
                for oficial in SUPERVISORES_ORDENADOS:
                    if oficial in sup: return oficial
                return "DESCARTADO"
            
            df['SUPERVISOR_CLEAN'] = df.apply(class_sup, axis=1)
            df_abc = df[df['SUPERVISOR_CLEAN'].isin(SUPS_ABC)].copy()
            
            if col_cat and col_os:
                cond_cat = df_abc[col_cat].astype(str).str.upper().str.contains('PME', na=False)
                str_os = df_abc[col_os].astype(str).str.upper()
                cond_os = str_os.str.contains('1 - ADES', na=False) | str_os.str.contains('51 - ADES', na=False) | str_os.str.contains('516 - ADES', na=False)
                df_pme = df_abc[cond_cat & cond_os].copy()
                
                if not df_pme.empty:
                    df_pme['STATUS_PADRAO'] = df_pme.apply(padronizar_status, axis=1)
                    df_pme = df_pme[df_pme['STATUS_PADRAO'] != 'Descartar'].copy()
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

                    st.session_state.ticker_data[8] = f"📊 PME: {total_geral_pme} O.S. | QUEBRAS: {quebra_global_pme:.1f}%"

                    st.markdown(f'''<div class="box-base">
                        <div style="font-size: 30px; font-weight: bold; color: #111;">
                            Total de O.S.: <span style="color:#003366">{total_geral_pme}</span> | Quebra Geral: <span style="color:{cor_quebra_global}">{quebra_global_pme:.1f}%</span> | Permitido: <span style="color:#2e7d32">{teto_ne_global}</span> | Atuais: <span style="color:{cor_limite}">{total_ne_pme}</span>
                        </div></div>''', unsafe_allow_html=True)
                    
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
                                    
                                    st.markdown(f'''<div class="sup-card"><div class="sup-header"><div class="sup-name">📋 {obter_nome_visual(sup)}</div>
                                    <div style="background: #f3f3f3; color: {cor_quebra}; border: 3px solid {cor_quebra}; padding: 5px 15px; border-radius: 8px; font-size: 22px; font-weight: 900;">Quebra: {quebra:.1f}%</div></div>
                                    <div class="faltas-grid"><div class="falta-box"><div class="falta-label">⏳ ABERTO</div><div class="falta-value" style="color: #b78103;">{qtd_aberto}</div></div>
                                    <div class="falta-box" style="border-color: #a5d6a7;"><div class="falta-label" style="color: #2e7d32;">✅ PROD.</div><div class="falta-value" style="color: #1b5e20;">{qtd_produtivo}</div></div>
                                    <div class="falta-box"><div class="falta-label">❌ QUEBRA</div><div class="falta-value">{qtd_ne}</div></div></div></div>''', unsafe_allow_html=True)
                                    
                    if st.session_state.novo_ciclo:
                        texto_audio = f"Atenção para a P M Ê . A quebra geral está em {quebra_global_pme:.1f} por cento. O limite é de 20 por cento. Podemos ter até {teto_ne_global} quebras de O.S., e no momento temos {total_ne_pme}."
                        st.session_state.script_audio_atual = f"<script>/*{time.time()}*/ {JS_MOTOR_AUDIO}anunciarBase('{texto_audio}', 0);</script>"
                        st.session_state.novo_ciclo = False 
                    st.components.v1.html(st.session_state.script_audio_atual, height=0)
            else: st.error("Colunas necessárias (Categorias, Tipo OS) não encontradas no arquivo.")
        else: st.error("Ficheiro rota_sincronizada.csv não encontrado.")

    # -------------------------------------------------------------------------
    # TELA 9: VISÃO GERAL DA ROTA E PROJEÇÃO (SEM RETORNOS)
    # -------------------------------------------------------------------------
    elif st.session_state.idx == 9:
        st.markdown(render_topo("VISÃO GERAL DA ROTA - TÉCNICOS ESCALADOS") + html_audio_ind, unsafe_allow_html=True)

        if os.path.exists(ARQUIVO_ROTA_DISCO):
            df_rota = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str, on_bad_lines='skip')
            df_rota.columns = [str(c).strip().upper() for c in df_rota.columns]

            col_tecnico = next((c for c in df_rota.columns if 'RECURSO' in c or 'NOME' in c), df_rota.columns[0])
            col_sup = next((c for c in df_rota.columns if 'SUPERVISOR' in c), None)
            col_tipo_os = next((c for c in df_rota.columns if 'TIPO DE ATIVIDADE3' in c or 'TIPO DE ATIVIDADE 3' in c or 'ATIVIDADE3' in c), None)
            if not col_tipo_os: col_tipo_os = next((c for c in df_rota.columns if 'TIPO O.S' in c or 'ATIVIDADE' in c), None)
            col_tarefas = next((c for c in df_rota.columns if 'TAREFA' in c or 'QTD' in c), None)

            df_proj = df_rota.copy()

            def class_sup_9(row):
                sup = str(row.get(col_sup, '')).upper().strip() if col_sup else ''
                for oficial in SUPERVISORES_ORDENADOS:
                    if oficial in sup: return oficial
                return "DESCARTADO"

            df_proj['SUPERVISOR_CLEAN'] = df_proj.apply(class_sup_9, axis=1)
            
            # --- RETORNO EXCLUÍDO DA SOMA ---
            if col_tipo_os:
                df_proj = df_proj[~df_proj[col_tipo_os].astype(str).str.upper().str.contains('RETORNO', na=False)]

            df_proj['STATUS_PADRAO'] = df_proj.apply(padronizar_status, axis=1)
            df_proj = df_proj[df_proj['STATUS_PADRAO'] != 'Descartar']

            if col_tarefas:
                df_proj['VALOR_TAREFA'] = pd.to_numeric(df_proj[col_tarefas].astype(str).str.replace(',', '.').str.strip(), errors='coerce').fillna(0)
                if df_proj['VALOR_TAREFA'].sum() == 0 and len(df_proj) > 0: df_proj['VALOR_TAREFA'] = 1
            else: df_proj['VALOR_TAREFA'] = 1

            df_abc_proj = df_proj[df_proj['SUPERVISOR_CLEAN'].isin(SUPS_ABC)]
            
            total_tarefas_op = df_abc_proj['VALOR_TAREFA'].sum()
            os_ne_op = df_abc_proj.loc[df_abc_proj['STATUS_PADRAO'] == 'O.S NE', 'VALOR_TAREFA'].sum()
            produtivo_op = df_abc_proj.loc[df_abc_proj['STATUS_PADRAO'] == 'Produtivo', 'VALOR_TAREFA'].sum()
            em_aberto_op = df_abc_proj.loc[df_abc_proj['STATUS_PADRAO'] == 'Em aberto', 'VALOR_TAREFA'].sum()

            total_tecnicos_op = df_abc_proj[col_tecnico].nunique() if col_tecnico in df_abc_proj.columns else 1
            if total_tecnicos_op == 0: total_tecnicos_op = 1

            denom_quebra_op = os_ne_op + produtivo_op
            quebra_op = (os_ne_op / denom_quebra_op) * 100 if denom_quebra_op > 0 else 0
            eficiencia_op = (produtivo_op / denom_quebra_op) * 100 if denom_quebra_op > 0 else 100
            projecao_op = produtivo_op + (em_aberto_op * (eficiencia_op / 100))
            
            os_reais_op = produtivo_op + em_aberto_op
            media_equipe_op = os_reais_op / total_tecnicos_op if total_tecnicos_op > 0 else 0

            cor_q_op = "#c62828" if quebra_op > 20.0 else "#2e7d32"

            st.session_state.ticker_data[9] = f"🌍 GERAL: {int(total_tarefas_op)} O.S. | PROJ: {int(round(projecao_op))} | QUEBRAS: {quebra_op:.1f}%"

            st.markdown(f'''
            <div class="box-base" style="padding: 10px; border-left: 15px solid #003366; background: #e3f2fd;">
                <div style="display: flex; justify-content: space-around; align-items: center; background: #ffffff; padding: 10px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 8px;">
                    <div style="text-align: center;">
                        <div style="font-size: 16px; font-weight: bold; color: #666;">TOTAL DE O.S.</div>
                        <div style="font-size: 45px; font-weight: 900; color: #003366; line-height: 1;">{int(total_tarefas_op)}</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 16px; font-weight: bold; color: #666;">PROJEÇÃO</div>
                        <div style="font-size: 45px; font-weight: 900; color: #00838f; line-height: 1;">{int(round(projecao_op))}</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 16px; font-weight: bold; color: #666;">EFICIÊNCIA</div>
                        <div style="font-size: 45px; font-weight: 900; color: #2e7d32; line-height: 1;">{eficiencia_op:.1f}%</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 16px; font-weight: bold; color: #666;">QUEBRAS</div>
                        <div style="font-size: 45px; font-weight: 900; color: {cor_q_op}; line-height: 1;">{quebra_op:.1f}%</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 16px; font-weight: bold; color: #666;">MÉDIA / TÉC</div>
                        <div style="font-size: 45px; font-weight: 900; color: #e65100; line-height: 1;">{media_equipe_op:.2f}</div>
                    </div>
                </div>
                <div style="font-size: 20px; color: #444; font-weight: bold; display: flex; justify-content: center; gap: 40px; text-transform: uppercase;">
                    <span>⏳ ABERTO: <span style="color:#b78103;">{int(em_aberto_op)}</span></span>
                    <span>✅ PRODUTIVO: <span style="color:#1b5e20;">{int(produtivo_op)}</span></span>
                    <span>❌ QUEBRAS: <span style="color:#b30000;">{int(os_ne_op)}</span></span>
                    <span>👷 TÉCNICOS: <span style="color:#003366;">{total_tecnicos_op}</span></span>
                </div>
            </div>
            ''', unsafe_allow_html=True)

            for i in range(0, len(SUPS_ABC), 2):
                cols_sup = st.columns(2)
                for j in range(2):
                    if i + j < len(SUPS_ABC):
                        sup = SUPS_ABC[i + j]
                        with cols_sup[j]:
                            df_sup = df_abc_proj[df_abc_proj['SUPERVISOR_CLEAN'] == sup]

                            total_tarefas = df_sup['VALOR_TAREFA'].sum()
                            os_ne = df_sup.loc[df_sup['STATUS_PADRAO'] == 'O.S NE', 'VALOR_TAREFA'].sum()
                            produtivo = df_sup.loc[df_sup['STATUS_PADRAO'] == 'Produtivo', 'VALOR_TAREFA'].sum()
                            em_aberto = df_sup.loc[df_sup['STATUS_PADRAO'] == 'Em aberto', 'VALOR_TAREFA'].sum()

                            total_tecnicos = df_sup[col_tecnico].nunique() if col_tecnico in df_sup.columns else 1
                            if total_tecnicos == 0: total_tecnicos = 1

                            os_reais = produtivo + em_aberto
                            media_equipe = os_reais / total_tecnicos if total_tecnicos > 0 else 0

                            denom_quebra = os_ne + produtivo
                            quebra = (os_ne / denom_quebra) * 100 if denom_quebra > 0 else 0
                            eficiencia = (produtivo / denom_quebra) * 100 if denom_quebra > 0 else 100
                            projecao = produtivo + (em_aberto * (eficiencia / 100))

                            cor_q = "#c62828" if quebra > 20.0 else "#2e7d32"

                            st.markdown(f'''
                            <div class="sup-card">
                                <div class="sup-header">
                                    <div class="sup-name">📋 {obter_nome_visual(sup)}</div>
                                    <div style="display: flex; gap: 8px; align-items: center;">
                                        <div style="background: #f8f9fa; color: #333; border: 1px solid #ccc; padding: 4px 10px; border-radius: 8px; font-size: 16px; font-weight: bold;">O.S.: {int(total_tarefas)}</div>
                                        <div style="background: #ffebee; color: {cor_q}; border: 1px solid {cor_q}; padding: 4px 10px; border-radius: 8px; font-size: 16px; font-weight: bold;">Quebra: {quebra:.1f}%</div>
                                        <div style="background: #e3f2fd; color: #006064; border: 1px solid #006064; padding: 4px 10px; border-radius: 8px; font-size: 16px; font-weight: bold;">Média: {media_equipe:.2f}</div>
                                    </div>
                                </div>
                                <div class="faltas-grid">
                                    <div class="falta-box" style="background-color: #fff8e1; border-color: #ffe082;">
                                        <div class="falta-label" style="color: #b78103;">ABERTO</div>
                                        <div class="falta-value" style="color: #b78103;">{int(em_aberto)}</div>
                                    </div>
                                    <div class="falta-box" style="background-color: #e8f5e9; border-color: #a5d6a7;">
                                        <div class="falta-label" style="color: #2e7d32;">PROD.</div>
                                        <div class="falta-value" style="color: #1b5e20;">{int(produtivo)}</div>
                                    </div>
                                    <div class="falta-box" style="background-color: #ffebee; border-color: #ffcdd2;">
                                        <div class="falta-label" style="color: #c62828;">QUEBRAS</div>
                                        <div class="falta-value" style="color: #b30000;">{int(os_ne)}</div>
                                    </div>
                                    <div class="falta-box" style="background-color: #e0f7fa; border-color: #80deea;">
                                        <div class="falta-label" style="color: #00838f;">PROJ.</div>
                                        <div class="falta-value" style="color: #00838f;">{int(round(projecao))}</div>
                                    </div>
                                </div>
                            </div>''', unsafe_allow_html=True)
            if st.session_state.novo_ciclo:
                texto_audio_9 = f"Atenção para a Visão Geral da Rota. Temos um total de {int(total_tarefas_op)} O.S. A projeção da operação está em {int(round(projecao_op))}, com um total de {int(os_ne_op)} quebras de O.S. no momento."
                st.session_state.script_audio_atual = f"<script>/*{time.time()}*/ {JS_MOTOR_AUDIO}anunciarBase('{texto_audio_9}', 0);</script>"
                st.session_state.novo_ciclo = False
            st.components.v1.html(st.session_state.script_audio_atual, height=0)
        else: st.error("Ficheiro rota_sincronizada.csv não encontrado.")

    # -------------------------------------------------------------------------
    # TELA 10: VISÃO DA ROTA DOS MONTADOS (EQUIPE FIXA - SEM RETORNOS)
    # -------------------------------------------------------------------------
    elif st.session_state.idx == 10:
        st.markdown(render_topo("VISÃO GERAL DA ROTA - EQUIPE FIXA") + icone_mudo, unsafe_allow_html=True)

        if os.path.exists(ARQUIVO_ROTA_DISCO):
            df_rota = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str, on_bad_lines='skip')
            df_rota.columns = [str(c).strip().upper() for c in df_rota.columns]

            col_sup = next((c for c in df_rota.columns if 'SUPERVISOR' in c), None)
            col_tipo_os = next((c for c in df_rota.columns if 'TIPO DE ATIVIDADE3' in c or 'TIPO DE ATIVIDADE 3' in c or 'ATIVIDADE3' in c), None)
            if not col_tipo_os: col_tipo_os = next((c for c in df_rota.columns if 'TIPO O.S' in c or 'ATIVIDADE' in c), None)
            col_tarefas = next((c for c in df_rota.columns if 'TAREFA' in c or 'QTD' in c), None)

            df_proj = df_rota.copy()

            def class_sup_10(row):
                sup = str(row.get(col_sup, '')).upper().strip() if col_sup else ''
                for oficial in SUPERVISORES_ORDENADOS:
                    if oficial in sup: return oficial
                return "DESCARTADO"

            df_proj['SUPERVISOR_CLEAN'] = df_proj.apply(class_sup_10, axis=1)

            # --- RETORNO EXCLUÍDO DA SOMA ---
            if col_tipo_os:
                df_proj = df_proj[~df_proj[col_tipo_os].astype(str).str.upper().str.contains('RETORNO', na=False)]

            df_proj['STATUS_PADRAO'] = df_proj.apply(padronizar_status, axis=1)
            df_proj = df_proj[df_proj['STATUS_PADRAO'] != 'Descartar'].copy()

            if col_tarefas:
                df_proj['VALOR_TAREFA'] = pd.to_numeric(df_proj[col_tarefas].astype(str).str.replace(',', '.').str.strip(), errors='coerce').fillna(0)
                if df_proj['VALOR_TAREFA'].sum() == 0 and len(df_proj) > 0: df_proj['VALOR_TAREFA'] = 1
            else: df_proj['VALOR_TAREFA'] = 1

            df_abc_proj = df_proj[df_proj['SUPERVISOR_CLEAN'].isin(SUPS_ABC)]
            
            total_tarefas_op = df_abc_proj['VALOR_TAREFA'].sum()
            os_ne_op = df_abc_proj.loc[df_abc_proj['STATUS_PADRAO'] == 'O.S NE', 'VALOR_TAREFA'].sum()
            produtivo_op = df_abc_proj.loc[df_abc_proj['STATUS_PADRAO'] == 'Produtivo', 'VALOR_TAREFA'].sum()
            em_aberto_op = df_abc_proj.loc[df_abc_proj['STATUS_PADRAO'] == 'Em aberto', 'VALOR_TAREFA'].sum()

            total_tecnicos_op = sum(QTD_TECNICOS_MONTADOS.get(sup, 0) for sup in SUPS_ABC)
            if total_tecnicos_op == 0: total_tecnicos_op = 1

            denom_quebra_op = os_ne_op + produtivo_op
            quebra_op = (os_ne_op / denom_quebra_op) * 100 if denom_quebra_op > 0 else 0
            eficiencia_op = (produtivo_op / denom_quebra_op) * 100 if denom_quebra_op > 0 else 100
            projecao_op = produtivo_op + (em_aberto_op * (eficiencia_op / 100))
            
            os_reais_op = produtivo_op + em_aberto_op
            media_equipe_op = os_reais_op / total_tecnicos_op if total_tecnicos_op > 0 else 0

            cor_q_op = "#c62828" if quebra_op > 20.0 else "#2e7d32"

            st.session_state.ticker_data[10] = f"🌍 MONTADOS: {int(total_tarefas_op)} OS | PROJ: {int(round(projecao_op))} | QUEBRAS: {quebra_op:.1f}%"

            st.markdown(f'''
            <div class="box-base" style="padding: 10px 10px; margin-bottom: 15px; border-left: 10px solid #003366; background: #e3f2fd;">
                <div style="display: flex; justify-content: space-around; align-items: center; background: #ffffff; padding: 10px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 8px;">
                    <div style="text-align: center;">
                        <div style="font-size: 16px; font-weight: bold; color: #666;">TOTAL DE O.S.</div>
                        <div style="font-size: 45px; font-weight: 900; color: #003366; line-height: 1;">{int(total_tarefas_op)}</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 16px; font-weight: bold; color: #666;">PROJEÇÃO</div>
                        <div style="font-size: 45px; font-weight: 900; color: #00838f; line-height: 1;">{int(round(projecao_op))}</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 16px; font-weight: bold; color: #666;">EFICIÊNCIA</div>
                        <div style="font-size: 45px; font-weight: 900; color: #2e7d32; line-height: 1;">{eficiencia_op:.1f}%</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 16px; font-weight: bold; color: #666;">QUEBRAS</div>
                        <div style="font-size: 45px; font-weight: 900; color: {cor_q_op}; line-height: 1;">{quebra_op:.1f}%</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 16px; font-weight: bold; color: #666;">MÉDIA / TÉC</div>
                        <div style="font-size: 45px; font-weight: 900; color: #e65100; line-height: 1;">{media_equipe_op:.2f}</div>
                    </div>
                </div>
                <div style="font-size: 20px; color: #444; font-weight: bold; display: flex; justify-content: center; gap: 40px; text-transform: uppercase;">
                    <span>⏳ ABERTO: <span style="color:#b78103;">{int(em_aberto_op)}</span></span>
                    <span>✅ PRODUTIVO: <span style="color:#1b5e20;">{int(produtivo_op)}</span></span>
                    <span>❌ QUEBRAS: <span style="color:#b30000;">{int(os_ne_op)}</span></span>
                    <span>👷 TÉCNICOS: <span style="color:#003366;">{total_tecnicos_op}</span></span>
                </div>
            </div>
            ''', unsafe_allow_html=True)

            for i in range(0, len(SUPS_ABC), 2):
                cols_sup = st.columns(2)
                for j in range(2):
                    if i + j < len(SUPS_ABC):
                        sup = SUPS_ABC[i + j]
                        with cols_sup[j]:
                            df_sup = df_abc_proj[df_abc_proj['SUPERVISOR_CLEAN'] == sup]

                            total_tarefas = df_sup['VALOR_TAREFA'].sum()
                            os_ne = df_sup.loc[df_sup['STATUS_PADRAO'] == 'O.S NE', 'VALOR_TAREFA'].sum()
                            produtivo = df_sup.loc[df_sup['STATUS_PADRAO'] == 'Produtivo', 'VALOR_TAREFA'].sum()
                            em_aberto = df_sup.loc[df_sup['STATUS_PADRAO'] == 'Em aberto', 'VALOR_TAREFA'].sum()

                            total_tecnicos = QTD_TECNICOS_MONTADOS.get(sup, 1)

                            os_reais = produtivo + em_aberto
                            media_equipe = os_reais / total_tecnicos if total_tecnicos > 0 else 0

                            denom_quebra = os_ne + produtivo
                            quebra = (os_ne / denom_quebra) * 100 if denom_quebra > 0 else 0
                            eficiencia = (produtivo / denom_quebra) * 100 if denom_quebra > 0 else 100
                            projecao = produtivo + (em_aberto * (eficiencia / 100))

                            cor_q = "#c62828" if quebra > 20.0 else "#2e7d32"

                            st.markdown(f'''
                            <div class="sup-card">
                                <div class="sup-header">
                                    <div class="sup-name">📋 {obter_nome_visual(sup)}</div>
                                    <div style="display: flex; gap: 8px; align-items: center;">
                                        <div style="background: #f8f9fa; color: #333; border: 1px solid #ccc; padding: 4px 10px; border-radius: 8px; font-size: 16px; font-weight: bold;">O.S.: {int(total_tarefas)}</div>
                                        <div style="background: #ffebee; color: {cor_q}; border: 1px solid {cor_q}; padding: 4px 10px; border-radius: 8px; font-size: 16px; font-weight: bold;">Quebra: {quebra:.1f}%</div>
                                        <div style="background: #e3f2fd; color: #006064; border: 1px solid #006064; padding: 4px 10px; border-radius: 8px; font-size: 16px; font-weight: bold;">Média: {media_equipe:.2f}</div>
                                    </div>
                                </div>
                                <div class="faltas-grid">
                                    <div class="falta-box" style="background-color: #fff8e1; border-color: #ffe082;">
                                        <div class="falta-label" style="color: #b78103;">ABERTO</div>
                                        <div class="falta-value" style="color: #b78103;">{int(em_aberto)}</div>
                                    </div>
                                    <div class="falta-box" style="background-color: #e8f5e9; border-color: #a5d6a7;">
                                        <div class="falta-label" style="color: #2e7d32;">PROD.</div>
                                        <div class="falta-value" style="color: #1b5e20;">{int(produtivo)}</div>
                                    </div>
                                    <div class="falta-box" style="background-color: #ffebee; border-color: #ffcdd2;">
                                        <div class="falta-label" style="color: #c62828;">QUEBRAS</div>
                                        <div class="falta-value" style="color: #b30000;">{int(os_ne)}</div>
                                    </div>
                                    <div class="falta-box" style="background-color: #e0f7fa; border-color: #80deea;">
                                        <div class="falta-label" style="color: #00838f;">PROJ.</div>
                                        <div class="falta-value" style="color: #00838f;">{int(round(projecao))}</div>
                                    </div>
                                </div>
                            </div>''', unsafe_allow_html=True)
            if st.session_state.novo_ciclo:
                texto_audio_10 = f"Atenção para a Visão Geral da Rota da Equipe Fixa. Temos um total de {int(total_tarefas_op)} O.S. A projeção da operação está em {int(round(projecao_op))}, com um total de {int(os_ne_op)} quebras de O.S. no momento."
                st.session_state.script_audio_atual = f"<script>/*{time.time()}*/ {JS_MOTOR_AUDIO}anunciarBase('{texto_audio_10}', 0);</script>"
                st.session_state.novo_ciclo = False
            st.components.v1.html(st.session_state.script_audio_atual, height=0)
        else: st.error("Ficheiro rota_sincronizada.csv não encontrado.")

    # -------------------------------------------------------------------------
    # TELA 5: CONSULTIVO GERAL
    # -------------------------------------------------------------------------
    elif st.session_state.idx == 5:
        st.markdown(render_topo("CONSULTIVO GERAL") + icone_mudo, unsafe_allow_html=True)

        if os.path.exists(ARQUIVO_CONSULTIVO):
            try:
                df_cons = pd.read_csv(ARQUIVO_CONSULTIVO, dtype=str, on_bad_lines='skip')
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

                col_contrato_cons = next((c for c in df_cards.columns if 'CONTRATO' in c or 'OS' in c or 'O.S' in c or 'PEDIDO' in c), None)
                def count_contracts(df_x): return df_x[col_contrato_cons].nunique() if col_contrato_cons else len(df_x)

                total_realizado_abc = int(df_cards['QTD_PRODUTOS_CALC'].sum())
                total_contratos_abc = count_contracts(df_cards)

                hoje = datetime.utcnow() - timedelta(hours=3)
                ano, mes = hoje.year, hoje.month
                _, num_dias = calendar.monthrange(ano, mes)
                dias_restantes = sum(1 for d in range(hoje.day, num_dias + 1) if calendar.weekday(ano, mes, d) != 6)
                if dias_restantes == 0: dias_restantes = 1

                meta_mensal_abc = len(SUPS_ABC) * 350
                st.session_state.ticker_data[5] = f"📈 CONSULTIVO MÊS: {total_realizado_abc} PRODUTOS (META: {meta_mensal_abc})"

                st.markdown(f'''<div style="text-align: center; margin-top: -10px; margin-bottom: 10px;">
                    <span style="font-size: 20px; font-weight: bold; color: #555;">Dias úteis restantes: </span>
                    <span style="font-size: 28px; font-weight: 900; color: #cc6600;">{dias_restantes}</span>
                </div>''', unsafe_allow_html=True)

                st.markdown(f'''<div class="box-base" style="padding: 10px;">
                    <div class="nome-base" style="margin-bottom: 5px;">🏢 ACUMULADO DO MÊS (Meta: {meta_mensal_abc})</div>
                    <div style="display: flex; justify-content: space-around; align-items: center;">
                        <div>
                            <div style="font-size: 20px; font-weight: bold; color: #666; text-transform: uppercase;">Contratos</div>
                            <div style="font-size: 70px; font-weight: 900; color: #0277bd; line-height: 1;">{total_contratos_abc}</div>
                        </div>
                        <div>
                            <div style="font-size: 20px; font-weight: bold; color: #666; text-transform: uppercase;">Produtos</div>
                            <div style="font-size: 70px; font-weight: 900; color: #111; line-height: 1;">{total_realizado_abc}</div>
                        </div>
                    </div>
                </div>''', unsafe_allow_html=True)
                
                for i in range(0, len(SUPS_ABC), 2):
                    cols_sup = st.columns(2)
                    for j in range(2):
                        if i + j < len(SUPS_ABC):
                            sup = SUPS_ABC[i + j]
                            with cols_sup[j]:
                                df_sup_mes = df_cards[df_cards['SUPERVISOR_CLEAN'] == sup]
                                qtd_sup = int(df_sup_mes['QTD_PRODUTOS_CALC'].sum())
                                qtd_contratos_sup = count_contracts(df_sup_mes)
                                falta_individual = max(0, 350 - qtd_sup)
                                ritmo_diario_individual = int(round(falta_individual / dias_restantes))

                                st.markdown(f'''
                                <div class="sup-card">
                                    <div class="sup-header">
                                        <div class="sup-name">📋 {obter_nome_visual(sup)}</div>
                                        <div class="badge-faltas" style="background: #e8f5e9; color: #2e7d32; border-color: #a5d6a7;">Alvo: 350</div>
                                    </div>
                                    <div class="faltas-grid">
                                        <div class="falta-box" style="background-color: #e3f2fd; border-color: #81d4fa;">
                                            <div class="falta-label" style="color: #0277bd;">CONTRATOS</div>
                                            <div class="falta-value" style="color: #01579b;">{qtd_contratos_sup}</div>
                                        </div>
                                        <div class="falta-box" style="background-color: #e8f5e9; border-color: #a5d6a7;">
                                            <div class="falta-label" style="color: #2e7d32;">PRODUTOS</div>
                                            <div class="falta-value" style="color: #1b5e20;">{qtd_sup}</div>
                                        </div>
                                        <div class="falta-box" style="background-color: #ffebee; border-color: #ffcdd2;">
                                            <div class="falta-label" style="color: #c62828;">FALTAM</div>
                                            <div class="falta-value" style="color: #b30000;">{falta_individual}</div>
                                        </div>
                                        <div class="falta-box" style="background-color: #fff8e1; border-color: #ffe082;">
                                            <div class="falta-label" style="color: #b78103;">DIÁRIA</div>
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
        st.markdown(render_topo("CONSULTIVO DIÁRIO") + icone_mudo, unsafe_allow_html=True)

        if os.path.exists(ARQUIVO_CONSULTIVO):
            try:
                df_cons = pd.read_csv(ARQUIVO_CONSULTIVO, dtype=str, on_bad_lines='skip')
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

                col_contrato_cons = next((c for c in df_cards.columns if 'CONTRATO' in c or 'OS' in c or 'O.S' in c or 'PEDIDO' in c), None)
                def count_contracts(df_x): return df_x[col_contrato_cons].nunique() if col_contrato_cons else len(df_x)

                hoje_br = datetime.utcnow() - timedelta(hours=3)
                hoje_str_br = hoje_br.strftime('%d/%m/%Y')
                hoje_str_us = hoje_br.strftime('%Y-%m-%d')

                df_hoje = pd.DataFrame()
                col_data = next((c for c in df_cards.columns if 'DATA' in c), None)
                if col_data:
                    df_cards['DATA_TXT'] = df_cards[col_data].astype(str).str.strip().str[:10]
                    mask_hoje = (df_cards['DATA_TXT'] == hoje_str_br) | (df_cards['DATA_TXT'] == hoje_str_us)
                    df_hoje = df_cards[mask_hoje].copy()
                
                ano, mes = hoje_br.year, hoje_br.month
                _, num_dias = calendar.monthrange(ano, mes)
                dias_restantes = sum(1 for d in range(hoje_br.day, num_dias + 1) if calendar.weekday(ano, mes, d) != 6)
                if dias_restantes <= 0: dias_restantes = 1

                total_hoje_abc = int(df_hoje['QTD_PRODUTOS_CALC'].sum()) if not df_hoje.empty else 0
                total_contratos_hoje_abc = count_contracts(df_hoje) if not df_hoje.empty else 0

                meta_dia_base_abc = 0
                for sup in SUPS_ABC:
                    qtd_m = df_cards[df_cards['SUPERVISOR_CLEAN'] == sup]['QTD_PRODUTOS_CALC'].sum()
                    meta_dia_base_abc += int(round(max(0, 350 - qtd_m) / dias_restantes))

                st.session_state.ticker_data[6] = f"📉 CONSULTIVO HOJE: {total_hoje_abc} PRODUTOS (META: {meta_dia_base_abc})"

                st.markdown(f'''<div style="text-align: center; margin-top: -10px; margin-bottom: 10px;">
                    <span style="font-size: 20px; font-weight: bold; color: #555;">Resultados de Hoje ({hoje_str_br}) - Dias úteis restantes: </span>
                    <span style="font-size: 28px; font-weight: 900; color: #cc6600;">{dias_restantes}</span>
                </div>''', unsafe_allow_html=True)

                st.markdown(f'''<div class="box-base" style="padding: 10px;">
                    <div class="nome-base" style="margin-bottom: 5px;">🏢 HOJE (Meta Diária: {meta_dia_base_abc})</div>
                    <div style="display: flex; justify-content: space-around; align-items: center;">
                        <div>
                            <div style="font-size: 20px; font-weight: bold; color: #666; text-transform: uppercase;">Contratos Hoje</div>
                            <div style="font-size: 70px; font-weight: 900; color: #0277bd; line-height: 1;">{total_contratos_hoje_abc}</div>
                        </div>
                        <div>
                            <div style="font-size: 20px; font-weight: bold; color: #666; text-transform: uppercase;">Produtos Hoje</div>
                            <div style="font-size: 70px; font-weight: 900; color: #111; line-height: 1;">{total_hoje_abc}</div>
                        </div>
                    </div>
                </div>''', unsafe_allow_html=True)
                
                for i in range(0, len(SUPS_ABC), 2):
                    cols_sup = st.columns(2)
                    for j in range(2):
                        if i + j < len(SUPS_ABC):
                            sup = SUPS_ABC[i + j]
                            with cols_sup[j]:
                                qtd_mes = df_cards[df_cards['SUPERVISOR_CLEAN'] == sup]['QTD_PRODUTOS_CALC'].sum()
                                df_sup_hoje = df_hoje[df_hoje['SUPERVISOR_CLEAN'] == sup] if not df_hoje.empty else pd.DataFrame()
                                qtd_hoje = int(df_sup_hoje['QTD_PRODUTOS_CALC'].sum()) if not df_sup_hoje.empty else 0
                                qtd_contratos_hoje_sup = count_contracts(df_sup_hoje) if not df_sup_hoje.empty else 0
                                
                                meta_dia = int(round(max(0, 350 - qtd_mes) / dias_restantes))
                                falta_hoje = int(round(max(0, meta_dia - qtd_hoje)))

                                st.markdown(f'''
                                <div class="sup-card">
                                    <div class="sup-header">
                                        <div class="sup-name">📋 {obter_nome_visual(sup)}</div>
                                        <div class="badge-faltas" style="background: #e8f5e9; color: #2e7d32; border-color: #a5d6a7;">Acumulado: {int(qtd_mes)}</div>
                                    </div>
                                    <div class="faltas-grid">
                                        <div class="falta-box" style="background-color: #e3f2fd; border-color: #81d4fa;">
                                            <div class="falta-label" style="color: #0277bd;">CONTRATOS</div>
                                            <div class="falta-value" style="color: #01579b;">{qtd_contratos_hoje_sup}</div>
                                        </div>
                                        <div class="falta-box" style="background-color: #e8f5e9; border-color: #a5d6a7;">
                                            <div class="falta-label" style="color: #2e7d32;">PRODUTOS</div>
                                            <div class="falta-value" style="color: #1b5e20;">{qtd_hoje}</div>
                                        </div>
                                        <div class="falta-box" style="background-color: #ffebee; border-color: #ffcdd2;">
                                            <div class="falta-label" style="color: #c62828;">FALTAM</div>
                                            <div class="falta-value" style="color: #b30000;">{falta_hoje}</div>
                                        </div>
                                        <div class="falta-box" style="background-color: #fff8e1; border-color: #ffe082;">
                                            <div class="falta-label" style="color: #b78103;">DIÁRIA</div>
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
        st.markdown(render_topo("PRINT DOS INDICADORES") + html_audio_ind, unsafe_allow_html=True)

        if os.path.exists(ARQUIVO_ROTA_DISCO):
            try:
                df_ind = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str, on_bad_lines='skip')
                df_ind.columns = [str(c).strip().upper() for c in df_ind.columns]
                col_status = next((c for c in df_ind.columns if 'STATUS' in c), None)
                col_recurso = 'RECURSO' if 'RECURSO' in df.columns else df_ind.columns[0]
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

                    def resolver_supervisor(row):
                        sup = str(row.get(col_sup, '')).upper().strip() if col_sup else ''
                        for oficial in SUPERVISORES_ORDENADOS:
                            if oficial in sup: return oficial
                        return "DESCARTADO"

                    df_produtivo['SUPERVISOR_CLEAN'] = df_produtivo.apply(resolver_supervisor, axis=1)
                    df_produtivo = df_produtivo[df_produtivo['SUPERVISOR_CLEAN'].isin(SUPS_ABC)]

                    total_faltas_ind = df_produtivo['FALTA_NR35'].sum() + df_produtivo['FALTA_CERT'].sum() + df_produtivo['FALTA_BST'].sum()
                    st.session_state.ticker_data[3] = f"📋 INDICADORES: {int(total_faltas_ind)} FALTAS"

                    st.markdown('<div style="font-size: 28px; font-weight: 900; text-align: center; margin-bottom: 20px; color: #c62828; text-transform: uppercase; background-color: #ffebee; padding: 10px; border-radius: 10px; border: 2px solid #ffcdd2;">⚠️ FALTAM PRINTS</div>', unsafe_allow_html=True)
                    
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

                    if permitir_audio_ind:
                        script_ind = f"<script>/*{time.time()}*/ {JS_MOTOR_AUDIO}anunciarBase('Monitores, enviem os prints pendentes do N R 35, Band Steering e certidão de atendimento.', 0);</script>"
                    else: 
                        script_ind = ""
                    st.components.v1.html(script_ind, height=0)
                else: st.error("Coluna Status não encontrada na base da rota.")
            except Exception as e:
                st.error("Nenhum contrato ativo válido para Indicadores nesta leitura.")
        else: st.error("Ficheiro rota_sincronizada.csv não encontrado.")

    # -------------------------------------------------------------------------
    # TELA 2: HORÁRIO
    # -------------------------------------------------------------------------
    elif st.session_state.idx == 2:
        st.markdown(render_topo("HORÁRIO") + icone_ativo, unsafe_allow_html=True)

        tempo_real = datetime.utcnow() - timedelta(hours=3)
        
        st.markdown(f'''
        <div class="relogio-container">
            <div id="relogio-dinamico" class="hora-gigante">{tempo_real.strftime("%H:%M:%S")}</div>
            <div class="data-media">{tempo_real.strftime("%d/%m/%Y")}</div>
        </div>
        ''', unsafe_allow_html=True)
        
        if st.session_state.novo_ciclo:
            st.session_state.script_audio_atual = f"<script>/*{time.time()}*/ {JS_MOTOR_AUDIO}anunciarBase('Hora certa: {tempo_real.strftime('%H e %M')}.', 0);</script>"
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
    if st.session_state.idx != 4 and not modo_estatico:  
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
# CONTROLES DE NAVEGAÇÃO E TRANSIÇÃO 🔄
# =========================================================================
if modo_estatico:
    btn_atualizar = st.button("🔄 ATUALIZAR", key="btn_atualizar_estatico")
    if btn_atualizar:
        st.rerun()

    js_timer_estatico = f"""
    <script>
    setTimeout(function() {{
        var buttons = window.parent.document.querySelectorAll('button');
        for (var i=0; i<buttons.length; i++) {{
            if (buttons[i].innerText && buttons[i].innerText.indexOf('ATUALIZAR') !== -1) {{
                buttons[i].click();
                break;
            }}
        }}
    }}, 60000);
    </script>
    """
    st.components.v1.html(js_timer_estatico, height=0)
    st.stop()

col_voltar, col_vazio, col_pular = st.columns([1, 8, 1])
with col_voltar:
    voltar = st.button("⬅️ ANTERIOR", key="btn_anterior")
with col_pular:
    pular = st.button("PRÓXIMA ➡️", key="btn_proxima")

agora_loop = datetime.utcnow() - timedelta(hours=3)
minutos_loop = agora_loop.hour * 60 + agora_loop.minute

periodo_matinal_base = (7*60 <= minutos_loop < 8*60 + 30)

alerta_fim_janela_loop = False
if agora_loop.hour in [11, 14, 17] and agora_loop.minute >= 0: alerta_fim_janela_loop = True
if agora_loop.hour in [12, 15, 18]: alerta_fim_janela_loop = True

tempos_espera = {
    0: 60,
    1: 30 if alerta_fim_janela_loop else 60,
    7: 60,
    8: 60,
    9: 60,
    10: 60,
    11: 20, 12: 20, 13: 20, 14: 20, 15: 20, 16: 20,
    5: 60,
    6: 60,
    3: 45,
    2: 30 if (alerta_fim_janela_loop or periodo_matinal_base) else 60,
    4: 2
}

espera = tempos_espera.get(st.session_state.idx, 60)

if st.session_state.idx == 1 and permitir_audio_tec1:
    espera = 95 

if st.session_state.idx == 4:
    st.session_state.idx = st.session_state.prox_idx
    st.rerun()
else:
    if periodo_matinal_base:
        telas_fluxo = [0, 2]
    else:
        telas_fluxo = [0, 1, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 5, 6, 3, 2]
        
    try:
        pos = telas_fluxo.index(st.session_state.idx)
    except ValueError:
        pos = 0
        
    if pular:
        st.session_state.prox_idx = telas_fluxo[(pos + 1) % len(telas_fluxo)]
        st.session_state.idx = 4
        st.rerun()
    elif voltar:
        st.session_state.prox_idx = telas_fluxo[(pos - 1) % len(telas_fluxo)]
        st.session_state.idx = 4
        st.rerun()
    else:
        js_timer = f"""
        <script>
        /* TIMESTAMP: {time.time()} */
        setTimeout(function() {{
            var buttons = window.parent.document.querySelectorAll('button');
            for (var i=0; i<buttons.length; i++) {{
                if (buttons[i].innerText && buttons[i].innerText.indexOf('PRÓXIMA') !== -1) {{
                    buttons[i].click();
                    break;
                }}
            }}
        }}, {espera * 1000});
        </script>
        """
        st.components.v1.html(js_timer, height=0)
        st.stop()

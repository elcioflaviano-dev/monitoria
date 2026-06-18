import streamlit as st
import pandas as pd
import os
import time
import base64
from datetime import datetime, timedelta

# =========================================================================
# CONFIGURAÇÕES DE CAMINHOS E LINKS
# =========================================================================
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1kB1YmUuhzHpfN1dLv8PaQn0ipXcHcd6kGKnI3nguT14/export?format=csv&gid=0"

# Padronização dos arquivos para leitura direta (Resolve o problema da tela vazia)
ARQUIVO_INDICADORES = "indicadores_data.csv"
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

ARQUIVO_LOGO = "logo.png"
if not os.path.exists(ARQUIVO_LOGO):
    ARQUIVO_LOGO = os.path.join("pages", "logo.png")

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

def carregar_logo_html(caminho_imagem):
    if os.path.exists(caminho_imagem):
        try:
            with open(caminho_imagem, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f'<img src="data:image/png;base64,{encoded_string}" style="height: 100px; width: auto; object-fit: contain; display: block;">'
        except:
            return '<div></div>'
    return '<div></div>'

logo_html = carregar_logo_html(ARQUIVO_LOGO)

# =========================================================================
# CSS E ESTILIZAÇÃO DO PAINEL
# =========================================================================
st.markdown("""<style>
    [data-testid="stHeader"] { visibility: hidden !important; }
    .stDeployButton { display: none !important; }
    footer { visibility: hidden !important; }
    #MainMenu { visibility: hidden !important; }
    [data-testid="stSidebar"] { display: none !important; }
    
    .stApp { background-color: #ffffff !important; }

    .topo-container { 
        background: #003366; color: white; padding: 0px 30px; border-radius: 0 0 15px 15px; 
        display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; margin-bottom: 10px; height: 100px;
    }
    .topo-esquerda { display: flex; justify-content: flex-start; align-items: center; height: 100%; }
    .topo-centro { font-size: 45px; font-weight: 900; text-align: center; white-space: nowrap; }
    .topo-direita { display: flex; justify-content: flex-end; align-items: center; }
    
    .botao-home { color: #fff; font-size: 18px; font-weight: bold; border: 2px solid #fff; padding: 8px 15px; border-radius: 5px; text-decoration: none; }
    
    .box-base { background: #e8f5e9; border-left: 10px solid #2e7d32; padding: 15px 10px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.15); margin-bottom: 10px; }
    .box-base-sp { background: #dcf7f5; border-left: 10px solid #03a398; padding: 15px 10px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.15); margin-bottom: 10px; }
    .nome-base { font-size: 28px; font-weight: 900; color: #333; text-transform: uppercase;}
    .num-base { font-size: 85px; font-weight: 900; color: #111; line-height: 1.1; }
    
    .box-contagem { background: #f0f2f6; border-left: 8px solid #cc6600; padding: 15px 5px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); margin-top: 15px; margin-left: 10px; margin-right: 10px; margin-bottom: 15px; position: relative; z-index: 1; }
    .box-nome { font-size: 18px; font-weight: 900; color: #003366; text-transform: uppercase;}
    .box-num { font-size: 65px; font-weight: 900; color: #cc6600; line-height: 1; }
    
    .destaque-ativo { transform: scale(1.30) !important; box-shadow: 0px 25px 45px rgba(204, 102, 0, 0.6) !important; border-left: 20px solid #ff8800 !important; background: #fff8e1 !important; z-index: 9999 !important; }
    
    .relogio-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 70vh; background-color: #ffffff; width: 100%; }
    .hora-gigante { font-size: 180px; font-weight: 900; color: #003366; text-shadow: 4px 4px 10px rgba(0,0,0,0.1); line-height: 1; letter-spacing: 5px; }
    .data-media { font-size: 40px; color: #666; font-weight: bold; margin-top: -20px; }
    .tec-base-nome { background: #f8f9fa; padding: 8px 12px; border-left: 5px solid #008080; border-radius: 4px; margin-bottom: 8px; font-weight: bold; font-size: 16px; color: #333; box-shadow: 1px 1px 3px rgba(0,0,0,0.1); }
    
    .card-indicador { background:#ffffff; border-radius:8px; padding:15px; text-align:center; border: 2px solid #e0e0e0; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .card-ind-titulo { font-size:16px; font-weight:800; color:#555; margin-bottom:8px; text-transform:uppercase; }
    .card-ind-valor { font-size:42px; font-weight:900; color:#005088; line-height:1; }
</style>""", unsafe_allow_html=True)

# =========================================================================
# 🧠 INTELIGÊNCIA: BUSCA DINÂMICA DE SUPERVISORES E TÉCNICOS
# =========================================================================
@st.cache_data(ttl=300)
def carregar_dados_compilado():
    mapa = {}
    supervisores = []
    try:
        df_comp = pd.read_csv(URL_PLANILHA, dtype=str)
        df_comp.columns = [str(c).strip().upper() for c in df_comp.columns]
        
        # 1. Mapear Técnicos para as suas Bases (Substitui as listas fixas)
        col_nome = next((c for c in df_comp.columns if 'NOME' in c or 'RECURSO' in c or 'TÉCN' in c or 'TECN' in c), None)
        col_base = next((c for c in df_comp.columns if 'BASE' in c or 'POLO' in c or 'LOCAL' in c), None)
        if col_nome and col_base:
            for _, row in df_comp.iterrows():
                nome = str(row[col_nome]).strip().upper()
                base = str(row[col_base]).strip().upper()
                if nome != 'NAN' and base != 'NAN':
                    mapa[nome] = base
                    
        # 2. Mapear Supervisores
        col_sup = next((c for c in df_comp.columns if 'SUPERVISOR' in c), None)
        if col_sup:
            supervisores = [str(s).strip().upper() for s in df_comp[col_sup].dropna().unique().tolist() if str(s).strip().upper() != "NAN" and str(s).strip() != ""]
            
    except Exception:
        pass
    return mapa, supervisores

mapa_bases, SUPERVISORES = carregar_dados_compilado()

def obter_nome_visual(nome_completo):
    n = str(nome_completo).upper()
    if 'FRANCISCO' in n: return "FRANCISCO"
    if 'MARCOS' in n: return "MARCOS ROBERTO"
    return n.split()[0]

# =========================================================================
# ⚙️ MÁQUINA DE TEMPO E ESTADOS (PLAYLIST)
# =========================================================================
if "idx" not in st.session_state: 
    st.session_state.idx = 2         
    st.session_state.last_time = time.time()
    st.session_state.novo_ciclo = True
    st.session_state.script_audio_atual = ""

if "posicao_ordem" not in st.session_state:
    st.session_state.posicao_ordem = 0

agora_br = datetime.utcnow() - timedelta(hours=3)

antes_0830 = (agora_br.hour < 8) or (agora_br.hour == 8 and agora_br.minute < 30)
mostrar_indicadores = True 

alerta_fim_janela = False
if agora_br.hour in [11, 14, 17] and agora_br.minute >= 40: 
    alerta_fim_janela = True

# ⏳ TEMPO DE CADA TELA
if st.session_state.idx == 0: espera = 60 
elif st.session_state.idx == 1: espera = 30 if alerta_fim_janela else 60 
elif st.session_state.idx == 3: espera = 45 
elif st.session_state.idx == 2: espera = 30 if alerta_fim_janela else 60 
elif st.session_state.idx == 4: espera = 2 

tempo_passado = time.time() - st.session_state.last_time

# 🔄 ORDEM DE APRESENTAÇÃO
if antes_0830: ordem_telas = [2, 0] 
elif mostrar_indicadores: ordem_telas = [2, 1, 2, 3] 
else: ordem_telas = [2, 1] 

if tempo_passado > espera:
    if st.session_state.idx != 4:
        st.session_state.idx = 4
    else:
        st.session_state.posicao_ordem += 1
        if st.session_state.posicao_ordem >= len(ordem_telas):
            st.session_state.posicao_ordem = 0
        st.session_state.idx = ordem_telas[st.session_state.posicao_ordem]
        
    st.session_state.last_time = time.time()
    st.session_state.novo_ciclo = True
    st.rerun()

# 🔊 MOTOR DE ÁUDIO JS (Reduzido para economizar linhas)
JS_MOTOR_AUDIO = """
function tocarAlertaChamaAtencao() {
    try {
        let ctx = new (window.parent.AudioContext || window.AudioContext)(); let tempo = ctx.currentTime;
        let osc1 = ctx.createOscillator(); let gain1 = ctx.createGain();
        osc1.type = 'triangle'; osc1.frequency.setValueAtTime(880, tempo);
        gain1.gain.setValueAtTime(0, tempo); gain1.gain.linearRampToValueAtTime(0.4, tempo + 0.05); gain1.gain.exponentialRampToValueAtTime(0.01, tempo + 0.6);
        osc1.connect(gain1); gain1.connect(ctx.destination); osc1.start(tempo); osc1.stop(tempo + 0.6);
    } catch(e) {}
}
function anunciarBase(texto, delay) {
    setTimeout(() => { tocarAlertaChamaAtencao(); setTimeout(() => { let synth = window.parent.speechSynthesis || window.speechSynthesis; let m = new SpeechSynthesisUtterance(texto); m.lang = 'pt-BR'; synth.speak(m); }, 1500); }, delay);
}
function limparDestaques(total) { for(let j=0; j<total; j++) { let el = window.parent.document.getElementById('sup-box-' + j); if(el) { el.classList.remove('destaque-ativo'); } } }
function animarSupervisor(texto, delay, index, totalSup) {
    setTimeout(() => { limparDestaques(totalSup); let elAtual = window.parent.document.getElementById('sup-box-' + index); if(elAtual) { elAtual.classList.add('destaque-ativo'); } tocarAlertaChamaAtencao(); setTimeout(() => { let synth = window.parent.speechSynthesis || window.speechSynthesis; let m = new SpeechSynthesisUtterance(texto); m.lang = 'pt-BR'; synth.speak(m); }, 1500); }, delay);
}
"""

# =========================================================================
# TELA 4: TELA BRANCA DE LIMPEZA
# =========================================================================
if st.session_state.idx == 4:
    st.markdown('<div style="height: 100vh; width: 100vw; background-color: #ffffff;"></div>', unsafe_allow_html=True)
    st.components.v1.html("", height=0)

# =========================================================================
# TELA 0: TÉCNICOS NA BASE
# =========================================================================
elif st.session_state.idx == 0:
    st.markdown(f'''<div class="topo-container"><div class="topo-esquerda">{logo_html}</div><div class="topo-centro">🚀 TÉCNICOS EM BASE</div><div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div></div>''', unsafe_allow_html=True)

    if os.path.exists(ARQUIVO_ROTA_DISCO):
        df = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
        df.columns = [str(c).strip() for c in df.columns]
        col_tipo = 'Tipo de Atividade.1' if 'Tipo de Atividade.1' in df.columns else ('Tipo de Atividade' if 'Tipo de Atividade' in df.columns else None)
        col_status = 'Status da Atividade' if 'Status da Atividade' in df.columns else 'STATUS_ATIVIDADE'
        
        if col_tipo and col_status:
            df_tela = df[(df[col_tipo].astype(str).str.contains('NA BASE', na=False, case=False)) & (df[col_status].astype(str).str.contains('PENDENTE', na=False, case=False))].copy()
            nomes_na_base = sorted(df_tela['Recurso'].dropna().astype(str).str.strip().unique().tolist())
            
            # Cruzamento Dinâmico Inteligente
            nomes_abc, nomes_sp = [], []
            for n in nomes_na_base:
                n_upper = n.upper()
                if "ABC" in mapa_bases.get(n_upper, "SP"): nomes_abc.append(n_upper)
                else: nomes_sp.append(n_upper)

            c1, c2, c3, c4 = st.columns(4)
            mid_abc = len(nomes_abc) // 2
            mid_sp = len(nomes_sp) // 2
            
            with c1:
                st.markdown('<h3 style="color:#008080;">🏢 ABC (1/2)</h3>', unsafe_allow_html=True)
                for n in nomes_abc[:mid_abc]: st.markdown(f'<div class="tec-base-nome">🏃‍♂️ {n}</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<h3 style="color:#008080;">🏢 ABC (2/2)</h3>', unsafe_allow_html=True)
                for n in nomes_abc[mid_abc:]: st.markdown(f'<div class="tec-base-nome">🏃‍♂️ {n}</div>', unsafe_allow_html=True)
            with c3:
                st.markdown('<h3 style="color:#c62828;">🏙️ SP (1/2)</h3>', unsafe_allow_html=True)
                for n in nomes_sp[:mid_sp]: st.markdown(f'<div class="tec-base-nome" style="border-left-color:#c62828;">🏃‍♂️ {n}</div>', unsafe_allow_html=True)
            with c4:
                st.markdown('<h3 style="color:#c62828;">🏙️ SP (2/2)</h3>', unsafe_allow_html=True)
                for n in nomes_sp[mid_sp:]: st.markdown(f'<div class="tec-base-nome" style="border-left-color:#c62828;">🏃‍♂️ {n}</div>', unsafe_allow_html=True)

            if st.session_state.novo_ciclo:
                script_cenario = f"<script>{JS_MOTOR_AUDIO} anunciarBase('Atenção. Existem {len(nomes_abc)} técnicos pendentes na base A B C, e {len(nomes_sp)} na base São Paulo.', 0); </script>"
                st.session_state.script_audio_atual = script_cenario
                st.session_state.novo_ciclo = False 
            st.components.v1.html(st.session_state.script_audio_atual, height=0)
    else: st.error("Ficheiro de rota não encontrado.")

# =========================================================================
# TELA 1: CONTRATOS PENDENTES
# =========================================================================
elif st.session_state.idx == 1: 
    st.markdown(f'''<div class="topo-container"><div class="topo-esquerda">{logo_html}</div><div class="topo-centro">CONTRATOS PENDENTES</div><div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div></div>''', unsafe_allow_html=True)

    if os.path.exists(ARQUIVO_ROTA_DISCO):
        df = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
        df.columns = [str(c).strip() for c in df.columns]
        
        def padronizar_supervisor(nome):
            n = str(nome).upper().strip()
            for s in SUPERVISORES:
                if s in n or n in s: return s
            return n
        
        df['SUPERVISOR_CLEAN'] = df['SUPERVISOR'].apply(padronizar_supervisor)
        col_status_real = 'Status da Atividade' if 'Status da Atividade' in df.columns else 'STATUS_ATIVIDADE'
        df['Status_Atividade_Upper'] = df[col_status_real].fillna('').astype(str).str.upper().str.strip()
        df_limpo = df[df['Status_Atividade_Upper'] != 'SUSPENSO'].copy()
        df_limpo['P_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('PENDENTE|EM ABERTO|ABERTO|PEND', na=False).astype(int)
        df_limpo['R_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('ROTA|DESLOC|DESLOCAMENTO', na=False).astype(int)
        df_limpo['I_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('INICIADO|PRODUTIVO|EXECUCAO|INIC', na=False).astype(int)
        df_validos = df_limpo[(df_limpo['P_COUNT'] > 0) | (df_limpo['R_COUNT'] > 0) | (df_limpo['I_COUNT'] > 0)].copy()
        
        col_janela = next((c for c in df_validos.columns if 'JANELA' in str(c).upper() or 'INTERVALO' in str(c).upper()), None)
        hora_atual = (datetime.utcnow() - timedelta(hours=3)).hour

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
            if df_pendentes_geral.empty and df_base_janela.empty: df_pendentes_geral = df_validos[df_validos['P_COUNT'] > 0].copy()
        else: df_pendentes_geral = df_validos[df_validos['P_COUNT'] > 0].copy()

        if 'Contrato' in df_pendentes_geral.columns and not df_pendentes_geral.empty:
            df_pendentes_geral['Contrato'] = df_pendentes_geral['Contrato'].fillna('').astype(str).apply(lambda x: str(x).split('.')[0])
            df_pendentes_geral = df_pendentes_geral.drop_duplicates(subset=['Contrato'])

        cond_sp = df_pendentes_geral['SUPERVISOR_CLEAN'].str.contains('ALAN|FRANCISCO|JOAO', na=False) 
        qtd_sp = len(df_pendentes_geral[cond_sp])
        qtd_abc = len(df_pendentes_geral[~cond_sp])

        c_abc, c_sp = st.columns(2)
        with c_abc: st.markdown(f'<div class="box-base"><div class="nome-base" style="color:#2e7d32;">ABC PENDENTES</div><div class="num-base">{qtd_abc}</div></div>', unsafe_allow_html=True)
        with c_sp: st.markdown(f'<div class="box-base-sp"><div class="nome-base" style="color:#03a398;">SP PENDENTES</div><div class="num-base">{qtd_sp}</div></div>', unsafe_allow_html=True)

        if SUPERVISORES:
            cols_sup = st.columns(len(SUPERVISORES))
            if st.session_state.novo_ciclo:
                script_cenario = f"<script>{JS_MOTOR_AUDIO} limparDestaques({len(SUPERVISORES)});\n"
                script_cenario += f"anunciarBase('Contratos pendentes. A B C: {qtd_abc} pendentes.', 0);\n"
                script_cenario += f"anunciarBase('São Paulo: {qtd_sp} pendentes.', 7000);\n"
                for i, sup_full in enumerate(SUPERVISORES):
                    q = len(df_pendentes_geral[df_pendentes_geral['SUPERVISOR_CLEAN'] == sup_full])
                    script_cenario += f"animarSupervisor('{obter_nome_visual(sup_full)}: {q} pendentes.', {14000 + i * 7000}, {i}, {len(SUPERVISORES)});\n"
                script_cenario += f"setTimeout(() => limparDestaques({len(SUPERVISORES)}) , {14000 + len(SUPERVISORES) * 7000}); </script>"
                st.session_state.script_audio_atual = script_cenario
                st.session_state.novo_ciclo = False 
                
            for i, sup_full in enumerate(SUPERVISORES):
                q = len(df_pendentes_geral[df_pendentes_geral['SUPERVISOR_CLEAN'] == sup_full])
                with cols_sup[i]: st.markdown(f'<div id="sup-box-{i}" class="box-contagem"><div class="box-nome">{obter_nome_visual(sup_full)}</div><div class="box-num">{q}</div></div>', unsafe_allow_html=True)
            st.components.v1.html(st.session_state.script_audio_atual, height=0)
    else: st.error("Ficheiro de rota não encontrado.")

# =========================================================================
# TELA 2: HORÁRIO E ALERTAS
# =========================================================================
elif st.session_state.idx == 2:
    st.markdown(f'''<div class="topo-container"><div class="topo-esquerda">{logo_html}</div><div class="topo-centro">HORÁRIO</div><div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div></div>''', unsafe_allow_html=True)

    tempo_real = datetime.utcnow() - timedelta(hours=3)
    st.markdown(f'''<div class="relogio-container"><div class="hora-gigante">{tempo_real.strftime("%H:%M:%S")}</div><div class="data-media">{tempo_real.strftime("%d/%m/%Y")}</div></div>''', unsafe_allow_html=True)
    
    if st.session_state.novo_ciclo:
        msg = f"Atenção equipe. Fim da janela se aproximando. Hora certa: {tempo_real.strftime('%H e %M')}." if alerta_fim_janela else f"Hora certa: {tempo_real.strftime('%H e %M')}."
        st.session_state.script_audio_atual = f"<script>{JS_MOTOR_AUDIO} anunciarBase('{msg}', 0); </script>"
        st.session_state.novo_ciclo = False
    st.components.v1.html(st.session_state.script_audio_atual, height=0)

# =========================================================================
# TELA 3: INDICADORES DA EQUIPE
# =========================================================================
elif st.session_state.idx == 3:
    st.markdown(f'''<div class="topo-container"><div class="topo-esquerda">{logo_html}</div><div class="topo-centro">📈 INDICADORES DA EQUIPE</div><div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div></div>''', unsafe_allow_html=True)

    if st.session_state.novo_ciclo:
        st.session_state.script_audio_atual = f"<script>{JS_MOTOR_AUDIO} anunciarBase('Atenção equipe. Quadro de indicadores atualizado.', 0); </script>"
        st.session_state.novo_ciclo = False
    st.components.v1.html(st.session_state.script_audio_atual, height=0)

    df_ind = pd.DataFrame()
    if os.path.exists(ARQUIVO_INDICADORES):
        try:
            # Força a leitura das colunas em caixa alta para evitar conflitos de digitação
            df_ind = pd.read_csv(ARQUIVO_INDICADORES)
            df_ind.columns = [str(c).strip().upper() for c in df_ind.columns]
        except Exception:
            pass 

    if not df_ind.empty and "VALOR" in df_ind.columns:
        c_abc, c_sp = st.columns(2)
        
        def renderizar_cards_indicadores(df_base):
            pivot = df_base.pivot_table(index="SUPERVISOR", columns="INDICADOR", values="VALOR", aggfunc="max").fillna(0).astype(int)
            for col in ["NR35", "Certidão de Atendimento", "Band Steering"]:
                if col.upper() not in [c.upper() for c in pivot.columns]: pivot[col.upper()] = 0
            
            for supervisor in sorted(pivot.index):
                row = pivot.loc[supervisor]
                with st.container(border=True):
                    st.markdown(f'<div style="font-size:24px; font-weight:900; margin-bottom:15px; color:#333;">📋 Supervisor: {supervisor}</div>', unsafe_allow_html=True)
                    m1, m2, m3 = st.columns(3)
                    
                    # Recupera o valor usando tratamento de caixa para não dar erro
                    val_nr35 = row.get("NR35", row.get("NR35".upper(), 0))
                    val_cert = row.get("Certidão de Atendimento", row.get("CERTIDÃO DE ATENDIMENTO", 0))
                    val_band = row.get("Band Steering", row.get("BAND STEERING", 0))

                    with m1: st.markdown(f'<div class="card-indicador"><div class="card-ind-titulo">👷 NR35</div><div class="card-ind-valor">{int(val_nr35)}</div></div>', unsafe_allow_html=True)
                    with m2: st.markdown(f'<div class="card-indicador"><div class="card-ind-titulo">📄 CERTIDÃO</div><div class="card-ind-valor">{int(val_cert)}</div></div>', unsafe_allow_html=True)
                    with m3: st.markdown(f'<div class="card-indicador"><div class="card-ind-titulo">📡 BAND STEERING</div><div class="card-ind-valor">{int(val_band)}</div></div>', unsafe_allow_html=True)

        with c_abc:
            st.markdown('<div class="nome-base" style="color:#2e7d32; text-align:center; margin-bottom:15px; border-bottom:3px solid #2e7d32; padding-bottom:5px;">ABC PAULISTA</div>', unsafe_allow_html=True)
            df_abc = df_ind[df_ind["BASE"].str.upper() == "ABC"]
            if not df_abc.empty: renderizar_cards_indicadores(df_abc)
            else: st.info("Nenhum indicador lançado para o ABC hoje.")

        with c_sp:
            st.markdown('<div class="nome-base" style="color:#03a398; text-align:center; margin-bottom:15px; border-bottom:3px solid #03a398; padding-bottom:5px;">SÃO PAULO</div>', unsafe_allow_html=True)
            df_sp = df_ind[df_ind["BASE"].str.upper() == "SP"]
            if not df_sp.empty: renderizar_cards_indicadores(df_sp)
            else: st.info("Nenhum indicador lançado para SP hoje.")
    else:
        st.info("Nenhum indicador lançado hoje. Utilize a página 'Lançamento de Indicadores' para alimentar o painel.")

time.sleep(1)
st.rerun()

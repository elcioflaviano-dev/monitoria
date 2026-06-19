import streamlit as st
import pandas as pd
import os
import time
import base64
from datetime import datetime, timedelta

# =========================================================================
# CONFIGURAÇÕES (SEM LINKS EXTERNOS) 🚀
# =========================================================================
ROOT_DIR = os.getcwd()
ARQUIVO_ROTA_DISCO = os.path.join(ROOT_DIR, "rota_sincronizada.csv")

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
        except:
            return '<div></div>'
    return '<div></div>'

logo_html = carregar_logo_html(ARQUIVO_LOGO)

st.markdown("""<style>
    [data-testid="stHeader"] { visibility: hidden !important; }
    .stDeployButton { display: none !important; }
    footer { visibility: hidden !important; }
    #MainMenu { visibility: hidden !important; }
    [data-testid="stSidebar"] { display: none !important; }
    
    /* FORÇA O FUNDO A FICAR BRANCO PARA ELIMINAR RASTROS */
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
    
    /* CSS DOS INDICADORES */
    .kpi-container-ind { display: flex; justify-content: center; gap: 30px; margin-top: 50px; }
    .kpi-card-ind { background-color: #f8f9fa; border-radius: 10px; padding: 25px 35px; text-align: center; min-width: 300px; border: 1px solid #e0e0e0; box-shadow: 2px 4px 10px rgba(0,0,0,0.05); }
    .kpi-card-ind.nr35 { border-bottom: 8px solid #008080; }
    .kpi-card-ind.cert { border-bottom: 8px solid #005088; }
    .kpi-card-ind.bst { border-bottom: 8px solid #b30000; }
    .ind-title { font-size: 22px; color: #555; font-weight: bold; text-transform: uppercase; margin-bottom: 10px;}
    .ind-value { font-size: 70px; font-weight: 900; color: #111; margin-top: 5px; }
    
    .destaque-ativo { transform: scale(1.30) !important; box-shadow: 0px 25px 45px rgba(204, 102, 0, 0.6) !important; border-left: 20px solid #ff8800 !important; background: #fff8e1 !important; z-index: 9999 !important; }
    
    .relogio-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 70vh; background-color: #ffffff; width: 100%; }
    .hora-gigante { font-size: 180px; font-weight: 900; color: #003366; text-shadow: 4px 4px 10px rgba(0,0,0,0.1); line-height: 1; letter-spacing: 5px; }
    .data-media { font-size: 40px; color: #666; font-weight: bold; margin-top: -20px; }
    .tec-base-nome { background: #f8f9fa; padding: 8px 12px; border-left: 5px solid #008080; border-radius: 4px; margin-bottom: 8px; font-weight: bold; font-size: 16px; color: #333; box-shadow: 1px 1px 3px rgba(0,0,0,0.1); }
</style>""", unsafe_allow_html=True)

# LEITURA DE SUPERVISORES E DADOS DINÂMICOS DIRETAMENTE DO CSV LOCAL 🚀
SUPERVISORES = []
if os.path.exists(ARQUIVO_ROTA_DISCO):
    try:
        df_temp = pd.read_csv(ARQUIVO_ROTA_DISCO, sep=None, engine='python', dtype=str)
        df_temp.columns = [str(c).strip().upper() for c in df_temp.columns]
        
        col_sup = next((c for c in df_temp.columns if 'SUPERVISOR' in c), None)
        if col_sup:
            supervisores_brutos = df_temp[col_sup].dropna().unique().tolist()
            SUPERVISORES = sorted([str(s).strip().upper() for s in supervisores_brutos if str(s).strip().upper() not in ["", "NAN", "N/A", "NÃO IDENTIFICADO"]])
    except Exception:
        pass

def padronizar_supervisor(nome):
    n = str(nome).upper().strip()
    for s in SUPERVISORES:
        if s in n or n in s: return s
    return n

def obter_nome_visual(nome_completo):
    n = str(nome_completo).upper()
    if 'FRANCISCO' in n: return "FRANCISCO"
    if 'MARCOS' in n: return "MARCOS ROBERTO"
    return n.split()[0]

# =========================================================================
# ⚙️ MÁQUINA DE TEMPO E ESTADOS INTELIGENTE
# =========================================================================
# Telas Disponíveis: 
# 0 = Técnicos na Base
# 1 = Pendentes
# 2 = Relógio
# 3 = Indicadores (Nova!)
# 4 = Tela Branca

if "idx" not in st.session_state: 
    st.session_state.idx = 0          
    st.session_state.last_main = 0   
    st.session_state.last_time = time.time()
    st.session_state.novo_ciclo = True
    st.session_state.script_audio_atual = ""

agora_br = datetime.utcnow() - timedelta(hours=3)
antes_0830 = (agora_br.hour < 8) or (agora_br.hour == 8 and agora_br.minute < 30)

alerta_fim_janela = False
if agora_br.hour in [11, 14, 17] and agora_br.minute >= 40: 
    alerta_fim_janela = True

# ⏳ TEMPO DE CADA TELA
if st.session_state.idx == 0: espera = 60 # Técnicos na Base
elif st.session_state.idx == 1: espera = 30 if alerta_fim_janela else 60 # Pendentes
elif st.session_state.idx == 2: espera = 30 if alerta_fim_janela else 60 # Relógio
elif st.session_state.idx == 3: espera = 45 # Indicadores
elif st.session_state.idx == 4: espera = 2 # Tela Branca

tempo_passado = time.time() - st.session_state.last_time

# 🔄 ROTADOR LÓGICO
if tempo_passado > espera:
    if antes_0830:
        if st.session_state.idx == 0:
            st.session_state.last_main = 0
            prox_idx = 4
        else:
            prox_idx = 0
    else:
        # Telas de dados vão para a tela branca
        if st.session_state.idx in [0, 1, 3]:
            st.session_state.last_main = st.session_state.idx
            prox_idx = 4
        # Tela branca vai sempre para o Relógio
        elif st.session_state.idx == 4:
            prox_idx = 2
        # Relógio decide qual será a próxima tela de dados
        elif st.session_state.idx == 2:
            if st.session_state.last_main == 0: prox_idx = 1
            elif st.session_state.last_main == 1: prox_idx = 3
            else: prox_idx = 0
            
    st.session_state.idx = prox_idx
    st.session_state.last_time = time.time()
    st.session_state.novo_ciclo = True
    st.rerun()

# 🔊 MOTOR DE ÁUDIO JS (MANTIDO)
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

# =========================================================================
# TELAS
# =========================================================================

# TELA 4: TELA BRANCA
if st.session_state.idx == 4:
    st.markdown('<div style="height: 100vh; width: 100vw; background-color: #ffffff;"></div>', unsafe_allow_html=True)
    st.components.v1.html("", height=0)

# -------------------------------------------------------------------------
# TELA 0: TÉCNICOS NA BASE (Dinâmico sem lista fixa)
# -------------------------------------------------------------------------
elif st.session_state.idx == 0:
    st.markdown(f'''<div class="topo-container">
        <div class="topo-esquerda">{logo_html}</div>
        <div class="topo-centro">🚀 TÉCNICOS EM BASE</div>
        <div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div>
    </div>''', unsafe_allow_html=True)

    if os.path.exists(ARQUIVO_ROTA_DISCO):
        df = pd.read_csv(ARQUIVO_ROTA_DISCO, sep=None, engine='python', dtype=str)
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        col_recurso = next((c for c in df.columns if 'RECURSO' in c or 'NOME' in c), df.columns[0])
        col_status = next((c for c in df.columns if 'STATUS' in c), None)
        col_tipo_exata = next((c for c in df.columns if 'TIPO DE ATIVIDADE3' in c or 'TIPO DE ATIVIDADE 3' in c), None)
        col_sup = next((c for c in df.columns if 'SUPERVISOR' in c), None)

        if col_status:
            mask_status = df[col_status].fillna('').astype(str).str.lower().str.contains('pend')
            
            if col_tipo_exata:
                mask_base = df[col_tipo_exata].fillna('').astype(str).str.strip().str.lower() == 'na base'
            else:
                cols_tipo = [c for c in df.columns if 'TIPO' in c]
                mask_base = df[cols_tipo].apply(lambda col: col.astype(str).str.strip().str.lower() == 'na base').any(axis=1)

            df_tela = df[mask_base & mask_status].copy()
            
            # Aplica inteligência do Supervisor para separar ABC e SP
            if col_sup:
                df_tela['SUP_CLEAN'] = df_tela[col_sup].apply(padronizar_supervisor)
            else:
                df_tela['SUP_CLEAN'] = ''

            cond_sp = df_tela['SUP_CLEAN'].str.contains('ALAN|FRANCISCO|JOAO', na=False)
            
            nomes_sp = sorted([str(n).strip().upper() for n in df_tela[cond_sp][col_recurso].dropna().unique()])
            nomes_abc = sorted([str(n).strip().upper() for n in df_tela[~cond_sp][col_recurso].dropna().unique()])

            c1, c2, c3, c4 = st.columns(4)
            mid_abc = (len(nomes_abc) + 1) // 2
            mid_sp = (len(nomes_sp) + 1) // 2
            
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
                script_cenario = f"<script>{JS_MOTOR_AUDIO}"
                texto_fala = f"Atenção. Existem {len(nomes_abc)} técnicos pendentes na base A B C, e {len(nomes_sp)} na base São Paulo."
                script_cenario += f"anunciarBase('{texto_fala}', 0);\n"
                script_cenario += f"\n// TIMESTAMP_RUN: {time.time()}\n</script>"
                st.session_state.script_audio_atual = script_cenario
                st.session_state.novo_ciclo = False 
            
            st.components.v1.html(st.session_state.script_audio_atual, height=0)
        else: st.error("Coluna Status não encontrada.")
    else: st.error("Ficheiro rota_sincronizada.csv não encontrado.")

# -------------------------------------------------------------------------
# TELA 1: CONTRATOS PENDENTES
# -------------------------------------------------------------------------
elif st.session_state.idx == 1: 
    st.markdown(f'''<div class="topo-container">
        <div class="topo-esquerda">{logo_html}</div>
        <div class="topo-centro">CONTRATOS PENDENTES</div>
        <div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div>
    </div>''', unsafe_allow_html=True)

    if os.path.exists(ARQUIVO_ROTA_DISCO):
        df = pd.read_csv(ARQUIVO_ROTA_DISCO, sep=None, engine='python', dtype=str)
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        col_sup = next((c for c in df.columns if 'SUPERVISOR' in c), None)
        if col_sup:
            df['SUPERVISOR_CLEAN'] = df[col_sup].apply(padronizar_supervisor)
        else:
            df['SUPERVISOR_CLEAN'] = 'NÃO IDENTIFICADO'
            
        col_status_real = next((c for c in df.columns if 'STATUS' in c), None)
        if col_status_real:
            df['Status_Atividade_Upper'] = df[col_status_real].fillna('').astype(str).str.upper().str.strip()
            df_limpo = df[df['Status_Atividade_Upper'] != 'SUSPENSO'].copy()
            df_limpo['P_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('PENDENTE|EM ABERTO|ABERTO|PEND', na=False).astype(int)
            df_limpo['R_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('ROTA|DESLOC|DESLOCAMENTO', na=False).astype(int)
            df_limpo['I_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('INICIADO|PRODUTIVO|EXECUCAO|INIC', na=False).astype(int)
            df_validos = df_limpo[(df_limpo['P_COUNT'] > 0) | (df_limpo['R_COUNT'] > 0) | (df_limpo['I_COUNT'] > 0)].copy()
            
            col_janela = None
            for c in df_validos.columns:
                if 'JANELA' in str(c) or 'INTERVALO' in str(c):
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
                if df_pendentes_geral.empty and df_base_janela.empty: df_pendentes_geral = df_validos[df_validos['P_COUNT'] > 0].copy()
            else: df_pendentes_geral = df_validos[df_validos['P_COUNT'] > 0].copy()

            col_contrato = next((c for c in df_pendentes_geral.columns if 'CONTRATO' in c), None)
            if col_contrato and not df_pendentes_geral.empty:
                df_pendentes_geral[col_contrato] = df_pendentes_geral[col_contrato].fillna('').astype(str).apply(lambda x: str(x).split('.')[0])
                df_pendentes_geral = df_pendentes_geral.drop_duplicates(subset=[col_contrato])

            cond_sp = df_pendentes_geral['SUPERVISOR_CLEAN'].str.contains('ALAN|FRANCISCO|JOAO', na=False) 
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
                    <div class="nome-base" style="color: #03a398;">SÃO PAULO PENDENTES</div>
                    <div class="num-base">{qtd_sp}</div>
                </div>''', unsafe_allow_html=True)

            if SUPERVISORES:
                cols_sup = st.columns(len(SUPERVISORES))
                if st.session_state.novo_ciclo:
                    script_cenario = f"<script>{JS_MOTOR_AUDIO}"
                    script_cenario += f"limparDestaques({len(SUPERVISORES)});\n"
                    script_cenario += f"anunciarBase('Contratos pendentes. A B C: {qtd_abc} pendentes.', 0);\n"
                    script_cenario += f"anunciarBase('São Paulo: {qtd_sp} pendentes.', 7000);\n"
                    for i, sup_full in enumerate(SUPERVISORES):
                        qtd_pendentes = len(df_pendentes_geral[df_pendentes_geral['SUPERVISOR_CLEAN'] == sup_full])
                        nome_visual = obter_nome_visual(sup_full)
                        texto_fala = f"{nome_visual}: {qtd_pendentes} pendentes."
                        script_cenario += f"animarSupervisor('{texto_fala}', {14000 + i * 7000}, {i}, {len(SUPERVISORES)});\n"
                    script_cenario += f"setTimeout(() => limparDestaques({len(SUPERVISORES)}) , {14000 + len(SUPERVISORES) * 7000});\n"
                    script_cenario += f"\n// TIMESTAMP_RUN: {time.time()}\n</script>"
                    st.session_state.script_audio_atual = script_cenario
                    st.session_state.novo_ciclo = False 
                    
                for i, sup_full in enumerate(SUPERVISORES):
                    qtd_pendentes = len(df_pendentes_geral[df_pendentes_geral['SUPERVISOR_CLEAN'] == sup_full])
                    nome_visual = obter_nome_visual(sup_full)
                    with cols_sup[i]:
                        st.markdown(f'''<div id="sup-box-{i}" class="box-contagem">
                            <div class="box-nome">{nome_visual}</div>
                            <div class="box-num">{qtd_pendentes}</div>
                        </div>''', unsafe_allow_html=True)
                st.components.v1.html(st.session_state.script_audio_atual, height=0)
        else:
            st.error("Coluna Status não encontrada.")
    else: st.error("Ficheiro rota_sincronizada.csv não encontrado.")

# -------------------------------------------------------------------------
# TELA 3: INDICADORES
# -------------------------------------------------------------------------
elif st.session_state.idx == 3:
    st.markdown(f'''<div class="topo-container">
        <div class="topo-esquerda">{logo_html}</div>
        <div class="topo-centro">INDICADORES DE CONFORMIDADE</div>
        <div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div>
    </div>''', unsafe_allow_html=True)

    if os.path.exists(ARQUIVO_ROTA_DISCO):
        df_ind = pd.read_csv(ARQUIVO_ROTA_DISCO, sep=None, engine='python', dtype=str)
        df_ind.columns = [str(c).strip().upper() for c in df_ind.columns]
        
        col_status = next((c for c in df_ind.columns if 'STATUS' in c), None)
        col_recurso = next((c for c in df_ind.columns if 'RECURSO' in c or 'NOME' in c), df_ind.columns[0])
        col_nr35 = next((c for c in reversed(df_ind.columns) if 'NR35' in c or 'NR-35' in c), None)
        col_cert = next((c for c in reversed(df_ind.columns) if 'CERTID' in c or 'ELEGIVEL' in c or 'ELEGÍVEL' in c), None)
        col_bst  = next((c for c in reversed(df_ind.columns) if 'BST' in c or 'STEERING' in c or 'BAND' in c), None)

        if col_status:
            status_upper = df_ind[col_status].fillna('').astype(str).str.upper()
            df_prod = df_ind[status_upper.str.contains('CONCL|PRODUTIVO|INIC|EXEC', na=False)].copy()
            
            # Remove duplicados para calcular o % corretamente por técnico único
            df_tec = df_prod.drop_duplicates(subset=[col_recurso]).copy()
            total_tecnicos = len(df_tec) if len(df_tec) > 0 else 1

            pct_nr35, pct_cert, pct_bst = 0, 0, 0
            if col_nr35: pct_nr35 = (len(df_tec[df_tec[col_nr35].fillna('').astype(str).str.upper().str.strip() == 'SIM']) / total_tecnicos) * 100
            if col_cert: pct_cert = (len(df_tec[df_tec[col_cert].fillna('').astype(str).str.upper().str.strip() == 'SIM']) / total_tecnicos) * 100
            if col_bst:  pct_bst = (len(df_tec[df_tec[col_bst].fillna('').astype(str).str.upper().str.strip() == 'SIM']) / total_tecnicos) * 100

            st.markdown(f'''
                <div class="kpi-container-ind">
                    <div class="kpi-card-ind nr35">
                        <div class="ind-title">🪜 NR35</div>
                        <div class="ind-value">{pct_nr35:.0f}%</div>
                    </div>
                    <div class="kpi-card-ind cert">
                        <div class="ind-title">📜 Certidão</div>
                        <div class="ind-value">{pct_cert:.0f}%</div>
                    </div>
                    <div class="kpi-card-ind bst">
                        <div class="ind-title">📶 BST</div>
                        <div class="ind-value">{pct_bst:.0f}%</div>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
            
            if st.session_state.novo_ciclo:
                script_cenario = f"<script>{JS_MOTOR_AUDIO}"
                texto_hora = f"Apresentando indicadores operacionais gerais."
                script_cenario += f"anunciarBase('{texto_hora}', 0);\n"
                script_cenario += f"\n// TIMESTAMP_RUN: {time.time()}\n</script>"
                st.session_state.script_audio_atual = script_cenario
                st.session_state.novo_ciclo = False
                
            st.components.v1.html(st.session_state.script_audio_atual, height=0)
        else:
            st.error("Coluna Status não encontrada.")
    else: st.error("Ficheiro rota_sincronizada.csv não encontrado.")

# -------------------------------------------------------------------------
# TELA 2: HORÁRIO
# -------------------------------------------------------------------------
elif st.session_state.idx == 2:
    st.markdown(f'''<div class="topo-container">
        <div class="topo-esquerda">{logo_html}</div>
        <div class="topo-centro">HORÁRIO</div>
        <div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div>
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
    
    if st.session_state.novo_ciclo:
        script_cenario = f"<script>{JS_MOTOR_AUDIO}"
        texto_hora = f"Hora certa: {hora_fala}."
        script_cenario += f"anunciarBase('{texto_hora}', 0);\n"
        script_cenario += f"\n// TIMESTAMP_RUN: {time.time()}\n</script>"
        st.session_state.script_audio_atual = script_cenario
        st.session_state.novo_ciclo = False
        
    st.components.v1.html(st.session_state.script_audio_atual, height=0)

time.sleep(1)
st.rerun()

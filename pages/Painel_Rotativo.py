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
    
    .box-base { background: #e8f5e9; border-left: 10px solid #2e7d32; padding: 15px 10px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.15); margin-bottom: 10px; }
    .box-base-sp { background: #ffebee; border-left: 10px solid #c62828; padding: 15px 10px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.15); margin-bottom: 10px; }
    .nome-base { font-size: 28px; font-weight: 900; color: #333; text-transform: uppercase;}
    .num-base { font-size: 85px; font-weight: 900; color: #111; line-height: 1.1; }
    
    .box-contagem { 
        background: #f0f2f6; border-left: 8px solid #cc6600; padding: 15px 5px; 
        text-align: center; border-radius: 8px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); 
        margin-top: 15px; margin-left: 10px; margin-right: 10px; margin-bottom: 15px;
        transition: transform 0.5s ease, box-shadow 0.5s ease, background 0.5s ease, border-left 0.5s ease, z-index 0.5s ease; 
        position: relative; z-index: 1; 
    }
    .box-nome { font-size: 18px; font-weight: 900; color: #003366; text-transform: uppercase;}
    .box-num { font-size: 65px; font-weight: 900; color: #cc6600; line-height: 1; }
    
    .destaque-ativo {
        transform: scale(1.30) !important; 
        box-shadow: 0px 25px 45px rgba(204, 102, 0, 0.6) !important;
        border-left: 20px solid #ff8800 !important;
        background: #fff8e1 !important;
        z-index: 9999 !important; 
    }
    
    .relogio-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 60vh; }
    .hora-gigante { font-size: 180px; font-weight: 900; color: #003366; text-shadow: 4px 4px 10px rgba(0,0,0,0.1); line-height: 1; letter-spacing: 5px; }
    .data-media { font-size: 40px; color: #666; font-weight: bold; margin-top: -20px; }
    
    .tec-base-nome { background: #f8f9fa; padding: 8px 12px; border-left: 5px solid #008080; border-radius: 4px; margin-bottom: 8px; font-weight: bold; font-size: 16px; color: #333; box-shadow: 1px 1px 3px rgba(0,0,0,0.1); }
</style>""", unsafe_allow_html=True)

SUPERVISORES_LIST = ["MAICON", "NELSON", "MARCOS ROBERTO", "ALAN", "FRANCISCO GERALDO CARVALHO JUNIOR"]
NOMES_VISUAIS = {
    "MAICON": "MAICON", "NELSON": "NELSON", "MARCOS ROBERTO": "MARCOS ROBERTO", 
    "ALAN": "ALAN", "FRANCISCO GERALDO CARVALHO JUNIOR": "FRANCISCO"
}

# FORÇAR CAMINHO ABSOLUTO PARA GARANTIR QUE SALVA NA PASTA CORRETA
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_EQUIPE = os.path.join(BASE_DIR, "cadastro_equipe.csv")

if not os.path.exists(ARQUIVO_EQUIPE):
    SUP_ORIGINAIS = ["MAICON", "NELSON", "MARCOS ROBERTO", "ALAN", "FRANCISCO GERALDO CARVALHO JUNIOR"]
    SP_ORIGINAIS = [
        "ABNER MAKALAS MARTINS PAULINO", "ADRIANO JOSE DE OLIVEIRA", "ALYSON CAMPOS ANDRADE", "ANTONIO CICERO PEREIRA DA SILVA", "BRUNO CARLOS COUTO CRUZ", "BRUNO MIRANDA SANTOS", "CARLIELTON FERREIRA SANTOS", "CLAYTON IONAMINE", "EDCARLOS PEREIRA DE JESUS", "GETULIO DOS SANTOS CAFE", "GLEMERSON LIMA DE SOUZA", "GUILHERME DE OLIVEIRA DANTAS", "ILTON OLIVEIRA CORREIA", "ISAQUE INACIO BARRETO MENDONCA", "JANAILSON RICARDO FERREIRA DOS SANTOS", "JHONNY DORNELLES DE ALMEIDA", "JOSE CARLOS DA SILVA SANTOS", "LUCAS DE OLIVEIRA SANTOS", "MARCOS VINICIUS BARRETO", "NICHOLAS CZAR LEITAO SANTOS", "RAFAEL GOMES PEREIRA", "RINALDO ANTONIO DA SILVA JUNIOR", "THIAGO ARAUJO SANTOS", "VICENTE RODRIGUES DOS SANTOS", "VINICIUS ARAUJO DA SILVA", "VINICIUS SILVA FARIAS", "VITORIA FERREIRA", "TAILSON JUAN SANTOS DA CONCEICAO", "ALAN CESAR CARDOSO", "ALEXANDRE ROGERIO GONCALVES DE MACEDO", "BARBARA CRISTINA DOS SANTOS PINTO", "BRUNA DA SILVA GOMES FERREIRA", "DOUGLAS WILLIAM SANTOS", "EMERSON DA SILVA", "FABIO OLIVEIRA CAMPOS FARIAS", "FABIO XAVIER CATAO", "FELIPE DE SOUZA OLIVEIRA", "FERNANDO LOPES", "FRANCISCO ALVES FILHO", "FRANKLIM ALVES MAIA", "GUILHERME SILVA DIAS CASTRO", "HELVIO STAFF", "JOAO CARLOS MIRON", "JOSE MARCIO DA SILVA VELOSO", "LUCAS FREIRIA PINTO", "MANOELA MIRANDA", "MATHEUS DOS SANTOS OLIVEIRA", "PEDRO LUIZ FEREEIRA CORREA", "PEDRO OLIVEIRA CARLOS DA SILVA", "RAFAELA SANTOS SILVA", "ROBSON SANTIAGO DA LUZ", "TIAGO MEIRA DA SILVA", "VALMIR RAMOS", "VITOR OLIVEIRA DA SILVA", "WELLINGTON GOMES DE OLIVEIRA", "DIEGO FRAGOSO DE BRITO"
    ]
    ABC_ORIGINAIS = [
        "ADRIEL ALEXANDER DE LIMA", "AIRON HENRIQUE FERREIRA MINA", "ALAN RODRIGUES COSTA", "ALEX BERNARDES DA SILVA", "ALINE CAMARGO PIRES", "AMANDA CAROLINE DOS SANTOS", "ANA LUISA CULAU SILVA", "ANDERSON MARCELO LOPES DOS SANTOS", "ANTONIO WESLEY HOLANDA DA SILVA", "AUGUSTO ERNANDES DA SILVA", "BRUNO MARTINS AVELINO", "CARLOS ALBERTO LIMA REBOUÇAS", "CARLOS EDUARDO DA SILVA CONCEICAO", "DANIEL SOUZA OLIVEIRA", "DANILO FERREIRA LIMA", "DEBORA BENEVENUTO PEREIRA", "DOMINGOS PEREIRA DA SILVA", "EDER SALES MONTEIRO", "EDSON JAIRO DE ALMEIDA SOUSA", "EDUARDO FERNANDES BERNARDO DE MELO", "ELIAS AGUIAR LOPES", "ENOQUE FERREIRA SANTOS FILHO", "ERICK PAULO FERREIRA DA SILVA", "ERIK CASSIMIRO DA SILVA GOMES", "ESTEVAM MATEUS GONCALVES", "FABIO OLIVEIRA MOURA", "FELIPI ANTONIO DA SILVA", "FRANCISCO IGOR SOARES DA SILVA", "HELTON LIMA DE QUEIROZ", "IGOR DA SILVA VAYDA", "JAKSON DE JESUS E SILVA", "JEANDERSON SOUZA BERTO DA SILVA", "JEFFERSON BRANDAO BASTOS", "JEFFERSON FRANCISCO DA SILVA", "JOANDERSON LOPES DA CONCEIÇÃO", "JOAO BATISTA DE LIMA TOME", "JUSCIELIO LIRA DE OLIVEIRA", "LEANDRO SOARES DA SILVA", "LEONARDO BESERRA DOS SANTOS", "LUCAS SILVA DE LIMA", "MAICON JORDAN PEDRO SANTOS GARCEZ", "LUIS HENRIQUE GOMES DA SILVA", "MARCOS VINICIUS OLIVEIRA GOVEIA", "NATALIA SANT ANA VELASCO", "MATHEUS BOAVENTURA DA SILVA", "OSCLEY FRANCA DE SOUSA", "ODIRLEI APARECIDO PIERETI", "PATRICIA DE ARAUJO RAMALHO", "PABLO WILLIAM DA SILVA", "RENATO FUTRO ROSSI", "PAULO CESAR BATISTA DE SOUSA", "RAFAEL DOS ANJOS BAPTISTA ONOFRE", "SIDNEY ROSENDO DA SILVA", "RICARDO SANTOS", "RODRIGO FEITOZA DA SILVA", "VICTOR MENDES DOS SANTOS", "SILAS DA SILVA NASCIMENTO", "YURI URCESINO COSTA", "WESLAYNE CELINA FERREIRA SILVA", "ALESSANDRO RAMOS DA SILVA", "ALICE EULINA SILVA", "BRUNO PINHEIRO MAGALHAES", "KAUE BARBEIRO SOARES", "ENZO RUBENS ARAUJO MACIEL", "HAMILTON RICARDO INACIO", "WILLIAM BORGES DOS SANTOS", "LUIS GUSTAVO CECCONELLO", "CLEBER FERREIRA SANTOS", "DANIEL AUGUSTO PEREIRA", "JULIO CESAR SILVA DOS SANTOS", "MATHEUS DA SILVA NASCIMENTO"
    ]
    dados_iniciais = [{"NOME": n, "FUNCAO": "SUPERVISOR", "BASE": "GERAL"} for n in SUP_ORIGINAIS]
    dados_iniciais += [{"NOME": n, "FUNCAO": "TECNICO", "BASE": "SP"} for n in SP_ORIGINAIS]
    dados_iniciais += [{"NOME": n, "FUNCAO": "TECNICO", "BASE": "ABC"} for n in ABC_ORIGINAIS]
    pd.DataFrame(dados_iniciais).to_csv(ARQUIVO_EQUIPE, index=False, sep=',')

df_equipe = pd.read_csv(ARQUIVO_EQUIPE)
SUPERVISORES = df_equipe[df_equipe["FUNCAO"] == "SUPERVISOR"]["NOME"].tolist()
LISTA_SP_FIXA = df_equipe[(df_equipe["FUNCAO"] == "TECNICO") & (df_equipe["BASE"] == "SP")]["NOME"].tolist()
LISTA_ABC_FIXA = df_equipe[(df_equipe["FUNCAO"] == "TECNICO") & (df_equipe["BASE"] == "ABC")]["NOME"].tolist()

def obter_nome_visual(nome_completo):
    n = str(nome_completo).upper()
    if 'FRANCISCO' in n: return "FRANCISCO"
    if 'MARCOS' in n: return "MARCOS ROBERTO"
    return n.split()[0]

if "novos_sp" not in st.session_state: st.session_state["novos_sp"] = []
if "novos_abc" not in st.session_state: st.session_state["novos_abc"] = []

if "idx" not in st.session_state: 
    st.session_state.idx = 0
    st.session_state.last_time = time.time()
    st.session_state.novo_ciclo = True
    st.session_state.script_audio_atual = ""

agora_br = datetime.utcnow() - timedelta(hours=3)
antes_0825 = (agora_br.hour < 8) or (agora_br.hour == 8 and agora_br.minute < 25)

if st.session_state.idx == 0: espera = 40  
elif st.session_state.idx == 1: espera = 55 
else: espera = 20 

tempo_passado = time.time() - st.session_state.last_time

if tempo_passado > espera:
    prox_idx = st.session_state.idx + 1
    if prox_idx > 2: prox_idx = 0
    if antes_0825 and prox_idx == 1: prox_idx = 2 
    elif not antes_0825 and prox_idx == 0: prox_idx = 1 
    st.session_state.idx = prox_idx 
    st.session_state.last_time = time.time()
    st.session_state.novo_ciclo = True
    st.rerun()

JS_MOTOR_AUDIO = """
function tocarAlertaChamaAtencao() {
    try {
        let ctx = new (window.AudioContext || window.webkitAudioContext)();
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
            let m = new SpeechSynthesisUtterance(texto);
            m.lang = 'pt-BR'; m.rate = 1.0; m.volume = 1.0; 
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
            let m = new SpeechSynthesisUtterance(texto);
            m.lang = 'pt-BR'; m.rate = 1.0; m.volume = 1.0; 
            let voices = window.speechSynthesis.getVoices();
            let vozLuciana = voices.find(v => v.name.includes('Luciana')) || voices.find(v => v.name.includes('Maria')) || voices.find(v => v.lang.includes('pt-BR'));
            if(vozLuciana) { m.voice = vozLuciana; }
            window.speechSynthesis.speak(m);
        }, 1500);
    }, delay);
}
"""

tela_placeholder = st.empty()
tela_placeholder.empty()

with tela_placeholder.container():
    if st.session_state.idx == 0:
        st.markdown(f'''<div class="topo-container">
            <div class="nome-sup">🚀 TÉCNICOS EM BASE</div>
            <a href="/" style="color:#fff; font-size:18px; font-weight:bold; border:2px solid #fff; padding:8px 15px; border-radius:5px; text-decoration:none;">🏠 HOME</a>
        </div>''', unsafe_allow_html=True)

        if os.path.exists("rota_sincronizada.csv"):
            df = pd.read_csv("rota_sincronizada.csv", dtype=str)
            df.columns = [str(c).strip() for c in df.columns]
            col_tipo = 'Tipo de Atividade.1' if 'Tipo de Atividade.1' in df.columns else ('Tipo de Atividade' if 'Tipo de Atividade' in df.columns else None)
            col_status = 'Status da Atividade' if 'Status da Atividade' in df.columns else 'STATUS_ATIVIDADE'
            
            if col_tipo and col_status:
                df_tela = df[(df[col_tipo].astype(str).str.contains('NA BASE', na=False, case=False)) & (df[col_status].astype(str).str.contains('PENDENTE', na=False, case=False))].copy()
                nomes_na_base = sorted(df_tela['Recurso'].dropna().unique().tolist())
                lista_sp = [n.upper() for n in LISTA_SP_FIXA] + [n.upper() for n in st.session_state["novos_sp"]]
                lista_abc = [n.upper() for n in LISTA_ABC_FIXA] + [n.upper() for n in st.session_state["novos_abc"]]
                nomes_abc = [n for n in nomes_na_base if str(n).upper() in lista_abc or str(n).upper() not in lista_sp]
                nomes_sp = [n for n in nomes_na_base if str(n).upper() in lista_sp]

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

                st.divider()
                with st.expander("➕ Incluir Novo Técnico Temporário (Só para hoje)"):
                    c_a, c_b, c_c = st.columns([2, 1, 1])
                    nome_i = c_a.text_input("Nome:").upper()
                    base_i = c_b.selectbox("Base:", ["SP", "ABC"])
                    if c_c.button("Adicionar"):
                        if nome_i:
                            if base_i == "SP": st.session_state["novos_sp"].append(nome_i)
                            else: st.session_state["novos_abc"].append(nome_i)
                            st.rerun()

                if st.session_state.novo_ciclo:
                    script_cenario = f"<script>{JS_MOTOR_AUDIO}"
                    texto_fala = f"Atenção. Existem {len(nomes_abc)} técnicos pendentes na base A B C, e {len(nomes_sp)} na base São Paulo."
                    script_cenario += f"anunciarBase('{texto_fala}', 0);\n"
                    script_cenario += f"\n// TIMESTAMP_RUN: {time.time()}\n</script>"
                    st.session_state.script_audio_atual = script_cenario
                    st.session_state.novo_ciclo = False 
                st.components.v1.html(st.session_state.script_audio_atual, height=0)
            else: st.error("Colunas não encontradas.")
        else: st.error("Ficheiro rota_sincronizada.csv não encontrado.")

    elif st.session_state.idx == 1: 
        st.markdown(f'''<div class="topo-container">
            <div class="nome-sup">CONTRATOS PENDENTES</div>
            <a href="/" style="color:#fff; font-size:18px; font-weight:bold; border:2px solid #fff; padding:8px 15px; border-radius:5px; text-decoration:none;">🏠 HOME</a>
        </div>''', unsafe_allow_html=True)

        if os.path.exists("rota_sincronizada.csv"):
            df = pd.read_csv("rota_sincronizada.csv", dtype=str)
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
                if df_pendentes_geral.empty and df_base_janela.empty: df_pendentes_geral = df_validos[df_validos['P_COUNT'] > 0].copy()
            else: df_pendentes_geral = df_validos[df_validos['P_COUNT'] > 0].copy()

            if 'Contrato' in df_pendentes_geral.columns and not df_pendentes_geral.empty:
                df_pendentes_geral['Contrato'] = df_pendentes_geral['Contrato'].fillna('').astype(str).apply(lambda x: str(x).split('.')[0])
                df_pendentes_geral = df_pendentes_geral.drop_duplicates(subset=['Contrato'])

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
                script_cenario += f"setTimeout(() => limparDestaques({len(SUPERVISORES)}), {14000 + len(SUPERVISORES) * 7000});\n"
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
        else: st.error("Ficheiro rota_sincronizada.csv não encontrado.")

    elif st.session_state.idx == 2:
        st.markdown(f'''<div class="topo-container">
            <div class="nome-sup">HORÁRIO</div>
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
        if st.session_state.novo_ciclo:
            script_cenario = f"<script>{JS_MOTOR_AUDIO}"
            script_cenario += f"anunciarBase('Atenção. Hora certa: {hora_fala}.', 0);\n"
            script_cenario += f"\n// TIMESTAMP_RUN: {time.time()}\n</script>"
            st.session_state.script_audio_atual = script_cenario
            st.session_state.novo_ciclo = False
        st.components.v1.html(st.session_state.script_audio_atual, height=0)

time.sleep(1); st.rerun()

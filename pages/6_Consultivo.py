import streamlit as st
import pandas as pd
import os
import time
import base64
import calendar
import unicodedata
from datetime import datetime, timedelta

st.set_page_config(page_title="Consultivo", layout="wide")

ROOT_DIR = os.getcwd()
ARQUIVO_CONSULTIVO = os.path.join(ROOT_DIR, "consultivo_sincronizado.csv")
ARQUIVO_LOGO = os.path.join(ROOT_DIR, "logo.png")

if not os.path.exists(ARQUIVO_LOGO):
    ARQUIVO_LOGO = os.path.join(ROOT_DIR, "pages", "logo.png")

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
    
    .stApp { background-color: #ffffff !important; }
    .topo-container { background: #003366; color: white; padding: 0px 30px; border-radius: 0 0 15px 15px; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; margin-bottom: 25px; height: 100px; }
    .topo-esquerda { display: flex; justify-content: flex-start; align-items: center; height: 100%; }
    .topo-centro { font-size: 45px; font-weight: 900; text-align: center; white-space: nowrap; }
    .topo-direita { display: flex; justify-content: flex-end; align-items: center; }
    .botao-home { color: #fff; font-size: 18px; font-weight: bold; border: 2px solid #fff; padding: 8px 15px; border-radius: 5px; text-decoration: none; }
    
    .box-base { background: #e8f5e9; border-left: 10px solid #2e7d32; padding: 15px 10px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.15); margin-bottom: 25px; }
    .nome-base { font-size: 22px; font-weight: 900; color: #333; text-transform: uppercase;}
    .num-base { font-size: 85px; font-weight: 900; color: #111; line-height: 1.1; }
    
    .sup-card { background: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .sup-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 10px; }
    .sup-name { font-size: 24px; font-weight: 900; color: #333; text-transform: uppercase; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}
    .badge-faltas { font-size: 14px; font-weight: bold; padding: 6px 12px; border-radius: 6px; border: 1px solid transparent; }
    
    .faltas-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }
    .falta-box { border-radius: 6px; padding: 12px 5px; text-align: center; margin-bottom: 5px; border: 1px solid transparent; }
    .falta-label { font-size: 11px; font-weight: bold; text-transform: uppercase; margin-bottom: 6px; }
    .falta-value { font-size: 32px; font-weight: 900; line-height: 1; }
</style>""", unsafe_allow_html=True)

SUPS_ABC = ["EDSON MARCO", "MAICON", "MARCOS ROBERTO", "NELSON"]
SUPERVISORES_ORDENADOS = SUPS_ABC

def obter_nome_visual(nome_completo):
    n = str(nome_completo).upper()
    if 'MARCOS' in n: return "MARCOS ROBERTO"
    if 'EDSON' in n: return "EDSON MARCO"
    if 'MAICON' in n: return "MAICON"
    if 'NELSON' in n: return "NELSON"
    return n.split()[0]

def limpar_texto(txt):
    if pd.isna(txt): return ''
    return unicodedata.normalize('NFKD', str(txt).strip().upper()).encode('ASCII', 'ignore').decode('utf-8')

st.markdown(f'''<div class="topo-container">
    <div class="topo-esquerda">{logo_html}</div>
    <div class="topo-centro">CONSULTIVO</div>
    <div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div>
</div>''', unsafe_allow_html=True)

if os.path.exists(ARQUIVO_CONSULTIVO):
    try:
        df_cons = pd.read_csv(ARQUIVO_CONSULTIVO, sep=None, engine='python', dtype=str)
        df_cons.columns = [unicodedata.normalize('NFKD', str(c)).encode('ASCII', 'ignore').decode('utf-8').strip().upper().replace(' ', '_') for c in df_cons.columns]

        if 'BASE' in df_cons.columns:
            df_cons['BASE'] = df_cons['BASE'].apply(limpar_texto)
        else:
            df_cons['BASE'] = 'N/D'

        col_qtd = next((c for c in df_cons.columns if 'QTD' in c and 'PRODUTO' in c), None)
        if col_qtd:
            df_cons['QTD_PRODUTOS_CALC'] = pd.to_numeric(df_cons[col_qtd].astype(str).str.replace(',', '.'), errors='coerce').fillna(0).astype(int)
        else:
            df_cons['QTD_PRODUTOS_CALC'] = 0

        df_cons['SUPERVISOR'] = df_cons['SUPERVISOR'].apply(limpar_texto) if 'SUPERVISOR' in df_cons.columns else ''

        def classificar_supervisor_limpo(row):
            texto_celula = row.get('SUPERVISOR', '')
            for oficial in SUPERVISORES_ORDENADOS:
                primeiro_nome = limpar_texto(oficial.split()[0])
                if primeiro_nome in texto_celula:
                    return oficial
            return "DESCARTADO"

        df_cons['SUPERVISOR_CLEAN'] = df_cons.apply(classificar_supervisor_limpo, axis=1)
        df_cards = df_cons[df_cons['SUPERVISOR_CLEAN'] != "DESCARTADO"].copy()

        total_realizado_abc = df_cards['QTD_PRODUTOS_CALC'].sum()

        hoje = datetime.utcnow() - timedelta(hours=3)
        ano, mes = hoje.year, hoje.month
        
        _, num_dias = calendar.monthrange(ano, mes)
        dias_uteis_totais = sum(1 for d in range(1, num_dias + 1) if calendar.weekday(ano, mes, d) != 6)
        dias_restantes = sum(1 for d in range(hoje.day, num_dias + 1) if calendar.weekday(ano, mes, d) != 6)
        if dias_restantes == 0: dias_restantes = 1

        meta_mensal_abc = len(SUPS_ABC) * 350
        ritmo_diario_base_abc = int(meta_mensal_abc / dias_uteis_totais) if dias_uteis_totais > 0 else 0

        st.markdown(f'''<div class="box-base">
            <div class="nome-base" style="color: #2e7d32;">🏢 ABC TOTAL (Meta: {meta_mensal_abc} | Ritmo: {ritmo_diario_base_abc}/dia)</div>
            <div class="num-base">{total_realizado_abc}</div>
        </div>''', unsafe_allow_html=True)
        
        cols_abc = st.columns(4)
        for i, sup in enumerate(SUPS_ABC):
            with cols_abc[i % 4]:
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
                        <div class="falta-box" style="background-color: #ffebee; border-color: #ffcdd2;">
                            <div class="falta-label" style="color: #c62828;">📉 FALTA PARA META</div>
                            <div class="falta-value" style="color: #b30000;">{falta_individual}</div>
                        </div>
                        <div class="falta-box" style="background-color: #fff8e1; border-color: #ffe082;">
                            <div class="falta-label" style="color: #b78103;">🎯 META DIÁRIA</div>
                            <div class="falta-value" style="color: #b78103;">{ritmo_diario_individual}</div>
                        </div>
                    </div>
                </div>''', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Erro ao processar dados: {e}")
else: 
    st.warning("Aguardando sincronização da planilha master para carregar o Consultivo...")

time.sleep(60)
st.rerun()

import streamlit as st
import pandas as pd
import os
import calendar
import unicodedata
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# --- CSS E ESTILOS ---
st.markdown("""<style>
    .topo-container { background: #003366; color: white; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px; }
    .sup-card { background: #ffffff; border: 1px solid #e0e0e0; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    .sup-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 15px; }
    .sup-name { font-size: 32px; font-weight: 900; color: #333; text-transform: uppercase; }
    .badge-acumulado { background: #e8f5e9; color: #2e7d32; padding: 8px 16px; border-radius: 8px; font-size: 18px; font-weight: bold; border: 1px solid #a5d6a7; }
    .faltas-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; }
    .falta-box { border-radius: 8px; padding: 15px; text-align: center; border: 1px solid #eee; background-color: #f9f9f9; }
    .falta-label { font-size: 14px; font-weight: bold; text-transform: uppercase; margin-bottom: 8px; color: #666; }
    .falta-value { font-size: 45px; font-weight: 900; color: #003366; line-height: 1; }
</style>""", unsafe_allow_html=True)

st.markdown('<div class="topo-container"><h1>PERFORMANCE CONSULTIVO DIÁRIO</h1></div>', unsafe_allow_html=True)

# --- CONFIGURAÇÕES ---
ARQUIVO_CONSULTIVO = os.path.join(os.getcwd(), "consultivo_sincronizado.csv")
SUPS_ABC = ["EDSON MARCO", "MARCOS ROBERTO", "NELSON"]
SUPS_SP = ["ALAN", "FRANCISCO", "JOAO CARLOS MIRON"]
SUPERVISORES_ORDENADOS = SUPS_ABC + SUPS_SP

def limpar_texto(txt):
    if pd.isna(txt): return ''
    return unicodedata.normalize('NFKD', str(txt).strip().upper()).encode('ASCII', 'ignore').decode('utf-8')

def obter_nome_visual(n):
    n = str(n).upper()
    if 'FRANCISCO' in n: return "FRANCISCO"
    if 'MARCOS' in n: return "MARCOS ROBERTO"
    if 'EDSON' in n: return "EDSON MARCO"
    if 'JOAO' in n or 'MIRON' in n: return "JOÃO CARLOS"
    if 'NELSON' in n: return "NELSON"
    if 'ALAN' in n: return "ALAN"
    return n.split()[0]

# --- LÓGICA DE PROCESSAMENTO ---
if os.path.exists(ARQUIVO_CONSULTIVO):
    try:
        # Carrega o arquivo
        df_cons = pd.read_csv(ARQUIVO_CONSULTIVO, sep=None, engine='python', dtype=str)
        df_cons.columns = [str(c).upper().strip().replace(' ', '_') for c in df_cons.columns]
        
        # Limpeza básica
        df_cons['SUPERVISOR'] = df_cons['SUPERVISOR'].fillna('#N/D').apply(limpar_texto)
        df_cons['BASE'] = df_cons['BASE'].fillna('N/D').apply(limpar_texto)
        df_cons['QTD_PRODUTOS'] = pd.to_numeric(df_cons['QTD_PRODUTOS'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
        
        # Filtra apenas supervisores válidos
        df_cards = df_cons[df_cons['SUPERVISOR'] != 'DESCARTADO'].copy()
        
        # Define o dia de hoje
        hoje = datetime.utcnow() - timedelta(hours=3)
        hoje_str = hoje.strftime('%d/%m/%Y')
        
        # Criação de objetos de data reais para filtros de período (Essencial para os cálculos de "Até Ontem")
        df_cards['DATA_DT'] = pd.to_datetime(df_cards['DATA'], dayfirst=True, errors='coerce')
        hoje_dt = pd.to_datetime(hoje.date())
        
        # Cálculos de dias úteis restantes
        _, num_dias = calendar.monthrange(hoje.year, hoje.month)
        dias_restantes = sum(1 for d in range(hoje.day, num_dias + 1) if calendar.weekday(hoje.year, hoje.month, d) != 6)
        if dias_restantes == 0: dias_restantes = 1
        
        col_abc, col_sp = st.columns(2)
        
        def render_base(base, col, sups):
            with col:
                st.subheader(f"BASE {base}")
                for s in sups:
                    # Filtro base por supervisor e região
                    df_sup_total = df_cards[df_cards['SUPERVISOR'].str.contains(s.split()[0], na=False) & (df_cards['BASE'] == base)]
                    
                    # 1. Pega as vendas específicas do dia de hoje na planilha
                    df_sup_hoje = df_sup_total[df_sup_total['DATA_DT'] == hoje_dt]
                    qtd_hoje = df_sup_hoje['QTD_PRODUTOS'].sum()
                    
                    # 2. Pega as vendas acumuladas estritamente ANTES de hoje (Até Ontem)
                    df_sup_ate_ontem = df_sup_total[df_sup_total['DATA_DT'] < hoje_dt]
                    qtd_mes_anterior = df_sup_ate_ontem['QTD_PRODUTOS'].sum()
                    
                    # 3. Qtd total do mês inteiro (Acumulado Real que aparece no topo do Card)
                    qtd_mes_total = df_sup_total['QTD_PRODUTOS'].sum()
                    
                    # 4. Cálculos adaptados e corrigidos utilizando o histórico anterior
                    meta_dia = round(max(0, 350 - qtd_mes_anterior) / dias_restantes, 1)
                    falta_hoje = round(max(0, meta_dia - qtd_hoje), 1)
                    
                    st.markdown(f'''
                    <div class="sup-card">
                        <div class="sup-header">
                            <div class="sup-name">📋 {obter_nome_visual(s)}</div>
                            <div class="badge-acumulado">Acumulado: {int(qtd_mes_total)}</div>
                        </div>
                        <div class="faltas-grid">
                            <div class="falta-box"><div class="falta-label">📦 HOJE</div><div class="falta-value">{int(qtd_hoje)}</div></div>
                            <div class="falta-box"><div class="falta-label">📉 FALTAM</div><div class="falta-value">{falta_hoje}</div></div>
                            <div class="falta-box"><div class="falta-label">🎯 META DIA</div><div class="falta-value">{meta_dia}</div></div>
                        </div>
                    </div>''', unsafe_allow_html=True)

        render_base('ABC', col_abc, SUPS_ABC)
        render_base('SP', col_sp, SUPS_SP)

    except Exception as e:
        st.error(f"Erro ao processar os dados: {e}")
        st.write("Verifique se as colunas 'DATA', 'SUPERVISOR', 'BASE' e 'QTD_PRODUTOS' existem no seu CSV.")
else:
    st.error("Arquivo consultivo_sincronizado.csv não encontrado na pasta raiz.")

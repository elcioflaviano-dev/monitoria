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

# --- LÓGICA DE PROCESSAMENTO (Tudo dentro do IF para evitar erros) ---
if os.path.exists(ARQUIVO_CONSULTIVO):
    try:
        # Carrega o arquivo
        df_cons = pd.read_csv(ARQUIVO_CONSULTIVO, sep=None, engine='python', dtype=str)
        df_cons.columns = [str(c).upper().strip().replace(' ', '_') for c in df_cons.columns]
        
        # Limpeza básica
        df_cons['SUPERVISOR'] = df_cons['SUPERVISOR'].fillna('#N/D').apply(limpar_texto)
        df_cons['BASE'] = df_cons['BASE'].fillna('N/D').apply(limpar_texto)
        
        # Converte coluna de quantidade para numérico (Ajuste 'QTD_PRODUTOS' se o nome no CSV for diferente)
        df_cons['QTD_PRODUTOS'] = pd.to_numeric(df_cons['QTD_PRODUTOS'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)

        # Filtra apenas supervisores válidos
        df_cons = df_cons[df_cons['SUPERVISOR'] != 'DESCARTADO'].copy()
        
        # Define o dia de hoje
        hoje = datetime.utcnow() - timedelta(hours=3)
        hoje_str = hoje.strftime('%d/%m/%Y')
        
        # Converte DATA para string para comparação
        df_cons['DATA_STR'] = pd.to_datetime(df_cons['DATA'], dayfirst=True, errors='coerce').dt.strftime('%d/%m/%Y')
        df_hoje = df_cons[df_cons['DATA_STR'] == hoje_str].copy()
        
        # Cálculos de dias úteis
        _, num_dias = calendar.monthrange(hoje.year, hoje.month)
        dias_restantes = sum(1 for d in range(hoje.day, num_dias + 1) if calendar.weekday(hoje.year, hoje.month, d) != 6)
        if dias_restantes == 0: dias_restantes = 1
        
        col_abc, col_sp = st.columns(2)
        
        def render_base(base, col, sups):
            with col:
                st.subheader(f"BASE {base}")
                for s in sups:
                    # Filtra supervisor por parte do nome
                    df_sup_mes = df_cons[df_cons['SUPERVISOR'].str.contains(s.split()[0], na=False) & (df_cons['BASE'] == base)]
                    df_sup_hoje = df_hoje[df_hoje['SUPERVISOR'].str.contains(s.split()[0], na=False) & (df_hoje['BASE'] == base)]
                    
                    qtd_mes = df_sup_mes['QTD_PRODUTOS'].sum()
                    qtd_hoje = df_sup_hoje['QTD_PRODUTOS'].sum()
                    
                    meta_dia = round(max(0, 350 - qtd_mes) / dias_restantes, 1)
                    falta_hoje = round(max(0, meta_dia - qtd_hoje), 1)
                    
                    st.markdown(f'''
                    <div class="sup-card">
                        <div class="sup-header">
                            <div class="sup-name">📋 {s}</div>
                            <div class="badge-acumulado">Acumulado: {int(qtd_mes)}</div>
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

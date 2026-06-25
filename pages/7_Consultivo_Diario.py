import streamlit as st
import pandas as pd
import os
import calendar
import unicodedata
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# --- CSS E ESTILOS (Mantendo o layout padrão) ---
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

def obter_nome_visual(n):
    n = str(n).upper()
    if 'FRANCISCO' in n: return "FRANCISCO"
    if 'MARCOS' in n: return "MARCOS ROBERTO"
    if 'EDSON' in n: return "EDSON MARCO"
    if 'JOAO' in n or 'MIRON' in n: return "JOÃO CARLOS"
    return n.split()[0]

# --- LÓGICA DE PROCESSAMENTO ---
if os.path.exists(ARQUIVO_CONSULTIVO):
    try:
        # Carrega dados
        df = pd.read_csv(ARQUIVO_CONSULTIVO, sep=None, engine='python', dtype=str)
        df.columns = [str(c).upper().strip().replace(' ', '_') for c in df.columns]
        
        # Limpeza
        df['SUPERVISOR'] = df['SUPERVISOR'].fillna('#N/D').apply(limpar_texto)
        df['BASE'] = df['BASE'].fillna('N/D').apply(limpar_texto)
        df['QTD_PRODUTOS'] = pd.to_numeric(df['QTD_PRODUTOS'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
        
        # Filtro de data seguro
        hoje = datetime.utcnow() - timedelta(hours=3)
        hoje_str = hoje.strftime('%d/%m/%Y')
        df['DATA_FORMATADA'] = pd.to_datetime(df['DATA'], dayfirst=True, errors='coerce').dt.strftime('%d/%m/%Y')
        
        # Filtra apenas supervisores válidos
        df_valid = df[df['SUPERVISOR'] != 'DESCARTADO'].copy()
        df_hoje = df_valid[df_valid['DATA_FORMATADA'] == hoje_str].copy()
        
        # Cálculo de dias úteis restantes
        _, num_dias = calendar.monthrange(hoje.year, hoje.month)
        dias_restantes = sum(1 for d in range(hoje.day, num_dias + 1) if calendar.weekday(hoje.year, hoje.month, d) != 6)
        if dias_restantes == 0: dias_restantes = 1
        
        col_abc, col_sp = st.columns(2)
        
        # Função para renderizar
        def processar_supervisor(base, col, lista_sups):
            with col:
                st.subheader(f"BASE {base}")
                for s in lista_sups:
                    # Filtra supervisor pelo primeiro nome
                    df_s = df_valid[df_valid['SUPERVISOR'].str.contains(s.split()[0], na=False) & (df_valid['BASE'] == base)]
                    df_s_hoje = df_hoje[df_hoje['SUPERVISOR'].str.contains(s.split()[0], na=False) & (df_hoje['BASE'] == base)]
                    
                    qtd_mes = df_s['QTD_PRODUTOS'].sum()
                    qtd_hoje = df_s_hoje['QTD_PRODUTOS'].sum()
                    
                    # CÁLCULO DA META: (350 - Acumulado) / Dias Restantes
                    meta_dia = round(max(0, 350 - qtd_mes) / dias_restantes, 1)
                    falta_hoje = round(max(0, meta_dia - qtd_hoje), 1)
                    
                    st.markdown(f'''
                    <div class="sup-card">
                        <div class="sup-header">
                            <div class="sup-name">📋 {obter_nome_visual(s)}</div>
                            <div class="badge-acumulado">Acumulado: {int(qtd_mes)}</div>
                        </div>
                        <div class="faltas-grid">
                            <div class="falta-box"><div class="falta-label">📦 HOJE</div><div class="falta-value">{int(qtd_hoje)}</div></div>
                            <div class="falta-box"><div class="falta-label">📉 FALTAM</div><div class="falta-value">{falta_hoje}</div></div>
                            <div class="falta-box"><div class="falta-label">🎯 META DIA</div><div class="falta-value">{meta_dia}</div></div>
                        </div>
                    </div>''', unsafe_allow_html=True)

        processar_supervisor('ABC', col_abc, SUPS_ABC)
        processar_supervisor('SP', col_sp, SUPS_SP)

    except Exception as e:
        st.error(f"Erro ao processar arquivo: {e}")
        st.write("Verifique se as colunas DATA, SUPERVISOR, BASE e QTD_PRODUTOS estão corretas.")
else:
    st.error("Arquivo consultivo_sincronizado.csv não encontrado.")

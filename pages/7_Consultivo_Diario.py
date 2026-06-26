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
    .box-base { background: #e8f5e9; border-left: 10px solid #2e7d32; padding: 20px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.15); margin-bottom: 25px; }
    .box-base-sp { background: #e0f2f1; border-left: 10px solid #00897b; padding: 20px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 8px rgba(0,0,0,0.15); margin-bottom: 25px; }
    .nome-base { font-size: 20px; font-weight: 900; color: #333; text-transform: uppercase; margin-bottom: 10px; }
    .num-base { font-size: 70px; font-weight: 900; color: #111; line-height: 1; }
    
    .sup-card { background: #ffffff; border: 1px solid #e0e0e0; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    .sup-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding-bottom: 15px; margin-bottom: 15px; }
    .sup-name { font-size: 28px; font-weight: 900; color: #333; text-transform: uppercase; }
    .badge-acumulado { background: #e8f5e9; color: #2e7d32; padding: 8px 16px; border-radius: 8px; font-size: 16px; font-weight: bold; border: 1px solid #a5d6a7; }
    
    .faltas-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; }
    .falta-box { border-radius: 8px; padding: 15px; text-align: center; border: 1px solid #eee; background-color: #f9f9f9; }
    .falta-label { font-size: 14px; font-weight: bold; text-transform: uppercase; margin-bottom: 8px; color: #666; }
    .falta-value { font-size: 45px; font-weight: 900; color: #003366; line-height: 1; }
</style>""", unsafe_allow_html=True)

st.markdown('<div class="topo-container"><h1>PERFORMANCE CONSULTIVO DIÁRIO</h1></div>', unsafe_allow_html=True)

# --- CONFIGURAÇÕES GERAIS ---
ARQUIVO_CONSULTIVO = os.path.join(os.getcwd(), "consultivo_sincronizado.csv")
SUPS_ABC = ["EDSON MARCO", "MARCOS ROBERTO", "NELSON"]
SUPS_SP = ["ALAN", "FRANCISCO", "JOAO CARLOS MIRON"]
SUPERVISORES_ORDENADOS = SUPS_ABC + SUPS_SP

def limpar_texto(txt):
    if pd.isna(txt): return ''
    return unicodedata.normalize('NFKD', str(txt).strip().upper()).encode('ASCII', 'ignore').decode('utf-8')

# --- LÓGICA DE PROCESSAMENTO ---
if os.path.exists(ARQUIVO_CONSULTIVO):
    try:
        df = pd.read_csv(ARQUIVO_CONSULTIVO, sep=None, engine='python', dtype=str)
        df.columns = [str(c).upper().strip().replace(' ', '_') for c in df.columns]
        
        # Limpeza
        df['BASE_CLEAN'] = df['BASE'].fillna('N/D').apply(limpar_texto)
        df['SUP_CLEAN'] = df['SUPERVISOR'].fillna('#N/D').apply(limpar_texto)
        df['QTD_CALC'] = pd.to_numeric(df['QTD_PRODUTOS'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
        
        def classificar_sup(row):
            for oficial in SUPERVISORES_ORDENADOS:
                if limpar_texto(oficial.split()[0]) in row: return oficial
            return "DESCARTADO"
        
        df['SUP_FINAL'] = df['SUP_CLEAN'].apply(classificar_sup)
        df_cards = df[df['SUP_FINAL'] != 'DESCARTADO'].copy()

        # 🔥 TRATAMENTO DE DATA ---
        hoje_real = datetime.utcnow() - timedelta(hours=3)
        hoje_str = hoje_real.strftime('%d/%m/%Y')
        df['DATA_STR'] = df['DATA'].astype(str).str.strip().str[:10]
        df_hoje = df[df['DATA_STR'] == hoje_str].copy()
        
        # Cálculos de dias úteis restantes
        _, num_dias = calendar.monthrange(hoje_real.year, hoje_real.month)
        dias_restantes = sum(1 for d in range(hoje_real.day, num_dias + 1) if calendar.weekday(hoje_real.year, hoje_real.month, d) != 6)
        
        # 🔥 CORREÇÃO DO ERRO DE SINTAXE AQUI: usando == 0
        if dias_restantes == 0: 
            dias_restantes = 1
        
        st.markdown(f'''<div style="text-align: center; margin-top: -10px; margin-bottom: 20px;">
            <span style="font-size: 24px; font-weight: bold; color: #555;">Resultados de Hoje ({hoje_str}) - Dias úteis restantes: </span>
            <span style="font-size: 32px; font-weight: 900; color: #cc6600;">{dias_restantes}</span>
        </div>''', unsafe_allow_html=True)

        col_abc, col_sp = st.columns(2)
        
        def renderizar_base(base_nome, coluna_st, sups_lista):
            with coluna_st:
                # Totais
                total_hoje = df_hoje[df_hoje['BASE_CLEAN'] == base_nome]['QTD_CALC'].sum()
                
                classe_box = "box-base" if base_nome == "ABC" else "box-base-sp"
                cor_texto = "#2e7d32" if base_nome == "ABC" else "#00695c"
                icone_base = "🏢" if base_nome == "ABC" else "🏙️"
                
                st.markdown(f'''<div class="{classe_box}">
                    <div class="nome-base" style="color: {cor_texto};">{icone_base} BASE {base_nome} HOJE</div>
                    <div class="num-base">{int(total_hoje)}</div>
                </div>''', unsafe_allow_html=True)
                
                for sup in sups_lista:
                    qtd_mes = df_cards[df_cards['SUP_FINAL'] == sup]['QTD_CALC'].sum()
                    qtd_hoje_sup = df_hoje[(df_hoje['SUP_FINAL'] == sup) & (df_hoje['BASE_CLEAN'] == base_nome)]['QTD_CALC'].sum()
                    
                    meta_dia = int(round(max(0, 350 - qtd_mes) / dias_restantes))
                    falta_hoje = int(round(max(0, meta_dia - qtd_hoje_sup)))

                    st.markdown(f'''
                    <div class="sup-card">
                        <div class="sup-header">
                            <div class="sup-name">📋 {obter_nome_visual(sup)}</div>
                            <div class="badge-acumulado">Total Acumulado: {int(qtd_mes)}</div>
                        </div>
                        <div class="faltas-grid">
                            <div class="falta-box"><div class="falta-label">📦 HOJE</div><div class="falta-value">{int(qtd_hoje_sup)}</div></div>
                            <div class="falta-box"><div class="falta-label">📉 FALTAM</div><div class="falta-value">{falta_hoje}</div></div>
                            <div class="falta-box"><div class="falta-label">🎯 META DIA</div><div class="falta-value">{meta_dia}</div></div>
                        </div>
                    </div>''', unsafe_allow_html=True)

        renderizar_base('ABC', col_abc, SUPS_ABC)
        renderizar_base('SP', col_sp, SUPS_SP)

    except Exception as e:
        st.error(f"Erro ao processar: {e}")
else:
    st.error("Arquivo consultivo_sincronizado.csv não encontrado.")

import streamlit as st
import pandas as pd
import os
import calendar
import unicodedata
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# --- CSS PADRONIZADO ---
st.markdown("""<style>
    .topo-container { background: #003366; color: white; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px; }
    .sup-card { background: #ffffff; border: 1px solid #e0e0e0; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    .sup-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 15px; }
    .sup-name { font-size: 28px; font-weight: 900; color: #333; text-transform: uppercase; }
    .badge-acumulado { background: #e8f5e9; color: #2e7d32; padding: 8px 16px; border-radius: 8px; font-size: 16px; font-weight: bold; border: 1px solid #a5d6a7; }
    .faltas-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; }
    .falta-box { border-radius: 8px; padding: 15px; text-align: center; border: 1px solid #eee; background-color: #f9f9f9; }
    .falta-label { font-size: 14px; font-weight: bold; text-transform: uppercase; margin-bottom: 8px; color: #666; }
    .falta-value { font-size: 40px; font-weight: 900; color: #003366; line-height: 1; }
</style>""", unsafe_allow_html=True)

# --- DEFINIÇÃO DE VARIÁVEIS GLOBAIS (EVITA O NameError) ---
icone_ativo = '<div style="position: fixed; bottom: 20px; left: 20px; z-index: 9999; opacity: 0.8;"><svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#2e7d32" stroke-width="2"><path d="M11 5L6 9H2v6h4l5 4zM19.07 4.93a10 10 0 0 1 0 14.14"/></svg></div>'

st.markdown('<div class="topo-container"><h1>PERFORMANCE CONSULTIVO DIÁRIO</h1></div>', unsafe_allow_html=True)
st.markdown(icone_ativo, unsafe_allow_html=True)

# --- CONFIGURAÇÕES ---
ARQUIVO_CONSULTIVO = os.path.join(os.getcwd(), "consultivo_sincronizado.csv")
SUPS_ABC = ["EDSON MARCO", "MARCOS ROBERTO", "NELSON"]
SUPS_SP = ["ALAN", "FRANCISCO", "JOAO CARLOS MIRON"]
SUPERVISORES_ORDENADOS = SUPS_ABC + SUPS_SP

def limpar_texto(txt):
    if pd.isna(txt): return ''
    return unicodedata.normalize('NFKD', str(txt).strip().upper()).encode('ASCII', 'ignore').decode('utf-8')

# --- PROCESSAMENTO ---
if os.path.exists(ARQUIVO_CONSULTIVO):
    try:
        df = pd.read_csv(ARQUIVO_CONSULTIVO, sep=None, engine='python', dtype=str)
        df.columns = [str(c).upper().strip().replace(' ', '_') for c in df.columns]
        
        df['SUPERVISOR'] = df['SUPERVISOR'].fillna('#N/D').apply(limpar_texto)
        df['BASE'] = df['BASE'].fillna('N/D').apply(limpar_texto)
        df['QTD_PRODUTOS'] = pd.to_numeric(df['QTD_PRODUTOS'].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
        
        # 🔥 FORÇANDO O FILTRO DE DATA HOJE 🔥
        hoje_alvo = datetime.utcnow() - timedelta(hours=3)
        hoje_str = hoje_alvo.strftime('%d/%m/%Y')
        
        # Converte a coluna para data do Pandas para garantir a precisão
        df['DATA_DT'] = pd.to_datetime(df['DATA'], dayfirst=True, errors='coerce')
        df['DATA_STR'] = df['DATA_DT'].dt.strftime('%d/%m/%Y')
        
        # Verifica se o dia de hoje existe nos dados
        df_hoje = df[df['DATA_STR'] == hoje_str].copy()
        
        if df_hoje.empty:
            st.warning(f"⚠️ Atenção: Não foram encontrados dados para a data de hoje ({hoje_str}). Verifique se a planilha foi atualizada.")
            # Se não tem hoje, não soma nada como "Realizado Hoje"
        
        # Cálculos globais
        df_valid = df[df['SUPERVISOR'] != 'DESCARTADO'].copy()
        _, num_dias = calendar.monthrange(hoje_alvo.year, hoje_alvo.month)
        dias_restantes = sum(1 for d in range(hoje_alvo.day, num_dias + 1) if calendar.weekday(hoje_alvo.year, hoje_alvo.month, d) != 6)
        dias_restantes = max(1, dias_restantes)
        
        col_abc, col_sp = st.columns(2)
        
        def render_base(base, col, sups):
            with col:
                st.subheader(f"BASE {base}")
                for s in sups:
                    df_s = df_valid[df_valid['SUPERVISOR'].str.contains(s.split()[0], na=False) & (df_valid['BASE'] == base)]
                    df_s_hoje = df_hoje[df_hoje['SUPERVISOR'].str.contains(s.split()[0], na=False) & (df_hoje['BASE'] == base)]
                    
                    qtd_mes = df_s['QTD_PRODUTOS'].sum()
                    qtd_hoje = df_s_hoje['QTD_PRODUTOS'].sum()
                    
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
        st.error(f"Erro ao processar: {e}")
else:
    st.error("Arquivo consultivo_sincronizado.csv não encontrado.")
